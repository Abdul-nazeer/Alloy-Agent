import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const messages = [
  { role: 'user', text: 'Why is AC-001 vibrating?' },
  { role: 'assistant', text: 'Analyzing AC-001... Bearing degradation detected. Current vibration: 3.2 mm/s (threshold: 3.0). Root cause: Insufficient lubrication. Recommendation: Replace bearing within 4 hours.', citations: ['Maintenance Manual p.42', 'Bearing Spec Sheet'] },
  { role: 'user', text: 'Show remaining useful life' },
  { role: 'assistant', text: 'AC-001 RUL Prediction:\n• Estimated: 38 days\n• Confidence: 89%\n• Next maintenance: 2024-07-25', citations: [] },
];

export default function AIAssistantSection() {
  const [visibleMessages, setVisibleMessages] = useState<typeof messages>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < messages.length) {
      const timer = setTimeout(() => {
        setVisibleMessages(prev => [...prev, messages[currentIndex]]);
        setCurrentIndex(prev => prev + 1);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [currentIndex]);

  return (
    <section className="relative min-h-screen py-20 flex items-center" style={{ background: '#050505' }}>
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4">
            AI <span className="landing-text-gradient-cyan">Assistant</span>
          </h2>
          <p className="text-xl text-[#B8C1CC]">Natural language interface to your entire maintenance system</p>
        </div>

        <div className="max-w-3xl mx-auto landing-glass rounded-2xl p-8 border border-[rgba(0,229,255,0.2)]">
          <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {visibleMessages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] p-4 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-[#00E5FF]/20 border border-[#00E5FF]/30'
                        : 'landing-glass border border-white/10'
                    }`}
                  >
                    <p className="text-white whitespace-pre-line">{msg.text}</p>
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-white/10">
                        {msg.citations.map((citation, j) => (
                          <div key={j} className="text-xs text-[#00E5FF] flex items-center gap-1">
                            <span>📄</span>
                            <span>{citation}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Ask about machine faults, procedures..."
              className="flex-1 px-4 py-3 rounded-lg landing-glass border border-white/10 text-white placeholder-[#6B7280] focus:outline-none focus:border-[#00E5FF]"
              readOnly
            />
            <button className="px-6 py-3 rounded-lg landing-btn-primary">
              Send
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
