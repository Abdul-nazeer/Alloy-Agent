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
    """Add alerts table if missing, seed spare parts, and clean old test data"""
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
    
    # Add spare_parts table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spare_parts (
                part_id TEXT PRIMARY KEY,
                part_name TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                quantity_available INTEGER DEFAULT 0,
                minimum_stock INTEGER DEFAULT 1,
                unit_cost REAL DEFAULT 0.0,
                lead_time_days INTEGER DEFAULT 7,
                supplier TEXT,
                last_ordered TEXT,
                status TEXT DEFAULT 'IN_STOCK',
                criticality TEXT DEFAULT 'MEDIUM'
            )
        """)
        logger.info("✅ Spare parts table created/verified")
        
        # Seed spare parts if table is empty
        cursor.execute("SELECT COUNT(*) FROM spare_parts")
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("📦 Seeding spare parts database...")
            SPARE_PARTS_DATA = [
                # Air Compressor Parts
                ("BR-4410", "High-Temperature Bearing", "Air Compressor", 2, 2, 450.00, 3, "SKF Bearings", "IN_STOCK", "HIGH"),
                ("SL-2301", "Oil Seal Kit", "Air Compressor", 5, 3, 85.00, 2, "Parker Seals", "IN_STOCK", "MEDIUM"),
                ("VL-8822", "Pressure Relief Valve", "Air Compressor", 1, 1, 320.00, 7, "Bosch Industrial", "LOW_STOCK", "CRITICAL"),
                ("PS-5544", "Pressure Sensor", "Air Compressor", 3, 2, 175.00, 5, "Honeywell", "IN_STOCK", "MEDIUM"),
                ("GK-7733", "Gasket Set", "Air Compressor", 8, 4, 45.00, 1, "Local Supplier", "IN_STOCK", "LOW"),
                
                # Cooling Fan Parts
                ("MT-6601", "Fan Motor Assembly", "Cooling Fan System", 1, 1, 850.00, 10, "Siemens Motors", "OUT_OF_STOCK", "CRITICAL"),
                ("BL-3322", "Fan Blade Set", "Cooling Fan System", 2, 2, 220.00, 5, "Industrial Fans Co", "IN_STOCK", "HIGH"),
                ("BR-2211", "Motor Bearing Kit", "Cooling Fan System", 4, 2, 120.00, 3, "SKF Bearings", "IN_STOCK", "MEDIUM"),
                
                # Rolling Mill Parts
                ("RL-9988", "Rolling Cylinder", "Rolling Mill", 0, 1, 12500.00, 30, "Heavy Industry GmbH", "OUT_OF_STOCK", "CRITICAL"),
                ("HY-4455", "Hydraulic Pump", "Rolling Mill", 1, 1, 3200.00, 14, "Bosch Rexroth", "LOW_STOCK", "CRITICAL"),
                ("BR-7766", "Heavy-Duty Bearing", "Rolling Mill", 2, 2, 980.00, 7, "Timken", "IN_STOCK", "HIGH"),
                
                # Conveyor Motor Parts
                ("CV-5533", "Conveyor Belt", "Conveyor Motor", 1, 1, 1200.00, 10, "Continental Belts", "IN_STOCK", "HIGH"),
                ("MT-4422", "Motor Controller", "Conveyor Motor", 2, 1, 450.00, 7, "ABB Automation", "IN_STOCK", "MEDIUM"),
                ("BR-1199", "Roller Bearing Set", "Conveyor Motor", 5, 3, 95.00, 3, "SKF Bearings", "IN_STOCK", "LOW"),
            ]
            
            for part in SPARE_PARTS_DATA:
                cursor.execute("""
                    INSERT INTO spare_parts (
                        part_id, part_name, equipment_type, quantity_available, 
                        minimum_stock, unit_cost, lead_time_days, supplier, status, criticality
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, part)
            
            logger.info(f"✅ Seeded {len(SPARE_PARTS_DATA)} spare parts")
        else:
            logger.info(f"✓ Spare parts already seeded ({count} parts)")
            
    except Exception as e:
        logger.error(f"❌ Failed to create/seed spare parts table: {e}")
    
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
