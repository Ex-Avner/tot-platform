"""
TOT Web Platform — Database Layer
SQLite storage for profiles and analytics.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict


class TOTWebDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "tot_platform.db")
        self.db_path = db_path
        self._init()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    responses_json TEXT NOT NULL,
                    profile_json TEXT NOT NULL,
                    zone TEXT,
                    subtype TEXT,
                    shape_parameter REAL,
                    vertical REAL,
                    horizontal REAL,
                    temporal_extension REAL,
                    capture_type TEXT,
                    primary_stamp TEXT,
                    label TEXT DEFAULT ''
                )
            """)
            conn.commit()

    def save_profile(self, session_id: str, responses: Dict, profile: Dict):
        axes = profile.get("axis_scores", {})
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO profiles
                (session_id, created_at, responses_json, profile_json,
                 zone, subtype, shape_parameter, vertical, horizontal,
                 temporal_extension, capture_type, primary_stamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                datetime.utcnow().isoformat(),
                json.dumps(responses),
                json.dumps(profile),
                profile.get("zone", ""),
                profile.get("primary_subtype", ""),
                profile.get("shape_parameter", 1.0),
                axes.get("vertical", 0),
                axes.get("horizontal", 0),
                axes.get("temporal_extension", 0),
                profile.get("capture_type", ""),
                profile.get("primary_stamp", ""),
            ))
            conn.commit()

    def get_profile(self, session_id: str) -> Optional[Dict]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM profiles WHERE session_id = ?", (session_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_profiles(self) -> List[Dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM profiles ORDER BY created_at DESC"
            ).fetchall()
            return [dict(r) for r in rows]

    def get_stats(self) -> Dict:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
            zones = conn.execute(
                "SELECT zone, COUNT(*) as n FROM profiles GROUP BY zone ORDER BY n DESC"
            ).fetchall()
            stamps = conn.execute(
                "SELECT primary_stamp, COUNT(*) as n FROM profiles WHERE primary_stamp != 'None' GROUP BY primary_stamp ORDER BY n DESC"
            ).fetchall()
            return {
                "total": total,
                "zones": [dict(z) for z in zones],
                "stamps": [dict(s) for s in stamps],
            }

    def update_label(self, session_id: str, label: str):
        with self._connect() as conn:
            conn.execute(
                "UPDATE profiles SET label = ? WHERE session_id = ?",
                (label, session_id)
            )
            conn.commit()
