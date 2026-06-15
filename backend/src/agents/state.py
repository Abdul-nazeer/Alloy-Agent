"""
LangGraph State Schema — Shared whiteboard for all agents
"""

from typing import TypedDict, Optional, Annotated, Literal
from operator import add
from dataclasses import dataclass, field


# ══════════════════════════════════════════════════════════════════════════════
# Sensor Data Types
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class SensorReading:
    """Individual sensor measurement."""
    sensor_type: str  # "TEMP" | "VIB" | "PRES" | "CURR" | "RPM"
    value: float
    unit: str
    timestamp: str
    is_anomalous: bool = False
    severity: Optional[str] = None  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"


@dataclass
class Anomaly:
    """Detected anomaly with severity."""
    sensor_type: str
    current_value: float
    threshold: float
    deviation_percent: float
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    message: str


@dataclass
class RootCause:
    """Probable root cause with confidence."""
    cause: str
    confidence: float  # 0.0-1.0
    evidence: list[str]
    doc_sources: list[str]


@dataclass
class Recommendation:
    """Action recommendation with priority."""
    priority: int
    action: str
    reason: str
    estimated_time: str
    required_parts: list[str]
    safety_notes: list[str]


# ══════════════════════════════════════════════════════════════════════════════
# Main Agent State
# ══════════════════════════════════════════════════════════════════════════════

class AgentState(TypedDict):
    """
    Shared state that flows through the LangGraph.
    Every agent can read and write to this.
    """
    
    # ── Input (from user) ────────────────────────────────────────────────────
    query: str                                  # User's natural language question
    equipment_id: Optional[str]                 # e.g., "FC-TH-01"
    equipment_type: Optional[str]               # e.g., "Air Compressor"
    sensor_readings: Optional[list[SensorReading]]  # Current readings
    error_codes: Optional[list[str]]            # Fault codes from equipment
    user_role: Literal["technician", "supervisor", "manager"]  # Controls output depth
    session_id: str                             # For multi-turn memory
    uploaded_doc_ids: list[str]                 # User-uploaded documents in scope
    
    # ── Working Data (agents write) ──────────────────────────────────────────
    retrieved_chunks: list[dict]                # RAG results
    anomalies_detected: list[Anomaly]           # Threshold violations
    diagnosis: Optional[str]                    # Primary fault diagnosis
    root_causes: list[RootCause]                # Ranked probable causes
    risk_level: Optional[Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]]
    recommendations: list[Recommendation]       # Prioritized actions
    rul_estimate: Optional[dict]                # Remaining Useful Life prediction
    citations: list[dict]                       # Citation metadata (doc, page, bbox)
    
    # ── Control Flow ─────────────────────────────────────────────────────────
    next_agent: Optional[str]                   # Supervisor's routing decision
    iteration_count: int                        # Prevent infinite loops
    requires_escalation: bool                   # CRITICAL alert flag
    completed_agents: list[str]                 # Track execution path
    
    # ── Output ───────────────────────────────────────────────────────────────
    final_answer: str                           # Terminal output to user
    report_content: Optional[str]               # Structured maintenance report
    messages: Annotated[list[dict], add]        # Conversation history (multi-turn)
    metadata: dict                              # Additional context
    
    # ── Error Handling ───────────────────────────────────────────────────────
    errors: Annotated[list[str], add]           # Error messages from agents


# ══════════════════════════════════════════════════════════════════════════════
# Tool Outputs
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class RAGResult:
    """Output from RAG retrieval tool."""
    chunks: list[dict]
    sources: list[dict]
    grounded: bool
    num_results: int
    context: str


@dataclass
class ThresholdCheck:
    """Output from threshold lookup tool."""
    sensor_type: str
    normal_min: float
    normal_max: float
    warning_threshold: float
    critical_threshold: float
    unit: str


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def create_initial_state(
    query: str,
    equipment_id: Optional[str] = None,
    equipment_type: Optional[str] = None,
    sensor_readings: Optional[list[SensorReading]] = None,
    error_codes: Optional[list[str]] = None,
    user_role: str = "technician",
    session_id: str = "default",
    uploaded_doc_ids: Optional[list[str]] = None,
) -> AgentState:
    """Create initial state for graph execution."""
    return AgentState(
        # Input
        query=query,
        equipment_id=equipment_id,
        equipment_type=equipment_type,
        sensor_readings=sensor_readings or [],
        error_codes=error_codes or [],
        user_role=user_role,
        session_id=session_id,
        uploaded_doc_ids=uploaded_doc_ids or [],
        
        # Working data
        retrieved_chunks=[],
        anomalies_detected=[],
        diagnosis=None,
        root_causes=[],
        risk_level=None,
        recommendations=[],
        rul_estimate=None,
        citations=[],
        
        # Control
        next_agent=None,
        iteration_count=0,
        requires_escalation=False,
        completed_agents=[],
        
        # Output
        final_answer="",
        report_content=None,
        messages=[],
        metadata={},
        
        # Errors
        errors=[],
    )


def parse_sensor_readings(raw_data: dict) -> list[SensorReading]:
    """Parse raw sensor dict to SensorReading objects."""
    # Mapping from database column names to sensor types
    SENSOR_TYPE_MAPPING = {
        "temperature_c": "TEMP",
        "pressure_bar": "PRES",
        "vibration_mm_s": "VIB",
        "current_a": "CURR",
        "rpm": "RPM",
        "torque_nm": "TORQUE",
    }
    
    # Unit mapping
    UNIT_MAPPING = {
        "TEMP": "°C",
        "PRES": "bar",
        "VIB": "mm/s",
        "CURR": "A",
        "RPM": "RPM",
        "TORQUE": "Nm",
    }
    
    readings = []
    for sensor_key, data in raw_data.items():
        # Convert sensor key to standard type
        sensor_type = SENSOR_TYPE_MAPPING.get(sensor_key, sensor_key.upper())
        unit = UNIT_MAPPING.get(sensor_type, "")
        
        if isinstance(data, dict):
            readings.append(SensorReading(
                sensor_type=sensor_type,
                value=data.get("value", 0.0),
                unit=data.get("unit", unit),
                timestamp=data.get("timestamp", ""),
            ))
        else:
            # Simple value
            readings.append(SensorReading(
                sensor_type=sensor_type,
                value=float(data),
                unit=unit,
                timestamp="",
            ))
    return readings
