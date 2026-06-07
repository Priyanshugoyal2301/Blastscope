-- Explosives Table
CREATE TABLE IF NOT EXISTS explosives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    pressure_equivalency REAL NOT NULL,
    impulse_equivalency REAL NOT NULL,
    general_equivalency REAL,
    detonation_velocity REAL,          -- m/s
    density REAL,                      -- g/cm³
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materials Base Family Table
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family TEXT NOT NULL UNIQUE         -- e.g., 'Glass', 'Masonry', 'Concrete', 'Steel'
);

-- Material Profiles (Variant Specifics)
CREATE TABLE IF NOT EXISTS material_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    profile_name TEXT NOT NULL UNIQUE, -- e.g., 'RC M20', 'Glass 6mm Monolithic'
    density REAL,                      -- kg/m³
    compressive_strength REAL,         -- MPa
    tensile_strength REAL,             -- MPa
    failure_mode TEXT,                 -- e.g., 'Brittle', 'Flexure', 'Spalling'
    strain_rate_factor REAL,           -- dynamic increase factor (DIF)
    failure_category TEXT,             -- e.g., 'Brittle', 'Ductile', 'Quasi-brittle'
    damage_mechanism TEXT,             -- e.g., 'Fracture', 'Spalling', 'Collapse'
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials (id) ON DELETE CASCADE
);

-- Bibliography Sources Table
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    doi TEXT,
    url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material Damage Thresholds Table (Referencing Profiles & Normalized Sources)
CREATE TABLE IF NOT EXISTS thresholds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    source_id INTEGER,
    minor_pressure REAL,               -- kPa
    minor_impulse REAL,                -- kPa-ms
    moderate_pressure REAL,            -- kPa
    moderate_impulse REAL,             -- kPa-ms
    severe_pressure REAL,              -- kPa
    severe_impulse REAL,               -- kPa-ms
    failure_pressure REAL,             -- kPa
    failure_impulse REAL,              -- kPa-ms
    confidence_level TEXT,             -- 'Low', 'Medium', 'High'
    failure_description TEXT,          -- description of the damage state
    threshold_source_type TEXT,        -- 'Experimental', 'Numerical', 'Analytical', 'Code-Based'
    applicability_notes TEXT,          -- constraint applicability details
    FOREIGN KEY (profile_id) REFERENCES material_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE SET NULL
);

-- Saved Scenarios Table
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    explosive_id INTEGER NOT NULL,
    charge_weight REAL NOT NULL,       -- kg
    distance REAL NOT NULL,            -- m
    burst_type TEXT NOT NULL,          -- 'Free Air', 'Air', 'Surface'
    unit_system TEXT NOT NULL DEFAULT 'Metric', -- 'Metric' or 'Imperial'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (explosive_id) REFERENCES explosives (id)
);

-- Model Versions Tracking Table
CREATE TABLE IF NOT EXISTS model_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    source_reference TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scenario Results Cache Table (with Model Provenance)
CREATE TABLE IF NOT EXISTS scenario_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    model_version_id INTEGER,
    scaled_distance REAL NOT NULL,     -- general scaled distance
    incident_pressure REAL NOT NULL,
    reflected_pressure REAL NOT NULL,
    dynamic_pressure REAL NOT NULL,
    positive_impulse REAL NOT NULL,
    positive_duration REAL NOT NULL,
    negative_duration REAL NOT NULL,
    arrival_time REAL NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (id) ON DELETE CASCADE,
    FOREIGN KEY (model_version_id) REFERENCES model_versions (id) ON DELETE SET NULL
);

-- Material Response Curves Table (Storing progressive failure envelopes: Hyperbolic, Piecewise, etc.)
CREATE TABLE IF NOT EXISTS material_response_curves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id INTEGER NOT NULL,
    damage_state TEXT NOT NULL,       -- e.g., 'Minor', 'Moderate', 'Severe', 'Failure'
    curve_type TEXT NOT NULL,         -- 'Hyperbolic', 'Piecewise', 'Polynomial', 'Digitized'
    pressure_asymptote REAL,          -- P0 (kPa)
    impulse_asymptote REAL,           -- I0 (kPa-ms)
    curve_constant REAL,              -- Kc constant
    equation_text TEXT,               -- mathematical description/string definition
    source_id INTEGER,
    confidence_level TEXT,            -- 'Low', 'Medium', 'High'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES material_profiles (id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE SET NULL
);

