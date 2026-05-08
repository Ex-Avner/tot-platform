"""
TOT Web Platform — Database Layer
Supports PostgreSQL (production) and SQLite (local dev).
"""

import os
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict

_DB_URL = os.getenv("DATABASE_URL")
_USE_PG = bool(_DB_URL)

if not _USE_PG:
    import sqlite3
    from pathlib import Path
    _SQLITE_PATH = str(Path(__file__).parent / "tot_platform.db")


class TOTWebDB:
    def __init__(self):
        self._init()

    @contextmanager
    def _conn(self):
        if _USE_PG:
            import psycopg2
            import psycopg2.extras
            conn = psycopg2.connect(_DB_URL)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            conn = sqlite3.connect(_SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            finally:
                conn.close()

    def _cursor(self, conn):
        if _USE_PG:
            import psycopg2.extras
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return conn.cursor()

    @property
    def _ph(self):
        return "%s" if _USE_PG else "?"

    def _init(self):
        with self._conn() as conn:
            cur = self._cursor(conn)
            cur.execute("""
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

    def save_profile(self, session_id: str, responses: Dict, profile: Dict):
        axes = profile.get("axis_scores", {})
        ph = self._ph
        params = (
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
        )
        with self._conn() as conn:
            cur = self._cursor(conn)
            if _USE_PG:
                cur.execute(f"""
                    INSERT INTO profiles
                    (session_id, created_at, responses_json, profile_json,
                     zone, subtype, shape_parameter, vertical, horizontal,
                     temporal_extension, capture_type, primary_stamp)
                    VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
                    ON CONFLICT (session_id) DO UPDATE SET
                      responses_json=EXCLUDED.responses_json,
                      profile_json=EXCLUDED.profile_json,
                      zone=EXCLUDED.zone, subtype=EXCLUDED.subtype,
                      shape_parameter=EXCLUDED.shape_parameter,
                      vertical=EXCLUDED.vertical, horizontal=EXCLUDED.horizontal,
                      temporal_extension=EXCLUDED.temporal_extension,
                      capture_type=EXCLUDED.capture_type,
                      primary_stamp=EXCLUDED.primary_stamp
                """, params)
            else:
                cur.execute(f"""
                    INSERT OR REPLACE INTO profiles
                    (session_id, created_at, responses_json, profile_json,
                     zone, subtype, shape_parameter, vertical, horizontal,
                     temporal_extension, capture_type, primary_stamp)
                    VALUES ({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})
                """, params)

    def get_profile(self, session_id: str) -> Optional[Dict]:
        ph = self._ph
        with self._conn() as conn:
            cur = self._cursor(conn)
            cur.execute(f"SELECT * FROM profiles WHERE session_id = {ph}", (session_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_profiles(self) -> List[Dict]:
        with self._conn() as conn:
            cur = self._cursor(conn)
            cur.execute("SELECT * FROM profiles ORDER BY created_at DESC")
            return [dict(r) for r in cur.fetchall()]

    def get_stats(self) -> Dict:
        with self._conn() as conn:
            cur = self._cursor(conn)
            cur.execute("SELECT COUNT(*) as n FROM profiles")
            total = cur.fetchone()["n"]
            cur.execute("SELECT zone, COUNT(*) as n FROM profiles GROUP BY zone ORDER BY n DESC")
            zones = [dict(r) for r in cur.fetchall()]
            cur.execute("SELECT primary_stamp, COUNT(*) as n FROM profiles WHERE primary_stamp != 'None' GROUP BY primary_stamp ORDER BY n DESC")
            stamps = [dict(r) for r in cur.fetchall()]
            return {"total": total, "zones": zones, "stamps": stamps}

    def update_label(self, session_id: str, label: str):
        ph = self._ph
        with self._conn() as conn:
            cur = self._cursor(conn)
            cur.execute(f"UPDATE profiles SET label = {ph} WHERE session_id = {ph}", (label, session_id))
