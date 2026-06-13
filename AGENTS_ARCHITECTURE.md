# Alloy-Agent: Multi-Agent Architecture

## Overview

The system uses a **multi-agent architecture** where specialized agents handle different maintenance tasks. This follows the hackathon requirement for intelligent, context-aware decision support.

---

## Agent Hierarchy

```
User Query
    ↓
Router Agent (decides which agent to use)
    ↓
┌─────────────┬──────────────┬─────────────┬──────────────┐
│             │              │             │              │
Diagnostic   Predictive   Planning    Query          
Agent        Agent        Agent       Agent
│             │              │             │
└─────────────┴──────────────┴─────────────┴──────────────┘
              ↓
         Knowledge Base (RAG)
              ↓
         Fine-tuned Phi-3 Model
```

---

## Agent Types

### 1. Router Agent
**Purpose:** Routes user requests to appropriate specialized agent

**Inputs:**
- User query or request type
- Context from previous conversation

**Logic:**
- If query contains: "diagnose", "fault", "error" → Diagnostic Agent
- If query contains: "predict", "RUL", "failure", "when" → Predictive Agent
- If query contains: "plan", "maintenance", "schedule" → Planning Agent
- Otherwise → Query Agent (general questions)

**Outputs:**
- Selected agent
- Formatted input for agent

---

### 2. Diagnostic Agent
**Purpose:** Diagnose equipment failures and identify root causes

**Inputs:**
- Equipment ID/type
- Sensor readings (temperature, vibration, pressure, etc.)
- Error messages/codes
- Operating hours

**Process:**
1. Retrieve relevant equipment manuals from RAG
2. Retrieve similar historical failures from RAG
3. Format context + input for LLM
4. Call fine-tuned Phi-3 model
5. Parse and structure output

**Outputs:**
```json
{
  "diagnosis": "Bearing failure due to overheating",
  "root_cause": "Insufficient lubrication",
  "risk_level": "HIGH",
  "confidence": 0.87,
  "supporting_evidence": [
    "Temperature 95°C (20°C above normal)",
    "Vibration 1.2mm/s (2.4x baseline)",
    "Similar failure in maintenance log ML-2023-0451"
  ],
  "sources": [
    "Air Compressor Manual - Section 5.3",
    "Historical Log - ML-2023-0451"
  ]
}
```

---

### 3. Predictive Agent
**Purpose:** Predict equipment failures and estimate remaining useful life

**Inputs:**
- Equipment ID/type
- Current sensor readings
- Operating hours
- Maintenance history

**Process:**
1. Retrieve equipment degradation patterns from RAG
2. Compare current state to historical failure data
3. Use fine-tuned model for RUL prediction
4. Calculate risk level based on thresholds

**Outputs:**
```json
{
  "equipment_id": "AC-001",
  "equipment_type": "Air Compressor",
  "remaining_useful_life": {
    "hours": 120,
    "confidence_interval": "80-160 hours",
    "confidence": 0.75
  },
  "failure_probability": {
    "next_24h": 0.05,
    "next_week": 0.25,
    "next_month": 0.68
  },
  "risk_level": "MEDIUM",
  "degradation_indicators": [
    "Temperature trend: +2°C per 100 hours",
    "Vibration trend: +0.1mm/s per 100 hours"
  ],
  "early_warning": "Equipment showing signs of bearing wear. Recommend inspection within 5 days.",
  "sources": [
    "Historical degradation pattern: Similar equipment failed at 2,250 hours"
  ]
}
```

---

### 4. Planning Agent
**Purpose:** Generate prioritized maintenance plans

**Inputs:**
- List of equipment with issues
- Spare parts availability
- Procurement lead times
- Production schedule constraints

**Process:**
1. Retrieve maintenance SOPs from RAG
2. Get risk levels for all equipment
3. Consider spare availability and lead time
4. Use LLM to generate optimized plan
5. Prioritize based on criticality

