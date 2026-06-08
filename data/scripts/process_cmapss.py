"""
NASA CMAPSS (Turbofan Engine) Dataset Processor
Converts turbofan degradation data to steel plant equipment maintenance format.

Input: train_FD001.txt - train_FD004.txt (708 engines)
Output: Structured training samples with degradation patterns
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from config import (
    get_equipment_config,
    get_sensor_config,
    get_severity_threshold,
    get_processing_param,
    get_root_cause_template,
    CMAPSSSensorMapping,
    CMAPSS_DATASETS,
    MAINTENANCE_ACTIONS,
    LONG_TERM_RECOMMENDATIONS,
    DOWNTIME_ESTIMATES
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


class CMAPSSProcessor:
    """Production-grade processor for CMAPSS turbofan dataset."""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'engines_processed': 0,
            'samples_generated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # Column names for CMAPSS data (26 columns total)
        self.column_names = ['unit', 'cycle'] + \
                           [f'setting{i}' for i in range(1, 4)] + \
                           [f'sensor{i}' for i in range(1, 22)]
        
        # Load processing parameters from config
        self.degradation_window = get_processing_param('degradation_window_percentage')
        self.samples_per_engine = get_processing_param('samples_per_engine')
        self.min_cycles = get_processing_param('min_cycles_per_window')
        self.cycle_multiplier = get_processing_param('cycle_to_hours_multiplier')
        self.confidence_range = get_processing_param('confidence_range')
    
    def load_dataset(self, filename: str) -> Tuple[pd.DataFrame, Dict]:
        """Load CMAPSS dataset and RUL labels."""
        train_file = self.input_dir / filename
        
        logger.info(f"Loading {filename}")
        
        try:
            # Load training data
            df = pd.read_csv(train_file, sep=r'\s+', header=None, names=self.column_names)
            
            # Determine fault mode from filename
            dataset_info = self._get_dataset_info(filename)
            
            logger.info(f"Loaded {df['unit'].nunique()} engines from {filename}")
            return df, dataset_info
            
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            raise
    
    def _get_dataset_info(self, filename: str) -> Dict:
        """Get dataset characteristics from config."""
        return CMAPSS_DATASETS.get(filename, {
            'operating_conditions': 1,
            'fault_modes': ['HPC_degradation'],
            'complexity': 'simple'
        })
    
    def extract_degradation_windows(self, df: pd.DataFrame, window_percentage: float = None) -> pd.DataFrame:
        """Extract last X% of engine life showing degradation."""
        if window_percentage is None:
            window_percentage = self.degradation_window
            
        degradation_data = []
        
        for unit_id in df['unit'].unique():
            unit_data = df[df['unit'] == unit_id].copy()
            total_cycles = len(unit_data)
            
            # Take last X% of lifecycle (degradation period)
            window_size = max(int(total_cycles * window_percentage), self.min_cycles)
            degradation_window = unit_data.tail(window_size)
            
            # Calculate RUL (Remaining Useful Life)
            degradation_window['RUL'] = total_cycles - degradation_window['cycle']
            
            degradation_data.append(degradation_window)
        
        return pd.concat(degradation_data, ignore_index=True)
    
    def calculate_health_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate health degradation indicators."""
        # Select key sensors from CMAPSS mapping instead of hardcoding
        key_sensors = list(CMAPSSSensorMapping.SENSOR_STATS.keys())
        
        # Add commonly used CMAPSS sensors not in mapping
        additional_sensors = ['sensor2', 'sensor3', 'sensor4', 'sensor7', 'sensor17', 'sensor20', 'sensor21']
        key_sensors.extend(additional_sensors)
        
        # Filter to sensors that actually exist in dataframe
        key_sensors = [s for s in key_sensors if s in df.columns]
        
        for unit_id in df['unit'].unique():
            mask = df['unit'] == unit_id
            unit_data = df[mask]
            
            # Calculate baseline (first 10% of life)
            baseline_size = max(int(len(unit_data) * 0.1), 3)
            baseline = unit_data[key_sensors].head(baseline_size).mean()
            
            # Calculate degradation (% change from baseline)
            for sensor in key_sensors:
                df.loc[mask, f'{sensor}_degradation'] = \
                    ((df.loc[mask, sensor] - baseline[sensor]) / baseline[sensor] * 100)
        
        return df
    
    def determine_severity_from_rul(self, rul: int) -> str:
        """Determine severity based on Remaining Useful Life using config thresholds."""
        thresholds = get_severity_threshold('RUL_BASED')
        
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM']:
            if rul <= thresholds[severity]:
                return severity
        return 'LOW'
    
    def map_to_steel_equipment(self, row: pd.Series, fault_mode: str, dataset_info: Dict) -> Dict:
        """Map turbofan sensors to steel plant equipment sensors using config."""
        equipment_config = get_equipment_config(fault_mode)
        
        # Get sensor configs
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        speed_config = get_sensor_config('speed')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        # Map normalized CMAPSS values to physical values
        mapped_data = {
            'equipment': equipment_config.steel_equivalent,
            'equipment_id': f"{equipment_config.steel_equivalent.replace(' ', '-')}-{int(row['unit']):03d}",
            'sensors': {
                'discharge_temperature': CMAPSSSensorMapping.normalize_to_physical(
                    'sensor9', row['sensor9'], temp_config
                ),
                'discharge_pressure': CMAPSSSensorMapping.normalize_to_physical(
                    'sensor13', row['sensor13'], pressure_config
                ),
                'compressor_rpm': int(CMAPSSSensorMapping.normalize_to_physical(
                    'sensor12', row['sensor12'], speed_config
                )),
                'vibration_level': CMAPSSSensorMapping.normalize_to_physical(
                    'sensor11', row.get('sensor11', vibration_config.baseline_value), vibration_config
                ),
                'efficiency': CMAPSSSensorMapping.normalize_to_physical(
                    'sensor15', row.get('sensor15', efficiency_config.baseline_value), efficiency_config
                )
            },
            'operating_hours': int(row['cycle'] * self.cycle_multiplier),
            'rul_hours': int(row['RUL'] * self.cycle_multiplier)
        }
        
        return mapped_data
    
    def generate_diagnosis(self, mapped_data: Dict, fault_mode: str, severity: str) -> str:
        """Generate diagnosis based on fault mode and sensor data using config."""
        equipment_config = get_equipment_config(fault_mode)
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        efficiency_config = get_sensor_config('efficiency')
        vibration_config = get_sensor_config('vibration')
        
        sensors = mapped_data['sensors']
        
        if fault_mode == 'HPC_degradation':
            diagnosis = f"{equipment_config.steel_equivalent} showing progressive efficiency degradation. "
            diagnosis += f"Discharge temperature elevated to {sensors['discharge_temperature']}°C "
            diagnosis += f"(baseline: {temp_config.baseline_value}°C), "
            diagnosis += f"discharge pressure at {sensors['discharge_pressure']} bar "
            diagnosis += f"(baseline: {pressure_config.baseline_value} bar). "
            diagnosis += f"Efficiency at {sensors['efficiency']}% "
            diagnosis += f"(baseline: {efficiency_config.baseline_value}%). "
            diagnosis += "Consistent with compressor blade fouling and internal seal wear."
        else:  # Fan_degradation
            diagnosis = f"{equipment_config.steel_equivalent} exhibiting performance degradation. "
            diagnosis += f"Vibration increased to {sensors['vibration_level']} Hz "
            diagnosis += f"(baseline: {vibration_config.baseline_value} Hz), "
            diagnosis += f"fan speed at {sensors['compressor_rpm']} RPM showing load irregularities. "
            diagnosis += "Pattern indicates bearing wear or blade damage."
        
        return diagnosis
    
    def generate_root_cause(self, mapped_data: Dict, fault_mode: str) -> str:
        """Generate root cause analysis from config template."""
        sensors = mapped_data['sensors']
        hours = mapped_data['operating_hours']
        
        # Get template from config
        template = get_root_cause_template(fault_mode)
        
        if not template:
            return f"Root cause analysis not available for {fault_mode}."
        
        # Build root cause from template
        root_cause = template['context'].format(hours=hours) + " "
        root_cause += f"Primary cause: {template['primary_cause']}. "
        root_cause += f"Secondary cause: {template['secondary_cause']}. "
        
        # Add specific metric indicator
        if fault_mode == 'HPC_degradation':
            indicator = template.get('efficiency_indicator', 'efficiency')
            root_cause += f"Current {indicator} at {sensors.get(indicator, 'N/A')}% indicates advanced wear state."
        else:  # Fan_degradation
            indicator = template.get('vibration_indicator', 'vibration_level')
            root_cause += f"Vibration signature at {sensors.get(indicator, 'N/A')} Hz indicates bearing wear or shaft imbalance."
        
        return root_cause
    
    def generate_actions(self, fault_mode: str, severity: str, rul_hours: int) -> List[str]:
        """Generate immediate action recommendations from config."""
        actions = []
        
        # Get severity-specific actions
        severity_actions = MAINTENANCE_ACTIONS[fault_mode].get(severity, [])
        
        # Add RUL information to first action if CRITICAL or HIGH
        if severity in ['CRITICAL', 'HIGH'] and severity_actions:
            first_action = severity_actions[0].replace(
                'next shift', 
                f'next shift (~{rul_hours} hours remaining)'
            ).replace(
                '48 hours',
                f'{rul_hours} operating hours'
            )
            actions.append(first_action)
            actions.extend(severity_actions[1:])
        else:
            actions.extend(severity_actions)
        
        # Add common actions
        common_actions = MAINTENANCE_ACTIONS[fault_mode].get('COMMON', [])
        actions.extend(common_actions)
        
        return actions[:6]  # Return top 6 actions
    
    def generate_long_term_recommendations(self, fault_mode: str) -> List[str]:
        """Generate long-term recommendations from config."""
        return LONG_TERM_RECOMMENDATIONS.get(fault_mode, [])
    
    def create_training_sample(self, row: pd.Series, fault_mode: str, dataset_info: Dict, sample_idx: int) -> TrainingSample:
        """Create a structured training sample."""
        # Map to steel equipment
        mapped_data = self.map_to_steel_equipment(row, fault_mode, dataset_info)
        equipment_config = get_equipment_config(fault_mode)
        
        # Determine severity
        severity = self.determine_severity_from_rul(int(row['RUL']))
        
        # Generate components
        diagnosis = self.generate_diagnosis(mapped_data, fault_mode, severity)
        root_cause = self.generate_root_cause(mapped_data, fault_mode)
        actions = self.generate_actions(fault_mode, severity, mapped_data['rul_hours'])
        long_term = self.generate_long_term_recommendations(fault_mode)
        
        # Get sensor configs for baselines
        temp_config = get_sensor_config('temperature')
        pressure_config = get_sensor_config('pressure')
        speed_config = get_sensor_config('speed')
        vibration_config = get_sensor_config('vibration')
        efficiency_config = get_sensor_config('efficiency')
        
        # Instruction
        instruction = f"Analyze equipment degradation pattern and predict maintenance requirements for {mapped_data['equipment']}."
        
        # Input
        sensors = mapped_data['sensors']
        input_data = f"""Equipment: {mapped_data['equipment']} | ID: {mapped_data['equipment_id']}
Operating Hours: {mapped_data['operating_hours']:,} hours

Current Sensor Readings:
- Discharge Temperature: {sensors['discharge_temperature']}°C (baseline: {temp_config.baseline_value}°C, delta: +{sensors['discharge_temperature']-temp_config.baseline_value:.1f}°C)
- Discharge Pressure: {sensors['discharge_pressure']} bar (baseline: {pressure_config.baseline_value} bar)
- Compressor Speed: {sensors['compressor_rpm']} RPM (rated: {speed_config.baseline_value} RPM)
- Vibration Level: {sensors['vibration_level']} Hz (baseline: {vibration_config.baseline_value} Hz)
- Operating Efficiency: {sensors['efficiency']}% (baseline: {efficiency_config.baseline_value}%)

Trend: Progressive degradation over past 30 days
Alert: Predictive maintenance recommended"""
        
        # Output
        confidence = np.random.uniform(*self.confidence_range)
        downtime_est = DOWNTIME_ESTIMATES[severity]
        
        output = f"""DIAGNOSIS: {diagnosis}

ROOT CAUSE: {root_cause}

RISK LEVEL: {severity}

REMAINING USEFUL LIFE (RUL): Approximately {mapped_data['rul_hours']} operating hours

CONFIDENCE: {confidence:.2f}

IMMEDIATE ACTIONS:
{chr(10).join(f'{i+1}. {action}' for i, action in enumerate(actions))}

LONG-TERM RECOMMENDATIONS:
{chr(10).join(f'- {rec}' for rec in long_term)}

ESTIMATED DOWNTIME: {downtime_est['min']}-{downtime_est['max']} {downtime_est['unit']}

SPARE PARTS REQUIRED: Compressor overhaul kit, seal assembly, bearing set

MANUAL REFERENCE: {mapped_data['equipment']} Maintenance Manual Section {np.random.randint(3, 8)}.{np.random.randint(1, 9)}"""
        
        # Metadata
        metadata = {
            'source': 'CMAPSS',
            'dataset': dataset_info.get('complexity', 'unknown'),
            'fault_mode': fault_mode,
            'severity': severity,
            'equipment': mapped_data['equipment'],
            'rul_cycles': int(row['RUL']),
            'rul_hours': mapped_data['rul_hours'],
            'cycle': int(row['cycle']),
            'unit_id': int(row['unit']),
            'sample_id': sample_idx,
            'timestamp': datetime.now().isoformat()
        }
        
        return TrainingSample(
            instruction=instruction,
            input=input_data,
            output=output,
            metadata=metadata
        )
    
    def process_dataset(self, filename: str) -> List[TrainingSample]:
        """Process a single CMAPSS dataset file."""
        samples = []
        
        try:
            # Load data
            df, dataset_info = self.load_dataset(filename)
            
            # Extract degradation windows
            degradation_df = self.extract_degradation_windows(df, window_percentage=0.3)
            
            # Calculate health indicators
            degradation_df = self.calculate_health_indicators(degradation_df)
            
            # Sample data (don't use every cycle, sample strategically)
            sampled_df = self._strategic_sampling(degradation_df)
            
            logger.info(f"Sampled {len(sampled_df)} records from {filename}")
            
            # Generate training samples
            for idx, row in sampled_df.iterrows():
                try:
                    # Pick fault mode
                    fault_mode = np.random.choice(dataset_info['fault_modes'])
                    
                    sample = self.create_training_sample(row, fault_mode, dataset_info, len(samples))
                    samples.append(sample)
                    self.stats['samples_generated'] += 1
                    
                except Exception as e:
                    logger.warning(f"Error creating sample from row {idx}: {e}")
                    self.stats['errors'] += 1
            
            self.stats['engines_processed'] += df['unit'].nunique()
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            self.stats['errors'] += 1
        
        return samples
    
    def _strategic_sampling(self, df: pd.DataFrame, samples_per_engine: int = None) -> pd.DataFrame:
        """Sample strategically from degradation data."""
        if samples_per_engine is None:
            samples_per_engine = self.samples_per_engine
            
        sampled = []
        rul_threshold = get_severity_threshold('RUL_BASED')['MEDIUM']
        
        for unit_id in df['unit'].unique():
            unit_data = df[df['unit'] == unit_id]
            
            if len(unit_data) < 2:
                sampled.append(unit_data)
                continue
            
            # Take samples from different degradation stages
            # Early degradation (RUL > threshold)
            early = unit_data[unit_data['RUL'] > rul_threshold]
            if len(early) > 0:
                sampled.append(early.sample(n=min(1, len(early))))
            
            # Late degradation (RUL <= threshold)
            late = unit_data[unit_data['RUL'] <= rul_threshold]
            if len(late) > 0:
                sampled.append(late.sample(n=min(1, len(late))))
        
        return pd.concat(sampled, ignore_index=True) if sampled else pd.DataFrame()
    
    def process_all(self) -> List[TrainingSample]:
        """Process all CMAPSS datasets from config."""
        logger.info("Starting CMAPSS processing pipeline...")
        
        all_samples = []
        
        # Load datasets from config instead of hardcoding
        for dataset in CMAPSS_DATASETS.keys():
            dataset_path = self.input_dir / dataset
            if dataset_path.exists():
                logger.info(f"\nProcessing {dataset}...")
                samples = self.process_dataset(dataset)
                all_samples.extend(samples)
                logger.info(f"Generated {len(samples)} samples from {dataset}")
            else:
                logger.warning(f"Dataset not found: {dataset}")
        
        return all_samples
    
    def save_samples(self, samples: List[TrainingSample], output_file: str = "cmapss_samples.jsonl"):
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
        """Print processing statistics."""
        logger.info("\n" + "="*60)
        logger.info("CMAPSS PROCESSING STATISTICS")
        logger.info("="*60)
        for key, value in self.stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")
        logger.info("="*60)


def main():
    """Main execution function."""
    # Paths
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / "raw" / "kaggle" / "CMaps"
    output_dir = base_dir / "processed"
    
    # Process
    processor = CMAPSSProcessor(str(input_dir), str(output_dir))
    samples = processor.process_all()
    processor.save_samples(samples)
    processor.print_stats()
    
    # Show sample output
    if samples:
        logger.info("\n" + "="*60)
        logger.info("SAMPLE OUTPUT (First Training Example)")
        logger.info("="*60)
        sample = samples[0]
        print(f"\nINSTRUCTION:\n{sample.instruction}\n")
        print(f"INPUT:\n{sample.input}\n")
        print(f"OUTPUT:\n{sample.output}\n")
        print(f"METADATA:\n{json.dumps(sample.metadata, indent=2)}")


if __name__ == "__main__":
    main()
