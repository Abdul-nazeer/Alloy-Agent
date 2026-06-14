"""
SQLite Database Schema for Maintenance System
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "maintenance.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Get database connection."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return rows as dicts
    return conn


def init_database():
    """Initialize database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ═══════════════════════════════════════════════════════════════
    # INCIDENTS TABLE
    # ═══════════════════════════════════════════════════════════════
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id TEXT PRIMARY KEY,
            equipment_id TEXT NOT NULL,
            equipment_name TEXT NOT NULL,
            sensor_readings TEXT,
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # LOGBOOK ENTRIES TABLE
    # ═══════════════════════════════════════════════════════════════
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logbook_entries (
            entry_id TEXT PRIMARY KEY,
            incident_id TEXT,
            equipment_name TEXT NOT NULL,
            fault_description TEXT,
            root_cause TEXT,
            risk_level TEXT,
            urgency_hours INTEGER,
            immediate_actions TEXT,
            repair_steps TEXT,
            long_term_recommendations TEXT,
            evidence_sources TEXT,
            confidence_score REAL,
            status TEXT DEFAULT 'OPEN',
            timestamp TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
        )
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # FEEDBACK TABLE
    # ═══════════════════════════════════════════════════════════════
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT NOT NULL,
            verdict TEXT NOT NULL,
            actual_root_cause TEXT,
            action_taken TEXT,
            outcome TEXT,
            downtime_hours REAL,
            engineer_notes TEXT,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (entry_id) REFERENCES logbook_entries(entry_id)
        )
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # REPORTS TABLE
    # ═══════════════════════════════════════════════════════════════
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY,
            incident_id TEXT,
            entry_id TEXT,
            report_data TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
            FOREIGN KEY (entry_id) REFERENCES logbook_entries(entry_id)
        )
    """)
    
    # ═══════════════════════════════════════════════════════════════
    # DOCUMENTS TABLE (for PDF metadata)
    # ═══════════════════════════════════════════════════════════════
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY,
            doc_name TEXT NOT NULL,
            doc_type TEXT,
            equipment_tag TEXT,
            file_path TEXT,
            upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
            num_pages INTEGER,
            num_chunks INTEGER
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info(f"✓ Database initialized: {DB_PATH}")


# Initialize on module import
init_database()
