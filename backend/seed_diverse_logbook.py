"""
Seed diverse logbook entries for all equipment types
Run this to populate the logbook with comprehensive test data
"""
import sqlite3
import json
from datetime import datetime, timedelta
import random
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "maintenance.db"

# Sample comprehensive data for different equipment types
EQUIPMENT_DATA = [
    {
        "equipment_id": "AC-002",
        "equipment_type": "Air Compressor",
        "fault": "Pressure drop detected with oil contamination",
        "root_causes": [
            {"cause": "Oil filter clogged", "confidence": 0.88, "evidence": ["Pressure drop", "Oil analysis shows particulates"]},
            {"cause": "Compressor valve wear", "confidence": 0.72, "evidence": ["Gradual pressure decline", "Operating hours exceed recommendation"]},
        ],
        "risk_level": "HIGH",
        "actions": [
            "Immediately switch to backup compressor",
            "Isolate and lockout affected compressor",
            "Schedule oil analysis and filter inspection",
            "Check pressure relief valves",
            "Monitor backup compressor pressure closely",
            "Order replacement oil filter (Part: AC-FLT-002)",
        ],
    },
    {
        "equipment_id": "CF-003",
        "equipment_type": "Cooling Fan System",
        "fault": "Abnormal vibration with temperature rise",
        "root_causes": [
            {"cause": "Fan blade imbalance", "confidence": 0.85, "evidence": ["Vibration frequency matches blade pass", "Visual inspection shows debris"]},
            {"cause": "Motor bearing wear", "confidence": 0.65, "evidence": ["Temperature rise at motor housing", "Operating hours: 18,200"]},
        ],
        "risk_level": "CRITICAL",
        "actions": [
            "Reduce fan speed to 50% immediately",
            "Notify operations to prepare for reduced cooling capacity",
            "LOTO procedure - ensure zero energy state",
            "Inspect fan blades for debris or damage",
            "Prepare for motor bearing replacement",
            "Order fan balancing kit (Part: CF-BAL-003)",
            "Coordinate with production for cooling system downtime",
        ],
    },
    {
        "equipment_id": "RM-005",
        "equipment_type": "Rolling Mill",
        "fault": "Excessive torque with motor current spike",
        "root_causes": [
            {"cause": "Roll misalignment", "confidence": 0.78, "evidence": ["Torque variation across length", "Current spikes during operation"]},
            {"cause": "Lubrication system failure", "confidence": 0.82, "evidence": ["Temperature rise", "Lubrication pressure low"]},
        ],
        "risk_level": "CRITICAL",
        "actions": [
            "STOP rolling mill immediately - product quality risk",
            "Implement emergency LOTO procedures",
            "Evacuate personnel from rolling area",
            "Check lubrication system pressure and flow",
            "Measure roll alignment with dial indicators",
            "Inspect roll bearings for damage",
            "Notify production of extended downtime (est: 12-16 hours)",
            "Order emergency bearing set (Part: RM-BRG-SET-005)",
        ],
    },
    {
        "equipment_id": "CM-007",
        "equipment_type": "Conveyor Motor",
        "fault": "Intermittent belt slippage with motor overload",
        "root_causes": [
            {"cause": "Belt tension too low", "confidence": 0.90, "evidence": ["Slippage marks on belt", "Motor current fluctuations"]},
            {"cause": "Drive pulley wear", "confidence": 0.68, "evidence": ["Pulley surface glazing", "Belt tracking issues"]},
        ],
        "risk_level": "MEDIUM",
        "actions": [
            "Reduce conveyor load to 60% capacity",
            "Monitor motor temperature every 30 minutes",
            "Schedule belt tension adjustment",
            "Inspect drive pulley for wear or contamination",
            "Check belt alignment and tracking",
            "Prepare replacement belt if wear is severe (Part: CM-BLT-007)",
        ],
    },
]

