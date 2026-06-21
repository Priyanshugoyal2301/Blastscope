import os
import sys
import time
import pytest
import joblib
import numpy as np
import pandas as pd

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.blast_engine.services.blast_calculator import BlastCalculatorService

@pytest.fixture
def loaded_model_package():
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blast_engine", "models", "inverse_characterization_model.joblib"))
    assert os.path.exists(model_path), f"Inverse model file not found at {model_path}. Run train_baseline.py first."
    package = joblib.load(model_path)
    return package

def test_model_metadata(loaded_model_package):
    """Verify that model package contains the required feature columns and target variables."""
    assert "model" in loaded_model_package
    assert "features" in loaded_model_package
    assert "targets" in loaded_model_package
    assert "features_to_log" in loaded_model_package
    assert "best_model_name" in loaded_model_package

    expected_features = [
        "is_surface",
        "log_incident_pressure",
        "log_reflected_pressure",
        "log_positive_impulse",
        "log_reflected_impulse",
        "log_arrival_time",
        "log_positive_duration"
    ]
    assert len(loaded_model_package["features"]) == len(expected_features)
    for feat in expected_features:
        assert feat in loaded_model_package["features"]

def test_inference_latency(loaded_model_package):
    """Verify that inference speed per sample is well under 50ms."""
    model = loaded_model_package["model"]
    features = loaded_model_package["features"]

    # Generate a dummy input vector (log-scale)
    # is_surface, log_incident_pressure, log_reflected_pressure, log_positive_impulse, log_reflected_impulse, log_arrival_time, log_positive_duration
    dummy_input = pd.DataFrame([[1.0, 3.0, 4.0, 2.5, 3.5, 1.0, 1.5]], columns=features)

    # Warmup
    model.predict(dummy_input)

    # Timing sweep over 100 iterations
    start_time = time.time()
    n_iterations = 100
    for _ in range(n_iterations):
        model.predict(dummy_input)
    elapsed_time = time.time() - start_time
    latency_ms = (elapsed_time / n_iterations) * 1000.0

    print(f"\nAverage prediction latency: {latency_ms:.4f} ms")
    assert latency_ms < 50.0, f"Latency of {latency_ms:.2f} ms exceeds the 50ms budget limit"

def test_prediction_physical_consistency(loaded_model_package):
    """
    Verify physical consistency:
    - We feed in a known case from the forward solver.
    - We check that the predicted W and Z reconstruct the physical standoff distance R via R ≈ Z * W^(1/3).
    - We check that the relative errors are within acceptable bounds.
    """
    model = loaded_model_package["model"]
    features = loaded_model_package["features"]
    features_to_log = loaded_model_package["features_to_log"]

    # 1. Setup a known forward solver state
    # W = 100.0 kg TNT, R = 15.0 m, Z = 15.0 / 100^(1/3) = 3.2312
    W_true = 100.0
    R_true = 15.0
    burst_type = "Surface"
    
    calc = BlastCalculatorService.calculate_environment(
        charge_weight=W_true,
        distance=R_true,
        burst_type=burst_type,
        pressure_factor=1.0,
        impulse_factor=1.0,
        general_factor=1.0,
        model="Kingery-Bulmash"
    )

    is_surface = 1.0 if burst_type == "Surface" else 0.0

    # Build input dict
    feat_dict = {
        "is_surface": is_surface,
        "log_incident_pressure": np.log10(calc["incident_pressure"]),
        "log_reflected_pressure": np.log10(calc["reflected_pressure"]),
        "log_positive_impulse": np.log10(calc["positive_impulse"]),
        "log_reflected_impulse": np.log10(calc["reflected_impulse"]),
        "log_arrival_time": np.log10(calc["arrival_time"]),
        "log_positive_duration": np.log10(calc["positive_duration"])
    }

    # Format DataFrame
    X_df = pd.DataFrame([[feat_dict[f] for f in features]], columns=features)

    # 2. Predict log targets
    preds_log = model.predict(X_df)
    W_pred = 10 ** float(preds_log[0, 0])
    Z_pred = 10 ** float(preds_log[0, 1])

    # 3. Derive distance R_pred
    R_pred = Z_pred * (W_pred ** (1.0 / 3.0))

    # 4. Check errors
    error_w = abs(W_pred - W_true) / W_true * 100.0
    error_r = abs(R_pred - R_true) / R_true * 100.0

    print(f"\nReconstruction Verification:")
    print(f"True values: W = {W_true:.2f} kg, Z = {R_true / (W_true ** (1/3)):.4f}, R = {R_true:.2f} m")
    print(f"Pred values: W = {W_pred:.2f} kg, Z = {Z_pred:.4f}, R = {R_pred:.2f} m")
    print(f"Errors: Weight Error = {error_w:.3f}%, Distance Error = {error_r:.3f}%")

    # Assert model error is low (within 5% for this clean test case)
    assert error_w < 5.0, f"Weight prediction error ({error_w:.2f}%) exceeds the 5% tolerance threshold."
    assert error_r < 5.0, f"Derived distance error ({error_r:.2f}%) exceeds the 5% tolerance threshold."

def test_multi_samples_regression(loaded_model_package):
    """
    Verify regression metrics across a small subset of the clean validation dataset.
    Asserts R^2 >= 0.90 on targets.
    """
    model = loaded_model_package["model"]
    features = loaded_model_package["features"]
    features_to_log = loaded_model_package["features_to_log"]

    # Load first 200 samples of dataset
    csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "inverse_dataset_v1.csv"))
    df = pd.read_csv(csv_path)

    # Filter Z-clamped
    df_clean = df[~((df["burst_type"] == "Surface") & (df["scaled_distance"] < 0.20))].copy()
    df_sub = df_clean.sample(n=min(500, len(df_clean)), random_state=100)

    # Preprocess
    df_sub["log_weight"] = np.log10(df_sub["weight"])
    df_sub["log_scaled_distance"] = np.log10(df_sub["scaled_distance"])
    df_sub["is_surface"] = (df_sub["burst_type"] == "Surface").astype(int)
    for col in features_to_log:
        df_sub[f"log_{col}"] = np.log10(df_sub[col])

    X = df_sub[features]
    y_w_true = df_sub["log_weight"].values
    y_z_true = df_sub["log_scaled_distance"].values

    # Predict
    preds = model.predict(X)
    y_w_pred = preds[:, 0]
    y_z_pred = preds[:, 1]

    # Calculate R2
    from sklearn.metrics import r2_score
    r2_w = r2_score(y_w_true, y_w_pred)
    r2_z = r2_score(y_z_true, y_z_pred)

    print(f"\nSubset Validation Metrics (N={len(df_sub)}):")
    print(f"Weight log R^2: {r2_w:.6f}")
    print(f"Z log R^2: {r2_z:.6f}")

    assert r2_w >= 0.90, f"Weight R^2 ({r2_w:.4f}) is below target 0.90"
    assert r2_z >= 0.90, f"Scaled distance R^2 ({r2_z:.4f}) is below target 0.90"
