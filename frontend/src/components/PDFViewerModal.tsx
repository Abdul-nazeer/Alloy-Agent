import { useState, useEffect, useRef } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import { X, ZoomIn, ZoomOut, ChevronLeft, ChevronRight } from 'lucide-react';

// Configure PDF.js worker
pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.js`;

interface BBox {
  page: number;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface PDFViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentName: string;
  documentUrl: string;
  initialPage?: number;
  bboxes?: BBox[];
}

export default function PDFViewerModal({
  isOpen,
  onClose,
  documentName,
  documentUrl,
  initialPage = 1,
  bboxes = []
}: PDFViewerModalProps) {
  const [numPages, setNumPages] = useState<number>(0);
  const [pageNumber, setPageNumber] = useState<number>(initialPage);
  const [scale, setScale] = useState<number>(1.0);
  const [pageWidth, setPageWidth] = useState<number>(800);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      setPageNumber(initialPage);
    }
  }, [isOpen, initialPage]);

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  const changePage = (offset: number) => {
    setPageNumber(prevPageNumber => {
      const newPage = prevPageNumber + offset;
      return Math.min(Math.max(1, newPage), numPages);
    });
  };

  const zoomIn = () => setScale(prev => Math.min(prev + 0.2, 3.0));
  const zoomOut = () => setScale(prev => Math.max(prev - 0.2, 0.5));

  // Draw bboxes on canvas overlay
  const drawBBoxes = () => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Filter bboxes for current page
    const pageBBoxes = bboxes.filter(bbox => bbox.page === pageNumber);

    if (pageBBoxes.length === 0) return;

    // Draw each bbox
    pageBBoxes.forEach(bbox => {
      // Convert PDF coordinates to canvas coordinates
      // PDF coordinates are from bottom-left, canvas is from top-left
      const x = bbox.x * scale;
      const y = (canvas.height - (bbox.y + bbox.height)) * scale;
      const width = bbox.width * scale;
      const height = bbox.height * scale;

      // Draw semi-transparent yellow rectangle
      ctx.fillStyle = 'rgba(0, 229, 255, 0.2)';
      ctx.fillRect(x, y, width, height);

      // Draw cyan border
      ctx.strokeStyle = 'rgba(0, 229, 255, 0.8)';
      ctx.lineWidth = 2;
      ctx.strokeRect(x, y, width, height);
    });
  };

  useEffect(() => {
    drawBBoxes();
  }, [pageNumber, scale, bboxes]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.9)' }}
      onClick={onClose}
    >
      <div 
        className="relative w-full h-full max-w-6xl max-h-screen p-4 flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div 
          className="glass-card-elevated px-4 py-3 mb-4 rounded-sm flex items-center justify-between"
          style={{ borderColor: 'var(--border-glow)' }}
        >
          <div className="flex items-center space-x-3">
            <h3 
              className="text-sm font-mono text-uppercase-spaced"
              style={{ color: 'var(--accent-cyan)' }}
            >
              📄 {documentName}
            </h3>
            {bboxes.length > 0 && (
              <span 
                className="text-2xs px-2 py-1 rounded"
                style={{ 
                  backgroundColor: 'rgba(0, 229, 255, 0.2)',
                  color: 'var(--accent-cyan)'
                }}
              >
                ✨ {bboxes.filter(b => b.page === pageNumber).length} Highlighted Section{bboxes.filter(b => b.page === pageNumber).length !== 1 ? 's' : ''}
              </span>
            )}
          </div>
          
          {/* Controls */}
          <div className="flex items-center space-x-2">
            {/* Zoom Controls */}
            <button
              onClick={zoomOut}
              className="glass-card p-2 rounded-sm hover-scale transition-smooth"
              style={{ color: 'var(--text-secondary)' }}
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span className="text-xs font-mono" style={{ color: 'var(--text-secondary)' }}>
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={zoomIn}
              className="glass-card p-2 rounded-sm hover-scale transition-smooth"
              style={{ color: 'var(--text-secondary)' }}
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4" />
            </button>

            {/* Page Navigation */}
            <div className="ml-4 flex items-center space-x-2">
              <button
                onClick={() => changePage(-1)}
                disabled={pageNumber <= 1}
                className="glass-card p-2 rounded-sm hover-scale transition-smooth disabled:opacity-50"
                style={{ color: 'var(--text-secondary)' }}
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-xs font-mono" style={{ color: 'var(--text-primary)' }}>
                Page {pageNumber} / {numPages}
              </span>
              <button
                onClick={() => changePage(1)}
                disabled={pageNumber >= numPages}
                className="glass-card p-2 rounded-sm hover-scale transition-smooth disabled:opacity-50"
                style={{ color: 'var(--text-secondary)' }}
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            {/* Close Button */}
            <button
              onClick={onClose}
              className="ml-4 glass-card p-2 rounded-sm hover-scale transition-smooth"
              style={{ color: 'var(--text-secondary)' }}
              title="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* PDF Viewer */}
        <div 
          ref={containerRef}
          className="flex-1 overflow-auto glass-card rounded-sm p-4 relative"
          style={{ backgroundColor: 'rgba(15, 23, 42, 0.8)' }}
        >
          <div className="flex justify-center">
            <div className="relative inline-block">
              <Document
                file={documentUrl}
                onLoadSuccess={onDocumentLoadSuccess}
                loading={
                  <div className="text-center py-20" style={{ color: 'var(--text-secondary)' }}>
                    <div className="animate-pulse">Loading PDF...</div>
                  </div>
                }
                error={
                  <div className="text-center py-20" style={{ color: 'var(--status-critical)' }}>
                    Failed to load PDF. Please check if the document exists.
                  </div>
                }
              >
                <Page
                  pageNumber={pageNumber}
                  scale={scale}
                  width={pageWidth}
                  onLoadSuccess={(page) => {
                    setPageWidth(page.width);
                    // Set canvas dimensions
                    if (canvasRef.current) {
                      canvasRef.current.width = page.width * scale;
                      canvasRef.current.height = page.height * scale;
                      drawBBoxes();
                    }
                  }}
                  renderTextLayer={true}
                  renderAnnotationLayer={false}
                />
              </Document>
              
              {/* BBox Overlay Canvas */}
              <canvas
                ref={canvasRef}
                className="absolute top-0 left-0 pointer-events-none"
                style={{ 
                  mixBlendMode: 'multiply',
                  opacity: 0.8
                }}
              />
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div 
          className="glass-card mt-4 px-4 py-2 rounded-sm text-2xs font-mono text-center"
          style={{ color: 'var(--text-tertiary)' }}
        >
          Use mouse wheel to scroll • Arrow keys to navigate pages • ESC to close
        </div>
      </div>
    </div>
  );
}
