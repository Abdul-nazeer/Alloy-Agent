import { motion } from 'framer-motion';
import { Bot, Zap, FileText, Bell, MessageSquare, Database, TrendingUp, Package, Activity } from 'lucide-react';

export default function FeaturesSection() {
  return (
    <section
      id="features"
      className="min-h-screen relative flex items-center justify-center py-20"
      style={{ background: 'linear-gradient(180deg, #0A0A0A 0%, #050505 100%)' }}
    >
      <div className="container mx-auto px-6 lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl lg:text-7xl font-black landing-heading mb-6 text-white">
            What We Built
          </h2>
          <p className="text-xl text-[#B8C1CC] max-w-3xl mx-auto">
            Real-time monitoring, AI diagnosis, and automated reporting for industrial equipment
          </p>
        </motion.div>

        {/* Main Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          <FeatureCard
            icon={<Activity className="w-8 h-8" />}
            title="Live Sensor Streams"
            description="WebSocket pushes data every 15 seconds. Temp, pressure, vibration, current, RPM - the works."
            badge="<50ms"
          />

          <FeatureCard
            icon={<Zap className="w-8 h-8" />}
            title="Anomaly Detection"
            description="Catches issues fast. Threshold checks for obvious stuff, ML for subtle patterns. Alerts in under 3 seconds."
            badge="Dual-layer"
          />

          <FeatureCard
            icon={<Bot className="w-8 h-8" />}
            title="Six AI Agents"
            description="Built with LangGraph. Each agent has a job - anomaly detection, diagnosis, recommendations, reports, chat."
            badge="LangGraph"
          />

          <FeatureCard
            icon={<FileText className="w-8 h-8" />}
            title="RAG Search"
            description="2,606 chunks from maintenance PDFs. Dense + sparse search with reranking. Finds the right procedure."
            badge="Hybrid"
          />

          <FeatureCard
            icon={<Bell className="w-8 h-8" />}
            title="Dashboard Alerts"
            description="Critical issues show up instantly. No email delays, just dashboard notifications."
            badge="Instant"
          />

          <FeatureCard
            icon={<MessageSquare className="w-8 h-8" />}
            title="Chat Interface"
            description="Ask questions, get answers. Understands equipment context and maintenance history."
            badge="NLP"
          />
        </div>

        {/* Secondary Features */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3 }}
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-6 mb-16"
        >
          <SecondaryFeature
            icon={<Database className="w-6 h-6" />}
            title="Operations Logbook"
            description="Auto-logs everything - incidents, diagnoses, repairs. Full timestamps and action history."
            color="#FFFFFF"
          />

          <SecondaryFeature
            icon={<TrendingUp className="w-6 h-6" />}
            title="Historical Analysis"
            description="Trained on 845K records from NASA C-MAPSS. Spots patterns and predicts failures."
            color="#FFFFFF"
          />

          <SecondaryFeature
            icon={<Package className="w-6 h-6" />}
            title="Parts Inventory"
            description="Track what's in stock, what's low, what you need. Integrated with repair workflows."
            color="#FFFFFF"
          />
        </motion.div>

        {/* Showcase Feature - AI Reports */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          viewport={{ once: true }}
          className="landing-glass rounded-2xl p-8 lg:p-12 border-2 border-[rgba(255,106,0,0.3)]"
        >
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <div className="inline-block px-4 py-2 rounded-full mb-4" style={{ backgroundColor: '#00E5FF20', border: '1px solid #00E5FF', color: '#00E5FF' }}>
                <span className="text-xs font-mono font-bold">FLAGSHIP FEATURE</span>
              </div>
              <h3 className="text-3xl font-bold text-white mb-4">
                Auto-Generated Reports
              </h3>
              <p className="text-lg text-[#B8C1CC] mb-6">
                When equipment fails, the system writes a full maintenance report. Fault description, root cause, repair steps, long-term fixes.
              </p>
              <div className="space-y-3">
                <ReportFeature text="Fault analysis from live sensor data" />
                <ReportFeature text="Root cause with confidence scores" />
                <ReportFeature text="Immediate actions to stop damage" />
                <ReportFeature text="Step-by-step repair procedures" />
                <ReportFeature text="Long-term recommendations" />
              </div>
            </div>

            <div className="landing-glass rounded-xl p-6 border border-[rgba(255,106,0,0.3)]">
              <div className="space-y-4 font-mono text-sm">
                <div>
                  <div className="text-[#00E5FF] font-bold mb-2">📋 INCIDENT DETAILS</div>
                  <div className="text-[#B8C1CC] text-xs">
                    Alert: 3 anomalies detected<br/>
                    Equipment: Air Compressor AC-001<br/>
                    Severity: HIGH
                  </div>
                </div>
                <div>
                  <div className="text-[#00FF85] font-bold mb-2">⚡ IMMEDIATE ACTIONS</div>
                  <div className="text-[#B8C1CC] text-xs">
                    1. Reduce compressor load to 60%<br/>
                    2. Monitor bearing temperature<br/>
                    3. Check oil levels and quality<br/>
                    4. Inspect for unusual vibration
                  </div>
                </div>
                <div>
                  <div className="text-[#00E5FF] font-bold mb-2">🔧 REPAIR PROCEDURE</div>
                  <div className="text-[#B8C1CC] text-xs">
                    Phase 1: System shutdown<br/>
                    Phase 2: Component inspection<br/>
                    Phase 3: Replace damaged parts<br/>
                    Phase 4: Testing and validation
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          viewport={{ once: true }}
          className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6"
        >
          <StatBox value="5" label="Equipment" sublabel="Types monitored" />
          <StatBox value="2.6K" label="KB Chunks" sublabel="Maintenance docs" />
          <StatBox value="845K" label="Records" sublabel="Training data" />
          <StatBox value="<3s" label="Response" sublabel="Full diagnosis" />
        </motion.div>
      </div>
    </section>
  );
}

