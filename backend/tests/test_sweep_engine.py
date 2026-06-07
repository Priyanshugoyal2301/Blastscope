"""
Sprint 5 — Sweep Engine Tests
==============================
Verifies: distance sweep ordering, charge sweep ordering, Z-scaling correctness,
explosive comparison (C4 > TNT), grid result shape, CSV headers, material ranker ordering.
"""

import csv
import math
import os
import tempfile
import pytest

from backend.studies.sweep_engine import SweepEngine
from backend.studies.material_ranker import MaterialRanker
from backend.studies.batch_runner import BatchRunner, export_sweep_to_csv

# --------------------------------------------------------------------------
# Minimal mock data that avoids hitting the real database
# --------------------------------------------------------------------------

TNT = {
    "id": 1,
    "name": "TNT",
    "pressure_equivalency": 1.0,
    "impulse_equivalency": 1.0,
    "general_equivalency": 1.0,
}

C4 = {
    "id": 2,
    "name": "C4",
    "pressure_equivalency": 1.37,
    "impulse_equivalency": 1.19,
    "general_equivalency": 1.34,
}

ANFO = {
    "id": 3,
    "name": "ANFO",
    "pressure_equivalency": 0.82,
    "impulse_equivalency": 0.89,
    "general_equivalency": 0.82,
}


def _make_rc_profile(pid: int = 1) -> dict:
    return {
        "id": pid,
        "name": "Reinforced Concrete M30",
        "profile_name": "Reinforced Concrete M30",
        "family": "Concrete",
        "density": 2400.0,
        "minor_pressure": 120.0, "minor_impulse": 300.0,
        "moderate_pressure": 300.0, "moderate_impulse": 500.0,
        "severe_pressure": 1200.0, "severe_impulse": 1000.0,
        "failure_pressure": 2000.0, "failure_impulse": 2500.0,
        "curves": [],
    }


def _make_glass_profile(pid: int = 2) -> dict:
    return {
        "id": pid,
        "name": "Glass 6mm Monolithic",
        "profile_name": "Glass 6mm Monolithic",
        "family": "Glass",
        "density": 2500.0,
        "minor_pressure": 15.0, "minor_impulse": 100.0,
        "moderate_pressure": 25.0, "moderate_impulse": 150.0,
        "severe_pressure": 50.0, "severe_impulse": 250.0,
        "failure_pressure": 80.0, "failure_impulse": 400.0,
        "curves": [],
    }


# --------------------------------------------------------------------------
# 1. Distance sweep ordering
# --------------------------------------------------------------------------

def test_distance_sweep_ordering():
    """
    Increasing standoff must produce non-increasing damage rank for each profile.
    """
    profiles = [_make_rc_profile()]
    distances = [5, 10, 20, 40, 80, 150]
    pts = SweepEngine.distance_sweep(TNT, 100.0, distances, profiles)

    # Sort by distance and extract damage levels for RC
    sorted_pts = sorted(pts, key=lambda p: p["distance_m"])
    RANK = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}
    prev_rank = 5
    for p in sorted_pts:
        r = RANK.get(p["damage_level"], 0)
        assert r <= prev_rank, (
            f"Damage rank increased with distance: {p['distance_m']}m → {p['damage_level']} "
            f"(rank {r}) after rank {prev_rank}"
        )
        prev_rank = r


# --------------------------------------------------------------------------
# 2. Charge sweep ordering
# --------------------------------------------------------------------------

def test_charge_sweep_ordering():
    """
    Increasing charge weight at fixed distance must produce non-decreasing damage rank.
    """
    profiles = [_make_rc_profile()]
    charges = [5, 10, 25, 50, 100, 200, 500]
    pts = SweepEngine.charge_sweep(TNT, charges, 30.0, profiles)

    sorted_pts = sorted(pts, key=lambda p: p["charge_kg"])
    RANK = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}
    prev_rank = -1
    for p in sorted_pts:
        r = RANK.get(p["damage_level"], 0)
        assert r >= prev_rank, (
            f"Damage rank decreased with increasing charge: {p['charge_kg']}kg → "
            f"{p['damage_level']} (rank {r}) after rank {prev_rank}"
        )
        prev_rank = r


# --------------------------------------------------------------------------
# 3. Scaled distance computation
# --------------------------------------------------------------------------

