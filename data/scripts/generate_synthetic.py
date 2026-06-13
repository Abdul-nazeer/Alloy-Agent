"""
Synthetic Training Data Generator for Steel Plant Maintenance
Generates edge cases and scenarios not well-represented in real datasets.
NO API KEYS REQUIRED - Rule-based generation with physics-informed constraints.
"""

import json
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

from config import (
    EQUIPMENT_CONFIGS,
    SENSOR_CONFIGS,
    SEVERITY_THRESHOLDS,
    MAINTENANCE_ACTIONS,
    LONG_TERM_RECOMMENDATIONS,
    DOWNTIME_ESTIMATES,
    get_equipment_config,
    get_sensor_config
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TrainingSample:
    """Structured training sample for fine-tuning."""
    instruction: str
    input: str
    output: str
    metadata: Dict
    
    def to_dict(self):
        return asdict(self)


class SyntheticDataGenerator:
    """Production-grade synthetic data generator for edge cases."""
    
    def __init__(self, output_dir: str, target_samples: int = 200):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.target_samples = target_samples
        
        self.stats = {
            'cascading_failures': 0,
            'extreme_edge_cases': 0,
            'rare_conditions': 0,
            'complex_diagnostics': 0,
            'total_generated': 0
        }
        
        # Scenario distribution
        self.scenario_weights = {
            'cascading_failures': 0.30,
            'extreme_edge_cases': 0.25,
            'rare_conditions': 0.25,
            'complex_diagnostics': 0.20
        }
        
        # Equipment types for synthetic generation
        self.equipment_types = list(EQUIPMENT_CONFIGS.keys())
        
        # Additional steel plant equipment not in CMAPSS
        self.extended_equipment = {
            'rolling_mill': {
                'name': 'Rolling Mill Drive System',
                'sensors': ['motor_temperature', 'bearing_temperature', 'load_current', 'vibration'],
                'faults': ['Bearing wear', 'Motor overheating', 'Drive belt damage', 'Misalignment']
            },
            'hydraulic_press': {
                'name': 'Hydraulic Press System',
                'sensors': ['hydraulic_pressure', 'oil_temperature', 'cylinder_position', 'flow_rate'],
                'faults': ['Seal leakage', 'Pump degradation', 'Valve malfunction', 'Oil contamination']
            },
            'cooling_tower': {
                'name': 'Cooling Tower System',
                'sensors': ['water_temperature', 'flow_rate', 'fan_speed', 'chemical_balance'],
                'faults': ['Scale buildup', 'Fan failure', 'Pump cavitation', 'Biological growth']
            }
        }
    
    def generate_cascading_failure(self, sample_id: int) -> TrainingSample:
        """Generate cascading failure scenario (multi-equipment impact)."""
        # Primary failure equipment
        primary_fault = np.random.choice(self.equipment_types)
        equipment_config = get_equipment_config(primary_fault)
        
        # Generate sensor readings with cascading effects
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        # Primary equipment - severe degradation
        severity = np.random.choice(['HIGH', 'CRITICAL'])
        rul_hours = np.random.randint(8, 40) if severity == 'HIGH' else np.random.randint(1, 8)
        operating_hours = np.random.randint(8000, 25000)
        
        # Cascading impact - sensors show correlated failures
        temp_spike = np.random.uniform(20, 35) if severity == 'CRITICAL' else np.random.uniform(10, 20)
        pressure_drop = np.random.uniform(-1.5, -0.3)
        vibration_increase = np.random.uniform(25, 50) if severity == 'CRITICAL' else np.random.uniform(15, 25)
        efficiency_drop = np.random.uniform(8, 15) if severity == 'CRITICAL' else np.random.uniform(4, 8)
        
        sensors = {
            'discharge_temperature': round(temp_config.baseline_value + temp_spike, 1),
            'discharge_pressure': round(pressure_config.baseline_value + pressure_drop, 2),
            'compressor_rpm': int(3500 - np.random.randint(100, 400)),
            'vibration_level': round(vibration_config.baseline_value + vibration_increase, 1),
            'efficiency': round(efficiency_config.baseline_value - efficiency_drop, 1)
        }
        
        equipment_id = f"{equipment_config.steel_equivalent.replace(' ', '-')}-{np.random.randint(100, 999)}"
        
        # Secondary equipment affected
        secondary_equipment = np.random.choice(['Cooling System', 'Bearing Assembly', 'Lubrication System'])
        
        instruction = f"Analyze cascading equipment failure and predict maintenance requirements for {equipment_config.steel_equivalent}."
        
        input_data = f"""Equipment: {equipment_config.steel_equivalent} | ID: {equipment_id}
Operating Hours: {operating_hours:,} hours

Current Sensor Readings:
- Discharge Temperature: {sensors['discharge_temperature']}°C (baseline: {temp_config.baseline_value}°C, delta: +{temp_spike:.1f}°C) ⚠️ ALARM
- Discharge Pressure: {sensors['discharge_pressure']} bar (baseline: {pressure_config.baseline_value} bar, delta: {pressure_drop:.2f} bar) ⚠️
- Compressor Speed: {sensors['compressor_rpm']} RPM (rated: 3500 RPM) 
- Vibration Level: {sensors['vibration_level']} Hz (baseline: {vibration_config.baseline_value} Hz, delta: +{vibration_increase:.1f} Hz) ⚠️ CRITICAL
- Operating Efficiency: {sensors['efficiency']}% (baseline: {efficiency_config.baseline_value}%, delta: -{efficiency_drop:.1f}%)

ALERT: Multiple system alarms - Cascading failure detected
SECONDARY IMPACT: {secondary_equipment} showing abnormal readings
Trend: Rapid deterioration over past 12 hours"""

        # Generate cascading failure diagnosis
        diagnosis = f"{equipment_config.steel_equivalent} experiencing cascading failure with multi-system impact. "
        diagnosis += f"Primary fault in {equipment_config.name} with discharge temperature at {sensors['discharge_temperature']}°C "
        diagnosis += f"(+{temp_spike:.1f}°C above baseline). "
        diagnosis += f"Vibration levels critically elevated to {sensors['vibration_level']} Hz. "
        diagnosis += f"Secondary impact detected in {secondary_equipment}. "
        diagnosis += f"Efficiency degraded to {sensors['efficiency']}%. "
        diagnosis += "Pattern indicates primary component failure with downstream equipment stress."
        
        root_cause = f"Cascading failure initiated after {operating_hours:,} operating hours. "
        root_cause += f"Primary cause: Critical failure in {np.random.choice(equipment_config.common_faults)} "
        root_cause += f"causing thermal overload and vibration propagation. "
        root_cause += f"Secondary cause: {secondary_equipment} unable to compensate for primary equipment degradation, "
        root_cause += f"leading to system-wide performance collapse. "
        root_cause += f"Rapid onset (12 hours) suggests catastrophic component failure rather than gradual wear."
        
        # Actions for cascading failures
        actions = MAINTENANCE_ACTIONS[primary_fault][severity][:2]
        actions.extend([
            f"Inspect {secondary_equipment} for collateral damage",
            "Implement temporary bypass or redundancy if available",
            "Review system interlocks and alarm response procedures",
            "Prepare for extended downtime due to multi-system repairs"
        ])
        
        long_term = LONG_TERM_RECOMMENDATIONS[primary_fault][:3]
        long_term.extend([
            f"Install redundant {secondary_equipment} to prevent cascading failures",
            "Implement real-time multi-equipment correlation monitoring"
        ])
        
        confidence = np.random.uniform(0.82, 0.94)
        downtime_est = DOWNTIME_ESTIMATES[severity]
        # Add extra time for cascading repairs
        downtime_extra = np.random.randint(4, 8)
        
        output = f"""DIAGNOSIS: {diagnosis}

ROOT CAUSE: {root_cause}

RISK LEVEL: {severity}

CASCADING IMPACT: Secondary failure in {secondary_equipment}

REMAINING USEFUL LIFE (RUL): Approximately {rul_hours} operating hours

CONFIDENCE: {confidence:.2f}

IMMEDIATE ACTIONS:
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(actions[:6]))}

LONG-TERM RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in long_term[:5])}

ESTIMATED DOWNTIME: {downtime_est['min']+downtime_extra}-{downtime_est['max']+downtime_extra} {downtime_est['unit']} (includes secondary system repairs)

SPARE PARTS REQUIRED: Primary equipment overhaul kit, {secondary_equipment} components, emergency spares

MANUAL REFERENCE: {equipment_config.steel_equivalent} Emergency Response Section {np.random.randint(8, 12)}.{np.random.randint(1, 9)}"""
        
        metadata = {
            'source': 'SYNTHETIC',
            'scenario_type': 'cascading_failure',
            'fault_mode': primary_fault,
            'severity': severity,
            'equipment': equipment_config.steel_equivalent,
            'secondary_impact': secondary_equipment,
            'rul_hours': rul_hours,
            'operating_hours': operating_hours,
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['cascading_failures'] += 1
        return TrainingSample(instruction, input_data, output, metadata)
    
    def generate_extreme_edge_case(self, sample_id: int) -> TrainingSample:
        """Generate extreme edge case (very sudden or very slow degradation)."""
        fault_mode = np.random.choice(self.equipment_types)
        equipment_config = get_equipment_config(fault_mode)
        
        # Choose edge case type
        edge_case_type = np.random.choice(['sudden_failure', 'very_early_warning'])
        
        if edge_case_type == 'sudden_failure':
            # Near-instant failure (< 4 hours RUL)
            severity = 'CRITICAL'
            rul_hours = np.random.randint(1, 4)
            operating_hours = np.random.randint(5000, 30000)
            
            temp_config = get_sensor_config('temperature')
            vibration_config = get_sensor_config('vibration')
            efficiency_config = get_sensor_config('efficiency')
            
            # Extreme sensor readings
            sensors = {
                'discharge_temperature': round(temp_config.critical_threshold + np.random.uniform(5, 15), 1),
                'discharge_pressure': round(get_sensor_config('pressure').baseline_value - np.random.uniform(2, 3), 2),
                'compressor_rpm': int(3500 - np.random.randint(500, 800)),
                'vibration_level': round(vibration_config.critical_threshold + np.random.uniform(10, 30), 1),
                'efficiency': round(efficiency_config.critical_threshold - np.random.uniform(5, 12), 1)
            }
            
            alert_msg = "⚠️⚠️ EMERGENCY - IMMINENT FAILURE ⚠️⚠️"
            trend_msg = "SUDDEN ONSET - All parameters degraded rapidly in past 2 hours"
            
        else:  # very_early_warning
            # Very early detection (> 400 hours RUL)
            severity = 'LOW'
            rul_hours = np.random.randint(400, 800)
            operating_hours = np.random.randint(2000, 8000)
            
            temp_config = get_sensor_config('temperature')
            vibration_config = get_sensor_config('vibration')
            efficiency_config = get_sensor_config('efficiency')
            
            # Subtle sensor changes
            sensors = {
                'discharge_temperature': round(temp_config.baseline_value + np.random.uniform(2, 6), 1),
                'discharge_pressure': round(get_sensor_config('pressure').baseline_value + np.random.uniform(-0.2, 0.3), 2),
                'compressor_rpm': int(3500 - np.random.randint(20, 80)),
                'vibration_level': round(vibration_config.baseline_value + np.random.uniform(3, 8), 1),
                'efficiency': round(efficiency_config.baseline_value - np.random.uniform(0.5, 2), 1)
            }
            
            alert_msg = "Early warning detected - Subtle degradation pattern"
            trend_msg = "Very gradual degradation over past 90 days - Predictive maintenance opportunity"
        
        equipment_id = f"{equipment_config.steel_equivalent.replace(' ', '-')}-{np.random.randint(100, 999)}"
        
        instruction = f"Analyze equipment degradation pattern and predict maintenance requirements for {equipment_config.steel_equivalent}."
        
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        input_data = f"""Equipment: {equipment_config.steel_equivalent} | ID: {equipment_id}
Operating Hours: {operating_hours:,} hours

Current Sensor Readings:
- Discharge Temperature: {sensors['discharge_temperature']}°C (baseline: {temp_config.baseline_value}°C, delta: +{sensors['discharge_temperature']-temp_config.baseline_value:.1f}°C)
- Discharge Pressure: {sensors['discharge_pressure']} bar (baseline: {pressure_config.baseline_value} bar)
- Compressor Speed: {sensors['compressor_rpm']} RPM (rated: 3500 RPM)
- Vibration Level: {sensors['vibration_level']} Hz (baseline: {vibration_config.baseline_value} Hz)
- Operating Efficiency: {sensors['efficiency']}% (baseline: {efficiency_config.baseline_value}%)

{alert_msg}
Trend: {trend_msg}"""

        if edge_case_type == 'sudden_failure':
            diagnosis = f"EMERGENCY: {equipment_config.steel_equivalent} experiencing catastrophic failure. "
            diagnosis += f"Temperature critically elevated to {sensors['discharge_temperature']}°C. "
            diagnosis += f"Vibration at {sensors['vibration_level']} Hz indicates imminent mechanical failure. "
            diagnosis += f"Efficiency collapsed to {sensors['efficiency']}%. "
            diagnosis += "Immediate shutdown required to prevent equipment destruction and safety hazard."
            
            root_cause = f"Catastrophic failure after {operating_hours:,} operating hours. "
            root_cause += "Primary cause: Sudden bearing seizure or blade separation causing immediate mechanical failure. "
            root_cause += "Contributing factor: Possible lubrication system failure or foreign object damage. "
            root_cause += "Rapid onset suggests discrete failure event rather than gradual degradation."
        else:
            diagnosis = f"{equipment_config.steel_equivalent} showing early-stage degradation. "
            diagnosis += f"Temperature marginally elevated to {sensors['discharge_temperature']}°C. "
            diagnosis += f"Vibration slightly increased to {sensors['vibration_level']} Hz. "
            diagnosis += f"Efficiency at {sensors['efficiency']}% shows minor decline. "
            diagnosis += "Pattern indicates beginning of degradation cycle - optimal time for preventive action."
            
            root_cause = f"Early-stage degradation detected after {operating_hours:,} operating hours. "
            root_cause += "Primary cause: Initial stage of blade surface fouling or seal wear beginning. "
            root_cause += "Predictive analytics detected subtle patterns before traditional alarm thresholds. "
            root_cause += f"Estimated {rul_hours} hours remaining provides ample planning time for scheduled maintenance."
        
        actions = MAINTENANCE_ACTIONS[fault_mode][severity][:4]
        long_term = LONG_TERM_RECOMMENDATIONS[fault_mode][:4]
        
        confidence = np.random.uniform(0.88, 0.96) if edge_case_type == 'sudden_failure' else np.random.uniform(0.65, 0.78)
        downtime_est = DOWNTIME_ESTIMATES[severity]
        
        output = f"""DIAGNOSIS: {diagnosis}

ROOT CAUSE: {root_cause}

RISK LEVEL: {severity}

REMAINING USEFUL LIFE (RUL): Approximately {rul_hours} operating hours

CONFIDENCE: {confidence:.2f}

IMMEDIATE ACTIONS:
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(actions))}

LONG-TERM RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in long_term)}

ESTIMATED DOWNTIME: {downtime_est['min']}-{downtime_est['max']} {downtime_est['unit']}

SPARE PARTS REQUIRED: {'Emergency replacement unit, critical components' if edge_case_type == 'sudden_failure' else 'Standard maintenance kit, inspection tools'}

MANUAL REFERENCE: {equipment_config.steel_equivalent} Maintenance Manual Section {np.random.randint(3, 10)}.{np.random.randint(1, 9)}"""

        metadata = {
            'source': 'SYNTHETIC',
            'scenario_type': 'extreme_edge_case',
            'edge_case_subtype': edge_case_type,
            'fault_mode': fault_mode,
            'severity': severity,
            'equipment': equipment_config.steel_equivalent,
            'rul_hours': rul_hours,
            'operating_hours': operating_hours,
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['extreme_edge_cases'] += 1
        return TrainingSample(instruction, input_data, output, metadata)
    
    def generate_rare_condition(self, sample_id: int) -> TrainingSample:
        """Generate rare operating condition scenario."""
        fault_mode = np.random.choice(self.equipment_types)
        equipment_config = get_equipment_config(fault_mode)
        
        # Choose rare condition type
        condition_type = np.random.choice(['extreme_temperature', 'high_load', 'intermittent'])
        
        severity = np.random.choice(['MEDIUM', 'HIGH'])
        rul_hours = np.random.randint(20, 100) if severity == 'HIGH' else np.random.randint(100, 250)
        operating_hours = np.random.randint(10000, 35000)
        
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        if condition_type == 'extreme_temperature':
            # Extreme ambient or process temperature
            extreme_temp = np.random.choice([
                temp_config.normal_range[0] - 10,  # Cold environment
                temp_config.critical_threshold + np.random.uniform(0, 8)  # Hot environment
            ])
            sensors = {
                'discharge_temperature': round(extreme_temp, 1),
                'discharge_pressure': round(pressure_config.baseline_value + np.random.uniform(-0.5, 0.5), 2),
                'compressor_rpm': int(3500 - np.random.randint(100, 250)),
                'vibration_level': round(vibration_config.baseline_value + np.random.uniform(12, 20), 1),
                'efficiency': round(efficiency_config.baseline_value - np.random.uniform(5, 10), 1)
            }
            condition_desc = f"Extreme temperature operation ({'sub-baseline' if extreme_temp < temp_config.normal_range[0] else 'above critical'})"
            
        elif condition_type == 'high_load':
            # Continuous high-load operation
            sensors = {
                'discharge_temperature': round(temp_config.baseline_value + np.random.uniform(12, 18), 1),
                'discharge_pressure': round(pressure_config.normal_range[1] + np.random.uniform(0, 0.8), 2),
                'compressor_rpm': int(3800 + np.random.randint(0, 200)),  # Above rated
                'vibration_level': round(vibration_config.baseline_value + np.random.uniform(18, 28), 1),
                'efficiency': round(efficiency_config.baseline_value - np.random.uniform(3, 7), 1)
            }
            condition_desc = "Sustained high-load operation above rated capacity"
            
        else:  # intermittent
            # Intermittent fault pattern
            sensors = {
                'discharge_temperature': round(temp_config.baseline_value + np.random.uniform(8, 15), 1),
                'discharge_pressure': round(pressure_config.baseline_value + np.random.uniform(-0.8, -0.2), 2),
                'compressor_rpm': int(3500 - np.random.randint(150, 300)),
                'vibration_level': round(vibration_config.baseline_value + np.random.uniform(15, 25), 1),
                'efficiency': round(efficiency_config.baseline_value - np.random.uniform(4, 8), 1)
            }
            condition_desc = "Intermittent fault - symptoms appear and disappear"
        
        equipment_id = f"{equipment_config.steel_equivalent.replace(' ', '-')}-{np.random.randint(100, 999)}"
        
        instruction = f"Analyze rare operating condition and predict maintenance requirements for {equipment_config.steel_equivalent}."
        
        input_data = f"""Equipment: {equipment_config.steel_equivalent} | ID: {equipment_id}
Operating Hours: {operating_hours:,} hours

Current Sensor Readings:
- Discharge Temperature: {sensors['discharge_temperature']}°C (baseline: {temp_config.baseline_value}°C)
- Discharge Pressure: {sensors['discharge_pressure']} bar (baseline: {pressure_config.baseline_value} bar)
- Compressor Speed: {sensors['compressor_rpm']} RPM (rated: 3500 RPM)
- Vibration Level: {sensors['vibration_level']} Hz (baseline: {vibration_config.baseline_value} Hz)
- Operating Efficiency: {sensors['efficiency']}% (baseline: {efficiency_config.baseline_value}%)

RARE CONDITION: {condition_desc}
Trend: Degradation accelerated by unusual operating conditions
Alert: Non-standard operating pattern detected"""

        diagnosis = f"{equipment_config.steel_equivalent} degrading under rare operating conditions. "
        diagnosis += f"Condition: {condition_desc}. "
        diagnosis += f"Temperature at {sensors['discharge_temperature']}°C, vibration {sensors['vibration_level']} Hz, "
        diagnosis += f"efficiency {sensors['efficiency']}%. "
        diagnosis += "Unusual operating profile accelerating normal wear patterns."
        
        root_cause = f"Degradation after {operating_hours:,} operating hours under non-standard conditions. "
        root_cause += f"Primary cause: {np.random.choice(equipment_config.common_faults)} accelerated by {condition_desc}. "
        if condition_type == 'intermittent':
            root_cause += "Intermittent nature suggests electrical fault, loose connection, or thermally-dependent failure mode. "
        else:
            root_cause += f"Continuous operation outside design envelope causing accelerated component degradation. "
        root_cause += "Standard failure models may underestimate risk under these conditions."
        
        actions = MAINTENANCE_ACTIONS[fault_mode][severity][:3]
        actions.extend([
            f"Review operating parameters - reduce load if {condition_desc}",
            "Engineering review of operating envelope compliance",
            "Consider equipment upgrade if conditions persist"
        ])
        
        long_term = LONG_TERM_RECOMMENDATIONS[fault_mode][:3]
        long_term.append(f"Evaluate equipment specification vs actual operating conditions")
        
        confidence = np.random.uniform(0.68, 0.82)  # Lower confidence for rare conditions
        downtime_est = DOWNTIME_ESTIMATES[severity]
        
        output = f"""DIAGNOSIS: {diagnosis}

ROOT CAUSE: {root_cause}

RISK LEVEL: {severity}

OPERATING CONDITION: {condition_desc} (Non-standard)

REMAINING USEFUL LIFE (RUL): Approximately {rul_hours} operating hours (reduced due to operating conditions)

CONFIDENCE: {confidence:.2f} (lower confidence due to rare operating profile)

IMMEDIATE ACTIONS:
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(actions[:6]))}

LONG-TERM RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in long_term)}

ESTIMATED DOWNTIME: {downtime_est['min']}-{downtime_est['max']} {downtime_est['unit']}

SPARE PARTS REQUIRED: Standard overhaul kit plus high-temperature/high-load rated components

MANUAL REFERENCE: {equipment_config.steel_equivalent} Maintenance Manual Section {np.random.randint(4, 9)}.{np.random.randint(1, 9)}"""
        
        metadata = {
            'source': 'SYNTHETIC',
            'scenario_type': 'rare_condition',
            'condition_subtype': condition_type,
            'fault_mode': fault_mode,
            'severity': severity,
            'equipment': equipment_config.steel_equivalent,
            'rul_hours': rul_hours,
            'operating_hours': operating_hours,
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['rare_conditions'] += 1
        return TrainingSample(instruction, input_data, output, metadata)
    
    def generate_complex_diagnostic(self, sample_id: int) -> TrainingSample:
        """Generate complex diagnostic scenario (ambiguous symptoms, multiple possible causes)."""
        fault_mode = np.random.choice(self.equipment_types)
        equipment_config = get_equipment_config(fault_mode)
        
        severity = np.random.choice(['MEDIUM', 'HIGH'])
        rul_hours = np.random.randint(30, 80) if severity == 'HIGH' else np.random.randint(80, 200)
        operating_hours = np.random.randint(12000, 28000)
        
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        # Ambiguous sensor pattern
        sensors = {
            'discharge_temperature': round(temp_config.baseline_value + np.random.uniform(7, 12), 1),
            'discharge_pressure': round(pressure_config.baseline_value + np.random.uniform(-0.6, 0.3), 2),
            'compressor_rpm': int(3500 - np.random.randint(80, 180)),
            'vibration_level': round(vibration_config.baseline_value + np.random.uniform(10, 18), 1),
            'efficiency': round(efficiency_config.baseline_value - np.random.uniform(3, 6), 1)
        }
        
        equipment_id = f"{equipment_config.steel_equivalent.replace(' ', '-')}-{np.random.randint(100, 999)}"
        
        # Multiple possible root causes
        possible_causes = equipment_config.common_faults[:3]
        primary_cause = possible_causes[0]
        alternative_causes = possible_causes[1:]
        
        instruction = f"Analyze complex degradation pattern with ambiguous symptoms for {equipment_config.steel_equivalent}."
        
        input_data = f"""Equipment: {equipment_config.steel_equivalent} | ID: {equipment_id}
Operating Hours: {operating_hours:,} hours

Current Sensor Readings:
- Discharge Temperature: {sensors['discharge_temperature']}°C (baseline: {temp_config.baseline_value}°C, delta: +{sensors['discharge_temperature']-temp_config.baseline_value:.1f}°C)
- Discharge Pressure: {sensors['discharge_pressure']} bar (baseline: {pressure_config.baseline_value} bar)
- Compressor Speed: {sensors['compressor_rpm']} RPM (rated: 3500 RPM)
- Vibration Level: {sensors['vibration_level']} Hz (baseline: {vibration_config.baseline_value} Hz, delta: +{sensors['vibration_level']-vibration_config.baseline_value:.1f} Hz)
- Operating Efficiency: {sensors['efficiency']}% (baseline: {efficiency_config.baseline_value}%)

DIAGNOSTIC CHALLENGE: Symptoms consistent with multiple failure modes
Trend: Gradual degradation with inconsistent sensor correlation
Alert: Further investigation required for definitive diagnosis"""

        diagnosis = f"{equipment_config.steel_equivalent} showing degradation with ambiguous symptom pattern. "
        diagnosis += f"Temperature elevated to {sensors['discharge_temperature']}°C, "
        diagnosis += f"vibration at {sensors['vibration_level']} Hz, "
        diagnosis += f"efficiency at {sensors['efficiency']}%. "
        diagnosis += f"Sensor pattern consistent with multiple possible failure modes. "
        diagnosis += "Recommend additional diagnostic testing for definitive root cause identification."
        
        root_cause = f"Complex degradation after {operating_hours:,} operating hours. "
        root_cause += f"Most likely cause: {primary_cause} based on dominant symptom pattern. "
        root_cause += f"Alternative possibilities: {', '.join(alternative_causes)}. "
        root_cause += "Recommend borescope inspection, oil analysis, and vibration spectrum analysis to differentiate between causes. "
        root_cause += "Treatment approach will vary significantly based on actual root cause."
        
        actions = [
            f"Conduct detailed inspection to differentiate between {primary_cause} and alternatives",
            "Perform borescope inspection of internal components",
            "Schedule oil analysis and vibration spectrum analysis",
            "Monitor sensor trends closely for pattern clarification"
        ]
        actions.extend(MAINTENANCE_ACTIONS[fault_mode][severity][:2])
        
        long_term = LONG_TERM_RECOMMENDATIONS[fault_mode][:3]
        long_term.append("Implement advanced diagnostics for faster root cause identification")
        
        confidence = np.random.uniform(0.62, 0.75)  # Lower confidence for ambiguous cases
        downtime_est = DOWNTIME_ESTIMATES[severity]
        
        output = f"""DIAGNOSIS: {diagnosis}

ROOT CAUSE: {root_cause}

RISK LEVEL: {severity}

DIAGNOSTIC COMPLEXITY: High - Multiple possible failure modes

PRIMARY HYPOTHESIS: {primary_cause} (60-70% probability)
ALTERNATIVE HYPOTHESES: {', '.join(alternative_causes)}

REMAINING USEFUL LIFE (RUL): Approximately {rul_hours} operating hours

CONFIDENCE: {confidence:.2f} (moderate confidence due to diagnostic ambiguity)

IMMEDIATE ACTIONS:
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(actions[:6]))}

LONG-TERM RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in long_term)}

ESTIMATED DOWNTIME: {downtime_est['min']}-{downtime_est['max']+4} {downtime_est['unit']} (includes diagnostic time)

SPARE PARTS REQUIRED: Prepare multiple component sets based on possible failure modes

MANUAL REFERENCE: {equipment_config.steel_equivalent} Diagnostic Guide Section {np.random.randint(6, 10)}.{np.random.randint(1, 9)}"""

        metadata = {
            'source': 'SYNTHETIC',
            'scenario_type': 'complex_diagnostic',
            'fault_mode': fault_mode,
            'severity': severity,
            'equipment': equipment_config.steel_equivalent,
            'primary_hypothesis': primary_cause,
            'alternative_hypotheses': alternative_causes,
            'rul_hours': rul_hours,
            'operating_hours': operating_hours,
            'sample_id': sample_id,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['complex_diagnostics'] += 1
        return TrainingSample(instruction, input_data, output, metadata)
    
    def generate_all(self) -> List[TrainingSample]:
        """Generate all synthetic samples according to distribution."""
        logger.info(f"Starting synthetic data generation (target: {self.target_samples} samples)...")
        
        samples = []
        
        # Calculate samples per scenario
        samples_per_scenario = {
            'cascading_failures': int(self.target_samples * self.scenario_weights['cascading_failures']),
            'extreme_edge_cases': int(self.target_samples * self.scenario_weights['extreme_edge_cases']),
            'rare_conditions': int(self.target_samples * self.scenario_weights['rare_conditions']),
            'complex_diagnostics': int(self.target_samples * self.scenario_weights['complex_diagnostics'])
        }
        
        # Adjust for rounding
        total_allocated = sum(samples_per_scenario.values())
        if total_allocated < self.target_samples:
            samples_per_scenario['cascading_failures'] += (self.target_samples - total_allocated)
        
        sample_id = 0
        
        # Generate cascading failures
        logger.info(f"Generating {samples_per_scenario['cascading_failures']} cascading failure samples...")
        for _ in range(samples_per_scenario['cascading_failures']):
            samples.append(self.generate_cascading_failure(sample_id))
            sample_id += 1
            self.stats['total_generated'] += 1
        
        # Generate extreme edge cases
        logger.info(f"Generating {samples_per_scenario['extreme_edge_cases']} extreme edge case samples...")
        for _ in range(samples_per_scenario['extreme_edge_cases']):
            samples.append(self.generate_extreme_edge_case(sample_id))
            sample_id += 1
            self.stats['total_generated'] += 1
        
        # Generate rare conditions
        logger.info(f"Generating {samples_per_scenario['rare_conditions']} rare condition samples...")
        for _ in range(samples_per_scenario['rare_conditions']):
            samples.append(self.generate_rare_condition(sample_id))
            sample_id += 1
            self.stats['total_generated'] += 1
        
        # Generate complex diagnostics
        logger.info(f"Generating {samples_per_scenario['complex_diagnostics']} complex diagnostic samples...")
        for _ in range(samples_per_scenario['complex_diagnostics']):
            samples.append(self.generate_complex_diagnostic(sample_id))
            sample_id += 1
            self.stats['total_generated'] += 1
        
        logger.info(f"Generated {len(samples)} synthetic samples")
        return samples
    
    def save_samples(self, samples: List[TrainingSample], output_file: str = "synthetic_samples.jsonl"):
        """Save samples to JSONL format."""
        output_path = self.output_dir / output_file
        
        logger.info(f"\nSaving {len(samples)} samples to {output_path}")
        
        try:
            with open(output_path, 'w') as f:
                for sample in samples:
                    json.dump(sample.to_dict(), f)
                    f.write('\n')
            
            logger.info(f"Successfully saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving samples: {e}")
            raise
    
    def print_stats(self):
        """Print generation statistics."""
        logger.info("\n" + "="*60)
        logger.info("SYNTHETIC DATA GENERATION STATISTICS")
        logger.info("="*60)
        logger.info(f"Cascading Failures: {self.stats['cascading_failures']} ({self.scenario_weights['cascading_failures']*100:.0f}%)")
        logger.info(f"Extreme Edge Cases: {self.stats['extreme_edge_cases']} ({self.scenario_weights['extreme_edge_cases']*100:.0f}%)")
        logger.info(f"Rare Conditions: {self.stats['rare_conditions']} ({self.scenario_weights['rare_conditions']*100:.0f}%)")
        logger.info(f"Complex Diagnostics: {self.stats['complex_diagnostics']} ({self.scenario_weights['complex_diagnostics']*100:.0f}%)")
        logger.info("-"*60)
        logger.info(f"Total Generated: {self.stats['total_generated']}")
        logger.info("="*60)


def main():
    """Main execution function."""
    # Paths
    base_dir = Path(__file__).parent.parent
    output_dir = base_dir / "processed"
    
    # Generate
    generator = SyntheticDataGenerator(str(output_dir), target_samples=200)
    samples = generator.generate_all()
    generator.save_samples(samples)
    generator.print_stats()
    
    # Show sample output
    if samples:
        logger.info("\n" + "="*60)
        logger.info("SAMPLE OUTPUT (Cascading Failure Example)")
        logger.info("="*60)
        sample = samples[0]
        print(f"\nINSTRUCTION:\n{sample.instruction}\n")
        print(f"INPUT:\n{sample.input}\n")
        print(f"OUTPUT:\n{sample.output}\n")
        print(f"METADATA:\n{json.dumps(sample.metadata, indent=2)}")


if __name__ == "__main__":
    main()
