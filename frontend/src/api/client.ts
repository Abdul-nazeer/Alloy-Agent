import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Equipment {
  equipment_id: string;
  equipment_type: string;
  location: string;
  install_date: string;
  last_maintenance: string;
  operating_hours: number;
  status: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'NORMAL';
}

export interface SensorReading {
  equipment_id: string;
  timestamp: string;
  temperature_c: number;
  pressure_bar: number;
  vibration_mm_s: number;
  current_a: number;
  rpm: number;
}

export interface TrendAnalysis {
  sensor: string;
  trend: 'increasing' | 'decreasing' | 'stable';
  change_rate: number;
  first_value: number;
  last_value: number;
  data_points: number;
  time_range_hours: number;
}

export interface MaintenanceLog {
  log_id: string;
  equipment_id: string;
  timestamp: string;
  event_type: string;
  description: string;
  parts_used: string;
  cost: number;
  downtime_hours: number;
  engineer: string;
}

export interface AgentResponse {
  answer: string;
  citations?: Array<{ source: string; page?: number }>;
  metadata?: {
    risk_level?: string;
    anomalies_detected?: number;
    agents_used?: string[];
    [key: string]: any;
  };
  session_id?: string;
  timestamp?: string;
}

// API Functions
export const equipmentAPI = {
  getAll: () => api.get<Equipment[]>('/api/sensors/equipment'),
  getById: (id: string) => api.get<Equipment>(`/api/sensors/equipment/${id}`),
  getHistory: (id: string, hours: number = 24) => 
    api.get<SensorReading[]>(`/api/sensors/equipment/${id}/history?hours=${hours}`),
  getLatest: (id: string) => api.get<SensorReading>(`/api/sensors/equipment/${id}/latest`),
  getTrend: (id: string, sensor: string, hours: number = 24) =>
    api.get<TrendAnalysis>(`/api/sensors/equipment/${id}/trend/${sensor}?hours=${hours}`),
};

export const maintenanceAPI = {
  getLogs: (equipmentId?: string, days: number = 30) => {
    const params = new URLSearchParams();
    if (equipmentId) params.append('equipment_id', equipmentId);
    params.append('days', days.toString());
    return api.get<MaintenanceLog[]>(`/api/sensors/maintenance/logs?${params}`);
  },
};

export const agentAPI = {
  chat: (message: string, sessionId?: string) =>
    api.post<AgentResponse>('/api/agents/chat', { message, session_id: sessionId }),
  
  checkAnomalies: (equipmentId: string, equipmentType: string, sensorData: any) =>
    api.post<AgentResponse>('/api/agents/check-anomalies', {
      equipment_id: equipmentId,
      equipment_type: equipmentType,
      sensor_data: sensorData,
    }),
  
  diagnose: (equipmentId: string, sensorData: any, symptoms?: string[]) =>
    api.post<AgentResponse>('/api/agents/diagnose', {
      equipment_id: equipmentId,
      sensor_data: sensorData,
      symptoms,
    }),
};

export const healthAPI = {
  getSystemHealth: () => api.get('/health'),
  getSensorHealth: () => api.get('/api/sensors/health'),
  getAgentHealth: () => api.get('/api/agents/health'),
};

export const reportsAPI = {
  getReports: (equipmentId?: string, days: number = 30) => {
    const params = new URLSearchParams();
    if (equipmentId) params.append('equipment_id', equipmentId);
    params.append('days', days.toString());
    return api.get(`/api/reports/list?${params}`);
  },
  
  getLogbook: (equipmentId?: string, status?: string, days: number = 30) => {
    const params = new URLSearchParams();
    if (equipmentId) params.append('equipment_id', equipmentId);
    if (status) params.append('status', status);
    params.append('days', days.toString());
    return api.get(`/api/reports/logbook?${params}`);
  },
  
  generateReport: (equipmentId: string, reportType: string = 'health_summary') =>
    api.post('/api/reports/generate', { equipment_id: equipmentId, report_type: reportType }),
};

// Named exports for convenience
export const getEquipment = equipmentAPI.getAll;
export const sensorAPI = {
  getHistory: equipmentAPI.getHistory,
  getLatest: equipmentAPI.getLatest,
};
