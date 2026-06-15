import { useEffect, useRef, useState } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollStorySection() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [currentScene, setCurrentScene] = useState(0);
  
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"]
  });

  const sceneProgress = useTransform(scrollYProgress, [0, 1], [0, 8]);

  useEffect(() => {
    return sceneProgress.onChange(latest => {
      setCurrentScene(Math.min(Math.floor(latest), 7));
    });
  }, [sceneProgress]);

  const scenes = [
    {
      title: "Plant Operating Normally",
      subtitle: "All systems green. Production at 100%",
      status: "healthy",
      color: "#00FF85"
    },
    {
      title: "Sensor Values Increasing",
      subtitle: "Temperature +15°C, Vibration +2.5mm/s",
      status: "warning",
      color: "#FFC107"
    },
    {
      title: "Threshold Exceeded",
      subtitle: "AC-001 Bearing Temperature: CRITICAL",
      status: "alert",
      color: "#FF6A00"
    },
    {
      title: "ANOMALY DETECTED",
      subtitle: "Multi-sensor correlation confirmed",
      status: "critical",
      color: "#FF3D3D"
    },
    {
      title: "AI Agents Activated",
      subtitle: "Supervisor → Anomaly → Diagnosis → Recommendation",
      status: "processing",
      color: "#00E5FF"
    },
    {
      title: "Root Cause Identified",
      subtitle: "Bearing lubrication failure. RUL: 4 hours",
      status: "diagnosed",
      color: "#00E5FF"
    },
    {
      title: "Maintenance Plan Generated",
      subtitle: "15-step repair procedure. Parts ordered. ETA: 2 hours",
      status: "resolved",
      color: "#00FF85"
    },
    {
      title: "Preventing Failures Before They Happen",
      subtitle: "Autonomous. Intelligent. Always watching.",
      status: "complete",
      color: "#00E5FF"
    }
  ];

  const currentSceneData = scenes[currentScene] || scenes[0];

  return (
    <section
      ref={sectionRef}
      className="relative h-[300vh] bg-gradient-to-b from-[#050505] via-[#0A0A0A] to-[#050505]"
    >
      {/* Sticky Container */}
      <div className="sticky top-0 h-screen flex items-center justify-center overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0">
          <motion.div
            className="absolute inset-0 landing-grid"
            style={{
              opacity: useTransform(scrollYProgress, [0, 0.5, 1], [0.2, 0.5, 0.2])
            }}
          />
          
          {/* Alert Flash Effect */}
          {currentScene === 3 && (
            <motion.div
              className="absolute inset-0"
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 0.3, 0] }}
              transition={{ duration: 0.5, repeat: 3 }}
              style={{ backgroundColor: '#FF3D3D' }}
            />
          )}
        </div>

        {/* Content */}
        <div className="relative z-10 text-center px-6 max-w-5xl mx-auto">
          {/* Machine Visualization */}
          <motion.div
            className="mb-12"
            animate={{
              scale: currentScene >= 3 ? 1.1 : 1,
              rotate: currentScene >= 3 ? [0, -2, 2, 0] : 0
            }}
            transition={{ duration: 0.3 }}
          >
            <MachineDiagram
              status={currentSceneData.status}
              scene={currentScene}
            />
          </motion.div>

          {/* Title */}
          <motion.h2
            key={currentScene}
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="text-5xl lg:text-7xl font-bold landing-heading mb-6"
            style={{ color: currentSceneData.color }}
          >
            {currentSceneData.title}
          </motion.h2>

          {/* Subtitle */}
          <motion.p
            key={`subtitle-${currentScene}`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-xl lg:text-2xl text-[#B8C1CC] font-medium"
          >
            {currentSceneData.subtitle}
          </motion.p>

          {/* Progress Indicator */}
          <div className="mt-12 flex justify-center gap-2">
            {scenes.map((_, index) => (
              <div
                key={index}
                className="h-1 w-12 rounded-full transition-all duration-300"
                style={{
                  backgroundColor: index <= currentScene ? currentSceneData.color : 'rgba(255,255,255,0.1)'
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function MachineDiagram({ status, scene }: { status: string; scene: number }) {
  const getStatusColor = () => {
    switch (status) {
      case 'healthy': return '#00FF85';
      case 'warning': return '#FFC107';
      case 'alert': return '#FF6A00';
      case 'critical': return '#FF3D3D';
      case 'processing':
      case 'diagnosed': return '#00E5FF';
      case 'resolved': return '#00FF85';
      default: return '#B8C1CC';
    }
  };

  const color = getStatusColor();
  const shouldPulse = status === 'critical' || status === 'processing';

  return (
    <div className="relative w-64 h-64 mx-auto">
      {/* Machine Body */}
      <motion.div
        className="w-full h-full rounded-lg landing-glass border-2 relative overflow-hidden"
        style={{ borderColor: color }}
        animate={shouldPulse ? {
          boxShadow: [
            `0 0 20px ${color}40`,
            `0 0 60px ${color}80`,
            `0 0 20px ${color}40`
          ]
        } : {}}
        transition={{ duration: 1, repeat: Infinity }}
      >
        {/* Equipment Label */}
        <div className="absolute top-4 left-4">
          <span className="text-sm font-mono text-white">AC-001</span>
        </div>

        {/* Status Indicator */}
        <div className="absolute top-4 right-4">
          <motion.div
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: color }}
            animate={shouldPulse ? { scale: [1, 1.5, 1] } : {}}
            transition={{ duration: 0.5, repeat: Infinity }}
          />
        </div>

        {/* Center Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            className="w-24 h-24 rounded-full border-4 flex items-center justify-center"
            style={{ borderColor: color }}
            animate={scene >= 4 ? { rotate: 360 } : {}}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            {scene >= 4 ? (
              <svg className="w-12 h-12" fill={color} viewBox="0 0 24 24">
                <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5zm0 18c-4 0-7-2.58-7-6V9.5l7-3.5 7 3.5V14c0 3.42-3 6-7 6z"/>
                <circle cx="12" cy="12" r="3" />
              </svg>
            ) : (
              <svg className="w-12 h-12" fill={color} viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                <circle cx="12" cy="12" r="4" />
              </svg>
            )}
          </motion.div>
        </div>

        {/* Sensor Readings */}
        <div className="absolute bottom-4 left-4 right-4 space-y-1">
          <SensorBar label="TEMP" value={scene >= 1 ? 85 + scene * 5 : 75} max={115} color={color} />
          <SensorBar label="VIB" value={scene >= 1 ? 1.5 + scene * 0.5 : 1.2} max={5} color={color} />
          <SensorBar label="PRES" value={scene >= 1 ? 6.2 - scene * 0.3 : 6.5} max={8} color={color} />
        </div>

        {/* Alert Overlay */}
        {scene === 3 && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center bg-black/80"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 0.5, repeat: 2 }}
          >
            <span className="text-3xl font-bold text-[#FF3D3D]">⚠️ ALERT</span>
          </motion.div>
        )}
      </motion.div>

      {/* Agent Activity Indicators */}
      {scene >= 4 && scene <= 6 && (
        <div className="absolute -right-20 top-1/2 transform -translate-y-1/2 space-y-2">
          {['Anomaly', 'Diagnosis', 'Recommendation'].map((agent, i) => (
            <motion.div
              key={agent}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.3 }}
              className="px-3 py-1 rounded-full landing-glass border text-xs font-mono"
              style={{ borderColor: '#00E5FF', color: '#00E5FF' }}
            >
              {agent}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

function SensorBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const percentage = (value / max) * 100;
  const isHigh = percentage > 80;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="font-mono text-[#B8C1CC] w-8">{label}</span>
      <div className="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: isHigh ? '#FF3D3D' : color }}
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <span className="font-mono text-[#B8C1CC] w-8 text-right">{value.toFixed(1)}</span>
    </div>
  );
}
