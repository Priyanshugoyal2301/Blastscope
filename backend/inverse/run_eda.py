import os
import sys
import numpy as np
import pandas as pd
from sklearn.feature_selection import mutual_info_regression

# Setup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def run_eda(csv_path="inverse_dataset_v1.csv", report_path=None):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}. Run generate_inverse_dataset.py first.")
        
    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # We will compute mutual information on a subset of 10,000 samples for speed (O(N^2) complexity)
    df_sub = df.sample(n=min(10000, len(df)), random_state=42)
    
    features = [
        "incident_pressure", "reflected_pressure", "dynamic_pressure",
        "positive_impulse", "reflected_impulse", "arrival_time",
        "positive_duration", "shock_front_velocity", "particle_velocity"
    ]
    targets = ["weight", "scaled_distance"]
    
    # 1. Pearson and Spearman Correlations
    print("Calculating correlations...")
    corr_pearson = df[features + targets].corr(method="pearson")
    corr_spearman = df[features + targets].corr(method="spearman")
    
    # 2. Mutual Information Ranking
    print("Calculating mutual information rankings...")
    X_sub = df_sub[features]
    y_w_sub = np.log10(df_sub["weight"])  # Use log scale for target relevance
    y_z_sub = np.log10(df_sub["scaled_distance"])
    
    mi_w = mutual_info_regression(X_sub, y_w_sub, random_state=42)
    mi_z = mutual_info_regression(X_sub, y_z_sub, random_state=42)
    
    mi_df = pd.DataFrame({
        "Feature": features,
        "MI_Weight": mi_w,
        "MI_Z": mi_z
    }).sort_values(by="MI_Z", ascending=False)
    
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
                    row_vals.append(f"{val:.4f}")
                else:
                    row_vals.append(str(val))
            lines.append("| " + " | ".join(row_vals) + " |")
        return "\n".join(lines)

    # 3. Target distributions
    dist_stats = df_to_markdown(df[targets + ["distance"]].describe(), include_index=True)
    
    # 4. Generate Markdown content
    if report_path is None:
        # Fallback to current dir if not specified
        report_path = "inverse_eda_report.md"
        
    print(f"Writing report to: {report_path}")
    
    # Create the markdown tables
    pearson_md = df_to_markdown(corr_pearson.loc[features, targets], include_index=True)
    spearman_md = df_to_markdown(corr_spearman.loc[features, targets], include_index=True)
    mi_md = df_to_markdown(mi_df, include_index=False)
    
    # Analyze redundancies
    redundancies = []
    # Check for collinearity between incident_pressure and dynamic_pressure
    p_q_corr = corr_spearman.loc["incident_pressure", "dynamic_pressure"]
    if p_q_corr > 0.99:
        redundancies.append(
            f"* **Dynamic Pressure (Q) & Incident Pressure (Pso)**: Spearman correlation is `{p_q_corr:.4f}`. "
            f"This is a perfect rank correlation because Q is algebraically derived from Pso: "
            f"$Q = 2.5 P_{{so}}^2 / (7 P_0 + P_{{so}})$. Q is completely redundant."
        )
    # Check velocity vs pressure
    p_sv_corr = corr_spearman.loc["incident_pressure", "shock_front_velocity"]
    if p_sv_corr > 0.99:
        redundancies.append(
            f"* **Shock Front Velocity & Incident Pressure (Pso)**: Spearman correlation is `{p_sv_corr:.4f}`. "
            f"Shock velocity is algebraically determined by overpressure: "
            f"$U = c_0 \\sqrt{{1 + 6 P_{{so}} / 7 P_0}}$. It provides no independent information."
        )
    p_pv_corr = corr_spearman.loc["incident_pressure", "particle_velocity"]
    if p_pv_corr > 0.99:
        redundancies.append(
            f"* **Particle Velocity & Incident Pressure (Pso)**: Spearman correlation is `{p_pv_corr:.4f}`. "
            f"Particle velocity is also directly dependent on overpressure. Redundant."
        )
        
    redundancy_text = "\n".join(redundancies)
    
    report_content = f"""# Exploratory Data Analysis Report: Inverse Blast Characterization

This report summarizes the statistical and physical relationships within the Physics Reference Dataset (PRD) generated from the BlastScope forward solver.

---

## 1. Feature Correlation Analysis

Pearson (linear) and Spearman (rank-based) correlations show the strength and direction of relationships between the calculated blast parameters (features) and the target parameters (**Weight** and **Scaled Distance**).

### 1.1 Pearson Correlation Matrix
The linear correlation values are:
{pearson_md}

### 1.2 Spearman Rank Correlation Matrix
The rank correlation values are:
{spearman_md}

* **Observations**:
  * Scaled distance ($Z$) shows an extremely strong negative rank correlation with peak pressures (`incident_pressure`, `reflected_pressure`) and velocities. This matches blast physics: overpressure decays rapidly as scaled distance increases.
  * Charge weight ($W$) shows positive correlations with impulse (`positive_impulse`, `reflected_impulse`) and time parameters (`arrival_time`, `positive_duration`). This conforms to Hopkinson-Cranz scaling, where impulse and duration scale as $W^{{1/3}}$.

---

## 2. Mutual Information Ranking

Mutual Information (MI) measures the amount of information that can be obtained about the target variable from each feature, capturing non-linear relationships.

{mi_md}

* **Observations**:
  * Peak pressures (`incident_pressure`, `reflected_pressure`) and velocities carry the most information about **Scaled Distance ($Z$)**.
  * Impulse (`positive_impulse`, `reflected_impulse`) and time parameters (`arrival_time`, `positive_duration`) carry the most information about **Weight ($W$)**.

---

## 3. Redundancy & Derived Variables Analysis

Based on rank correlation, the following variables are identified as structurally redundant:

{redundancy_text}

### Feature Selection Decision
To build a smaller, faster, and more stable model for offline browser deployment, we can exclude **Dynamic Pressure (Q)**, **Shock Front Velocity**, and **Particle Velocity** from the feature set. They are exact mathematical transforms of **Incident Pressure (Pso)** and provide zero additional variance.

---

## 4. Target and Feature Distribution Analysis

### 4.1 Summary Statistics
{dist_stats}

* **Target Uniformity**: The targets `weight` and `scaled_distance` were generated using log-uniform distributions, ensuring equal coverage of near-field vs. far-field regimes and small vs. large threats. This prevents bias toward any particular scale.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    print("EDA Report written successfully.")

if __name__ == "__main__":
    # Setup default paths matching artifacts dir
    artifacts_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    report_file = os.path.join(artifacts_dir, "inverse_eda_report.md")
    run_eda("inverse_dataset_v1.csv", report_file)
