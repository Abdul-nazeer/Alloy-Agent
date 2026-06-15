import { X, Download } from 'lucide-react';

interface PDFViewerModalProps {
  filename: string;
  onClose: () => void;
}

export default function PDFViewerModal({ filename, onClose }: PDFViewerModalProps) {
  // PDF URL from backend
  const pdfUrl = `${import.meta.env.VITE_API_URL || 'https://alloy-agent-production.up.railway.app'}/api/pdfs/${filename}`;

  const handleDownload = () => {
    window.open(pdfUrl, '_blank');
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
      onClick={onClose}
    >
      <div 
        className="w-full max-w-5xl h-[90vh] flex flex-col rounded-sm"
        style={{ 
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-default)'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: 'var(--border-default)' }}
        >
          <div className="flex items-center space-x-3">
            <h3 
              className="text-sm font-mono"
              style={{ color: 'var(--text-primary)' }}
            >
              {filename}
            </h3>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleDownload}
              className="flex items-center space-x-2 px-3 py-2 rounded-sm transition-all"
              style={{
                backgroundColor: 'var(--accent-cyan)',
                color: 'var(--bg-base)'
              }}
            >
              <Download className="w-4 h-4" />
              <span className="text-xs font-mono">Download</span>
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-sm transition-all"
              style={{
                backgroundColor: 'var(--bg-elevated)',
                border: '1px solid var(--border-default)',
                color: 'var(--text-secondary)'
              }}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* PDF Viewer using iframe */}
        <div className="flex-1 overflow-hidden">
          <iframe
            src={`${pdfUrl}#toolbar=1&navpanes=0&scrollbar=1`}
            className="w-full h-full"
            title={filename}
            style={{ border: 'none' }}
          />
        </div>
      </div>
    </div>
  );
}
