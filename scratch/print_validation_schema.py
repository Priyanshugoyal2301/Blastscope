import sqlite3

conn = sqlite3.connect("backend/database/sqlite.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(validation_cases)")
for row in cursor.fetchall():
    print(dict(row))

cursor.execute("SELECT * FROM validation_cases LIMIT 5")
for row in cursor.fetchall():
    print(dict(row))

conn.close()