def test_scaled_distance_computation():
    """
    Z = R / W^(1/3) must match the value in SweepPoint for TNT (factor=1.0).
    """
    profiles = [_make_rc_profile()]
    pts = SweepEngine.distance_sweep(TNT, 64.0, [20.0], profiles)
    assert len(pts) >= 1
    pt = pts[0]
    expected_Z = 20.0 / (64.0 ** (1/3))  # = 20 / 4 = 5.0
    assert abs(pt["scaled_distance"] - expected_Z) < 0.05, (
        f"Scaled distance {pt['scaled_distance']:.4f} ≠ expected {expected_Z:.4f}"
    )


# --------------------------------------------------------------------------
# 4. Explosive comparison: C4 > TNT at same mass and distance
# --------------------------------------------------------------------------

def test_explosive_comparison_c4_vs_tnt():
    """
    C4 has pressure_equivalency=1.37, so at the same mass and distance it
    must produce equal or higher peak pressure than TNT.
    """
    profiles = [_make_rc_profile()]
    distances = [15.0, 30.0, 60.0]
    pts = SweepEngine.explosive_comparison([TNT, C4], 100.0, distances, profiles)

    for d in distances:
        tnt_pts = [p for p in pts if p["explosive_name"] == "TNT" and abs(p["distance_m"] - d) < 0.01]
        c4_pts  = [p for p in pts if p["explosive_name"] == "C4"  and abs(p["distance_m"] - d) < 0.01]
        if not tnt_pts or not c4_pts:
            continue
        p_tnt = tnt_pts[0]["peak_pressure_kPa"]
        p_c4  = c4_pts[0]["peak_pressure_kPa"]
        assert p_c4 >= p_tnt, (
            f"At d={d}m: C4 peak pressure {p_c4:.2f} kPa < TNT {p_tnt:.2f} kPa — wrong!"
        )


# --------------------------------------------------------------------------
# 5. Grid result shape
# --------------------------------------------------------------------------

def test_grid_result_shape():
    """
    n_points == len(charges) × len(distances) × len(profiles)
    """
    profiles = [_make_rc_profile(1), _make_glass_profile(2)]
    charges  = [50.0, 100.0, 200.0]
    distances = [10.0, 25.0, 50.0, 100.0]

    result = BatchRunner.run_grid(TNT, charges, distances, profiles)
    expected = len(charges) * len(distances) * len(profiles)
    assert result["n_points"] == expected, (
        f"Grid shape {result['n_points']} ≠ expected {expected}"
    )
    assert result["study_type"] == "grid"
    assert result["explosive_name"] == "TNT"
    assert len(result["summary"]) == len(profiles)


# --------------------------------------------------------------------------
# 6. CSV export headers
# --------------------------------------------------------------------------

def test_csv_export_headers():
    """
    Exported CSV must include all required columns for research traceability.
    """
    profiles = [_make_rc_profile()]
    pts = SweepEngine.distance_sweep(TNT, 50.0, [20.0, 50.0], profiles)

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test_export.csv")
        written = export_sweep_to_csv(pts, path)
        assert os.path.isfile(written)
        with open(written, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames or []

        required = ["study_id", "study_type", "explosive_name", "charge_kg",
                    "distance_m", "damage_level", "damage_state", "severity_score"]
        for col in required:
            assert col in headers, f"Required CSV column '{col}' missing. Got: {headers}"


# --------------------------------------------------------------------------
# 7. Material ranker ordering: Glass more vulnerable than UHPC
# --------------------------------------------------------------------------

def test_material_ranker_glass_vs_rc():
    """
    At close range, Glass should be ranked more vulnerable than Reinforced Concrete
    because its thresholds are far lower.
    """
    profiles = [_make_rc_profile(1), _make_glass_profile(2)]
    distances = [5.0, 10.0, 20.0, 40.0, 80.0]

    pts = SweepEngine.distance_sweep(TNT, 50.0, distances, profiles)
    ranking = MaterialRanker.rank(pts, profiles)

    assert len(ranking) == 2
    glass_rank = next(r["rank"] for r in ranking if r["profile_name"] == "Glass 6mm Monolithic")
    rc_rank    = next(r["rank"] for r in ranking if r["profile_name"] == "Reinforced Concrete M30")
    assert glass_rank < rc_rank, (
        f"Glass should be ranked more vulnerable (lower rank #) than RC. "
        f"Got Glass={glass_rank}, RC={rc_rank}"
    )