REPAIR_PROCEDURES = {
    "Air Compressor": """## REPAIR PROCEDURE

### Phase 1: Preparation (Est: 1 hour)
1. Switch operations to backup compressor
2. Implement LOTO on affected compressor
3. Allow compressor to cool and depressurize
4. Gather tools: filter wrench, oil analysis kit, torque wrench

### Phase 2: Oil System Inspection (Est: 2 hours)
5. Drain oil sample for laboratory analysis
6. Remove and inspect oil filter element
7. Check filter housing for metal particles
8. Inspect oil cooler for blockages
9. Test pressure relief valve operation

### Phase 3: Filter Replacement (Est: 1.5 hours)
10. Install new oil filter element (Part: AC-FLT-002)
11. Replace filter housing gasket
12. Refill with approved synthetic oil (Grade: ISO VG 46)
13. Prime oil pump manually
14. Check oil level and pressure

### Phase 4: System Checkout (Est: 1 hour)
15. Remove LOTO and perform pre-start inspection
16. Start compressor in manual mode
17. Monitor oil pressure, temperature, vibration
18. Run no-load test for 30 minutes
19. Gradually increase load to 50%, then 75%, then 100%
20. Document final readings and return to service

**Total Time: 5-6 hours**""",

    "Cooling Fan System": """## REPAIR PROCEDURE

### Phase 1: Safety & Isolation (Est: 30 minutes)
1. Reduce cooling load gradually
2. Implement LOTO on fan motor circuit
3. Verify zero energy state with voltage tester
4. Post warning signs in cooling area

### Phase 2: Fan Inspection (Est: 1 hour)
5. Remove fan guard and access covers
6. Visual inspection of fan blades for damage
7. Check for debris buildup or corrosion
8. Measure blade-to-housing clearance
9. Document blade condition with photos

### Phase 3: Balancing/Repair (Est: 3 hours)
10. Clean fan blades thoroughly
11. If imbalance detected, remove and rebalance fan assembly
12. Replace damaged blades if necessary
13. Check motor bearings for wear (replace if needed)
14. Apply anti-corrosion coating to blades
15. Reinstall fan with proper alignment

### Phase 4: Motor Bearing Replacement (Est: 2 hours)
16. Remove motor from fan housing
17. Extract worn bearings using bearing puller
18. Clean bearing seats and inspect for damage
19. Install new bearings (heated to 80°C)
20. Pack with high-temp bearing grease
21. Reinstall motor and verify alignment

### Phase 5: Testing & Commissioning (Est: 1 hour)
22. Perform insulation resistance test
23. Start fan at low speed and monitor vibration
24. Incrementally increase to full speed
25. Verify airflow with anemometer
26. Monitor temperature and vibration for 1 hour
27. Return to normal operation

**Total Time: 7-8 hours**""",

    "Rolling Mill": """## REPAIR PROCEDURE

### Phase 1: Emergency Shutdown (Est: 30 minutes)
1. Execute controlled shutdown sequence
2. Implement comprehensive LOTO (main drive, hydraulics, electrical)
3. Relieve all hydraulic pressure
4. Post "DO NOT OPERATE" signs at all control stations
5. Notify production of estimated 12-16 hour downtime

### Phase 2: Diagnostic Assessment (Est: 2 hours)
6. Inspect lubrication system pressure and flow
7. Check roll alignment using dial indicators
8. Measure roll bearing temperatures
9. Inspect roll surface for scoring or damage
10. Check drive motor alignment and coupling

### Phase 3: Lubrication System Repair (Est: 3 hours)
11. Identify and repair lubrication leak
12. Replace failed pump if necessary
13. Clean or replace clogged filters
14. Test system pressure and flow rate
15. Verify oil distribution to all bearing points

### Phase 4: Roll Alignment Correction (Est: 4 hours)
16. Loosen bearing housing bolts
17. Adjust roll position using alignment jacks
18. Verify parallel alignment (tolerance: ±0.002")
19. Check roll gap uniformity across width
20. Torque bearing housing bolts to spec (850 ft-lbs)
21. Recheck alignment after torquing

### Phase 5: Bearing Inspection/Replacement (Est: 3 hours)
22. Remove bearing housing covers
23. Inspect bearings for spalling, scoring, or contamination
24. If damaged, extract and replace bearing set
25. Apply proper lubrication to new bearings
26. Reinstall bearing covers with new gaskets

### Phase 6: System Testing (Est: 2 hours)
27. Remove LOTO and perform safety checks
28. Start lubrication system and verify flow
29. Run mill in manual mode without load
30. Gradually increase rolling force to 50%, 75%, 100%
31. Verify torque balance across roll width
32. Monitor bearing temperatures during test run
33. Roll test piece and verify quality

**Total Time: 14-16 hours**""",

    "Conveyor Motor": """## REPAIR PROCEDURE

### Phase 1: Load Reduction (Est: 30 minutes)
1. Reduce conveyor loading to 60% capacity
2. Notify operations of reduced throughput
3. Monitor motor temperature continuously

### Phase 2: Belt Tension Assessment (Est: 1 hour)
4. Stop conveyor and implement LOTO
5. Measure belt tension with tension meter
6. Check belt tracking and alignment
7. Inspect belt for glazing, cracks, or wear
8. Examine drive and idler pulleys

### Phase 3: Tension Adjustment (Est: 2 hours)
9. Loosen motor mounting bolts
10. Adjust motor position using tensioning screws
11. Set belt tension to manufacturer spec (150 lbs)
12. Verify belt tracking through full travel
13. Torque motor mounting bolts to spec

### Phase 4: Pulley Maintenance (Est: 2 hours)
14. Clean drive pulley with degreaser
15. If glazed, resurface pulley with emery cloth
16. Check pulley runout and balance
17. Inspect pulley for wear or damage
18. If excessive wear, replace pulley (Part: CM-PLY-007)

### Phase 5: Belt Replacement (if needed) (Est: 1.5 hours)
19. Remove old belt and dispose properly
20. Clean all pulley surfaces
21. Install new belt (Part: CM-BLT-007)
22. Set initial tension to 80% of final spec
23. Run-in for 30 minutes, then retension to 100%

### Phase 6: Testing (Est: 1 hour)
24. Remove LOTO and perform safety inspection
25. Start conveyor unloaded and monitor
26. Gradually increase load to 50%, 75%, 100%
27. Verify no slippage under full load
28. Monitor motor current and temperature
29. Return to normal operation

**Total Time: 6-8 hours**""",
}

