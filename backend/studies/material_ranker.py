"""
MaterialRanker — BlastScope Sprint 5
======================================
Computes vulnerability scores and standoff metrics from sweep results.

Vulnerability Score Formula
----------------------------
  vulnerability_score = (
      w_sev  * mean_severity          +   # Mean severity over all sweep points
      w_fail * normalized_fail_radius +   # Failure radius relative to max in set
      w_safe * normalized_safe_standoff   # Inverted safe standoff relative to min in set
  )

  Weights: w_sev=0.4, w_fail=0.35, w_safe=0.25

  Score is in [0, 1] with 1 = most vulnerable.

Standoff Metrics
-----------------
  min_safe_standoff_m  — Smallest distance at which material is predicted "Safe"
                          across the sweep (answers: "How far must I be?")

  failure_radius_m     — Largest distance at which material is predicted "Failure"
                          (answers: "How far does catastrophic failure extend?")

  Both fields are None if the sweep never reaches that level.
"""

import statistics
from typing import Optional, List, Dict

DAMAGE_RANK = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}


def _points_for_profile(sweep_points: list, profile_id: int) -> list:
    return [p for p in sweep_points if p["profile_id"] == profile_id]


def compute_standoff_metrics(profile_points: list) -> dict:
    """
    Given all sweep points for a single profile (varying distance at fixed charge,
    or a grid slice), return:
        min_safe_standoff_m  — minimum distance where damage_level == 'Safe'
        failure_radius_m     — maximum distance where damage_level == 'Failure'
    """
    safe_distances = [
        p["distance_m"] for p in profile_points if p["damage_level"] == "Safe"
    ]
    failure_distances = [
        p["distance_m"] for p in profile_points if p["damage_level"] == "Failure"
    ]

    min_safe = min(safe_distances) if safe_distances else None
    fail_radius = max(failure_distances) if failure_distances else None

    return {
        "min_safe_standoff_m": round(min_safe, 2) if min_safe is not None else None,
        "failure_radius_m": round(fail_radius, 2) if fail_radius is not None else None,
    }


def compute_mean_severity(profile_points: list) -> float:
    scores = [p.get("severity_score", 0.0) for p in profile_points]
    return round(statistics.mean(scores), 4) if scores else 0.0


class MaterialRanker:
    """
    Ranks material profiles by vulnerability using sweep results.
    """

    WEIGHT_SEVERITY = 0.40
    WEIGHT_FAIL_RADIUS = 0.35
    WEIGHT_SAFE_STANDOFF = 0.25

    @classmethod
    def rank(cls, sweep_points: list, profiles_data: list) -> list:
        """
        Compute vulnerability scores and full standoff metrics for every profile.

        Args:
            sweep_points: Output from SweepEngine (distance_sweep or charge_sweep)
            profiles_data: Original profile dicts (for name/family metadata)

        Returns:
            List of ranking dicts sorted by vulnerability_score descending (most vulnerable first).
        """
        profile_ids = list({p["profile_id"] for p in sweep_points})

        # --- Step 1: compute raw metrics per profile ---
        raw: List[Dict] = []
        for pid in profile_ids:
            pts = _points_for_profile(sweep_points, pid)
            if not pts:
                continue

            profile_name = pts[0]["profile_name"]
            family = pts[0]["family"]
            standoff = compute_standoff_metrics(pts)
            mean_sev = compute_mean_severity(pts)

            raw.append({
                "profile_id": pid,
                "profile_name": profile_name,
                "family": family,
                "mean_severity": mean_sev,
                "min_safe_standoff_m": standoff["min_safe_standoff_m"],
                "failure_radius_m": standoff["failure_radius_m"],
            })

        if not raw:
            return []

        # --- Step 2: normalise for scoring ---
        all_sev = [r["mean_severity"] for r in raw]
        all_fail = [r["failure_radius_m"] or 0.0 for r in raw]
        all_safe = [r["min_safe_standoff_m"] or 0.0 for r in raw]

        max_sev = max(all_sev) or 1.0
        max_fail = max(all_fail) or 1.0
        max_safe = max(all_safe) or 1.0

        for r in raw:
            norm_sev = r["mean_severity"] / max_sev
            norm_fail = (r["failure_radius_m"] or 0.0) / max_fail
            # Safe standoff inverted: smaller standoff → more vulnerable
            safe = r["min_safe_standoff_m"]
            if safe is not None and max_safe > 0:
                norm_safe_inv = 1.0 - (safe / max_safe)
            else:
                norm_safe_inv = 0.5  # unknown → mid

            score = (
                cls.WEIGHT_SEVERITY * norm_sev +
                cls.WEIGHT_FAIL_RADIUS * norm_fail +
                cls.WEIGHT_SAFE_STANDOFF * norm_safe_inv
            )
            r["vulnerability_score"] = round(score, 4)

        # --- Step 3: sort descending (most vulnerable first) ---
        ranked = sorted(raw, key=lambda x: x["vulnerability_score"], reverse=True)
        for idx, r in enumerate(ranked):
            r["rank"] = idx + 1

        return ranked

    @classmethod
    def standoff_to_damage(
        cls,
        sweep_points: list,
        profile_id: int,
        target_level: str = "Failure",
    ) -> Optional[float]:
        """
        Find the minimum standoff distance where a profile first achieves `target_level`
        or worse. Returns None if the level is never reached in the sweep.
        """
        rank_target = DAMAGE_RANK.get(target_level, 4)
        pts = _points_for_profile(sweep_points, profile_id)
        hit = [
            p["distance_m"] for p in pts
            if DAMAGE_RANK.get(p["damage_level"], 0) >= rank_target
        ]
        return round(max(hit), 2) if hit else None
