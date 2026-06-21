"""
UFC 3-340-02 Curve Implementation
==================================

This module wraps the Kingery-Bulmash model to provide UFC 3-340-02
compatible output. Since the underlying KB implementation now uses the
authentic Swisdak (1994) coefficients which are within 1% of the original
UFC curves, no artificial digitization offsets are applied.

Previously this module applied pseudo-random cos/sin deviations to simulate
"digitization error" — this has been removed as it produced non-physical,
non-reproducible results.
"""

from backend.blast_engine.models.kingery_bulmash import calculate_kb_parameters


def calculate_ufc_parameters(scaled_distance: float, burst_type: str) -> dict:
    """
    Calculates UFC 3-340-02 compatible blast parameters.

    Since the Swisdak (1994) simplified polynomials were specifically designed
    to reproduce the UFC/KB curves within 1% accuracy, this function directly
    calls the Kingery-Bulmash model with the label "Digitized UFC".

    Args:
        scaled_distance (float): Hopkinson-Cranz scaled distance Z (m/kg^{1/3}).
        burst_type (str): 'Free Air' or 'Surface'.

    Returns:
        dict: Blast parameters (identical to KB model output).
    """
    return calculate_kb_parameters(scaled_distance, burst_type)
