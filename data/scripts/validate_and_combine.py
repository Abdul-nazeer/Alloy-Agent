"""
Production-Grade Data Validation and Combination Pipeline
Validates, combines, and splits datasets for fine-tuning.
"""

import json
import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
from collections import Counter, defaultdict
from dataclasses import dataclass

from config import VALIDATION_RULES

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Validation report for a dataset."""
    total_samples: int
    valid_samples: int
    invalid_samples: int
    errors: List[Dict]
    warnings: List[Dict]
    statistics: Dict


class DataValidator:
    """Production-grade data validator and combiner."""
    
    def __init__(self, input_dir: str, output_dir: str):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.validation_rules = VALIDATION_RULES
        self.all_samples = []
        self.reports = {}
        
        self.stats = {
            'total_samples': 0,
            'valid_samples': 0,
            'invalid_samples': 0,
            'duplicates_removed': 0
        }
    
    def load_dataset(self, filename: str) -> Tuple[List[Dict], ValidationReport]:
        """Load and validate a single dataset file."""
        filepath = self.input_dir / filename
        
        if not filepath.exists():
            logger.error(f"File not found: {filepath}")
            return [], ValidationReport(0, 0, 0, [{'error': 'File not found'}], [], {})
        
        logger.info(f"Loading {filename}...")
        
        samples = []
        errors = []
        warnings = []
        line_num = 0
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line_num += 1
                    try:
                        sample = json.loads(line.strip())
                        
                        # Validate sample
                        is_valid, validation_errors, validation_warnings = self._validate_sample(sample, line_num)
                        
                        if is_valid:
                            samples.append(sample)
                        else:
                            errors.extend(validation_errors)
                        
                        warnings.extend(validation_warnings)
                        
                    except json.JSONDecodeError as e:
                        errors.append({
                            'line': line_num,
                            'error': f'JSON decode error: {str(e)}',
                            'severity': 'CRITICAL'
                        })
                    except Exception as e:
                        errors.append({
                            'line': line_num,
                            'error': f'Unexpected error: {str(e)}',
                            'severity': 'CRITICAL'
                        })
        
        except Exception as e:
            logger.error(f"Error reading {filename}: {e}")
            errors.append({'error': f'File read error: {str(e)}', 'severity': 'CRITICAL'})
        
        # Generate statistics
        stats = self._generate_statistics(samples, filename)
        
        report = ValidationReport(
            total_samples=line_num,
            valid_samples=len(samples),
            invalid_samples=line_num - len(samples),
            errors=errors,
            warnings=warnings,
            statistics=stats
        )
        
        logger.info(f"Loaded {len(samples)}/{line_num} valid samples from {filename}")
        
        return samples, report
    
    def _validate_sample(self, sample: Dict, line_num: int) -> Tuple[bool, List[Dict], List[Dict]]:
        """Validate a single sample against rules."""
        errors = []
        warnings = []
        is_valid = True
        
        # Check required fields
        for field in self.validation_rules['required_fields']:
            if field not in sample:
                errors.append({
                    'line': line_num,
                    'error': f'Missing required field: {field}',
                    'severity': 'CRITICAL'
                })
                is_valid = False
        
        if not is_valid:
            return False, errors, warnings
        
        # Check metadata required fields
        if 'metadata' in sample and isinstance(sample['metadata'], dict):
            for field in self.validation_rules['metadata_required_fields']:
                if field not in sample['metadata']:
                    errors.append({
                        'line': line_num,
                        'error': f'Missing metadata field: {field}',
                        'severity': 'HIGH'
                    })
                    is_valid = False
        
        # Check field lengths
        for field in ['instruction', 'input', 'output']:
            if field in sample and isinstance(sample[field], str):
                length = len(sample[field])
                
                if length < self.validation_rules['min_sample_length']:
                    errors.append({
                        'line': line_num,
                        'error': f'{field} too short: {length} chars (min: {self.validation_rules["min_sample_length"]})',
                        'severity': 'HIGH'
                    })
                    is_valid = False
                
                if length > self.validation_rules['max_sample_length']:
                    warnings.append({
                        'line': line_num,
                        'warning': f'{field} very long: {length} chars (max recommended: {self.validation_rules["max_sample_length"]})',
                        'severity': 'LOW'
                    })
        
        # Check for empty strings
        for field in ['instruction', 'input', 'output']:
            if field in sample and isinstance(sample[field], str):
                if not sample[field].strip():
                    errors.append({
                        'line': line_num,
                        'error': f'{field} is empty or whitespace only',
                        'severity': 'CRITICAL'
                    })
                    is_valid = False
        
        return is_valid, errors, warnings
    
    def _generate_statistics(self, samples: List[Dict], source: str) -> Dict:
        """Generate statistics for a dataset."""
        if not samples:
            return {}
        
        stats = {
            'total_samples': len(samples),
            'source': source,
            'sources': Counter(),
            'severities': Counter(),
            'equipment_types': Counter(),
            'fault_modes': Counter(),
            'rul_distribution': {
                '0-10h': 0,
                '10-50h': 0,
                '50-100h': 0,
                '100-200h': 0,
                '200-500h': 0,
                '500h+': 0
            },
            'avg_instruction_length': 0,
            'avg_input_length': 0,
            'avg_output_length': 0
        }
        
        instruction_lengths = []
        input_lengths = []
        output_lengths = []
        
        for sample in samples:
            metadata = sample.get('metadata', {})
            
            # Count sources
            source_val = metadata.get('source', 'UNKNOWN')
            stats['sources'][source_val] += 1
            
            # Count severities
            severity = metadata.get('severity', 'UNKNOWN')
            stats['severities'][severity] += 1
            
            # Count equipment types
            equipment = metadata.get('equipment', 'UNKNOWN')
            stats['equipment_types'][equipment] += 1
            
            # Count fault modes
            fault_mode = metadata.get('fault_mode', 'UNKNOWN')
            stats['fault_modes'][fault_mode] += 1
            
            # RUL distribution
            rul_hours = metadata.get('rul_hours', 0)
            if rul_hours <= 10:
                stats['rul_distribution']['0-10h'] += 1
            elif rul_hours <= 50:
                stats['rul_distribution']['10-50h'] += 1
            elif rul_hours <= 100:
                stats['rul_distribution']['50-100h'] += 1
            elif rul_hours <= 200:
                stats['rul_distribution']['100-200h'] += 1
            elif rul_hours <= 500:
                stats['rul_distribution']['200-500h'] += 1
            else:
                stats['rul_distribution']['500h+'] += 1
            
            # Lengths
            instruction_lengths.append(len(sample.get('instruction', '')))
            input_lengths.append(len(sample.get('input', '')))
            output_lengths.append(len(sample.get('output', '')))
        
        stats['avg_instruction_length'] = int(np.mean(instruction_lengths)) if instruction_lengths else 0
        stats['avg_input_length'] = int(np.mean(input_lengths)) if input_lengths else 0
        stats['avg_output_length'] = int(np.mean(output_lengths)) if output_lengths else 0
        
        return stats
    
    def remove_duplicates(self, samples: List[Dict]) -> Tuple[List[Dict], int]:
        """Remove duplicate samples based on input field."""
        logger.info("Checking for duplicate samples...")
        
        seen_inputs: Set[str] = set()
        unique_samples = []
        duplicates = 0
        
        for sample in samples:
            input_text = sample.get('input', '')
            
            # Create a hash of the input for comparison
            input_hash = hash(input_text)
            
            if input_hash not in seen_inputs:
                seen_inputs.add(input_hash)
                unique_samples.append(sample)
            else:
                duplicates += 1
        
        if duplicates > 0:
            logger.warning(f"Found and removed {duplicates} duplicate samples")
        else:
            logger.info("No duplicates found")
        
        self.stats['duplicates_removed'] = duplicates
        return unique_samples, duplicates
    
    def shuffle_samples(self, samples: List[Dict], seed: int = 42) -> List[Dict]:
        """Shuffle samples with fixed seed for reproducibility."""
        logger.info(f"Shuffling samples (seed={seed})...")
        np.random.seed(seed)
        indices = np.random.permutation(len(samples))
        return [samples[i] for i in indices]
    
    def split_train_val(self, samples: List[Dict], val_ratio: float = 0.1, seed: int = 42) -> Tuple[List[Dict], List[Dict]]:
        """Split samples into train and validation sets."""
        logger.info(f"Splitting into train/val (validation ratio: {val_ratio})...")
        
        # Shuffle first
        shuffled = self.shuffle_samples(samples, seed=seed)
        
        # Split
        val_size = int(len(shuffled) * val_ratio)
        train_size = len(shuffled) - val_size
        
        train_samples = shuffled[:train_size]
        val_samples = shuffled[train_size:]
        
        logger.info(f"Train: {len(train_samples)} samples, Validation: {len(val_samples)} samples")
        
        return train_samples, val_samples
    
    def save_dataset(self, samples: List[Dict], filename: str):
        """Save dataset to JSONL format."""
        output_path = self.output_dir / filename
        
        logger.info(f"Saving {len(samples)} samples to {filename}...")
        
        try:
            with open(output_path, 'w') as f:
                for sample in samples:
                    json.dump(sample, f)
                    f.write('\n')
            
            logger.info(f"Successfully saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
            raise
    
    def generate_report(self, output_file: str = "validation_report.txt"):
        """Generate comprehensive validation report."""
        report_path = self.output_dir / output_file
        
        logger.info(f"Generating validation report...")
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("DATA VALIDATION AND COMBINATION REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Overall statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Samples Processed: {self.stats['total_samples']}\n")
            f.write(f"Valid Samples: {self.stats['valid_samples']}\n")
            f.write(f"Invalid Samples: {self.stats['invalid_samples']}\n")
            f.write(f"Duplicates Removed: {self.stats['duplicates_removed']}\n")
            f.write(f"Success Rate: {(self.stats['valid_samples']/self.stats['total_samples']*100):.2f}%\n")
            f.write("\n")
            
            # Per-dataset reports
            for filename, report in self.reports.items():
                f.write("\n" + "="*80 + "\n")
                f.write(f"DATASET: {filename}\n")
                f.write("="*80 + "\n\n")
                
                f.write(f"Total Samples: {report.total_samples}\n")
                f.write(f"Valid Samples: {report.valid_samples}\n")
                f.write(f"Invalid Samples: {report.invalid_samples}\n")
                f.write(f"Success Rate: {(report.valid_samples/report.total_samples*100):.2f}%\n")
                f.write("\n")
                
                # Errors
                if report.errors:
                    f.write(f"ERRORS ({len(report.errors)}):\n")
                    f.write("-"*80 + "\n")
                    for i, error in enumerate(report.errors[:20], 1):  # Show first 20
                        f.write(f"{i}. Line {error.get('line', 'N/A')}: {error.get('error', 'Unknown error')}\n")
                    if len(report.errors) > 20:
                        f.write(f"... and {len(report.errors)-20} more errors\n")
                    f.write("\n")
                
                # Warnings
                if report.warnings:
                    f.write(f"WARNINGS ({len(report.warnings)}):\n")
                    f.write("-"*80 + "\n")
                    for i, warning in enumerate(report.warnings[:10], 1):  # Show first 10
                        f.write(f"{i}. Line {warning.get('line', 'N/A')}: {warning.get('warning', 'Unknown warning')}\n")
                    if len(report.warnings) > 10:
                        f.write(f"... and {len(report.warnings)-10} more warnings\n")
                    f.write("\n")
                
                # Statistics
                stats = report.statistics
                if stats:
                    f.write("STATISTICS:\n")
                    f.write("-"*80 + "\n")
                    
                    if 'sources' in stats:
                        f.write("\nSource Distribution:\n")
                        for source, count in stats['sources'].items():
                            f.write(f"  {source}: {count}\n")
                    
                    if 'severities' in stats:
                        f.write("\nSeverity Distribution:\n")
                        for severity, count in sorted(stats['severities'].items()):
                            f.write(f"  {severity}: {count}\n")
                    
                    if 'equipment_types' in stats:
                        f.write("\nEquipment Type Distribution:\n")
                        for equipment, count in stats['equipment_types'].most_common():
                            f.write(f"  {equipment}: {count}\n")
                    
                    if 'fault_modes' in stats:
                        f.write("\nFault Mode Distribution:\n")
                        for fault, count in stats['fault_modes'].items():
                            f.write(f"  {fault}: {count}\n")
                    
                    if 'rul_distribution' in stats:
                        f.write("\nRUL (Remaining Useful Life) Distribution:\n")
                        for range_name, count in stats['rul_distribution'].items():
                            f.write(f"  {range_name}: {count}\n")
                    
                    f.write("\nAverage Field Lengths:\n")
                    f.write(f"  Instruction: {stats.get('avg_instruction_length', 0)} chars\n")
                    f.write(f"  Input: {stats.get('avg_input_length', 0)} chars\n")
                    f.write(f"  Output: {stats.get('avg_output_length', 0)} chars\n")
                    f.write("\n")
        
        logger.info(f"Report saved to {report_path}")
        return report_path
    
    def process_all(self, val_ratio: float = 0.1, seed: int = 42):
        """Main processing pipeline."""
        logger.info("="*80)
        logger.info("STARTING DATA VALIDATION AND COMBINATION PIPELINE")
        logger.info("="*80)
        
        # Dataset files
        datasets = [
            'uci_samples.jsonl',
            'cmapss_samples.jsonl',
            'synthetic_samples.jsonl'
        ]
        
        # Load and validate all datasets
        all_samples = []
        
        for dataset in datasets:
            samples, report = self.load_dataset(dataset)
            self.reports[dataset] = report
            all_samples.extend(samples)
            
            self.stats['total_samples'] += report.total_samples
            self.stats['valid_samples'] += report.valid_samples
            self.stats['invalid_samples'] += report.invalid_samples
        
        logger.info(f"\nTotal samples loaded: {len(all_samples)}")
        
        # Remove duplicates
        all_samples, duplicates = self.remove_duplicates(all_samples)
        logger.info(f"Samples after deduplication: {len(all_samples)}")
        
        # Split into train/val
        train_samples, val_samples = self.split_train_val(all_samples, val_ratio=val_ratio, seed=seed)
        
        # Save combined dataset
        self.save_dataset(all_samples, 'combined_training_data.jsonl')
        
        # Save train/val splits
        self.save_dataset(train_samples, 'train.jsonl')
        self.save_dataset(val_samples, 'val.jsonl')
        
        # Generate combined statistics
        combined_stats = self._generate_statistics(all_samples, 'COMBINED')
        self.reports['COMBINED'] = ValidationReport(
            total_samples=len(all_samples),
            valid_samples=len(all_samples),
            invalid_samples=0,
            errors=[],
            warnings=[],
            statistics=combined_stats
        )
        
        # Generate report
        report_path = self.generate_report()
        
        # Print summary
        self.print_summary(train_samples, val_samples, report_path)
    
    def print_summary(self, train_samples: List[Dict], val_samples: List[Dict], report_path: Path):
        """Print final summary."""
        logger.info("\n" + "="*80)
        logger.info("VALIDATION AND COMBINATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Total Samples: {self.stats['total_samples']}")
        logger.info(f"Valid Samples: {self.stats['valid_samples']}")
        logger.info(f"Invalid Samples: {self.stats['invalid_samples']}")
        logger.info(f"Duplicates Removed: {self.stats['duplicates_removed']}")
        logger.info(f"Success Rate: {(self.stats['valid_samples']/self.stats['total_samples']*100):.2f}%")
        logger.info("-"*80)
        logger.info(f"Training Samples: {len(train_samples)}")
        logger.info(f"Validation Samples: {len(val_samples)}")
        logger.info("-"*80)
        logger.info(f"Detailed Report: {report_path}")
        logger.info("="*80)


def main():
    """Main execution function."""
    # Paths
    base_dir = Path(__file__).parent.parent
    input_dir = base_dir / "processed"
    output_dir = base_dir / "training"
    
    # Validate and combine
    validator = DataValidator(str(input_dir), str(output_dir))
    validator.process_all(val_ratio=0.1, seed=42)


if __name__ == "__main__":
    main()
