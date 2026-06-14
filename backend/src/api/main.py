"""
FastAPI Main Application Entrypoint
"""

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import asyncio
import json

from backend.src.api.routes.rag_routes import router as rag_router
from backend.src.api.routes.agent_routes import router as agent_router
from backend.src.api.routes.sensor_routes import router as sensor_router
from backend.src.api.routes.reports_routes import router as reports_router
from backend.src.database import init_database
from backend.src.services.sensor_data_service import get_sensor_service
from backend.src.services.sensor_simulator import get_sensor_simulator
from backend.src.services.auto_report_generator import get_report_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get PDF directory path
PDF_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "manuals"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown tasks.
    """
    # ── STARTUP ──────────────────────────────────────────────────────
    logger.info("🚀 Starting Alloy Agent API...")
    
    # Initialize database schema
    try:
        init_database()
        logger.info("✓ Database initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Load sensor data service
    try:
        sensor_service = get_sensor_service()
        logger.info("✓ Sensor data service initialized")
    except Exception as e:
        logger.error(f"Sensor service initialization failed: {e}")
    
    logger.info("✓ Alloy Agent API ready\n")
    
    yield  # Application runs here
    
    # ── SHUTDOWN ─────────────────────────────────────────────────────
    logger.info("Shutting down Alloy Agent API...")


app = FastAPI(
    title="Alloy Agent API",
    description="Backend API for the Alloy Agent AI maintenance assistant.",
    version="1.0.0",
    lifespan=lifespan
)

# Allow CORS for the frontend React dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(agent_router)
app.include_router(sensor_router)
app.include_router(reports_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Alloy Agent API"}

@app.api_route("/api/pdfs/{filename}", methods=["GET", "HEAD"])
async def get_pdf(filename: str):
    """Serve PDF files with proper headers for inline viewing"""
    file_path = PDF_DIR / filename
    if file_path.exists():
        return FileResponse(
            file_path,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename={filename}",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    return {"error": "PDF not found"}, 404

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)


# ══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET - Real-time Sensor Streaming
# ══════════════════════════════════════════════════════════════════════════════

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, equipment_id: str):
        await websocket.accept()
        if equipment_id not in self.active_connections:
            self.active_connections[equipment_id] = []
        self.active_connections[equipment_id].append(websocket)
        logger.info(f"WebSocket connected for {equipment_id}. Total: {len(self.active_connections[equipment_id])}")
    
    def disconnect(self, websocket: WebSocket, equipment_id: str):
        if equipment_id in self.active_connections:
            self.active_connections[equipment_id].remove(websocket)
            if not self.active_connections[equipment_id]:
                del self.active_connections[equipment_id]
        logger.info(f"WebSocket disconnected for {equipment_id}")
    
    async def broadcast(self, equipment_id: str, message: dict):
        if equipment_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[equipment_id]:
                try:
                    await connection.send_json(message)
                except:
                    dead_connections.append(connection)
            
            for dead in dead_connections:
                self.disconnect(dead, equipment_id)

manager = ConnectionManager()

@app.websocket("/ws/sensors/{equipment_id}")
async def websocket_sensor_stream(websocket: WebSocket, equipment_id: str):
    """
    WebSocket endpoint for real-time sensor streaming with auto-report generation
    
    Usage:
        ws://localhost:8000/ws/sensors/AC-001
    
    Streams sensor readings every 2 seconds with anomaly detection.
    Automatically generates reports and logbook entries when anomalies detected.
    """
    await manager.connect(websocket, equipment_id)
    simulator = get_sensor_simulator()
    report_generator = get_report_generator()
    
    try:
        async for reading in simulator.stream_readings(equipment_id, interval=2.0):
            # Send reading to client
            await websocket.send_json(reading)
            
            # Auto-generate reports if anomalies detected
            if reading.get('has_anomaly'):
                asyncio.create_task(report_generator.process_sensor_reading(reading))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, equipment_id)
        logger.info(f"Client disconnected from {equipment_id}")
    except Exception as e:
        logger.error(f"WebSocket error for {equipment_id}: {e}")
        manager.disconnect(websocket, equipment_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.api.main:app", host="0.0.0.0", port=8000, reload=True)
