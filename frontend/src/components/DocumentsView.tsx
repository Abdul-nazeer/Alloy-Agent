import { useState, useEffect } from 'react';
import { FileText, Download, Eye, Search } from 'lucide-react';
import PDFViewerModal from './PDFViewerModal';

interface Document {
  filename: string;
  size: string;
  chunks: number;
  uploadDate: string;
  type: string;
}

export default function DocumentsView() {
  const [selectedPDF, setSelectedPDF] = useState<string | null>(null);
  const [documents] = useState<Document[]>([
    {
      filename: '76-Contitech-Conveyor-Belt-Maintenance-Manual-2015.pdf',
      size: '2.4 MB',
      chunks: 456,
      uploadDate: '2024-01-15',
      type: 'Maintenance Manual'
    },
    {
      filename: 'FORM-70012.pdf',
      size: '1.8 MB',
      chunks: 389,
      uploadDate: '2024-01-15',
      type: 'Technical Form'
    },
    {
      filename: 'p00120_user_manual.pdf',
      size: '3.1 MB',
      chunks: 512,
      uploadDate: '2024-01-15',
      type: 'User Manual'
    },
    {
      filename: '10m.pdf',
      size: '2.2 MB',
      chunks: 423,
      uploadDate: '2024-01-15',
      type: 'Equipment Guide'
    },
    {
      filename: 'Steel-Manufacturing-Incident-Analysis-and-Prediction.pdf',
      size: '1.5 MB',
      chunks: 312,
      uploadDate: '2024-01-15',
      type: 'Safety Analysis'
    },
    {
      filename: 'ijrtssh.vol_.4.issue2_171.pdf',
      size: '2.0 MB',
      chunks: 514,
      uploadDate: '2024-01-15',
      type: 'Research Paper'
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDocs, setFilteredDocs] = useState(documents);

  useEffect(() => {
    if (searchQuery.trim()) {
      setFilteredDocs(
        documents.filter(doc =>
          doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
          doc.type.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredDocs(documents);
    }
  }, [searchQuery, documents]);

  const totalChunks = documents.reduce((sum, doc) => sum + doc.chunks, 0);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 
            className="text-xs font-mono tracking-widest mb-1"
            style={{ color: 'var(--accent-cyan)' }}
          >
            📄 KNOWLEDGE BASE DOCUMENTS
          </h2>
          <p 
            className="text-sm font-sans"
            style={{ color: 'var(--text-secondary)' }}
          >
            {documents.length} documents indexed → {totalChunks.toLocaleString()} chunks stored
          </p>
        </div>

        <div 
          className="px-3 py-1 rounded-sm text-xs font-mono"
          style={{
            border: '1px solid rgba(34, 197, 94, 0.4)',
            backgroundColor: 'rgba(34, 197, 94, 0.05)',
            color: '#22c55e'
          }}
        >
          ● RAG Active
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative">
        <Search 
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" 
          style={{ color: 'var(--text-tertiary)' }}
        />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search documents by name or type..."
          className="w-full pl-10 pr-4 py-2 rounded-sm text-sm font-sans focus:outline-none"
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-default)',
            color: 'var(--text-primary)'
          }}
        />
      </div>

      {/* Documents List */}
      <div className="space-y-2">
        {filteredDocs.map((doc, idx) => (
          <div
            key={idx}
            className="p-4 rounded-sm hover:border-opacity-60 transition-all"
            style={{
              backgroundColor: 'var(--bg-surface)',
              border: '1px solid var(--border-default)'
            }}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                <div 
                  className="p-2 rounded-sm"
                  style={{ backgroundColor: 'var(--bg-elevated)' }}
                >
                  <FileText className="w-5 h-5" style={{ color: 'var(--accent-cyan)' }} />
                </div>

                <div className="flex-1">
                  <h3 
                    className="text-sm font-medium font-sans mb-1"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {doc.filename}
                  </h3>
                  
                  <div className="flex items-center space-x-4 text-xs font-mono mb-2" style={{ color: 'var(--text-secondary)' }}>
                    <span>
                      <span style={{ color: 'var(--text-tertiary)' }}>Size:</span>{' '}
                      <span style={{ color: 'var(--text-primary)' }}>{doc.size}</span>
                    </span>
                    <span>•</span>
                    <span>
                      <span style={{ color: 'var(--text-tertiary)' }}>Chunks:</span>{' '}
                      <span style={{ color: 'var(--accent-cyan)' }}>{doc.chunks}</span>
                    </span>
                    <span>•</span>
                    <span>
                      <span style={{ color: 'var(--text-tertiary)' }}>Uploaded:</span>{' '}
                      <span style={{ color: 'var(--text-primary)' }}>{doc.uploadDate}</span>
                    </span>
                  </div>

                  <div>
                    <span 
                      className="inline-block px-2 py-0.5 rounded-sm text-2xs font-mono"
                      style={{
                        border: '1px solid var(--border-default)',
                        backgroundColor: 'var(--bg-elevated)',
                        color: 'var(--text-secondary)'
                      }}
                    >
                      {doc.type}
                    </span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={() => setSelectedPDF(doc.filename)}
                  className="p-2 rounded-sm transition-all hover:border-opacity-80"
                  style={{
                    backgroundColor: 'var(--bg-elevated)',
                    border: '1px solid var(--border-default)',
                    color: 'var(--text-secondary)'
                  }}
                  title="View document"
                >
                  <Eye className="w-4 h-4" />
                </button>
                <button
                  onClick={() => {
                    // Trigger download
                    window.open(`${import.meta.env.VITE_API_URL || 'https://alloy-agent-production.up.railway.app'}/api/pdfs/${doc.filename}`, '_blank');
                  }}
                  className="p-2 rounded-sm transition-all hover:border-opacity-80"
                  style={{
                    backgroundColor: 'var(--bg-elevated)',
                    border: '1px solid var(--border-default)',
                    color: 'var(--text-secondary)'
                  }}
                  title="Download document"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredDocs.length === 0 && (
        <div 
          className="text-center py-12 rounded-sm"
          style={{ 
            backgroundColor: 'var(--bg-surface)', 
            border: '1px solid var(--border-default)' 
          }}
        >
          <Search className="w-12 h-12 mx-auto mb-3" style={{ color: 'var(--text-tertiary)' }} />
          <p 
            className="text-sm font-mono"
            style={{ color: 'var(--text-secondary)' }}
          >
            No documents match your search
          </p>
        </div>
      )}

      {/* Info Banner */}
      <div 
        className="p-4 rounded-sm"
        style={{
          backgroundColor: 'rgba(0, 212, 170, 0.05)',
          border: '1px solid rgba(0, 212, 170, 0.2)'
        }}
      >
        <div className="flex items-start space-x-3">
          <FileText className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--accent-cyan)' }} />
          <div>
            <p className="text-sm font-sans mb-1" style={{ color: 'var(--text-primary)' }}>
              RAG-Powered Document Search
            </p>
            <p className="text-xs font-sans" style={{ color: 'var(--text-secondary)' }}>
              All documents are indexed and searchable via the AI Chat. Ask questions and the AI will automatically cite relevant sections from these manuals.
            </p>
          </div>
        </div>
      </div>

      {/* PDF Viewer Modal */}
      {selectedPDF && (
        <PDFViewerModal
          filename={selectedPDF}
          onClose={() => setSelectedPDF(null)}
        />
      )}
    </div>
  );
}
