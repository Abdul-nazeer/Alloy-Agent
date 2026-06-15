# Alloy Agent

An autonomous predictive maintenance system for steel manufacturing plants. Built for real-world industrial environments where downtime costs thousands per hour.

**Live Demo:** https://alloy-agent.vercel.app  
**API:** https://alloy-agent-production.up.railway.app

---

## What This Does

Steel plants run 24/7. When a compressor fails or a rolling mill seizes up, you're losing money every minute. This system watches your equipment in real-time, spots problems before they become failures, and tells maintenance teams exactly what to fix.

Instead of scheduled maintenance (wasteful) or reactive repairs (expensive), you get intelligent alerts that say "AC-001 will fail in 48 hours - replace the bearing now."

### The Stack

**Backend:**
- FastAPI for the API layer
- LangGraph orchestrating five specialized AI agents
- Qdrant vector database with 2,606 maintenance manual chunks
- Fine-tuned Phi-3.5 model trained on industrial maintenance data
- SQLite for operational data
- WebSocket streaming for live sensor feeds

**Frontend:**
- React with TypeScript
- Recharts for live equipment visualization  
- Custom HMI-inspired interface (industrial control room aesthetic)
- WebSocket client for real-time updates

**Deployment:**
- Backend on Railway (auto-scaling with health checks)
- Frontend on Vercel (edge network, instant deploys)
- Qdrant Cloud for vector search
- Groq API for LLM inference (14K requests/day free tier)

---

## Why This Architecture

We tried several approaches before landing here:

1. **Single LLM agent** → Too slow, couldn't handle complex diagnosis
2. **Rule-based system** → Too brittle, missed edge cases  
3. **Multi-agent with RAG** → Fast, accurate, explainable ✓

The supervisor agent routes queries to specialists:
- Anomaly agent runs threshold checks and ML detection
- Diagnosis agent does root cause analysis with manual context
- Recommendation agent suggests maintenance actions
- Report agent generates structured summaries
- Conversational agent handles general questions

Each agent only loads when needed, keeping response times under 3 seconds even on free-tier APIs.

---

## Getting Started

### Prerequisites

You'll need:
- Python 3.11 or higher
- Node.js 18 or higher  
- A Groq API key (free at console.groq.com)
- A Qdrant Cloud instance (free tier works fine)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start the server
python -m uvicorn src.api.main:app --reload --port 8000
```

The API will be at http://localhost:8000 with interactive docs at /docs.

### Frontend Setup

```bash
cd frontend

# Install packages
npm install

# Start dev server
npm run dev
```

Open http://localhost:5173 to see the interface.

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# LLM Configuration
GROQ_API_KEY=your_groq_key_here
LLM_PROVIDER=groq  # or huggingface
GROQ_MODEL=llama-3.1-8b-instant

# HuggingFace (fallback)
HUGGINGFACE_API_KEY=your_hf_key_here
HF_MODEL_ID=CodeMasterAbdul/alloy-phi3-steel-maintenance

# Vector Database
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_key
QDRANT_COLLECTION_CHUNKS=alloy_maintenance
QDRANT_COLLECTION_PAGES=alloy_pages

# System Configuration
ENABLE_AUTONOMOUS_MONITORING=false  # true for production
API_USAGE_MODE=balanced  # balanced, production, or conservative
```

---

## How to Use It

### Dashboard

The main view shows five equipment cards with live sensor data streaming every 15 seconds. Each card displays current status (NORMAL to CRITICAL) and key metrics.

Click any equipment card to see detailed charts and historical trends. The AI assistant in the sidebar can answer questions about that specific machine.

### Demo Anomaly Button

Since sensor data defaults to normal/healthy values (to conserve API calls), there's a DEMO ANOMALY button on the dashboard. Click it to trigger a critical failure on AC-001 and watch the system:

1. Detect the anomaly in real-time
2. Route to diagnosis agent
3. Query maintenance manuals via RAG
4. Generate a complete incident report
5. Create logbook entry
6. Fire alert notifications

