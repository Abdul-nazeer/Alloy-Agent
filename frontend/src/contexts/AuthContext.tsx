import { createContext, useContext, useState, type ReactNode } from 'react';

export type UserRole = 'technician' | 'supervisor' | 'manager';

export interface User {
  id: string;
  name: string;
  role: UserRole;
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<boolean>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock user database (in production, this would be a backend API)
const mockUsers: Record<string, { password: string; user: User }> = {
  'tech@alloy.ai': {
    password: 'tech123',
    user: {
      id: '1',
      name: 'John Smith',
      role: 'technician',
      email: 'tech@alloy.ai'
    }
  },
  'supervisor@alloy.ai': {
    password: 'super123',
    user: {
      id: '2',
      name: 'Sarah Johnson',
      role: 'supervisor',
      email: 'supervisor@alloy.ai'
    }
  },
  'manager@alloy.ai': {
    password: 'manager123',
    user: {
      id: '3',
      name: 'Michael Chen',
      role: 'manager',
      email: 'manager@alloy.ai'
    }
  }
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string): Promise<boolean> => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const userRecord = mockUsers[email.toLowerCase()];
    if (userRecord && userRecord.password === password) {
      setUser(userRecord.user);
      localStorage.setItem('alloy_user', JSON.stringify(userRecord.user));
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('alloy_user');
  };

  const hasRole = (roles: UserRole[]): boolean => {
    return user ? roles.includes(user.role) : false;
  };

  return (
    <AuthContext.Provider value={{
      user,
      login,
      logout,
      isAuthenticated: !!user,
      hasRole
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
