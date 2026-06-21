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

-- Material Damage Thresholds Table
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

-- Material Response Curves Table
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
