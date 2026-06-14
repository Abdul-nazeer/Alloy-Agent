"""
Machine Monitoring Service
Real-time sensor simulation with anomaly detection.
"""

import logging
import random
import time
from collections import deque
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Single sensor reading with timestamp."""
    timestamp: str
    temperature: float
    vibration: float
    current: float
    pressure: float
    rpm: int


@dataclass
class MachineConfig:
    """Machine configuration with thresholds."""
    machine_tag: str
    display_name: str
    nominal_rpm: int
    
    # Temperature thresholds (°C)
    temp_normal_max: float = 80.0
    temp_warning_max: float = 95.0
    temp_critical_max: float = 110.0
    
    # Vibration thresholds (mm/s)
    vib_normal_max: float = 1.5
    vib_warning_max: float = 2.5
    vib_critical_max: float = 4.0
    
    # Current thresholds (A)
    current_normal_max: float = 50.0
    current_warning_max: float = 70.0
    current_critical_max: float = 90.0
    
    # Pressure thresholds (bar)
    pressure_normal_min: float = 6.0
    pressure_warning_min: float = 5.0
    pressure_critical_min: float = 4.0


# 4 Configured Machines
MACHINES = {
    "rolling-mill-main-drive-motor": MachineConfig(
        machine_tag="rolling-mill-main-drive-motor",
        display_name="Rolling Mill Main Drive Motor",
        nominal_rpm=1480,
        temp_normal_max=85.0,
        vib_normal_max=1.8,
        current_normal_max=85.0,
        pressure_normal_min=7.0
    ),
    "general-plant-motor": MachineConfig(
        machine_tag="general-plant-motor",
        display_name="General Plant Motor",
        nominal_rpm=1450,
        temp_normal_max=80.0,
        vib_normal_max=1.5,
        current_normal_max=45.0,
        pressure_normal_min=6.5
    ),
    "industrial-induction-compressor-motor": MachineConfig(
        machine_tag="industrial-induction-compressor-motor",
        display_name="Industrial Induction / Compressor Motor",
        nominal_rpm=1475,
        temp_normal_max=90.0,
        vib_normal_max=2.0,
        current_normal_max=65.0,
        pressure_normal_min=8.0
    ),
    "blower-large-motor-reference": MachineConfig(
        machine_tag="blower-large-motor-reference",
        display_name="BF Blower / Large Motor",
        nominal_rpm=990,
        temp_normal_max=75.0,
        vib_normal_max=1.2,
        current_normal_max=55.0,
        pressure_normal_min=5.5
    )
}


class MachineMonitor:
    """
    Real-time machine monitoring with sensor simulation.
    
    Features:
    - Random walk sensor simulation
    - Anomaly injection
    - In-memory log buffer (last 50 readings per machine)
    - Threshold-based severity detection
    """
    
    def __init__(self, buffer_size: int = 50):
        self.buffer_size = buffer_size
        # In-memory buffers: machine_tag -> deque of readings
        self._logs: Dict[str, deque] = {
            tag: deque(maxlen=buffer_size) for tag in MACHINES.keys()
        }
        # Current sensor states for random walk
        self._states: Dict[str, Dict[str, float]] = {}
        
        # Initialize states at mid-range
        for tag, config in MACHINES.items():
            self._states[tag] = {
                "temperature": config.temp_normal_max * 0.7,
                "vibration": config.vib_normal_max * 0.5,
                "current": config.current_normal_max * 0.8,
                "pressure": config.pressure_normal_min * 1.2,
                "rpm": config.nominal_rpm
            }
    
    def get_machine_config(self, machine_tag: str) -> Optional[MachineConfig]:
        """Get machine configuration."""
        return MACHINES.get(machine_tag)
    
    def get_all_machines(self) -> List[Dict[str, Any]]:
        """Get list of all machines."""
        return [
            {
                "machine_tag": config.machine_tag,
                "display_name": config.display_name,
                "nominal_rpm": config.nominal_rpm
            }
            for config in MACHINES.values()
        ]
    
    def generate_reading(
        self,
        machine_tag: str,
        inject_anomaly: bool = False,
        anomaly_type: str = "vibration"
    ) -> SensorReading:
        """
        Generate next sensor reading using random walk.
        
        Args:
            machine_tag: Machine identifier
            inject_anomaly: If True, spike sensor to critical level
            anomaly_type: Which sensor to spike (temperature, vibration, current, pressure)
        """
        config = MACHINES.get(machine_tag)
        if not config:
            raise ValueError(f"Unknown machine: {machine_tag}")
        
        state = self._states[machine_tag]
        
        # Random walk parameters
        drift = 0.002  # Slow upward degradation
        noise_factor = 0.03  # ±3% random variation
        
        # Temperature
        temp_range = config.temp_normal_max - 60.0
        state["temperature"] += (temp_range * drift) + random.uniform(-temp_range * noise_factor, temp_range * noise_factor)
        state["temperature"] = max(60.0, min(state["temperature"], config.temp_critical_max * 1.1))
        
        # Vibration
        vib_range = config.vib_normal_max
        state["vibration"] += (vib_range * drift) + random.uniform(-vib_range * noise_factor, vib_range * noise_factor)
        state["vibration"] = max(0.1, min(state["vibration"], config.vib_critical_max * 1.3))
        
        # Current
        current_range = config.current_normal_max - 30.0
        state["current"] += (current_range * drift) + random.uniform(-current_range * noise_factor, current_range * noise_factor)
        state["current"] = max(30.0, min(state["current"], config.current_normal_max * 1.2))
        
        # Pressure (lower is bad)
        pressure_range = 2.0
        state["pressure"] += random.uniform(-pressure_range * noise_factor, pressure_range * noise_factor)
        state["pressure"] = max(config.pressure_critical_min * 0.8, min(state["pressure"], config.pressure_normal_min * 1.3))
        
        # RPM degrades under stress
        rpm_factor = 1.0
        if state["temperature"] > config.temp_critical_max:
            rpm_factor = 0.85
        elif state["temperature"] > config.temp_warning_max:
            rpm_factor = 0.95
        state["rpm"] = int(config.nominal_rpm * rpm_factor)
        
        # Inject anomaly
        if inject_anomaly:
            if anomaly_type == "temperature":
                state["temperature"] = config.temp_critical_max * random.uniform(1.1, 1.3)
            elif anomaly_type == "vibration":
                state["vibration"] = config.vib_critical_max * random.uniform(1.2, 1.4)
            elif anomaly_type == "current":
                state["current"] = config.current_critical_max * random.uniform(1.1, 1.3)
            elif anomaly_type == "pressure":
                state["pressure"] = config.pressure_critical_min * random.uniform(0.7, 0.9)
        
        reading = SensorReading(
            timestamp=datetime.utcnow().isoformat(),
            temperature=round(state["temperature"], 1),
            vibration=round(state["vibration"], 2),
            current=round(state["current"], 1),
            pressure=round(state["pressure"], 1),
            rpm=state["rpm"]
        )
        
        # Add to buffer
        self._logs[machine_tag].append(reading)
        
        return reading
    
    def get_latest_reading(self, machine_tag: str) -> Optional[SensorReading]:
        """Get latest sensor reading."""
        logs = self._logs.get(machine_tag, [])
        return logs[-1] if logs else None
    
    def get_logs(self, machine_tag: str, count: int = 10) -> List[SensorReading]:
        """Get recent log entries."""
        logs = self._logs.get(machine_tag, [])
        
        # Initialize buffer if empty
        if not logs:
            for _ in range(min(count, 5)):
                self.generate_reading(machine_tag)
            logs = self._logs[machine_tag]
        
        # Return last N entries
        return list(logs)[-count:]
    
    def get_severity(self, machine_tag: str, reading: SensorReading) -> tuple[str, str]:
        """
        Determine severity level and fault code.
        
        Returns:
            (severity, fault_code)
            severity: NORMAL, WARNING, CRITICAL
            fault_code: e.g., FC-TH-01, FC-VM-01
        """
        config = MACHINES.get(machine_tag)
        if not config:
            return ("NORMAL", "")
        
        # Check each sensor (worst case wins)
        severity = "NORMAL"
        fault_code = ""
        
        # Temperature
        if reading.temperature >= config.temp_critical_max:
            severity = "CRITICAL"
            fault_code = "FC-TH-01"
        elif reading.temperature >= config.temp_warning_max and severity == "NORMAL":
            severity = "WARNING"
            fault_code = "FC-TH-02"
        
        # Vibration
        if reading.vibration >= config.vib_critical_max:
            severity = "CRITICAL"
            fault_code = "FC-VM-01"
        elif reading.vibration >= config.vib_warning_max and severity == "NORMAL":
            severity = "WARNING"
            fault_code = "FC-VM-02"
        
        # Current
        if reading.current >= config.current_critical_max:
            severity = "CRITICAL"
            fault_code = "FC-CU-01"
        elif reading.current >= config.current_warning_max and severity == "NORMAL":
            severity = "WARNING"
            fault_code = "FC-CU-02"
        
        # Pressure (low is bad)
        if reading.pressure <= config.pressure_critical_min:
            severity = "CRITICAL"
            fault_code = "FC-LP-01"
        elif reading.pressure <= config.pressure_warning_min and severity == "NORMAL":
            severity = "WARNING"
            fault_code = "FC-LP-02"
        
        return (severity, fault_code)
    
    def inject_anomaly(self, machine_tag: str, anomaly_type: str = "vibration"):
        """Inject critical anomaly into machine readings."""
        logger.info(f"Injecting {anomaly_type} anomaly into {machine_tag}")
        self.generate_reading(machine_tag, inject_anomaly=True, anomaly_type=anomaly_type)
    
    def get_summary(self, machine_tag: str) -> Dict[str, Any]:
        """Get machine summary with latest reading and thresholds."""
        config = MACHINES.get(machine_tag)
        if not config:
            return {"error": "Machine not found"}
        
        reading = self.get_latest_reading(machine_tag)
        if not reading:
            reading = self.generate_reading(machine_tag)
        
        severity, fault_code = self.get_severity(machine_tag, reading)
        
        return {
            "machine_tag": machine_tag,
            "display_name": config.display_name,
            "latest_reading": asdict(reading),
            "severity": severity,
            "fault_code": fault_code,
            "thresholds": {
                "temperature": {
                    "normal_max": config.temp_normal_max,
                    "warning_max": config.temp_warning_max,
                    "critical_max": config.temp_critical_max
                },
                "vibration": {
                    "normal_max": config.vib_normal_max,
                    "warning_max": config.vib_warning_max,
                    "critical_max": config.vib_critical_max
                },
                "current": {
                    "normal_max": config.current_normal_max,
                    "warning_max": config.current_warning_max,
                    "critical_max": config.current_critical_max
                },
                "pressure": {
                    "normal_min": config.pressure_normal_min,
                    "warning_min": config.pressure_warning_min,
                    "critical_min": config.pressure_critical_min
                }
            }
        }


# Singleton
_monitor: Optional[MachineMonitor] = None

def get_machine_monitor() -> MachineMonitor:
    global _monitor
    if _monitor is None:
        _monitor = MachineMonitor()
    return _monitor
