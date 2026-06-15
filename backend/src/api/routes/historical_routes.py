"""
Historical Data Import Routes - Equipment delays, failure reports, maintenance logs
"""

import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import csv
import io
from backend.src.database.schema import get_connection

router = APIRouter(prefix="/historical", tags=["historical"])
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Models
# ══════════════════════════════════════════════════════════════════════════════

class EquipmentDelay(BaseModel):
    equipment_id: str
    delay_date: str
    duration_hours: float
    reason: str
    impact: str
    resolved: bool = False


class FailureReport(BaseModel):
    equipment_id: str
    failure_date: str
    failure_type: str
    root_cause: str
    downtime_hours: float
    repair_cost: float
    parts_replaced: List[str]


class MaintenanceLog(BaseModel):
    equipment_id: str
    maintenance_date: str
    maintenance_type: str
    technician: str
    actions_taken: str
    parts_used: List[str]
    duration_hours: float


# ══════════════════════════════════════════════════════════════════════════════
# Equipment Delay Logs
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/delays/upload")
async def upload_delay_logs(file: UploadFile = File(...)):
    """
    Upload equipment delay logs (CSV or JSON format).
    
    CSV format: equipment_id, delay_date, duration_hours, reason, impact, resolved
    JSON format: Array of EquipmentDelay objects
    """
    try:
        # Validate file size (10MB limit)
        content = await file.read()
        if len(content) > 10_000_000:
            raise HTTPException(413, "File too large. Maximum 10MB allowed")
        
        if len(content) == 0:
            raise HTTPException(400, "Empty file uploaded")
        
        if file.filename.endswith('.csv'):
            delays = _parse_delay_csv(content)
        elif file.filename.endswith('.json'):
            delays = _parse_delay_json(content)
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or JSON")
        
        if len(delays) == 0:
            raise HTTPException(400, "No valid records found in file")
        
        # Store in database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equipment_delays (
                delay_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id TEXT NOT NULL,
                delay_date TEXT NOT NULL,
                duration_hours REAL NOT NULL,
                reason TEXT,
                impact TEXT,
                resolved INTEGER DEFAULT 0,
                imported_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        inserted = 0
        for delay in delays:
            cursor.execute("""
                INSERT INTO equipment_delays 
                (equipment_id, delay_date, duration_hours, reason, impact, resolved)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                delay.equipment_id,
                delay.delay_date,
                delay.duration_hours,
                delay.reason,
                delay.impact,
                1 if delay.resolved else 0
            ))
            inserted += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Imported {inserted} delay logs from {file.filename}")
        
        return {
            "status": "success",
            "records_imported": inserted,
            "message": f"Successfully imported {inserted} equipment delay records"
        }
        
    except Exception as e:
        logger.error(f"Failed to import delay logs: {e}")
        raise HTTPException(500, f"Import failed: {str(e)}")


@router.get("/delays")
async def get_delay_logs(equipment_id: Optional[str] = None, limit: int = 50):
    """Get equipment delay logs"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if equipment_id:
            cursor.execute("""
                SELECT * FROM equipment_delays 
                WHERE equipment_id = ?
                ORDER BY delay_date DESC
                LIMIT ?
            """, (equipment_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM equipment_delays 
                ORDER BY delay_date DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        delays = [dict(row) for row in rows]
        
        return {
            "status": "success",
            "count": len(delays),
            "delays": delays
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch delay logs: {e}")
        raise HTTPException(500, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# Failure Analysis Reports
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/failures/upload")
async def upload_failure_reports(file: UploadFile = File(...)):
    """
    Upload failure analysis reports (CSV or JSON format).
    
    CSV format: equipment_id, failure_date, failure_type, root_cause, downtime_hours, repair_cost, parts_replaced
    JSON format: Array of FailureReport objects
    """
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            failures = _parse_failure_csv(content)
        elif file.filename.endswith('.json'):
            failures = _parse_failure_json(content)
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or JSON")
        
        # Store in database
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS failure_reports (
                failure_id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_id TEXT NOT NULL,
                failure_date TEXT NOT NULL,
                failure_type TEXT NOT NULL,
                root_cause TEXT,
                downtime_hours REAL DEFAULT 0,
                repair_cost REAL DEFAULT 0,
                parts_replaced TEXT,
                imported_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        inserted = 0
        for failure in failures:
            cursor.execute("""
                INSERT INTO failure_reports 
                (equipment_id, failure_date, failure_type, root_cause, downtime_hours, repair_cost, parts_replaced)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                failure.equipment_id,
                failure.failure_date,
                failure.failure_type,
                failure.root_cause,
                failure.downtime_hours,
                failure.repair_cost,
                json.dumps(failure.parts_replaced)
            ))
            inserted += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Imported {inserted} failure reports from {file.filename}")
        
        return {
            "status": "success",
            "records_imported": inserted,
            "message": f"Successfully imported {inserted} failure analysis reports"
        }
        
    except Exception as e:
        logger.error(f"Failed to import failure reports: {e}")
        raise HTTPException(500, f"Import failed: {str(e)}")


@router.get("/failures")
async def get_failure_reports(equipment_id: Optional[str] = None, limit: int = 50):
    """Get failure analysis reports"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if equipment_id:
            cursor.execute("""
                SELECT * FROM failure_reports 
                WHERE equipment_id = ?
                ORDER BY failure_date DESC
                LIMIT ?
            """, (equipment_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM failure_reports 
                ORDER BY failure_date DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        failures = []
        for row in rows:
            failure_dict = dict(row)
            # Parse parts_replaced JSON
            if failure_dict.get('parts_replaced'):
                failure_dict['parts_replaced'] = json.loads(failure_dict['parts_replaced'])
            failures.append(failure_dict)
        
        return {
            "status": "success",
            "count": len(failures),
            "failures": failures
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch failure reports: {e}")
        raise HTTPException(500, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# Historical Maintenance Logs
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/maintenance/upload")
async def upload_maintenance_logs(file: UploadFile = File(...)):
    """
    Upload historical maintenance logs (CSV or JSON format).
    
    CSV format: equipment_id, maintenance_date, maintenance_type, technician, actions_taken, parts_used, duration_hours
    JSON format: Array of MaintenanceLog objects
    """
    try:
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            logs = _parse_maintenance_csv(content)
        elif file.filename.endswith('.json'):
            logs = _parse_maintenance_json(content)
        else:
            raise HTTPException(400, "Unsupported file format. Use CSV or JSON")
        
        # Store in logbook_entries table
        conn = get_connection()
        cursor = conn.cursor()
        
        inserted = 0
        for log in logs:
            entry_id = f"HIST-{log.equipment_id}-{datetime.now().timestamp()}"
            
            cursor.execute("""
                INSERT INTO logbook_entries 
                (entry_id, equipment_name, fault_description, risk_level, 
                 repair_steps, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                f"Historical: {log.equipment_id}",
                f"{log.maintenance_type} by {log.technician}",
                "HISTORICAL",
                log.actions_taken,
                log.maintenance_date,
                "CLOSED"
            ))
            inserted += 1
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Imported {inserted} maintenance logs from {file.filename}")
        
        return {
            "status": "success",
            "records_imported": inserted,
            "message": f"Successfully imported {inserted} historical maintenance records"
        }
        
    except Exception as e:
        logger.error(f"Failed to import maintenance logs: {e}")
        raise HTTPException(500, f"Import failed: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions - CSV Parsing
# ══════════════════════════════════════════════════════════════════════════════

def _parse_delay_csv(content: bytes) -> List[EquipmentDelay]:
    """Parse delay logs CSV with error handling"""
    delays = []
    
    try:
        # Try UTF-8 first, fallback to latin-1
        try:
            csv_text = content.decode('utf-8')
        except UnicodeDecodeError:
            csv_text = content.decode('latin-1')
        
        reader = csv.DictReader(io.StringIO(csv_text))
        
        # Validate headers
        required_fields = ['equipment_id', 'delay_date', 'duration_hours']
        if not all(field in reader.fieldnames for field in required_fields):
            raise ValueError(f"Missing required columns: {required_fields}")
        
        for row_num, row in enumerate(reader, start=2):
            try:
                delays.append(EquipmentDelay(
                    equipment_id=row['equipment_id'].strip(),
                    delay_date=row['delay_date'].strip(),
                    duration_hours=float(row['duration_hours']),
                    reason=row.get('reason', '').strip(),
                    impact=row.get('impact', '').strip(),
                    resolved=row.get('resolved', 'false').lower() == 'true'
                ))
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping row {row_num}: {e}")
                continue
    
    except Exception as e:
        raise ValueError(f"CSV parsing failed: {str(e)}")
    
    return delays


def _parse_failure_csv(content: bytes) -> List[FailureReport]:
    """Parse failure reports CSV"""
    failures = []
    csv_text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_text))
    
    for row in reader:
        parts = row.get('parts_replaced', '').split(';') if row.get('parts_replaced') else []
        failures.append(FailureReport(
            equipment_id=row['equipment_id'],
            failure_date=row['failure_date'],
            failure_type=row['failure_type'],
            root_cause=row.get('root_cause', ''),
            downtime_hours=float(row.get('downtime_hours', 0)),
            repair_cost=float(row.get('repair_cost', 0)),
            parts_replaced=parts
        ))
    
    return failures


def _parse_maintenance_csv(content: bytes) -> List[MaintenanceLog]:
    """Parse maintenance logs CSV"""
    logs = []
    csv_text = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_text))
    
    for row in reader:
        parts = row.get('parts_used', '').split(';') if row.get('parts_used') else []
        logs.append(MaintenanceLog(
            equipment_id=row['equipment_id'],
            maintenance_date=row['maintenance_date'],
            maintenance_type=row['maintenance_type'],
            technician=row.get('technician', 'Unknown'),
            actions_taken=row.get('actions_taken', ''),
            parts_used=parts,
            duration_hours=float(row.get('duration_hours', 0))
        ))
    
    return logs


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions - JSON Parsing
# ══════════════════════════════════════════════════════════════════════════════

def _parse_delay_json(content: bytes) -> List[EquipmentDelay]:
    """Parse delay logs JSON with validation"""
    try:
        data = json.loads(content)
        
        if not isinstance(data, list):
            raise ValueError("JSON must be an array of objects")
        
        if len(data) == 0:
            raise ValueError("JSON array is empty")
        
        delays = []
        for item in data:
            try:
                delays.append(EquipmentDelay(**item))
            except Exception as e:
                logger.warning(f"Skipping invalid record: {e}")
                continue
        
        return delays
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {str(e)}")


def _parse_failure_json(content: bytes) -> List[FailureReport]:
    """Parse failure reports JSON"""
    data = json.loads(content)
    return [FailureReport(**item) for item in data]


def _parse_maintenance_json(content: bytes) -> List[MaintenanceLog]:
    """Parse maintenance logs JSON"""
    data = json.loads(content)
    return [MaintenanceLog(**item) for item in data]