// Feature Card Component
function FeatureCard({
  icon,
  title,
  description,
  badge,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  badge?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      whileInView={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      viewport={{ once: true }}
      whileHover={{ scale: 1.05 }}
      className="landing-glass rounded-xl p-6 border transition-all"
      style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#FFFFFF' }}>
          {icon}
        </div>
        {badge && (
          <span
            className="px-2 py-1 rounded text-xs font-mono font-bold"
            style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#B8C1CC' }}
          >
            {badge}
          </span>
        )}
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-sm text-[#B8C1CC]">{description}</p>
    </motion.div>
  );
}

// Secondary Feature Component
function SecondaryFeature({
  icon,
  title,
  description,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}) {
  return (
    <div className="landing-glass rounded-xl p-6 border border-[rgba(255,255,255,0.1)]">
      <div className="flex items-center gap-3 mb-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}20`, color }}>
          {icon}
        </div>
        <h4 className="font-bold text-white">{title}</h4>
      </div>
      <p className="text-sm text-[#B8C1CC]">{description}</p>
    </div>
  );
}

// Report Feature Item
function ReportFeature({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-5 h-5 rounded-full flex items-center justify-center" style={{ backgroundColor: '#00E5FF20' }}>
        <span className="text-xs" style={{ color: '#00E5FF' }}>✓</span>
      </div>
      <span className="text-sm text-[#B8C1CC]">{text}</span>
    </div>
  );
}

// Stat Box Component
function StatBox({ value, label, sublabel }: { value: string; label: string; sublabel: string }) {
  return (
    <div className="landing-glass rounded-xl p-6 border border-[rgba(255,255,255,0.1)] text-center">
      <div className="text-3xl font-black landing-mono mb-2 text-[#00E5FF]">{value}</div>
      <div className="text-sm font-bold text-white mb-1">{label}</div>
      <div className="text-xs text-[#B8C1CC]">{sublabel}</div>
    </div>
  );
}
