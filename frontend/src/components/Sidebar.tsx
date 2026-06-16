import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { MessageSquare, Activity, FileText, BarChart2, FileCheck, PackageOpen, Upload } from 'lucide-react';
import { useEffect, useState } from 'react';
import { equipmentAPI, type Equipment } from '../api/client';

interface SidebarProps {
  currentView: string;
  onViewChange: (view: string) => void;
  equipmentFilter: string;
  onEquipmentFilterChange: (filter: string) => void;
}

export default function Sidebar({ 
  currentView, 
  onViewChange, 
  equipmentFilter, 
  onEquipmentFilterChange 
}: SidebarProps) {
  const { user } = useAuth();
  const permissions = usePermissions();
  const [equipment, setEquipment] = useState<Equipment[]>([]);
  const [docCount, setDocCount] = useState(0);
  const [chunkCount, setChunkCount] = useState(0);

  // Load equipment dynamically on mount
  useEffect(() => {
    loadEquipment();
    loadKnowledgeBaseStats();
  }, []);

  const loadEquipment = async () => {
    try {
      const response = await equipmentAPI.getAll();
      setEquipment(response.data);
    } catch (err) {
      console.error('Failed to load equipment for filter:', err);
    }
  };

  const loadKnowledgeBaseStats = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/rag/documents`);
      if (response.ok) {
        const docs = await response.json();
        setDocCount(docs.length);
        const total = docs.reduce((sum: number, doc: any) => sum + (doc.chunk_count || 0), 0);
        setChunkCount(total);
      }
    } catch (err) {
      console.error('Failed to load knowledge base stats:', err);
    }
  };

  const getRoleBadgeStyle = () => {
    const styles = {
      technician: { border: 'rgba(0, 212, 170, 0.3)', color: '#00d4aa', bg: 'rgba(0, 212, 170, 0.05)' },
      supervisor: { border: 'rgba(251, 191, 36, 0.3)', color: '#fbbf24', bg: 'rgba(251, 191, 36, 0.05)' },
      manager: { border: 'rgba(168, 85, 247, 0.3)', color: '#a855f7', bg: 'rgba(168, 85, 247, 0.05)' }
    };
    return styles[user?.role || 'technician'];
  };

  const navItems = [
    { 
      id: 'chat', 
      label: 'Chat Assistant', 
      subtitle: 'Conversational Intelligence',
      icon: MessageSquare, 
      permission: 'canViewChat' 
    },
    { 
      id: 'monitor', 
      label: 'Live Monitor', 
      subtitle: 'Real-Time Sensor Streams',
      icon: Activity, 
      permission: 'canViewLiveMonitor' 
    },
    { 
      id: 'documents', 
      label: 'Knowledge Base', 
      subtitle: 'Technical Documentation',
      icon: FileText, 
      permission: 'canViewDocuments' 
    },
    { 
      id: 'reports', 
      label: 'Analysis Reports', 
      subtitle: 'AI Generated Diagnostics',
      icon: BarChart2, 
      permission: 'canViewReports' 
    },
    { 
      id: 'logs', 
      label: 'Operations Logbook', 
      subtitle: 'Maintenance Records',
      icon: FileCheck, 
      permission: 'canViewLogbook' 
    },
    { 
      id: 'spareparts', 
      label: 'Spare Parts', 
      subtitle: 'Inventory Intelligence',
      icon: PackageOpen, 
      permission: 'canViewReports' 
    },
    { 
      id: 'historical', 
      label: 'Data Import', 
      subtitle: 'Historical Data Upload',
      icon: Upload, 
      permission: 'canViewReports' 
    },
  ];

  const filteredNavItems = navItems.filter(item => 
    permissions[item.permission as keyof typeof permissions]
  );

  // Build equipment filter list dynamically from API
  const equipmentTypes = [
    'All Equipment',
    ...equipment.map(eq => `${eq.equipment_id} (${eq.equipment_type})`)
  ];

  const badgeStyle = getRoleBadgeStyle();

  return (
    <aside 
      className="w-64 h-full flex flex-col"
      style={{ 
        backgroundColor: 'var(--bg-surface)', 
        borderRight: '1px solid var(--border-default)' 
      }}
    >
      {/* Header with Alloy Logo Mark */}
      <div 
        className="px-4 py-5 border-b"
        style={{ borderColor: 'var(--border-glow)' }}
      >
        {/* Simple Industrial Logo Mark */}
        <div className="flex items-center space-x-3 mb-4">
          <div 
            className="relative w-10 h-10 flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, rgba(0, 229, 255, 0.15), rgba(0, 229, 255, 0.05))',
              border: '2px solid var(--accent-cyan)',
              clipPath: 'polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%)',
              boxShadow: '0 0 15px rgba(0, 229, 255, 0.3)'
            }}
          >
            <span 
              className="text-xl font-bold font-mono"
              style={{
                color: 'var(--accent-cyan)',
                textShadow: '0 0 10px rgba(0, 229, 255, 0.5)'
              }}
            >
              A
            </span>
          </div>
          <div>
            <h2 
              className="text-base font-bold font-mono"
              style={{ 
                color: 'var(--text-primary)',
                letterSpacing: '0.05em'
              }}
            >
              ALLOY AGENT
            </h2>
            <p 
              className="text-2xs text-mono"
              style={{ color: 'var(--text-tertiary)' }}
            >
              Maintenance Intelligence
            </p>
          </div>
        </div>

        {/* Role Badge */}
        <div 
          className="px-3 py-2 rounded-sm"
          style={{ 
            border: `1px solid ${badgeStyle.border}`,
            backgroundColor: badgeStyle.bg,
          }}
        >
          <div className="flex items-center justify-between text-2xs text-mono">
            <span style={{ color: badgeStyle.color }}>
              {user?.role.toUpperCase()}
            </span>
            <span style={{ color: 'var(--text-tertiary)' }}>
              SHIFT A
            </span>
          </div>
          <div className="text-2xs mt-1" style={{ color: 'var(--text-tertiary)' }}>
            {equipment.length} systems online
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-1">
          {filteredNavItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            
            return (
              <button
                key={item.id}
                onClick={() => onViewChange(item.id)}
                className="w-full flex items-start space-x-2 px-3 py-2.5 rounded-sm text-left transition-all group"
                style={{
                  backgroundColor: isActive ? 'rgba(0, 229, 255, 0.08)' : 'transparent',
                  borderLeft: isActive ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                }}
              >
                {/* Icon */}
                <div 
                  className="flex-shrink-0 mt-0.5"
                  style={{
                    color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)'
                  }}
                >
                  <Icon className="w-4 h-4" />
                </div>

                {/* Text Content */}
                <div className="flex-1 min-w-0">
                  <div 
                    className="font-sans text-sm font-medium mb-0.5"
                    style={{ 
                      color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)' 
                    }}
                  >
                    {item.label}
                  </div>
                  <div 
                    className="text-mono text-2xs"
                    style={{ 
                      color: 'var(--text-tertiary)',
                      opacity: 0.7
                    }}
                  >
                    {item.subtitle}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Equipment Filter Section */}
        <div className="mt-5 pt-5 border-t" style={{ borderColor: 'var(--border-default)' }}>
          <h3 
            className="px-2 mb-2 text-2xs font-mono uppercase"
            style={{ color: 'var(--text-tertiary)' }}
          >
            EQUIPMENT FILTER
          </h3>
          <div className="space-y-0.5">
            {equipmentTypes.map((type) => {
              const isActive = equipmentFilter === type;
              
              return (
                <button
                  key={type}
                  onClick={() => onEquipmentFilterChange(type)}
                  className="w-full text-left px-2 py-1.5 rounded-sm text-xs font-mono transition-all"
                  style={{
                    backgroundColor: isActive ? 'rgba(0, 212, 170, 0.08)' : 'transparent',
                    color: isActive ? 'var(--status-normal)' : 'var(--text-secondary)'
                  }}
                >
                  {type}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Knowledge Base Stats */}
      <div 
        className="p-3 border-t"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <h3 
          className="mb-2 text-2xs font-mono uppercase flex items-center space-x-1"
          style={{ color: 'var(--text-tertiary)' }}
        >
          <FileText className="w-3 h-3" />
          <span>KNOWLEDGE BASE</span>
        </h3>
        <div className="flex items-center justify-between text-xs">
          <div>
            <span className="font-mono font-bold" style={{ color: 'var(--accent-cyan)' }}>
              {docCount}
            </span>
            <span className="ml-1 text-2xs" style={{ color: 'var(--text-tertiary)' }}>
              docs
            </span>
          </div>
          <div>
            <span className="font-mono font-bold" style={{ color: 'var(--accent-orange)' }}>
              {chunkCount > 1000 ? `${(chunkCount / 1000).toFixed(1)}K` : chunkCount}
            </span>
            <span className="ml-1 text-2xs" style={{ color: 'var(--text-tertiary)' }}>
              chunks
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}