LONG_TERM_RECOMMENDATIONS = {
    "Air Compressor": """## LONG-TERM RECOMMENDATIONS

1. **Implement Oil Analysis Program**
   - Monthly oil sampling and laboratory analysis
   - Track wear particles, viscosity, contamination
   - Predict component failures 2-3 months in advance
   - Cost: $85/sample | ROI: 4 months

2. **Upgrade to Synthetic Oil**
   - Extended oil change intervals (2x longer)
   - Better high-temperature performance
   - Reduced friction and wear
   - Cost: $450/change | Payback: 8 months

3. **Install Pressure Monitoring System**
   - Real-time pressure trend analysis
   - Automated alerts for pressure drops
   - Data logging for troubleshooting
   - Cost: $1,200 | ROI: 6 months

4. **Preventive Filter Replacement Schedule**
   - Replace filters at 80% of rated life, not 100%
   - Reduces contamination-related failures
   - Target: 95% reduction in oil-related issues
   - Annual cost: $800 | Saves: $5K+ in avoided failures

5. **Compressed Air Leak Detection Program**
   - Ultrasonic leak detection survey (quarterly)
   - Typical savings: 20-30% energy cost
   - ROI: 3-6 months
   - Cost: $2,500 equipment | Annual savings: $8K+""",

    "Cooling Fan System": """## LONG-TERM RECOMMENDATIONS

1. **Implement Vibration Monitoring**
   - Install permanent vibration sensors
   - Automated alerts for imbalance or bearing wear
   - Early warning 4-6 weeks before failure
   - Cost: $1,800 | ROI: 5 months

2. **Establish Fan Balancing Program**
   - Quarterly balancing checks
   - Reduces bearing wear and energy consumption
   - Extends motor life by 2-3x
   - Cost: $400/quarter | Saves: $3K+ per motor replacement

3. **Upgrade to Variable Frequency Drive (VFD)**
   - Match fan speed to actual cooling demand
   - Energy savings: 30-50%
   - Reduced mechanical stress and wear
   - Cost: $3,500 | Payback: 12-18 months

4. **Corrosion Protection Program**
   - Apply ceramic coating to fan blades
   - Annual inspection and touch-up
   - Prevents imbalance from corrosion
   - Cost: $1,200 initial | Maintenance: $200/year

5. **Motor Temperature Monitoring**
   - Install bearing temperature sensors
   - Detect lubrication failures early
   - Automatic shutdown before damage
   - Cost: $600 | ROI: 3 months""",

    "Rolling Mill": """## LONG-TERM RECOMMENDATIONS

1. **Implement Predictive Lubrication Monitoring**
   - Continuous oil pressure and flow monitoring
   - Automated makeup oil system
   - Early warning of pump or filter failures
   - Cost: $8,500 | ROI: 6 months (prevents $50K+ mill damage)

2. **Laser Alignment System**
   - Annual precision alignment of mill rolls
   - Reduces torque variation and product defects
   - Extends bearing life by 40-50%
   - Cost: $4,200 initial | Annual service: $1,500

3. **Torque Monitoring System**
   - Real-time torque measurement across roll width
   - Immediate detection of alignment issues
   - Reduces scrap from quality defects
   - Cost: $12,000 | Typical savings: $40K+/year

4. **Bearing Temperature Monitoring**
   - Wireless temperature sensors on all bearings
   - Trending analysis for predictive maintenance
   - Prevents catastrophic bearing failures
   - Cost: $6,500 | ROI: 4 months

5. **Roll Cooling System Upgrade**
   - Improved coolant distribution
   - Reduces thermal expansion and alignment drift
   - Better product quality and consistency
   - Cost: $15,000 | Quality improvement: $60K+/year

6. **Automated Lubrication System**
   - Programmable lube cycles matched to production
   - Eliminates over/under lubrication
   - Remote monitoring and diagnostics
   - Cost: $8,000 | Lube cost savings: $3K/year + reliability

7. **Vibration Analysis Program**
   - Monthly vibration surveys of drive train
   - Detect misalignment, imbalance, bearing wear
   - Schedule maintenance before failures
   - Cost: $2,500/year | Avoids: $25K+ in emergency repairs""",

    "Conveyor Motor": """## LONG-TERM RECOMMENDATIONS

1. **Implement Belt Monitoring System**
   - Continuous tension monitoring
   - Automated alerts for belt slip or misalignment
   - Reduces unplanned downtime by 60%
   - Cost: $1,400 | ROI: 4 months

2. **Upgrade to High-Efficiency Motor**
   - Premium efficiency motor (IE3 or IE4 rated)
   - Energy savings: 5-8%
   - Longer life and better reliability
   - Cost: $2,800 | Payback: 2-3 years

3. **Install Motor Current Monitoring**
   - Track motor load and detect overload conditions
   - Early warning of mechanical problems
   - Prevents motor burnout
   - Cost: $900 | ROI: 6 months

4. **Quarterly Belt Inspection Program**
   - Scheduled tension checks and adjustments
   - Visual inspection for wear and tracking
   - Replace belts proactively at 80% life
   - Cost: $600/year | Saves: $4K+ in emergency repairs

5. **Pulley Alignment Service**
   - Laser alignment of drive and idler pulleys
   - Reduces belt wear by 40-50%
   - Extends belt life from 12 to 18-24 months
   - Cost: $800/year | Belt savings: $2K+/year

6. **Variable Frequency Drive (VFD)**
   - Match conveyor speed to production needs
   - Soft start reduces mechanical stress
   - Energy savings: 15-25%
   - Cost: $2,200 | Payback: 18 months""",
}


