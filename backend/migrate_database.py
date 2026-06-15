"""
Database Migration Script - Safe to run multiple times
Adds missing tables and cleans up old data
"""
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data" / "maintenance.db"

def migrate_database():
    """Add alerts table if missing and clean old test data"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    logger.info("🔧 Starting database migration...")
    
    # Add alerts table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                alert_id TEXT PRIMARY KEY,
                equipment_id TEXT NOT NULL,
                equipment_name TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                report_id TEXT,
                incident_id TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(report_id),
                FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
            )
        """)
        logger.info("✅ Alerts table created/verified")
    except Exception as e:
        logger.error(f"❌ Failed to create alerts table: {e}")
    
    # Clean up old test data (equipment that's not in our 5 equipment list)
    valid_equipment = ['AC-001', 'AC-002', 'CF-003', 'RM-005', 'CM-007']
    
    try:
        # Delete incidents from invalid equipment
        cursor.execute("""
            DELETE FROM incidents 
            WHERE equipment_id NOT IN (?, ?, ?, ?, ?)
        """, valid_equipment)
        deleted_incidents = cursor.rowcount
        logger.info(f"✅ Deleted {deleted_incidents} old test incidents")
        
        # Delete reports linked to invalid incidents
        cursor.execute("""
            DELETE FROM reports 
            WHERE incident_id NOT IN (
                SELECT incident_id FROM incidents
            ) AND incident_id IS NOT NULL
        """)
        deleted_reports = cursor.rowcount
        logger.info(f"✅ Deleted {deleted_reports} orphaned reports")
        
        # Delete logbook entries from invalid equipment
        cursor.execute("""
            DELETE FROM logbook_entries 
            WHERE equipment_name NOT LIKE '%AC-001%'
            AND equipment_name NOT LIKE '%AC-002%'
            AND equipment_name NOT LIKE '%CF-003%'
            AND equipment_name NOT LIKE '%RM-005%'
            AND equipment_name NOT LIKE '%CM-007%'
        """)
        deleted_logbook = cursor.rowcount
        logger.info(f"✅ Deleted {deleted_logbook} old test logbook entries")
        
        conn.commit()
        logger.info("✨ Database migration complete!")
        logger.info("🤖 Autonomous system will now generate clean reports for AC-001, AC-002, CF-003, RM-005, CM-007")
        
    except Exception as e:
        logger.error(f"❌ Failed to clean old data: {e}")
        conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    migrate_database()
