import { useState } from 'react';
import { useAuth, type UserRole } from '../contexts/AuthContext';
import { Activity, Home } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [selectedRole, setSelectedRole] = useState<UserRole>('technician');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const credentials = {
      technician: { email: 'tech@alloy.ai', password: 'tech123' },
      supervisor: { email: 'supervisor@alloy.ai', password: 'super123' },
      manager: { email: 'manager@alloy.ai', password: 'manager123' }
    };
    
    const { email, password } = credentials[selectedRole];
    await login(email, password);
  };

  const roles: { value: UserRole; label: string }[] = [
    { value: 'technician', label: 'Technician' },
    { value: 'supervisor', label: 'Supervisor' },
    { value: 'manager', label: 'Manager' }
  ];

  return (
    <div 
      className="min-h-screen flex items-center justify-center"
      style={{ backgroundColor: 'var(--bg-base)' }}
    >
      <div 
        className="w-full max-w-sm p-8 rounded-sm"
        style={{ 
          backgroundColor: 'var(--bg-surface)', 
          border: '1px solid var(--border-default)' 
        }}
      >
        {/* Logo */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center space-x-2">
            <Activity className="w-6 h-6" style={{ color: 'var(--accent-cyan)' }} />
            <span 
              className="font-mono text-sm tracking-widest"
              style={{ color: 'var(--text-primary)' }}
            >
              ALLOY AGENT
            </span>
          </div>
        </div>

        {/* Title */}
        <p 
          className="text-center text-sm font-sans mb-6"
          style={{ color: 'var(--text-secondary)' }}
        >
          Select your role
        </p>

        {/* Role Selection */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            {roles.map((role) => (
              <label
                key={role.value}
                className="flex items-center px-4 py-3 rounded-sm cursor-pointer transition-all"
                style={{
                  border: selectedRole === role.value 
                    ? '1px solid var(--accent-cyan)' 
                    : '1px solid var(--border-default)',
                  backgroundColor: selectedRole === role.value 
                    ? 'var(--bg-elevated)' 
                    : 'transparent',
                  color: selectedRole === role.value 
                    ? 'var(--text-primary)' 
                    : 'var(--text-secondary)'
                }}
              >
                <input
                  type="radio"
                  name="role"
                  value={role.value}
                  checked={selectedRole === role.value}
                  onChange={(e) => setSelectedRole(e.target.value as UserRole)}
                  className="sr-only"
                />
                <span className="w-4 h-4 rounded-full mr-3 border-2 flex items-center justify-center"
                  style={{
                    borderColor: selectedRole === role.value ? 'var(--accent-cyan)' : 'var(--border-default)'
                  }}
                >
                  {selectedRole === role.value && (
                    <span 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: 'var(--accent-cyan)' }}
                    ></span>
                  )}
                </span>
                <span className="text-sm font-sans">{role.label}</span>
              </label>
            ))}
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full py-3 rounded-sm font-mono text-sm tracking-wide transition-all"
            style={{
              backgroundColor: 'var(--accent-cyan)',
              color: 'var(--bg-base)'
            }}
          >
            Enter System →
          </button>

          {/* Back to Home Button */}
          <button
            type="button"
            onClick={() => navigate('/')}
            className="w-full py-3 rounded-sm font-mono text-sm tracking-wide transition-all flex items-center justify-center gap-2"
            style={{
              backgroundColor: 'transparent',
              border: '1px solid var(--border-default)',
              color: 'var(--text-secondary)'
            }}
          >
            <Home className="w-4 h-4" />
            <span>Back to Home</span>
          </button>
        </form>

        {/* Footer */}
        <p 
          className="text-center text-xs font-mono mt-6"
          style={{ color: 'var(--text-tertiary)' }}
        >
          AI-Powered Maintenance Assistant
        </p>
      </div>
    </div>
  );
}
