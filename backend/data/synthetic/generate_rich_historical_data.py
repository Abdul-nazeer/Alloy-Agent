"""
Generate Rich Synthetic Historical Data for Upload Demo
Creates realistic delay logs, failure reports, and maintenance logs
"""
import csv
import random
from datetime import datetime, timedelta

# Equipment configuration
EQUIPMENT = [
    {"id": "AC-001", "type": "Air Compressor", "install_date": "2020-03-15"},
    {"id": "AC-002", "type": "Air Compressor", "install_date": "2020-03-20"},
    {"id": "CF-003", "type": "Cooling Fan System", "install_date": "2019-11-20"},
    {"id": "RM-005", "type": "Rolling Mill", "install_date": "2018-07-10"},
    {"id": "CM-007", "type": "Conveyor Motor", "install_date": "2021-01-05"},
]

# Delay reasons by equipment type
DELAY_REASONS = {
    "Air Compressor": [
        "Oil filter clogged", "Pressure drop", "Valve malfunction", "Control system error",
        "Temperature sensor failure", "Compressor shutdown", "Cooling system issue"
    ],
    "Cooling Fan System": [
        "Fan blade imbalance", "Motor bearing noise", "Belt slippage", "Electrical fault",
        "Vibration alarm", "Fan speed irregular", "Overheating"
    ],
    "Rolling Mill": [
        "Roll misalignment", "Hydraulic pressure loss", "Drive motor overload", 
        "Emergency stop activated", "Material jam", "Lubrication failure", "Bearing temperature high"
    ],
    "Conveyor Motor": [
        "Belt tension low", "Motor overload", "Gearbox noise", "Chain wear",
        "Speed fluctuation", "Brake failure", "Alignment issue"
    ],
}

# Failure types and root causes
FAILURES = {
    "Air Compressor": [
        ("Motor failure", "Winding insulation breakdown", 12, 3500, "Motor;Bearings"),
        ("Valve failure", "Valve seat erosion", 8, 1200, "Control valve;Seals"),
        ("Oil pump failure", "Pump impeller wear", 6, 950, "Oil pump"),
        ("Pressure sensor failure", "Sensor drift", 2, 450, "Pressure sensor"),
        ("Compressor head failure", "Piston ring wear", 16, 5500, "Compressor head;Piston rings"),
    ],
    "Cooling Fan System": [
        ("Motor failure", "Bearing seizure", 10, 2800, "Motor;Bearings"),
        ("Fan blade failure", "Fatigue crack", 12, 3200, "Fan blades"),
        ("Belt failure", "Belt wear and tear", 4, 450, "V-belt"),
        ("Control system failure", "Relay contact failure", 3, 680, "Control relay;Contactor"),
        ("Shaft failure", "Torsional stress", 14, 4200, "Drive shaft;Coupling"),
    ],
    "Rolling Mill": [
        ("Hydraulic system failure", "Pump seal leak", 18, 8500, "Hydraulic pump;Seals"),
        ("Roll bearing failure", "Spalling", 22, 12000, "Roll bearings;Bearing housing"),
        ("Drive motor failure", "Rotor bar crack", 20, 15000, "Drive motor"),
        ("Lubrication system failure", "Filter blockage", 8, 2200, "Oil filter;Lubrication pump"),
        ("Roll surface damage", "Material buildup", 14, 6500, "Roll surface treatment"),
    ],
    "Conveyor Motor": [
        ("Motor bearing failure", "Bearing wear", 6, 1800, "Motor bearings"),
        ("Gearbox failure", "Gear tooth breakage", 10, 3500, "Gearbox;Gears"),
        ("Belt failure", "Belt tension loss", 3, 850, "Conveyor belt"),
        ("Shaft failure", "Shaft misalignment", 8, 2200, "Drive shaft;Coupling"),
        ("Brake failure", "Brake pad wear", 4, 950, "Brake assembly"),
    ],
}

# Maintenance types and actions
MAINTENANCE_TYPES = [
    "Preventive", "Corrective", "Predictive", "Emergency", "Scheduled"
]