def create_comprehensive_entry(conn, equipment):
    """Create a comprehensive logbook entry for equipment"""
    
    entry_id = f"LOG-{random.randint(10000000, 99999999):08X}"
    equipment_name = f"{equipment['equipment_type']} ({equipment['equipment_id']})"
    
    # Build fault description
    fault_lines = [
        f"* **Equipment**: {equipment_name}",
        f"* **Alert**: {equipment['fault']}",
        "",
        "**Current Sensor Readings:**",
        f"  - temperature_c: {random.uniform(85, 115):.2f}",
        f"  - pressure_bar: {random.uniform(3, 200):.2f}",
        f"  - vibration_mm_s: {random.uniform(1.5, 4.5):.2f}",
        f"  - current_a: {random.uniform(40, 220):.2f}",
        "",
        "**Anomalies:**",
        f"  - {equipment['fault']}",
    ]
    fault_description = "\n".join(fault_lines)
    
    # Build root cause analysis
    root_cause_lines = []
    for i, rc in enumerate(equipment['root_causes'], 1):
        conf_pct = int(rc['confidence'] * 100)
        evidence = ', '.join(rc['evidence'])
        root_cause_lines.append(f"{i}. {rc['cause']} ({conf_pct}% confident)")
        root_cause_lines.append(f"   Evidence: {evidence}")
    root_cause = "\n".join(root_cause_lines)
    
    # Build immediate actions
    immediate_actions = "\n".join(equipment['actions'])
    
    # Get repair procedure and recommendations
    repair_steps = REPAIR_PROCEDURES.get(equipment['equipment_type'], "N/A")
    long_term = LONG_TERM_RECOMMENDATIONS.get(equipment['equipment_type'], "N/A")
    
    # Determine urgency
    urgency_map = {'CRITICAL': 4, 'HIGH': 24, 'MEDIUM': 72}
    urgency_hours = urgency_map.get(equipment['risk_level'], 72)
    
    # Create timestamp (within last 7 days)
    days_ago = random.randint(0, 7)
    hours_ago = random.randint(0, 23)
    timestamp = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()
    
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logbook_entries (
            entry_id, equipment_name, fault_description, root_cause,
            risk_level, urgency_hours, immediate_actions, repair_steps,
            long_term_recommendations, status, timestamp, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        entry_id,
        equipment_name,
        fault_description,
        root_cause,
        equipment['risk_level'],
        urgency_hours,
        immediate_actions,
        repair_steps,
        long_term,
        'OPEN',
        timestamp,
        datetime.now().isoformat()
    ))
    
    print(f"✅ Created logbook entry {entry_id} for {equipment_name} ({equipment['risk_level']})")


def main():
    """Seed diverse logbook entries"""
    print("🌱 Seeding diverse logbook entries...")
    
    conn = sqlite3.connect(str(DB_PATH))
    
    for equipment in EQUIPMENT_DATA:
        create_comprehensive_entry(conn, equipment)
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully created {len(EQUIPMENT_DATA)} diverse logbook entries!")
    print("\n📋 Entries created for:")
    for eq in EQUIPMENT_DATA:
        print(f"   - {eq['equipment_type']} ({eq['equipment_id']}) - {eq['risk_level']}")
    
    print("\n🚀 Go to Operations Logbook to view comprehensive details!")


if __name__ == "__main__":
    main()
