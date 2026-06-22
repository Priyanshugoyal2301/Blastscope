# ML Model Data Leakage Assessment Report

This report documents the audit of potential data leakage, target leakage, and memorization within the Inverse Blast Characterization model dataset.

## 1. Leakage Audit Checks

| Leakage Check | Metric / Status | Verification Verdict |
| :--- | :--- | :--- |
| **Raw Row Duplicates** | 0 duplicate rows | **PASS** (Zero identical records exist in the generated dataset) |
| **Feature Space Duplicates** | 0 rows with identical inputs | **PASS** (Input space features are unique across the dataset) |
| **Train/Test Set Overlap** | 0 overlapping feature rows | **PASS** (No identical feature vectors exist in both train and test sets) |
| **Target Variable Leakage** | Weight: `False`, Scaled Distance: `False` | **PASS** (Targets do not appear in the input feature space) |
| **Physical Standoff Leakage** | Standoff Distance ($R$) in features: `False` | **PASS** (Physical distance $R$ is excluded to prevent trivial R-to-Z solving) |

## 2. Methodology & Scientific Review

### 2.1 Order of Preprocessing
*   **Split Order**: In [train_baseline.py](file:///c:/project/drdo/code/backend/inverse/train_baseline.py#L40-L68), the dataset is cleaned, and features are computed before splitting.
*   **Leakage Risk**: The preprocessing is limited to **row-wise** monotonic transformations (log-scaling) and boolean mapping. Since **no dataset-wide aggregations** (such as mean scaling, min-max standardizations, or PCA parameter calculations) are applied before the split, there is zero statistical leakage.

### 2.2 Input-Target Feature Independence
*   **Feature Space Isolation**: Features are restricted to sensor readings ($P_{so}$, $P_r$, $I_s$, $I_r$, $T_a$, $T_o$). Target variables $W$ (charge weight) and $Z$ (scaled distance) are completely hidden.
*   **Omission of Physical Distance ($R$)**: Physical standoff distance $R$ is excluded. Because scaled distance $Z$ is defined as $Z = R / W^0.3333333333333333$, including $R$ in the features would allow the model to easily solve the algebraic relation. Excluding $R$ forces the model to rely solely on the physical shock wave decay signatures.

### 2.3 R² Explanation (0.999974 and 0.999981)
*   **Governing Equation Determinism**: The Physics Reference Dataset (PRD) is generated using the Kingery-Bulmash equations, which are highly deterministic closed-form polynomial fits. Because there is no random experimental variance, structural thermal turbulence, or measurement noise in the baseline dataset, the model is learning a smooth, clean mathematical mapping, explaining the near-perfect R² score.
*   **Is it memorization?**: No, the validation set is completely independent. Random Forest regressors are tested on out-of-sample data and achieve high validation performance due to the smoothness of the underlying physical function.

*Report saved automatically during leakage audit verification.*
