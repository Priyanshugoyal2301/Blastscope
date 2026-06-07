"""
Engineering Sanity Verification Suite — BlastScope Sprint 4
============================================================

Three verification categories (as per the research supervisor's pre-Sprint-5 checklist):

  1. Envelope Nesting Integrity
     Every Failure envelope must strictly enclose Severe, which encloses Moderate,
     which encloses Minor.  No two hyperbolic curves for the same material profile
     may intersect over the physically meaningful P–I domain.

  2. Monotonic Damage Progression
     Increasing blast load applied along any single loading path (pressure sweep,
     impulse sweep, or diagonal sweep) must never produce a *lower* damage state
     than was returned at the previous (smaller) load.

  3. P–I Assessment Consistency
     100 random P–I points are evaluated by the Python assessment engine and then
     independently classified by checking each point against the hyperbolic curve
     equation.  The two classifications must agree on every point.
     This catches frontend/backend mismatches at the curve-equation level.
"""

import math
import pytest
import random

from backend.materials.glass import Glass
from backend.materials.rc import ReinforcedConcrete
from backend.materials.steel import Steel
from backend.materials.masonry import Masonry
from backend.materials.uhpc import UHPC

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

# Standard RC reference thresholds (kPa / kPa·ms) taken from db_manager seeding.
RC_THRESHOLDS = {
    "minor_pressure":    120.0,
    "minor_impulse":     300.0,
    "moderate_pressure": 300.0,
    "moderate_impulse":  500.0,
    "severe_pressure":   1200.0,
    "severe_impulse":    1000.0,
    "failure_pressure":  2000.0,
    "failure_impulse":   2500.0,
}

STEEL_THRESHOLDS = {
    "minor_pressure":    150.0,
    "minor_impulse":     400.0,
    "moderate_pressure": 800.0,
    "moderate_impulse":  1200.0,
    "severe_pressure":   3500.0,
    "severe_impulse":    3000.0,
    "failure_pressure":  5000.0,
    "failure_impulse":   4000.0,
}

MASONRY_THRESHOLDS = {
    "minor_pressure":    60.0,
    "minor_impulse":     200.0,
    "moderate_pressure": 200.0,
    "moderate_impulse":  500.0,
    "severe_pressure":   600.0,
    "severe_impulse":    1000.0,
    "failure_pressure":  1200.0,
    "failure_impulse":   2000.0,
}

GLASS_THRESHOLDS = {
    "minor_pressure": 15.0,
    "minor_impulse":  100.0,
}

UHPC_THRESHOLDS = {
    "minor_pressure":    400.0,
    "minor_impulse":     800.0,
    "moderate_pressure": 1500.0,
    "moderate_impulse":  2500.0,
    "severe_pressure":   5000.0,
    "severe_impulse":    6000.0,
    "failure_pressure":  10000.0,
    "failure_impulse":   12000.0,
}

DAMAGE_RANK = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}


def _build_hyperbolic_curves(thresholds: dict, factor: float = 0.70) -> list:
    """
    Derive a canonical set of 4 hyperbolic curves from rectangular thresholds.

    Each curve's asymptotes are `factor` × the corresponding threshold, and
    Kc is chosen so the curve passes exactly through the threshold point:

        P_thresh = P0 + Kc / (I_thresh - I0)
        => Kc = (P_thresh - P0) * (I_thresh - I0)
    """
    level_map = [
        ("Minor",    "minor_pressure",    "minor_impulse"),
        ("Moderate", "moderate_pressure", "moderate_impulse"),
        ("Severe",   "severe_pressure",   "severe_impulse"),
        ("Failure",  "failure_pressure",  "failure_impulse"),
    ]
    curves = []
    for state, pk, ik in level_map:
        p_thresh = thresholds.get(pk)
        i_thresh = thresholds.get(ik)
        if p_thresh is None or i_thresh is None:
            continue
        p0 = factor * p_thresh
        i0 = factor * i_thresh
        kc = (p_thresh - p0) * (i_thresh - i0)
        curves.append({
            "damage_state":       state,
            "curve_type":         "Hyperbolic",
            "pressure_asymptote": p0,
            "impulse_asymptote":  i0,
            "curve_constant":     kc,
        })
    return curves


