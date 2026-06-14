import { useState, useEffect } from 'react';
import { Download, RefreshCw, X } from 'lucide-react';
import { reportsAPI } from '../api/client';

interface Report {
  id: string;
  equipment_id: string;
  equipment_name: string;
  title: string;
  status: 'critical' | 'warning' | 'normal';
  findings: string;
  content: any;
  date: string;
}

export default function ReportsView() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [equipmentFilter, setEquipmentFilter] = useState<string>('All Equipment');

  useEffect(() => {
    loadReports();
    const interval = setInterval(loadReports, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadReports = async () => {
    try {
      const response = await reportsAPI.getReports(undefined, 30);
      setReports(response.data.reports || []);
    } catch (error) {
      console.error('Failed to load reports:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (status: string) => {
    const colors = {
      critical: '#ef4444',
      warning: '#f97316',
      normal: '#22c55e'
    };
    return colors[status as keyof typeof colors] || colors.normal;
  };

  const exportAllReports = () => {
    const markdown = reports.map(r => `# ${r.title}\n\n${typeof r.content === 'string' ? r.content : JSON.stringify(r.content, null, 2)}\n\n---\n\n`).join('');
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `all-reports-${new Date().toISOString().split('T')[0]}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredReports = equipmentFilter === 'All Equipment' 
    ? reports 
    : reports.filter(r => r.equipment_id === equipmentFilter);

  const uniqueEquipment = ['All Equipment', ...new Set(reports.map(r => r.equipment_id))];

  return (
    <div className="flex h-full">
      {/* Reports List */}
      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xs font-mono tracking-widest" style={{ color: 'var(--accent-cyan)' }}>
            📊 ANALYSIS REPORTS
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={exportAllReports}
              disabled={reports.length === 0}
              className="px-3 py-1 text-xs font-mono rounded-sm transition-all disabled:opacity-50"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                color: 'var(--accent-cyan)'
              }}
            >
              <Download className="w-3 h-3 inline mr-1" />
              EXPORT ALL
            </button>
            <button
              onClick={loadReports}
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
          {filteredReports.length} entries
        </div>

        {/* Reports List */}
        <div className="flex-1 overflow-y-auto space-y-2">
          {loading ? (
            <div className="text-center py-12">
              <p className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>Loading...</p>
            </div>
          ) : filteredReports.length === 0 ? (
            <div className="text-center py-12 rounded-sm" style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}>
              <p className="text-sm font-mono" style={{ color: 'var(--text-secondary)' }}>No reports yet</p>
              <p className="text-xs font-sans mt-1" style={{ color: 'var(--text-tertiary)' }}>Reports auto-generate when anomalies detected</p>
            </div>
          ) : (
            filteredReports.map(report => (
              <div
                key={report.id}
                onClick={() => setSelectedReport(report)}
                className="p-3 rounded-sm cursor-pointer transition-all hover:border-opacity-70"
                style={{
                  backgroundColor: selectedReport?.id === report.id ? 'var(--bg-elevated)' : 'var(--bg-surface)',
                  border: `1px solid ${selectedReport?.id === report.id ? 'var(--accent-cyan)' : 'var(--border-default)'}`
                }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-sm font-sans mb-1" style={{ color: 'var(--text-primary)' }}>
                      {report.equipment_name || report.equipment_id}
                    </div>
                    <div className="text-xs font-sans" style={{ color: 'var(--text-secondary)' }}>
                      {report.findings}
                    </div>
                  </div>
                  <span
                    className="px-2 py-0.5 rounded-sm text-2xs font-mono uppercase"
                    style={{
                      backgroundColor: `${getRiskColor(report.status)}20`,
                      color: getRiskColor(report.status)
                    }}
                  >
                    {report.status}
                  </span>
                </div>
                <div className="text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                  {new Date(report.date).toLocaleString()}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Report Detail Panel */}
      {selectedReport && (
        <div 
          className="w-2/3 ml-4 flex flex-col rounded-sm overflow-hidden"
          style={{ backgroundColor: 'var(--bg-surface)', border: '1px solid var(--border-default)' }}
        >
          {/* Header */}
          <div className="p-4 border-b flex items-start justify-between" style={{ borderColor: 'var(--border-default)' }}>
            <div className="flex-1">
              <div className="text-lg font-sans mb-1" style={{ color: 'var(--text-primary)' }}>
                {selectedReport.title}
              </div>
              <div className="flex items-center space-x-3 text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                <span>Equipment ID: {selectedReport.equipment_id}</span>
                <span>•</span>
                <span>Incident ID: {selectedReport.id}</span>
              </div>
              <div className="text-xs font-mono mt-1" style={{ color: 'var(--text-tertiary)' }}>
                Generated: {new Date(selectedReport.date).toLocaleString('en-US', { 
                  month: 'short', 
                  day: 'numeric', 
                  year: 'numeric', 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}
              </div>
            </div>
            <button
              onClick={() => setSelectedReport(null)}
              className="p-1 rounded-sm"
              style={{ color: 'var(--text-secondary)' }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Risk Level */}
            <div>
              <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                Risk Level:
              </div>
              <span
                className="inline-block px-3 py-1 rounded-sm text-xs font-mono uppercase"
                style={{
                  backgroundColor: `${getRiskColor(selectedReport.status)}20`,
                  color: getRiskColor(selectedReport.status)
                }}
              >
                {selectedReport.status}
              </span>
            </div>

            {/* Root Cause Analysis */}
            <div>
              <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                Root Cause Analysis
              </div>
              <div className="text-sm font-sans leading-relaxed" style={{ color: 'var(--text-primary)' }}>
                {typeof selectedReport.content === 'string' ? selectedReport.content : selectedReport.findings}
              </div>
              {selectedReport.content?.root_causes && (
                <div className="mt-2 space-y-2">
                  {selectedReport.content.root_causes.map((cause: any, i: number) => (
                    <div key={i} className="pl-3 border-l-2" style={{ borderColor: 'var(--accent-cyan)' }}>
                      <div className="text-sm font-sans" style={{ color: 'var(--text-primary)' }}>{cause.cause}</div>
                      <div className="text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                        Confidence: {Math.round((cause.confidence || 0) * 100)}%
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Immediate Actions */}
            {selectedReport.content?.recommendations && selectedReport.content.recommendations.length > 0 && (
              <div>
                <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                  Immediate Actions
                </div>
                <ol className="space-y-2 list-decimal list-inside">
                  {selectedReport.content.recommendations.slice(0, 4).map((rec: any, i: number) => (
                    <li key={i} className="text-sm font-sans" style={{ color: 'var(--text-primary)' }}>
                      {rec.action}
                      {rec.estimated_time && (
                        <span className="text-xs font-mono ml-2" style={{ color: 'var(--text-tertiary)' }}>
                          ({rec.estimated_time})
                        </span>
                      )}
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {/* Evidence from Knowledge Base */}
            {selectedReport.content?.agents_used && selectedReport.content.agents_used.length > 0 && (
              <div>
                <div className="text-xs font-mono uppercase mb-2" style={{ color: 'var(--text-tertiary)' }}>
                  Evidence from Knowledge Base
                </div>
                <div className="text-xs font-mono" style={{ color: 'var(--accent-cyan)' }}>
                  Analysis performed by: {selectedReport.content.agents_used.join(', ')}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
