import { useState, useRef, useEffect } from 'react';
import { agentAPI } from '../api/client';
import { Send, User, FileText, Paperclip, X } from 'lucide-react';
import AlloyAgentIcon from './AlloyAgentIcon';
import PDFViewerPanel from './PDFViewerPanel';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Array<{ 
    document?: string;
    doc_name?: string;  // Alternative field name
    source?: string;  // For backward compatibility
    section?: string;
    pages?: number[];
    page?: number;  // For backward compatibility
    bboxes?: any[];  // Bounding boxes for PDF highlights
  }>;
}

interface ChatPanelProps {
  compact?: boolean;
  initialMessage?: string;
}

export default function ChatPanel({ compact = false, initialMessage }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Live Monitor AI ready. Click a machine card or press Ctrl+Shift to run diagnosis.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [uploadingPDF, setUploadingPDF] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<{
    docName: string;
    docId: string;
    pages: number[];
    bboxes?: any[];
  } | null>(null);
  const [showPDFViewer, setShowPDFViewer] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Generate unique session ID for this chat instance (persists across component lifecycle)
  const [sessionId] = useState(() => `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);

  // Auto-submit initial message if provided
  useEffect(() => {
    if (initialMessage && !loading) {
      setInput(initialMessage);
      // Auto-submit after a short delay to allow UI to render
      setTimeout(() => {
        const fakeEvent = { preventDefault: () => {} } as React.FormEvent;
        handleSubmit(fakeEvent);
      }, 500);
    }
  }, [initialMessage]);

  const handleCitationClick = (citation: any) => {
    console.log('📖 Citation clicked:', citation);
    
    const docName = citation.document || citation.doc_name || citation.source || 'Unknown';
    const docId = citation.doc_id || docName.replace(/\s+/g, '_').toLowerCase();
    const pages = citation.pages || (citation.page ? [citation.page] : [1]);
    const bboxes = citation.bboxes || [];
    
    console.log('📄 Opening PDF viewer:', { docName, docId, pages, bboxesCount: bboxes.length });
    
    setSelectedCitation({
      docName,
      docId,
      pages,
      bboxes
    });
    setShowPDFViewer(true);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleFileAttach = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const pdfFiles = files.filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length < files.length) {
      alert('Only PDF files are supported');
    }
    
    setAttachedFiles(prev => [...prev, ...pdfFiles]);
    
    // Reset input
    if (e.target) {
      e.target.value = '';
    }
  };

  const removeAttachedFile = (index: number) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadPDFToKnowledgeBase = async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch('http://localhost:8000/api/rag/upload', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Failed to upload ${file.name}`);
    }

    const result = await response.json();
    return result.doc_name || file.name;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    console.log('🚀 Chat submit handler called');

    // If PDFs attached, upload them first
    let uploadedDocs: string[] = [];
    if (attachedFiles.length > 0) {
      setUploadingPDF(true);
      
      // Show uploading message
      const uploadingMessage: Message = {
        role: 'assistant',
        content: `📤 Uploading ${attachedFiles.length} PDF${attachedFiles.length > 1 ? 's' : ''} to knowledge base...`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, uploadingMessage]);

      try {
        // Upload all PDFs
        for (const file of attachedFiles) {
          const docName = await uploadPDFToKnowledgeBase(file);
          uploadedDocs.push(docName);
        }

        // Update message to show success
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: `✅ Indexed ${uploadedDocs.length} document${uploadedDocs.length > 1 ? 's' : ''}: ${uploadedDocs.join(', ')}\n\nNow I can answer your questions about ${uploadedDocs.length > 1 ? 'these documents' : 'this document'}.`,
            timestamp: new Date()
          };
          return updated;
        });

        await new Promise(resolve => setTimeout(resolve, 800)); // Brief pause so user sees confirmation

      } catch (error) {
        console.error('PDF upload error:', error);
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: 'assistant',
            content: `❌ Failed to upload PDFs: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date()
          };
          return updated;
        });
        setUploadingPDF(false);
        return;
      } finally {
        setUploadingPDF(false);
      }
    }

    const userMessage: Message = {
      role: 'user',
      content: input.trim() + (uploadedDocs.length > 0 ? `\n\n📎 Context: ${uploadedDocs.join(', ')}` : ''),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = input.trim();
    setInput('');
    
    // Clear attached files
    setAttachedFiles([]);
    
    setLoading(true);

    // Create placeholder assistant message
    const assistantMessage: Message = {
      role: 'assistant',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      console.log('📡 Calling chatStream endpoint...');
      // Use streaming endpoint with session ID for conversation continuity
      const response = await agentAPI.chatStream(messageText, sessionId);
      
      console.log('📡 Response received, status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      console.log('📖 Starting to read stream...');
      const decoder = new TextDecoder();
      let streamedContent = '';
      let buffer = '';

      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('✅ Stream complete');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue;
          
          try {
            const jsonStr = line.slice(6).trim();
            if (!jsonStr) continue;
            
            const data = JSON.parse(jsonStr);
            
            if (data.error) {
              console.error('❌ Stream error:', data.error);
              throw new Error(data.error);
            }
            
            if (data.token) {
              streamedContent += data.token;
              // Update the message content in real-time
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg && lastMsg.role === 'assistant') {
                  lastMsg.content = streamedContent;
                }
                return newMessages;
              });
            }
            
            if (data.done && data.metadata) {
              console.log('✅ Metadata received:', data.metadata);
              // Add citations when stream completes
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMsg = newMessages[newMessages.length - 1];
                if (lastMsg && lastMsg.role === 'assistant') {
                  lastMsg.citations = data.metadata.citations || [];
                }
                return newMessages;
              });
            }
          } catch (parseErr) {
            console.error('⚠️ Error parsing SSE line:', line, parseErr);
          }
        }
      }

      // If no content was streamed, there was an error
      if (!streamedContent.trim()) {
        console.error('❌ No content received from stream');
        throw new Error('No content received from stream');
      }

      console.log(`✅ Successfully streamed ${streamedContent.length} characters`);

    } catch (error) {
      console.error('❌ Chat streaming error:', error);
      
      // Remove the empty assistant message and add error message
      setMessages(prev => {
        const newMessages = prev.slice(0, -1);
        return [...newMessages, {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
          timestamp: new Date()
        }];
      });
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex h-full space-x-4">
      {/* Chat Panel - Takes remaining space */}
      <div 
        className={`flex flex-col rounded-sm transition-all ${showPDFViewer ? 'flex-1' : 'w-full'}`}
        style={{ 
          backgroundColor: 'var(--bg-surface)',
          border: compact ? 'none' : '1px solid var(--border-default)'
        }}
      >
      {/* Header - Minimal */}
      <div 
        className="glass-card-elevated px-4 py-2 border-b"
        style={{ borderColor: 'var(--border-glow)' }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlloyAgentIcon size={24} animated={true} />
            <h2 
              className="heading-secondary text-xs text-uppercase-spaced"
              style={{ color: 'var(--accent-cyan)' }}
            >
              CHAT ASSISTANT
            </h2>
          </div>
          <div className="flex items-center space-x-2">
            <span className="status-dot status-normal pulse-dot" style={{ width: '6px', height: '6px' }} />
            <span className="text-2xs text-mono text-uppercase-spaced" style={{ color: 'var(--status-normal)' }}>
              ONLINE
            </span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, idx) => (
          <div
            key={idx}
            className={`flex space-x-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0">
                <AlloyAgentIcon size={28} />
              </div>
            )}

            <div className={`flex flex-col max-w-2xl ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div
                className="rounded-sm px-3 py-2 text-sm font-sans"
                style={{
                  backgroundColor: message.role === 'user' ? 'var(--bg-elevated)' : 'transparent',
                  border: message.role === 'assistant' ? '1px solid var(--border-subtle)' : 'none',
                  color: 'var(--text-primary)'
                }}
              >
                <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                
                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="mt-3 pt-3 space-y-2" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                    <div className="flex items-center space-x-2 mb-2">
                      <FileText className="w-3.5 h-3.5" style={{ color: 'var(--accent-cyan)' }} />
                      <span className="text-2xs text-mono text-uppercase-spaced" style={{ color: 'var(--accent-cyan)' }}>
                        SOURCES ({message.citations.length})
                      </span>
                    </div>
                    {message.citations.map((citation, i) => {
                      const docName = citation.document || citation.doc_name || citation.source || 'Unknown Document';
                      const section = citation.section;
                      const pages = citation.pages && citation.pages.length > 0 
                        ? citation.pages.join(', ') 
                        : citation.page 
                        ? String(citation.page)
                        : null;
                      
                      return (
                        <div 
                          key={i} 
                          onClick={() => handleCitationClick(citation)}
                          className="glass-card px-3 py-2 rounded-sm hover-scale-sm transition-smooth cursor-pointer"
                          style={{ 
                            borderLeft: '2px solid var(--accent-cyan)',
                            backgroundColor: 'rgba(0, 229, 255, 0.05)'
                          }}
                          title="Click to view document with highlighted sections"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2">
                                <span 
                                  className="text-xs font-mono font-medium"
                                  style={{ color: 'var(--accent-cyan)' }}
                                >
                                  [{i + 1}]
                                </span>
                                <span 
                                  className="text-xs font-mono"
                                  style={{ color: 'var(--text-primary)' }}
                                >
                                  {docName}
                                </span>
                              </div>
                              <div className="mt-1 flex flex-wrap items-center gap-2 text-2xs font-mono" style={{ color: 'var(--text-tertiary)' }}>
                                {section && (
                                  <span>📑 {section}</span>
                                )}
                                {pages && (
                                  <span>📄 Page{citation.pages && citation.pages.length > 1 ? 's' : ''} {pages}</span>
                                )}
                                {citation.bboxes && citation.bboxes.length > 0 && (
                                  <span className="px-1.5 py-0.5 rounded" style={{ backgroundColor: 'rgba(0, 229, 255, 0.2)', color: 'var(--accent-cyan)' }}>
                                    ✨ Highlighted
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
              
              <span 
                className="text-2xs font-mono mt-1"
                style={{ color: 'var(--text-tertiary)' }}
              >
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
            </div>

            {message.role === 'user' && (
              <div 
                className="flex-shrink-0 w-6 h-6 rounded-sm flex items-center justify-center"
                style={{ backgroundColor: 'var(--bg-elevated)' }}
              >
                <User className="w-3 h-3" style={{ color: 'var(--text-secondary)' }} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex space-x-3">
            <div className="flex-shrink-0">
              <AlloyAgentIcon size={28} animated={true} />
            </div>
            <div 
              className="glass-card px-4 py-2 rounded-lg text-sm text-mono"
              style={{ color: 'var(--text-secondary)' }}
            >
              <span className="animate-pulse">Analyzing...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area with Attachment */}
      <div 
        className="glass-card p-4 border-t"
        style={{ borderColor: 'var(--border-default)' }}
      >
        {/* Attached Files Preview */}
        {attachedFiles.length > 0 && (
          <div className="mb-3 flex flex-wrap gap-2">
            {attachedFiles.map((file, index) => (
              <div
                key={index}
                className="glass-card-elevated px-3 py-2 rounded-lg flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
                <span className="text-xs text-mono" style={{ color: 'var(--text-primary)' }}>
                  {file.name}
                </span>
                <button
                  onClick={() => removeAttachedFile(index)}
                  className="hover-scale transition-fast"
                  style={{ color: 'var(--text-tertiary)' }}
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex items-end space-x-2">
          {/* Attach Button */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="glass-card p-3 rounded-lg hover-scale transition-smooth"
            style={{ color: 'var(--text-secondary)' }}
            title="Upload PDF to knowledge base and query it"
            disabled={uploadingPDF || loading}
          >
            <Paperclip className="w-5 h-5" />
          </button>
          
          {/* Hidden File Input */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            multiple
            onChange={handleFileAttach}
            className="hidden"
          />
          
          {/* Text Input */}
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask about equipment failures, procedures, anomalies, maintenance recommendations..."
            className="flex-1 px-4 py-3 rounded-lg text-sm text-body resize-none focus:outline-none glass-card transition-smooth"
            style={{
              border: '1px solid var(--border-default)',
              color: 'var(--text-primary)',
              minHeight: '60px'
            }}
            rows={2}
            disabled={loading}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--accent-cyan)';
              e.target.style.boxShadow = '0 0 20px rgba(0, 229, 255, 0.3)';
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--border-default)';
              e.target.style.boxShadow = 'none';
            }}
          />
          
          {/* Send Button - Floating Gradient */}
          <button
            type="submit"
            disabled={loading || uploadingPDF || !input.trim()}
            className="btn-primary p-4 rounded-lg hover-scale transition-smooth disabled:opacity-50 disabled:cursor-not-allowed"
            style={{
              background: 'linear-gradient(135deg, var(--accent-cyan), #0099CC)',
              color: '#000',
              boxShadow: '0 4px 12px rgba(0, 229, 255, 0.3)'
            }}
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
        
        {/* Help Text */}
        <div className="mt-2 flex items-center justify-between text-2xs text-mono" style={{ color: 'var(--text-tertiary)' }}>
          <span>Press Enter to send • Shift+Enter for new line</span>
          <span>📎 Attach PDFs - they'll be indexed automatically for Q&A</span>
        </div>
      </div>
      </div>

      {/* PDF Viewer Panel - Side by side */}
      {showPDFViewer && selectedCitation && (
        <div 
          className="flex-1 rounded-sm overflow-hidden"
          style={{ 
            border: '1px solid var(--border-default)',
            minWidth: '500px',
            maxWidth: '50%'
          }}
        >
          <PDFViewerPanel
            documentName={selectedCitation.docName}
            documentUrl={`http://localhost:8000/api/rag/pdf/${selectedCitation.docId}`}
            initialPage={selectedCitation.pages[0] || 1}
            bboxes={selectedCitation.bboxes}
            onClose={() => setShowPDFViewer(false)}
          />
        </div>
      )}
    </div>
  );
}
