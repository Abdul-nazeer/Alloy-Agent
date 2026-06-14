"""
Multi-agent system for intelligent maintenance decision support.

LangGraph-based architecture with specialized agents:
- Supervisor: Intelligent routing
- Anomaly Agent: Real-time sensor analysis
- Diagnosis Agent: Root cause analysis
- Recommendation Agent: Action planning
- Report Agent: Structured reporting

Usage:
    from backend.src.agents import chat, diagnose_equipment
    
    response = chat(
        query="What's wrong with AC-001?",
        equipment_id="AC-001",
        equipment_type="Air Compressor",
        sensor_data={"TEMP": 112.5, "VIB": 3.2}
    )
    
    print(response["answer"])
"""

from backend.src.agents.agent_api import (
    chat,
    diagnose_equipment,
    generate_maintenance_report,
    check_anomalies,
)

from backend.src.agents.state import (
    AgentState,
    SensorReading,
    Anomaly,
    RootCause,
    Recommendation,
    create_initial_state,
)

__all__ = [
    # High-level API
    "chat",
    "diagnose_equipment",
    "generate_maintenance_report",
    "check_anomalies",
    
    # State types
    "AgentState",
    "SensorReading",
    "Anomaly",
    "RootCause",
    "Recommendation",
    "create_initial_state",
]
