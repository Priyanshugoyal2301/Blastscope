"""
SweepEngine — BlastScope Sprint 5
==================================
Executes parametric blast studies:
  • Distance sweep   (fixed charge, varying standoff)
  • Charge sweep     (fixed standoff, varying charge)
  • Explosive comparison (multiple explosives, varying range)

Each sweep point carries full blast environment and damage assessment
for every requested material profile.
"""

import uuid
from backend.blast_engine.services.blast_calculator import BlastCalculatorService
from backend.assessment.damage_engine import DamageEngine
from backend.blast_engine.core.scaled_distance import calculate_scaled_distance


DAMAGE_RANK = {"Safe": 0, "Minor": 1, "Moderate": 2, "Severe": 3, "Failure": 4}


def _blast_and_assess(
    charge_kg: float,
    distance_m: float,
    pressure_factor: float,
    impulse_factor: float,
    general_factor: float,
    burst_type: str,
    profiles_data: list,
    explosive_name: str,
    study_id: str,
    study_type: str,
) -> list:
    """
    Run blast calculator + damage engine for one (charge, distance) pair.
    Returns one dict per profile with all SweepPoint fields.
    """
    blast = BlastCalculatorService.calculate_environment(
        charge_weight=charge_kg,
        distance=distance_m,
        burst_type=burst_type,
        pressure_factor=pressure_factor,
        impulse_factor=impulse_factor,
        general_factor=general_factor,
        model="Kingery-Bulmash",
    )

    assessments = DamageEngine.assess_batch(blast, profiles_data)

    # Compute a single "reference" scaled distance (using general/pressure factor)
    from backend.blast_engine.core.tnt_equivalence import calculate_general_tnt_equivalent
    W_g = calculate_general_tnt_equivalent(charge_kg, general_factor or pressure_factor)
    Z = calculate_scaled_distance(distance_m, W_g)

    points = []
    for ass in assessments:
        is_facade = ass["family"] in ["Glass", "Masonry"]
        P_used = blast["reflected_pressure"] if is_facade else blast["incident_pressure"]
        points.append({
            # Provenance
            "study_id": study_id,
            "study_type": study_type,
            "explosive_name": explosive_name,
            # Scenario
            "charge_kg": round(charge_kg, 4),
            "distance_m": round(distance_m, 4),
            "scaled_distance": round(Z, 4),
            # Blast environment
            "peak_pressure_kPa": round(P_used, 4),
            "peak_impulse_kPa_ms": round(blast["positive_impulse"], 4),
            "reflected_pressure_kPa": round(blast["reflected_pressure"], 4),
            "arrival_time_ms": round(blast["arrival_time"], 4),
            # Assessment
            "profile_id": ass["profile_id"],
            "profile_name": ass["profile_name"],
            "family": ass["family"],
            "damage_level": ass["damage_level"],
            "damage_state": ass["damage_state"],
            "severity_score": ass["severity_score"],
            "controlling_mode": ass["controlling_mode"],
            "damage_index": ass["damage_index"],
            "pressure_ratio": ass["pressure_ratio"],
            "impulse_ratio": ass["impulse_ratio"],
        })

    return points


class SweepEngine:
    """Parametric blast sweep engine."""

    @staticmethod
    def distance_sweep(
        explosive: dict,
        charge_kg: float,
        distances_m: list,
        profiles_data: list,
        burst_type: str = "Surface",
    ) -> list:
        """
        Vary standoff distance at a fixed charge weight.

        Args:
            explosive: dict with keys pressure_equivalency, impulse_equivalency, general_equivalency, name
            charge_kg: Charge mass in kg
            distances_m: List of standoff distances to evaluate
            profiles_data: List of material profile dicts (from db_manager)
            burst_type: 'Surface', 'Air', or 'Free Air'

        Returns:
            Flat list of SweepPoint dicts (one per distance × profile combination)
        """
        study_id = str(uuid.uuid4())[:8]
        points = []
        for d in sorted(distances_m):
            pts = _blast_and_assess(
                charge_kg=charge_kg,
                distance_m=d,
                pressure_factor=explosive.get("pressure_equivalency", 1.0),
                impulse_factor=explosive.get("impulse_equivalency", 1.0),
                general_factor=explosive.get("general_equivalency"),
                burst_type=burst_type,
                profiles_data=profiles_data,
                explosive_name=explosive.get("name", "Unknown"),
                study_id=study_id,
                study_type="distance_sweep",
            )
            points.extend(pts)
        return points

    @staticmethod
    def charge_sweep(
        explosive: dict,
        charges_kg: list,
        distance_m: float,
        profiles_data: list,
        burst_type: str = "Surface",
    ) -> list:
        """
        Vary charge weight at a fixed standoff distance.

        Returns:
            Flat list of SweepPoint dicts (one per charge × profile combination)
        """
        study_id = str(uuid.uuid4())[:8]
        points = []
        for c in sorted(charges_kg):
            pts = _blast_and_assess(
                charge_kg=c,
                distance_m=distance_m,
                pressure_factor=explosive.get("pressure_equivalency", 1.0),
                impulse_factor=explosive.get("impulse_equivalency", 1.0),
                general_factor=explosive.get("general_equivalency"),
                burst_type=burst_type,
                profiles_data=profiles_data,
                explosive_name=explosive.get("name", "Unknown"),
                study_id=study_id,
                study_type="charge_sweep",
            )
            points.extend(pts)
        return points

    @staticmethod
    def explosive_comparison(
        explosives: list,
        charge_kg: float,
        distances_m: list,
        profiles_data: list,
        burst_type: str = "Surface",
    ) -> list:
        """
        Compare multiple explosives across a range of distances at the same charge mass.

        Returns:
            Flat list of SweepPoint dicts (one per explosive × distance × profile combination)
        """
        study_id = str(uuid.uuid4())[:8]
        points = []
        for explosive in explosives:
            for d in sorted(distances_m):
                pts = _blast_and_assess(
                    charge_kg=charge_kg,
                    distance_m=d,
                    pressure_factor=explosive.get("pressure_equivalency", 1.0),
                    impulse_factor=explosive.get("impulse_equivalency", 1.0),
                    general_factor=explosive.get("general_equivalency"),
                    burst_type=burst_type,
                    profiles_data=profiles_data,
                    explosive_name=explosive.get("name", "Unknown"),
                    study_id=study_id,
                    study_type="explosive_comparison",
                )
                points.extend(pts)
        return points
