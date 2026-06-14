# Alloy Agent - Frontend

Modern React + TypeScript dashboard for the Alloy Agent AI-powered maintenance system.

## 🎨 Features

### ✅ Dashboard View
- **Real-time Equipment Monitoring**: Live status of all 5 machines
- **Status Overview Cards**: Critical, High, Normal equipment counts
- **Equipment List**: Sortable table with operating hours, location, status
- **Click-through Navigation**: Select equipment for detailed analysis

### ✅ Equipment Detail View
- **Live Sensor Readings**: Temperature, Pressure, Vibration, Current
- **Trend Indicators**: Real-time trend analysis (increasing/decreasing/stable)
- **Historical Charts**: 24-hour time-series visualization using Recharts
- **Auto-refresh**: Updates every 10 seconds
- **4 Real-time Graphs**: Temperature, Pressure, Vibration, Current

### ✅ AI Chat Panel
- **Multi-Agent Integration**: Chat with Supervisor, Anomaly, Diagnosis, Recommendation, Report agents
- **Session Memory**: Maintains conversation context
- **Risk Level Display**: Shows CRITICAL/HIGH/MEDIUM/LOW risk assessments
- **Agent Tracing**: See which agents were involved in responses
- **Suggested Queries**: Quick-start conversation templates
- **Real-time Streaming**: Live responses from AI agents

## 🚀 Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

## 📦 Installation

```bash
cd frontend
npm install
```

## 🏃 Running

```bash
# Development mode (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend runs on: **http://localhost:5173**  
Backend API: **http://localhost:8000**

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts           # API client & TypeScript types
│   ├── components/
│   │   ├── Dashboard.tsx       # Equipment overview grid
│   │   ├── EquipmentDetail.tsx # Detailed equipment monitoring
│   │   └── ChatPanel.tsx       # AI assistant chat interface
│   ├── App.tsx                 # Main app with routing
│   ├── main.tsx               # Entry point
│   └── index.css              # Global styles + Tailwind
├── tailwind.config.js
├── vite.config.ts
└── package.json
```

## 🎯 Key Components

### Dashboard
- Displays all equipment with status badges
- Real-time statistics (total, critical, high, healthy)
- Click equipment to view details

### Equipment Detail
- Live sensor readings with trend indicators
- 4 time-series charts (24-hour history)
- Auto-refresh every 10 seconds
- Manual refresh button

### Chat Panel
- Natural language queries to AI agents
- Displays risk levels and agent metadata
- Session-based conversation memory
- Suggested starter queries

## 🔌 API Integration

All API calls are in `src/api/client.ts`:

```typescript
// Get all equipment
equipmentAPI.getAll()

// Get equipment details
equipmentAPI.getById(id)

// Get sensor history (24h)
equipmentAPI.getHistory(id, 24)

// Get latest reading
equipmentAPI.getLatest(id)

// Get trend analysis
equipmentAPI.getTrend(id, 'temperature_c', 24)

// Chat with AI
agentAPI.chat(message, sessionId)

// Check anomalies
agentAPI.checkAnomalies(equipmentId, equipmentType, sensorData)

// Diagnose equipment
agentAPI.diagnose(equipmentId, sensorData, symptoms)
```

## 🎨 Design System

### Colors
- **Primary**: Blue (#0ea5e9)
- **Danger**: Red (#ef4444)
- **Warning**: Orange/Yellow (#f59e0b)
- **Success**: Green (#10b981)

### Status Badges
- 🔴 **CRITICAL**: Red background
- 🟠 **HIGH**: Orange background
- 🟡 **MEDIUM**: Yellow background
- 🔵 **LOW**: Blue background
- 🟢 **NORMAL**: Green background

## 📊 Data Flow

1. **Dashboard** → Loads all equipment from `/api/sensors/equipment`
2. **Select Equipment** → Navigates to Equipment Detail view
3. **Equipment Detail** → Loads:
   - Equipment info (`/api/sensors/equipment/{id}`)
   - Latest reading (`/api/sensors/equipment/{id}/latest`)
   - 24h history (`/api/sensors/equipment/{id}/history?hours=24`)
   - Trends for 4 sensors (`/api/sensors/equipment/{id}/trend/{sensor}`)
4. **Chat Panel** → Sends messages to `/api/agents/chat`
5. **Auto-refresh** → Equipment Detail refreshes every 10s

## 🔥 Demo Features

Perfect for hackathon judges:

1. **Real-time Monitoring**: See live sensor data updating
2. **AI Diagnostics**: Ask "What's wrong with AC-001?" and get AI-powered root cause analysis
3. **Trend Detection**: Visual indication of increasing/decreasing trends
4. **Multi-Agent System**: Chat responses show which agents (Anomaly, Diagnosis, Recommendation) were involved
5. **Professional UI**: Clean, modern design with smooth animations

## 🐛 Troubleshooting

### CORS Errors
Make sure FastAPI backend has CORS enabled (already configured).

### API Connection Failed
Ensure backend is running on http://localhost:8000:
```bash
cd ../
source venv/bin/activate
python -m uvicorn backend.src.api.main:app --reload --port 8000
```

### Build Errors
Clear node_modules and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```

## 📝 Notes

- Frontend auto-connects to `http://localhost:8000` (configurable in `src/api/client.ts`)
- All TypeScript types are defined in `src/api/client.ts`
- Charts use Recharts for smooth animations
- Tailwind CSS provides responsive design
- Components are functional with React Hooks (no class components)
