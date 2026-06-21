-- Migration 005: Convert some hyperbolic curves to Piecewise for testing/demonstration
-- We will convert "Brick Masonry Unreinforced" moderate and severe curves to Piecewise.
-- Masonry moderate thresholds: pressure = 35.0, impulse = 150.0. Asymptotes: p0 = 24.5, i0 = 105.0.
UPDATE material_response_curves
SET curve_type = 'Piecewise',
    equation_text = '[[105.0, 200.0], [105.0, 50.0], [180.0, 24.5], [500.0, 24.5]]'
WHERE profile_id = (SELECT id FROM material_profiles WHERE profile_name = 'Brick Masonry Unreinforced')
  AND damage_state = 'Moderate';

-- Masonry severe thresholds: pressure = 80.0, impulse = 380.0. Asymptotes: p0 = 56.0, i0 = 266.0.
UPDATE material_response_curves
SET curve_type = 'Piecewise',
    equation_text = '[[266.0, 400.0], [266.0, 120.0], [420.0, 56.0], [1000.0, 56.0]]'
WHERE profile_id = (SELECT id FROM material_profiles WHERE profile_name = 'Brick Masonry Unreinforced')
  AND damage_state = 'Severe';