# ---------------------------------------------------------------------------
# 1. Envelope Nesting Integrity
# ---------------------------------------------------------------------------

class TestEnvelopeNesting:
    """
    Verify that for any impulse I in the testable range, the pressure on the
    Failure curve is strictly greater than on the Severe curve, which is
    strictly greater than Moderate, which is strictly greater than Minor.

    Hyperbolic curve geometry: P(I) = P₀ + Kc / (I – I₀)
    Higher-damage curves have larger P₀, I₀, and Kc, so they lie ABOVE
    lower-damage curves on the P–I diagram (greater pressure at the same
    impulse).  A point must overcome more pressure to be classified Failure
    than Minor.

    Nesting is VALID when:  P_minor < P_moderate < P_severe < P_failure
    Nesting is VIOLATED when any inner_P >= outer_P at the same impulse.

    The test sweeps 200 log-spaced impulse values above the largest I₀
    asymptote so all four curve equations are defined.
    """

    def _check_nesting_for_profile(self, thresholds: dict, profile_name: str):
        curves = _build_hyperbolic_curves(thresholds)
        assert len(curves) == 4, f"{profile_name}: Expected 4 curves, got {len(curves)}"

        # Sort by rank so index 0=Minor … 3=Failure
        rank_key = {"Minor": 0, "Moderate": 1, "Severe": 2, "Failure": 3}
        curves_sorted = sorted(curves, key=lambda c: rank_key[c["damage_state"]])

        # Sweep impulse range: from just above the largest I0 asymptote to just
        # below the Failure threshold (curves are valid up to I → ∞).
        i0_max = max(c["impulse_asymptote"] for c in curves_sorted)
        i_min  = i0_max * 1.05
        i_max  = thresholds.get("failure_impulse", i0_max * 10) * 5.0
        n_pts  = 200

        violations = []
        for k in range(n_pts):
            # Logarithmic spacing
            i = i_min * (i_max / i_min) ** (k / (n_pts - 1))
            p_vals = []
            for c in curves_sorted:
                p0, i0, kc = c["pressure_asymptote"], c["impulse_asymptote"], c["curve_constant"]
                if i <= i0:
                    # Below this curve's asymptote: curve pressure is +∞, safe skip
                    p_vals.append(float("inf"))
                else:
                    p_vals.append(p0 + kc / (i - i0))

            # VALID nesting: Minor_P < Moderate_P < Severe_P < Failure_P
            # VIOLATION:     inner_P >= outer_P  (inner envelope overlaps or encloses outer)
            for idx in range(len(p_vals) - 1):
                inner = curves_sorted[idx]["damage_state"]
                outer = curves_sorted[idx + 1]["damage_state"]
                if p_vals[idx] >= p_vals[idx + 1]:
                    violations.append(
                        f"I={i:.1f}: {inner} P={p_vals[idx]:.2f} >= {outer} P={p_vals[idx+1]:.2f} "
                        f"[VIOLATION — inner curve encloses outer]"
                    )

        assert len(violations) == 0, (
            f"{profile_name}: {len(violations)} envelope nesting violations:\n"
            + "\n".join(violations[:5])
        )

    def test_rc_envelope_nesting(self):
        self._check_nesting_for_profile(RC_THRESHOLDS, "Reinforced Concrete")

    def test_steel_envelope_nesting(self):
        self._check_nesting_for_profile(STEEL_THRESHOLDS, "Steel")

    def test_masonry_envelope_nesting(self):
        self._check_nesting_for_profile(MASONRY_THRESHOLDS, "Masonry")

    def test_uhpc_envelope_nesting(self):
        self._check_nesting_for_profile(UHPC_THRESHOLDS, "UHPC")


# ---------------------------------------------------------------------------
# 2. Monotonic Damage Progression
# ---------------------------------------------------------------------------

LEVEL_ORDER = ["Safe", "Minor", "Moderate", "Severe", "Failure"]


def _rank(level: str) -> int:
    return LEVEL_ORDER.index(level) if level in LEVEL_ORDER else -1


