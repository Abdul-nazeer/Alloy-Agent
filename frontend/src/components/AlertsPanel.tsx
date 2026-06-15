import { useEffect, useState } from 'react';
import { alertsAPI } from '../api/client';
import { X, Bell, CheckCircle, AlertTriangle } from 'lucide-react';

interface Alert {
  alert_id: string;
  equipment_id: string;
  equipment_name: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  title: string;
  message: string;
  report_id?: string;
  incident_id?: string;
  created_at: string;
}

interface AlertsPanelProps {
  onClose: () => void;
  onAlertUpdate: () => void;
}

export default function AlertsPanel({ onClose, onAlertUpdate }: AlertsPanelProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const response = await alertsAPI.getAll(50);
      setAlerts(response.data.alerts);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (alertId: string) => {
    try {
      await alertsAPI.markAsRead(alertId);
      setAlerts(alerts.filter(a => a.alert_id !== alertId));
      onAlertUpdate();
    } catch (err) {
      console.error('Failed to mark alert as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await alertsAPI.markAllAsRead();
      setAlerts([]);
      onAlertUpdate();
    } catch (err) {
      console.error('Failed to mark all as read:', err);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors = {
      CRITICAL: '#ef4444',
      HIGH: '#f97316',
      MEDIUM: '#eab308',
      LOW: '#3b82f6',
    };
    return colors[severity as keyof typeof colors] || '#3b82f6';
  };

  const getSeverityIcon = (severity: string) => {
    if (severity === 'CRITICAL' || severity === 'HIGH') {
      return <AlertTriangle className="w-4 h-4" />;
    }
    return <Bell className="w-4 h-4" />;
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div 
        className="flex items-center justify-between p-4 border-b"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <div className="flex items-center space-x-2">
          <Bell className="w-5 h-5" style={{ color: 'var(--accent-cyan)' }} />
          <h2 
            className="text-sm font-semibold font-sans"
            style={{ color: 'var(--text-primary)' }}
          >
            Alerts & Notifications
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-opacity-10 transition-all"
          style={{ color: 'var(--text-secondary)' }}
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Actions */}
      {alerts.length > 0 && (
        <div 
          className="px-4 py-2 border-b flex items-center justify-between"
          style={{ 
            borderColor: 'var(--border-default)',
            backgroundColor: 'rgba(0, 212, 170, 0.05)'
          }}
        >
          <span 
            className="text-xs font-mono"
            style={{ color: 'var(--text-secondary)' }}
          >
            {alerts.length} unread alert{alerts.length !== 1 ? 's' : ''}
          </span>
          <button
            onClick={handleMarkAllAsRead}
            className="text-xs font-mono hover:opacity-80 transition-all"
            style={{ color: 'var(--accent-cyan)' }}
          >
            Mark all as read
          </button>
        </div>
      )}

      {/* Alerts List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div 
            className="flex items-center justify-center h-32"
            style={{ color: 'var(--text-secondary)' }}
          >
            <span className="text-xs font-mono">Loading alerts...</span>
          </div>
        ) : alerts.length === 0 ? (
          <div 
            className="flex flex-col items-center justify-center h-32 space-y-2"
            style={{ color: 'var(--text-secondary)' }}
          >
            <CheckCircle className="w-8 h-8" style={{ color: 'var(--status-normal)' }} />
            <span className="text-xs font-mono">No unread alerts</span>
            <span className="text-2xs font-sans" style={{ color: 'var(--text-tertiary)' }}>
              All systems operating normally
            </span>
          </div>
        ) : (
          <div className="divide-y" style={{ borderColor: 'var(--border-subtle)' }}>
            {alerts.map((alert) => (
              <div
                key={alert.alert_id}
                className="p-4 hover:bg-opacity-5 transition-all cursor-pointer"
                style={{ 
                  backgroundColor: `${getSeverityColor(alert.severity)}05`,
                  borderLeft: `3px solid ${getSeverityColor(alert.severity)}`
                }}
                onClick={() => handleMarkAsRead(alert.alert_id)}
              >
                <div className="flex items-start space-x-3">
                  <div style={{ color: getSeverityColor(alert.severity) }}>
                    {getSeverityIcon(alert.severity)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <span
                        className="text-xs font-medium font-sans"
                        style={{ color: 'var(--text-primary)' }}
                      >
                        {alert.equipment_id}
                      </span>
                      <span
                        className="text-2xs font-mono px-1.5 py-0.5 rounded"
                        style={{
                          backgroundColor: `${getSeverityColor(alert.severity)}20`,
                          color: getSeverityColor(alert.severity)
                        }}
                      >
                        {alert.severity}
                      </span>
                    </div>
                    
                    <p
                      className="text-xs font-sans mb-1"
                      style={{ color: 'var(--text-secondary)' }}
                    >
                      {alert.message}
                    </p>
                    
                    <div className="flex items-center justify-between mt-2">
                      <span
                        className="text-2xs font-mono"
                        style={{ color: 'var(--text-tertiary)' }}
                      >
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                      
                      {alert.report_id && (
                        <span
                          className="text-2xs font-mono"
                          style={{ color: 'var(--accent-cyan)' }}
                        >
                          Report: {alert.report_id}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
