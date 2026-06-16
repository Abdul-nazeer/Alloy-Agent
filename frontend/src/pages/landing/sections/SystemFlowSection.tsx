import { motion } from 'framer-motion';
import { Activity, AlertTriangle, Brain, FileText, CheckCircle, ArrowRight } from 'lucide-react';
import MermaidDiagram from '../../../components/MermaidDiagram';

export default function SystemFlowSection() {
  return (
    <section
      id="system-flow"
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
            How It Works
          </h2>
          <p className="text-xl text-[#B8C1CC] max-w-3xl mx-auto">
            Sensor data → Anomaly detection → AI agents → Maintenance report. All in under 3 seconds.
          </p>
        </motion.div>

        {/* Vertical Flow Diagram */}
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Step 1: Data Collection */}
          <FlowStep
            number="01"
            icon={<Activity className="w-8 h-8" />}
            title="Real-Time Data Collection"
            description="Equipment streams sensor data every 15 seconds via WebSocket"
            
            details={[
              'Temperature, pressure, vibration, current, RPM - the usual suspects',
              'We track Compressors, Fans, Rolling Mills, and Motors',
              'Mix of simulated data + NASA C-MAPSS historical dataset',
              'Everything gets stored in SQLite for later analysis',
            ]}
            tech="WebSocket + SQLite + FastAPI"
          />

          <FlowArrow />

          {/* Step 2: Anomaly Detection */}
          <FlowStep
            number="02"
            icon={<AlertTriangle className="w-8 h-8" />}
            title="Anomaly Detection"
            description="Two layers catch problems - rules for obvious stuff, ML for the subtle stuff"
            
            details={[
              '**Threshold Detection**: Simple min/max bounds - if temp exceeds 100°C something is wrong',
              '**Pattern Recognition**: ML model trained on C-MAPSS spots degradation patterns',
              '**Confidence Scoring**: LOW/MEDIUM/HIGH/CRITICAL based on severity',
              '**Alert Generation**: Fires within 3 seconds when something looks off',
            ]}
            tech="Threshold Logic + ML Patterns"
          />

          <FlowArrow />

          {/* Step 3: Multi-Agent Diagnosis */}
          <FlowStep
            number="03"
            icon={<Brain className="w-8 h-8" />}
            title="Multi-Agent AI Diagnosis"
            description="Six specialized agents work together - think of it like a maintenance team"
            
            details={[
              '**Supervisor**: The manager - routes work to the right agents',
              '**Anomaly Agent**: Looks at sensor patterns and spots abnormal behavior',
              '**Diagnosis Agent**: Digs into maintenance manuals (RAG) for root cause',
              '**Recommendation Agent**: Figures out what to fix and how',
              '**Report Agent**: Writes everything down in proper documentation',
              '**Chat Agent**: Lets you ask questions in plain English',
            ]}
            tech="LangGraph + Groq Llama 3.1 + Qdrant RAG"
          />

          <FlowArrow />

          {/* Step 4: Knowledge Retrieval */}
          <FlowStep
            number="04"
            icon={<FileText className="w-8 h-8" />}
            title="RAG Knowledge Retrieval"
            description="We search 2,606 chunks from maintenance manuals to find relevant info"
            
            details={[
              '**Dense Retrieval**: all-MiniLM embeddings find semantically similar text',
              '**Sparse Retrieval**: BM25 does keyword matching for exact terms',
              '**Reranking**: BGE reranker sorts results by relevance',
              '**Context Fusion**: Top 5 chunks get fed to the LLM',
              '**Citation Tracking**: Links back to source PDFs with page numbers',
            ]}
            tech="Qdrant + Sentence Transformers + BM25"
          />

          <FlowArrow />

          {/* Step 5: Action & Documentation */}
          <FlowStep
            number="05"
            icon={<CheckCircle className="w-8 h-8" />}
            title="Autonomous Action & Documentation"
            description="System generates reports and notifies the right people"
            
            details={[
              '**Automated Reports**: AI writes up the incident with repair steps',
              '**Operations Logbook**: Detailed records of what happened and what to do',
              '**Team Notifications**: Critical alerts hit the dashboard immediately',
              '**Spare Parts Check**: Makes sure you have the parts before starting repairs',
              '**Historical Archive**: Everything saved for trend analysis',
            ]}
            tech="SQLite + FastAPI + Report Generator"
          />
        </div>

        {/* Performance Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-16 landing-glass rounded-2xl p-8 border"
          style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
        >
          <h3 className="text-3xl font-bold text-center mb-8 text-white">
            Numbers
          </h3>
          <div className="grid md:grid-cols-4 gap-6">
            <MetricBox
              value="<3s"
              label="Detection to Report"
              description="End-to-end"
            />
            <MetricBox
              value="<50ms"
              label="Stream Latency"
              description="WebSocket"
            />
            <MetricBox
              value="6"
              label="Agents"
              description="Parallel"
            />
            <MetricBox
              value="2.6K"
              label="Chunks"
              description="RAG"
            />
          </div>
        </motion.div>

        {/* Simplified Flow Diagram */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.6 }}
          viewport={{ once: true }}
          className="mt-16 landing-glass rounded-xl p-8 border border-[rgba(0,229,255,0.2)]"
        >
          <h3 className="text-2xl font-bold text-center mb-8 text-[#00E5FF]">
            The Flow
          </h3>
          <div className="overflow-x-auto">
            <MermaidDiagram
              chart={`
graph LR
    A[Equipment Sensors] -->|15s intervals| B[Anomaly Detection]
    B -->|Issue found| C[AI Agents]
    C -->|Analyze| D[Maintenance Report]
    D --> E[Dashboard Alert]
    
    style A fill:#00E5FF20,stroke:#00E5FF,stroke-width:2px
    style B fill:#FF6A0020,stroke:#FF6A00,stroke-width:2px
    style C fill:#00FF8520,stroke:#00FF85,stroke-width:2px
    style D fill:#00E5FF20,stroke:#00E5FF,stroke-width:2px
    style E fill:#FF6A0020,stroke:#FF6A00,stroke-width:2px
              `}
              className="min-h-[200px]"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Flow Step Component