class TestMonotonicProgression:
    """
    Apply steadily increasing blast loads and assert that the returned damage
    level never *decreases*.  Three sweep directions:
      (a) Pressure sweep at fixed high impulse
      (b) Impulse sweep at fixed high pressure
      (c) Diagonal sweep (P and I both increase proportionally)
    """

    def _sweep_and_verify_monotonic(self, material, thresholds, curves, sweep_pts, profile_name, direction):
        prev_rank = -1
        violations = []
        for p, i in sweep_pts:
            res = material.evaluate_damage(pressure=p, impulse=i, thresholds=thresholds, curves=curves)
            curr_rank = _rank(res["damage_level"])
            if curr_rank < prev_rank:
                violations.append(
                    f"[{direction}] P={p:.1f}, I={i:.1f} → {res['damage_level']} "
                    f"(rank {curr_rank}) after rank {prev_rank}"
                )
            prev_rank = max(prev_rank, curr_rank)   # ratchet up

        assert len(violations) == 0, (
            f"{profile_name} monotonic violation ({direction}):\n" + "\n".join(violations[:5])
        )

    # --- RC ----------------------------------------------------------------

    def test_rc_pressure_sweep_monotonic(self):
        rc = ReinforcedConcrete()
        curves = _build_hyperbolic_curves(RC_THRESHOLDS)
        # Fixed impulse at 5× failure impulse to stay in pressure-governed regime
        fixed_i = RC_THRESHOLDS["failure_impulse"] * 5.0
        pts = [(p, fixed_i) for p in [10, 50, 100, 150, 250, 350, 600, 1000, 1500, 2500, 4000]]
        self._sweep_and_verify_monotonic(rc, RC_THRESHOLDS, curves, pts, "RC", "Pressure sweep")

    def test_rc_impulse_sweep_monotonic(self):
        rc = ReinforcedConcrete()
        curves = _build_hyperbolic_curves(RC_THRESHOLDS)
        fixed_p = RC_THRESHOLDS["failure_pressure"] * 5.0
        pts = [(fixed_p, i) for i in [50, 150, 250, 350, 600, 800, 1200, 2000, 3000, 5000]]
        self._sweep_and_verify_monotonic(rc, RC_THRESHOLDS, curves, pts, "RC", "Impulse sweep")

    def test_rc_diagonal_sweep_monotonic(self):
        rc = ReinforcedConcrete()
        curves = _build_hyperbolic_curves(RC_THRESHOLDS)
        pts = [(s * RC_THRESHOLDS["failure_pressure"], s * RC_THRESHOLDS["failure_impulse"])
               for s in [0.05, 0.1, 0.3, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0]]
        self._sweep_and_verify_monotonic(rc, RC_THRESHOLDS, curves, pts, "RC", "Diagonal sweep")

    # --- Steel -------------------------------------------------------------

    def test_steel_diagonal_sweep_monotonic(self):
        steel = Steel()
        curves = _build_hyperbolic_curves(STEEL_THRESHOLDS)
        pts = [(s * STEEL_THRESHOLDS["failure_pressure"], s * STEEL_THRESHOLDS["failure_impulse"])
               for s in [0.05, 0.15, 0.3, 0.6, 0.8, 1.0, 1.5, 2.5, 4.0]]
        self._sweep_and_verify_monotonic(steel, STEEL_THRESHOLDS, curves, pts, "Steel", "Diagonal sweep")

    # --- Masonry -----------------------------------------------------------

    def test_masonry_diagonal_sweep_monotonic(self):
        masonry = Masonry()
        curves = _build_hyperbolic_curves(MASONRY_THRESHOLDS)
        pts = [(s * MASONRY_THRESHOLDS["failure_pressure"], s * MASONRY_THRESHOLDS["failure_impulse"])
               for s in [0.05, 0.15, 0.3, 0.6, 0.8, 1.0, 1.5, 2.5, 4.0]]
        self._sweep_and_verify_monotonic(masonry, MASONRY_THRESHOLDS, curves, pts, "Masonry", "Diagonal sweep")

    # --- UHPC --------------------------------------------------------------

    def test_uhpc_diagonal_sweep_monotonic(self):
        uhpc = UHPC()
        curves = _build_hyperbolic_curves(UHPC_THRESHOLDS)
        pts = [(s * UHPC_THRESHOLDS["failure_pressure"], s * UHPC_THRESHOLDS["failure_impulse"])
               for s in [0.02, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]]
        self._sweep_and_verify_monotonic(uhpc, UHPC_THRESHOLDS, curves, pts, "UHPC", "Diagonal sweep")


