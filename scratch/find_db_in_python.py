import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.db_manager import DatabaseManager

def main():
    print("ENV BLASTSCOPE_USER_DATA_DIR:", os.environ.get("BLASTSCOPE_USER_DATA_DIR"))
    print("ENV BLASTSCOPE_PACKAGED:", os.environ.get("BLASTSCOPE_PACKAGED"))
    db = DatabaseManager()
    print("Database path:", db.db_path)
    print("Exists:", os.path.exists(db.db_path))

if __name__ == "__main__":
    main()
