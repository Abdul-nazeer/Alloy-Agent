"""
Real-time Sensor Simulator - Generates live sensor readings with anomaly injection
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, Optional
import numpy as np

class SensorSimulator:
    """Simulates real-time sensor readings with configurable anomaly injection"""
    
    def __init__(self):
        self.equipment_configs = {
            "AC-001": {
                "type": "Air Compressor",
                "status": "CRITICAL",
                "base_values": {"temperature_c": 110, "pressure_bar": 2.0, "vibration_mm_s": 3.5, "current_a": 55, "rpm": 1450},
                "anomaly_prob": 0.3,  # 30% chance of anomaly
            },
            "AC-002": {
                "type": "Air Compressor", 
                "status": "HIGH",
                "base_values": {"temperature_c": 85, "pressure_bar": 5.5, "vibration_mm_s": 2.3, "current_a": 44, "rpm": 1470},
                "anomaly_prob": 0.15,
            },
            "CF-003": {
                "type": "Cooling Fan System",
                "status": "MEDIUM",
                "base_values": {"temperature_c": 58, "pressure_bar": 0, "vibration_mm_s": 1.6, "current_a": 13, "rpm": 1455},
                "anomaly_prob": 0.08,
            },
            "RM-005": {
                "type": "Rolling Mill",
                "status": "LOW",
                "base_values": {"temperature_c": 92, "pressure_bar": 178, "vibration_mm_s": 3.6, "current_a": 202, "rpm": 0},
                "anomaly_prob": 0.05,
            },
            "CM-007": {
                "type": "Conveyor Motor",
                "status": "NORMAL",
                "base_values": {"temperature_c": 66, "pressure_bar": 0, "vibration_mm_s": 1.9, "current_a": 26, "rpm": 1462},
                "anomaly_prob": 0.02,
            },
        }
        
        self.thresholds = {
            "Air Compressor": {
                "temperature_c": {"min": 60, "max": 105, "critical": 115},
                "pressure_bar": {"min": 4.0, "max": 8.0, "critical": 2.0},
                "vibration_mm_s": {"min": 0.5, "max": 3.0, "critical": 4.0},
                "current_a": {"min": 35, "max": 50, "critical": 60},
            },
            "Cooling Fan System": {
                "temperature_c": {"min": 40, "max": 70, "critical": 85},
                "vibration_mm_s": {"min": 0.5, "max": 2.0, "critical": 3.0},
                "current_a": {"min": 8, "max": 18, "critical": 25},
            },
            "Rolling Mill": {
                "temperature_c": {"min": 70, "max": 110, "critical": 130},
                "pressure_bar": {"min": 150, "max": 200, "critical": 220},
                "vibration_mm_s": {"min": 2.0, "max": 4.5, "critical": 6.0},
            },
            "Conveyor Motor": {
                "temperature_c": {"min": 50, "max": 80, "critical": 95},
                "vibration_mm_s": {"min": 0.5, "max": 2.5, "critical": 3.5},
                "current_a": {"min": 20, "max": 32, "critical": 40},
            },
        }
    
    def generate_reading(self, equipment_id: str) -> Dict:
        """Generate a single sensor reading with optional anomaly"""
        config = self.equipment_configs.get(equipment_id)
        if not config:
            raise ValueError(f"Unknown equipment: {equipment_id}")
        
        base = config["base_values"]
        inject_anomaly = random.random() < config["anomaly_prob"]
        
        reading = {
            "equipment_id": equipment_id,
            "equipment_type": config["type"],
            "timestamp": datetime.now().isoformat(),
        }
        
        for sensor, base_value in base.items():
            if inject_anomaly and random.random() < 0.5:  # 50% chance this sensor is anomalous
                # Inject anomaly
                if config["status"] == "CRITICAL":
                    deviation = random.uniform(0.15, 0.30)  # 15-30% deviation
                else:
                    deviation = random.uniform(0.10, 0.20)
                
                anomaly_value = base_value * (1 + random.choice([-1, 1]) * deviation)
                reading[sensor] = round(max(0, anomaly_value), 2)
            else:
                # Normal variation (±5%)
                noise = random.uniform(-0.05, 0.05)
                reading[sensor] = round(max(0, base_value * (1 + noise)), 2)
        
        # Detect anomalies
        reading["anomalies"] = self.detect_anomalies(equipment_id, reading)
        reading["has_anomaly"] = len(reading["anomalies"]) > 0
        
        return reading
    
    def detect_anomalies(self, equipment_id: str, reading: Dict) -> list:
        """Detect threshold violations"""
        config = self.equipment_configs[equipment_id]
        equipment_type = config["type"]
        thresholds = self.thresholds.get(equipment_type, {})
        
        anomalies = []
        
        for sensor, limits in thresholds.items():
            if sensor in reading:
                value = reading[sensor]
                
                if "critical" in limits:
                    if sensor in ["pressure_bar"] and value < limits["critical"]:
                        anomalies.append({
                            "sensor": sensor,
                            "value": value,
                            "threshold": limits["critical"],
                            "severity": "CRITICAL",
                            "message": f"{sensor} critically low: {value} < {limits['critical']}"
                        })
                    elif value > limits.get("critical", float('inf')):
                        anomalies.append({
                            "sensor": sensor,
                            "value": value,
                            "threshold": limits["critical"],
                            "severity": "CRITICAL",
                            "message": f"{sensor} critically high: {value} > {limits['critical']}"
                        })
                
                if value > limits.get("max", float('inf')):
                    anomalies.append({
                        "sensor": sensor,
                        "value": value,
                        "threshold": limits["max"],
                        "severity": "HIGH",
                        "message": f"{sensor} above max: {value} > {limits['max']}"
                    })
                elif value < limits.get("min", 0):
                    anomalies.append({
                        "sensor": sensor,
                        "value": value,
                        "threshold": limits["min"],
                        "severity": "HIGH",
                        "message": f"{sensor} below min: {value} < {limits['min']}"
                    })
        
        return anomalies
    
    async def stream_readings(self, equipment_id: str, interval: float = 2.0):
        """Async generator for streaming sensor readings"""
        while True:
            reading = self.generate_reading(equipment_id)
            yield reading
            await asyncio.sleep(interval)
    
    def get_all_equipment_ids(self) -> list:
        """Get list of all equipment IDs"""
        return list(self.equipment_configs.keys())
    
    def get_latest_reading_with_anomaly(self, equipment_id: str) -> Optional[Dict]:
        """
        Get latest sensor reading and check for anomalies
        Used by autonomous monitoring loop
        """
        try:
            reading = self.generate_reading(equipment_id)
            return reading
        except Exception as e:
            return None


# Singleton instance
_simulator_instance = None

def get_sensor_simulator() -> SensorSimulator:
    """Get or create sensor simulator singleton"""
    global _simulator_instance
    if _simulator_instance is None:
        _simulator_instance = SensorSimulator()
    return _simulator_instance