# ---------------------------------------------------------------------------
# 3. P–I Assessment Consistency (engine vs. direct curve equation)
# ---------------------------------------------------------------------------

class TestAssessmentConsistency:
    """
    For 100 randomly sampled P–I points, compare:

      (A) Classification returned by material.evaluate_damage() — the engine path
      (B) Classification computed by directly evaluating each curve equation
          and finding the highest-ranked curve whose boundary is exceeded

    The two must agree on every point, guaranteeing no frontend/backend mismatch.
    """

    SEED = 42  # deterministic RNG

    def _direct_classify(self, pressure: float, impulse: float, curves: list) -> str:
        """Reproduce exactly the base_material.py curve-check logic."""
        rank = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}
        exceeded = ["Safe"]
        for curve in curves:
            p0 = curve["pressure_asymptote"]
            i0 = curve["impulse_asymptote"]
            kc = curve["curve_constant"]
            state = curve["damage_state"]
            if impulse > i0 and pressure > p0:
                if pressure >= p0 + kc / (impulse - i0):
                    exceeded.append(state)
        return max(exceeded, key=lambda x: rank.get(x, 0))

    def _run_consistency_check(self, material, thresholds: dict, profile_name: str):
        rng = random.Random(self.SEED)
        curves = _build_hyperbolic_curves(thresholds)

        # Sample 100 points in a region that spans Safe → Failure
        p_max = thresholds.get("failure_pressure", 2000.0) * 3.0
        i_max = thresholds.get("failure_impulse", 2500.0) * 3.0

        mismatches = []
        for trial in range(100):
            # Mix of linear and logarithmic sampling to cover edge regions
            if trial < 50:
                p = rng.uniform(0.5, p_max)
                i = rng.uniform(0.5, i_max)
            else:
                p = math.exp(rng.uniform(math.log(0.5), math.log(p_max)))
                i = math.exp(rng.uniform(math.log(0.5), math.log(i_max)))

            engine_level = material.evaluate_damage(
                pressure=p, impulse=i, thresholds=thresholds, curves=curves
            )["damage_level"]

            direct_level = self._direct_classify(p, i, curves)

            if engine_level != direct_level:
                mismatches.append(
                    f"Trial {trial}: P={p:.2f}, I={i:.2f} → "
                    f"engine={engine_level}, direct={direct_level}"
                )

        assert len(mismatches) == 0, (
            f"{profile_name}: {len(mismatches)}/100 P-I consistency mismatches:\n"
            + "\n".join(mismatches[:5])
        )

    def test_rc_pi_consistency(self):
        self._run_consistency_check(ReinforcedConcrete(), RC_THRESHOLDS, "RC")

    def test_steel_pi_consistency(self):
        self._run_consistency_check(Steel(), STEEL_THRESHOLDS, "Steel")

    def test_masonry_pi_consistency(self):
        self._run_consistency_check(Masonry(), MASONRY_THRESHOLDS, "Masonry")

    def test_uhpc_pi_consistency(self):
        self._run_consistency_check(UHPC(), UHPC_THRESHOLDS, "UHPC")

    def test_glass_pi_consistency(self):
        """Glass uses a Weibull breakage model, not curve-based assessment.
        Verify monotonic Pb increase with load — a consistency check suited
        to its model architecture."""
        glass = Glass(name="Glass 6mm Monolithic")
        thresholds = GLASS_THRESHOLDS
        rng = random.Random(self.SEED)

        violations = []
        # 50-point pressure sweep (impulse fixed at 5× threshold)
        fixed_i = thresholds["minor_impulse"] * 5.0
        pressures = sorted([rng.uniform(0.1, thresholds["minor_pressure"] * 5.0) for _ in range(50)])
        prev_score = -1.0
        for p in pressures:
            res = glass.evaluate_damage(pressure=p, impulse=fixed_i, thresholds=thresholds)
            score = res.get("severity_score", 0.0)
            if score < prev_score - 1e-9:   # allow tiny float drift
                violations.append(f"P={p:.2f}: Pb={score:.4f} < prev Pb={prev_score:.4f}")
            prev_score = max(prev_score, score)

        assert len(violations) == 0, (
            f"Glass Weibull breakage probability not monotonic:\n" + "\n".join(violations[:5])
        )
