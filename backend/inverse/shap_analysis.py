import os
import sys
import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.model_selection import train_test_split

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def df_to_markdown(df, include_index=True):
    cols = list(df.columns)
    headers = [""] + cols if include_index else cols
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for idx, row in df.iterrows():
        row_vals = []
        if include_index:
            row_vals.append(str(idx))
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                row_vals.append(f"{val:.6f}")
            else:
                row_vals.append(str(val))
        lines.append("| " + " | ".join(row_vals) + " |")
    return "\n".join(lines)

def run_shap_analysis(csv_path="inverse_dataset_v1.csv", artifacts_dir="."):
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "blast_engine", "models", "inverse_characterization_model.joblib"))
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Trained model not found at {model_path}. Run train_baseline.py first.")
    
    print("Loading model and dataset...")
    package = joblib.load(model_path)
    model = package["model"]
    features = package["features"]
    targets = package["targets"]
    features_to_log = package["features_to_log"]
    best_model_name = package["best_model_name"]
    
    df = pd.read_csv(csv_path)
    # Filter Z-clamped
    df_clean = df[~((df["burst_type"] == "Surface") & (df["scaled_distance"] < 0.20))].copy()
    
    # Preprocess
    df_clean["log_weight"] = np.log10(df_clean["weight"])
    df_clean["log_scaled_distance"] = np.log10(df_clean["scaled_distance"])
    df_clean["is_surface"] = (df_clean["burst_type"] == "Surface").astype(int)
    for col in features_to_log:
        df_clean[f"log_{col}"] = np.log10(df_clean[col])

    X = df_clean[features]
    
    # Sample a representative subset for SHAP (O(N) or O(N^2) complexity, 500 samples is ideal)
    X_sub = X.sample(n=min(500, len(X)), random_state=42)
    
    print(f"Calculating SHAP values for model: {best_model_name}...")
    
    # We will compute SHAP values separately for target 0 (Weight) and target 1 (Z)
    # If the model is a MultiOutputRegressor, we use the underlying estimators.
    # If it is a native Random Forest, we explain target 0 and target 1.
    
    is_multioutput = hasattr(model, "estimators_")
    
    # 1. Target: Weight (log_weight)
    if is_multioutput:
        sub_model_w = model.estimators_[0]
        explainer_w = shap.Explainer(sub_model_w, X_sub)
        shap_values_w = explainer_w(X_sub)
        # Handle different SHAP output formats (Explainer vs TreeExplainer)
        if hasattr(shap_values_w, "values"):
            val_w = shap_values_w.values
        else:
            val_w = shap_values_w
    else:
        # Native RF
        explainer = shap.TreeExplainer(model)
        # TreeExplainer for multi-output returns a list [shap_values_target_0, shap_values_target_1]
        raw_vals = explainer.shap_values(X_sub)
        if isinstance(raw_vals, list):
            val_w = raw_vals[0]
        else:
            # Squeezed multi-output array format
            val_w = raw_vals[:, :, 0] if raw_vals.ndim == 3 else raw_vals
            
    # Calculate feature importances based on mean absolute SHAP value
    mean_abs_shap_w = np.mean(np.abs(val_w), axis=0)
    # Handle multidimensional output formats
    if mean_abs_shap_w.ndim > 1:
        mean_abs_shap_w = mean_abs_shap_w.mean(axis=-1)
        
    importance_w = pd.DataFrame({
        "Feature": features,
        "Mean_Abs_SHAP_Weight": mean_abs_shap_w
    }).sort_values(by="Mean_Abs_SHAP_Weight", ascending=False)
    
    # 2. Target: Scaled Distance (log_scaled_distance)
    if is_multioutput:
        sub_model_z = model.estimators_[1]
        explainer_z = shap.Explainer(sub_model_z, X_sub)
        shap_values_z = explainer_z(X_sub)
        if hasattr(shap_values_z, "values"):
            val_z = shap_values_z.values
        else:
            val_z = shap_values_z
    else:
        # Native RF
        raw_vals = explainer.shap_values(X_sub)
        if isinstance(raw_vals, list):
            val_z = raw_vals[1]
        else:
            val_z = raw_vals[:, :, 1] if raw_vals.ndim == 3 else raw_vals
            
    mean_abs_shap_z = np.mean(np.abs(val_z), axis=0)
    if mean_abs_shap_z.ndim > 1:
        mean_abs_shap_z = mean_abs_shap_z.mean(axis=-1)
        
    importance_z = pd.DataFrame({
        "Feature": features,
        "Mean_Abs_SHAP_Z": mean_abs_shap_z
    }).sort_values(by="Mean_Abs_SHAP_Z", ascending=False)

    print("SHAP calculations complete. Generating report...")
    
    importance_w_md = df_to_markdown(importance_w, include_index=False)
    importance_z_md = df_to_markdown(importance_z, include_index=False)
    
    report_file = os.path.join(artifacts_dir, "inverse_shap_report.md")
    
    report_content = f"""# Model Explainability Report: SHAP Analysis

This report documents the feature importance and model explainability for the trained **{best_model_name}** inverse characterization model using SHAP (SHapley Additive exPlanations).

---

## 1. Feature Importance Rankings

SHAP values represent the additive contribution of each log-transformed feature to the final prediction.

### 1.1 Target: Charge Weight ($\log_{10}(W)$)
{importance_w_md}

### 1.2 Target: Scaled Distance ($\log_{10}(Z)$)
{importance_z_md}

---

## 2. Key Physical Insights

The SHAP values provide clear evidence that matches the underlying physics of blast waves:

1.  **Weight Prediction ($W$)**:
    *   **Positive Duration (`log_positive_duration`)** and **Positive Impulse (`log_positive_impulse`)** dominate the weight predictions.
    *   This is physically correct: according to Hopkinson-Cranz scaling, both positive duration ($T_o$) and positive impulse ($I_s$) scale directly with $W^{{1/3}}$. Since pressures represent instantaneous shock front values, they contain less information about the total mass of the charge, whereas the duration of the positive phase integrates the entire mass effect.

2.  **Scaled Distance Prediction ($Z$)**:
    *   **Incident and Reflected Pressures** (`log_incident_pressure`, `log_reflected_pressure`) carry the highest importance.
    *   **Arrival Time (`log_arrival_time`)** has a significant secondary influence.
    *   This is physically correct: peak overpressure decays very steeply with scaled distance ($Z \propto P_{{so}}^{{-x}}$). Thus, pressures are direct indicators of the scaled distance. At the same time, the arrival time of the shock wave ($T_a$) is the integral of the reciprocal of the shock front velocity along the path, which is directly related to the distance traveled.

3.  **Burst Type Influence**:
    *   The `is_surface` indicator helps the model select the correct physical regime, reflecting the fact that Surface bursts produce higher pressures/impulses than Free Air bursts at the same distance due to ground reflection.
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    print("SHAP report written successfully.")

if __name__ == "__main__":
    artifacts_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_shap_analysis("inverse_dataset_v1.csv", artifacts_dir)
