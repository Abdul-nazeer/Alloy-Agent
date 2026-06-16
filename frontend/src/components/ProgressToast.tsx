import { useEffect, useState } from 'react';
import { CheckCircle, Loader, FileText, AlertTriangle, Wrench, ClipboardList, X } from 'lucide-react';

interface ProgressStep {
  id: string;
  label: string;
  status: 'pending' | 'active' | 'complete' | 'error';
  clickable?: boolean;
  redirectTo?: string;
  icon?: string;
}

interface ProgressToastProps {
  steps: ProgressStep[];
  onStepClick?: (step: ProgressStep) => void;
  onClose?: () => void;
  title?: string;
}

export default function ProgressToast({ 
  steps, 
  onStepClick, 
  onClose,
  title = "Agent Analysis in Progress"
}: ProgressToastProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Fade in animation
    setTimeout(() => setVisible(true), 50);
  }, []);

  const getIcon = (step: ProgressStep) => {
    if (step.status === 'complete') {
      return <CheckCircle className="w-4 h-4" style={{ color: 'var(--accent-success)' }} />;
    } else if (step.status === 'active') {
      return <Loader className="w-4 h-4 animate-spin" style={{ color: 'var(--accent-cyan)' }} />;
    } else if (step.status === 'error') {
      return <AlertTriangle className="w-4 h-4" style={{ color: 'var(--accent-danger)' }} />;
    } else {
      // Pending - show custom icon based on step type
      const iconProps = { className: "w-4 h-4 opacity-40", style: { color: 'var(--text-tertiary)' } };
      switch (step.icon) {
        case 'anomaly':
          return <AlertTriangle {...iconProps} />;
        case 'diagnosis':
          return <ClipboardList {...iconProps} />;
        case 'recommendation':
          return <Wrench {...iconProps} />;
        case 'report':
          return <FileText {...iconProps} />;
        default:
          return <div className="w-4 h-4 rounded-full border-2 opacity-40" style={{ borderColor: 'var(--border-subtle)' }} />;
      }
    }
  };

  const handleStepClick = (step: ProgressStep) => {
    if (step.clickable && step.status === 'complete' && onStepClick) {
      onStepClick(step);
    }
  };

  return (
    <div
      className={`fixed bottom-6 right-6 glass-card-elevated rounded-lg shadow-2xl transition-all duration-300 z-50 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}
      style={{
        width: '420px',
        maxHeight: '500px',
        border: '1px solid var(--border-glow)',
        backgroundColor: 'rgba(10, 10, 15, 0.95)',
        backdropFilter: 'blur(20px)'
      }}
    >
      {/* Header */}
      <div
        className="px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--border-subtle)' }}
      >
        <div className="flex items-center space-x-2">
          <Loader className="w-4 h-4 animate-spin" style={{ color: 'var(--accent-cyan)' }} />
          <h3 className="text-xs text-mono text-uppercase-spaced font-medium" style={{ color: 'var(--accent-cyan)' }}>
            {title}
          </h3>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="hover-scale transition-fast p-1"
            style={{ color: 'var(--text-tertiary)' }}
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Progress Steps */}
      <div className="p-4 space-y-3 max-h-96 overflow-y-auto">
        {steps.map((step, index) => (
          <div
            key={step.id}
            onClick={() => handleStepClick(step)}
            className={`flex items-start space-x-3 p-3 rounded-sm transition-all ${
              step.clickable && step.status === 'complete'
                ? 'cursor-pointer hover-scale-sm glass-card'
                : ''
            } ${step.status === 'active' ? 'glass-card-elevated' : ''}`}
            style={{
              backgroundColor:
                step.status === 'active'
                  ? 'rgba(0, 229, 255, 0.08)'
                  : step.status === 'complete' && step.clickable
                  ? 'rgba(0, 229, 255, 0.03)'
                  : 'transparent',
              border:
                step.status === 'active'
                  ? '1px solid rgba(0, 229, 255, 0.3)'
                  : step.status === 'complete' && step.clickable
                  ? '1px solid rgba(0, 229, 255, 0.15)'
                  : '1px solid transparent'
            }}
          >
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">{getIcon(step)}</div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p
                  className="text-sm text-body font-medium"
                  style={{
                    color:
                      step.status === 'complete'
                        ? 'var(--text-primary)'
                        : step.status === 'active'
                        ? 'var(--accent-cyan)'
                        : 'var(--text-tertiary)'
                  }}
                >
                  {step.label}
                </p>
                {step.clickable && step.status === 'complete' && (
                  <span className="text-2xs text-mono ml-2" style={{ color: 'var(--accent-cyan)' }}>
                    VIEW →
                  </span>
                )}
              </div>

              {/* Connecting Line */}
              {index < steps.length - 1 && (
                <div
                  className="w-0.5 h-4 ml-2 mt-2"
                  style={{
                    backgroundColor:
                      step.status === 'complete'
                        ? 'var(--accent-cyan)'
                        : 'var(--border-subtle)'
                  }}
                />
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Footer - Show when all complete */}
      {steps.every(s => s.status === 'complete' || s.status === 'error') && (
        <div
          className="px-4 py-3 border-t flex items-center justify-between"
          style={{ borderColor: 'var(--border-subtle)' }}
        >
          <span className="text-2xs text-mono" style={{ color: 'var(--text-secondary)' }}>
            Analysis complete - Click steps to view details
          </span>
          {onClose && (
            <button
              onClick={onClose}
              className="text-2xs text-mono font-medium px-2 py-1 rounded hover-scale transition-fast"
              style={{
                color: 'var(--accent-cyan)',
                backgroundColor: 'rgba(0, 229, 255, 0.1)'
              }}
            >
              DISMISS
            </button>
          )}
        </div>
      )}
    </div>
  );
}
