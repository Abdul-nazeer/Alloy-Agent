---
title: Predictive Maintenance and Condition Monitoring Procedure
equipment_type: Critical Equipment
document_type: sop
revision: 1.5
date: 2026-02-01
---

# Predictive Maintenance and Condition Monitoring Procedure

## 1. Purpose
This procedure establishes the framework for implementing predictive maintenance strategies using condition monitoring techniques to prevent unplanned downtime.

## 2. Scope
Applies to all critical rotating equipment, motors, compressors, pumps, and conveyors in steel plant operations.

## 3. Predictive Maintenance Philosophy
Predictive maintenance uses real-time data to predict equipment failures before they occur, allowing maintenance to be scheduled during planned downtime rather than reactive repairs.

**Benefits:**
- Reduce unplanned downtime by 50-70%
- Extend equipment life by 20-40%
- Lower maintenance costs by 25-30%
- Improve safety through early fault detection
- Optimize spare parts inventory

## 4. Monitoring Technologies

### 4.1 Vibration Analysis
**Purpose**: Detect mechanical defects (bearings, misalignment, unbalance)

**Monitoring Points**: Motor drive end, non-drive end, pump inlets/outlets

**Measurement Frequency**:
- Critical equipment: Weekly
- Important equipment: Bi-weekly
- Standard equipment: Monthly

**Alert Thresholds (ISO 10816)**:
- **Normal**: <2.8 mm/s RMS
- **Caution**: 2.8-7.1 mm/s RMS (Monitor closely)
- **Alert**: 7.1-11.2 mm/s RMS (Plan maintenance within 2 weeks)
- **Danger**: >11.2 mm/s RMS (Shutdown and repair immediately)

**Common Defect Frequencies**:
- Unbalance: 1× RPM
- Misalignment: 2× RPM
- Bearing outer race defect: 3-5× RPM
- Bearing inner race defect: 5-8× RPM
- Belt issues: <1× RPM (sub-synchronous)

### 4.2 Thermography (Infrared Scanning)
**Purpose**: Detect hot spots indicating electrical or mechanical issues

**Inspection Frequency**:
- Electrical panels: Quarterly
- Motors under load: Monthly
- Bearings: Bi-weekly

**Temperature Thresholds**:
- **Normal**: ΔT <15°C above ambient
- **Caution**: ΔT 15-40°C (Investigate within 1 week)
- **Alert**: ΔT 40-80°C (Repair within 48 hours)
- **Critical**: ΔT >80°C (Immediate action required)

**Defects Detected**:
- Loose electrical connections (hot spots)
- Bearing lubrication issues (elevated temperature)
- Motor phase imbalance (uneven heating)
- Overloaded circuits (cable overheating)
- Cooling system failures (blocked ventilation)

### 4.3 Oil Analysis
**Purpose**: Monitor lubricant condition and internal wear

**Sample Frequency**:
- Gearboxes: Every 3 months
- Hydraulic systems: Every 2 months
- Compressors: Monthly

**Key Parameters Monitored**:
- **Viscosity**: Indicates oil degradation
  - Normal: ±10% of specification
  - Abnormal: >10% change → Oil change required
  
- **Particle Count (ISO 4406)**:
  - Target: ISO 16/14/11 or cleaner
  - Alert: ISO 18/16/13 → Filter or change oil
  
- **Water Contamination**:
  - Normal: <200 ppm
  - Alert: 200-1000 ppm → Investigate source
  - Critical: >1000 ppm → Immediate oil change
  
- **Wear Metals (ppm)**:
  - Iron: <75 ppm (bearing/gear wear)
  - Copper: <50 ppm (bushing/bearing wear)
  - Aluminum: <15 ppm (pump/compressor wear)
  - Exceeding limits → Plan component inspection

### 4.4 Ultrasonic Testing
**Purpose**: Detect leaks, electrical arcing, bearing lubrication issues

**Applications**:
- Compressed air leak detection
- Steam trap testing
- Electrical corona/arcing detection
- Bearing lubrication monitoring

**Leak Detection Savings**:
- 3mm air leak @ 7 bar = $2,500/year wasted energy
- Regular surveys can save 10-30% of compressed air costs

**Bearing Lubrication Monitoring**:
- Baseline dB reading when properly lubricated
- +8 dB above baseline → Under-lubricated (add grease)
- +35 dB above baseline → Over-lubricated (purge excess)

### 4.5 Motor Current Signature Analysis (MCSA)
**Purpose**: Detect electrical and mechanical faults in motors

**Parameters Monitored**:
- Current imbalance between phases
- Harmonic distortion
- Rotor bar defects
- Air gap eccentricity

**Thresholds**:
- **Current Imbalance**: <5% acceptable, >10% investigate
- **Total Harmonic Distortion (THD)**: <5% good, >8% poor power quality
- **Rotor Bar Health**: <20% broken bars, >20% repair/replace

## 5. Equipment Criticality Classification

### A-Class (Critical)
- **Failure Impact**: Complete production stoppage
- **Monitoring**: Real-time sensors + weekly inspection
- **RUL Threshold**: Repair when RUL <60 days
- **Examples**: Main mill motors, primary compressors, cooling tower pumps

