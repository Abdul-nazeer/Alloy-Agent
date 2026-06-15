import { useState, useRef, useEffect } from 'react';
import { agentAPI } from '../api/client';
import { Send, Bot, User, FileText } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Array<{ source: string; page?: number }>;
}

interface ChatPanelProps {
  compact?: boolean;
}

export default function ChatPanel({ compact = false }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Live Monitor AI ready. Click a machine card or press Ctrl+Shift to run diagnosis.',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageText = input.trim();
    setInput('');
    setLoading(true);

    try {
      // Use regular chat endpoint (streaming disabled for now - compatibility issues)
      const response = await agentAPI.chat(messageText);
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.response || response.data.answer || 'No response',
        timestamp: new Date(),
        citations: response.data.citations || []
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Error processing request. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div 
      className={`flex flex-col ${compact ? 'h-full' : 'h-full'} rounded-sm`}
      style={{ 
        backgroundColor: 'var(--bg-surface)',
        border: compact ? 'none' : '1px solid var(--border-default)'
      }}
    >
      {/* Header */}
      <div 
        className="flex items-center justify-between px-4 py-3 border-b"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <div className="flex items-center space-x-3">
          <div 
            className="p-2 rounded-sm"
            style={{ backgroundColor: 'var(--bg-elevated)' }}
          >
            <Bot className="w-4 h-4" style={{ color: 'var(--accent-cyan)' }} />
          </div>
          <div>
            <h2 
              className="text-xs font-mono tracking-widest"
              style={{ color: 'var(--text-primary)' }}
            >
              🤖 AI ASSISTANT
            </h2>
            <p 
              className="text-2xs font-mono"
              style={{ color: 'var(--text-secondary)' }}
            >
              Powered by RAG + Fine-tuned Phi-3
            </p>
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
              <div 
                className="flex-shrink-0 w-6 h-6 rounded-sm flex items-center justify-center"
                style={{ backgroundColor: 'var(--bg-elevated)' }}
              >
                <Bot className="w-3 h-3" style={{ color: 'var(--accent-cyan)' }} />
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
                  <div className="mt-2 pt-2 space-y-1" style={{ borderTop: '1px solid var(--border-subtle)' }}>
                    {message.citations.map((citation, i) => (
                      <div key={i} className="flex items-center space-x-2 text-xs">
                        <FileText className="w-3 h-3" style={{ color: 'var(--accent-cyan)' }} />
                        <span className="font-mono" style={{ color: 'var(--accent-cyan)' }}>
                          {citation.source}
                        </span>
                        {citation.page && (
                          <span className="font-mono" style={{ color: 'var(--text-tertiary)' }}>
                            • Page {citation.page}
                          </span>
                        )}
                      </div>
                    ))}
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
            <div 
              className="flex-shrink-0 w-6 h-6 rounded-sm flex items-center justify-center"
              style={{ backgroundColor: 'var(--bg-elevated)' }}
            >
              <Bot className="w-3 h-3" style={{ color: 'var(--accent-cyan)' }} />
            </div>
            <div 
              className="px-3 py-2 rounded-sm text-sm font-mono"
              style={{ 
                backgroundColor: 'var(--bg-elevated)',
                color: 'var(--text-secondary)'
              }}
            >
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div 
        className="p-4 border-t"
        style={{ borderColor: 'var(--border-default)' }}
      >
        <form onSubmit={handleSubmit} className="flex space-x-2">
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
            placeholder="Ask about machine faults, procedures..."
            className="flex-1 px-3 py-2 rounded-sm text-sm font-sans resize-none focus:outline-none"
            style={{
              backgroundColor: 'var(--bg-elevated)',
              border: '1px solid var(--border-default)',
              color: 'var(--text-primary)'
            }}
            rows={2}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="px-4 py-2 rounded-sm transition-all disabled:opacity-50"
            style={{
              backgroundColor: 'var(--accent-cyan)',
              color: 'var(--bg-base)'
            }}
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
