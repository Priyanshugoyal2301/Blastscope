# Noise Robustness & Dataset Qualification Report

This report documents the statistical validation of the noisy dataset and measures the performance degradation of the production independent Random Forest regressors under realistic sensor noise.

> [!IMPORTANT]
> All numerical values and interpretations in this report are dynamically computed from actual K-S test results, model predictions, and statistical analyses. No values are hardcoded.

---

## 1. Noise Qualification Statistics

Relative uniform noise was injected directly into the physics solver parameters to simulate field measurements:
*   **Incident, Reflected, Dynamic Pressure**: $\pm 5\%$
*   **Incident and Reflected Impulse**: $\pm 3\%$
*   **Arrival Time, Positive Duration**: $\pm 2\%$
*   **Shock and Particle Velocity**: $\pm 3\%$

To qualify that the noise injection does not introduce mean shifts or statistically distort the physical parameter domains, we compute shifts and run the **Kolmogorov-Smirnov (K-S) two-sample test** on the clean vs. noisy populations:

| Parameter | Clean_Mean | Noisy_Mean | Mean_Shift_Pct | Clean_Std | Noisy_Std | Std_Shift_Pct | KS_Statistic | KS_p_value |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| incident_pressure | 4775.244661 | 4774.386542 | -0.017970 | 9336.027080 | 9336.949468 | 0.009880 | 0.001588 | 0.999840 |
| reflected_pressure | 51043.587539 | 51067.670259 | 0.047181 | 110963.991018 | 111123.821640 | 0.144038 | 0.001665 | 0.999598 |
| dynamic_pressure | 11221.043960 | 11221.114346 | 0.000627 | 22860.001374 | 22877.608585 | 0.077022 | 0.001632 | 0.999725 |
| positive_impulse | 955.128319 | 955.204878 | 0.008016 | 2460.981019 | 2461.488092 | 0.020604 | 0.000706 | 1.000000 |
| reflected_impulse | 18076.370203 | 18071.207368 | -0.028561 | 68915.699728 | 68897.634682 | -0.026213 | 0.000529 | 1.000000 |
| arrival_time | 84.845745 | 84.854784 | 0.010653 | 213.950858 | 213.987460 | 0.017108 | 0.000419 | 1.000000 |
| positive_duration | 14.900594 | 14.900970 | 0.002527 | 23.058628 | 23.062963 | 0.018801 | 0.000474 | 1.000000 |
| shock_front_velocity | 1475.776016 | 1475.837610 | 0.004174 | 1616.356533 | 1616.862577 | 0.031308 | 0.055449 | 0.000000 |
| particle_velocity | 1071.897566 | 1071.966236 | 0.006406 | 1432.727685 | 1433.217612 | 0.034195 | 0.001665 | 0.999598 |

*   **Interpretation**:
    *   **Sample Sizes**: Clean N = 90,696, Noisy N = 90,696. At these sample sizes, the K-S test has extremely high statistical power, meaning even tiny distributional shifts will be detected as significant.
    *   **Mean Shifts**: Maximum absolute mean shift is `0.0472%` (feature: `reflected_pressure`). This confirms the noise injection is symmetric and approximately zero-mean.
    *   **Std Shifts**: Maximum absolute standard deviation shift is `0.1440%` (feature: `reflected_pressure`). This matches the expected spread of uniform distribution perturbations.
    *   **K-S Test Results**: 1/9 features are statistically significant (p < 0.05): `shock_front_velocity`.
    *   8/9 features are non-significant (p ≥ 0.05): `incident_pressure`, `reflected_pressure`, `dynamic_pressure`, `positive_impulse`, `reflected_impulse`, `arrival_time`, `positive_duration`, `particle_velocity`.
    *   The largest K-S statistic is `0.055449` (feature: `shock_front_velocity`).
    *   **Verdict**: Some features show K-S statistics above 0.05. Manual review of the affected features is recommended.

![Clean vs Noisy Distributions Overlay](file:///./plots/clean_vs_noisy_distributions.png)

---

## 2. Model Performance Degradation Analysis

To assess real-world viability, the production Separate Trees Random Forest model trained on the **clean** dataset (N = 90,696) was evaluated on the **noisy** validation test set (simulating deployment on noisy field sensors):

| Target | Clean_R2 | Noisy_R2 | R2_Degradation | Clean_MAE | Noisy_MAE | Clean_RelErr_% | Noisy_RelErr_% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Weight (W) kg TNT | 0.999470 | 0.999374 | 0.000096 | 41.204435 | 48.616528 | 4.827911 | 5.789818 |
| Scaled Distance (Z) | 1.000000 | 0.999936 | 0.000064 | 0.001710 | 0.081605 | 0.023117 | 1.097453 |

*   **Interpretation**:
    *   **Weight ($W$)**: $R^2$ drops from `0.999470` (clean) to `0.999374` (noisy), a degradation of `0.000096`. Relative error shifts from `4.83%` to `5.79%`. MAE changes from `41.20` to `48.62` kg TNT.
    *   **Scaled Distance ($Z$)**: $R^2$ drops from `1.000000` (clean) to `0.999936` (noisy), a degradation of `0.000064`. Relative error shifts from `0.02%` to `1.10%`.
    *   **Verdict**: Both targets show $R^2$ degradation < 0.01, confirming the model is **highly robust** to the specified sensor noise levels.
    *   **General Rationale**: Standardizing input parameters via $\log_{10}$ scaling and using pruned features ($Q$ and velocities excluded) prevents individual high-pressure errors from dominating predictions. Independent estimators prevent joint variance leakage.
