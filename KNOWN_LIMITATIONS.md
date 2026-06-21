# BlastScope Known Limitations & Future Roadmap (v1.0.0)

This document details the engineering assumptions, limits of applicability, and physical phenomena not modeled in the current BlastScope platform.

---

## 1. Physics Model & Blast Calculations Limitations

*   **Spherically/Hemispherically Symmetric Assumptions**:
    *   *Limit*: Calculations assume ideal spherical (Free Air) or hemispherical (Surface) bursts.
    *   *Real-World Behavior*: Detonations in urban areas undergo channel reflections, diffractions, and shielding around building corners, causing localized pressure concentrations not captured by Kingery-Bulmash.
*   **Dual Equivalence Factor Simplification**:
    *   *Limit*: TNT equivalency is modeled using separate peak-pressure and positive-impulse multipliers.
    *   *Real-World Behavior*: True chemical equivalency varies continuously with scaled distance ($Z$). Splitting into pressure/impulse equivalents enables non-TNT explosive calculations but introduces systematic errors that grow with charge weight and scaled distance. For extreme loading cases, full JWL Equation of State (EOS) or hydrocode simulations are recommended.
*   **Confined & Internal Blasts**:
    *   *Limit*: BlastScope only calculates open-air or surface bursts where the shock wave expands freely into the atmosphere.
    *   *Real-World Behavior*: Detonations inside buildings, vehicles, tunnels, or partially enclosed spaces accumulate quasi-static gas pressure (gas venting duration is much longer than shock wave duration) and experience multiple shock reflections. Confined blast pressures are typically several factors higher than open-air blasts and can cause structural collapse at standoffs that would otherwise be safe.
*   **Thermal Radiation & Fireball Effects**:
    *   *Limit*: The solver restricts calculations to mechanical shock parameters (overpressure, impulse, arrival time, positive duration).
    *   *Real-World Behavior*: High explosives release substantial thermal energy, generating a high-temperature fireball. This leads to thermal radiation hazards, secondary fires, material degradation, and severe burn injuries. BlastScope does not simulate thermal flux or fireball propagation.
*   **Fragment and Secondary Debris Modeling**:
    *   *Limit*: BlastScope does not simulate primary fragments (from explosive casing fragmentation) or secondary fragments (from shattered masonry bricks, concrete spalls, or window glazing shards).
    *   *Real-World Behavior*: Fragmentation is a primary casualty driver in blast events. High-speed casing fragments and shattered building materials can travel hundreds of meters, penetrating protective armor and causing fatalities even when the structural overpressure is within the "Safe" limit.

---

## 2. Structural & Material Assessment Limitations

*   **Simplified Hyperbolic & Piecewise P-I Boundaries**:
    *   *Limit*: Vulnerability is evaluated against static P-I curves.
    *   *Real-World Behavior*: Structural members exhibit complex multi-mode dynamics (flexure, direct shear, diagonal tension) which require non-linear transient Finite Element Analysis (FEA) or detailed SDOF integration.
*   **Uniform Pressure Loading**:
    *   *Limit*: Standoff calculations assume uniform pressure distribution across the facade.
    *   *Real-World Behavior*: For close standoffs, pressure is concentrated directly in front of the detonation point and decays rapidly toward the element boundaries.
*   **Support Edge Conditions**:
    *   *Limit*: Base thresholds assume standard simple supports or full fixity defined in UFC 3-340-02/ISO 16933.
    *   *Real-World Behavior*: Imperfect frame connections, dynamic gasket slippage (in glass), or masonry wall arching action will modify capacity thresholds.
*   **Deterministic Calculations**:
    *   *Limit*: Material responses and blast loads are calculated deterministically.
    *   *Real-World Behavior*: Real-world explosions, material strengths, construction quality, and support boundaries exhibit significant statistical variation. BlastScope does not currently implement Monte Carlo simulations or probabilistic risk assessments (PRA).

---

## 3. Future Development Roadmap

### Version 1.1: Dynamic SDOF Solver
*   **Features**:
    *   Replace static P-I curves with a numerical SDOF time-history integrator (Euler-Newton) for custom glass/reinforced concrete cross-sections.
    *   Support user-defined resistance-deflection functions.

### Version 1.2: Fragmentation & Secondary Debris Hazards
*   **Features**:
    *   Integrate casing fragmentation velocity and density algorithms (Gurney and Mott equations).
    *   Implement glass shard dispersion and velocity modeling (using ISO 16933 standards).

### Version 2.0: 3D Urban Ray-Tracing & Obstacles
*   **Features**:
    *   Import 3D CAD/GIS city layouts.
    *   Execute fast GPU-accelerated shock wave ray-tracing to model shielding and street canyon blast enhancements.