function FlowStep({
  number,
  icon,
  title,
  description,
  details,
  tech,
}: {
  number: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  details: string[];
  tech: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -50 }}
      whileInView={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6 }}
      viewport={{ once: true }}
      className="landing-glass rounded-2xl p-8 border"
      style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }}
    >
      <div className="flex items-start gap-6">
        {/* Number Badge */}
        <div
          className="flex-shrink-0 w-16 h-16 rounded-xl flex items-center justify-center text-2xl font-black landing-mono"
          style={{
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            color: '#FFFFFF',
            border: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          {number}
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2 rounded-lg" style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)', color: '#FFFFFF' }}>
              {icon}
            </div>
            <div>
              <h3 className="text-2xl font-bold text-white">{title}</h3>
              <p className="text-sm text-[#B8C1CC]">{description}</p>
            </div>
          </div>

          {/* Details List */}
          <ul className="space-y-2 mb-4">
            {details.map((detail, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-[#B8C1CC]">
                <span className="text-white mt-1 flex-shrink-0">▸</span>
                <span
                  dangerouslySetInnerHTML={{
                    __html: detail.replace(
                      /\*\*(.*?)\*\*/g,
                      `<strong style="color: #FFFFFF">$1</strong>`
                    ),
                  }}
                />
              </li>
            ))}
          </ul>

          {/* Tech Badge */}
          <div
            className="inline-block px-4 py-2 rounded-full text-xs font-mono font-bold"
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: '#B8C1CC',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            TECH: {tech}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

// Flow Arrow Component
function FlowArrow() {
  return (
    <div className="flex justify-center">
      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        <ArrowRight
          className="w-8 h-8 rotate-90"
          style={{ color: '#00E5FF' }}
        />
      </motion.div>
    </div>
  );
}

// Metric Box Component
function MetricBox({
  value,
  label,
  description,
}: {
  value: string;
  label: string;
  description: string;
}) {
  return (
    <div className="text-center p-6 rounded-xl" style={{ backgroundColor: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
      <div className="text-4xl font-black landing-mono mb-2 text-white">
        {value}
      </div>
      <div className="text-lg font-bold text-white mb-1">{label}</div>
      <div className="text-xs text-[#B8C1CC]">{description}</div>
    </div>
  );
}
