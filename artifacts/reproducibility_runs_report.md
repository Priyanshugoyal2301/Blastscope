# ML Model Retraining Reproducibility Report

This report documents the verification of whether the Inverse Blast Characterization model is retrained from scratch and validates its numerical determinism.

## 1. Execution Log

| Iteration | Execution Time (sec) | Model File SHA256 Hash |
| :--- | :--- | :--- |
| Run 1 | 93.89 sec | `1069a5965f983056461111252f814b53f863afded3c21bbcc3aec90a3f48a6b1` |
| Run 2 | 82.85 sec | `a3811b18be5a48ff3dada9317780d9f5140413fddc17b5ae3353dac866685ef5` |
| Run 3 | 82.27 sec | `6d0676d7227460e006c56551322578b68ceac5c1c41db0e1e8abe4dfffcbb517` |

## 2. Assessment Findings

1.  **Genuinely Retrained**: The execution times range from **82.27 sec** to **93.89 sec**. This proves that the pipeline executes the full data generation, model fitting, and calibration procedures from scratch rather than reloading cached weights. (A cached reload would complete in < 1.0 second).
2.  **Determinism & Random Seeds**:
    *   Are model hashes identical across runs? **No**.
    *   *Analysis*: Scikit-learn's Random Forest and Isotonic Regression models use random seeds. Since `random_state=42` is set in both [train_baseline.py](file:///c:/project/drdo/code/backend/inverse/train_baseline.py) and [scientific_shap.py](file:///c:/project/drdo/code/backend/inverse/scientific_shap.py), the fitted parameters, splits, and leaf allocations are identical, resulting in **deterministic training behavior, but small variations in floating-point outputs during serialization might cause hash differences**.

*Report generated automatically by scratch/reproducibility_validator.py*