**Outputs:**
```json
{
  "maintenance_plan": {
    "immediate_actions": [
      {
        "priority": 1,
        "equipment": "AC-001",
        "action": "Replace bearing assembly",
        "risk_if_delayed": "CRITICAL - Risk of catastrophic failure",
        "estimated_downtime": "4 hours",
        "spare_availability": "In stock",
        "recommended_window": "Next 48 hours"
      }
    ],
    "scheduled_actions": [
      {
        "priority": 2,
        "equipment": "CF-003",
        "action": "Motor inspection and lubrication",
        "risk_if_delayed": "MEDIUM",
        "estimated_downtime": "2 hours",
        "spare_availability": "N/A",
        "recommended_window": "Within 7 days"
      }
    ],
    "long_term_actions": [
      {
        "equipment": "RM-005",
        "action": "Vibration analysis study",
        "timeline": "Next monthly shutdown"
      }
    ],
    "spare_procurement": [
      {
        "part": "Bearing 6308-2RS",
        "quantity": 2,
        "lead_time": "3 days",
        "reason": "Predicted requirement for AC-002 and AC-004"
      }
    ]
  },
  "bottleneck_analysis": "AC-001 is critical path equipment. Delay will impact rolling mill operation.",
  "sources": [
    "Maintenance SOP: Bearing Replacement Procedure",
    "Spare inventory: Current stock levels"
  ]
}
```

---

### 5. Query Agent (Conversational)
**Purpose:** Answer general maintenance questions using RAG

**Inputs:**
- Natural language query
- Conversation history (multi-turn)

**Process:**
1. Retrieve relevant documents from RAG (manuals, SOPs, logs)
2. Format as context for LLM
3. Generate answer with source citations
4. Maintain conversation context

**Outputs:**
```json
{
  "answer": "The recommended lubrication interval for air compressor bearings is every 500 operating hours or 3 months, whichever comes first. Use high-temperature bearing grease (NLGI Grade 2) as specified in the manual.",
  "sources": [
    {
      "document": "Air Compressor Maintenance Manual",
      "section": "5.2 - Lubrication Schedule",
      "relevance": 0.94
    },
    {
      "document": "Preventive Maintenance SOP",
      "section": "Lubrication Guidelines",
      "relevance": 0.87
    }
  ],
  "related_questions": [
    "What type of grease should I use?",
    "How do I check if bearing needs lubrication?",
    "What are signs of insufficient lubrication?"
  ]
}
```

---

## Supporting Components

### RAG Pipeline
**Purpose:** Retrieve relevant context from knowledge base

**Process:**
1. Convert query to embedding (sentence-transformers)
2. Search Qdrant vector DB
3. Retrieve top-k most relevant documents
4. Rerank results (optional)
5. Format as context for LLM

**Collections:**
- `equipment_manuals` - Equipment technical documentation
- `maintenance_sops` - Standard operating procedures
- `historical_logs` - Past maintenance records and failures
- `fault_patterns` - Known failure modes and solutions

---

### LLM Client
**Purpose:** Interface with fine-tuned Phi-3 model

**Methods:**
- `generate()` - Single response generation
- `generate_structured()` - Structured JSON output
- `chat()` - Multi-turn conversation

**Features:**
- Prompt templates for each agent type
- Error handling and retries
- Response parsing and validation
- Source citation extraction

---

### Anomaly Detector
**Purpose:** Real-time abnormality detection from sensor data

**Process:**
1. Compare sensor values to baselines
2. Calculate z-scores or anomaly scores
3. Detect outliers using statistical methods
4. Generate alerts for significant deviations

**Output:**
```json
{
  "anomaly_detected": true,
  "equipment_id": "AC-001",
  "anomaly_type": "temperature_spike",
  "severity": "HIGH",
  "details": {
    "sensor": "temperature",
    "current_value": 95,
    "baseline": 75,
    "deviation": "+26.7%",
    "threshold": "+15%"
  },
  "timestamp": "2024-06-13T10:30:00Z"
}
```

---