This demonstrates the full autonomous workflow in about 5 seconds.

### AI Chat

Ask questions in natural language:
- "What's causing the temperature spike on AC-001?"
- "How do I replace a bearing on the rolling mill?"
- "Show me the maintenance procedure for cooling fans"

The system extracts equipment context, fetches relevant manual sections, and responds with citations. Every answer includes source attribution so you can verify against the original documentation.

### Reports & Logbook

Analysis Reports shows AI-generated health summaries with:
- Risk assessment and severity level
- Root cause analysis
- Maintenance recommendations with estimated time and parts
- Both technical detail for engineers and executive summary for managers

Operations Logbook tracks all system activities - maintenance performed, anomalies detected, repairs completed. Each entry is timestamped and tagged with equipment ID and engineer name.

---

## API Reference

### Equipment Endpoints

```bash
# List all equipment
GET /api/sensors/equipment

# Get equipment details
GET /api/sensors/equipment/{equipment_id}

# Latest sensor reading
GET /api/sensors/equipment/{equipment_id}/latest

# Historical data
GET /api/sensors/equipment/{equipment_id}/history?hours=24

# Real-time WebSocket stream
WS /ws/sensors/{equipment_id}
```

### AI Agent Endpoints

```bash
# Chat with AI assistant
POST /api/agents/chat
{
  "message": "Diagnose AC-001",
  "session_id": "optional-session-id"
}

# Check for anomalies
POST /api/agents/check-anomalies
{
  "equipment_id": "AC-001",
  "equipment_type": "Air Compressor",
  "sensor_data": {...}
}

# Equipment diagnosis
POST /api/agents/diagnose
{
  "equipment_id": "AC-001",
  "sensor_data": {...},
  "symptoms": ["excessive heat", "unusual noise"]
}
```

### RAG & Documents

```bash
# Query knowledge base
POST /api/rag/query
{
  "query": "bearing maintenance procedure",
  "top_k": 5
}

# Serve PDF manuals
GET /api/pdfs/{filename}
```

### Reports & Alerts

```bash
# List reports
GET /api/reports/list?equipment_id=AC-001&days=30

# Get logbook entries
GET /api/reports/logbook?status=OPEN

# Unread alerts
GET /api/alerts/unread

# Mark alert as read
POST /api/alerts/{alert_id}/mark-read
```

---

## System Architecture

```
┌──────────────────┐
│  React Frontend  │  TypeScript, Vite, Tailwind
│   (Vercel Edge)  │  WebSocket client for live data
└────────┬─────────┘
         │
         │ HTTP/WS
         ▼
┌──────────────────┐
│  FastAPI Backend │  Python 3.11, async/await
│    (Railway)     │  WebSocket server, REST API
└────────┬─────────┘
         │
    ┌────┴────┬────────────┬──────────┐
    ▼         ▼            ▼          ▼
┌────────┐ ┌──────┐ ┌──────────┐ ┌────────┐
│SQLite  │ │Qdrant│ │  Groq    │ │LangGraph│
│Metadata│ │Vector│ │LLM API   │ │Multi-   │
│845 rows│ │Store │ │Free Tier │ │Agent    │
└────────┘ └──────┘ └──────────┘ └────────┘
```

The architecture separates concerns cleanly:

**Data Layer:** SQLite stores equipment metadata, incidents, reports. Qdrant holds embedded maintenance manual chunks for semantic search.

**Agent Layer:** LangGraph manages workflow. The supervisor routes queries to specialists based on intent detection.

**API Layer:** FastAPI exposes everything via REST and WebSocket. CORS configured for cross-origin requests.

**UI Layer:** React components subscribe to WebSocket for live updates. All data fetching through a centralized API client.

---

## What Makes This Different

**Autonomous Operation:** Once running, the system monitors equipment continuously without human input. Alerts fire automatically when thresholds are exceeded.

**Production-Grade RAG:** Not just basic similarity search. We use hybrid retrieval (dense + sparse), cross-encoder reranking, and citation extraction with bounding boxes. Every AI response includes verifiable sources.

