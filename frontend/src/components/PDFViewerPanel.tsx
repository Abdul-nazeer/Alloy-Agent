import { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { X, ZoomIn, ZoomOut, ChevronLeft, ChevronRight, FileText } from 'lucide-react';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface BBox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface PDFViewerPanelProps {
  documentName: string;
  documentUrl: string;
  initialPage?: number;
  bboxes?: BBox[];
  onClose: () => void;
}

export default function PDFViewerPanel({
  documentName,
  documentUrl,
  initialPage = 1,
  bboxes = [],
  onClose
}: PDFViewerPanelProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(initialPage);
  const [scale, setScale] = useState<number>(1.2);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setPageNumber(initialPage);
  }, [initialPage]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
    setLoading(false);
    setError(null);
  };

  const onDocumentLoadError = (error: Error) => {
    console.error('PDF load error:', error);
    console.error('Document URL:', documentUrl);
    setError(`Failed to load PDF: ${error.message}`);
    setLoading(false);
  };

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPage = prevPageNumber + offset;
      return Math.min(Math.max(1, newPage), numPages);
    });
  };

  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 2.5));
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.6));

  const pageBBoxCount = bboxes.filter(b => b.page === pageNumber).length;

  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: 'var(--bg-surface)' }}>
      {/* Header */}
      <div 
        className="glass-card-elevated px-4 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--border-glow)' }}
      >
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <FileText className="w-5 h-5 flex-shrink-0" style={{ color: 'var(--accent-cyan)' }} />
          <div className="flex-1 min-w-0">
            <h3 
              className="text-sm font-mono text-uppercase-spaced truncate"
              style={{ color: 'var(--accent-cyan)' }}
            >
              {documentName}
            </h3>
            {pageBBoxCount > 0 && (
              <span 
                className="text-2xs font-mono"
                style={{ color: 'var(--text-tertiary)' }}
              >
                ✨ {pageBBoxCount} highlighted section{pageBBoxCount !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="glass-card p-2 rounded-sm hover-scale transition-smooth flex-shrink-0"
          style={{ color: 'var(--text-secondary)' }}
          title="Close PDF Viewer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Controls Bar */}
      <div 
        className="glass-card px-4 py-2 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--border-default)' }}
      >
        {/* Zoom Controls */}
        <div className="flex items-center space-x-2">
          <button
            onClick={zoomOut}
            className="glass-card p-1.5 rounded-sm hover-scale transition-smooth text-2xs"
            style={{ color: 'var(--text-secondary)' }}
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-2xs font-mono" style={{ color: 'var(--text-secondary)', minWidth: '45px', textAlign: 'center' }}>
            {Math.round(scale * 100)}%
          </span>
          <button
            onClick={zoomIn}
            className="glass-card p-1.5 rounded-sm hover-scale transition-smooth"
            style={{ color: 'var(--text-secondary)' }}
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Page Navigation */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => changePage(-1)}
            disabled={pageNumber <= 1}
            className="glass-card p-1.5 rounded-sm hover-scale transition-smooth disabled:opacity-30"
            style={{ color: 'var(--text-secondary)' }}
          >
            <ChevronLeft className="w-3.5 h-3.5" />
          </button>
          <span className="text-2xs font-mono" style={{ color: 'var(--text-primary)', minWidth: '70px', textAlign: 'center' }}>
            {numPages > 0 ? `${pageNumber} / ${numPages}` : '- / -'}
          </span>
          <button
            onClick={() => changePage(1)}
            disabled={pageNumber >= numPages}
            className="glass-card p-1.5 rounded-sm hover-scale transition-smooth disabled:opacity-30"
            style={{ color: 'var(--text-secondary)' }}
          >
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* PDF Content */}
      <div 
        className="flex-1 overflow-auto p-4"
        style={{ backgroundColor: 'var(--bg-elevated)' }}
      >
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div 
                className="animate-pulse text-sm font-mono"
                style={{ color: 'var(--text-secondary)' }}
              >
                Loading PDF...
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="glass-card p-6 rounded-sm max-w-md text-center">
              <div 
                className="text-sm font-mono mb-2"
                style={{ color: 'var(--status-critical)' }}
              >
                ⚠️ Failed to Load PDF
              </div>
              <div 
                className="text-2xs font-mono"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {error}
              </div>
              <div 
                className="text-2xs font-mono mt-3"
                style={{ color: 'var(--text-tertiary)' }}
              >
                Document: {documentName}
              </div>
            </div>
          </div>
        )}

        {!error && (
          <div className="flex justify-center">
            <Document
              file={documentUrl}
              options={{
                cMapUrl: `https://unpkg.com/pdfjs-dist@${pdfjs.version}/cmaps/`,
                cMapPacked: true,
                standardFontDataUrl: `https://unpkg.com/pdfjs-dist@${pdfjs.version}/standard_fonts/`
              }}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={onDocumentLoadError}
              loading={null}
              error={null}
            >
              <Page
                pageNumber={pageNumber}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
                loading={null}
              />
            </Document>
          </div>
        )}
      </div>

      {/* Footer */}
      <div 
        className="glass-card px-4 py-2 border-t text-center"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <span 
          className="text-2xs font-mono"
          style={{ color: 'var(--text-tertiary)' }}
        >
          Scroll to navigate • Arrow keys for pages
        </span>
      </div>
    </div>
  );
}
