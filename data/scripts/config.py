"""
Configuration for data processing pipeline.
All hardcoded values centralized here for easy maintenance.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SensorConfig:
    """Configuration for a single sensor."""
    name: str
    steel_equivalent: str
    unit: str
    baseline_value: float
    normal_range: tuple  # (min, max)
    critical_threshold: float


@dataclass
class EquipmentConfig:
    """Configuration for equipment type."""
    name: str
    steel_equivalent: str
    common_faults: List[str]
    sensors: Dict[str, SensorConfig]


# ============================================================================
# SENSOR CONFIGURATIONS
# ============================================================================

SENSOR_CONFIGS = {
    # Temperature sensors (°C)
    'temperature': SensorConfig(
        name='Discharge Temperature',
        steel_equivalent='Compressor Discharge Temperature',
        unit='°C',
        baseline_value=85.0,
        normal_range=(75.0, 95.0),
        critical_threshold=100.0
    ),
    
    # Pressure sensors (bar)
    'pressure': SensorConfig(
        name='Discharge Pressure',
        steel_equivalent='System Pressure',
        unit='bar',
        baseline_value=8.5,
        normal_range=(7.5, 9.5),
        critical_threshold=10.0
    ),
    
    # Speed sensors (RPM)
    'speed': SensorConfig(
        name='Compressor Speed',
        steel_equivalent='Motor RPM',
        unit='RPM',
        baseline_value=3500,
        normal_range=(3200, 3800),
        critical_threshold=4000
    ),
    
    # Vibration sensors (Hz)
    'vibration': SensorConfig(
        name='Vibration Level',
        steel_equivalent='Bearing Vibration',
        unit='Hz',
        baseline_value=80.0,
        normal_range=(75.0, 100.0),
        critical_threshold=120.0
    ),
    
    # Efficiency (%)
    'efficiency': SensorConfig(
        name='Operating Efficiency',
        steel_equivalent='System Efficiency',
        unit='%',
        baseline_value=100.0,
        normal_range=(95.0, 100.0),
        critical_threshold=90.0
    )
}


# ============================================================================
# EQUIPMENT CONFIGURATIONS
# ============================================================================

EQUIPMENT_CONFIGS = {
    'HPC_degradation': EquipmentConfig(
        name='High Pressure Compressor',
        steel_equivalent='Air Compressor Unit',
        common_faults=[
            'Blade fouling',
            'Seal wear',
            'Efficiency degradation',
            'Internal leakage'
        ],
        sensors={
            'temperature': SENSOR_CONFIGS['temperature'],
            'pressure': SENSOR_CONFIGS['pressure'],
            'speed': SENSOR_CONFIGS['speed'],
            'vibration': SENSOR_CONFIGS['vibration'],
            'efficiency': SENSOR_CONFIGS['efficiency']
        }
    ),
    
    'Fan_degradation': EquipmentConfig(
        name='Fan Module',
        steel_equivalent='Cooling Fan System',
        common_faults=[
            'Blade damage',
            'Bearing wear',
            'Imbalance',
            'Shaft misalignment'
        ],
        sensors={
            'temperature': SENSOR_CONFIGS['temperature'],
            'speed': SENSOR_CONFIGS['speed'],
            'vibration': SENSOR_CONFIGS['vibration'],
            'efficiency': SENSOR_CONFIGS['efficiency']
        }
    )
}


# ============================================================================
# CMAPSS SENSOR MAPPING
# ============================================================================

class CMAPSSSensorMapping:
    """
    Mapping CMAPSS normalized sensor values to physical values.
    Based on statistical analysis of CMAPSS datasets.
    """
    
    # Sensor statistics from CMAPSS data analysis
    SENSOR_STATS = {
        'sensor9': {'mean': 21.61, 'std': 0.001, 'physical_range': (75, 95)},  # Temperature
        'sensor11': {'mean': 47.5, 'std': 0.2, 'physical_range': (3200, 3800)},  # Speed
        'sensor12': {'mean': 521.0, 'std': 2.0, 'physical_range': (3200, 3800)},  # Speed
        'sensor13': {'mean': 2388.0, 'std': 5.0, 'physical_range': (7.5, 9.5)},  # Pressure
        'sensor15': {'mean': 8.4, 'std': 0.05, 'physical_range': (95, 100)},  # Efficiency related
    }
    
    @staticmethod
    def normalize_to_physical(sensor_name: str, normalized_value: float, target_config: SensorConfig) -> float:
        """
        Convert CMAPSS normalized sensor value to physical engineering units.
        
        Args:
            sensor_name: CMAPSS sensor identifier (e.g., 'sensor9')
            normalized_value: Normalized sensor reading from CMAPSS
            target_config: Target sensor configuration with desired range
        
        Returns:
            Physical value in engineering units
        """
        if sensor_name not in CMAPSSSensorMapping.SENSOR_STATS:
            # Fallback: return baseline
            return target_config.baseline_value
        
        stats = CMAPSSSensorMapping.SENSOR_STATS[sensor_name]
        mean = stats['mean']
        std_dev = stats['std']
        
        # Z-score normalization
        if std_dev > 0:
            z_score = (normalized_value - mean) / std_dev
        else:
            z_score = 0
        
        # Map to target physical range
        target_min, target_max = target_config.normal_range
        target_range = target_max - target_min
        
        # Linear mapping with z-score influence
        physical_value = target_config.baseline_value + (z_score * target_range * 0.1)
        
        # Clip to reasonable bounds
        physical_value = max(target_min, min(target_max * 1.1, physical_value))
        
        return round(physical_value, 2)


# ============================================================================
# SEVERITY THRESHOLDS
# ============================================================================

SEVERITY_THRESHOLDS = {
    'RUL_BASED': {
        'CRITICAL': 5,   # cycles
        'HIGH': 15,
        'MEDIUM': 30,
        'LOW': float('inf')
    },
    
    'SENSOR_BASED': {
        'temperature_delta': {
            'CRITICAL': 20.0,  # °C above baseline
            'HIGH': 15.0,
            'MEDIUM': 10.0,
            'LOW': 5.0
        },
        'vibration_delta': {
            'CRITICAL': 40.0,  # Hz above baseline
            'HIGH': 30.0,
            'MEDIUM': 20.0,
            'LOW': 10.0
        },
        'efficiency_drop': {
            'CRITICAL': 10.0,  # % below baseline
            'HIGH': 5.0,
            'MEDIUM': 3.0,
            'LOW': 1.0
        }
    }
}


# ============================================================================
# PROCESSING PARAMETERS
# ============================================================================

PROCESSING_PARAMS = {
    'degradation_window_percentage': 0.3,  # Use last 30% of lifecycle
    'samples_per_engine': 2,  # Sample 2 points per engine
    'min_cycles_per_window': 5,  # Minimum cycles in degradation window
    
    'outlier_std_threshold': 3.0,  # Standard deviations for outlier detection
    
    'confidence_range': (0.75, 0.95),  # Random confidence range for outputs
    
    'cycle_to_hours_multiplier': 8,  # Convert cycles to operating hours
}


# ============================================================================
# MAINTENANCE RECOMMENDATIONS
# ============================================================================

MAINTENANCE_ACTIONS = {
    'HPC_degradation': {
        'CRITICAL': [
            "IMMEDIATE ACTION REQUIRED - Schedule shutdown within next shift",
            "Reduce compressor load to 70% rated capacity immediately",
            "Initiate emergency maintenance protocol"
        ],
        'HIGH': [
            "Reduce compressor load to 80% rated capacity to slow degradation",
            "Schedule compressor teardown within 48 hours"
        ],
        'MEDIUM': [
            "Plan maintenance within next scheduled shutdown",
            "Monitor efficiency trends daily"
        ],
        'LOW': [
            "Schedule inspection during next planned maintenance window",
            "Continue normal monitoring"
        ],
        'COMMON': [
            "Prepare replacement components: blade set, seal assembly",
            "Perform borescope inspection to assess internal condition",
            "Check air filtration system for contamination source",
            "Review operating parameters and loading history"
        ]
    },
    
    'Fan_degradation': {
        'CRITICAL': [
            "IMMEDIATE ACTION REQUIRED - Risk of catastrophic failure",
            "Reduce fan speed by 30% immediately",
            "Prepare for emergency equipment swap"
        ],
        'HIGH': [
            "Reduce fan speed by 20% to minimize bearing stress",
            "Schedule vibration analysis within 24 hours"
        ],
        'MEDIUM': [
            "Monitor vibration levels every shift",
            "Plan bearing replacement during next shutdown"
        ],
        'LOW': [
            "Include in routine maintenance inspection",
            "Trend vibration data for early warning"
        ],
        'COMMON': [
            "Prepare replacement bearings and balance equipment",
            "Lubrication system inspection and oil sample analysis",
            "Check for shaft misalignment or coupling issues",
            "Verify fan blade integrity with visual inspection"
        ]
    }
}


LONG_TERM_RECOMMENDATIONS = {
    'HPC_degradation': [
        "Upgrade air filtration to higher efficiency class",
        "Implement online efficiency monitoring system",
        "Reduce maintenance interval by 25% for this equipment class",
        "Consider compressor blade coating upgrade for fouling resistance",
        "Install differential pressure monitoring across stages"
    ],
    
    'Fan_degradation': [
        "Install continuous vibration monitoring system",
        "Switch to synthetic lubricant for extended bearing life",
        "Implement predictive maintenance program with oil analysis",
        "Review operating conditions to reduce bearing load",
        "Consider fan upgrade to modern high-efficiency design"
    ]
}


# ============================================================================
# DOWNTIME ESTIMATES
# ============================================================================

DOWNTIME_ESTIMATES = {
    'CRITICAL': {'min': 12, 'max': 16, 'unit': 'hours'},
    'HIGH': {'min': 8, 'max': 12, 'unit': 'hours'},
    'MEDIUM': {'min': 6, 'max': 8, 'unit': 'hours'},
    'LOW': {'min': 4, 'max': 6, 'unit': 'hours'}
}


# ============================================================================
# DATASET INFORMATION
# ============================================================================

CMAPSS_DATASETS = {
    'train_FD001.txt': {
        'operating_conditions': 1,
        'fault_modes': ['HPC_degradation'],
        'complexity': 'simple',
        'description': 'Single operating condition, HPC degradation only'
    },
    'train_FD002.txt': {
        'operating_conditions': 6,
        'fault_modes': ['HPC_degradation'],
        'complexity': 'medium',
        'description': 'Multiple operating conditions, HPC degradation'
    },
    'train_FD003.txt': {
        'operating_conditions': 1,
        'fault_modes': ['HPC_degradation', 'Fan_degradation'],
        'complexity': 'medium',
        'description': 'Single condition, multiple fault modes'
    },
    'train_FD004.txt': {
        'operating_conditions': 6,
        'fault_modes': ['HPC_degradation', 'Fan_degradation'],
        'complexity': 'complex',
        'description': 'Multiple conditions and fault modes'
    }
}


# ============================================================================
# ROOT CAUSE ANALYSIS TEMPLATES
# ============================================================================

ROOT_CAUSE_TEMPLATES = {
    'HPC_degradation': {
        'primary_cause': 'Compressor blade surface fouling from airborne contaminants reducing aerodynamic efficiency',
        'secondary_cause': 'Internal seal wear allowing pressure stage bypass, reducing compression ratio',
        'efficiency_indicator': 'efficiency',
        'context': 'Progressive degradation after {hours:,} operating hours'
    },
    
    'Fan_degradation': {
        'primary_cause': 'Bearing race spalling due to extended operation under high-load conditions',
        'secondary_cause': 'Insufficient lubrication or contaminated lubricant',
        'vibration_indicator': 'vibration_level',
        'context': 'Mechanical degradation after {hours:,} operating hours'
    }
}


# ============================================================================
# VALIDATION RULES
# ============================================================================

VALIDATION_RULES = {
    'min_sample_length': 10,  # Minimum characters for instruction/input/output
    'max_sample_length': 5000,  # Maximum characters
    'required_fields': ['instruction', 'input', 'output', 'metadata'],
    'metadata_required_fields': ['source', 'fault_mode', 'severity', 'equipment']
}


def get_sensor_config(sensor_type: str) -> SensorConfig:
    """Get sensor configuration by type."""
    return SENSOR_CONFIGS.get(sensor_type)


def get_equipment_config(fault_mode: str) -> EquipmentConfig:
    """Get equipment configuration by fault mode."""
    return EQUIPMENT_CONFIGS.get(fault_mode)


def get_severity_threshold(metric_type: str = 'RUL_BASED') -> Dict:
    """Get severity thresholds."""
    return SEVERITY_THRESHOLDS.get(metric_type, {})


def get_processing_param(param_name: str):
    """Get processing parameter value."""
    return PROCESSING_PARAMS.get(param_name)


def get_root_cause_template(fault_mode: str) -> Dict:
    """Get root cause analysis template."""
    return ROOT_CAUSE_TEMPLATES.get(fault_mode, {})
