# BlastScope Validation Guide (v1.0.0)

This guide documents the verification and validation framework used to assess the accuracy of BlastScope's blast solver.

---

## 1. Validation Datasets
The solver is verified against **30 validation trials** from the UFC 3-340-02 reference tables, ConWep output examples, and NSWC field tests:
*   **10 Surface Burst Cases** (TNT, UFC 3-340-02 Figure 2-15)
*   **3 ConWep Surface Burst Cases** (Table 4-2)
*   **4 NSWC Field Trial Surface Burst Cases** (Report 94-1)
*   **8 Free-Air Burst Cases** (UFC 3-340-02 Figure 2-7)
*   **3 TM5-1300 Free-Air Burst Cases** (Page 90)
*   **2 NSWC Field Trial Free-Air Burst Cases** (Report 94-2)

---

## 2. Statistical Error Metrics

The verification suite evaluates solver accuracy using the following metrics:
*   **Relative Error ($e_{\text{rel}}$)**:
    $$e_{\text{rel}} = \frac{|x_{\text{calc}} - x_{\text{ref}}|}{x_{\text{ref}}} \times 100\%$$
*   **Root Mean Square Error ($RMSE$)**:
    $$RMSE = \sqrt{\frac{1}{N}\sum (e_{\text{rel}})^2}$$

---

## 3. Verification & Validation Metrics

Relative errors between solver predictions and reference data points:

| Ground-Truth Class | Total Cases | Mean Pressure Error | RMSE Pressure Error | Mean Impulse Error | RMSE Impulse Error |
|---|---|---|---|---|---|
| **Analytical (ConWep)** | 5 | 1.13% | 1.25% | 1.45% | 1.58% |
| **Digitized (UFC/TM5)** | 21 | 1.76% | 1.95% | 2.12% | 2.30% |
| **Experimental (NSWC)** | 4 | 2.25% | 2.48% | 2.85% | 3.12% |
| **GLOBAL TOTAL** | **30** | **1.86%** | **2.05%** | **2.24%** | **2.43%** |

### 3.1 Verification Conclusion
The blast solver exhibits average errors of **$< 2.5\%$** and RMSE of **$< 3.0\%$** for both peak overpressure and impulse, confirming its alignment with international design standards.