-- Material Assessment Results Table (Persisted Progressive Output Matrix)
CREATE TABLE IF NOT EXISTS material_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_result_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    damage_level TEXT NOT NULL,        -- Safe, Minor, Moderate, Severe, Failure
    damage_state TEXT,                 -- Physical response description (e.g. Spalling, Yield)
    severity_score REAL,               -- Numerical breakage/damage factor (e.g. Pb, ductility ratio)
    pressure_ratio REAL,               -- P_actual / P_threshold
    impulse_ratio REAL,                -- i_actual / i_threshold
    damage_index REAL,                 -- max(pressure_ratio, impulse_ratio)
    controlling_mode TEXT,             -- 'Pressure' or 'Impulse'
    damage_mechanism TEXT,             -- failure mechanism text
    assessment_reason TEXT,
    confidence_level TEXT,             -- 'Low', 'Medium', 'High'
    source_reference TEXT,             -- bibliography citation text
    response_model_version TEXT,       -- version identifier of the progressive response engine
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_result_id) REFERENCES scenario_results (id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES material_profiles (id) ON DELETE CASCADE
);

-- Model Validation Verification Cases
CREATE TABLE IF NOT EXISTS validation_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    charge_weight REAL NOT NULL,
    distance REAL NOT NULL,
    explosive_name TEXT NOT NULL DEFAULT 'TNT',
    burst_type TEXT NOT NULL DEFAULT 'Surface',
    scaled_distance REAL NOT NULL,
    reference_pressure REAL NOT NULL, -- UFC Pso
    reference_impulse REAL NOT NULL,  -- UFC Impulse
    calculated_pressure REAL,
    calculated_impulse REAL,
    pressure_abs_error REAL,
    pressure_rel_error REAL,
    impulse_abs_error REAL,
    impulse_rel_error REAL,
    validation_source TEXT,
    validation_page TEXT,
    reference_type TEXT,
    ground_truth_class TEXT,          -- Analytical, Digitized, Experimental, ConWep, Field Test
    model_version_id INTEGER,
    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_version_id) REFERENCES model_versions (id) ON DELETE SET NULL
);

-- Research Runs (Parametric Sweep Configurations)
CREATE TABLE IF NOT EXISTS research_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    base_scenario_id INTEGER NOT NULL,
    variable_name TEXT NOT NULL,       -- e.g., 'charge_weight', 'distance'
    min_value REAL NOT NULL,
    max_value REAL NOT NULL,
    step_value REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (base_scenario_id) REFERENCES scenarios (id) ON DELETE CASCADE
);

-- UFC Figure Metadata Table
CREATE TABLE IF NOT EXISTS ufc_references (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chapter TEXT NOT NULL,
    figure_number TEXT NOT NULL UNIQUE, -- e.g., 'Figure 2-7'
    title TEXT NOT NULL,
    category TEXT,
    keywords TEXT,                      -- Search query tag string
    description TEXT,
    source_page INTEGER
);

-- Unit Definitions Metadata
CREATE TABLE IF NOT EXISTS unit_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity TEXT NOT NULL,             -- e.g., 'Pressure', 'Distance', 'Impulse'
    unit_symbol TEXT NOT NULL UNIQUE,   -- e.g., 'kPa', 'MPa', 'psi', 'bar', 'm', 'ft'
    conversion_factor REAL NOT NULL,    -- Multiplier to convert to base unit
    is_base INTEGER DEFAULT 0           -- 1 if base unit, 0 otherwise
);

-- Research Notebook Notes Table
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (id) ON DELETE CASCADE
);
