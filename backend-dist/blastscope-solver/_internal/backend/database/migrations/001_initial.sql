-- Explosives Table
CREATE TABLE IF NOT EXISTS explosives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    pressure_equivalency REAL NOT NULL,
    impulse_equivalency REAL NOT NULL,
    general_equivalency REAL,
    detonation_velocity REAL,
    density REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materials Base Family Table
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family TEXT NOT NULL UNIQUE
);

-- Material Profiles
CREATE TABLE IF NOT EXISTS material_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    profile_name TEXT NOT NULL UNIQUE,
    density REAL,
    compressive_strength REAL,
    tensile_strength REAL,
    failure_mode TEXT,
    strain_rate_factor REAL,
    failure_category TEXT,
    damage_mechanism TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials (id) ON DELETE CASCADE
);

-- Saved Scenarios Table
CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    explosive_id INTEGER NOT NULL,
    charge_weight REAL NOT NULL,
    distance REAL NOT NULL,
    burst_type TEXT NOT NULL,
    unit_system TEXT NOT NULL DEFAULT 'Metric',
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

-- Scenario Results Cache Table
CREATE TABLE IF NOT EXISTS scenario_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    model_version_id INTEGER,
    scaled_distance REAL NOT NULL,
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

-- Material Assessment Results Table
CREATE TABLE IF NOT EXISTS material_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_result_id INTEGER NOT NULL,
    profile_id INTEGER NOT NULL,
    damage_level TEXT NOT NULL,
    damage_state TEXT,
    severity_score REAL,
    pressure_ratio REAL,
    impulse_ratio REAL,
    damage_index REAL,
    controlling_mode TEXT,
    damage_mechanism TEXT,
    assessment_reason TEXT,
    confidence_level TEXT,
    source_reference TEXT,
    response_model_version TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_result_id) REFERENCES scenario_results (id) ON DELETE CASCADE,
    FOREIGN KEY (profile_id) REFERENCES material_profiles (id) ON DELETE CASCADE
);

-- Unit Definitions Metadata
CREATE TABLE IF NOT EXISTS unit_definitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantity TEXT NOT NULL,
    unit_symbol TEXT NOT NULL UNIQUE,
    conversion_factor REAL NOT NULL,
    is_base INTEGER DEFAULT 0
);
