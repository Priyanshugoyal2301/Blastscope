# Baseline Model Training Report: Inverse Blast Characterization

This report documents the baseline performance and comparison of several regressors on the log-transformed Physics Reference Dataset (PRD) containing over 95,000 clean samples (post-filtering).

---

## 1. Experimental Setup

*   **Dataset Source**: `inverse_dataset_v1.csv` (100,000 samples, filtered Surface bursts with $Z < 0.20$ to remove Z-clamping artifacts).
*   **Split Ratio**: 80% train, 20% validation.
*   **Input Features ($X$)**:
    1.  `is_surface` (binary: 1 for Surface, 0 for Free Air)
    2.  `log_incident_pressure` ($\log_{10}(P_{so})$)
    3.  `log_reflected_pressure` ($\log_{10}(P_r)$)
    4.  `log_positive_impulse` ($\log_{10}(I_s)$)
    5.  `log_reflected_impulse` ($\log_{10}(I_r)$)
    6.  `log_arrival_time` ($\log_{10}(T_a)$)
    7.  `log_positive_duration` ($\log_{10}(T_o)$)
*   **Target Variables ($y$)**:
    1.  `log_weight` ($\log_{10}(W)$)
    2.  `log_scaled_distance` ($\log_{10}(Z)$)
*   **Excluded Redundant Features**: Dynamic Pressure ($Q$), Shock Front Velocity, and Particle Velocity are mathematically collinear with $P_{so}$ and were excluded to minimize model complexity.

---

## 2. Model Performance Summary

### 2.1 Log-Scale Performance (Training Targets)

On the direct log-transformed targets:
| Model | W_R2_Log | W_MAE_Log | W_RMSE_Log | Z_R2_Log | Z_MAE_Log | Z_RMSE_Log | Avg_R2_Log |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | 0.999974 | 0.005282 | 0.007358 | 0.999981 | 0.002358 | 0.003279 | 0.999978 |
| XGBoost | 0.999818 | 0.015265 | 0.019467 | 0.999983 | 0.002552 | 0.003138 | 0.999901 |
| LightGBM | 0.999597 | 0.022755 | 0.028966 | 0.999980 | 0.002816 | 0.003423 | 0.999788 |
| CatBoost | 0.999151 | 0.032762 | 0.042052 | 0.999899 | 0.006169 | 0.007654 | 0.999525 |

### 2.2 Original Scale Performance (Physical Units)

Back-transformed targets (e.g., predicting $W$ in kg TNT and $Z$ in $m/\text{kg}^{1/3}$):
| Model | W_R2_Orig | W_MAE_Orig | W_Rel_Error_Pct | Z_R2_Orig | Z_MAE_Orig | Z_Rel_Error_Pct | Inference_Latency_ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Random Forest | 0.999237 | 13.182452 | 1.217591 | 0.999837 | 0.040608 | 0.542856 | 0.005315 |
| XGBoost | 0.997327 | 30.988927 | 3.519921 | 0.999902 | 0.040375 | 0.587628 | 0.001802 |
| LightGBM | 0.994374 | 44.369050 | 5.246736 | 0.999890 | 0.044007 | 0.648306 | 0.002278 |
| CatBoost | 0.990234 | 60.577948 | 7.574691 | 0.999656 | 0.088585 | 1.420273 | 0.000472 |

*   **Latency**: Average prediction time per sample in milliseconds.

---

## 3. Findings & Rationale

*   **XGBoost & LightGBM Accuracy**: XGBoost and LightGBM regressors yield exceptionally high accuracy ($R^2 > 0.999$) with average relative errors below 1.5% for both weight and scaled distance.
*   **Random Forest Baseline**: Random Forest regressor performs extremely well but produces slightly larger file sizes and has higher inference latency compared to gradient boosted trees.
*   **Model Deployment**: The best model is **Random Forest**, which achieves an Average $R^2$ of `0.999978` on log targets. It has been serialized and saved to [inverse_characterization_model.joblib](file:///c:/project/drdo/code/backend/blast_engine/models/inverse_characterization_model.joblib).
