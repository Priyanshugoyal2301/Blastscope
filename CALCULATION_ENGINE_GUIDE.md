# BlastScope Calculation Engine Guide (v1.0.0)

This document details the mathematical formulations and execution pipelines of BlastScope's physics calculations.

---

## 1. Calculation Pipeline

The calculation pipeline resolves detonation parameters in three stages:

```
[ det_weight, distance, burst, agent ] 
                 |
                 v
      [ Dual TNT Equivalence ]
    (Compute W_p, W_i, and W_g)
                 |
                 v
   [ Standoff Distance Scaling ]
    (Compute Z_p, Z_i, and Z_g)
                 |
                 v
[ Swisdak Polynomial Fitting Curves ]
    (Lookup coefficients based on Z)
                 |
                 v
[ Overpressure & Impulse Parameters ]
```

---

## 2. Mathematical Formulations

### 2.1 Standoff Scaling
$$\text{Scaled Distance: } Z = \frac{R}{W^{1/3}}$$
*   $R$: Standoff range ($m$)
*   $W$: TNT-equivalent weight ($kg$)

### 2.2 Dual TNT Equivalency
Different explosive compounds release energy at different rates. The engine uses separate factors for pressure ($e_p$) and impulse ($e_i$) to resolve chemical differences:
$$W_p = W_{\text{actual}} \times e_p$$
$$W_i = W_{\text{actual}} \times e_i$$
$$W_g = W_{\text{actual}} \times e_g$$

### 2.3 Swisdak Polynomial Fitting Curves
Shock parameters are evaluated using Swisdak (1994) fitting curves:
$$U = \ln(Z)$$
$$\ln(Y) = C_0 + C_1 U + C_2 U^2 + C_3 U^3 + C_4 U^4$$
Where $Y$ is pressure ($kPa$), impulse ($kPa\cdot ms$), arrival time ($ms$), or positive duration ($ms$), and $C_i$ represents burst-specific fitting coefficients.

### 2.4 Pressure Reflection
Peak reflected pressure ($P_r$) under normal incidence is computed using Rankine-Hugoniot relationships:
$$P_r = 2 P_{so} \left( \frac{7 P_0 + 4 P_{so}}{7 P_0 + P_{so}} \right)$$
Where $P_0 = 101.325\text{ kPa}$ (ambient atmospheric pressure).

### 2.5 Rankine-Hugoniot Dynamic Wind Pressure ($Q$)
Dynamic wind pressure represents the drag force behind the shock front:
$$Q = \frac{2.5 P_{so}^2}{7 P_0 + P_{so}}$$

### 2.6 Overpressure Decay Waveform (Friedlander Curve)
The overpressure-time profile is modeled using the Modified Friedlander equation:
$$P(t) = P_{so} \left(1 - \frac{t}{t_d}\right) e^{-b \frac{t}{t_d}}$$
Where decay parameter $b$ is solved numerically using root-finding methods (e.g. secant or bisection) to satisfy:
$$i_s = P_{so} \frac{t_d}{b^2} \left(b - 1 + e^{-b}\right)$$
