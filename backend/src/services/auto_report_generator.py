"""
Automatic Report Generation Service

Monitors sensor anomalies and automatically generates:
1. Analysis Reports when critical issues detected
2. Logbook entries for all maintenance events
3. Timestamps for full audit trail
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from backend.src.database.schema import get_connection
from backend.src.agents.agent_api import chat

logger = logging.getLogger(__name__)


class AutoReportGenerator:
    """
    Monitors equipment and generates reports automatically
    """
    
    def __init__(self):
        self.last_check = {}
        
    async def process_sensor_reading(self, sensor_data: Dict[str, Any]):
        """
        Process incoming sensor reading and auto-generate reports if needed
        
        Args:
            sensor_data: {
                equipment_id, equipment_type, timestamp,
                temperature_c, pressure_bar, vibration_mm_s, current_a,
                has_anomaly, anomalies: [{sensor, value, severity, message}]
            }
        """
        equipment_id = sensor_data.get('equipment_id')
        has_anomaly = sensor_data.get('has_anomaly', False)
        anomalies = sensor_data.get('anomalies', [])
        
        if not has_anomaly or not anomalies:
            return
        
        logger.info(f"🚨 Anomaly detected on {equipment_id}: {len(anomalies)} issues")
        
        # Check severity
        critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
        high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
        
        # Generate incident if critical or high severity
        if critical_count > 0 or high_count > 0:
            await self.create_incident_and_report(sensor_data, anomalies)
            await self.create_logbook_entry(sensor_data, anomalies)
    
    async def create_incident_and_report(self, sensor_data: Dict, anomalies: List[Dict]):
        """Create incident record and analysis report"""
        try:
            equipment_id = sensor_data['equipment_id']
            equipment_type = sensor_data['equipment_type']
            timestamp = sensor_data['timestamp']
            
            # Create incident ID
            incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
            
            # Store incident in database
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO incidents (incident_id, equipment_id, equipment_name, sensor_readings, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                incident_id,
                equipment_id,
                equipment_type,
                json.dumps(sensor_data),
                timestamp
            ))
            
            # Generate AI analysis report
            anomaly_description = "; ".join([a['message'] for a in anomalies[:3]])
            query = f"Analyze {equipment_type} {equipment_id} showing: {anomaly_description}"
            
            logger.info(f"🤖 Generating AI report for {incident_id}...")
            
            ai_response = chat(
                query=query,
                equipment_id=equipment_id,
                equipment_type=equipment_type,
                sensor_data={
                    'temperature_c': sensor_data.get('temperature_c'),
                    'pressure_bar': sensor_data.get('pressure_bar'),
                    'vibration_mm_s': sensor_data.get('vibration_mm_s'),
                    'current_a': sensor_data.get('current_a'),
                },
                user_role="supervisor"
            )
            
            # Determine report status based on risk level
            risk_level = ai_response.get('risk_level', 'MEDIUM')
            if risk_level == 'CRITICAL':
                status = 'critical'
            elif risk_level == 'HIGH':
                status = 'warning'
            else:
                status = 'normal'
            
            # Create report
            report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
            report_data = {
                "title": f"Equipment Health Alert - {equipment_id}",
                "risk_level": risk_level,
                "summary": f"{len(anomalies)} anomalies detected: {anomaly_description}",
                "content": ai_response.get('answer', ''),
                "recommendations": ai_response.get('recommendations', []),
                "root_causes": ai_response.get('root_causes', []),
                "agents_used": ai_response.get('agents_used', []),
                "anomalies": anomalies,
            }
            
            cursor.execute("""
                INSERT INTO reports (report_id, incident_id, report_data, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                report_id,
                incident_id,
                json.dumps(report_data),
                datetime.now().isoformat()
            ))
            
            # Create alert for frontend notification
            alert_id = f"ALERT-{uuid.uuid4().hex[:8].upper()}"
            alert_title = f"🚨 {risk_level} Alert: {equipment_id}"
            alert_message = f"{len(anomalies)} anomalies detected. Auto-report generated."
            
            cursor.execute("""
                INSERT INTO alerts (
                    alert_id, equipment_id, equipment_name, alert_type, 
                    severity, title, message, report_id, incident_id, 
                    is_read, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert_id,
                equipment_id,
                equipment_type,
                'anomaly_detected',
                risk_level,
                alert_title,
                alert_message,
                report_id,
                incident_id,
                0,  # unread
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Auto-generated report {report_id} for incident {incident_id}")
            logger.info(f"📢 Created alert {alert_id} for frontend notification")
            
        except Exception as e:
            logger.error(f"Failed to create incident report: {e}", exc_info=True)
    
    async def create_logbook_entry(self, sensor_data: Dict, anomalies: List[Dict]):
        """Create logbook entry for maintenance tracking"""
        try:
            equipment_id = sensor_data['equipment_id']
            equipment_type = sensor_data['equipment_type']
            timestamp = sensor_data['timestamp']
            
            entry_id = f"LOG-{uuid.uuid4().hex[:8].upper()}"
            
            # Determine risk level
            critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
            high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
            
            if critical_count > 0:
                risk_level = 'CRITICAL'
            elif high_count > 0:
                risk_level = 'HIGH'
            else:
                risk_level = 'MEDIUM'
            
            fault_description = f"Anomaly detected: {', '.join([a['message'] for a in anomalies[:2]])}"
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO logbook_entries (
                    entry_id, equipment_name, fault_description, risk_level, 
                    status, timestamp, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                f"{equipment_type} ({equipment_id})",
                fault_description,
                risk_level,
                'OPEN',
                timestamp,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created logbook entry {entry_id}")
            
        except Exception as e:
            logger.error(f"Failed to create logbook entry: {e}", exc_info=True)


# Singleton instance
_generator_instance = None

def get_report_generator() -> AutoReportGenerator:
    """Get or create auto report generator singleton"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = AutoReportGenerator()
    return _generator_instance