MAINTENANCE_ACTIONS = {
    "Air Compressor": [
        ("Oil change and filter replacement", "Oil;Filter", 2.5),
        ("Valve inspection and adjustment", "Valve kit", 3.0),
        ("Bearing lubrication", "Grease", 1.5),
        ("Cooling system cleaning", "Cleaning solution", 2.0),
        ("Pressure sensor calibration", "Calibration kit", 1.0),
        ("Compressor belt tensioning", "None", 1.0),
        ("Air filter replacement", "Air filter", 0.5),
    ],
    "Cooling Fan System": [
        ("Fan blade balancing", "Balancing weights", 2.0),
        ("Motor bearing replacement", "Bearings;Grease", 4.0),
        ("Belt replacement and tensioning", "V-belt", 1.5),
        ("Electrical connection inspection", "None", 1.0),
        ("Vibration analysis", "None", 0.5),
        ("Fan housing cleaning", "Cleaning solution", 2.0),
        ("Control system check", "None", 1.0),
    ],
    "Rolling Mill": [
        ("Roll surface inspection", "None", 2.0),
        ("Hydraulic oil change", "Hydraulic oil;Filter", 4.0),
        ("Bearing lubrication and inspection", "Grease", 3.0),
        ("Roll alignment check", "None", 4.0),
        ("Drive motor inspection", "None", 2.0),
        ("Lubrication pump maintenance", "Pump seals", 3.0),
        ("Cooling system maintenance", "Coolant", 2.5),
    ],
    "Conveyor Motor": [
        ("Belt tension adjustment", "None", 1.0),
        ("Motor bearing lubrication", "Grease", 1.5),
        ("Gearbox oil change", "Gear oil", 2.0),
        ("Shaft alignment check", "None", 2.0),
        ("Brake pad inspection", "Brake pads", 1.5),
        ("Chain lubrication", "Chain lubricant", 1.0),
        ("Speed sensor calibration", "None", 0.5),
    ],
}

TECHNICIANS = [
    "John Martinez", "Sarah Chen", "Michael O'Brien", "Priya Patel", 
    "Carlos Rodriguez", "Emma Thompson", "David Kim", "Lisa Anderson",
    "James Wilson", "Maria Garcia"
]


