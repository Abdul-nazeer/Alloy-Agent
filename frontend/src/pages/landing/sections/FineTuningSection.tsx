import { motion } from 'framer-motion';
import { Brain, Database, Zap, TrendingUp, CheckCircle2, Code } from 'lucide-react';
import MermaidDiagram from '../../../components/MermaidDiagram';

export default function FineTuningSection() {
  return (
    <section
      id="fine-tuning"
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
          <h2 className="text-5xl lg:text-7xl font-black landing-heading mb-6">
            <span style={{ color: '#00FF85' }}>Fine-Tuned</span>
            <span className="text-white"> Model</span>
          </h2>
          <p className="text-xl text-[#B8C1CC] max-w-3xl mx-auto">
            We trained Microsoft's Phi-3 on 845K turbofan engine records from NASA. 
            Now it actually understands maintenance jargon.
          </p>
        </motion.div>

        {/* Model Overview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          viewport={{ once: true }}
          className="landing-glass rounded-2xl p-8 lg:p-12 border-2 border-[rgba(0,255,133,0.3)] mb-12"
        >
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Left: Model Details */}
            <div className="space-y-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="p-4 rounded-xl bg-[#00FF8520]">
                  <Brain className="w-10 h-10 text-[#00FF85]" />
                </div>
                <div>
                  <h3 className="text-3xl font-bold text-white">Microsoft Phi-3</h3>
                  <p className="text-[#B8C1CC]">3.8 Billion Parameters</p>
                </div>
              </div>

              <div className="space-y-4">
                <InfoRow
                  label="Base Model"
                  value="microsoft/Phi-3-mini-4k-instruct"
                  color="#00FF85"
                />
                <InfoRow
                  label="Fine-tuned On"
                  value="NASA C-MAPSS Turbofan Engine Data"
                  color="#00FF85"
                />
                <InfoRow
                  label="Training Records"
                  value="845,730 sensor readings"
                  color="#00FF85"
                />
                <InfoRow
                  label="Context Length"
                  value="4,096 tokens"
                  color="#00FF85"
                />
                <InfoRow
                  label="Training Method"
                  value="LoRA (Low-Rank Adaptation)"
                  color="#00FF85"
                />
                <InfoRow
                  label="HuggingFace Model"
                  value="CodeMasterAbdul/alloy-phi3-steel-maintenance"
                  color="#00FF85"
                />
              </div>

              <div className="mt-6 p-4 rounded-xl bg-[#00FF8510] border border-[#00FF8540]">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-[#00FF85] mt-0.5" />
                  <div>
                    <h4 className="font-bold text-white mb-1">Live on HuggingFace</h4>
                    <p className="text-sm text-[#B8C1CC]">
                      You can grab the model and run it yourself - it's already deployed and ready to use
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Right: Training Pipeline */}
            <div className="space-y-6">
              <h3 className="text-2xl font-bold text-white mb-6">Training Pipeline</h3>
              
              <MermaidDiagram
                chart={`
graph TD
    A[NASA C-MAPSS Dataset<br/>845,730 records] --> B[Data Preprocessing]
    B --> C[Feature Engineering<br/>RUL Calculation]
    C --> D[Microsoft Phi-3<br/>3.8B Base Model]
    D --> E[LoRA Fine-Tuning<br/>Rank=8, Alpha=32]
    E --> F[4-bit Quantization]
    F --> G[HuggingFace Hub<br/>CodeMasterAbdul/alloy-phi3]
    G --> H[Production Deployment]
    
    style A fill:#00FF8520,stroke:#00FF85,stroke-width:2px
    style D fill:#00E5FF20,stroke:#00E5FF,stroke-width:2px
    style E fill:#FF6A0020,stroke:#FF6A00,stroke-width:2px
    style G fill:#00FF8520,stroke:#00FF85,stroke-width:2px
                `}
                className="min-h-[400px]"
              />
              
              <div className="grid grid-cols-2 gap-4 mt-6">
                <div className="p-4 rounded-lg bg-[#00FF8510] border border-[#00FF8540]">
                  <div className="text-2xl font-bold text-[#00FF85] mb-1">50</div>
                  <div className="text-xs text-[#B8C1CC]">Training Epochs</div>
                </div>
                <div className="p-4 rounded-lg bg-[#00FF8510] border border-[#00FF8540]">
                  <div className="text-2xl font-bold text-[#00FF85] mb-1">95%+</div>
                  <div className="text-xs text-[#B8C1CC]">Accuracy</div>
                </div>
                <div className="p-4 rounded-lg bg-[#00FF8510] border border-[#00FF8540]">
                  <div className="text-2xl font-bold text-[#00FF85] mb-1">4-bit</div>
                  <div className="text-xs text-[#B8C1CC]">Quantization</div>
                </div>
                <div className="p-4 rounded-lg bg-[#00FF8510] border border-[#00FF8540]">
                  <div className="text-2xl font-bold text-[#00FF85] mb-1">&lt;100ms</div>
                  <div className="text-xs text-[#B8C1CC]">Inference Time</div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Dataset Overview */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          viewport={{ once: true }}
          className="grid md:grid-cols-3 gap-6 mb-12"
        >
          <DatasetCard
            icon={<Database className="w-8 h-8" />}
            title="C-MAPSS Dataset"
            subtitle="NASA Turbofan Engine"
            details={[
              '100 engines tracked to failure',
              'Run-to-failure simulation',
              'Multiple operating conditions',
              'Real-world failure scenarios'
            ]}
            color="#00FF85"
          />

          <DatasetCard
            icon={<TrendingUp className="w-8 h-8" />}
            title="21 Sensor Parameters"
            subtitle="Multi-variate Time-series"
            details={[
              'Temperature sensors (6)',
              'Pressure sensors (5)',
              'Flow rates (3)',
              'RPM and vibration (7)'
            ]}
            color="#00E5FF"
          />

          <DatasetCard
            icon={<Zap className="w-8 h-8" />}
            title="Model Performance"
            subtitle="Inference Metrics"
            details={[
              '<100ms response time',
              '4-bit quantization',
              'Efficient token generation',
              'Production-optimized'
            ]}
            color="#FF6A00"
          />
        </motion.div>

        {/* Code Sample */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="landing-glass rounded-2xl p-8 border border-[rgba(0,255,133,0.2)]"
        >
          <div className="flex items-center gap-3 mb-6">
            <Code className="w-6 h-6 text-[#00FF85]" />
            <h3 className="text-2xl font-bold text-white">Model Usage Example</h3>
          </div>

          <div className="bg-[#050505] rounded-xl p-6 border border-[rgba(0,255,133,0.2)] font-mono text-sm overflow-x-auto">
            <pre className="text-[#B8C1CC]">
{`# Load Fine-tuned Model from HuggingFace
from transformers import AutoModelForCausalLM, AutoTokenizer

model_id = "CodeMasterAbdul/alloy-phi3-steel-maintenance"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    load_in_4bit=True,  # Efficient inference
    device_map="auto"
)

# Maintenance Query
prompt = """
Equipment: Air Compressor AC-001
Sensor Data:
- Temperature: 101.25°C (High)
- Pressure: 3.1 bar (Below minimum 4.0)
- Vibration: 3.24 mm/s (Above max 3.0)

Analyze the failure pattern and recommend actions.
"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512)
response = tokenizer.decode(outputs[0], skip_special_tokens=True)

# Model provides domain-specific maintenance recommendations`}
            </pre>
          </div>

          <div className="mt-6 flex flex-wrap gap-4">
            <button className="px-6 py-3 rounded-lg bg-[#00FF8520] text-[#00FF85] border border-[#00FF8540] font-semibold hover:bg-[#00FF8530] transition-colors">
              View on HuggingFace →
            </button>
            <button className="px-6 py-3 rounded-lg bg-[#00E5FF20] text-[#00E5FF] border border-[#00E5FF40] font-semibold hover:bg-[#00E5FF30] transition-colors">
              Training Notebook →
            </button>
          </div>
        </motion.div>

        {/* Benefits */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          viewport={{ once: true }}
          className="mt-12"
        >
          <h3 className="text-3xl font-bold text-center text-white mb-8">
            Why Fine-Tuning Matters
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <BenefitCard
              icon="🎯"
              title="Domain Knowledge"
              description="Actually understands maintenance terms and failure patterns - not just generic AI responses"
            />
            <BenefitCard
              icon="⚡"
              title="Way Faster"
              description="3.8B parameters vs 70B+ means sub-100ms responses instead of waiting around"
            />
            <BenefitCard
              icon="💰"
              title="Cheaper to Run"
              description="Self-host with 4-bit quantization - no expensive API calls eating your budget"
            />
            <BenefitCard
              icon="🔒"
              title="Keep Data Private"
              description="Run it on-premise - your maintenance data never leaves your servers"
            />
          </div>
        </motion.div>
      </div>
    </section>
  );
}

// Info Row Component
function InfoRow({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="flex justify-between items-start p-3 rounded-lg bg-[rgba(0,0,0,0.3)]">
      <span className="text-sm text-[#B8C1CC] font-medium">{label}:</span>
      <span className="text-sm font-mono font-bold text-right max-w-[60%]" style={{ color }}>
        {value}
      </span>
    </div>
  );
}

// Dataset Card Component
function DatasetCard({
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

// Benefit Card Component
function BenefitCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="landing-glass rounded-xl p-6 border border-[rgba(255,255,255,0.1)]">
      <div className="text-4xl mb-3">{icon}</div>
      <h4 className="text-lg font-bold text-white mb-2">{title}</h4>
      <p className="text-sm text-[#B8C1CC]">{description}</p>
    </div>
  );
}
