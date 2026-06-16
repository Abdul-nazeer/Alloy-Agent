import { motion } from 'framer-motion';

const agents = [
  { name: 'Supervisor', role: 'Orchestration', color: '#00E5FF', angle: 0 },
  { name: 'Anomaly', role: 'Detection', color: '#00E5FF', angle: 60 },
  { name: 'Diagnosis', role: 'Analysis', color: '#00E5FF', angle: 120 },
  { name: 'Recommendation', role: 'Planning', color: '#00E5FF', angle: 180 },
  { name: 'Report', role: 'Documentation', color: '#00E5FF', angle: 240 },
  { name: 'Conversational', role: 'Interface', color: '#00E5FF', angle: 300 },
];

export default function MultiAgentSection() {
  return (
    <section className="relative min-h-screen py-20 flex items-center justify-center" style={{ background: '#050505' }}>
      <div className="container mx-auto px-6 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4"
        >
          AI Multi-Agent <span className="landing-text-gradient-cyan">Orchestration</span>
        </motion.h2>
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-xl text-[#B8C1CC] mb-16 max-w-3xl mx-auto"
        >
          Six specialized agents working in harmony. Like Jarvis for industrial maintenance.
        </motion.p>

        <div className="relative w-full max-w-4xl mx-auto h-[600px]">
          {/* Center Core */}
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="w-32 h-32 rounded-full landing-glass border-2 border-[#00E5FF] flex items-center justify-center"
              style={{ boxShadow: '0 0 40px rgba(0,229,255,0.5)' }}
            >
              <span className="text-lg font-bold text-[#00E5FF]">CORE</span>
            </motion.div>
          </div>

          {/* Orbiting Agents */}
          {agents.map((agent, i) => {
            const radius = 250;
            const x = Math.cos((agent.angle * Math.PI) / 180) * radius;
            const y = Math.sin((agent.angle * Math.PI) / 180) * radius;

            return (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, scale: 0 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="absolute top-1/2 left-1/2"
                style={{
                  transform: `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`,
                }}
              >
                <div
                  className="w-24 h-24 rounded-full landing-glass border-2 flex flex-col items-center justify-center cursor-pointer hover:scale-110 transition-transform"
                  style={{ borderColor: agent.color, boxShadow: `0 0 20px ${agent.color}40` }}
                >
                  <span className="text-sm font-bold text-white">{agent.name}</span>
                  <span className="text-xs text-[#B8C1CC]">{agent.role}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
