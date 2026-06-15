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
from backend.src.api.routes.alerts_routes import router as alerts_router
from backend.src.api.routes.historical_routes import router as historical_router
from backend.src.api.routes.spare_parts_routes import router as spare_parts_router
# from backend.src.api.routes.feedback_routes import router as feedback_router  # Temporarily disabled
from backend.src.database import init_database
from backend.src.services.sensor_data_service import get_sensor_service
from backend.src.services.sensor_simulator import get_sensor_simulator
from backend.src.services.auto_report_generator import get_report_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get PDF directory path
PDF_DIR = Path(__file__).parent.parent.parent.parent / "data" / "raw" / "manuals"


# ══════════════════════════════════════════════════════════════════════════════
# AUTONOMOUS MONITORING LOOP
# ══════════════════════════════════════════════════════════════════════════════

async def autonomous_monitoring_loop():
    """
    Background task that continuously monitors all equipment
    and auto-generates reports when anomalies detected.
    
    **DISABLED for demo mode** - Use "DEMO ANOMALY" button instead.
    This prevents automatic API calls and gives users full control.
    
    To re-enable: Set ENABLE_AUTONOMOUS_MONITORING=true in environment
    """
    import os
    
    # Check if autonomous monitoring is enabled
    if os.getenv("ENABLE_AUTONOMOUS_MONITORING", "false").lower() != "true":
        logger.info("⏸️ Autonomous monitoring DISABLED (demo mode - use DEMO ANOMALY button)")
        return
    
    simulator = get_sensor_simulator()
    report_generator = get_report_generator()
    
    logger.info("🤖 Autonomous monitoring loop started")
    
    while True:
        try:
            # Get all equipment IDs
            equipment_ids = simulator.get_all_equipment_ids()
            
            for equipment_id in equipment_ids:
                # Get latest reading with anomaly check
                reading = simulator.get_latest_reading_with_anomaly(equipment_id)
                
                # Auto-generate report if CRITICAL or HIGH anomaly detected
                if reading and reading.get('has_anomaly'):
                    anomalies = reading.get('anomalies', [])
                    critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
                    high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
                    
                    if critical_count > 0 or high_count > 0:
                        logger.info(f"🚨 Autonomous: Critical anomaly on {equipment_id} - generating report")
                        await report_generator.process_sensor_reading(reading)
            
            # Check every 30 seconds
            await asyncio.sleep(30)
            
        except asyncio.CancelledError:
            logger.info("Autonomous monitoring loop cancelled")
            break
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            await asyncio.sleep(30)  # Continue despite errors


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
    
    # Start background autonomous monitoring
    monitoring_task = None
    try:
        monitoring_task = asyncio.create_task(autonomous_monitoring_loop())
        logger.info("✓ Autonomous monitoring started")
    except Exception as e:
        logger.error(f"Monitoring startup failed: {e}")
    
    logger.info("✓ Alloy Agent API ready\n")
    
    yield  # Application runs here
    
    # ── SHUTDOWN ─────────────────────────────────────────────────────
    logger.info("Shutting down Alloy Agent API...")
    if monitoring_task:
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        logger.info("✓ Autonomous monitoring stopped")
    logger.info("✓ Shutdown complete")


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
app.include_router(alerts_router)
app.include_router(historical_router)
app.include_router(spare_parts_router)
# app.include_router(feedback_router)  # Temporarily disabled

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
        async for reading in simulator.stream_readings(equipment_id, interval=15.0):
            # Send reading to client
            await websocket.send_json(reading)
            
            # Auto-generate reports if CRITICAL/HIGH anomalies detected
            if reading.get('has_anomaly'):
                anomalies = reading.get('anomalies', [])
                critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
                high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
                
                if critical_count > 0 or high_count > 0:
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
