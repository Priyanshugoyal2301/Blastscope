# BlastScope Database Guide (v1.0.0)

This guide documents the database schema, table structures, Write-Ahead Logging (WAL) configuration, and migration pathways implemented in the BlastScope local database framework.

---

## 1. Local Database Configuration
*   **Database Engine**: SQLite3.
*   **Storage Path**: `%APPDATA%/BlastScope/sqlite.db` in production; project root in development.
*   **Journal Mode**: Write-Ahead Logging (WAL) mode is enabled by default:
    ```sql
    PRAGMA journal_mode=WAL;
    ```
    This allows concurrent reads while writes are active, preventing database file locks on Windows.

---

## 2. Table Schemas & Definitions

### 2.1 Core Metadata Tables
1.  **`explosives`**: Stores explosive agents, densities, and TNT equivalency factors ($e_p, e_i, e_g$).
2.  **`materials`**: Base family identifier (Concrete, Steel, Glass, Masonry).
3.  **`material_profiles`**: Detailed variant specifications (compressive/tensile strengths, failure modes, density).
4.  **`sources`**: Reference sources and citations.
5.  **`thresholds`**: Static limits ($P_{\text{threshold}}, I_{\text{threshold}}$) for each damage state.
6.  **`material_response_curves`**: Storing dynamic response asymptotes ($P_0, I_0$) and curve constants ($K_c$) for hyperbolic damage checks.
7.  **`unit_definitions`**: Physical quantities and conversion multipliers.
8.  **`ufc_references`**: References to DoD UFC 3-340-02 guidelines.

### 2.2 Project & Scenario Tables
1.  **`scenarios`**: User configuration parameters ($W, R$, burst type).
2.  **`scenario_results`**: Cached calculation outputs ($P_{so}, P_r, i_s, t_d, t_a$).
3.  **`material_assessments`**: Dynamic damage results, severity scores, and controlling modes.
4.  **`notes`**: User notebook comments linked to scenarios.
5.  **`validation_cases`**: Verification database containing benchmark reference data.

---

## 3. Database Migration Framework

*   **Implementation**: `DatabaseManager.run_migrations()` checks the `migration_history` table to run pending migrations sequentially.
*   **Migrations Index**:
    *   `001_initial.sql`: Sets up core tables (scenarios, explosives, materials, units).
    *   `002_validation.sql`: Seeds validation case data.
    *   `003_pi_curves.sql`: Populates thresholds and hyperbolic response curves.
    *   `004_sprint5_studies.sql`: Adapts table indices to support large sweeps.
*   **Idempotency**: Prevents duplicate schema adjustments by checking already-applied versions.
*   **Backup Guard**: Creates timestamped backups at `%APPDATA%/BlastScope/backups/` before applying schema migrations.
