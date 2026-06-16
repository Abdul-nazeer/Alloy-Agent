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
import SparePartsInventory from './components/SparePartsInventory';
import HistoricalDataUpload from './components/HistoricalDataUpload';
import IndustrialBackground from './components/IndustrialBackground';
import { Clock, Bell } from 'lucide-react';
import { alertsAPI } from './api/client';

function AppContent() {
  const { isAuthenticated, logout } = useAuth();
  const [currentView, setCurrentView] = useState('monitor');
  const [equipmentFilter, setEquipmentFilter] = useState('All Equipment');
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(new Date());
  const [unreadAlertCount, setUnreadAlertCount] = useState(0);
  const [showAlertsPanel, setShowAlertsPanel] = useState(false);
  const [chatInitialMessage, setChatInitialMessage] = useState<string | undefined>(undefined);

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
        setUnreadAlertCount(response.data.count);
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

  const handleNavigateToChat = (message?: string) => {
    setCurrentView('chat');
    setChatInitialMessage(message);
    console.log('Navigating to chat with message:', message);
  };

  const handleNavigateToReports = () => {
    setCurrentView('reports');
  };

  return (
    <>
      {/* Industrial Animated Background */}
      <IndustrialBackground />
      
      {/* Main App Container */}
      <div className="flex flex-row h-screen overflow-hidden relative z-10">
        {/* Sidebar */}
        <Sidebar
          currentView={currentView}
          onViewChange={setCurrentView}
          equipmentFilter={equipmentFilter}
          onEquipmentFilterChange={setEquipmentFilter}
        />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Premium Header */}
          <header 
            className="glass-card border-b"
            style={{ borderColor: 'var(--border-default)' }}
          >
            <div className="h-16 flex items-center justify-between px-6">
              {/* Left: System Status */}
              <div className="flex items-center space-x-5">
                <div className="flex items-center space-x-1.5">
                  <span className="status-dot status-normal" style={{ width: '6px', height: '6px' }} />
                  <span className="text-2xs text-mono" style={{ color: 'var(--status-normal)' }}>
                    SYSTEM ONLINE
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="status-dot status-normal" style={{ width: '6px', height: '6px' }} />
                  <span className="text-2xs text-mono" style={{ color: 'var(--text-secondary)' }}>
                    Backend Connected
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="status-dot status-normal" style={{ width: '6px', height: '6px' }} />
                  <span className="text-2xs text-mono" style={{ color: 'var(--text-secondary)' }}>
                    RAG Active
                  </span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="status-dot status-normal" style={{ width: '6px', height: '6px' }} />
                  <span className="text-2xs text-mono" style={{ color: 'var(--text-secondary)' }}>
                    Sensors Streaming
                  </span>
                </div>
              </div>

              {/* Right: Time & Actions */}
              <div className="flex items-center space-x-4">
                {/* Clock */}
                <div className="flex items-center space-x-1.5">
                  <Clock className="w-3.5 h-3.5" style={{ color: 'var(--accent-cyan)' }} />
                  <span 
                    className="text-mono text-sm font-semibold"
                    style={{ color: 'var(--accent-cyan)' }}
                  >
                    {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span 
                    className="text-2xs text-mono"
                    style={{ color: 'var(--text-tertiary)' }}
                  >
                    {currentTime.toLocaleDateString([], { weekday: 'short' }).toUpperCase()}
                  </span>
                </div>

                {/* Alert Bell */}
                <button
                  onClick={() => setShowAlertsPanel(!showAlertsPanel)}
                  className="relative p-2 rounded-sm transition-all"
                  style={{
                    backgroundColor: unreadAlertCount > 0 ? 'rgba(239, 68, 68, 0.1)' : 'transparent',
                    border: '1px solid ' + (unreadAlertCount > 0 ? 'var(--accent-danger)' : 'var(--border-default)'),
                    color: unreadAlertCount > 0 ? 'var(--accent-danger)' : 'var(--text-secondary)'
                  }}
                >
                  <Bell className="w-4 h-4" />
                  {unreadAlertCount > 0 && (
                    <span
                      className="absolute -top-1 -right-1 px-1 min-w-[16px] h-4 rounded-sm text-[9px] font-bold flex items-center justify-center"
                      style={{
                        backgroundColor: 'var(--accent-danger)',
                        color: '#fff'
                      }}
                    >
                      {unreadAlertCount > 9 ? '9+' : unreadAlertCount}
                    </span>
                  )}
                </button>
                
                {/* Logout */}
                <button
                  onClick={logout}
                  className="px-3 py-1.5 rounded-sm text-2xs font-mono transition-all"
                  style={{
                    backgroundColor: 'var(--bg-elevated)',
                    border: '1px solid var(--border-default)',
                    color: 'var(--text-secondary)'
                  }}
                >
                  Logout
                </button>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto p-6 relative">
            {/* Alerts Panel Overlay */}
            {showAlertsPanel && (
              <div 
                className="absolute top-0 right-0 z-50 w-96 h-full glass-card-elevated"
                style={{ 
                  borderLeft: '1px solid var(--border-glow)'
                }}
              >
                <AlertsPanel 
                  onClose={() => setShowAlertsPanel(false)}
                  onAlertUpdate={() => {
                    alertsAPI.getUnread().then(res => setUnreadAlertCount(res.data.count));
                  }}
                />
              </div>
            )}
            
            {currentView === 'monitor' && !selectedEquipmentId && (
              <Dashboard 
                onEquipmentSelect={handleEquipmentSelect} 
                equipmentFilter={equipmentFilter}
                onNavigateToChat={handleNavigateToChat}
                onNavigateToReports={handleNavigateToReports}
              />
            )}
            {currentView === 'monitor' && selectedEquipmentId && (
              <EquipmentDetail
                equipmentId={selectedEquipmentId}
                onBack={() => setSelectedEquipmentId(null)}
              />
            )}
            {currentView === 'chat' && <ChatPanel initialMessage={chatInitialMessage} />}
            {currentView === 'documents' && <DocumentsView />}
            {currentView === 'reports' && <ReportsView />}
            {currentView === 'logs' && <LogbookView />}
            {currentView === 'spareparts' && <SparePartsInventory />}
            {currentView === 'historical' && <HistoricalDataUpload />}
          </main>

          {/* Premium Footer */}
          <footer 
            className="glass-card border-t px-6 py-2"
            style={{ borderColor: 'var(--border-default)' }}
          >
            <div className="flex items-center justify-between text-xs text-mono" style={{ color: 'var(--text-tertiary)' }}>
              <span>AI: Multi-Agent System (LangGraph)</span>
              <span>•</span>
              <span>RAG: Hybrid Search + Reranking</span>
              <span>•</span>
              <span>Vector DB: Qdrant Cloud</span>
            </div>
          </footer>
        </div>
      </div>
    </>
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
