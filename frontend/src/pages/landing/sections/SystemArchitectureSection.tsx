import { motion } from 'framer-motion';

const pipeline = [
  { name: 'IoT Sensors', icon: '📡' },
  { name: 'WebSocket Streaming', icon: '🔄' },
  { name: 'FastAPI Backend', icon: '⚡' },
  { name: 'LangGraph Agents', icon: '🤖' },
  { name: 'RAG Engine', icon: '🧠' },
  { name: 'Qdrant Vector DB', icon: '💾' },
  { name: 'LLMs', icon: '🎯' },
  { name: 'Dashboard', icon: '📊' },
];

export default function SystemArchitectureSection() {
  return (
    <section className="relative min-h-screen py-20 flex items-center" style={{ background: '#050505' }}>
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4">
            System <span className="landing-text-gradient-cyan">Architecture</span>
          </h2>
          <p className="text-xl text-[#B8C1CC]">Production-grade infrastructure built for reliability</p>
        </div>

        <div className="max-w-3xl mx-auto">
          {pipeline.map((stage, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-full landing-glass border border-[#00E5FF] flex items-center justify-center text-2xl">
                  {stage.icon}
                </div>
                <div className="flex-1 landing-glass rounded-lg p-4 border border-[rgba(0,229,255,0.2)]">
                  <span className="text-white font-semibold">{stage.name}</span>
                </div>
              </div>
              
              {i < pipeline.length - 1 && (
                <div className="flex justify-center my-2">
                  <motion.div
                    initial={{ scaleY: 0 }}
                    whileInView={{ scaleY: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.1 + 0.05 }}
                    className="w-0.5 h-8 origin-top"
                    style={{ background: 'linear-gradient(180deg, #00E5FF 0%, #FF6A00 100%)' }}
                  />
                </div>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
