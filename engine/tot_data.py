"""
Triaxial Orientation Theory — Data Storage
============================================
SQLite database for participant data, assessment responses,
and computed profiles. Zero-configuration, file-portable.

Theory: Ross Erickson / Avner Media
"""

import sqlite3
import json
import csv
import os
from datetime import datetime
from typing import List, Optional, Dict
from tot_engine import TOTProfile, PoleScores, AxisScores, Zone


class TOTDatabase:
    """SQLite-backed storage for TOT research data."""

    def __init__(self, db_path: str = "tot_research.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS participants (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                demographics TEXT DEFAULT '{}',
                notes TEXT DEFAULT ''
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                responses TEXT NOT NULL,
                session_label TEXT DEFAULT '',
                FOREIGN KEY (participant_id) REFERENCES participants(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT NOT NULL,
                assessment_id INTEGER,
                timestamp TEXT NOT NULL,
                profile_json TEXT NOT NULL,
                zone TEXT,
                subtype TEXT,
                shape_parameter REAL,
                vertical REAL,
                horizontal REAL,
                temporal_extension REAL,
                temporal_balance REAL,
                FOREIGN KEY (participant_id) REFERENCES participants(id),
                FOREIGN KEY (assessment_id) REFERENCES assessments(id)
            )
        """)

        self.conn.commit()

    def add_participant(self, participant_id: str, demographics: dict = None,
                        notes: str = "") -> str:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO participants (id, created_at, demographics, notes) VALUES (?, ?, ?, ?)",
            (participant_id, datetime.now().isoformat(),
             json.dumps(demographics or {}), notes)
        )
        self.conn.commit()
        return participant_id

    def save_responses(self, participant_id: str, responses: Dict[str, int],
                       session_label: str = "") -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO assessments (participant_id, timestamp, responses, session_label) VALUES (?, ?, ?, ?)",
            (participant_id, datetime.now().isoformat(),
             json.dumps(responses), session_label)
        )
        self.conn.commit()
        return cursor.lastrowid

    def save_profile(self, profile: TOTProfile, assessment_id: int = None):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO profiles (participant_id, assessment_id, timestamp,
               profile_json, zone, subtype, shape_parameter,
               vertical, horizontal, temporal_extension, temporal_balance)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (profile.participant_id, assessment_id, datetime.now().isoformat(),
             profile.to_json(), profile.zone.value,
             profile.subtype.primary_subtype, profile.shape_parameter,
             profile.axis_scores.vertical, profile.axis_scores.horizontal,
             profile.axis_scores.temporal_extension,
             profile.axis_scores.temporal_balance)
        )
        self.conn.commit()

    def get_all_profiles(self) -> List[dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles ORDER BY timestamp DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_participant_profiles(self, participant_id: str) -> List[dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM profiles WHERE participant_id = ? ORDER BY timestamp DESC",
            (participant_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all_participants(self) -> List[dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM participants ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def export_csv(self, filepath: str):
        """Export all profiles to CSV for statistical analysis."""
        profiles = self.get_all_profiles()
        if not profiles:
            return

        fieldnames = [
            "participant_id", "timestamp", "zone", "subtype", "shape_parameter",
            "vertical", "horizontal", "temporal_extension", "temporal_balance",
            "ohn", "hoc", "him", "allmen", "wasonce", "willbe",
            "capture_type", "capture_primary", "capture_intensity",
            "primary_stamp",
        ]

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in profiles:
                try:
                    pdata = json.loads(p["profile_json"])
                    row = {
                        "participant_id": p["participant_id"],
                        "timestamp": p["timestamp"],
                        "zone": p["zone"],
                        "subtype": p["subtype"],
                        "shape_parameter": p["shape_parameter"],
                        "vertical": p["vertical"],
                        "horizontal": p["horizontal"],
                        "temporal_extension": p["temporal_extension"],
                        "temporal_balance": p["temporal_balance"],
                    }
                    poles = pdata.get("pole_scores", {})
                    row["ohn"] = poles.get("Ohn (Depth)", "")
                    row["hoc"] = poles.get("Hoc (Surface)", "")
                    row["him"] = poles.get("Him (Singular)", "")
                    row["allmen"] = poles.get("Allmen (Plural)", "")
                    row["wasonce"] = poles.get("Wasonce (Past)", "")
                    row["willbe"] = poles.get("Willbe (Future)", "")
                    row["capture_type"] = pdata.get("capture_type", "")
                    row["capture_primary"] = pdata.get("capture_primary", "")
                    row["capture_intensity"] = pdata.get("capture_intensity", "")
                    row["primary_stamp"] = pdata.get("primary_stamp", "")
                    writer.writerow(row)
                except (json.JSONDecodeError, KeyError):
                    continue

    def export_json(self, filepath: str):
        """Export all profiles to JSON."""
        profiles = self.get_all_profiles()
        data = []
        for p in profiles:
            try:
                pdata = json.loads(p["profile_json"])
                pdata["_db_timestamp"] = p["timestamp"]
                data.append(pdata)
            except json.JSONDecodeError:
                continue

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def get_profile_count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM profiles")
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()
