import os
import sqlite3
from datetime import date

STATUSES = [
    "Draft", "Submitted", "Online Assessment", "Interview",
    "Offer", "Accepted", "Rejected"
]

# -----------------------------
# SQLite helper (tiny wrapper)
# -----------------------------
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()
        self._maybe_seed()

    def _ensure_schema(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                deadline TEXT NOT NULL,
                status TEXT NOT NULL,
                CV_file_path TEXT,
                CL_file_path TEXT
            )
        ''')
        self.conn.commit()

    def _maybe_seed(self):
        cur = self.conn.execute("SELECT COUNT(*) AS n FROM applications")
        if cur.fetchone()["n"] == 0:
            # Seed a few rows; update file_path to real files on your machine
            today = date.today().isoformat()
            samples = [
                ("SpaceTech Ltd", "RF Graduate Engineer", today, "Submitted",
                 os.path.join(os.getcwd(), "SpaceTech_RF_CoverLetter.pdf"), os.path.join(os.getcwd(), "SpaceTech_RF_CoverLetter.pdf")),
                ("PhotonWorks", "Applied Physicist (DFT)", today, "Draft",
                 os.path.join(os.getcwd(), "PhotonWorks_DFT_Notes.pdf"), os.path.join(os.getcwd(), "SpaceTech_RF_CoverLetter.pdf")),
                ("Aerosys", "Seeker Algorithms Intern", today, "Interview",
                 os.path.join(os.getcwd(), "Aerosys_Interview_Prep.pdf"), os.path.join(os.getcwd(), "SpaceTech_RF_CoverLetter.pdf")),
            ]
            self.conn.executemany("""
                INSERT INTO applications (company, role, deadline, status, CV_file_path, CL_file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, samples)
            self.conn.commit()

    # --- CRUD-ish methods ---
    def fetch_all(self):
        cur = self.conn.execute("""
            SELECT id, company, role, deadline, status, CV_file_path, CL_file_path
            FROM applications
            ORDER BY id DESC
        """)
        return cur.fetchall()

    # New entry into the database, and returns the id number of the inserted row (for future use)
    def new_entry(self, company: str, role: str, deadline: str, status: str) -> int:
        cur = self.conn.execute("INSERT INTO applications (company, role, deadline, status) VALUES (?, ?, ?, ?)", (company, role, deadline, status))
        self.conn.commit()
        return cur.lastrowid
    
    def add_CV_file_path(self, app_id: int, CV_file_path: str):
        self.conn.execute("UPDATE applications SET CV_file_path=? WHERE id=?", (CV_file_path, app_id))
        self.conn.commit()

    def add_CL_file_path(self, app_id: int, CL_file_path: str):
        self.conn.execute("UPDATE applications SET CL_file_path=? WHERE id=?", (CL_file_path, app_id))
        self.conn.commit()

    def update_status(self, app_id: int, new_status: str):
        self.conn.execute("UPDATE applications SET status=? WHERE id=?", (new_status, app_id))
        self.conn.commit()

    def delete(self, app_id: int):
        self.conn.execute("DELETE FROM applications WHERE id=?", (app_id,))
        self.conn.commit()

    def get_CV_file_path(self, app_id: int):
        cur = self.conn.execute("SELECT CV_file_path FROM applications WHERE id=?", (app_id,))
        row = cur.fetchone()
        return None if row is None else row["CV_file_path"]
        #return row["CV_file_path"]
    
    def get_CL_file_path(self, app_id: int):
        cur = self.conn.execute("SELECT CL_file_path FROM applications WHERE id=?", (app_id,))
        row = cur.fetchone()
        return None if row is None else row["CL_file_path"]