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
