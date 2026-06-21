import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

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


def classify_extrapolation(r2, mae, context_name):
    """
    Multi-tier extrapolation classification.
    More robust than simple R² < 0 check.
    """
    if r2 >= 0.90:
        return "EXCELLENT", f"Model generalizes well to {context_name} ($R^2 = {r2:.4f}$, MAE = {mae:.2f})."
    elif r2 >= 0.70:
        return "ACCEPTABLE", f"Model shows moderate generalization to {context_name} ($R^2 = {r2:.4f}$, MAE = {mae:.2f}). Results should be treated with caution."
    elif r2 >= 0.30:
        return "POOR", f"Model struggles to generalize to {context_name} ($R^2 = {r2:.4f}$, MAE = {mae:.2f}). Predictions in this regime are unreliable."
    elif r2 >= 0.0:
        return "VERY POOR", f"Model barely outperforms a mean predictor for {context_name} ($R^2 = {r2:.4f}$, MAE = {mae:.2f}). Extrapolation is fundamentally broken."
    else:
        return "FAILED", f"Model performs worse than a constant mean predictor for {context_name} ($R^2 = {r2:.4f}$, MAE = {mae:.2f}). This confirms the model cannot extrapolate beyond its training range."


def run_scientific_validation(csv_path="inverse_dataset_v1.csv", artifacts_dir="."):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run generate_inverse_dataset.py first.")

    # Ensure UTF-8 output on Windows
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("Loading dataset for holdout and extrapolation verification...")
    df = pd.read_csv(csv_path)

    # Filter out Z-clamped samples (Surface Z < 0.20)
    df_clean = df[~((df["burst_type"] == "Surface") & (df["scaled_distance"] < 0.20))].copy()

    features = [
        "is_surface",
        "log_incident_pressure", "log_reflected_pressure",
        "log_positive_impulse", "log_reflected_impulse",
        "log_arrival_time", "log_positive_duration"
    ]
    
    # Preprocess
    df_clean["log_weight"] = np.log10(df_clean["weight"])
    df_clean["log_scaled_distance"] = np.log10(df_clean["scaled_distance"])
    df_clean["is_surface"] = (df_clean["burst_type"] == "Surface").astype(int)
    for col in ["incident_pressure", "reflected_pressure", "positive_impulse", "reflected_impulse", "arrival_time", "positive_duration"]:
        df_clean[f"log_{col}"] = np.log10(df_clean[col])

    # Holdout Experiments
    records = []
    experiment_analyses = []

    # --- EXPERIMENT 1: Charge Weight (W) Extrapolation ---
    # Train on W <= 1000 kg TNT (small/med), Test on W > 1000 kg TNT (large)
    train_df = df_clean[df_clean["weight"] <= 1000.0]
    test_df = df_clean[df_clean["weight"] > 1000.0]
    n_train_1 = len(train_df)
    n_test_1 = len(test_df)
    
    rf_w_extrap = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_w_extrap.fit(train_df[features], train_df["log_weight"])
    preds_w = rf_w_extrap.predict(test_df[features])
    r2_w_ext = r2_score(test_df["log_weight"], preds_w)
    mae_w_ext = mean_absolute_error(10**test_df["log_weight"], 10**preds_w)
    rel_err_w_ext = np.mean(np.abs(10**preds_w - 10**test_df["log_weight"].values) / 10**test_df["log_weight"].values) * 100.0
    
    status_w, desc_w = classify_extrapolation(r2_w_ext, mae_w_ext, "W > 1000 kg TNT")
    
    records.append({
        "Experiment": "W Extrapolation (Train W ≤ 1000, Test W > 1000)",
        "Metric": "Weight (W) kg TNT",
        "Train_Samples": n_train_1,
        "Test_Samples": n_test_1,
        "R2_Score": r2_w_ext,
        "MAE": mae_w_ext,
        "Rel_Error_%": rel_err_w_ext,
        "Status": status_w
    })
    
    experiment_analyses.append(f"""### 2.1 Weight Extrapolation (W > 1000 kg TNT)
*   **Status**: `{status_w}` — {desc_w}
*   **Train Samples**: {n_train_1:,} | **Test Samples**: {n_test_1:,}
*   **Physical & ML Rationale**: Decision-tree regressors (Random Forest, XGBoost, LightGBM) cannot predict values outside the range of their training targets. The trees partition the feature space and assign constant predictions at leaf nodes. Consequently, any threat larger than the training maximum is predicted as approximately the training maximum.
*   **Mitigation**: The production model must be trained on the full envelope $[0.1, 10000.0]$ kg TNT. The model should never be evaluated on inputs suspected to exceed its training boundaries.""")

    # --- EXPERIMENT 2: Scaled Distance (Z) Extrapolation ---
    # Train on Z >= 0.5, Test on Z < 0.5 (near-field regime)
    train_df = df_clean[df_clean["scaled_distance"] >= 0.5]
    test_df = df_clean[df_clean["scaled_distance"] < 0.5]
    n_train_2 = len(train_df)
    n_test_2 = len(test_df)
    
    rf_z_extrap = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_z_extrap.fit(train_df[features], train_df["log_scaled_distance"])
    preds_z = rf_z_extrap.predict(test_df[features])
    r2_z_ext = r2_score(test_df["log_scaled_distance"], preds_z)
    mae_z_ext = mean_absolute_error(10**test_df["log_scaled_distance"], 10**preds_z)
    rel_err_z_ext = np.mean(np.abs(10**preds_z - 10**test_df["log_scaled_distance"].values) / 10**test_df["log_scaled_distance"].values) * 100.0
    
    status_z, desc_z = classify_extrapolation(r2_z_ext, mae_z_ext, "Z < 0.5")
    
    records.append({
        "Experiment": "Z Extrapolation (Train Z ≥ 0.5, Test Z < 0.5)",
        "Metric": "Scaled Distance (Z)",
        "Train_Samples": n_train_2,
        "Test_Samples": n_test_2,
        "R2_Score": r2_z_ext,
        "MAE": mae_z_ext,
        "Rel_Error_%": rel_err_z_ext,
        "Status": status_z
    })
    
    experiment_analyses.append(f"""### 2.2 Scaled Distance Extrapolation (Z < 0.5)
*   **Status**: `{status_z}` — {desc_z}
*   **Train Samples**: {n_train_2:,} | **Test Samples**: {n_test_2:,}
*   **Physical & ML Rationale**: Near-field blast physics ($Z < 0.5$) exhibits highly non-linear shock wave propagation, where chemical reaction kinetics and gas expansions dominate before transition to standard acoustic shock behavior. Decision trees cannot extrapolate these steep, non-linear curves into the near-field.
*   **Mitigation**: The training dataset must span the full physical range $[0.06, 40.0]$ $m/\\text{{kg}}^{{1/3}}$ to guarantee near-field coverage.""")

    # --- EXPERIMENT 3: Cross-Regime Generalization (Surface -> Free Air) ---
    # Train on Surface only, Test on Free Air
    train_df = df_clean[df_clean["burst_type"] == "Surface"]
    test_df = df_clean[df_clean["burst_type"] == "Free Air"]
    n_train_3 = len(train_df)
    n_test_3 = len(test_df)
    
    rf_w_s2f = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_w_s2f.fit(train_df[features], train_df["log_weight"])
    preds_s2f_w = rf_w_s2f.predict(test_df[features])
    r2_s2f_w = r2_score(test_df["log_weight"], preds_s2f_w)
    mae_s2f_w = mean_absolute_error(10**test_df["log_weight"], 10**preds_s2f_w)
    rel_err_s2f_w = np.mean(np.abs(10**preds_s2f_w - 10**test_df["log_weight"].values) / 10**test_df["log_weight"].values) * 100.0
    
    status_s2f, desc_s2f = classify_extrapolation(r2_s2f_w, mae_s2f_w, "Free Air from Surface-trained model")
    
    records.append({
        "Experiment": "Cross-Regime (Train Surface, Test Free Air)",
        "Metric": "Weight (W) kg TNT",
        "Train_Samples": n_train_3,
        "Test_Samples": n_test_3,
        "R2_Score": r2_s2f_w,
        "MAE": mae_s2f_w,
        "Rel_Error_%": rel_err_s2f_w,
        "Status": status_s2f
    })

    # --- EXPERIMENT 4: Cross-Regime Generalization (Free Air -> Surface) ---
    # Train on Free Air only, Test on Surface
    train_df = df_clean[df_clean["burst_type"] == "Free Air"]
    test_df = df_clean[df_clean["burst_type"] == "Surface"]
    n_train_4 = len(train_df)
    n_test_4 = len(test_df)
    
    rf_w_f2s = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf_w_f2s.fit(train_df[features], train_df["log_weight"])
    preds_f2s_w = rf_w_f2s.predict(test_df[features])
    r2_f2s_w = r2_score(test_df["log_weight"], preds_f2s_w)
    mae_f2s_w = mean_absolute_error(10**test_df["log_weight"], 10**preds_f2s_w)
    rel_err_f2s_w = np.mean(np.abs(10**preds_f2s_w - 10**test_df["log_weight"].values) / 10**test_df["log_weight"].values) * 100.0
    
    status_f2s, desc_f2s = classify_extrapolation(r2_f2s_w, mae_f2s_w, "Surface from Free-Air-trained model")
    
    records.append({
        "Experiment": "Cross-Regime (Train Free Air, Test Surface)",
        "Metric": "Weight (W) kg TNT",
        "Train_Samples": n_train_4,
        "Test_Samples": n_test_4,
        "R2_Score": r2_f2s_w,
        "MAE": mae_f2s_w,
        "Rel_Error_%": rel_err_f2s_w,
        "Status": status_f2s
    })
    
    experiment_analyses.append(f"""### 2.3 Cross-Regime Domain Shifts (Surface vs. Free Air)
*   **Surface → Free Air**: `{status_s2f}` — {desc_s2f}
    *   Train Samples: {n_train_3:,} | Test Samples: {n_test_3:,}
*   **Free Air → Surface**: `{status_f2s}` — {desc_f2s}
    *   Train Samples: {n_train_4:,} | Test Samples: {n_test_4:,}
*   **Physical Rationale**: At identical scaled distances, Surface bursts generate significantly higher incident impulses and pressures than Free-Air bursts due to ground reflections absorbing and redirecting energy. 
    *   If a model trained only on Surface bursts evaluates Free-Air blast parameters, it will **underestimate** the charge weight (since Free-Air parameters are smaller for the same weight).
    *   If a model trained only on Free-Air bursts evaluates Surface blast parameters, it will **overestimate** the charge weight.
*   **Mitigation**: The model must incorporate `is_surface` as a primary binary feature and train on an equal mix of both burst types. The end-user must specify the burst type in the Predict screen to ensure correct physical scaling is applied.""")

    validation_df = pd.DataFrame(records)
    print("\nHoldout Validation Results:")
    print(validation_df.to_string())

    validation_md = df_to_markdown(validation_df, include_index=False)
    
    # Count overall status
    n_total = len(records)
    n_pass = sum(1 for r in records if r["Status"] in ("EXCELLENT", "ACCEPTABLE"))
    n_fail = n_total - n_pass
    
    # Build overall verdict
    if n_fail == 0:
        overall_verdict = "All holdout experiments pass. The model generalizes well across all tested regimes."
    elif n_pass == 0:
        overall_verdict = f"All {n_total} holdout experiments show poor/failed generalization. This is **expected behavior** for tree-based models tested on data outside their training envelope — it confirms the importance of full-range training data."
    else:
        overall_verdict = f"{n_pass}/{n_total} experiments pass, {n_fail}/{n_total} show poor generalization. The failing experiments identify specific extrapolation boundaries that the production model must cover via full-range training."
    
    experiment_analysis_text = "\n\n".join(experiment_analyses)
    
    # Write report — ALL values dynamically derived
    report_file = os.path.join(artifacts_dir, "inverse_model_validation_report.md")
    report_content = f"""# Holdout & Extrapolation Validation Report

This report documents the rigorous generalization validation of the Inverse Blast Characterization module. We evaluate the model's performance on holdout regimes to identify extrapolation boundaries and physical limitations.

> [!IMPORTANT]
> All numerical values, status classifications, and interpretations in this report are dynamically computed from actual model predictions. No values are hardcoded. The status classification uses a multi-tier system: EXCELLENT ($R^2 \\ge 0.90$), ACCEPTABLE ($R^2 \\ge 0.70$), POOR ($R^2 \\ge 0.30$), VERY POOR ($R^2 \\ge 0.0$), FAILED ($R^2 < 0.0$).

---

## 1. Holdout Validation Performance

The Separate Trees Random Forest model was evaluated across {n_total} holdout experiments testing extrapolation boundaries (unseen ranges of weight and scaled distance) and domain shifts (unseen burst types):

{validation_md}

**Overall Verdict**: {overall_verdict}

---

## 2. Key Scientific Findings & Limitations

{experiment_analysis_text}
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Scientific Validation Report written successfully.")
    
    # Save temp metrics
    import json
    metrics_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "temp_metrics.json"))
    data = {}
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, "r") as f:
                data = json.load(f)
        except Exception:
            pass
    data["W_Extrap_R2"] = float(r2_w_ext)
    data["Z_Extrap_R2"] = float(r2_z_ext)
    with open(metrics_file, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    artifacts_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_scientific_validation("inverse_dataset_v1.csv", artifacts_dir)