### B-Class (Important)
- **Failure Impact**: Partial production loss
- **Monitoring**: Weekly/bi-weekly inspection
- **RUL Threshold**: Repair when RUL <30 days
- **Examples**: Conveyor motors, auxiliary pumps, HVAC systems

### C-Class (Standard)
- **Failure Impact**: Minimal production impact
- **Monitoring**: Monthly inspection
- **RUL Threshold**: Run to failure or routine replacement
- **Examples**: Office HVAC, lighting, small tools

## 6. Remaining Useful Life (RUL) Estimation

### RUL Calculation Methodology
RUL is estimated by tracking degradation trends and comparing to historical failure data.

**Input Parameters**:
- Vibration trend slope
- Temperature trend
- Operating hours since last maintenance
- Historical failure patterns
- Manufacturer recommended life

**RUL Formula (Simplified)**:
```
RUL = (Failure_Threshold - Current_Value) / Degradation_Rate
```

**Example - Bearing RUL**:
- Current vibration: 5.0 mm/s RMS
- Failure threshold: 11.2 mm/s RMS
- Degradation rate: 0.5 mm/s per month
- RUL = (11.2 - 5.0) / 0.5 = 12.4 months

### Confidence Levels
- **High Confidence**: Multiple parameter trends align (vibration + temperature + oil)
- **Medium Confidence**: Single parameter trending
- **Low Confidence**: Insufficient historical data or erratic readings

## 7. Predictive Maintenance Workflow

### Step 1: Data Collection
- Collect sensor readings (vibration, temperature, current)
- Sample oil and send for laboratory analysis
- Perform thermographic scans
- Record operating hours and load conditions

### Step 2: Data Analysis
- Compare readings to baseline and thresholds
- Identify trending parameters
- Calculate rate of degradation
- Estimate RUL for degrading equipment

### Step 3: Fault Diagnosis
- Identify root cause of abnormal conditions
- Determine failure mode (bearing, misalignment, etc.)
- Assess severity and urgency
- Classify equipment risk level

### Step 4: Maintenance Planning
- Schedule corrective action based on RUL
- Coordinate with production schedule
- Order spare parts with lead time buffer
- Assign technicians and allocate resources

### Step 5: Execute and Verify
- Perform planned maintenance during shutdown
- Replace or repair identified defects
- Establish new baseline after repair
- Verify improvement in monitored parameters

### Step 6: Continuous Improvement
- Log failure mode and root cause
- Update RUL prediction models
- Adjust monitoring thresholds if needed
- Train team on lessons learned

## 8. Alarm Management

### Tier 1: Advisory
- **Condition**: Parameter in caution range
- **Action**: Log for trending, no immediate action
- **Response Time**: Next scheduled inspection

### Tier 2: Warning
- **Condition**: Parameter in alert range
- **Action**: Investigate within 48 hours
- **Response Time**: Schedule maintenance within 2 weeks

### Tier 3: Alarm
- **Condition**: Parameter in danger range
- **Action**: Plan immediate maintenance
- **Response Time**: Shutdown within 72 hours

### Tier 4: Critical
- **Condition**: Imminent failure detected
- **Action**: Emergency shutdown and repair
- **Response Time**: Immediate (<4 hours)

## 9. Data Management and Reporting

### Database Requirements
- Store all sensor readings with timestamps
- Maintain equipment baseline values
- Track maintenance history and work orders
- Log spare parts usage and costs
- Archive oil analysis reports

### Monthly Predictive Maintenance Report
Include:
- Equipment health summary (by criticality class)
- New alerts and warnings generated
- Maintenance actions completed
- Cost savings from prevented failures
- RUL predictions for critical equipment
- Recommendations for next month

### Key Performance Indicators (KPIs)
- **Mean Time Between Failures (MTBF)**: Target >2000 hours
- **Planned vs Unplanned Maintenance Ratio**: Target 80:20
- **Predictive Maintenance Compliance**: Target >90%
- **Early Fault Detection Rate**: Target >85%
- **Cost Avoidance**: Target >$100K/month

## 10. Training Requirements
All maintenance technicians must complete:
- ISO Category I Vibration Analyst (40 hours)
- Thermography Level 1 Certification (24 hours)
- Oil analysis sampling procedures (8 hours)
- Equipment criticality and RUL concepts (4 hours)

## 11. Tools and Equipment Inventory
- Vibration analyzer (SKF, Fluke, or equivalent)
- Infrared camera (minimum 320×240 resolution)
- Ultrasonic leak detector
- Oil sampling kits and bottles
- Current clamp meters
- Data collection tablets with CMMS software

## 12. Continuous Improvement Initiatives
- Quarterly review of RUL prediction accuracy
- Annual update of baseline values
- Benchmark against industry standards
- Invest in advanced analytics (AI/ML models)
- Expand sensor coverage on critical equipment

## 13. Emergency Contacts
- Predictive Maintenance Engineer: Ext. 2410
- Reliability Manager: Ext. 2400
- Vibration Analysis Vendor: +1-555-VIBE-1
- Oil Analysis Lab: lab@oilanalysis.com
