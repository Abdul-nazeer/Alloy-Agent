"""
Spare Parts Management Routes
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from backend.src.database.schema import get_connection

router = APIRouter(prefix="/spare-parts", tags=["spare-parts"])
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Models
# ══════════════════════════════════════════════════════════════════════════════

class SparePart(BaseModel):
    part_id: str
    part_name: str
    equipment_type: str
    quantity_available: int
    minimum_stock: int
    unit_cost: float
    lead_time_days: int
    supplier: str
    status: str
    criticality: str


class UpdateStockRequest(BaseModel):
    quantity: int
    operation: str  # "add" or "set"


# ══════════════════════════════════════════════════════════════════════════════
# Spare Parts CRUD
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/")
async def get_all_spare_parts(
    equipment_type: Optional[str] = None,
    status: Optional[str] = None,
    criticality: Optional[str] = None
):
    """
    Get all spare parts with optional filters.
    
    Query params:
    - equipment_type: Filter by equipment type
    - status: Filter by status (IN_STOCK, LOW_STOCK, OUT_OF_STOCK)
    - criticality: Filter by criticality (CRITICAL, HIGH, MEDIUM, LOW)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM spare_parts WHERE 1=1"
        params = []
        
        if equipment_type:
            query += " AND equipment_type = ?"
            params.append(equipment_type)
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if criticality:
            query += " AND criticality = ?"
            params.append(criticality)
        
        query += " ORDER BY CASE criticality WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 WHEN 'MEDIUM' THEN 3 ELSE 4 END, part_name"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        parts = [dict(row) for row in rows]
        
        # Calculate statistics
        total_parts = len(parts)
        out_of_stock = sum(1 for p in parts if p['status'] == 'OUT_OF_STOCK')
        low_stock = sum(1 for p in parts if p['status'] == 'LOW_STOCK')
        critical_parts = sum(1 for p in parts if p['criticality'] == 'CRITICAL')
        total_value = sum(p['quantity_available'] * p['unit_cost'] for p in parts)
        
        return {
            "status": "success",
            "count": total_parts,
            "statistics": {
                "total_parts": total_parts,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock,
                "critical_parts": critical_parts,
                "total_inventory_value": round(total_value, 2)
            },
            "parts": parts
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch spare parts: {e}")
        raise HTTPException(500, str(e))


@router.get("/{part_id}")
async def get_spare_part(part_id: str):
    """Get specific spare part by ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM spare_parts WHERE part_id = ?", (part_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(404, f"Part {part_id} not found")
        
        return {
            "status": "success",
            "part": dict(row)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch spare part: {e}")
        raise HTTPException(500, str(e))


@router.put("/{part_id}/stock")
async def update_spare_part_stock(part_id: str, request: UpdateStockRequest):
    """
    Update spare part stock quantity.
    
    Operations:
    - "add": Add to current quantity (e.g., new shipment received)
    - "set": Set to exact quantity (e.g., inventory correction)
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current quantity
        cursor.execute("SELECT quantity_available, minimum_stock FROM spare_parts WHERE part_id = ?", (part_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise HTTPException(404, f"Part {part_id} not found")
        
        current_qty = row['quantity_available']
        min_stock = row['minimum_stock']
        
        # Calculate new quantity
        if request.operation == "add":
            new_qty = current_qty + request.quantity
        elif request.operation == "set":
            new_qty = request.quantity
        else:
            conn.close()
            raise HTTPException(400, "Operation must be 'add' or 'set'")
        
        # Determine new status
        if new_qty == 0:
            new_status = "OUT_OF_STOCK"
        elif new_qty < min_stock:
            new_status = "LOW_STOCK"
        else:
            new_status = "IN_STOCK"
        
        # Update database
        cursor.execute("""
            UPDATE spare_parts 
            SET quantity_available = ?, status = ?
            WHERE part_id = ?
        """, (new_qty, new_status, part_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Updated stock for {part_id}: {current_qty} → {new_qty} ({new_status})")
        
        return {
            "status": "success",
            "part_id": part_id,
            "previous_quantity": current_qty,
            "new_quantity": new_qty,
            "new_status": new_status,
            "message": f"Stock updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update stock: {e}")
        raise HTTPException(500, str(e))


@router.get("/critical/alerts")
async def get_critical_parts_alerts():
    """
    Get all parts that need immediate attention.
    
    Returns parts that are:
    - OUT_OF_STOCK with CRITICAL or HIGH criticality
    - LOW_STOCK with CRITICAL criticality
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM spare_parts 
            WHERE (status = 'OUT_OF_STOCK' AND criticality IN ('CRITICAL', 'HIGH'))
               OR (status = 'LOW_STOCK' AND criticality = 'CRITICAL')
            ORDER BY 
                CASE criticality
                    WHEN 'CRITICAL' THEN 1
                    WHEN 'HIGH' THEN 2
                    ELSE 3
                END,
                lead_time_days DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        alerts = []
        for row in rows:
            part = dict(row)
            
            # Calculate urgency message
            if part['status'] == 'OUT_OF_STOCK':
                urgency = "IMMEDIATE"
                message = f"Out of stock - Order immediately (Lead time: {part['lead_time_days']} days)"
            else:
                urgency = "HIGH"
                message = f"Low stock ({part['quantity_available']} units) - Reorder soon"
            
            alerts.append({
                **part,
                "urgency": urgency,
                "alert_message": message,
                "procurement_priority": _calculate_procurement_priority(part)
            })
        
        return {
            "status": "success",
            "count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch critical parts alerts: {e}")
        raise HTTPException(500, str(e))


@router.get("/equipment/{equipment_type}")
async def get_parts_by_equipment(equipment_type: str):
    """Get all spare parts for a specific equipment type"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM spare_parts 
            WHERE equipment_type = ?
            ORDER BY criticality DESC, part_name
        """, (equipment_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        parts = [dict(row) for row in rows]
        
        return {
            "status": "success",
            "equipment_type": equipment_type,
            "count": len(parts),
            "parts": parts
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch parts for equipment: {e}")
        raise HTTPException(500, str(e))


# ══════════════════════════════════════════════════════════════════════════════
# Helper Functions
# ══════════════════════════════════════════════════════════════════════════════

def _calculate_procurement_priority(part: dict) -> int:
    """
    Calculate procurement priority score (1-10, higher = more urgent).
    
    Factors:
    - Criticality: CRITICAL=4, HIGH=3, MEDIUM=2, LOW=1
    - Status: OUT_OF_STOCK=4, LOW_STOCK=2, IN_STOCK=0
    - Lead time: >14 days=2, >7 days=1, else=0
    """
    score = 0
    
    # Criticality factor
    criticality_scores = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    score += criticality_scores.get(part.get('criticality', 'MEDIUM'), 2)
    
    # Status factor
    if part.get('status') == 'OUT_OF_STOCK':
        score += 4
    elif part.get('status') == 'LOW_STOCK':
        score += 2
    
    # Lead time factor
    lead_time = part.get('lead_time_days', 0)
    if lead_time > 14:
        score += 2
    elif lead_time > 7:
        score += 1
    
    return min(score, 10)  # Cap at 10
