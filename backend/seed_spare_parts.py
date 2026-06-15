"""
Seed spare parts database with realistic industrial parts data
"""
import sqlite3
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "data" / "maintenance.db"

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

def seed_spare_parts():
    """Insert spare parts data into database"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    logger.info("🔧 Seeding spare parts database...")
    
    # Clear existing data
    cursor.execute("DELETE FROM spare_parts")
    
    # Insert spare parts
    for part in SPARE_PARTS_DATA:
        part_id, name, eq_type, qty, min_stock, cost, lead_time, supplier, status, criticality = part
        cursor.execute("""
            INSERT INTO spare_parts (
                part_id, part_name, equipment_type, quantity_available, 
                minimum_stock, unit_cost, lead_time_days, supplier, status, criticality
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (part_id, name, eq_type, qty, min_stock, cost, lead_time, supplier, status, criticality))
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Seeded {len(SPARE_PARTS_DATA)} spare parts")
    logger.info("📊 Status breakdown:")
    logger.info(f"  - IN_STOCK: {sum(1 for p in SPARE_PARTS_DATA if p[8] == 'IN_STOCK')}")
    logger.info(f"  - LOW_STOCK: {sum(1 for p in SPARE_PARTS_DATA if p[8] == 'LOW_STOCK')}")
    logger.info(f"  - OUT_OF_STOCK: {sum(1 for p in SPARE_PARTS_DATA if p[8] == 'OUT_OF_STOCK')}")

if __name__ == "__main__":
    seed_spare_parts()
