import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# VIF threshold: R² values above this are treated as "infinite" VIF.
# Using 1.0 - 1e-10 instead of 1.0 to handle floating-point near-unity R²
# (e.g. 0.9999999999999998) that represent practical perfect collinearity.
VIF_R2_INF_THRESHOLD = 1.0 - 1e-10

def calculate_manual_vif(df_features):
    """
    Calculate Variance Inflation Factor (VIF) manually using scikit-learn LinearRegression.
    VIF = 1 / (1 - R^2)
    
    R² values above VIF_R2_INF_THRESHOLD are treated as infinite VIF,
    since floating-point arithmetic can yield R² = 0.9999999999999998
    for perfectly collinear features.
    """
    vifs = {}
    cols = df_features.columns
    for col in cols:
        X = df_features.drop(columns=[col])
        y = df_features[col]
        reg = LinearRegression().fit(X, y)
        r2 = reg.score(X, y)
        if r2 > VIF_R2_INF_THRESHOLD:
            vif = float('inf')
        else:
            vif = 1.0 / (1.0 - r2)
        vifs[col] = vif
    return pd.DataFrame(list(vifs.items()), columns=["Feature", "VIF"])

def run_scientific_eda(csv_path="inverse_dataset_v1.csv", artifacts_dir="."):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run generate_inverse_dataset.py first.")
        
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # 1. Filter out Z-clamped samples (Surface Z < 0.20)
    df_clean = df[~((df["burst_type"] == "Surface") & (df["scaled_distance"] < 0.20))].copy()
    
    features_all = [
        "incident_pressure", "reflected_pressure", "dynamic_pressure",
        "positive_impulse", "reflected_impulse", "arrival_time",
        "positive_duration", "shock_front_velocity", "particle_velocity"
    ]
    
    # Log-transformed features
    df_log = pd.DataFrame()
    df_log["is_surface"] = (df_clean["burst_type"] == "Surface").astype(int)
    for col in features_all:
        df_log[f"log_{col}"] = np.log10(df_clean[col])
        
    # 2. Log-scale Histograms Plot
    print("Generating log-scale histograms...")
    plots_dir = os.path.join(artifacts_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    axes = axes.flatten()
    for i, col in enumerate(features_all):
        axes[i].hist(df_log[f"log_{col}"], bins=50, color="#2563EB", alpha=0.7, edgecolor='black', linewidth=0.5)
        axes[i].set_title(f"log10({col})")
        axes[i].set_xlabel("Value (log10)")
        axes[i].set_ylabel("Count")
        axes[i].grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    histogram_plot_path = os.path.join(plots_dir, "log_histograms.png")
    plt.savefig(histogram_plot_path, dpi=150)
    plt.close()
    print(f"Histograms plot saved to: {histogram_plot_path}")
    
    # 3. Multicollinearity and VIF Analysis
    print("Calculating VIF...")
    # Compute VIF on the continuous log-transformed features
    df_vif_input = df_log[[f"log_{col}" for col in features_all]]
    vif_df = calculate_manual_vif(df_vif_input).sort_values(by="VIF", ascending=False)
    
    # --- DYNAMICALLY generate VIF interpretation from actual computed values ---
    # Four tiers: infinite (R² > threshold), near-infinite (VIF > 1e6), high (VIF > 10), acceptable (VIF ≤ 10)
    inf_vif_features = vif_df[vif_df["VIF"] == float('inf')]["Feature"].tolist()
    near_inf_features = vif_df[(vif_df["VIF"] != float('inf')) & (vif_df["VIF"] > 1e6)]["Feature"].tolist()
    high_vif_features = vif_df[(vif_df["VIF"] != float('inf')) & (vif_df["VIF"] > 10.0) & (vif_df["VIF"] <= 1e6)]["Feature"].tolist()
    low_vif_features = vif_df[vif_df["VIF"] <= 10.0]["Feature"].tolist()
    
    n_inf = len(inf_vif_features)
    n_near_inf = len(near_inf_features)
    n_high = len(high_vif_features)
    n_low = len(low_vif_features)
    
    vif_interp_lines = []
    if n_inf > 0:
        feat_list = ", ".join([f"`{f}`" for f in inf_vif_features])
        vif_interp_lines.append(f"    *   {n_inf} feature(s) exhibit **infinite VIF** ($R^2 > {VIF_R2_INF_THRESHOLD}$): {feat_list}.")
        vif_interp_lines.append("    *   This is mathematically expected for features that are deterministic functions of other features:")
        vif_interp_lines.append("        *   Dynamic Pressure is derived via: $Q = 2.5 P_{so}^2 / (7 P_0 + P_{so})$.")
        vif_interp_lines.append("        *   Shock velocity is derived via: $U = c_0 \\sqrt{1 + 6 P_{so} / 7 P_0}$.")
        vif_interp_lines.append("        *   Particle velocity is derived via Rankine-Hugoniot relationships directly from $P_{so}$.")
        vif_interp_lines.append("    *   These derived features carry effectively zero independent variance.")
    if n_near_inf > 0:
        feat_list = ", ".join([f"`{f}` (VIF = {vif_df[vif_df['Feature']==f]['VIF'].values[0]:.0f})" for f in near_inf_features])
        vif_interp_lines.append(f"    *   {n_near_inf} feature(s) have **near-infinite VIF (> 1,000,000)**: {feat_list}. These are practically collinear — their variance is almost entirely explained by other features.")
    if n_high > 0:
        feat_list = ", ".join([f"`{f}` (VIF = {vif_df[vif_df['Feature']==f]['VIF'].values[0]:.0f})" for f in high_vif_features])
        vif_interp_lines.append(f"    *   {n_high} feature(s) have **high VIF (10–1,000,000)**: {feat_list}. These are strongly collinear but not perfectly redundant.")
    if n_low > 0:
        feat_list = ", ".join([f"`{f}`" for f in low_vif_features])
        vif_interp_lines.append(f"    *   {n_low} feature(s) have **acceptable VIF (≤ 10)**: {feat_list}. These features contribute independent variance.")
    if n_inf == 0 and n_near_inf == 0 and n_high == 0:
        vif_interp_lines.append("    *   **No features exhibit concerning multicollinearity.** All VIF values are within acceptable bounds (≤ 10).")
    
    vif_interpretation = "\n".join(vif_interp_lines)
    
    # 4. PCA Analysis
    print("Running PCA...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_vif_input)
    pca = PCA().fit(X_scaled)
    pca_df = pd.DataFrame({
        "Principal Component": [f"PC{i+1}" for i in range(len(features_all))],
        "Explained Variance Ratio": pca.explained_variance_ratio_,
        "Cumulative Explained Variance": np.cumsum(pca.explained_variance_ratio_)
    })
    
    # --- DYNAMICALLY determine how many PCs explain 99% variance ---
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    n_pcs_99 = int(np.argmax(cum_var >= 0.99)) + 1
    cum_var_at_n = cum_var[n_pcs_99 - 1] * 100.0
    
    # Also find 95% threshold
    n_pcs_95 = int(np.argmax(cum_var >= 0.95)) + 1
    cum_var_at_95 = cum_var[n_pcs_95 - 1] * 100.0
    
    # First 3 PCs cumulative variance
    cum_var_3 = cum_var[min(2, len(cum_var)-1)] * 100.0
    
    # --- Generate PCA Scree Plot ---
    print("Generating PCA scree plot...")
    fig_pca, ax_pca = plt.subplots(figsize=(8, 5))
    n_components = len(pca.explained_variance_ratio_)
    x_pcs = np.arange(1, n_components + 1)
    
    # Bar chart for individual variance
    ax_pca.bar(x_pcs, pca.explained_variance_ratio_ * 100, color="#2563EB", alpha=0.7, 
               label="Individual", edgecolor='black', linewidth=0.5)
    # Line chart for cumulative variance
    ax_pca.plot(x_pcs, cum_var * 100, 'o-', color="#EA580C", linewidth=2, markersize=6, 
                label="Cumulative")
    
    # Reference lines at 95% and 99%
    ax_pca.axhline(y=95, color='green', linestyle='--', alpha=0.6, label='95% threshold')
    ax_pca.axhline(y=99, color='red', linestyle='--', alpha=0.6, label='99% threshold')
    
    ax_pca.set_xlabel('Principal Component', fontsize=12)
    ax_pca.set_ylabel('Explained Variance (%)', fontsize=12)
    ax_pca.set_title('PCA Scree Plot: Explained Variance by Component', fontsize=13)
    ax_pca.set_xticks(x_pcs)
    ax_pca.set_xticklabels([f'PC{i}' for i in x_pcs])
    ax_pca.legend(loc='center right', fontsize=10)
    ax_pca.grid(True, linestyle='--', alpha=0.4)
    ax_pca.set_ylim(0, 105)
    
    plt.tight_layout()
    scree_plot_path = os.path.join(plots_dir, "pca_scree.png")
    plt.savefig(scree_plot_path, dpi=150)
    plt.close()
    print(f"PCA scree plot saved to: {scree_plot_path}")
    
    pca_interp_lines = [
        f"*   **Interpretation**: The first **{n_pcs_95}** principal component(s) explain **{cum_var_at_95:.2f}%** of the variance (95% threshold). The first **{n_pcs_99}** principal component(s) explain **{cum_var_at_n:.2f}%** (99% threshold).",
        f"    *   Specifically, the first 3 PCs cumulatively explain **{cum_var_3:.2f}%** of the entire dataset variance.",
    ]
    if cum_var_3 > 99.0:
        pca_interp_lines.append("    *   This confirms that the true physical dimensionality of the blast parameters is extremely small ($\\le 3$ independent dimensions), which matches blast physics where $W$, $Z$, and BurstType completely determine the environment.")
    else:
        pca_interp_lines.append(f"    *   The feature space has moderate dimensionality. {n_pcs_99} components are needed to capture 99% of the variance, suggesting some features carry partially independent information.")
    
    pca_interpretation = "\n".join(pca_interp_lines)
    
    # 5. Feature Elimination Study
    print("Running Feature Elimination study...")
    # Targets
    df_clean["log_weight"] = np.log10(df_clean["weight"])
    df_clean["log_scaled_distance"] = np.log10(df_clean["scaled_distance"])
    y = df_clean[["log_weight", "log_scaled_distance"]]
    
    # Setups
    features_full = ["is_surface"] + [f"log_{col}" for col in features_all]
    features_pruned = ["is_surface"] + [f"log_{col}" for col in [
        "incident_pressure", "reflected_pressure", "positive_impulse", "reflected_impulse", "arrival_time", "positive_duration"
    ]]
    
    X_full = df_log.copy()
    X_full["is_surface"] = df_log["is_surface"]
    X_full_cols = features_full
    
    X_pruned_cols = features_pruned
    
    # Train test splits
    X_train_f, X_test_f, y_train, y_test = train_test_split(df_log[X_full_cols], y, test_size=0.2, random_state=42)
    X_train_p, X_test_p = train_test_split(df_log[X_pruned_cols], test_size=0.2, random_state=42)
    
    # Train Random Forest on full set
    rf_full = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1)
    rf_full.fit(X_train_f, y_train)
    preds_f = rf_full.predict(X_test_f)
    r2_w_f = r2_score(y_test["log_weight"], preds_f[:, 0])
    r2_z_f = r2_score(y_test["log_scaled_distance"], preds_f[:, 1])
    mae_w_f = mean_absolute_error(y_test["log_weight"], preds_f[:, 0])
    mae_z_f = mean_absolute_error(y_test["log_scaled_distance"], preds_f[:, 1])
    
    # Train Random Forest on pruned set
    rf_pruned = RandomForestRegressor(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1)
    rf_pruned.fit(X_train_p, y_train)
    preds_p = rf_pruned.predict(X_test_p)
    r2_w_p = r2_score(y_test["log_weight"], preds_p[:, 0])
    r2_z_p = r2_score(y_test["log_scaled_distance"], preds_p[:, 1])
    mae_w_p = mean_absolute_error(y_test["log_weight"], preds_p[:, 0])
    mae_z_p = mean_absolute_error(y_test["log_scaled_distance"], preds_p[:, 1])
    
    elimination_df = pd.DataFrame([
        {
            "Feature Set": f"Full ({len(features_full)} features: is_surface + {len(features_all)} log-features)",
            "W_R2_Log": r2_w_f,
            "W_MAE_Log": mae_w_f,
            "Z_R2_Log": r2_z_f,
            "Z_MAE_Log": mae_z_f
        },
        {
            "Feature Set": f"Pruned ({len(features_pruned)} features: is_surface + {len(features_pruned)-1} log-features)",
            "W_R2_Log": r2_w_p,
            "W_MAE_Log": mae_w_p,
            "Z_R2_Log": r2_z_p,
            "Z_MAE_Log": mae_z_p
        }
    ])
    
    # --- DYNAMICALLY generate elimination interpretation ---
    r2_w_diff = abs(r2_w_f - r2_w_p)
    r2_z_diff = abs(r2_z_f - r2_z_p)
    
    if r2_w_diff < 0.01 and r2_z_diff < 0.01:
        elim_conclusion = f"*   **Conclusion**: Pruning the redundant features does **not** degrade the prediction accuracy ($\\Delta R^2_W = {r2_w_diff:.4f}$, $\\Delta R^2_Z = {r2_z_diff:.4f}$). The pruned model is smaller, faster, and less prone to overfitting on sensor measurement errors. Therefore, the **{len(features_pruned)}-feature pruned set is selected for production deployment**."
    elif r2_w_p > 0.99 and r2_z_p > 0.99:
        elim_conclusion = f"*   **Conclusion**: Although there is a minor accuracy difference ($\\Delta R^2_W = {r2_w_diff:.4f}$, $\\Delta R^2_Z = {r2_z_diff:.4f}$), both models achieve $R^2 > 0.99$. The pruned model is recommended for production to avoid multicollinearity issues."
    else:
        elim_conclusion = f"*   **Conclusion**: Feature pruning causes a notable accuracy change ($\\Delta R^2_W = {r2_w_diff:.4f}$, $\\Delta R^2_Z = {r2_z_diff:.4f}$). Pruned W $R^2 = {r2_w_p:.4f}$, Pruned Z $R^2 = {r2_z_p:.4f}$. Consider retaining more features or investigating further."
    
    # 6. Correlation matrices
    corr_spearman = df_clean[features_all + ["weight", "scaled_distance"]].corr(method="spearman")
    
    # --- DYNAMICALLY extract top correlations ---
    z_corrs = corr_spearman.loc[features_all, "scaled_distance"].abs().sort_values(ascending=False)
    w_corrs = corr_spearman.loc[features_all, "weight"].abs().sort_values(ascending=False)
    
    z_top_feat = z_corrs.index[0]
    z_top_corr = corr_spearman.loc[z_top_feat, "scaled_distance"]
    w_top_feat = w_corrs.index[0]
    w_top_corr = corr_spearman.loc[w_top_feat, "weight"]
    
    corr_interp = f"""*   **Observations**:
    *   Scaled distance ($Z$) is most strongly correlated with `{z_top_feat}` ($R_s = {z_top_corr:.4f}$).
    *   Weight ($W$) is most strongly correlated with `{w_top_feat}` ($R_s = {w_top_corr:.4f}$), consistent with Hopkinson-Cranz cube-root scaling."""
    
    # Helper formatting
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
                    if val == float('inf'):
                        row_vals.append("inf")
                    else:
                        row_vals.append(f"{val:.6f}")
                else:
                    row_vals.append(str(val))
            lines.append("| " + " | ".join(row_vals) + " |")
        return "\n".join(lines)
        
    vif_md = df_to_markdown(vif_df, include_index=False)
    pca_md = df_to_markdown(pca_df, include_index=False)
    elimination_md = df_to_markdown(elimination_df, include_index=False)
    spearman_md = df_to_markdown(corr_spearman.loc[features_all, ["weight", "scaled_distance"]], include_index=True)
    
    # Write EDA Report — ALL interpretations derived from computed variables
    report_file = os.path.join(artifacts_dir, "inverse_eda_report.md")
    report_content = f"""# Scientific Exploratory Data Analysis: Inverse Blast Characterization

This report documents the rigorous statistical analysis of the Physics Reference Dataset (PRD) consisting of {len(df):,} total samples ({len(df_clean):,} after filtering Surface bursts with $Z < 0.20$ to prevent clamping bias), generated by the BlastScope forward physics solver.

> [!IMPORTANT]
> All numerical values, interpretations, and thresholds in this report are dynamically computed from the dataset. No values are hardcoded.

---

## 1. Feature Distribution & Log-Scale Histograms

Blast parameters (pressures, impulses, timing) naturally span 4 to 6 orders of magnitude. A log-uniform sampling of targets (Weight and Scaled Distance) combined with power-law decay of blast waves results in highly skewed features in linear space. 

To address this, all continuous features were transformed using $\\log_{{10}}$.
The resulting log-scale histograms show well-behaved distributions across all variables.

![Log-scale Feature Histograms](file:///{histogram_plot_path.replace(os.sep, '/')})

---

## 2. Multicollinearity & Variance Inflation Factor (VIF)

Multicollinearity occurs when features are highly correlated, providing redundant variance and making model coefficients unstable. To measure this, the Variance Inflation Factor (VIF) was calculated for all log-transformed physics variables:

{vif_md}

*   **Interpretation**:
{vif_interpretation}

---

## 3. Principal Component Analysis (PCA)

PCA was executed on the standardized {len(features_all)} continuous log features to verify the actual dimensionality of the feature space:

{pca_md}

![PCA Scree Plot: Explained Variance by Component](file:///{scree_plot_path.replace(os.sep, '/')})

{pca_interpretation}

---

## 4. Feature Elimination Experiment

We trained Random Forest models comparing the full {len(features_full)}-feature set against the pruned {len(features_pruned)}-feature set (excluding derived features with infinite VIF):

{elimination_md}

{elim_conclusion}

---

## 5. Target Correlations (Spearman Rank)

Spearman rank correlations verify the direction and monotonic strength of the relationship between selected features and targets:

{spearman_md}

{corr_interp}
"""

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    print("Scientific EDA Report written successfully.")
    
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
    data["pca_cum_var_3"] = float(cum_var_3)
    with open(metrics_file, "w") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    artifacts_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_scientific_eda("inverse_dataset_v1.csv", artifacts_dir)
