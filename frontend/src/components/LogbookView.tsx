import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, RefreshCw } from 'lucide-react';
import { reportsAPI } from '../api/client';

interface LogEntry {
  id: string;
  equipment: string;
  timestamp: string;
  root_cause: string;
  risk: string;
  status: string;
  notes: string;
  details?: {
    alert?: string;
    fault?: string;
    actions?: string[];
  };
}

export default function LogbookView() {
  const [entries, setEntries] = useState<LogEntry[]>([]);
  const [expandedEntry, setExpandedEntry] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [equipmentFilter, setEquipmentFilter] = useState<string>('All Equipment');

  useEffect(() => {
    loadLogbook();
    const interval = setInterval(loadLogbook, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLogbook = async () => {
    try {
      const response = await reportsAPI.getLogbook(undefined, undefined, 30);
      const rawEntries = response.data.entries || [];
      
      // Transform to match production format
      const transformed = rawEntries.map((e: any) => ({
        id: e.id,
        equipment: e.equipment,
        timestamp: e.time,
        root_cause: e.notes.split(':')[0] || 'Anomaly detected',
        risk: e.type === 'alert' ? 'HIGH' : 'MEDIUM',
        status: e.status || 'OPEN',
        notes: e.notes,
        details: {
          alert: e.type === 'alert' ? 'N/A' : undefined,
          fault: e.notes,
          actions: []
        }
      }));
      
      setEntries(transformed);
    } catch (error) {
      console.error('Failed to load logbook:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    const colors = {
      HIGH: '#ef4444',
      MEDIUM: '#eab308',
      LOW: '#22c55e'
    };
    return colors[risk as keyof typeof colors] || colors.MEDIUM;
  };

  const getStatusColor = (status: string) => {
    return status === 'OPEN' ? '#ef4444' : '#22c55e';
  };

  const filteredEntries = equipmentFilter === 'All Equipment'
    ? entries
    : entries.filter(e => e.equipment.includes(equipmentFilter));

  const uniqueEquipment = ['All Equipment', ...new Set(entries.map(e => {
    const match = e.equipment.match(/\(([^)]+)\)/);
    return match ? match[1] : e.equipment;
  }))];

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-mono tracking-widest" style={{ color: 'var(--accent-cyan)' }}>
          📋 MAINTENANCE LOGBOOK
        </h2>
        <button
          onClick={loadLogbook}
          disabled={loading}
          className="p-1.5 rounded-sm transition-all"
          style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            color: 'var(--accent-cyan)'
          }}
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Filter */}
      <div className="mb-3">
        <select
          value={equipmentFilter}
          onChange={(e) => setEquipmentFilter(e.target.value)}
          className="w-full px-3 py-2 text-xs font-mono rounded-sm"
          style={{
            backgroundColor: 'var(--bg-elevated)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)'
          }}
        >
          {uniqueEquipment.map(eq => (
            <option key={eq} value={eq}>{eq}</option>
          ))}
        </select>
      </div>

      <div className="text-xs font-mono mb-3" style={{ color: 'var(--text-tertiary)' }}>
        {filteredEntries.length} entries
      </div>

      {/* Table */}
      <div className="flex-1 overflow-hidden">
        {loading ? (
          <div className="text-center py-12">
            <p className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>Loading...</p>
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="text-center py-12 rounded-sm" style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
            <p className="text-sm font-mono" style={{ color: 'var(--text-secondary)' }}>No logbook entries yet</p>
            <p className="text-xs font-sans mt-1" style={{ color: 'var(--text-tertiary)' }}>Entries auto-create when anomalies detected</p>
          </div>
        ) : (
          <div className="rounded-sm overflow-hidden" style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
            {/* Table Header */}
            <div 
              className="grid grid-cols-12 gap-2 px-4 py-2 border-b text-2xs font-mono uppercase"
              style={{ 
                backgroundColor: 'var(--bg-elevated)',
                borderColor: 'var(--border-default)',
                color: 'var(--text-tertiary)'
              }}
            >
              <div className="col-span-3">Equipment</div>
              <div className="col-span-2">Timestamp</div>
              <div className="col-span-4">Root Cause</div>
              <div className="col-span-1">Risk</div>
              <div className="col-span-2">Status</div>
            </div>

            {/* Table Body */}
            <div className="overflow-y-auto" style={{ maxHeight: 'calc(100vh - 280px)' }}>
              {filteredEntries.map((entry) => (
                <div key={entry.id}>
                  {/* Main Row */}
                  <div
                    onClick={() => setExpandedEntry(expandedEntry === entry.id ? null : entry.id)}
                    className="grid grid-cols-12 gap-2 px-4 py-3 border-b cursor-pointer hover:bg-opacity-50 transition-all"
                    style={{ 
                      borderColor: 'var(--border-subtle)',
                      backgroundColor: expandedEntry === entry.id ? 'var(--bg-elevated)' : 'transparent'
                    }}
                  >
                    <div className="col-span-3 flex items-center space-x-2">
                      {expandedEntry === entry.id ? (
                        <ChevronDown className="w-3 h-3" style={{ color: 'var(--text-tertiary)' }} />
                      ) : (
                        <ChevronRight className="w-3 h-3" style={{ color: 'var(--text-tertiary)' }} />
                      )}
                      <span className="text-sm font-sans" style={{ color: 'var(--text-primary)' }}>
                        {entry.equipment}
                      </span>
                    </div>
                    <div className="col-span-2 text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                      {new Date(entry.timestamp).toLocaleString('en-US', { 
                        month: 'short', 
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      }).replace(',', '')}
                    </div>
                    <div className="col-span-4 text-sm font-sans" style={{ color: 'var(--text-secondary)' }}>
                      {entry.root_cause}
                    </div>
                    <div className="col-span-1">
                      <span
                        className="px-2 py-0.5 rounded-sm text-2xs font-mono"
                        style={{
                          backgroundColor: `${getRiskColor(entry.risk)}20`,
                          color: getRiskColor(entry.risk)
                        }}
                      >
                        {entry.risk}
                      </span>
                    </div>
                    <div className="col-span-2">
                      <span
                        className="px-2 py-0.5 rounded-sm text-2xs font-mono"
                        style={{
                          backgroundColor: `${getStatusColor(entry.status)}20`,
                          color: getStatusColor(entry.status)
                        }}
                      >
                        {entry.status}
                      </span>
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedEntry === entry.id && (
                    <div 
                      className="px-4 py-4 border-b space-y-3"
                      style={{ 
                        backgroundColor: 'var(--bg-base)',
                        borderColor: 'var(--border-subtle)'
                      }}
                    >
                      <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--accent-cyan)' }}>
                        Incident Details
                      </div>

                      {entry.details?.alert && (
                        <div>
                          <div className="text-xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>Alert:</div>
                          <div className="text-sm font-sans" style={{ color: 'var(--text-primary)' }}>{entry.details.alert}</div>
                        </div>
                      )}

                      <div>
                        <div className="text-xs font-mono mb-1" style={{ color: 'var(--text-tertiary)' }}>Fault:</div>
                        <div className="text-sm font-sans leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                          {entry.notes}
                        </div>
                      </div>

                      {entry.details?.actions && entry.details.actions.length > 0 && (
                        <div>
                          <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                            Immediate Actions
                          </div>
                          <ol className="list-decimal list-inside space-y-1">
                            {entry.details.actions.map((action, i) => (
                              <li key={i} className="text-sm font-sans" style={{ color: 'var(--text-secondary)' }}>
                                {action}
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
