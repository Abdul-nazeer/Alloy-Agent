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
