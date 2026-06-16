import { useEffect, useState } from 'react';
import { equipmentAPI, type Equipment } from '../api/client';
import { Activity, Zap } from 'lucide-react';
import axios from 'axios';
import ProgressToast from './ProgressToast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://alloy-agent-production.up.railway.app';

interface DashboardProps {
  onEquipmentSelect: (equipmentId: string) => void;
  equipmentFilter: string;
  onNavigateToChat?: (message?: string) => void;
  onNavigateToReports?: () => void;
}

export default function Dashboard({ onEquipmentSelect, equipmentFilter, onNavigateToChat, onNavigateToReports }: DashboardProps) {
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [latestReadings, setLatestReadings] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<Record<string, boolean>>({});
  const [triggeringAnomaly, setTriggeringAnomaly] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [progressSteps, setProgressSteps] = useState<any[]>([]);
  const [currentEquipmentId, setCurrentEquipmentId] = useState<string>('');

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

  // Trigger demo anomaly function with progress visualization
  const triggerDemoAnomaly = async () => {
    try {
      setTriggeringAnomaly(true);
      setCurrentEquipmentId('AC-001');
      
      // Initialize progress steps
      const initialSteps = [
        { id: 'start', label: 'Starting analysis...', status: 'pending', icon: 'start' },
        { id: 'anomaly', label: 'Detecting anomalies...', status: 'pending', icon: 'anomaly', clickable: false },
        { id: 'diagnosis', label: 'Analyzing sensor data...', status: 'pending', icon: 'diagnosis', clickable: false },
        { id: 'recommendation', label: 'Generating recommendations...', status: 'pending', icon: 'recommendation', clickable: false },
        { id: 'report', label: 'Creating maintenance report...', status: 'pending', icon: 'report', clickable: false }
      ];
      
      setProgressSteps(initialSteps);
      setShowProgress(true);
      
      // Connect to progress stream
      const response = await fetch(`${API_BASE_URL}/api/agents/demo-progress/AC-001`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('✅ Progress stream complete');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue;
          
          try {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr) continue;
            
            const data = JSON.parse(jsonStr);
            
            console.log('📊 Progress update:', data);
            
            // Update progress steps
            setProgressSteps(prev => {
              return prev.map(step => {
                if (step.id === data.step) {
                  return {
                    ...step,
                    status: data.status,
                    label: data.label,
                    clickable: data.clickable || false,
                    redirectTo: data.redirectTo,
                    equipment_id: data.equipment_id,
                    message: data.message
                  };
                }
                return step;
              });
            });
            
          } catch (parseErr) {
            console.error('⚠️ Error parsing SSE line:', line, parseErr);
          }
        }
      }
      
    } catch (error) {
      console.error('❌ Failed to trigger demo anomaly:', error);
      alert('Failed to trigger demo anomaly. Please check backend connection.');
      setShowProgress(false);
    } finally {
      setTriggeringAnomaly(false);
    }
  };

  const handleProgressStepClick = (step: any) => {
    console.log('🔗 Progress step clicked:', step);
    
    if (!step.clickable || step.status !== 'complete') return;
    
    switch (step.redirectTo) {
      case 'equipment':
        // Navigate to equipment detail page
        if (step.equipment_id) {
          onEquipmentSelect(step.equipment_id);
          setShowProgress(false);
        }
        break;
        
      case 'chat':
        // Navigate to chat with optional message
        if (onNavigateToChat) {
          onNavigateToChat(step.message);
          setShowProgress(false);
        }
        break;
        
      case 'reports':
        // Navigate to reports page
        if (onNavigateToReports) {
          onNavigateToReports();
          setShowProgress(false);
        }
        break;
        
      default:
        console.warn('Unknown redirect target:', step.redirectTo);
    }
  };

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
    <div className="space-y-6">
      {/* Clean Page Header */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <Activity className="w-5 h-5" style={{ color: 'var(--accent-cyan)' }} />
            <h2 
              className="heading-primary text-base text-uppercase-spaced"
              style={{ color: 'var(--accent-cyan)' }}
            >
              LIVE MONITOR
            </h2>
            <span 
              className="text-2xs font-mono px-2 py-0.5 rounded"
              style={{ 
                backgroundColor: 'rgba(0, 229, 255, 0.1)',
                color: 'var(--text-tertiary)'
              }}
            >
              {filteredEquipment.length} MACHINES
            </span>
          </div>
          <p 
            className="text-mono text-xs"
            style={{ color: 'var(--text-tertiary)' }}
          >
            Real-time sensor data with automated fault detection
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Demo Anomaly Button - Compact */}
          <button
            onClick={triggerDemoAnomaly}
            disabled={triggeringAnomaly}
            className="px-3 py-2 rounded-sm text-2xs text-mono font-medium cursor-pointer hover-scale transition-smooth disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-1.5 glass-card"
            style={{
              border: '1px solid rgba(236, 72, 153, 0.4)',
              backgroundColor: 'rgba(236, 72, 153, 0.08)',
              color: '#ec4899'
            }}
          >
            <Zap className="w-3 h-3" />
            <span>{triggeringAnomaly ? 'TRIGGERING...' : 'DEMO ANOMALY'}</span>
          </button>
          
          {criticalCount > 0 && (
            <button
              onClick={() => {
                const criticalEquipment = equipment.find(e => e.status === 'CRITICAL');
                if (criticalEquipment) {
                  onEquipmentSelect(criticalEquipment.equipment_id);
                }
              }}
              className="px-3 py-2 rounded-sm text-2xs text-mono font-medium cursor-pointer hover-scale transition-smooth glass-card"
              style={{
                border: '1px solid rgba(239, 68, 68, 0.4)',
                backgroundColor: 'rgba(239, 68, 68, 0.08)',
                color: 'var(--accent-danger)'
              }}
            >
              <div className="flex items-center space-x-1.5">
                <span className="status-dot status-critical pulse-dot" style={{ width: '6px', height: '6px' }} />
                <span>{criticalCount} CRITICAL</span>
              </div>
            </button>
          )}
        </div>
      </div>

      {/* Premium Equipment Grid */}
      <div className="grid grid-cols-2 gap-4 mt-6">
        {filteredEquipment.map((item) => {
          const statusConfig = getStatusConfig(item.status);
          const reading = latestReadings[item.equipment_id];
          const isConnected = connectionStatus[item.equipment_id];
          
          return (
            <div
              key={item.equipment_id}
              onClick={() => onEquipmentSelect(item.equipment_id)}
              className="glass-card hover-lift transition-smooth cursor-pointer p-6 relative overflow-hidden"
            >
              {/* Holographic accent line */}
              <div 
                className="absolute top-0 left-0 right-0 h-1"
                style={{
                  background: `linear-gradient(90deg, ${statusConfig.dot}, transparent)`,
                  opacity: 0.6
                }}
              />
              
              {/* Status Indicators */}
              <div className="absolute top-4 right-4 flex items-center space-x-2">
                {isConnected && (
                  <div className="flex items-center space-x-1 glass-card px-2 py-1 rounded-full">
                    <span className="status-dot status-normal pulse-dot" style={{ width: '6px', height: '6px' }} />
                    <span className="text-2xs text-mono" style={{ color: 'var(--accent-cyan)' }}>
                      LIVE
                    </span>
                  </div>
                )}
                <span 
                  className="status-dot pulse-dot"
                  style={{ backgroundColor: statusConfig.dot, width: '10px', height: '10px' }}
                />
              </div>

              {/* Equipment Header */}
              <div className="mb-4">
                <div className="flex items-center space-x-3 mb-2">
                  <div className="p-2 rounded-lg glass-card-elevated">
                    <Activity className="w-5 h-5" style={{ color: 'var(--accent-cyan)' }} />
                  </div>
                  <div>
                    <h3 
                      className="heading-secondary text-lg text-mono"
                      style={{ color: 'var(--text-primary)' }}
                    >
                      {item.equipment_id}
                    </h3>
                    <p 
                      className="text-body text-xs"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {item.equipment_type}
                    </p>
                  </div>
                </div>
              </div>

              {/* Status Badge - Compact */}
              <div className="mb-4">
                <span 
                  className="inline-block px-2 py-0.5 rounded text-3xs text-mono text-uppercase-spaced font-medium"
                  style={{
                    border: `1px solid ${statusConfig.border}`,
                    backgroundColor: statusConfig.bg,
                    color: statusConfig.text
                  }}
                >
                  {item.status}
                </span>
              </div>

              {/* Live Sensor Values - Clean Professional Design */}
              <div className="grid grid-cols-3 gap-2 mb-3">
                {/* Vibration */}
                <div 
                  className="p-2 rounded-sm"
                  style={{ 
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: 'rgba(0, 229, 255, 0.03)'
                  }}
                >
                  <div className="text-3xs text-mono mb-0.5" style={{ color: 'var(--text-tertiary)' }}>
                    VIB
                  </div>
                  <div className="text-base text-mono font-semibold" style={{ color: 'var(--accent-cyan)' }}>
                    {reading?.vibration_mm_s?.toFixed(1) || '--'}
                  </div>
                  <div className="text-3xs text-mono" style={{ color: 'var(--text-muted)' }}>
                    mm/s
                  </div>
                </div>

                {/* Temperature */}
                <div 
                  className="p-2 rounded-sm"
                  style={{ 
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: 'rgba(255, 106, 0, 0.03)'
                  }}
                >
                  <div className="text-3xs text-mono mb-0.5" style={{ color: 'var(--text-tertiary)' }}>
                    TMP
                  </div>
                  <div className="text-base text-mono font-semibold" style={{ color: 'var(--accent-orange)' }}>
                    {reading?.temperature_c?.toFixed(1) || '--'}
                  </div>
                  <div className="text-3xs text-mono" style={{ color: 'var(--text-muted)' }}>
                    °C
                  </div>
                </div>

                {/* Current */}
                <div 
                  className="p-2 rounded-sm"
                  style={{ 
                    border: '1px solid var(--border-subtle)',
                    backgroundColor: 'rgba(34, 197, 94, 0.03)'
                  }}
                >
                  <div className="text-3xs text-mono mb-0.5" style={{ color: 'var(--text-tertiary)' }}>
                    CUR
                  </div>
                  <div className="text-base text-mono font-semibold" style={{ color: 'var(--accent-success)' }}>
                    {reading?.current_a?.toFixed(1) || '--'}
                  </div>
                  <div className="text-3xs text-mono" style={{ color: 'var(--text-muted)' }}>
                    A
                  </div>
                </div>
              </div>

              {/* Health Bar - Minimal */}
              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-3xs text-mono" style={{ color: 'var(--text-tertiary)' }}>
                    SYSTEM HEALTH
                  </span>
                  <span className="text-2xs text-mono font-medium" style={{ color: statusConfig.text }}>
                    {item.status === 'NORMAL' ? '98%' : item.status === 'LOW' ? '85%' : item.status === 'MEDIUM' ? '72%' : item.status === 'HIGH' ? '55%' : '35%'}
                  </span>
                </div>
                <div 
                  className="h-1 rounded-full overflow-hidden"
                  style={{ backgroundColor: 'var(--bg-elevated)' }}
                >
                  <div 
                    className="h-full transition-all duration-1000"
                    style={{ 
                      width: item.status === 'NORMAL' ? '98%' : item.status === 'LOW' ? '85%' : item.status === 'MEDIUM' ? '72%' : item.status === 'HIGH' ? '55%' : '35%',
                      background: statusConfig.dot
                    }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State - Premium Design */}
      {filteredEquipment.length === 0 && (
        <div className="glass-card text-center py-16 pattern-dots rounded-lg">
          <Activity className="w-16 h-16 mx-auto mb-4 opacity-30" style={{ color: 'var(--accent-cyan)' }} />
          <p 
            className="text-mono text-sm"
            style={{ color: 'var(--text-secondary)' }}
          >
            No equipment found for this filter
          </p>
        </div>
      )}

      {/* Progress Toast */}
      {showProgress && (
        <ProgressToast
          steps={progressSteps}
          onStepClick={handleProgressStepClick}
          onClose={() => setShowProgress(false)}
          title="Multi-Agent Analysis"
        />
      )}
    </div>
  );
}
