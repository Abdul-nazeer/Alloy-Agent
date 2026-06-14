import { useEffect, useState } from 'react';
import { sensorAPI, type SensorReading } from '../api/client';
import { LineChart, Line, CartesianGrid, ResponsiveContainer, XAxis } from 'recharts';
import { ArrowLeft } from 'lucide-react';
import ChatPanel from './ChatPanel';

interface EquipmentDetailProps {
  equipmentId: string;
  onBack: () => void;
}

export default function EquipmentDetail({ equipmentId, onBack }: EquipmentDetailProps) {
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [latest, setLatest] = useState<SensorReading | null>(null);
  const [loading, setLoading] = useState(true);

  // Load initial historical data
  useEffect(() => {
    loadHistoricalData();
  }, [equipmentId]);

  // Setup WebSocket for real-time updates
  useEffect(() => {
    console.log(`🔌 Setting up WebSocket for ${equipmentId}`);
    const ws = new WebSocket(`ws://localhost:8000/ws/sensors/${equipmentId}`);
    
    ws.onopen = () => {
      console.log(`✅ WebSocket connected: ${equipmentId}`);
    };

    ws.onmessage = (event) => {
      const reading = JSON.parse(event.data);
      console.log(`📡 Received real-time data for ${equipmentId}:`, reading);
      
      // Update latest reading
      setLatest(reading);
      
      // Add to readings array (keep last 100 points)
      setReadings(prev => {
        const updated = [...prev, reading].slice(-100);
        return updated;
      });
    };

    ws.onerror = (error) => {
      console.error(`❌ WebSocket error for ${equipmentId}:`, error);
    };

    ws.onclose = () => {
      console.log(`🔴 WebSocket closed for ${equipmentId}`);
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [equipmentId]);

  const loadHistoricalData = async () => {
    try {
      const historyRes = await sensorAPI.getHistory(equipmentId, 24);
      setReadings(historyRes.data);
      if (historyRes.data.length > 0) {
        setLatest(historyRes.data[historyRes.data.length - 1]);
      }
    } catch (err) {
      console.error('Failed to load historical data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
          Loading sensor data...
        </div>
      </div>
    );
  }

  const chartData = readings.map(r => ({
    time: new Date(r.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    temperature: r.temperature_c,
    pressure: r.pressure_bar,
    vibration: r.vibration_mm_s,
    current: r.current_a
  })).slice(-50);

  const chartConfig = {
    vibration: { label: 'Vibration (mm/s)', value: latest?.vibration_mm_s },
    temperature: { label: 'Bearing Temp (°C)', value: latest?.temperature_c },
    current: { label: 'Motor Current (A)', value: latest?.current_a },
    pressure: { label: 'Lube Pressure (bar)', value: latest?.pressure_bar }
  };

  return (
    <div className="flex flex-row h-full space-x-4">
      {/* Main Content Area */}
      <div className="flex-1 space-y-4 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={onBack}
              className="p-2 rounded-sm transition-all"
              style={{ 
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-default)',
                color: 'var(--text-secondary)'
              }}
            >
              <ArrowLeft className="w-4 h-4" />
            </button>
            <h2 
              className="text-xs font-mono tracking-widest"
              style={{ color: 'var(--accent-cyan)' }}
            >
              {equipmentId.toUpperCase()} — LIVE SENSOR TRENDS
            </h2>
          </div>
        </div>

        {/* Chart Grid */}
        <div className="grid grid-cols-2 gap-3 mt-4">
          {Object.entries(chartConfig).map(([key, config]) => (
            <div
              key={key}
              className="p-3 rounded-sm"
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: '1px solid var(--border-default)'
              }}
            >
              {/* Chart Header */}
              <div className="flex items-start justify-between mb-3">
                <h3 
                  className="text-xs font-mono"
                  style={{ color: 'var(--accent-cyan)' }}
                >
                  {config.label}
                </h3>
                <span 
                  className="text-2xl font-mono font-medium"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {config.value?.toFixed(1) || '--'}
                </span>
              </div>

              {/* Chart */}
              <ResponsiveContainer width="100%" height={120}>
                <LineChart data={chartData}>
                  <CartesianGrid 
                    stroke="var(--chart-grid)" 
                    strokeDasharray="3 3" 
                  />
                  <XAxis 
                    dataKey="time" 
                    stroke="var(--text-tertiary)"
                    tick={{ fontSize: 10, fontFamily: 'var(--font-mono)' }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Line
                    type="monotone"
                    dataKey={key}
                    stroke="var(--chart-line)"
                    strokeWidth={1.5}
                    dot={false}
                    isAnimationActive={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ))}
        </div>
      </div>

      {/* AI Assistant Side Panel */}
      <div 
        className="w-80 flex-shrink-0 rounded-sm overflow-hidden"
        style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-default)'
        }}
      >
        <ChatPanel compact={true} />
      </div>
    </div>
  );
}
