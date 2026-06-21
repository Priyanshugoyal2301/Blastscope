# BlastScope Material Model Guide (v1.0.0)

This guide documents the mechanical properties, damage thresholds, and failure characteristics implemented in BlastScope's material models.

---

## 1. Glass Models (`glass.py`)

*   **Variants**:
    *   *6mm Monolithic Glass*: Annealed monolithic glass.
    *   *12mm Laminated Glass*: Tougher glass with a PVB interlayer.
*   **Properties**: Density = $2500\text{ kg/m}^3$, Compressive Strength = $250\text{ MPa}$, Tensile Strength = $45\text{ MPa}$.
*   **Failure Mode**: Brittle tensile fracture.
*   **Damage Exponent ($m$)**:
    *   Monolithic: $m = 2.5$
    *   Laminated: $m = 1.8$
*   **Glazing Hazard States**:
    *   $P_b < 0.05 \implies$ **Glazing Safe**
    *   $0.05 \le P_b < 0.50 \implies$ **Low Hazard**
    *   $P_b \ge 0.50 \implies$ **High Hazard**
*   **Scientific Reference**: ISO 16933:2007.

---

## 2. Brick Masonry (`masonry.py`)

*   **Variant**: *Brick Masonry Unreinforced*.
*   **Properties**: Density = $2000\text{ kg/m}^3$, Compressive Strength = $15\text{ MPa}$, Tensile Strength = $0.5\text{ MPa}$.
*   **Failure Mode**: Flexural Collapse.
*   **Damage States**:
    *   $\le 0.24$: **Elastic** (mortar joints intact).
    *   $0.25 - 0.49$: **Cracking** (flexural mortar cracking).
    *   $0.50 - 0.74$: **Yielding** (mortar yield, block displacement).
    *   $\ge 0.75$: **Three-Hinge Collapse** (unstable wall collapse).
*   **Scientific Reference**: *Blast Performance of Concrete Masonry Unit (CMU) Walls*.

---

## 3. Reinforced Concrete (`rc.py`)

*   **Variant**: *Reinforced Concrete M30*.
*   **Properties**: Density = $2400\text{ kg/m}^3$, Compressive Strength = $30\text{ MPa}$, Tensile Strength = $3.5\text{ MPa}$.
*   **Failure Mode**: Flexure and Spalling.
*   **Damage States**:
    *   $\le 0.19$: **Elastic** (micro-cracks).
    *   $0.20 - 0.39$: **Cracking** (tensile cracking).
    *   $0.40 - 0.59$: **Spalling** (spalling of cover concrete).
    *   $0.60 - 0.79$: **Scabbing** (debris ejection from back face).
    *   $\ge 0.80$: **Breaching** (punch-through shear plug).
*   **Scientific Reference**: *Numerical and Theoretical Study of Concrete Spall Damage under Blast Loads*.

---

## 4. Structural Steel (`steel.py`)

*   **Variant**: *Structural Steel Grade 250*.
*   **Properties**: Density = $7850\text{ kg/m}^3$, Compressive Strength = $250\text{ MPa}$, Tensile Strength = $250\text{ MPa}$.
*   **Failure Mode**: Plastic Yielding.
*   **Damage States**:
    *   $\le 0.24$: **Elastic** (restorable deformation).
    *   $0.25 - 0.49$: **Yield** (permanent plastic yielding).
    *   $0.50 - 0.74$: **Membrane** (large-deflection membrane stretching).
    *   $\ge 0.75$: **Tearing** (ductile tearing at boundaries).
*   **Scientific Reference**: DoD UFC 3-340-02.

---

## 5. Ultra-High Performance Concrete (`uhpc.py`)

*   **Variant**: *Ultra-High Performance Concrete (UHPC)*.
*   **Properties**: Density = $2600\text{ kg/m}^3$, Compressive Strength = $150\text{ MPa}$, Tensile Strength = $12\text{ MPa}$.
*   **Failure Mode**: Localized punching shear.
*   **Damage States**:
    *   $\le 0.19$: **Elastic** (no micro-cracking).
    *   $0.20 - 0.39$: **Micro-cracking** (hairline cracking).
    *   $0.40 - 0.59$: **Fiber Activation** (fibers bridge micro-cracks).
    *   $0.60 - 0.79$: **Fiber Pullout** (frictional sliding of steel fibers).
    *   $\ge 0.80$: **Localized Shear Failure** (dynamic punching shear plug).
*   **Scientific Reference**: DoD UFC 3-340-02.
