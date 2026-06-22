# Holdout & Extrapolation Validation Report

This report documents the rigorous generalization validation of the Inverse Blast Characterization module. We evaluate the model's performance on holdout regimes to identify extrapolation boundaries and physical limitations.

> [!IMPORTANT]
> All numerical values, status classifications, and interpretations in this report are dynamically computed from actual model predictions. No values are hardcoded. The status classification uses a multi-tier system: EXCELLENT ($R^2 \ge 0.90$), ACCEPTABLE ($R^2 \ge 0.70$), POOR ($R^2 \ge 0.30$), VERY POOR ($R^2 \ge 0.0$), FAILED ($R^2 < 0.0$).

---

## 1. Holdout Validation Performance

The Separate Trees Random Forest model was evaluated across 4 holdout experiments testing extrapolation boundaries (unseen ranges of weight and scaled distance) and domain shifts (unseen burst types):

| Experiment | Metric | Train_Samples | Test_Samples | R2_Score | MAE | Rel_Error_% | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W Extrapolation (Train W ≤ 1000, Test W > 1000) | Weight (W) kg TNT | 72460 | 18236 | -3.619953 | 2998.962761 | 65.224765 | FAILED |
| Z Extrapolation (Train Z ≥ 0.5, Test Z < 0.5) | Scaled Distance (Z) | 67456 | 23240 | -2.143349 | 0.256186 | 190.103687 | FAILED |
| Cross-Regime (Train Surface, Test Free Air) | Weight (W) kg TNT | 40696 | 50000 | 0.938763 | 341.777159 | 163.046492 | EXCELLENT |
| Cross-Regime (Train Free Air, Test Surface) | Weight (W) kg TNT | 50000 | 40696 | 0.977090 | 384.395090 | 62.575739 | EXCELLENT |

**Overall Verdict**: 2/4 experiments pass, 2/4 show poor generalization. The failing experiments identify specific extrapolation boundaries that the production model must cover via full-range training.

---

## 2. Key Scientific Findings & Limitations

### 2.1 Weight Extrapolation (W > 1000 kg TNT)
*   **Status**: `FAILED` — Model performs worse than a constant mean predictor for W > 1000 kg TNT ($R^2 = -3.6200$, MAE = 2998.96). This confirms the model cannot extrapolate beyond its training range.
*   **Train Samples**: 72,460 | **Test Samples**: 18,236
*   **Physical & ML Rationale**: Decision-tree regressors (Random Forest, XGBoost, LightGBM) cannot predict values outside the range of their training targets. The trees partition the feature space and assign constant predictions at leaf nodes. Consequently, any threat larger than the training maximum is predicted as approximately the training maximum.
*   **Mitigation**: The production model must be trained on the full envelope $[0.1, 10000.0]$ kg TNT. The model should never be evaluated on inputs suspected to exceed its training boundaries.

### 2.2 Scaled Distance Extrapolation (Z < 0.5)
*   **Status**: `FAILED` — Model performs worse than a constant mean predictor for Z < 0.5 ($R^2 = -2.1433$, MAE = 0.26). This confirms the model cannot extrapolate beyond its training range.
*   **Train Samples**: 67,456 | **Test Samples**: 23,240
*   **Physical & ML Rationale**: Near-field blast physics ($Z < 0.5$) exhibits highly non-linear shock wave propagation, where chemical reaction kinetics and gas expansions dominate before transition to standard acoustic shock behavior. Decision trees cannot extrapolate these steep, non-linear curves into the near-field.
*   **Mitigation**: The training dataset must span the full physical range $[0.06, 40.0]$ $m/\text{kg}^{1/3}$ to guarantee near-field coverage.

### 2.3 Cross-Regime Domain Shifts (Surface vs. Free Air)
*   **Surface → Free Air**: `EXCELLENT` — Model generalizes well to Free Air from Surface-trained model ($R^2 = 0.9388$, MAE = 341.78).
    *   Train Samples: 40,696 | Test Samples: 50,000
*   **Free Air → Surface**: `EXCELLENT` — Model generalizes well to Surface from Free-Air-trained model ($R^2 = 0.9771$, MAE = 384.40).
    *   Train Samples: 50,000 | Test Samples: 40,696
*   **Physical Rationale**: At identical scaled distances, Surface bursts generate significantly higher incident impulses and pressures than Free-Air bursts due to ground reflections absorbing and redirecting energy. 
    *   If a model trained only on Surface bursts evaluates Free-Air blast parameters, it will **underestimate** the charge weight (since Free-Air parameters are smaller for the same weight).
    *   If a model trained only on Free-Air bursts evaluates Surface blast parameters, it will **overestimate** the charge weight.
*   **Mitigation**: The model must incorporate `is_surface` as a primary binary feature and train on an equal mix of both burst types. The end-user must specify the burst type in the Predict screen to ensure correct physical scaling is applied.
