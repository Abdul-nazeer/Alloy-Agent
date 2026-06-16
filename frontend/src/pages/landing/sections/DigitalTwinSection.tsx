import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const equipment = [
  { id: 'AC-001', name: 'Air Compressor 1', status: 'normal', x: 20, y: 30, temp: 82, pressure: 4.2, health: 91, rul: 38 },
  { id: 'AC-002', name: 'Air Compressor 2', status: 'warning', x: 80, y: 30, temp: 95, pressure: 3.8, health: 76, rul: 12 },
  { id: 'CF-003', name: 'Cooling Fan', status: 'normal', x: 50, y: 50, temp: 55, pressure: 0, health: 94, rul: 45 },
  { id: 'RM-005', name: 'Rolling Mill', status: 'normal', x: 30, y: 70, temp: 88, pressure: 175, health: 89, rul: 28 },
  { id: 'CM-007', name: 'Conveyor Motor', status: 'normal', x: 70, y: 70, temp: 65, pressure: 0, health: 96, rul: 52 },
];

export default function DigitalTwinSection() {
  const [selectedEquipment, setSelectedEquipment] = useState<typeof equipment[0] | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return '#FF3D3D';
      case 'warning': return '#00E5FF';
      case 'normal': return '#00FF85';
      default: return '#00E5FF';
    }
  };

  return (
    <section className="relative min-h-screen py-20 overflow-hidden" style={{ background: 'linear-gradient(180deg, #050505 0%, #0A0A0A 50%, #050505 100%)' }}>
      <div className="container mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4">
            Digital Twin <span className="landing-text-gradient-cyan">Command Center</span>
          </h2>
          <p className="text-xl text-[#B8C1CC] max-w-3xl mx-auto">
            Real-time visualization of your entire plant. Click any equipment to see live diagnostics.
          </p>
        </motion.div>

        <div className="relative">
          {/* Plant Map */}
          <div className="relative w-full h-[600px] landing-glass rounded-2xl border border-[rgba(0,229,255,0.2)] overflow-hidden">
            {/* Grid Background */}
            <div className="absolute inset-0 landing-grid opacity-20" />
            
            {/* Equipment Nodes */}
            {equipment.map((eq, index) => (
              <motion.div
                key={eq.id}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="absolute cursor-pointer"
                style={{
                  left: `${eq.x}%`,
                  top: `${eq.y}%`,
                  transform: 'translate(-50%, -50%)',
                }}
                onClick={() => setSelectedEquipment(eq)}
              >
                <motion.div
                  className="w-16 h-16 rounded-full landing-glass border-2 flex items-center justify-center relative"
                  style={{ borderColor: getStatusColor(eq.status) }}
                  whileHover={{ scale: 1.2 }}
                  animate={{
                    boxShadow: [
                      `0 0 20px ${getStatusColor(eq.status)}40`,
                      `0 0 40px ${getStatusColor(eq.status)}60`,
                      `0 0 20px ${getStatusColor(eq.status)}40`,
                    ]
                  }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div
                    className="w-8 h-8 rounded-full landing-pulse"
                    style={{ backgroundColor: getStatusColor(eq.status) }}
                  />
                </motion.div>
                
                {/* Label */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                  <span className="text-xs font-mono text-white">{eq.id}</span>
                </div>
              </motion.div>
            ))}

            {/* Connection Lines */}
            <svg className="absolute inset-0 pointer-events-none">
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.3" />
                  <stop offset="50%" stopColor="#00E5FF" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="#00E5FF" stopOpacity="0.3" />
                </linearGradient>
              </defs>
              {/* Draw connections between equipment */}
              {equipment.slice(0, -1).map((eq, i) => {
                const next = equipment[i + 1];
                return (
                  <motion.line
                    key={`${eq.id}-${next.id}`}
                    x1={`${eq.x}%`}
                    y1={`${eq.y}%`}
                    x2={`${next.x}%`}
                    y2={`${next.y}%`}
                    stroke="url(#lineGradient)"
                    strokeWidth="2"
                    strokeDasharray="5 5"
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ duration: 2, delay: i * 0.2 }}
                  />
                );
              })}
            </svg>
          </div>

          {/* Side Panel */}
          <AnimatePresence>
            {selectedEquipment && (
              <motion.div
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 100 }}
                className="absolute right-0 top-0 w-80 h-full landing-glass rounded-2xl border border-[rgba(0,229,255,0.2)] p-6 backdrop-blur-xl"
              >
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-xl font-bold text-white mb-1">{selectedEquipment.name}</h3>
                    <p className="text-sm font-mono text-[#00E5FF]">{selectedEquipment.id}</p>
                  </div>
                  <button
                    onClick={() => setSelectedEquipment(null)}
                    className="text-white hover:text-[#FF3D3D] transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="space-y-4">
                  <MetricDisplay label="Temperature" value={`${selectedEquipment.temp}°C`} />
                  <MetricDisplay label="Pressure" value={`${selectedEquipment.pressure} bar`} />
                  <MetricDisplay label="Health Score" value={`${selectedEquipment.health}%`} />
                  <MetricDisplay label="Predicted RUL" value={`${selectedEquipment.rul} Days`} />
                  <MetricDisplay label="Last Inspection" value="12 Hours Ago" />
                  
                  {/* Health Progress Bar */}
                  <div className="pt-4">
                    <div className="flex justify-between text-xs text-[#B8C1CC] mb-2">
                      <span>Health Status</span>
                      <span>{selectedEquipment.health}%</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                      <motion.div
                        className="h-full rounded-full"
                        style={{ backgroundColor: getStatusColor(selectedEquipment.status) }}
                        initial={{ width: 0 }}
                        animate={{ width: `${selectedEquipment.health}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}

function MetricDisplay({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-white/10">
      <span className="text-sm text-[#B8C1CC]">{label}</span>
      <span className="text-sm font-mono font-bold text-white">{value}</span>
    </div>
  );
}