**Real Industrial Data:** Sensor simulation based on C-MAPSS turbofan degradation dataset. Failure patterns match real bearing wear, compressor fouling, and thermal degradation.

**Cost-Optimized:** Built to run on free tiers. Sensor streaming at 15-second intervals instead of 1-second. Anomaly detection uses rules first, AI only for critical issues. Response caching prevents duplicate API calls. Total daily API usage: 30-60 calls (vs 14,400 limit).

**Role-Based Access:** Technicians see diagnostic details and repair procedures. Supervisors get reports and can mark issues resolved. Managers see executive summaries with business impact and cost estimates.

---

## Project Structure

```
Alloy-Agent/
├── backend/
│   ├── src/
│   │   ├── agents/              # Multi-agent system
│   │   │   ├── supervisor.py    # LangGraph orchestration
│   │   │   ├── anomaly_agent.py
│   │   │   ├── diagnosis_agent.py
│   │   │   ├── recommendation_agent.py
│   │   │   ├── report_agent.py
│   │   │   ├── conversational_agent.py
│   │   │   ├── llm_client.py    # Groq/HuggingFace wrapper
│   │   │   ├── prompts.py       # Agent prompts
│   │   │   └── tools.py         # Agent tools/functions
│   │   ├── api/
│   │   │   ├── main.py          # FastAPI app
│   │   │   └── routes/          # API endpoints
│   │   ├── database/
│   │   │   └── schema.py        # SQLite schema
│   │   ├── rag/
│   │   │   ├── pipeline.py      # RAG orchestration
│   │   │   ├── retriever.py     # Hybrid search
│   │   │   ├── ingest.py        # PDF processing
│   │   │   └── vector_store.py  # Qdrant client
│   │   └── services/
│   │       ├── sensor_simulator.py      # Live sensor generation
│   │       ├── auto_report_generator.py # Autonomous monitoring
│   │       └── api_config.py            # Usage optimization
│   ├── data/
│   │   ├── maintenance.db       # SQLite database
│   │   └── synthetic/           # Generated sensor logs
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx    # Main equipment view
│   │   │   ├── EquipmentDetail.tsx  # Live charts
│   │   │   ├── ChatPanel.tsx    # AI assistant
│   │   │   ├── ReportsView.tsx  # Analysis reports
│   │   │   └── LogbookView.tsx  # Operations log
│   │   ├── api/
│   │   │   └── client.ts        # API client
│   │   └── hooks/
│   │       └── useWebSocket.ts  # WebSocket hook
│   └── package.json
├── deployment/
│   ├── Dockerfile               # Container image
│   └── railway.json             # Railway config
├── .env                         # Environment config
└── README.md
```

---

## Performance

**Response Times:**
- WebSocket latency: <50ms
- Equipment query: <10ms  
- RAG query: 400-800ms (including reranking)
- Full diagnosis: 2-5 seconds
- Chart render: 60 FPS

**Resource Usage:**
- Backend memory: 180-250 MB
- Frontend bundle: 584 KB raw, 180 KB gzipped
- Database size: 1.2 MB
- Vector store: 45 MB (2,606 chunks)

**API Consumption:**
- Normal operation: 0 calls (just sensor streaming)
- Demo anomaly: 6-10 calls (full multi-agent analysis)
- Daily estimate: 30-60 calls (well within free tier)

---

## Deployment

Both frontend and backend are deployed and running:

**Backend:** Railway handles auto-deploy from main branch. Health checks every 30 seconds, auto-restart on failure. Logs available via Railway dashboard.

**Frontend:** Vercel rebuilds on every push. Edge network serves from 70+ locations worldwide. Preview deployments for every PR.

**Database:** SQLite file persists in Railway volume. Qdrant runs on their managed cloud with daily backups.

To deploy your own instance:

1. Fork this repo
2. Create Railway project, link to GitHub
3. Add environment variables in Railway dashboard  
4. Create Vercel project, link to GitHub
5. Set `VITE_API_URL` in Vercel env vars to your Railway URL
6. Push to main - both deploy automatically

