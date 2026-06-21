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

-- Research Notebook Notes Table
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scenario_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scenario_id) REFERENCES scenarios (id) ON DELETE CASCADE
);
