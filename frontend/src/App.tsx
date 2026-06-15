import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import EquipmentDetail from './components/EquipmentDetail';
import ChatPanel from './components/ChatPanel';
import DocumentsView from './components/DocumentsView';
import ReportsView from './components/ReportsView';
import LogbookView from './components/LogbookView';
import AlertsPanel from './components/AlertsPanel';
import { Activity, Clock, Bell } from 'lucide-react';
import { alertsAPI } from './api/client';

function AppContent() {
  const { isAuthenticated, logout } = useAuth();
  const [currentView, setCurrentView] = useState('monitor');
  const [equipmentFilter, setEquipmentFilter] = useState('All Equipment');
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [unreadAlertCount, setUnreadAlertCount] = useState(0);
  const [showAlertsPanel, setShowAlertsPanel] = useState(false);

  // Update clock every second
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Poll for unread alerts every 5 seconds
  useEffect(() => {
    const fetchUnreadAlerts = async () => {
      try {
        const response = await alertsAPI.getUnread();
        setUnreadAlertCount(response.count);
      } catch (err) {
        console.error('Failed to fetch unread alerts:', err);
      }
    };

    fetchUnreadAlerts();
    const alertTimer = setInterval(fetchUnreadAlerts, 5000);
    return () => clearInterval(alertTimer);
  }, []);

  if (!isAuthenticated) {
    return <Login />;
  }

  const handleEquipmentSelect = (equipmentId: string) => {
    setSelectedEquipmentId(equipmentId);
  };

  return (
    <div className="flex flex-row h-screen overflow-hidden" style={{ backgroundColor: 'var(--bg-base)' }}>
      {/* Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        equipmentFilter={equipmentFilter}
        onEquipmentFilterChange={setEquipmentFilter}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header 
          className="h-14 flex items-center justify-between px-6 border-b"
          style={{ 
            backgroundColor: 'var(--bg-surface)', 
            borderColor: 'var(--border-default)' 
          }}
        >
          <div className="flex items-center space-x-3">
            <Activity className="w-6 h-6" style={{ color: 'var(--accent-cyan)' }} />
            <div>
              <h1 
                className="font-mono text-sm tracking-widest font-medium"
                style={{ color: 'var(--text-primary)' }}
              >
                ALLOY AGENT
              </h1>
              <p 
                className="text-xs font-sans"
                style={{ color: 'var(--text-secondary)' }}
              >
                AI-Powered Maintenance Assistant
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            {/* Alert Bell Icon with Badge */}
            <button
              onClick={() => setShowAlertsPanel(!showAlertsPanel)}
              className="relative px-2 py-1.5 text-xs font-medium font-sans rounded-sm transition-all hover:opacity-80"
              style={{
                color: unreadAlertCount > 0 ? '#ef4444' : 'var(--text-secondary)',
                backgroundColor: unreadAlertCount > 0 ? 'rgba(239, 68, 68, 0.1)' : 'transparent'
              }}
            >
              <Bell className="w-4 h-4" />
              {unreadAlertCount > 0 && (
                <span
                  className="absolute -top-1 -right-1 w-4 h-4 rounded-full text-[10px] font-bold flex items-center justify-center"
                  style={{
                    backgroundColor: '#ef4444',
                    color: '#fff'
                  }}
                >
                  {unreadAlertCount > 9 ? '9+' : unreadAlertCount}
                </span>
              )}
            </button>
            
            <button
              onClick={() => setCurrentView('monitor')}
              className="px-3 py-1.5 text-xs font-medium font-sans rounded-sm transition-all"
              style={{
                color: currentView === 'monitor' ? 'var(--text-primary)' : 'var(--text-secondary)',
                backgroundColor: currentView === 'monitor' ? 'var(--bg-elevated)' : 'transparent'
              }}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentView('chat')}
              className="px-3 py-1.5 text-xs font-medium font-sans rounded-sm transition-all"
              style={{
                color: currentView === 'chat' ? 'var(--text-primary)' : 'var(--text-secondary)',
                backgroundColor: currentView === 'chat' ? 'var(--bg-elevated)' : 'transparent'
              }}
            >
              AI Chat
            </button>
            <button
              onClick={logout}
              className="px-3 py-1.5 text-xs font-medium font-sans rounded-sm transition-all"
              style={{ color: 'var(--text-secondary)' }}
            >
              Logout
            </button>
          </div>
        </header>

        {/* Status Bar */}
        <div 
          className="flex items-center justify-between px-6 py-2 border-b"
          style={{ 
            backgroundColor: 'rgba(13, 15, 20, 0.5)', 
            borderColor: 'var(--border-subtle)' 
          }}
        >
          <div className="flex items-center space-x-6 text-xs">
            <div className="flex items-center space-x-2">
              <span 
                className="w-2 h-2 rounded-full animate-pulse" 
                style={{ backgroundColor: 'var(--status-normal)' }}
              ></span>
              <span className="font-mono" style={{ color: 'var(--status-normal)' }}>
                SYSTEM ONLINE
              </span>
            </div>
            <div className="flex items-center space-x-1 font-mono" style={{ color: 'var(--text-tertiary)' }}>
              <Clock className="w-3 h-3" />
              <span>
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-4 text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
            <span>Backend: Connected</span>
            <span>•</span>
            <span>RAG: Active</span>
            <span>•</span>
            <span>Sensors: Streaming</span>
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 overflow-y-auto p-6 relative">
          {/* Alerts Panel Overlay */}
          {showAlertsPanel && (
            <div 
              className="absolute top-0 right-0 z-50 w-96 h-full shadow-2xl"
              style={{ 
                backgroundColor: 'var(--bg-surface)',
                borderLeft: '1px solid var(--border-default)'
              }}
            >
              <AlertsPanel 
                onClose={() => setShowAlertsPanel(false)}
                onAlertUpdate={() => {
                  // Refresh unread count when alert is marked as read
                  alertsAPI.getUnread().then(res => setUnreadAlertCount(res.count));
                }}
              />
            </div>
          )}
          
          {currentView === 'monitor' && !selectedEquipmentId && (
            <Dashboard 
              onEquipmentSelect={handleEquipmentSelect} 
              equipmentFilter={equipmentFilter}
            />
          )}
          {currentView === 'monitor' && selectedEquipmentId && (
            <EquipmentDetail
              equipmentId={selectedEquipmentId}
              onBack={() => setSelectedEquipmentId(null)}
            />
          )}
          {currentView === 'chat' && <ChatPanel />}
          {currentView === 'documents' && <DocumentsView />}
          {currentView === 'reports' && <ReportsView />}
          {currentView === 'logs' && <LogbookView />}
        </main>

        {/* Footer */}
        <footer 
          className="px-6 py-1.5 border-t"
          style={{ 
            backgroundColor: 'var(--bg-surface)', 
            borderColor: 'var(--border-default)' 
          }}
        >
          <div className="flex items-center justify-between text-xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
            <span>AI: Phi-3.5-mini Fine-tuned (2K+ scenarios)</span>
            <span>|</span>
            <span>RAG: Hybrid Search + Reranking</span>
            <span>|</span>
            <span>Vector DB: Qdrant Cloud</span>
          </div>
        </footer>
      </div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