See full deployment guide in `docs/DEPLOYMENT.md`.

---

## Known Limitations

**HuggingFace DNS resolution fails on Railway** - This is expected. Railway's container environment can't resolve `api-inference.huggingface.co`. System automatically falls back to Groq API. If you need HuggingFace inference, deploy on a platform with full DNS access.

**Sensor simulation isn't real hardware** - Obviously. For production use, replace the simulator with actual MODBUS/OPC-UA clients reading from PLCs. The rest of the system (agents, RAG, reports) works unchanged.

**Free tier rate limits** - Groq allows 14,400 requests/day. If you trigger demo anomaly 1,440 times in 24 hours, you'll hit the limit. Normal usage is 30-60 calls/day.

**SQLite isn't multi-region** - For high availability deployments, swap SQLite for PostgreSQL. Schema is standard SQL, no SQLite-specific features.

**No authentication** - This demo has role-based logic but no actual auth. Add JWT tokens or OAuth before putting this in production.

---

## Troubleshooting

**Backend won't start:**
```bash
# Check if port 8000 is already in use
lsof -i:8000

# Verify Python version
python --version  # Should be 3.11+

# Check environment variables are set
cat .env | grep -E "GROQ_API_KEY|QDRANT_URL"
```

**Frontend shows "Backend: Disconnected":**
```bash
# Test backend health
curl http://localhost:8000/health

# Check CORS settings in backend/src/api/main.py
# Ensure frontend URL is in allowed origins
```

**WebSocket won't connect:**
```bash
# Test WebSocket directly
wscat -c ws://localhost:8000/ws/sensors/AC-001

# If that works, check browser console for errors
# Look for "WebSocket connection failed" messages
```

**Chat not responding:**
```bash
# Check Groq API key is valid
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"

# Check backend logs for LLM errors
# Look for "LLM_PROVIDER" and "Falling back to Groq"
```

**No data in charts:**
- Hard refresh the page (Ctrl+Shift+R)
- Check equipment ID exists: `curl http://localhost:8000/api/sensors/equipment`
- Verify sensor simulator is running: look for "Sensor streaming started" in logs

---

## Contributing

Found a bug? Want to add a feature? PRs welcome.

```bash
# Fork and clone
git clone https://github.com/yourusername/Alloy-Agent
cd Alloy-Agent

# Create feature branch
git checkout -b feature/your-feature

# Make changes, test locally
# ...

# Commit with clear message
git commit -m "Add: your feature description"

# Push and create PR
git push origin feature/your-feature
```

Keep PRs focused on a single change. Add tests for new features. Update docs if you change APIs.

---

## License

MIT License - use this however you want. If you build something cool with it, let me know.

---

## Tech Notes

**Why LangGraph over LangChain?** Better control flow. LangChain's chains are too linear for complex multi-agent routing. LangGraph gives us conditional edges and cycles.

**Why Qdrant over Pinecone/Weaviate?** Hybrid search out of the box. Most vector DBs only do dense retrieval. Qdrant supports sparse vectors (BM25) + dense (embeddings) in one query.

**Why FastAPI over Flask?** Native async/await support. WebSocket handling is cleaner. Automatic API docs with OpenAPI/Swagger.

**Why React over Vue/Svelte?** TypeScript support is more mature. Recharts library for live data visualization. Larger ecosystem for industrial UI components.

**Why Railway over AWS?** Simpler. No VPC configs, security groups, load balancers. Push to GitHub, it deploys. Logs and metrics included. Free tier is actually usable.

**Why SQLite over PostgreSQL?** For this demo, latency doesn't matter and traffic is low. SQLite means one less service to run. For production, swap to Postgres - the ORM (SQLAlchemy) makes it a 2-line change.

---

**Questions?** Open an issue or check the wiki for more detailed guides on specific subsystems (RAG pipeline, agent orchestration, sensor simulation).
