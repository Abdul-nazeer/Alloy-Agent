import { motion } from 'framer-motion';

const metrics = [
  { value: '63%', label: 'Reduction in Downtime', icon: '📉' },
  { value: '3x', label: 'Faster Diagnosis', icon: '⚡' },
  { value: '89%', label: 'Failure Prevention', icon: '🛡️' },
  { value: '$0', label: 'Infrastructure Cost', icon: '💰' },
  { value: '<50ms', label: 'Streaming Latency', icon: '🚀' },
  { value: '100%', label: 'Autonomous Monitoring', icon: '🤖' },
];

export default function BusinessImpactSection() {
  return (
    <section className="relative min-h-screen py-20 flex items-center" style={{ background: 'linear-gradient(180deg, #0A0A0A 0%, #050505 100%)' }}>
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4">
            Business <span className="landing-text-gradient-orange">Impact</span>
          </h2>
          <p className="text-xl text-[#B8C1CC]">Measurable results that matter</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {metrics.map((metric, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ y: -10, rotateX: 5 }}
              className="landing-metric-card"
            >
              <div className="text-5xl mb-4">{metric.icon}</div>
              <div className="text-5xl font-bold landing-text-gradient-cyan mb-2">
                {metric.value}
              </div>
              <div className="text-lg text-[#B8C1CC]">{metric.label}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
