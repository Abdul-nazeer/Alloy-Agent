import { useEffect, useState } from 'react';
import { equipmentAPI, type Equipment } from '../api/client';
import { Activity } from 'lucide-react';

interface DashboardProps {
  onEquipmentSelect: (equipmentId: string) => void;
  equipmentFilter: string;
}

export default function Dashboard({ onEquipmentSelect, equipmentFilter }: DashboardProps) {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadEquipment();
  }, []);

  // Setup WebSocket connections for real-time sensor data
  useEffect(() => {
    if (equipment.length === 0) return;

    console.log('🔌 Setting up WebSocket connections for', equipment.length, 'equipment');
    const websocketConnections: Record<string, WebSocket> = {};

    equipment.forEach((eq) => {
      const ws = new WebSocket(`ws://localhost:8000/ws/sensors/${eq.equipment_id}`);
      
      ws.onopen = () => {
        console.log(`✅ WebSocket connected: ${eq.equipment_id}`);
        setConnectionStatus(prev => ({ ...prev, [eq.equipment_id]: true }));
      };

      ws.onmessage = (event) => {
        const reading = JSON.parse(event.data);
        console.log(`📡 Received data for ${eq.equipment_id}:`, {
          temp: reading.temperature_c,
          vib: reading.vibration_mm_s,
          cur: reading.current_a
        });
        setLatestReadings(prev => ({
          ...prev,
          [eq.equipment_id]: reading
        }));
      };

      ws.onerror = (error) => {
        console.error(`❌ WebSocket error for ${eq.equipment_id}:`, error);
        setConnectionStatus(prev => ({ ...prev, [eq.equipment_id]: false }));
      };

      ws.onclose = () => {
        console.log(`🔴 WebSocket closed for ${eq.equipment_id}`);
        setConnectionStatus(prev => ({ ...prev, [eq.equipment_id]: false }));
      };

      websocketConnections[eq.equipment_id] = ws;
    });

    // Cleanup on unmount
    return () => {
      console.log('🧹 Cleaning up WebSocket connections');
      Object.values(websocketConnections).forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      });
    };
  }, [equipment]);

  const loadEquipment = async () => {
    try {
      const response = await equipmentAPI.getAll();
      setEquipment(response.data);
    } catch (err) {
      console.error('Failed to load equipment:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusConfig = (status: string) => {
    const configs = {
      CRITICAL: { bg: '#1a0a0a', border: '#ef444440', text: '#ef4444', dot: '#ef4444' },
      HIGH: { bg: '#1a0f05', border: '#f9731640', text: '#f97316', dot: '#f97316' },
      MEDIUM: { bg: '#1a1500', border: '#eab30840', text: '#eab308', dot: '#eab308' },
      LOW: { bg: '#050f1a', border: '#3b82f640', text: '#3b82f6', dot: '#3b82f6' },
      NORMAL: { bg: '#0a1a0a', border: '#22c55e40', text: '#22c55e', dot: '#22c55e' },
    };
    return configs[status as keyof typeof configs] || configs.NORMAL;
  };

  const filteredEquipment = equipmentFilter === 'All Equipment'
    ? equipment
    : equipment.filter(e => e.equipment_type === equipmentFilter);

  const criticalCount = equipment.filter(e => e.status === 'CRITICAL').length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
          Loading equipment data...
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Page Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 
            className="text-xs font-mono tracking-widest mb-1"
            style={{ color: 'var(--accent-cyan)' }}
          >
            🛰 LIVE MONITOR INTELLIGENCE
          </h2>
          <p 
            className="text-sm font-sans"
            style={{ color: 'var(--text-secondary)' }}
          >
            Equipment Status → {filteredEquipment.length} Machines Monitored
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          {criticalCount > 0 && (
            <button
              onClick={() => {
                // Navigate to the first critical equipment
                const criticalEquipment = equipment.find(e => e.status === 'CRITICAL');
                if (criticalEquipment) {
                  onEquipmentSelect(criticalEquipment.equipment_id);
                }
              }}
              className="px-3 py-1 rounded-sm text-xs font-mono cursor-pointer hover:opacity-80 transition-all"
              style={{
                border: '1px solid rgba(239, 68, 68, 0.4)',
                backgroundColor: 'rgba(239, 68, 68, 0.05)',
                color: '#ef4444'
              }}
            >
              ● {criticalCount} CRITICAL ALERT{criticalCount > 1 ? 'S' : ''}
            </button>
          )}
          <div 
            className="px-3 py-1 rounded-sm text-xs font-mono"
            style={{
              border: '1px solid rgba(34, 197, 94, 0.4)',
              backgroundColor: 'rgba(34, 197, 94, 0.05)',
              color: '#22c55e'
            }}
          >
            ● System Online
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div></div>
        <p 
          className="text-xs font-mono"
          style={{ color: 'var(--text-tertiary)' }}
        >
          UPDATED JUST NOW
        </p>
      </div>

      {/* Equipment Grid */}
      <div className="grid grid-cols-2 gap-3 mt-4">
        {filteredEquipment.map((item) => {
          const statusConfig = getStatusConfig(item.status);
          
          return (
            <div
              key={item.equipment_id}
              onClick={() => onEquipmentSelect(item.equipment_id)}
              className="relative p-4 rounded-sm cursor-pointer transition-all hover:border-opacity-60"
              style={{
                backgroundColor: 'var(--bg-surface)',
                border: `1px solid var(--border-default)`
              }}
            >
              {/* Status Dot */}
              <div className="absolute top-3 right-3 flex items-center space-x-2">
                {connectionStatus[item.equipment_id] && (
                  <span 
                    className="w-2 h-2 rounded-full block animate-pulse"
                    style={{ backgroundColor: 'var(--accent-cyan)' }}
                    title="Live streaming"
                  ></span>
                )}
                <span 
                  className="w-2 h-2 rounded-full block"
                  style={{ backgroundColor: statusConfig.dot }}
                ></span>
              </div>

              {/* Equipment Name */}
              <div className="flex items-center space-x-2 mb-1">
                <Activity className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
                <h3 
                  className="text-sm font-medium font-sans"
                  style={{ color: 'var(--text-primary)' }}
                >
                  {item.equipment_id}
                </h3>
              </div>

              <p 
                className="text-xs font-sans mb-3"
                style={{ color: 'var(--text-secondary)' }}
              >
                {item.equipment_type}
              </p>

              {/* Status Badge */}
              <div className="mb-3">
                <span 
                  className="inline-block px-2 py-0.5 rounded-sm text-2xs font-mono tracking-widest"
                  style={{
                    border: `1px solid ${statusConfig.border}`,
                    backgroundColor: statusConfig.bg,
                    color: statusConfig.text
                  }}
                >
                  {item.status}
                </span>
              </div>

              {/* Sensor Values Row */}
              <div 
                className="flex items-center space-x-4 text-xs font-mono"
                style={{ color: 'var(--text-secondary)' }}
              >
                <div>
                  <span style={{ color: 'var(--text-tertiary)' }}>VIB</span>{' '}
                  <span style={{ color: 'var(--text-primary)' }}>
                    {latestReadings[item.equipment_id]?.vibration_mm_s?.toFixed(1) || '--'}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)' }}>TMP</span>{' '}
                  <span style={{ color: 'var(--text-primary)' }}>
                    {latestReadings[item.equipment_id]?.temperature_c?.toFixed(1) || '--'}
                  </span>
                </div>
                <div>
                  <span style={{ color: 'var(--text-tertiary)' }}>CUR</span>{' '}
                  <span style={{ color: 'var(--text-primary)' }}>
                    {latestReadings[item.equipment_id]?.current_a?.toFixed(1) || '--'}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredEquipment.length === 0 && (
        <div 
          className="text-center py-12 rounded-sm"
          style={{ 
            backgroundColor: 'var(--bg-surface)', 
            border: '1px solid var(--border-default)' 
          }}
        >
          <p 
            className="text-sm font-mono"
            style={{ color: 'var(--text-secondary)' }}
          >
            No equipment found for this filter
          </p>
        </div>
      )}
    </div>
  );
}
