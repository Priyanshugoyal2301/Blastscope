# Scientific Uncertainty Quantification & Isotonic Calibration Report

This report evaluates and calibrates the confidence score returned by the Inverse Blast Characterization module using isotonic probability calibration.

---

## 1. Monotonicity & Correlation Analysis

We evaluate the correlation between true prediction error (average relative error of $W$ and $Z$) and two uncertainty metrics:

| Metric | Spearman Rank Correlation | Pearson Correlation |
| --- | --- | --- |
| Physics-Consistency Discrepancy | 0.999461 | 0.995373 |
| Ensemble Tree Variance | 0.554148 | 0.519109 |

### Rationale:
*   **Physics-Consistency Discrepancy** exhibits a Spearman rank correlation of **0.999461** (nearly perfect monotonicity). 
*   **Ensemble Tree Variance** has a much lower Spearman correlation (**0.554148**), indicating that model tree variance is a weaker indicator of true error under highly constrained physics curves.

---

## 2. Isotonic Calibration Calibration

We map the physics-consistency discrepancy $e_{phys}$ to a probability of successful prediction (defined as having a relative error $\le 10\%$) using **Isotonic Regression**. This ensures that the returned confidence score has a direct empirical definition:
> **A confidence score of $C\%$ means that empirically, $C\%$ of predictions with similar physical discrepancies fall within a $10\%$ relative error bound.**

### Empirical Calibration Performance (deciles/bins):

| Confidence Bin (%) | Samples | Empirical Success Probability (%) | Mean Rel Error (%) | 95th Percentile Error (%) |
| --- | --- | --- | --- | --- |
| 90% - 100% | 957 | 100.000000 | 1.740461 | 6.262148 |
| 50% - 70% | 3 | 66.666667 | 9.344158 | 10.011676 |
| 0% - 50% | 40 | 15.000000 | 13.462790 | 21.931613 |

*   **Coverage Verification**: For the **90% - 100%** confidence bin, the actual percentage of samples with error $\le 10\%$ is **100.00%**, with a mean relative error of **1.74%**.
*   This validates that the confidence score is calibrated and represents a true probability of prediction coverage.

---

## 3. Calibration Curve Visualization

The figure below shows the fitted isotonic curve mapping the continuous physical discrepancy to the probability-calibrated confidence score:

![Isotonic Calibration Curve](file:///./plots/confidence_calibration.png)

---

## 4. OOD & Parameterized Envelope Definition

We extract the training boundaries and continuous feature covariance from the clean reference dataset:
*   **Weight training range**: $[0.10, 9998.78]$ kg TNT.
*   **Scaled distance range**: $[0.060, 39.998]$ $m/\text{kg}^{1/3}$.
*   **Mahalanobis Covariance Contours**: Stored mean vector $\mu$ and inverse covariance matrix $\Sigma^{-1}$ to calculate the 99.9% Chi-squared boundary ($D^2 > 22.46$).

This ensures OOD checks are completely parameterized and future-proof.
