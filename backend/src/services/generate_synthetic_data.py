#!/usr/bin/env python3
"""
Generate Synthetic Historical Data for Demo

Creates:
1. Historical sensor readings (time-series)
2. Maintenance logs
3. Equipment specifications
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Output directory
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("🔧 Generating synthetic data...")
print(f"Output directory: {DATA_DIR}")

# ══════════════════════════════════════════════════════════════════════════════
# Equipment Specifications
# ══════════════════════════════════════════════════════════════════════════════

equipment_specs = [
    {
        "equipment_id": "AC-001",
        "equipment_type": "Air Compressor",
        "location": "Zone-A",
        "install_date": "2020-03-15",
        "last_maintenance": "2024-05-15",
        "operating_hours": 12450,
        "status": "CRITICAL",
    },
    {
        "equipment_id": "AC-002",
        "equipment_type": "Air Compressor",
        "location": "Zone-A",
        "install_date": "2020-03-20",
        "last_maintenance": "2024-06-01",
        "operating_hours": 11200,
        "status": "HIGH",
    },
    {
        "equipment_id": "CF-003",
        "equipment_type": "Cooling Fan System",
        "location": "Zone-B",
        "install_date": "2019-11-20",
        "last_maintenance": "2024-06-01",
        "operating_hours": 18200,
        "status": "MEDIUM",
    },
    {
        "equipment_id": "RM-005",
        "equipment_type": "Rolling Mill",
        "location": "Zone-C",
        "install_date": "2018-07-10",
        "last_maintenance": "2024-05-20",
        "operating_hours": 24500,
        "status": "LOW",
    },
    {
        "equipment_id": "CM-007",
        "equipment_type": "Conveyor Motor",
        "location": "Zone-D",
        "install_date": "2021-01-05",
        "last_maintenance": "2024-06-10",
        "operating_hours": 8900,
        "status": "NORMAL",
    },
]

df_equipment = pd.DataFrame(equipment_specs)
df_equipment.to_csv(DATA_DIR / "equipment_specs.csv", index=False)
print(f"✅ Generated equipment_specs.csv ({len(df_equipment)} equipment)")

# ══════════════════════════════════════════════════════════════════════════════
# Historical Sensor Data (Time-Series)
# ══════════════════════════════════════════════════════════════════════════════

def generate_sensor_history(equipment_id, equipment_type, status, days=7):
    """Generate realistic degradation patterns."""
    
    # Base normal values per equipment type
    normal_values = {
        "Air Compressor": {"temperature_c": 75, "vibration_mm_s": 2.0, "pressure_bar": 7.0, "current_a": 42, "rpm": 1480},
        "Cooling Fan System": {"temperature_c": 55, "vibration_mm_s": 1.5, "pressure_bar": 0, "current_a": 12, "rpm": 1450},
        "Rolling Mill": {"temperature_c": 90, "vibration_mm_s": 3.5, "pressure_bar": 180, "current_a": 200, "rpm": 0},
        "Conveyor Motor": {"temperature_c": 65, "vibration_mm_s": 1.8, "pressure_bar": 0, "current_a": 25, "rpm": 1460},
    }
    
    base = normal_values.get(equipment_type, normal_values["Air Compressor"])
    
    # Generate timestamps (hourly readings)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    timestamps = pd.date_range(start_time, end_time, freq='1h')
    
    data = []
    
    for i, ts in enumerate(timestamps):
        hour = i
        
        # Simulate degradation based on status
        if status == "CRITICAL":
            # Bearing failure: gradual temp increase, pressure drop, vibration spike
            temp_delta = (hour / len(timestamps)) * 40  # +40°C over time
            vib_delta = (hour / len(timestamps)) * 1.5 + np.random.normal(0, 0.2)
            pres_delta = -(hour / len(timestamps)) * 5.5  # Pressure drops
            curr_delta = (hour / len(timestamps)) * 15
            
        elif status == "HIGH":
            # Moderate degradation
            temp_delta = (hour / len(timestamps)) * 15
            vib_delta = (hour / len(timestamps)) * 0.8 + np.random.normal(0, 0.15)
            pres_delta = -(hour / len(timestamps)) * 1.5
            curr_delta = (hour / len(timestamps)) * 8
            
        elif status == "MEDIUM":
            # Slight wear
            temp_delta = np.random.normal(0, 3) + (hour / len(timestamps)) * 5
            vib_delta = np.random.normal(0, 0.2) + (hour / len(timestamps)) * 0.3
            pres_delta = np.random.normal(0, 0.3)
            curr_delta = np.random.normal(0, 2)
            
        else:  # LOW or NORMAL
            # Normal operation with noise
            temp_delta = np.random.normal(0, 2)
            vib_delta = np.random.normal(0, 0.15)
            pres_delta = np.random.normal(0, 0.2)
            curr_delta = np.random.normal(0, 1.5)
        
        reading = {
            "equipment_id": equipment_id,
            "timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_c": round(base["temperature_c"] + temp_delta, 1),
            "vibration_mm_s": round(max(0.5, base["vibration_mm_s"] + vib_delta), 2),
            "pressure_bar": round(max(0, base["pressure_bar"] + pres_delta), 2),
            "current_a": round(base["current_a"] + curr_delta, 1),
            "rpm": int(base["rpm"] + np.random.normal(0, 10)) if base["rpm"] > 0 else 0,
        }
        
        data.append(reading)
    
    return data

# Generate for all equipment
all_sensor_data = []
for eq in equipment_specs:
    sensor_data = generate_sensor_history(
        eq["equipment_id"],
        eq["equipment_type"],
        eq["status"],
        days=7  # Last 7 days
    )
    all_sensor_data.extend(sensor_data)

df_sensors = pd.DataFrame(all_sensor_data)
df_sensors.to_csv(DATA_DIR / "historical_sensor_data.csv", index=False)
print(f"✅ Generated historical_sensor_data.csv ({len(df_sensors)} readings)")

# ══════════════════════════════════════════════════════════════════════════════
# Maintenance Logs
# ══════════════════════════════════════════════════════════════════════════════

maintenance_logs = [
    {
        "log_id": "LOG-001",
        "equipment_id": "AC-001",
        "timestamp": "2024-05-15 14:30:00",
        "event_type": "bearing_replacement",
        "description": "Replaced worn bearing due to overheating",
        "parts_used": "SKF-22220",
        "cost": 450.0,
        "downtime_hours": 4.0,
        "engineer": "John Smith",
    },
    {
        "log_id": "LOG-002",
        "equipment_id": "CF-003",
        "timestamp": "2024-06-01 09:00:00",
        "event_type": "preventive_maintenance",
        "description": "Routine lubrication and inspection",
        "parts_used": "NLGI-2-HT",
        "cost": 25.0,
        "downtime_hours": 0.5,
        "engineer": "Jane Doe",
    },
    {
        "log_id": "LOG-003",
        "equipment_id": "AC-002",
        "timestamp": "2024-06-01 11:00:00",
        "event_type": "inspection",
        "description": "Vibration levels slightly elevated, monitoring",
        "parts_used": "",
        "cost": 0.0,
        "downtime_hours": 0.0,
        "engineer": "Mike Johnson",
    },
    {
        "log_id": "LOG-004",
        "equipment_id": "RM-005",
        "timestamp": "2024-05-20 16:00:00",
        "event_type": "alignment_check",
        "description": "Roll alignment verified within spec",
        "parts_used": "",
        "cost": 0.0,
        "downtime_hours": 2.0,
        "engineer": "Sarah Williams",
    },
    {
        "log_id": "LOG-005",
        "equipment_id": "CM-007",
        "timestamp": "2024-06-10 08:00:00",
        "event_type": "belt_replacement",
        "description": "Replaced conveyor belt as scheduled",
        "parts_used": "CTB-1200-EP400",
        "cost": 3500.0,
        "downtime_hours": 6.0,
        "engineer": "John Smith",
    },
    {
        "log_id": "LOG-006",
        "equipment_id": "AC-001",
        "timestamp": "2024-03-10 10:30:00",
        "event_type": "seal_replacement",
        "description": "Motor seal replaced due to oil leak",
        "parts_used": "4521-BR-SEAL",
        "cost": 85.0,
        "downtime_hours": 2.0,
        "engineer": "Jane Doe",
    },
]

df_logs = pd.DataFrame(maintenance_logs)
df_logs.to_csv(DATA_DIR / "maintenance_logs.csv", index=False)
print(f"✅ Generated maintenance_logs.csv ({len(df_logs)} logs)")

# ══════════════════════════════════════════════════════════════════════════════
# Summary Statistics
# ══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("📊 SYNTHETIC DATA SUMMARY")
print("="*80)
print(f"Equipment: {len(df_equipment)}")
print(f"Sensor readings: {len(df_sensors):,} (7 days × {len(df_equipment)} equipment)")
print(f"Maintenance logs: {len(df_logs)}")
print(f"\nEquipment Status Distribution:")
print(df_equipment['status'].value_counts())
print("\n" + "="*80)
print(f"✅ All data saved to: {DATA_DIR}")
print("="*80)
