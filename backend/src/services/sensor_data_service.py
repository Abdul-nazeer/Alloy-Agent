"""
Sensor Data Service - Query synthetic historical sensor data and equipment specs
"""
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Path to synthetic data
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"

class SensorDataService:
    """Service for querying sensor data and equipment information"""
    
    def __init__(self):
        self.equipment_df = None
        self.sensor_df = None
        self.maintenance_df = None
        self._load_data()
    
    def _load_data(self):
        """Load CSV files into memory"""
        try:
            self.equipment_df = pd.read_csv(DATA_DIR / "equipment_specs.csv")
            self.sensor_df = pd.read_csv(DATA_DIR / "historical_sensor_data.csv")
            self.sensor_df['timestamp'] = pd.to_datetime(self.sensor_df['timestamp'])
            self.maintenance_df = pd.read_csv(DATA_DIR / "maintenance_logs.csv")
            self.maintenance_df['timestamp'] = pd.to_datetime(self.maintenance_df['timestamp'])
            print(f"✅ Loaded {len(self.equipment_df)} equipment, {len(self.sensor_df)} sensor readings, {len(self.maintenance_df)} maintenance logs")
        except Exception as e:
            print(f"⚠️ Error loading synthetic data: {e}")
            self.equipment_df = pd.DataFrame()
            self.sensor_df = pd.DataFrame()
            self.maintenance_df = pd.DataFrame()
    
    def get_all_equipment(self) -> List[Dict]:
        """Get all equipment specs"""
        if self.equipment_df.empty:
            return []
        return self.equipment_df.to_dict('records')
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict]:
        """Get specific equipment by ID"""
        if self.equipment_df.empty:
            return None
        result = self.equipment_df[self.equipment_df['equipment_id'] == equipment_id]
        if result.empty:
            return None
        return result.iloc[0].to_dict()
    
    def get_sensor_history(
        self, 
        equipment_id: str,
        hours: int = 24,
        end_time: Optional[datetime] = None
    ) -> List[Dict]:
        """Get sensor readings for equipment over last N hours"""
        if self.sensor_df.empty:
            return []
        
        # Filter by equipment
        equipment_data = self.sensor_df[self.sensor_df['equipment_id'] == equipment_id]
        
        if equipment_data.empty:
            return []
        
        # Time range filter
        if end_time is None:
            end_time = equipment_data['timestamp'].max()
        start_time = end_time - timedelta(hours=hours)
        
        time_filtered = equipment_data[
            (equipment_data['timestamp'] >= start_time) & 
            (equipment_data['timestamp'] <= end_time)
        ]
        
        # Convert to dict and ensure timestamp is string
        result = time_filtered.sort_values('timestamp').to_dict('records')
        for record in result:
            record['timestamp'] = str(record['timestamp'])
        
        return result
    
    def get_latest_reading(self, equipment_id: str) -> Optional[Dict]:
        """Get most recent sensor reading for equipment"""
        if self.sensor_df.empty:
            return None
        
        equipment_data = self.sensor_df[self.sensor_df['equipment_id'] == equipment_id]
        if equipment_data.empty:
            return None
        
        latest = equipment_data.sort_values('timestamp', ascending=False).iloc[0]
        result = latest.to_dict()
        result['timestamp'] = str(result['timestamp'])
        return result
    
    def get_maintenance_logs(
        self,
        equipment_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict]:
        """Get maintenance logs, optionally filtered by equipment"""
        if self.maintenance_df.empty:
            return []
        
        # Time filter
        cutoff = datetime.now() - timedelta(days=days)
        filtered = self.maintenance_df[self.maintenance_df['timestamp'] >= cutoff]
        
        # Equipment filter
        if equipment_id:
            filtered = filtered[filtered['equipment_id'] == equipment_id]
        
        # Convert to dict and ensure timestamp is string
        result = filtered.sort_values('timestamp', ascending=False).to_dict('records')
        for record in result:
            record['timestamp'] = str(record['timestamp'])
        
        return result
    
    def calculate_trend(
        self,
        equipment_id: str,
        sensor_name: str,
        hours: int = 24
    ) -> Dict:
        """Calculate trend for a specific sensor over time"""
        history = self.get_sensor_history(equipment_id, hours=hours)
        
        if not history:
            return {
                "sensor": sensor_name,
                "trend": "unknown",
                "change_rate": 0.0,
                "data_points": 0
            }
        
        df = pd.DataFrame(history)
        if sensor_name not in df.columns:
            return {
                "sensor": sensor_name,
                "trend": "unknown",
                "change_rate": 0.0,
                "data_points": 0
            }
        
        values = df[sensor_name].values
        if len(values) < 2:
            return {
                "sensor": sensor_name,
                "trend": "stable",
                "change_rate": 0.0,
                "data_points": len(values)
            }
        
        # Calculate linear trend
        first_val = values[0]
        last_val = values[-1]
        change = last_val - first_val
        change_rate = (change / first_val) * 100 if first_val != 0 else 0.0
        
        # Classify trend
        if abs(change_rate) < 2:
            trend = "stable"
        elif change_rate > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "sensor": sensor_name,
            "trend": trend,
            "change_rate": round(change_rate, 2),
            "first_value": round(first_val, 2),
            "last_value": round(last_val, 2),
            "data_points": len(values),
            "time_range_hours": hours
        }

# Singleton instance
_service_instance = None

def get_sensor_service() -> SensorDataService:
    """Get or create sensor data service singleton"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SensorDataService()
    return _service_instance
