import sqlite3

from pathlib import Path

# =====================================
# DATABASE PATH
# =====================================

DB_PATH = Path(
    "/media/ori_quadro/newhd1/Rahul/backend/app/database/rag.db"
)

# =====================================
# CONNECT DATABASE
# =====================================

conn = sqlite3.connect(DB_PATH)

cursor = conn.cursor()

# =====================================
# CREATE TABLE
# =====================================

cursor.execute("""

CREATE TABLE IF NOT EXISTS videos (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    video_name TEXT UNIQUE,

    transcript_path TEXT,

    summary_path TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

""")

conn.commit()

print("\nDATABASE READY\n")
