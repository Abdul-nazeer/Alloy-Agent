import { useAuth } from '../contexts/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { MessageSquare, Activity, FileText, BarChart2, FileCheck } from 'lucide-react';

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

  const getRoleBadgeStyle = () => {
    const styles = {
      technician: { border: 'rgba(0, 212, 170, 0.3)', color: '#00d4aa' },
      supervisor: { border: 'rgba(251, 191, 36, 0.3)', color: '#fbbf24' },
      manager: { border: 'rgba(168, 85, 247, 0.3)', color: '#a855f7' }
    };
    return styles[user?.role || 'technician'];
  };

  const navItems = [
    { id: 'chat', label: 'Chat Assistant', icon: MessageSquare, permission: 'canViewChat' },
    { id: 'monitor', label: 'Live Monitor', icon: Activity, permission: 'canViewLiveMonitor' },
    { id: 'documents', label: 'Documents', icon: FileText, permission: 'canViewDocuments' },
    { id: 'reports', label: 'Analysis Reports', icon: BarChart2, permission: 'canViewReports' },
    { id: 'logs', label: 'Operations Logbook', icon: FileCheck, permission: 'canViewLogbook' },
    { id: 'spareparts', label: 'Spare Parts', icon: FileCheck, permission: 'canViewReports' },
    { id: 'historical', label: 'Data Import', icon: FileText, permission: 'canViewReports' },
  ];

  const filteredNavItems = navItems.filter(item => 
    permissions[item.permission as keyof typeof permissions]
  );

  const equipmentTypes = [
    'All Equipment',
    'AC-001 (Air Compressor)',
    'AC-002 (Air Compressor)',
    'CF-003 (Cooling Fan)',
    'RM-005 (Rolling Mill)',
    'CM-007 (Conveyor Motor)'
  ];

  const badgeStyle = getRoleBadgeStyle();

  return (
    <aside 
      className="w-56 h-full flex flex-col"
      style={{ 
        backgroundColor: 'var(--bg-surface)', 
        borderRight: '1px solid var(--border-default)' 
      }}
    >
      {/* Role Badge */}
      <div className="p-3 border-b" style={{ borderColor: 'var(--border-default)' }}>
        <div 
          className="px-2 py-1 rounded-sm font-mono text-xs tracking-widest text-center"
          style={{ 
            border: `1px solid ${badgeStyle.border}`,
            color: badgeStyle.color
          }}
        >
          {user?.role.toUpperCase()}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="space-y-6">
          {/* Navigation Section */}
          <div>
            <h3 
              className="px-3 mb-1 text-2xs font-mono tracking-widest uppercase"
              style={{ color: 'var(--text-tertiary)' }}
            >
              NAVIGATION
            </h3>
            <nav className="space-y-0.5">
              {filteredNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = currentView === item.id;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => onViewChange(item.id)}
                    className="w-full flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-sans transition-all"
                    style={{
                      borderLeft: isActive ? '2px solid var(--accent-cyan)' : '2px solid transparent',
                      backgroundColor: isActive ? 'var(--bg-elevated)' : 'transparent',
                      color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)'
                    }}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Equipment Filter Section */}
          <div>
            <h3 
              className="px-3 mb-1 text-2xs font-mono tracking-widest uppercase"
              style={{ color: 'var(--text-tertiary)' }}
            >
              FILTER BY EQUIPMENT
            </h3>
            <div className="space-y-0.5">
              {equipmentTypes.map((type) => {
                const isActive = equipmentFilter === type;
                
                return (
                  <button
                    key={type}
                    onClick={() => onEquipmentFilterChange(type)}
                    className="w-full text-left px-3 py-2 rounded-sm text-sm font-sans transition-all"
                    style={{
                      borderLeft: isActive ? '2px solid rgba(0, 212, 170, 0.6)' : '2px solid transparent',
                      backgroundColor: isActive ? 'var(--bg-elevated)' : 'transparent',
                      color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)'
                    }}
                  >
                    {type}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Base */}
      <div className="p-3 border-t" style={{ borderColor: 'var(--border-default)' }}>
        <h3 
          className="mb-2 text-2xs font-mono tracking-widest uppercase"
          style={{ color: 'var(--text-tertiary)' }}
        >
          KNOWLEDGE BASE
        </h3>
        <div className="text-xs font-sans space-y-1" style={{ color: 'var(--text-secondary)' }}>
          <div>
            <span className="font-mono" style={{ color: 'var(--accent-cyan)' }}>6</span> documents indexed
          </div>
          <div>
            <span className="font-mono" style={{ color: 'var(--accent-cyan)' }}>2,606</span> chunks stored
          </div>
        </div>
      </div>
    </aside>
  );
}
