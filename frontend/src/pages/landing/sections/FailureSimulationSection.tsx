import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

export default function FailureSimulationSection() {
  const [isSimulating, setIsSimulating] = useState(false);
  const [step, setStep] = useState(0);

  const timeline = [
    { time: '08:42', event: 'Sensor Spike Detected', color: '#FFC107' },
    { time: '08:43', event: 'Anomaly Confirmed', color: '#FF6A00' },
    { time: '08:44', event: 'Root Cause Identified', color: '#FF3D3D' },
    { time: '08:45', event: 'Maintenance Plan Generated', color: '#00E5FF' },
    { time: '08:46', event: 'Engineer Notified', color: '#00FF85' },
  ];

  const startSimulation = () => {
    setIsSimulating(true);
    setStep(0);
    
    timeline.forEach((_, i) => {
      setTimeout(() => setStep(i + 1), (i + 1) * 1000);
    });

    setTimeout(() => setIsSimulating(false), 6000);
  };

  return (
    <section className="relative min-h-screen py-20 flex items-center" style={{ background: 'linear-gradient(180deg, #050505 0%, #0A0A0A 100%)' }}>
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-5xl lg:text-6xl font-bold landing-heading text-white mb-4">
            Failure <span className="landing-text-gradient-orange">Simulation Engine</span>
          </h2>
          <p className="text-xl text-[#B8C1CC]">Watch how Alloy Agent prevents catastrophic failures</p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="landing-glass rounded-2xl p-8 border border-[rgba(0,229,255,0.2)]">
            <div className="text-center mb-8">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={startSimulation}
                disabled={isSimulating}
                className="landing-btn-primary disabled:opacity-50"
              >
                {isSimulating ? 'Simulating...' : 'Simulate Bearing Failure'}
              </motion.button>
            </div>

            <AnimatePresence>
              {isSimulating && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="space-y-4"
                >
                  {timeline.map((item, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -50 }}
                      animate={step > i ? { opacity: 1, x: 0 } : {}}
                      className="flex items-center gap-4 p-4 rounded-lg landing-glass"
                      style={{ borderLeft: `4px solid ${item.color}` }}
                    >
                      <span className="font-mono text-sm" style={{ color: item.color }}>
                        {item.time}
                      </span>
                      <span className="flex-1 text-white">{item.event}</span>
                      {step > i && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-6 h-6 rounded-full flex items-center justify-center"
                          style={{ backgroundColor: item.color }}
                        >
                          <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                          </svg>
                        </motion.div>
                      )}
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </section>
  );
}
