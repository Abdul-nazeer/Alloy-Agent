import { useAuth, type UserRole } from '../contexts/AuthContext';

interface Permissions {
  canViewLiveMonitor: boolean;
  canViewChat: boolean;
  canViewDocuments: boolean;
  canViewReports: boolean;
  canViewLogbook: boolean;
  canTriggerAnomalyAlert: boolean;
  chatDepth: 'detailed' | 'summary' | 'executive';
}

const rolePermissions: Record<UserRole, Permissions> = {
  technician: {
    canViewLiveMonitor: true,
    canViewChat: true,
    canViewDocuments: true,
    canViewReports: false,
    canViewLogbook: false,
    canTriggerAnomalyAlert: false,
    chatDepth: 'detailed',
  },
  supervisor: {
    canViewLiveMonitor: true,
    canViewChat: true,
    canViewDocuments: true,
    canViewReports: true,
    canViewLogbook: true,
    canTriggerAnomalyAlert: true,
    chatDepth: 'summary',
  },
  manager: {
    canViewLiveMonitor: true,
    canViewChat: true,
    canViewDocuments: true,
    canViewReports: true,
    canViewLogbook: true,
    canTriggerAnomalyAlert: false,
    chatDepth: 'executive',
  },
};

export function usePermissions(): Permissions {
  const { user } = useAuth();
  
  if (!user) {
    return {
      canViewLiveMonitor: false,
      canViewChat: false,
      canViewDocuments: false,
      canViewReports: false,
      canViewLogbook: false,
      canTriggerAnomalyAlert: false,
      chatDepth: 'detailed',
    };
  }
  
  return rolePermissions[user.role];
}
