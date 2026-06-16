import { useState, useEffect } from 'react';
import { FileText, Download, Eye, Search } from 'lucide-react';
import PDFViewerModal from './PDFViewerModal';

interface Document {
  doc_id?: string;
  filename: string;
  size?: string;
  file_size_kb?: number;
  chunks?: number;
  chunk_count?: number;
  uploadDate?: string;
  type: string;
  page_count?: number;
  status?: string;
}

export default function DocumentsView() {
  const [selectedPDF, setSelectedPDF] = useState<string | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredDocs, setFilteredDocs] = useState<Document[]>([]);

  // Fetch documents from API
  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/rag/documents`);
      if (response.ok) {
        const docs = await response.json();
        setDocuments(docs);
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error);
    }
  };

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

  const totalChunks = documents.reduce((sum, doc) => sum + (doc.chunks || doc.chunk_count || 0), 0);

  return (
    <div className="space-y-4">
      {/* Header - Read-Only Knowledge Library */}
      <div className="flex items-start justify-between">
        <div>
          <h2 
            className="heading-primary text-xl text-uppercase-spaced mb-2"
            style={{ color: 'var(--accent-cyan)' }}
          >
            📄 KNOWLEDGE BASE LIBRARY
          </h2>
          <p 
            className="text-body text-base"
            style={{ color: 'var(--text-secondary)' }}
          >
            {documents.length} documents indexed → {totalChunks.toLocaleString()} chunks stored
          </p>
          <p 
            className="text-mono text-xs mt-2"
            style={{ color: 'var(--text-tertiary)' }}
          >
            Pre-indexed maintenance manuals and technical documentation. Search via AI Chat for intelligent retrieval.
          </p>
        </div>

        <div 
          className="glass-card px-4 py-2 rounded-lg text-xs text-mono"
          style={{
            border: '1px solid rgba(34, 197, 94, 0.4)',
            color: 'var(--status-normal)'
          }}
        >
          <span className="status-dot status-normal pulse-dot mr-2" style={{ width: '6px', height: '6px' }} />
          RAG ACTIVE
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
        {filteredDocs.map((doc, idx) => {
          const displaySize = doc.size || (doc.file_size_kb ? `${doc.file_size_kb.toFixed(1)} KB` : 'Unknown');
          const displayChunks = doc.chunks || doc.chunk_count || 0;
          const displayDate = doc.uploadDate || new Date().toISOString().split('T')[0];
          
          return (
            <div
              key={doc.doc_id || idx}
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
                        <span style={{ color: 'var(--text-primary)' }}>{displaySize}</span>
                      </span>
                      <span>•</span>
                      <span>
                        <span style={{ color: 'var(--text-tertiary)' }}>Chunks:</span>{' '}
                        <span style={{ color: 'var(--accent-cyan)' }}>{displayChunks}</span>
                      </span>
                      {doc.page_count && (
                        <>
                          <span>•</span>
                          <span>
                            <span style={{ color: 'var(--text-tertiary)' }}>Pages:</span>{' '}
                            <span style={{ color: 'var(--text-primary)' }}>{doc.page_count}</span>
                          </span>
                        </>
                      )}
                      <span>•</span>
                      <span>
                        <span style={{ color: 'var(--text-tertiary)' }}>Uploaded:</span>{' '}
                        <span style={{ color: 'var(--text-primary)' }}>{displayDate}</span>
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
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
                      {doc.status === 'indexed' && (
                        <span 
                          className="inline-block px-2 py-0.5 rounded-sm text-2xs font-mono"
                          style={{
                            border: '1px solid rgba(34, 197, 94, 0.4)',
                            backgroundColor: 'rgba(34, 197, 94, 0.05)',
                            color: '#22c55e'
                          }}
                        >
                          ✓ Indexed
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => setSelectedPDF(doc.doc_id || doc.filename)}
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
                      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                      const docId = doc.doc_id || doc.filename;
                      window.open(`${apiUrl}/api/rag/pdf/${docId}`, '_blank');
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
          );
        })}
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
