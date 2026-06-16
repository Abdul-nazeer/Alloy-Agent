"""
Automatic Report Generation Service

Monitors sensor anomalies and automatically generates:
1. Analysis Reports when critical issues detected
2. Logbook entries for all maintenance events
3. Timestamps for full audit trail

API Usage Control:
- Set API_USAGE_MODE environment variable: "production" | "balanced" | "conservative"
- Default: "balanced" (optimized for free tier Groq API)
"""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from backend.src.database.schema import get_connection
from backend.src.agents.agent_api import chat
from backend.src.services.api_config import (
    get_cooldown_seconds, 
    should_use_ai_for_severity,
    is_caching_enabled,
    track_api_call,
    get_api_config
)

logger = logging.getLogger(__name__)

# Log API configuration on startup
_config = get_api_config()
logger.info(f"🔧 Auto-report generator initialized with mode: {_config['description']}")


class AutoReportGenerator:
    """
    Monitors equipment and generates reports automatically
    
    API Usage Modes (configured via API_USAGE_MODE env var):
    
    BALANCED (Default - Free Tier Optimized):
    - CRITICAL: 0s cooldown → AI report (immediate)
    - HIGH: 30min cooldown → AI report (with caching)
    - MEDIUM: 60min cooldown → Template report (no API)
    - LOW: No reports
    - Max: ~6 reports/hour
    
    PRODUCTION (High Quality):
    - CRITICAL: 0s → AI | HIGH: 10min → AI | MEDIUM: 30min → AI
    - Max: ~20 reports/hour
    
    CONSERVATIVE (Minimal API):
    - CRITICAL: 5min → AI | HIGH: 60min → Template | MEDIUM: 120min → Template
    - Max: ~3 reports/hour
    
    Set mode: export API_USAGE_MODE=balanced|production|conservative
    """
    
    def __init__(self):
        self.last_check = {}
        self.last_alert_time = {}  # Track when last alert was sent per equipment
        
        # Report cache to avoid duplicate AI calls for similar issues
        self.report_cache = {}  # equipment_id -> {anomaly_signature: cached_response}
        
    async def process_sensor_reading(self, sensor_data: Dict[str, Any]):
        """
        Process incoming sensor reading and auto-generate reports if needed
        
        Implements severity-based alert debouncing (optimized for free tier):
        - CRITICAL: No cooldown - generates AI report immediately every time
        - HIGH: 30-minute cooldown - AI report with response caching
        - MEDIUM: 1-hour cooldown - template-based report (no API calls)
        - LOW: No reports generated
        
        API Optimization:
        - Caches AI responses to avoid duplicate API calls for similar issues
        - Uses template generation for MEDIUM severity (saves ~3-5 API calls per report)
        - Only invokes multi-agent system for CRITICAL/HIGH severity
        
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
        
        # Determine highest severity level
        critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
        high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
        medium_count = sum(1 for a in anomalies if a.get('severity') == 'MEDIUM')
        
        if critical_count > 0:
            highest_severity = 'CRITICAL'
        elif high_count > 0:
            highest_severity = 'HIGH'
        elif medium_count > 0:
            highest_severity = 'MEDIUM'
        else:
            highest_severity = 'LOW'
        
        # Only generate reports for CRITICAL, HIGH, or MEDIUM severity
        if highest_severity == 'LOW':
            logger.info(f"⏭️ Skipping report generation for {equipment_id} - severity too low (LOW)")
            return
        
        # Check cooldown based on severity (uses configuration)
        current_time = datetime.now()
        last_alert = self.last_alert_time.get(equipment_id)
        cooldown_seconds = get_cooldown_seconds(highest_severity)
        
        if cooldown_seconds == 0:
            logger.info(f"🚨 {highest_severity} anomaly detected on {equipment_id} - bypassing cooldown for immediate AI report")
        elif last_alert:
            time_since_last_alert = (current_time - last_alert).total_seconds()
            if time_since_last_alert < cooldown_seconds:
                remaining = cooldown_seconds - time_since_last_alert
                logger.info(
                    f"⏸️ Cooldown active for {equipment_id} ({highest_severity}) - "
                    f"{int(remaining/60)} minutes {int(remaining%60)} seconds remaining until next report"
                )
                return
        
        # Update last alert time
        self.last_alert_time[equipment_id] = current_time
        
        # Check if AI should be used for this severity (based on configuration)
        use_ai_generation = should_use_ai_for_severity(highest_severity)
        
        logger.info(
            f"✅ Generating {highest_severity} report for {equipment_id} "
            f"(cooldown: {cooldown_seconds/60:.0f} min, AI: {use_ai_generation})"
        )
        
        # Generate incident if critical or high severity
        ai_response = await self.create_incident_and_report(sensor_data, anomalies, use_ai_generation)
        await self.create_logbook_entry(sensor_data, anomalies, ai_response)
    
    async def create_incident_and_report(self, sensor_data: Dict, anomalies: List[Dict], use_ai: bool = True):
        """
        Create incident record and analysis report
        
        Args:
            sensor_data: Sensor reading data
            anomalies: List of detected anomalies
            use_ai: If True, use AI generation (costs API calls). If False, use template (free)
        """
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
            
            # Determine severity for AI usage decision
            critical_count = sum(1 for a in anomalies if a.get('severity') == 'CRITICAL')
            high_count = sum(1 for a in anomalies if a.get('severity') == 'HIGH')
            
            if critical_count > 0:
                risk_level = 'CRITICAL'
            elif high_count > 0:
                risk_level = 'HIGH'
            else:
                risk_level = 'MEDIUM'
            
            # Use AI only for CRITICAL/HIGH to save API quota
            if use_ai and risk_level in ['CRITICAL', 'HIGH']:
                # Check cache first to avoid duplicate AI calls (if caching enabled)
                use_cache = is_caching_enabled()
                anomaly_signature = f"{equipment_id}_{anomaly_description}"
                cached_response = None
                
                if use_cache:
                    cached_response = self.report_cache.get(equipment_id, {}).get(anomaly_signature)
                
                if cached_response and use_cache:
                    logger.info(f"📦 Using cached AI response for {equipment_id} (saving API call)")
                    ai_response = cached_response
                else:
                    query = f"Analyze {equipment_type} {equipment_id} showing: {anomaly_description}"
                    
                    # Track API call for monitoring
                    call_count = track_api_call()
                    logger.info(f"🤖 Generating AI report for {incident_id} (API call #{call_count} this hour)")
                    
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
                    
                    # Cache the response if caching enabled
                    if use_cache:
                        if equipment_id not in self.report_cache:
                            self.report_cache[equipment_id] = {}
                        self.report_cache[equipment_id][anomaly_signature] = ai_response
                        
                        # Limit cache size (keep only last 5 responses per equipment)
                        if len(self.report_cache[equipment_id]) > 5:
                            oldest_key = list(self.report_cache[equipment_id].keys())[0]
                            del self.report_cache[equipment_id][oldest_key]
                
                risk_level = ai_response.get('risk_level', risk_level) or risk_level  # Ensure non-None
            else:
                # Use template-based response (no API calls)
                logger.info(f"📝 Generating template-based report for {incident_id} (no API call)")
                ai_response = self._create_template_response(
                    equipment_id, equipment_type, anomalies, sensor_data, risk_level
                )
            if risk_level == 'CRITICAL':
                status = 'critical'
            elif risk_level == 'HIGH':
                status = 'warning'
            else:
                status = 'normal'
            
            # Create report
            report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
            
            # Extract structured information
            recommendations = ai_response.get('recommendations', [])
            root_causes = ai_response.get('root_causes', [])
            
            # Build maintenance decision summaries for different roles
            supervisor_summary = _create_supervisor_summary(
                equipment_id, equipment_type, risk_level, anomalies, 
                root_causes, recommendations
            )
            
            engineer_summary = _create_engineer_summary(
                equipment_id, equipment_type, anomaly_description,
                sensor_data, root_causes, recommendations
            )
            
            report_data = {
                "title": f"Equipment Health Alert - {equipment_id}",
                "risk_level": risk_level,
                "summary": f"{len(anomalies)} anomalies detected: {anomaly_description}",
                "content": ai_response.get('answer', ''),  # Short summary for quick view
                "report_content": ai_response.get('report', ''),  # Full comprehensive markdown report
                "recommendations": recommendations,
                "root_causes": root_causes,
                "agents_used": ai_response.get('agents_used', []),
                "anomalies": anomalies,
                # Role-specific decision summaries
                "supervisor_summary": supervisor_summary,
                "engineer_summary": engineer_summary,
                # Metadata for traceability
                "incident_id": incident_id,
                "equipment_type": equipment_type,
                "timestamp": timestamp,
                "sensor_readings": {
                    'temperature_c': sensor_data.get('temperature_c'),
                    'pressure_bar': sensor_data.get('pressure_bar'),
                    'vibration_mm_s': sensor_data.get('vibration_mm_s'),
                    'current_a': sensor_data.get('current_a'),
                },
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
            
            # Ensure severity is never None
            alert_severity = risk_level if risk_level else 'MEDIUM'
            
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
                alert_severity,  # Use safeguarded value
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
            
            # Return ai_response so it can be passed to logbook creation
            return ai_response
            
        except Exception as e:
            logger.error(f"Failed to create incident report: {e}", exc_info=True)
            return None
    
    async def create_logbook_entry(self, sensor_data: Dict, anomalies: List[Dict], ai_response: Dict = None):
        """Create comprehensive logbook entry for maintenance tracking"""
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
            
            # Create comprehensive fault description with incident details
            fault_lines = [
                f"* **Equipment**: {equipment_type} ({equipment_id})",
                f"* **Alert**: {len(anomalies)} anomalies detected at {timestamp}",
                "",
                "**Current Sensor Readings:**"
            ]
            
            # Add sensor readings (skip internal fields)
            skip_fields = ['equipment_id', 'equipment_type', 'timestamp', 'has_anomaly', 'anomalies']
            for key, value in sensor_data.items():
                if key not in skip_fields and value is not None:
                    fault_lines.append(f"  - {key}: {value}")
            
            fault_lines.append("")
            fault_lines.append("**Anomalies:**")
            for anomaly in anomalies[:5]:  # Top 5 anomalies
                fault_lines.append(f"  - {anomaly.get('message', 'Unknown anomaly')}")
            
            fault_description = "\n".join(fault_lines)
            
            # Extract comprehensive data from AI response
            root_cause = "N/A"
            immediate_actions = "N/A"
            repair_steps = "N/A"
            long_term_recommendations = "N/A"
            
            if ai_response:
                # Root causes
                if ai_response.get('root_causes'):
                    root_causes_list = []
                    for i, rc in enumerate(ai_response['root_causes'][:3], 1):
                        cause_text = f"{i}. {rc.get('cause', 'Unknown')} ({int(rc.get('confidence', 0) * 100)}% confident)"
                        if rc.get('evidence'):
                            evidence = rc['evidence'] if isinstance(rc['evidence'], list) else [rc['evidence']]
                            cause_text += f"\n   Evidence: {', '.join(evidence[:2])}"
                        root_causes_list.append(cause_text)
                    root_cause = "\n".join(root_causes_list)
                
                # Immediate actions from recommendations
                if ai_response.get('recommendations'):
                    actions_list = []
                    for i, rec in enumerate(ai_response['recommendations'][:5], 1):
                        action = f"{i}. {rec.get('action', 'Unknown action')}"
                        if rec.get('estimated_time'):
                            action += f" (Est: {rec['estimated_time']})"
                        if rec.get('safety_notes'):
                            action += f"\n   ⚠️ Safety: {rec['safety_notes']}"
                        actions_list.append(action)
                    immediate_actions = "\n".join(actions_list)
                
                # Repair steps from report content
                if ai_response.get('report'):
                    report_content = ai_response['report']
                    # Extract repair procedure section if available
                    if "## REPAIR PROCEDURE" in report_content:
                        repair_start = report_content.find("## REPAIR PROCEDURE")
                        repair_end = report_content.find("##", repair_start + 20)
                        if repair_end == -1:
                            repair_end = len(report_content)
                        repair_steps = report_content[repair_start:repair_end].strip()[:1000]  # First 1000 chars
                    
                    # Extract long-term recommendations
                    if "## LONG-TERM RECOMMENDATIONS" in report_content:
                        long_start = report_content.find("## LONG-TERM RECOMMENDATIONS")
                        long_end = report_content.find("##", long_start + 30)
                        if long_end == -1:
                            long_end = len(report_content)
                        long_term_recommendations = report_content[long_start:long_end].strip()[:1000]
            
            # Estimate urgency in hours
            urgency_map = {'CRITICAL': 4, 'HIGH': 24, 'MEDIUM': 72, 'LOW': 168}
            urgency_hours = urgency_map.get(risk_level, 72)
            
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO logbook_entries (
                    entry_id, equipment_name, fault_description, root_cause,
                    risk_level, urgency_hours, immediate_actions, repair_steps,
                    long_term_recommendations, status, timestamp, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry_id,
                f"{equipment_type} ({equipment_id})",
                fault_description,
                root_cause,
                risk_level,
                urgency_hours,
                immediate_actions,
                repair_steps,
                long_term_recommendations,
                'OPEN',
                timestamp,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Created comprehensive logbook entry {entry_id}")
            
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


# ══════════════════════════════════════════════════════════════════════════════
# Role-Specific Decision Summary Builders
# ══════════════════════════════════════════════════════════════════════════════

def _create_supervisor_summary(
    equipment_id: str, 
    equipment_type: str, 
    risk_level: str,
    anomalies: List[Dict],
    root_causes: List,
    recommendations: List
) -> Dict[str, Any]:
    """
    Create executive summary for supervisors/managers
    
    Focus: Business impact, resource allocation, escalation decisions
    """
    # Calculate impact metrics
    downtime_risk = "IMMEDIATE" if risk_level == "CRITICAL" else "MODERATE" if risk_level == "HIGH" else "LOW"
    
    # Parts needed
    parts_needed = []
    procurement_required = False
    for rec in recommendations:
        if hasattr(rec, 'required_parts') and rec.required_parts:
            parts_needed.extend(rec.required_parts)
            procurement_required = True
    
    # Time estimate
    total_estimated_hours = 0
    for rec in recommendations:
        if hasattr(rec, 'estimated_time') and rec.estimated_time:
            # Parse estimated time (e.g., "2-4 hours")
            time_str = rec.estimated_time.lower()
            if 'hour' in time_str:
                nums = [int(s) for s in time_str.split() if s.isdigit()]
                if nums:
                    total_estimated_hours += nums[0]
            elif 'day' in time_str:
                nums = [int(s) for s in time_str.split() if s.isdigit()]
                if nums:
                    total_estimated_hours += nums[0] * 8  # 8 hours per day
    
    return {
        "role": "supervisor",
        "equipment": f"{equipment_type} - {equipment_id}",
        "risk_level": risk_level,
        "downtime_risk": downtime_risk,
        "requires_immediate_action": risk_level in ["CRITICAL", "HIGH"],
        "estimated_downtime_hours": total_estimated_hours if total_estimated_hours > 0 else "Unknown",
        "resource_requirements": {
            "parts_needed": list(set(parts_needed)),
            "procurement_required": procurement_required,
            "specialist_required": risk_level == "CRITICAL",
        },
        "business_impact": _assess_business_impact(risk_level, equipment_type),
        "recommended_escalation": "URGENT - Notify plant manager" if risk_level == "CRITICAL" else 
                                  "Prioritize for next shift" if risk_level == "HIGH" else 
                                  "Schedule within 24 hours",
        "summary_text": _format_supervisor_text(
            equipment_id, risk_level, anomalies, root_causes, 
            downtime_risk, procurement_required
        )
    }


def _create_engineer_summary(
    equipment_id: str,
    equipment_type: str,
    anomaly_description: str,
    sensor_data: Dict,
    root_causes: List,
    recommendations: List
) -> Dict[str, Any]:
    """
    Create technical summary for maintenance engineers
    
    Focus: Technical details, troubleshooting steps, safety considerations
    """
    # Extract sensor values
    sensor_summary = []
    for sensor_key, value in sensor_data.items():
        if value is not None and sensor_key not in ['equipment_id', 'equipment_type', 'timestamp', 'has_anomaly', 'anomalies']:
            sensor_summary.append({
                "parameter": sensor_key.replace('_', ' ').title(),
                "value": value,
                "status": "ABNORMAL" if any(sensor_key in a.get('message', '').lower() for a in sensor_data.get('anomalies', [])) else "NORMAL"
            })
    
    # Extract immediate actions
    immediate_actions = []
    followup_actions = []
    for rec in recommendations:
        if hasattr(rec, 'priority'):
            if rec.priority in ['P1', 'CRITICAL', 'HIGH']:
                immediate_actions.append({
                    "action": rec.action if hasattr(rec, 'action') else str(rec),
                    "estimated_time": getattr(rec, 'estimated_time', None),
                    "parts": getattr(rec, 'required_parts', [])
                })
            else:
                followup_actions.append({
                    "action": rec.action if hasattr(rec, 'action') else str(rec),
                    "estimated_time": getattr(rec, 'estimated_time', None),
                })
    
    # Safety considerations
    safety_notes = []
    if "pressure" in anomaly_description.lower() and "high" in anomaly_description.lower():
        safety_notes.append("⚠️ High pressure detected - Follow lockout/tagout procedures")
    if "temperature" in anomaly_description.lower() and ("high" in anomaly_description.lower() or "critical" in anomaly_description.lower()):
        safety_notes.append("⚠️ High temperature - Allow cooldown period before inspection")
    if "vibration" in anomaly_description.lower():
        safety_notes.append("⚠️ Excessive vibration - Check for loose components before operation")
    
    return {
        "role": "engineer",
        "equipment": f"{equipment_type} - {equipment_id}",
        "fault_summary": anomaly_description,
        "sensor_readings": sensor_summary,
        "probable_root_causes": [
            {
                "cause": rc.cause if hasattr(rc, 'cause') else str(rc),
                "confidence": f"{getattr(rc, 'confidence', 0)*100:.0f}%" if hasattr(rc, 'confidence') else "N/A",
                "evidence": getattr(rc, 'evidence', [])
            }
            for rc in root_causes[:3]  # Top 3 causes
        ],
        "immediate_actions": immediate_actions,
        "followup_actions": followup_actions,
        "safety_considerations": safety_notes,
        "tools_required": _extract_tools_from_recommendations(recommendations),
        "summary_text": _format_engineer_text(
            equipment_id, anomaly_description, sensor_summary,
            root_causes, immediate_actions
        )
    }


def _assess_business_impact(risk_level: str, equipment_type: str) -> str:
    """Assess business impact based on risk level and equipment criticality"""
    critical_equipment = ["Rolling Mill", "Blast Furnace", "Continuous Caster"]
    
    is_critical_equipment = any(equip.lower() in equipment_type.lower() for equip in critical_equipment)
    
    if risk_level == "CRITICAL":
        if is_critical_equipment:
            return "HIGH - Production line stoppage imminent. Potential losses >$100K/day"
        else:
            return "MEDIUM-HIGH - Support system failure may cause production delays"
    elif risk_level == "HIGH":
        if is_critical_equipment:
            return "MEDIUM-HIGH - Reduced production capacity. Schedule immediate maintenance"
        else:
            return "MEDIUM - May impact auxiliary operations"
    else:
        return "LOW - Minimal production impact. Schedule routine maintenance"


def _format_supervisor_text(
    equipment_id: str,
    risk_level: str,
    anomalies: List[Dict],
    root_causes: List,
    downtime_risk: str,
    procurement_required: bool
) -> str:
    """Format text summary for supervisors"""
    lines = [
        f"**MAINTENANCE DECISION SUMMARY (SUPERVISOR)**",
        f"",
        f"**Equipment:** {equipment_id}",
        f"**Risk Level:** {risk_level}",
        f"**Downtime Risk:** {downtime_risk}",
        f"",
        f"**Situation:**",
        f"{len(anomalies)} anomal{'ies' if len(anomalies) != 1 else 'y'} detected requiring attention.",
    ]
    
    if root_causes:
        top_cause = root_causes[0]
        cause_text = top_cause.cause if hasattr(top_cause, 'cause') else str(top_cause)
        lines.append(f"Root cause identified: {cause_text}")
    
    lines.append("")
    lines.append(f"**Decision Required:**")
    if risk_level == "CRITICAL":
        lines.append(f"✓ Authorize immediate maintenance (production halt may be required)")
        lines.append(f"✓ Notify plant manager and safety team")
    elif risk_level == "HIGH":
        lines.append(f"✓ Prioritize for next available maintenance window")
        lines.append(f"✓ Monitor equipment status continuously")
    else:
        lines.append(f"✓ Schedule maintenance within 24-48 hours")
    
    if procurement_required:
        lines.append(f"✓ Expedite spare parts procurement")
    
    return "\n".join(lines)


def _format_engineer_text(
    equipment_id: str,
    anomaly_description: str,
    sensor_summary: List[Dict],
    root_causes: List,
    immediate_actions: List[Dict]
) -> str:
    """Format text summary for engineers"""
    lines = [
        f"**MAINTENANCE DECISION SUMMARY (ENGINEER)**",
        f"",
        f"**Equipment:** {equipment_id}",
        f"**Fault:** {anomaly_description}",
        f"",
        f"**Sensor Status:**",
    ]
    
    for sensor in sensor_summary[:4]:  # Top 4 sensors
        status_icon = "🔴" if sensor["status"] == "ABNORMAL" else "🟢"
        lines.append(f"  {status_icon} {sensor['parameter']}: {sensor['value']}")
    
    if root_causes:
        lines.append("")
        lines.append(f"**Probable Root Cause:**")
        top_cause = root_causes[0]
        cause_text = top_cause.cause if hasattr(top_cause, 'cause') else str(top_cause)
        confidence = f"{getattr(top_cause, 'confidence', 0)*100:.0f}%" if hasattr(top_cause, 'confidence') else "N/A"
        lines.append(f"  {cause_text} (Confidence: {confidence})")
    
    if immediate_actions:
        lines.append("")
        lines.append(f"**Immediate Actions Required:**")
        for i, action in enumerate(immediate_actions[:3], 1):
            lines.append(f"  {i}. {action['action']}")
            if action.get('estimated_time'):
                lines.append(f"     Time: {action['estimated_time']}")
    
    return "\n".join(lines)


def _extract_tools_from_recommendations(recommendations: List) -> List[str]:
    """Extract required tools from recommendations"""
    tools = []
    tool_keywords = {
        "wrench": "Wrench set",
        "torque": "Torque wrench",
        "multimeter": "Multimeter",
        "inspect": "Inspection tools",
        "thermography": "Thermal camera",
        "vibration": "Vibration analyzer",
        "pressure": "Pressure gauge",
        "oil": "Oil analysis kit",
    }
    
    for rec in recommendations:
        rec_text = rec.action.lower() if hasattr(rec, 'action') else str(rec).lower()
        for keyword, tool in tool_keywords.items():
            if keyword in rec_text and tool not in tools:
                tools.append(tool)
    
    return tools if tools else ["Standard maintenance toolkit"]


def _create_template_response(
    self, 
    equipment_id: str, 
    equipment_type: str, 
    anomalies: List[Dict],
    sensor_data: Dict,
    risk_level: str
) -> Dict[str, Any]:
    """
    Create template-based response without AI (saves API calls)
    
    Used for MEDIUM severity alerts where AI analysis is not critical
    """
    # Generate basic recommendations based on anomaly patterns
    recommendations = []
    root_causes = []
    
    for anomaly in anomalies:
        sensor = anomaly.get('sensor', '').lower()
        severity = anomaly.get('severity', 'MEDIUM')
        
        # Temperature anomalies
        if 'temperature' in sensor:
            root_causes.append({
                'cause': 'Elevated operating temperature detected',
                'confidence': 0.75,
                'evidence': [anomaly.get('message', 'Temperature out of range')]
            })
            recommendations.append({
                'action': 'Inspect cooling system and verify ambient conditions',
                'priority': 'P2',
                'estimated_time': '1-2 hours',
                'required_parts': ['Coolant', 'Filters']
            })
        
        # Pressure anomalies
        elif 'pressure' in sensor:
            root_causes.append({
                'cause': 'Pressure deviation from normal operating range',
                'confidence': 0.70,
                'evidence': [anomaly.get('message', 'Pressure abnormal')]
            })
            recommendations.append({
                'action': 'Check pressure relief valves and seals',
                'priority': 'P2',
                'estimated_time': '1-2 hours',
                'required_parts': ['Seals', 'Gaskets']
            })
        
        # Vibration anomalies
        elif 'vibration' in sensor:
            root_causes.append({
                'cause': 'Mechanical imbalance or misalignment detected',
                'confidence': 0.80,
                'evidence': [anomaly.get('message', 'Vibration excessive')]
            })
            recommendations.append({
                'action': 'Perform vibration analysis and check bearing condition',
                'priority': 'P2',
                'estimated_time': '2-3 hours',
                'required_parts': ['Bearings']
            })
        
        # Current anomalies
        elif 'current' in sensor:
            root_causes.append({
                'cause': 'Electrical load variation or motor inefficiency',
                'confidence': 0.70,
                'evidence': [anomaly.get('message', 'Current abnormal')]
            })
            recommendations.append({
                'action': 'Inspect motor windings and connections',
                'priority': 'P2',
                'estimated_time': '1-2 hours',
                'required_parts': []
            })
    
    # Default if no specific pattern matched
    if not recommendations:
        recommendations.append({
            'action': 'Perform routine inspection and verify operating parameters',
            'priority': 'P3',
            'estimated_time': '1 hour',
            'required_parts': []
        })
    
    # Generate answer text
    answer = f"""**{equipment_type} {equipment_id} Analysis**

**Risk Level:** {risk_level}

**Anomalies Detected:** {len(anomalies)} issue(s) identified requiring attention.

**Assessment:**
{chr(10).join([f"- {a['message']}" for a in anomalies[:3]])}

**Recommended Actions:**
{chr(10).join([f"{i}. {r['action']}" for i, r in enumerate(recommendations, 1)])}

**Note:** This is a template-based analysis. For critical issues, contact maintenance supervisor for detailed assessment.
"""
    
    return {
        'answer': answer,
        'risk_level': risk_level,
        'recommendations': recommendations,
        'root_causes': root_causes,
        'agents_used': ['template_generator'],
    }
