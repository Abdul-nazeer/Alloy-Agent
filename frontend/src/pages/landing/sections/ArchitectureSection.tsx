import { motion } from 'framer-motion';
import { Database, Cloud, Cpu, Network, Zap, Brain } from 'lucide-react';
import MermaidDiagram from '../../../components/MermaidDiagram';

export default function ArchitectureSection() {
  return (
    <section
      id="architecture"
      className="min-h-screen relative flex items-center justify-center py-20"
      style={{ background: 'linear-gradient(180deg, #050505 0%, #0A0A0A 100%)' }}
    >
      <div className="container mx-auto px-6 lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl lg:text-7xl font-black landing-heading mb-6" style={{ color: '#00E5FF' }}>
            System Architecture
          </h2>
          <p className="text-xl text-[#B8C1CC] max-w-3xl mx-auto">
            Standard three-tier setup with real-time streaming and agent orchestration
          </p>
        </motion.div>

        {/* Interactive Architecture Diagram */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="landing-glass rounded-2xl p-8 lg:p-12 border border-[rgba(0,229,255,0.2)] mb-12"
        >
          <h3 className="text-3xl font-bold text-center mb-8 text-white">
            The Stack
          </h3>
          <MermaidDiagram
            chart={`
graph TB
    subgraph Frontend["🖥️ Frontend Layer"]
        UI[React 18 + TypeScript]
        WC[WebSocket Client]
        VIZ[Recharts + PDF.js]
        FM[Framer Motion]
    end
    
    subgraph Backend["⚙️ Backend Layer FastAPI"]
        API[REST API Endpoints]
        WSS[WebSocket Server]
        SQLITE[(SQLite Database)]
        ASYNC[Async Processing]
    end
    
    subgraph AgentLayer["🤖 AI Agent Layer LangGraph"]
        SUP[Supervisor<br/>Orchestrator]
        AG1[Anomaly<br/>Detection]
        AG2[Diagnosis<br/>RCA]
        AG3[Recommendation<br/>Planning]
        AG4[Report<br/>Generation]
        AG5[Chat<br/>Interface]
    end
    
    subgraph External["☁️ External Services"]
        QD[(Qdrant Cloud<br/>Vector DB<br/>2606 chunks)]
        GROQ[Groq API<br/>Llama 3.1<br/>8B Instant]
        HF[HuggingFace<br/>Phi-3 Model<br/>Fine-tuned]
    end
    
    UI --> API
    WC --> WSS
    API --> SQLITE
    API --> SUP
    WSS --> SQLITE
    SUP --> AG1
    SUP --> AG2
    SUP --> AG3
    SUP --> AG4
    SUP --> AG5
    AG2 --> QD
    AG3 --> QD
    AG1 --> GROQ
    AG2 --> GROQ
    AG3 --> GROQ
    AG4 --> GROQ
    AG5 --> GROQ
    AG1 --> HF
    
    style Frontend fill:#00E5FF20,stroke:#00E5FF,stroke-width:3px
    style Backend fill:#FF6A0020,stroke:#FF6A00,stroke-width:3px
    style AgentLayer fill:#00FF8520,stroke:#00FF85,stroke-width:3px
    style External fill:#00E5FF20,stroke:#00E5FF,stroke-width:3px
            `}
            className="min-h-[500px]"
          />
        </motion.div>

        {/* Component Breakdown */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="landing-glass rounded-2xl p-8 lg:p-12 border border-[rgba(0,229,255,0.2)]"
        >
          {/* Three-Tier Architecture Visual */}
          <div className="space-y-8">
            {/* Frontend Layer */}
            <ArchitectureLayer
              title="Frontend Layer"
              color="#00E5FF"
              icon={<Network className="w-6 h-6" />}
              components={[
                { name: 'React 18 + TypeScript', detail: 'Type-safe UI components' },
                { name: 'Framer Motion', detail: 'Smooth animations' },
                { name: 'TailwindCSS', detail: 'Industrial theme' },
                { name: 'WebSocket Client', detail: 'Real-time updates' },
                { name: 'Recharts + PDF.js', detail: 'Data visualization' },
              ]}
            />

            {/* Arrow Down */}
            <div className="flex justify-center">
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="text-[#00E5FF]"
              >
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                  <path d="M12 5v14m0 0l-7-7m7 7l7-7" stroke="currentColor" strokeWidth="2" />
                </svg>
              </motion.div>
            </div>

            {/* Backend Layer */}
            <ArchitectureLayer
              title="Backend Layer (FastAPI)"
              color="#FF6A00"
              icon={<Cpu className="w-6 h-6" />}
              components={[
                { name: 'RESTful API', detail: '15+ endpoints' },
                { name: 'WebSocket Server', detail: 'Sensor streaming' },
                { name: 'SQLite Database', detail: 'Operational data' },
                { name: 'CORS + Security', detail: 'Production-ready' },
                { name: 'Async Processing', detail: 'Non-blocking I/O' },
              ]}
            />

            {/* Arrow Down */}
            <div className="flex justify-center">
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
                className="text-[#FF6A00]"
              >
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                  <path d="M12 5v14m0 0l-7-7m7 7l7-7" stroke="currentColor" strokeWidth="2" />
                </svg>
              </motion.div>
            </div>

            {/* AI Agent Layer */}
            <ArchitectureLayer
              title="AI Agent Layer (LangGraph)"
              color="#00FF85"
              icon={<Brain className="w-6 h-6" />}
              components={[
                { name: 'Supervisor Agent', detail: 'Orchestrates workflow' },
                { name: 'Anomaly Agent', detail: 'Pattern detection' },
                { name: 'Diagnosis Agent', detail: 'Root cause analysis' },
                { name: 'Recommendation Agent', detail: 'Action planning' },
                { name: 'Report Agent', detail: 'Documentation' },
                { name: 'Conversational Agent', detail: 'Chat interface' },
              ]}
            />

            {/* Arrow Down */}
            <div className="flex justify-center">
              <motion.div
                animate={{ y: [0, 10, 0] }}
                transition={{ duration: 1.5, repeat: Infinity, delay: 1 }}
                className="text-[#00FF85]"
              >
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                  <path d="M12 5v14m0 0l-7-7m7 7l7-7" stroke="currentColor" strokeWidth="2" />
                </svg>
              </motion.div>
            </div>

            {/* External Services Layer */}
            <div className="grid md:grid-cols-3 gap-6">
              <ServiceBox
                icon={<Cloud className="w-8 h-8" />}
                title="Qdrant Cloud"
                subtitle="Vector Database"
                details={['2,606 knowledge chunks', 'Hybrid search', 'Dense + sparse vectors']}
                color="#00E5FF"
              />
              <ServiceBox
                icon={<Zap className="w-8 h-8" />}
                title="Groq API"
                subtitle="LLM Inference"
                details={['Llama 3.1 8B', 'Ultra-fast inference', 'Rate-limited API']}
                color="#FF6A00"
              />
              <ServiceBox
                icon={<Database className="w-8 h-8" />}
                title="HuggingFace"
                subtitle="Fine-tuned Model"
                details={['Phi-3 3.8B parameters', 'C-MAPSS trained', '845K+ records']}
                color="#00FF85"
              />
            </div>
          </div>
        </motion.div>

        {/* Key Architecture Highlights */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="mt-12 grid md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          <HighlightCard
            number="01"
            title="Real-Time Streaming"
            description="WebSocket pushes sensor data every 15 seconds with sub-50ms latency"
          />
          <HighlightCard
            number="02"
            title="Async Everything"
            description="FastAPI handles 1000+ connections without breaking a sweat"
          />
          <HighlightCard
            number="03"
            title="Multi-Agent System"
            description="LangGraph runs 6 agents in parallel - each doing its own thing"
          />
          <HighlightCard
            number="04"
            title="Hybrid RAG"
            description="Dense embeddings + BM25 keyword search + reranking for better results"
          />
        </motion.div>
      </div>
    </section>
  );
}

// Architecture Layer Component
function ArchitectureLayer({
  title,
  color,
  icon,
  components,
}: {
  title: string;
  color: string;
  icon: React.ReactNode;
  components: { name: string; detail: string }[];
}) {
  return (
    <div className="landing-glass rounded-xl p-6 border-2" style={{ borderColor: `${color}40` }}>
      <div className="flex items-center gap-3 mb-6">
        <div
          className="p-2 rounded-lg"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {icon}
        </div>
        <h3 className="text-2xl font-bold" style={{ color }}>
          {title}
        </h3>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {components.map((comp, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            viewport={{ once: true }}
            className="p-4 rounded-lg"
            style={{ backgroundColor: 'rgba(0,0,0,0.3)', border: `1px solid ${color}20` }}
          >
            <div className="font-mono font-bold text-sm mb-1" style={{ color }}>
              {comp.name}
            </div>
            <div className="text-xs text-[#B8C1CC]">{comp.detail}</div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

// Service Box Component
function ServiceBox({
  icon,
  title,
  subtitle,
  details,
  color,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle: string;
  details: string[];
  color: string;
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, borderColor: color }}
      className="landing-glass rounded-xl p-6 border transition-all"
      style={{ borderColor: `${color}40` }}
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-3 rounded-lg" style={{ backgroundColor: `${color}20`, color }}>
          {icon}
        </div>
        <div>
          <h4 className="font-bold text-white">{title}</h4>
          <p className="text-xs text-[#B8C1CC]">{subtitle}</p>
        </div>
      </div>
      <ul className="space-y-2">
        {details.map((detail, idx) => (
          <li key={idx} className="flex items-center gap-2 text-sm text-[#B8C1CC]">
            <span style={{ color }}>▸</span>
            {detail}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}

// Highlight Card Component
function HighlightCard({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="landing-glass rounded-lg p-6 border border-[rgba(255,255,255,0.1)]">
      <div className="text-4xl font-black landing-mono mb-3" style={{ color: '#00E5FF', opacity: 0.3 }}>
        {number}
      </div>
      <h4 className="text-lg font-bold text-white mb-2">{title}</h4>
      <p className="text-sm text-[#B8C1CC]">{description}</p>
    </div>
  );
}
