"""
BatchRunner — BlastScope Sprint 5
====================================
Executes grid studies (charge × distance matrix) with configurable limits
and CSV export via Electron's dialog.showSaveDialog.

Point Limit Policy
-------------------
  0 – 2000   : Run immediately (no warning needed)
  2001–5000  : Frontend shows a soft warning; backend honours the request
  5001–10000 : Frontend requires explicit user confirmation; backend honours it
  > 10000    : Blocked — backend raises ValueError

CSV Format
-----------
Columns (in order):
  study_id, study_type, explosive_name, charge_kg, distance_m, scaled_distance,
  peak_pressure_kPa, peak_impulse_kPa_ms, reflected_pressure_kPa, arrival_time_ms,
  profile_id, profile_name, family, damage_level, damage_state, severity_score,
  controlling_mode, damage_index, pressure_ratio, impulse_ratio

CSV is written to the path returned by Electron's dialog (passed in from frontend).
Falls back to Documents/BlastScope/Exports if path is None.
"""

import csv
import os
import uuid
from pathlib import Path
from typing import Optional

from backend.studies.sweep_engine import SweepEngine
from backend.studies.material_ranker import MaterialRanker, compute_standoff_metrics

HARD_LIMIT = 10_000
SOFT_LIMIT = 5_000
WARN_LIMIT = 2_000

CSV_COLUMNS = [
    "study_id", "study_type", "explosive_name",
    "charge_kg", "distance_m", "scaled_distance",
    "peak_pressure_kPa", "peak_impulse_kPa_ms", "reflected_pressure_kPa", "arrival_time_ms",
    "profile_id", "profile_name", "family",
    "damage_level", "damage_state", "severity_score",
    "controlling_mode", "damage_index", "pressure_ratio", "impulse_ratio",
]


def _check_limit(n_points: int):
    if n_points > HARD_LIMIT:
        raise ValueError(
            f"Grid study would produce {n_points:,} points, which exceeds the "
            f"hard limit of {HARD_LIMIT:,}. Reduce the charge/distance ranges or "
            f"number of profiles."
        )


class BatchRunner:
    """
    Executes a full charge × distance grid study for one or more material profiles.
    """

    @staticmethod
    def run_grid(
        explosive: dict,
        charges_kg: list,
        distances_m: list,
        profiles_data: list,
        burst_type: str = "Surface",
    ) -> dict:
        """
        Run a grid study and return a GridResult dict.

        The grid is: every (charge, distance) combination evaluated for every profile.

        Args:
            explosive: dict with equivalency factors and name
            charges_kg: Sorted list of charge masses
            distances_m: Sorted list of standoff distances
            profiles_data: Material profile dicts from db_manager
            burst_type: Blast type for all points

        Returns:
            GridResult dict with fields:
              study_id, study_type, charges_kg, distances_m, profile_ids,
              n_points, points (list of SweepPoint), summary (ranking list)
        """
        n_profiles = len(profiles_data)
        n_total = len(charges_kg) * len(distances_m) * n_profiles
        _check_limit(n_total)

        study_id = str(uuid.uuid4())[:8]
        all_points = []

        for c in sorted(charges_kg):
            for d in sorted(distances_m):
                from backend.studies.sweep_engine import _blast_and_assess
                pts = _blast_and_assess(
                    charge_kg=c,
                    distance_m=d,
                    pressure_factor=explosive.get("pressure_equivalency", 1.0),
                    impulse_factor=explosive.get("impulse_equivalency", 1.0),
                    general_factor=explosive.get("general_equivalency"),
                    burst_type=burst_type,
                    profiles_data=profiles_data,
                    explosive_name=explosive.get("name", "Unknown"),
                    study_id=study_id,
                    study_type="grid",
                )
                all_points.extend(pts)

        # Build summary (ranking using the best distance sweep slice at largest charge)
        ranking = MaterialRanker.rank(all_points, profiles_data)

        # Enhance summary with standoff metrics per profile at the max charge
        max_charge = max(charges_kg)
        for item in ranking:
            pts_at_max = [
                p for p in all_points
                if p["profile_id"] == item["profile_id"] and p["charge_kg"] == max_charge
            ]
            metrics = compute_standoff_metrics(pts_at_max)
            item["min_safe_standoff_m"] = metrics["min_safe_standoff_m"]
            item["failure_radius_m"] = metrics["failure_radius_m"]

        return {
            "study_id": study_id,
            "study_type": "grid",
            "explosive_name": explosive.get("name", "Unknown"),
            "charges_kg": sorted(charges_kg),
            "distances_m": sorted(distances_m),
            "profile_ids": [p["id"] for p in profiles_data],
            "n_points": len(all_points),
            "points": all_points,
            "summary": ranking,
        }


def export_sweep_to_csv(sweep_points: list, save_path: Optional[str] = None) -> str:
    """
    Write sweep points to a CSV file at `save_path`.
    If save_path is None or empty, falls back to ~/Documents/BlastScope/Exports/.

    Args:
        sweep_points: List of SweepPoint dicts
        save_path: Absolute path chosen via Electron dialog.showSaveDialog

    Returns:
        Absolute path of the written CSV file.
    """
    if not save_path:
        fallback_dir = Path.home() / "Documents" / "BlastScope" / "Exports"
        fallback_dir.mkdir(parents=True, exist_ok=True)
        study_id = (sweep_points[0].get("study_id", "study") if sweep_points else "study")
        save_path = str(fallback_dir / f"blastscope_{study_id}.csv")

    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)

    with open(save_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sweep_points)

    return os.path.abspath(save_path)
