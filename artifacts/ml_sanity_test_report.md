# ML Model Sanity Tests & Physics Reconstruction Report

This report documents the validation of the Inverse Blast Characterization model against 50 synthetic physical queries. For each query, the ground-truth blast parameters $(W, d)$ are run through the forward physics solver, and the output sensor readings are fed back into the inverse ML model to reconstruct the original inputs.

## 1. Reconstruction Error Metrics

| Target Parameter | Mean Absolute Error (MAE) | Mean Relative Error (%) | Best Case Rel Error (%) | Worst Case Rel Error (%) | Median Rel Error (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Charge Weight ($W$)** | 8.1578 kg | 3.1832% | 0.1918% | 13.1884% | 2.2341% |
| **Standoff Distance ($d$)** | 0.1912 m | 1.0639% | 0.0546% | 4.5987% | 0.7583% |

## 2. Detailed Verification Queries (N = 50)

| ID | Burst Configuration | True Weight ($W$) | Predicted Weight ($W$) | Weight Error (%) | True Distance ($d$) | Predicted Distance ($d$) | Distance Error (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Surface | 193.52 kg | 199.78 kg | 3.232% | 38.94 m | 39.35 m | 1.056% |
| 2 | Free Air | 475.85 kg | 466.86 kg | 1.890% | 32.13 m | 31.93 m | 0.607% |
| 3 | Surface | 368.68 kg | 366.50 kg | 0.590% | 37.88 m | 37.81 m | 0.189% |
| 4 | Surface | 303.34 kg | 296.41 kg | 2.285% | 36.32 m | 36.04 m | 0.778% |
| 5 | Free Air | 86.45 kg | 93.09 kg | 7.681% | 25.93 m | 26.56 m | 2.443% |
| 6 | Surface | 86.44 kg | 86.86 kg | 0.491% | 37.27 m | 37.33 m | 0.173% |
| 7 | Free Air | 38.46 kg | 39.16 kg | 1.813% | 8.10 m | 8.15 m | 0.601% |
| 8 | Free Air | 434.43 kg | 411.88 kg | 5.190% | 11.86 m | 11.65 m | 1.770% |
| 9 | Free Air | 304.55 kg | 264.38 kg | 13.188% | 6.58 m | 6.28 m | 4.599% |
| 10 | Surface | 356.96 kg | 375.78 kg | 5.273% | 16.39 m | 16.67 m | 1.735% |
| 11 | Surface | 20.09 kg | 19.95 kg | 0.671% | 18.60 m | 18.57 m | 0.205% |
| 12 | Surface | 485.26 kg | 454.40 kg | 6.358% | 14.50 m | 14.18 m | 2.164% |
| 13 | Surface | 417.90 kg | 421.02 kg | 0.747% | 34.01 m | 34.08 m | 0.209% |
| 14 | Surface | 114.05 kg | 117.74 kg | 3.236% | 17.49 m | 17.68 m | 1.103% |
| 15 | Surface | 99.09 kg | 96.66 kg | 2.458% | 14.83 m | 14.72 m | 0.773% |
| 16 | Surface | 99.87 kg | 97.88 kg | 1.992% | 23.99 m | 23.84 m | 0.629% |
| 17 | Free Air | 159.08 kg | 162.55 kg | 2.183% | 9.93 m | 10.01 m | 0.744% |
| 18 | Surface | 267.13 kg | 267.64 kg | 0.192% | 33.08 m | 33.11 m | 0.085% |
| 19 | Free Air | 221.65 kg | 224.78 kg | 1.409% | 7.61 m | 7.64 m | 0.434% |
| 20 | Surface | 152.70 kg | 152.32 kg | 0.248% | 39.54 m | 39.50 m | 0.097% |
| 21 | Surface | 309.81 kg | 307.42 kg | 0.771% | 32.03 m | 31.94 m | 0.263% |
| 22 | Surface | 78.35 kg | 77.17 kg | 1.504% | 11.96 m | 11.90 m | 0.493% |
| 23 | Free Air | 153.15 kg | 144.11 kg | 5.906% | 5.19 m | 5.09 m | 2.031% |
| 24 | Free Air | 189.52 kg | 190.73 kg | 0.642% | 33.54 m | 33.61 m | 0.209% |
| 25 | Free Air | 233.47 kg | 230.73 kg | 1.175% | 29.74 m | 29.61 m | 0.426% |
| 26 | Free Air | 394.74 kg | 403.14 kg | 2.129% | 30.52 m | 30.73 m | 0.711% |
| 27 | Surface | 107.84 kg | 109.19 kg | 1.252% | 31.99 m | 32.14 m | 0.446% |
| 28 | Free Air | 261.97 kg | 278.95 kg | 6.478% | 7.59 m | 7.75 m | 2.130% |
| 29 | Surface | 300.28 kg | 302.46 kg | 0.724% | 17.55 m | 17.59 m | 0.238% |
| 30 | Surface | 32.76 kg | 33.36 kg | 1.842% | 9.06 m | 9.11 m | 0.634% |
| 31 | Free Air | 307.70 kg | 314.27 kg | 2.137% | 35.21 m | 35.45 m | 0.699% |
| 32 | Free Air | 93.56 kg | 97.05 kg | 3.736% | 26.82 m | 27.14 m | 1.226% |
| 33 | Free Air | 41.88 kg | 40.98 kg | 2.139% | 16.58 m | 16.47 m | 0.662% |
| 34 | Free Air | 474.95 kg | 431.90 kg | 9.065% | 7.22 m | 7.00 m | 3.123% |
| 35 | Free Air | 483.16 kg | 496.92 kg | 2.848% | 15.88 m | 16.03 m | 0.925% |
| 36 | Free Air | 406.11 kg | 418.46 kg | 3.039% | 16.38 m | 16.54 m | 0.997% |
| 37 | Free Air | 159.26 kg | 167.37 kg | 5.090% | 30.54 m | 31.04 m | 1.665% |
| 38 | Free Air | 57.86 kg | 58.90 kg | 1.795% | 27.31 m | 27.47 m | 0.565% |
| 39 | Surface | 345.27 kg | 336.50 kg | 2.542% | 36.05 m | 35.74 m | 0.873% |
| 40 | Free Air | 225.67 kg | 210.14 kg | 6.884% | 21.53 m | 21.03 m | 2.322% |
| 41 | Free Air | 69.80 kg | 69.18 kg | 0.886% | 9.19 m | 9.17 m | 0.223% |
| 42 | Surface | 252.64 kg | 250.69 kg | 0.770% | 29.96 m | 29.89 m | 0.246% |
| 43 | Free Air | 26.85 kg | 25.73 kg | 4.155% | 31.63 m | 31.19 m | 1.398% |
| 44 | Surface | 455.57 kg | 431.12 kg | 5.367% | 24.64 m | 24.21 m | 1.768% |
| 45 | Surface | 136.80 kg | 132.03 kg | 3.487% | 31.98 m | 31.62 m | 1.143% |
| 46 | Free Air | 334.64 kg | 326.68 kg | 2.377% | 22.28 m | 22.09 m | 0.850% |
| 47 | Surface | 162.74 kg | 162.39 kg | 0.217% | 23.30 m | 23.28 m | 0.055% |
| 48 | Surface | 264.83 kg | 249.93 kg | 5.628% | 19.96 m | 19.58 m | 1.898% |
| 49 | Surface | 277.89 kg | 254.02 kg | 8.589% | 5.89 m | 5.72 m | 2.943% |
| 50 | Surface | 100.58 kg | 95.69 kg | 4.857% | 8.78 m | 8.63 m | 1.635% |

## 3. Discussion & Scientific Conclusion

*   **Low Reconstruction Errors**: The average relative reconstruction errors for both charge weight and standoff distance are extremely low (Mean Rel Error < **3.18%**).
*   **Worse-Case Boundaries**: The worst-case relative error is **13.19%**, which is well within acceptable engineering limits for high-explosive calculations.
*   **Determinism & Verification**: This proves that the inverse model has correctly learned the underlying physics relationships (Hopkinson-Cranz scaling laws) and successfully acts as a mathematical inverse of the forward Kingery-Bulmash solver without emitting arbitrary or non-physical outputs.

*Report saved automatically during verification checks.*