def generate_date_range(start_date, end_date, count):
    """Generate random dates within range"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    dates = []
    for _ in range(count):
        delta = (end - start).days
        random_days = random.randint(0, delta)
        dates.append(start + timedelta(days=random_days))
    return sorted(dates)


def generate_delay_logs(output_file, num_records=250):
    """Generate delay logs with realistic patterns"""
    print(f"📋 Generating {num_records} delay logs...")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'equipment_id', 'delay_date', 'duration_hours', 'reason', 'impact', 'resolved'
        ])
        
        for equipment in EQUIPMENT:
            # More delays for older equipment
            install_year = int(equipment['install_date'].split('-')[0])
            age_factor = 2026 - install_year
            equipment_delays = num_records // 5 * (age_factor // 3 + 1)
            
            dates = generate_date_range(equipment['install_date'], '2026-06-15', equipment_delays)
            
            for date in dates:
                # Delay duration (more severe in summer months)
                if date.month in [6, 7, 8]:  # Summer
                    duration = random.uniform(1.5, 12.0)
                else:
                    duration = random.uniform(0.5, 6.0)
                
                reason = random.choice(DELAY_REASONS[equipment['type']])
                
                # Impact based on duration
                if duration > 8:
                    impact = "Production stopped"
                elif duration > 4:
                    impact = "Production reduced"
                elif duration > 2:
                    impact = "Minor disruption"
                else:
                    impact = "Minimal impact"
                
                resolved = "true" if random.random() > 0.05 else "false"
                
                writer.writerow([
                    equipment['id'],
                    date.strftime('%Y-%m-%d'),
                    f"{duration:.1f}",
                    reason,
                    impact,
                    resolved
                ])
    
    print(f"✅ Delay logs saved to {output_file}")


def generate_failure_reports(output_file, num_records=100):
    """Generate failure reports with realistic patterns"""
    print(f"⚠️ Generating {num_records} failure reports...")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'equipment_id', 'failure_date', 'failure_type', 'root_cause', 
            'downtime_hours', 'repair_cost', 'parts_replaced'
        ])
        
        for equipment in EQUIPMENT:
            # More failures for older equipment
            install_year = int(equipment['install_date'].split('-')[0])
            age_factor = 2026 - install_year
            equipment_failures = num_records // 5 * (age_factor // 4 + 1)
            
            dates = generate_date_range(equipment['install_date'], '2026-06-15', equipment_failures)
            
            for date in dates:
                failure = random.choice(FAILURES[equipment['type']])
                failure_type, root_cause, base_downtime, base_cost, parts = failure
                
                # Add randomness to downtime and cost
                downtime = base_downtime * random.uniform(0.8, 1.3)
                cost = base_cost * random.uniform(0.85, 1.25)
                
                writer.writerow([
                    equipment['id'],
                    date.strftime('%Y-%m-%d'),
                    failure_type,
                    root_cause,
                    f"{downtime:.1f}",
                    f"{cost:.2f}",
                    parts
                ])
        
    print(f"✅ Failure reports saved to {output_file}")


def generate_maintenance_logs(output_file, num_records=400):
    """Generate maintenance logs with realistic patterns"""
    print(f"🔧 Generating {num_records} maintenance logs...")
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'equipment_id', 'maintenance_date', 'maintenance_type', 
            'technician', 'actions_taken', 'parts_used', 'duration_hours'
        ])
        
        for equipment in EQUIPMENT:
            # More maintenance for older equipment
            install_year = int(equipment['install_date'].split('-')[0])
            age_factor = 2026 - install_year
            equipment_maintenance = num_records // 5 * (age_factor // 3 + 1)
            
            dates = generate_date_range(equipment['install_date'], '2026-06-15', equipment_maintenance)
            
            for date in dates:
                # 70% preventive, 20% corrective, 10% others
                rand = random.random()
                if rand < 0.7:
                    maint_type = "Preventive"
                elif rand < 0.9:
                    maint_type = "Corrective"
                else:
                    maint_type = random.choice(["Predictive", "Emergency", "Scheduled"])
                
                action = random.choice(MAINTENANCE_ACTIONS[equipment['type']])
                actions_taken, parts_used, base_duration = action
                
                # Add randomness to duration
                duration = base_duration * random.uniform(0.8, 1.3)
                
                technician = random.choice(TECHNICIANS)
                
                writer.writerow([
                    equipment['id'],
                    date.strftime('%Y-%m-%d'),
                    maint_type,
                    technician,
                    actions_taken,
                    parts_used,
                    f"{duration:.1f}"
                ])
        
    print(f"✅ Maintenance logs saved to {output_file}")


def main():
    """Generate all synthetic historical data"""
    print("\n" + "="*70)
    print("🏭 RICH SYNTHETIC HISTORICAL DATA GENERATOR")
    print("="*70 + "\n")
    
    # Generate delay logs
    generate_delay_logs('equipment_delay_logs.csv', num_records=250)
    print()
    
    # Generate failure reports
    generate_failure_reports('equipment_failure_reports.csv', num_records=100)
    print()
    
    # Generate maintenance logs
    generate_maintenance_logs('equipment_maintenance_logs.csv', num_records=400)
    print()
    
    print("="*70)
    print("✅ ALL SYNTHETIC DATA GENERATED SUCCESSFULLY!")
    print("="*70)
    print("\n📊 Summary:")
    print("  - Delay Logs: 250 records across 5 equipment")
    print("  - Failure Reports: 100 records with realistic costs and downtime")
    print("  - Maintenance Logs: 400 records with technician names and parts")
    print("\n📂 Files ready for upload in Data Import page!")
    print("\n🎯 Demo Story:")
    print("  1. Show empty system (generic AI responses)")
    print("  2. Upload these CSV files")
    print("  3. AI now has 750+ historical records")
    print("  4. Ask same question → AI gives contextual answer with historical patterns")
    print()


if __name__ == "__main__":
    main()
