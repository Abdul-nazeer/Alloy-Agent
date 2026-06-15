import { motion } from 'framer-motion';

interface FinalCTASectionProps {
  onLaunchDashboard: () => void;
}

export default function FinalCTASection({ onLaunchDashboard }: FinalCTASectionProps) {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden" style={{ background: '#000' }}>
      {/* Background */}
      <div className="absolute inset-0">
        <div className="landing-grid opacity-10" />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="absolute inset-0"
          style={{
            background: 'radial-gradient(circle at 50% 50%, rgba(0,229,255,0.1) 0%, transparent 50%)',
          }}
        />
      </div>

      <div className="relative z-10 container mx-auto px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="space-y-8"
        >
          <h2 className="text-5xl lg:text-7xl font-bold landing-heading text-white mb-6">
            Welcome to the Future of
            <br />
            <span className="landing-text-gradient-cyan">Industrial Maintenance Intelligence</span>
          </h2>

          <p className="text-xl lg:text-2xl text-[#B8C1CC] max-w-3xl mx-auto">
            Join the autonomous revolution. Let AI handle the monitoring,
            <br />
            while you focus on what matters.
          </p>

          <div className="flex flex-wrap justify-center gap-6 pt-8">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onLaunchDashboard}
              className="landing-btn-primary text-xl px-8 py-4"
            >
              Launch Dashboard
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="landing-btn-secondary text-xl px-8 py-4"
            >
              View Documentation
            </motion.button>
          </div>

          {/* Stats Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
            className="pt-16 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            <div>
              <div className="text-3xl font-bold landing-text-gradient-cyan">5</div>
              <div className="text-sm text-[#6B7280]">Equipment Monitored</div>
            </div>
            <div>
              <div className="text-3xl font-bold landing-text-gradient-cyan">24/7</div>
              <div className="text-sm text-[#6B7280]">Autonomous Operation</div>
            </div>
            <div>
              <div className="text-3xl font-bold landing-text-gradient-cyan">6</div>
              <div className="text-sm text-[#6B7280]">AI Agents</div>
            </div>
            <div>
              <div className="text-3xl font-bold landing-text-gradient-cyan">100%</div>
              <div className="text-sm text-[#6B7280]">Open Source</div>
            </div>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
