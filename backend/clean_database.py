"""
Clean Database - Remove old anomaly reports and incidents

Run this to start fresh with no existing alerts/reports.
"""
import sqlite3
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'maintenance.db')

def clean_database():
    """Remove all reports, incidents, and alerts from database"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM reports")
        reports_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM incidents")
        incidents_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts")
        alerts_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM logbook_entries")
        logbook_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current database status:")
        print(f"   Reports: {reports_count}")
        print(f"   Incidents: {incidents_count}")
        print(f"   Alerts: {alerts_count}")
        print(f"   Logbook entries: {logbook_count}")
        
        # Delete all anomaly-related data
        print(f"\n🧹 Cleaning database...")
        
        cursor.execute("DELETE FROM reports")
        print(f"   ✓ Deleted {reports_count} reports")
        
        cursor.execute("DELETE FROM incidents")
        print(f"   ✓ Deleted {incidents_count} incidents")
        
        cursor.execute("DELETE FROM alerts")
        print(f"   ✓ Deleted {alerts_count} alerts")
        
        cursor.execute("DELETE FROM logbook_entries")
        print(f"   ✓ Deleted {logbook_count} logbook entries")
        
        # Commit changes
        conn.commit()
        
        print(f"\n✅ Database cleaned successfully!")
        print(f"   All anomaly reports, incidents, and alerts removed.")
        print(f"   Equipment and sensor data preserved.")
        
    except Exception as e:
        print(f"\n❌ Error cleaning database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE CLEANUP TOOL")
    print("=" * 60)
    print("\nThis will remove all:")
    print("  - Analysis reports")
    print("  - Incidents")
    print("  - Alerts")
    print("  - Logbook entries")
    print("\nEquipment and sensor data will be preserved.")
    
    response = input("\nProceed with cleanup? (yes/no): ").lower().strip()
    
    if response == 'yes':
        clean_database()
    else:
        print("\n❌ Cleanup cancelled.")
