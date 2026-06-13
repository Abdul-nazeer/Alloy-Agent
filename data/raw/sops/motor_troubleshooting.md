---
title: Electric Motor Troubleshooting and Diagnostic Procedure
equipment_type: Electric Motors
document_type: sop
revision: 3.0
date: 2026-01-20
---

# Electric Motor Troubleshooting and Diagnostic Procedure

## 1. Purpose
This procedure provides systematic diagnostic steps for identifying and resolving common electric motor failures in steel plant operations.

## 2. Scope
Applies to three-phase AC induction motors (0.5 kW to 500 kW) used in conveyors, pumps, fans, and auxiliary equipment.

## 3. Required Test Equipment
- Digital multimeter (DMM)
- Insulation resistance tester (Megger)
- Clamp-on ammeter
- Infrared thermometer
- Vibration analyzer
- Phase rotation tester
- Contact thermometer

## 4. Safety Requirements
- De-energize motor and apply LOTO
- Verify zero voltage with meter
- Wait 5 minutes for capacitors to discharge
- Use appropriate PPE (arc flash rated)
- Test equipment calibration current

## 5. Preliminary Checks

### 5.1 Visual Inspection
- Check for physical damage or burning smell
- Inspect terminal box for loose connections
- Examine cooling fan and ventilation ports
- Look for oil/grease leaks near bearings
- Verify motor mounting and alignment

### 5.2 Environmental Assessment
- Ambient temperature (should be <40°C)
- Humidity levels (should be <90% RH)
- Dust/contamination levels
- Vibration from nearby equipment
- Supply voltage quality

## 6. Diagnostic Flowchart

### Problem: Motor Will Not Start

**Step 1: Check Power Supply**
- Measure voltage at motor terminals
- Expected: ±10% of rated voltage
- All three phases present and balanced
- If no voltage → Check MCB, contactor, cables

**Step 2: Check Motor Connections**
- Verify wiring matches nameplate diagram
- Star or Delta configured correctly
- Terminal tightness (torque spec 8-12 Nm)
- No loose or corroded connections

**Step 3: Test Motor Windings**
- Measure resistance between phases (U-V, V-W, W-U)
- Should be balanced within 5%
- Typical range: 0.5-50 Ω depending on size
- If infinite resistance → Open winding (rewind required)

**Step 4: Insulation Resistance Test**
- Use 500V Megger for motors up to 690V
- Minimum acceptable: 1 MΩ per kV + 1 MΩ
- For 400V motor: Minimum 1.5 MΩ
- If <1 MΩ → Winding insulation failure

**Step 5: Check Mechanical Load**
- Disconnect coupling/belt
- Try rotating shaft by hand
- Should turn freely with minimal resistance
- If locked → Bearing seizure or mechanical jam

### Problem: Motor Overheating

**Normal Operating Temperature**
- Surface temperature: 60-90°C (depends on insulation class)
- Bearing temperature: 40-80°C
- Temperature rise <80K for Class F insulation

**Diagnostic Steps:**

1. **Measure Load Current**
   - Compare to nameplate FLA (Full Load Amps)
   - If >105% FLA → Overload condition
   - Check load for mechanical binding

2. **Check Voltage Imbalance**
   - Measure voltage across all phases
   - Calculate imbalance: (Max deviation / Average) × 100
   - Should be <1%, maximum acceptable 2%
   - Imbalance causes circulating currents and heat

3. **Verify Cooling System**
   - Check cooling fan rotation (correct direction)
   - Clean ventilation ports and fins
   - Ensure adequate clearance around motor
   - Ambient temperature within limits

4. **Inspect for Single-Phasing**
   - Motor running on 2 phases instead of 3
   - Causes 200% current in remaining phases
   - Immediate shutdown required
   - Check fuses, contacts, and cables

### Problem: Excessive Vibration

**Vibration Severity Chart (ISO 10816)**
- **Good**: <2.8 mm/s RMS
- **Acceptable**: 2.8-7.1 mm/s RMS
- **Tolerable**: 7.1-11.2 mm/s RMS
- **Unacceptable**: >11.2 mm/s RMS

**Root Cause Analysis:**

1. **Mechanical Unbalance**
   - Vibration frequency = 1× running speed
   - Caused by: rotor imbalance, missing balance weight
   - Solution: Dynamic balancing required

2. **Misalignment**
   - Vibration frequency = 1×, 2×, or 3× running speed
   - Axial and radial vibration both elevated
   - Solution: Laser alignment of coupling

3. **Bearing Defects**
   - High frequency vibration (>10× running speed)
   - Often accompanied by temperature rise
   - Solution: Replace bearing immediately

4. **Loose Mounting**
   - Random, erratic vibration pattern
   - Visible movement of motor on base
   - Solution: Torque foundation bolts, check grouting

5. **Resonance**
   - Vibration peak at specific speed
   - Motor/base natural frequency = running speed
   - Solution: Change motor speed or stiffen base

### Problem: Motor Trips on Overload

**Diagnostic Approach:**

1. **Verify Overload Relay Settings**
   - Should be set to 110-115% of motor FLA
   - Check for correct thermal relay sizing
   - Test relay calibration

2. **Measure Running Current**
   - All three phases under normal load
   - Compare to nameplate current
   - If balanced and <FLA → Relay defective
   - If >FLA → True overload condition

3. **Check for Frequent Starts**
   - Count starts per hour (max typically 6-10)
   - Each start generates high inrush (5-7× FLA)
   - Thermal accumulation causes tripping
   - Solution: Reduce start frequency or use soft starter

4. **Assess Voltage Dips**
   - Voltage drop during start
   - Should recover within 2-3 seconds
   - Deep dips cause prolonged high current
   - Solution: Check supply transformer capacity

## 7. Common Failure Modes - Quick Reference

| Symptom | Probable Cause | Quick Check | Action |
|---------|---------------|-------------|--------|
| Won't start, hums | Single phase | Check voltage all phases | Replace fuse/contact |
| Starts then trips | Overload | Measure current | Reduce load or check relay |
| Overheating | Poor ventilation | Check fan, clean vents | Improve cooling |
| High vibration | Misalignment | Visual inspection | Realign coupling |
| Burning smell | Insulation failure | Megger test | Rewind motor |
| Erratic speed | Rotor bars broken | Current signature analysis | Replace rotor |
| Noisy operation | Bearing failure | Temperature/vibration | Replace bearing |

## 8. Preventive Measures
- Maintain proper lubrication schedule
- Keep motor and surroundings clean
- Monitor temperature and vibration trends
- Perform annual insulation resistance tests
- Verify supply voltage quality regularly
- Ensure proper ventilation clearances
- Inspect connections quarterly
- Log all abnormal events

## 9. When to Replace vs Repair

**Repair if:**
- Motor <5 years old
- Repair cost <50% of replacement
- Minor bearing or connection issue
- Rewind feasible and economical

**Replace if:**
- Motor >15 years old
- Severe winding damage
- Frame damage or corrosion
- Obsolete or non-standard motor
- Efficiency upgrade justifies cost
- Repeated failures within 2 years

## 10. Documentation
Record in CMMS:
- Fault symptoms and findings
- Test measurements and readings
- Root cause analysis
- Corrective actions taken
- Parts replaced
- Motor operating parameters
- Technician and date

## 11. Emergency Contacts
- Electrical Supervisor: Ext. 2301
- Motor Rewind Vendor: +1-555-MOTOR-1
- Spare Parts Store: Ext. 2350