## Agent Implementation Files

### Core Agents:
```
backend/src/agents/
├── __init__.py
├── base_agent.py              # Base class for all agents
├── router_agent.py            # Routes requests to specialized agents
├── diagnostic_agent.py        # Equipment diagnosis
├── predictive_agent.py        # Failure prediction & RUL
├── planning_agent.py          # Maintenance planning
├── query_agent.py             # Conversational Q&A
├── rag_pipeline.py            # RAG retrieval logic
├── llm_client.py              # HuggingFace Phi-3 client
└── prompts.py                 # Prompt templates
```

### Supporting Modules:
```
backend/src/alerting/
├── __init__.py
├── anomaly_detector.py        # Real-time anomaly detection
└── alert_manager.py           # Alert generation and management

backend/src/simulation/
├── __init__.py
└── sensor_simulator.py        # Simulate sensor data for demo
```

---

## Agent Prompt Templates

### Diagnostic Agent Prompt:
```
You are an expert maintenance engineer specializing in industrial equipment diagnostics.

EQUIPMENT INFORMATION:
{equipment_info}

SENSOR READINGS:
{sensor_data}

ERROR MESSAGES:
{error_messages}

RELEVANT DOCUMENTATION:
{rag_context}

TASK:
Diagnose the equipment issue and provide:
1. Primary diagnosis
2. Root cause analysis
3. Risk level (LOW/MEDIUM/HIGH/CRITICAL)
4. Supporting evidence
5. Immediate recommended actions

FORMAT YOUR RESPONSE AS:
DIAGNOSIS: [primary issue]
ROOT CAUSE: [underlying cause]
RISK LEVEL: [severity]
EVIDENCE: [bullet points]
RECOMMENDATIONS: [action items]
```

### Predictive Agent Prompt:
```
You are an expert in predictive maintenance and equipment lifecycle analysis.

EQUIPMENT: {equipment_type} (ID: {equipment_id})
OPERATING HOURS: {operating_hours}
CURRENT CONDITION: {sensor_data}

HISTORICAL DEGRADATION PATTERNS:
{rag_context}

TASK:
Predict equipment remaining useful life and failure probability:
1. Estimate RUL in operating hours
2. Calculate failure probability (24h, 7d, 30d)
3. Classify risk level
4. Identify degradation indicators
5. Provide early warning if needed

FORMAT AS:
RUL: [hours] ± [confidence interval]
FAILURE PROBABILITY: 24h: [%] | 7d: [%] | 30d: [%]
RISK LEVEL: [LOW/MEDIUM/HIGH/CRITICAL]
DEGRADATION: [trends]
WARNING: [if applicable]
```

---

## Agent Interaction Flow

### Example: User asks "Diagnose air compressor AC-001"

1. **Router Agent** → Identifies as diagnostic task
2. **Diagnostic Agent**:
   - Retrieves sensor data for AC-001
   - Queries RAG for air compressor manuals
   - Queries RAG for similar historical failures
   - Formats prompt with context
   - Calls fine-tuned Phi-3 model
   - Parses response
   - Structures output with sources
3. **Response** → Returns to user with citations

---

## Multi-Turn Conversation

Agents maintain conversation context:

```
User: "What's wrong with AC-001?"
Agent: [Diagnostic Agent provides diagnosis]

User: "How long before it fails?"
Agent: [Predictive Agent uses context from previous turn]

User: "What should I do?"
Agent: [Planning Agent generates maintenance plan]
```

Context stored in conversation state.

---

## Next Steps

Build agents in this order:

1. **Base Agent** - Abstract class with common functionality
2. **LLM Client** - HuggingFace API integration
3. **RAG Pipeline** - Retrieval logic
4. **Query Agent** - Simplest, test RAG + LLM
5. **Diagnostic Agent** - Core functionality
6. **Predictive Agent** - RUL prediction
7. **Planning Agent** - Maintenance planning
8. **Router Agent** - Tie everything together

---

Ready to start building? Let me know!
