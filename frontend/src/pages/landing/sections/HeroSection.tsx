import { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import Particles from '@tsparticles/react';
import { Play } from 'lucide-react';

interface HeroSectionProps {
  onEnterDashboard: () => void;
}

export default function HeroSection({ onEnterDashboard }: HeroSectionProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  
  // Mouse parallax
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const springConfig = { damping: 25, stiffness: 150 };
  const x = useSpring(mouseX, springConfig);
  const y = useSpring(mouseY, springConfig);
  
  const rotateX = useTransform(y, [-0.5, 0.5], ["5deg", "-5deg"]);
  const rotateY = useTransform(x, [-0.5, 0.5], ["-5deg", "5deg"]);

  // Animated counters
  const [counters, setCounters] = useState({
    equipment: 0,
    agents: 0,
    chunks: 0,
    records: 0,
    latency: 0
  });

  useEffect(() => {
    const targets = {
      equipment: 5,
      agents: 6,
      chunks: 2606,
      records: 845,
      latency: 50
    };

    const duration = 2000;
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);

      setCounters({
        equipment: Math.floor(targets.equipment * easeOutCubic),
        agents: Math.floor(targets.agents * easeOutCubic),
        chunks: Math.floor(targets.chunks * easeOutCubic),
        records: Math.floor(targets.records * easeOutCubic),
        latency: Math.floor(targets.latency * easeOutCubic)
      });

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    const timer = setTimeout(animate, 500);
    return () => clearTimeout(timer);
  }, []);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!sectionRef.current) return;
    
    const rect = sectionRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    mouseX.set((e.clientX - centerX) / rect.width);
    mouseY.set((e.clientY - centerY) / rect.height);
  };

  return (
    <section
      ref={sectionRef}
      onMouseMove={handleMouseMove}
      className="relative w-full h-screen overflow-hidden landing-gpu-accelerated"
      style={{ background: 'linear-gradient(135deg, #050505 0%, #0A0A0A 50%, #050505 100%)' }}
    >
      {/* Animated Grid Background */}
      <div className="absolute inset-0 landing-grid opacity-30" />
      
      {/* Particles */}
      <div className="absolute inset-0">
        <Particles
          id="hero-particles"
          options={{
            background: {
              color: {
                value: "transparent",
              },
            },
            fpsLimit: 60,
            particles: {
              color: {
                value: ["#00E5FF", "#FF6A00"],
              },
              links: {
                color: "#00E5FF",
                distance: 150,
                enable: true,
                opacity: 0.2,
                width: 1,
              },
              move: {
                enable: true,
                speed: 1,
                direction: "none",
                random: false,
                straight: false,
                outModes: {
                  default: "bounce",
                },
              },
              number: {
                value: 80,
                density: {
                  enable: true,
                },
              },
              opacity: {
                value: 0.5,
              },
              shape: {
                type: "circle",
              },
              size: {
                value: { min: 1, max: 3 },
              },
            },
            detectRetina: true,
          }}
        />
      </div>

      {/* Orange Sparks */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 rounded-full"
            style={{
              background: '#FF6A00',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              boxShadow: '0 0 10px #FF6A00',
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
            }}
            transition={{
              duration: 2 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* Content Container */}
      <div className="relative z-10 h-full flex items-center">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left: Text Content */}
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="space-y-8"
            >
              {/* Title */}
              <div className="space-y-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6 }}
                  className="inline-block px-4 py-2 rounded-full landing-glass border border-[rgba(0,229,255,0.3)]"
                >
                  <span className="text-sm font-mono text-[#00E5FF]">● SYSTEM ONLINE</span>
                </motion.div>

                <h1 className="text-6xl lg:text-8xl font-bold landing-heading">
                  <span className="block text-white">ALLOY</span>
                  <span className="block landing-text-gradient-cyan">AGENT</span>
                </h1>

                <h2 className="text-xl lg:text-2xl font-semibold text-[#B8C1CC]">
                  AI-Powered Predictive Maintenance System
                  <br />
                  <span className="text-[#6B7280]">for Steel Manufacturing</span>
                </h2>

                <p className="text-base lg:text-lg text-[#B8C1CC] leading-relaxed max-w-xl">
                  Real-time anomaly detection, predictive maintenance, multi-agent intelligence,
                  and autonomous maintenance decision support.
                </p>
              </div>

              {/* Buttons */}
              <div className="flex flex-wrap gap-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={onEnterDashboard}
                  className="landing-btn-primary flex items-center gap-2 text-lg"
                  style={{ fontSize: '1.125rem' }}
                >
                  <span>Enter Command Center</span>
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                    <path d="M4 10h12m0 0l-4-4m4 4l-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="landing-btn-secondary flex items-center gap-2 text-lg"
                >
                  <Play className="w-5 h-5" />
                  <span>Watch Failure Simulation</span>
                </motion.button>
              </div>

              {/* Stats Counters */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 1 }}
                className="grid grid-cols-2 lg:grid-cols-5 gap-4 pt-8"
              >
                <StatCounter label="Equipment Online" value={counters.equipment} />
                <StatCounter label="AI Agents" value={counters.agents} />
                <StatCounter label="Knowledge Chunks" value={counters.chunks} />
                <StatCounter label="Maintenance Records" value={counters.records} />
                <StatCounter label="<" value={counters.latency} unit="ms Streaming" />
              </motion.div>
            </motion.div>

            {/* Right: 3D Holographic Plant */}
            <motion.div
              style={{ 
                rotateX, 
                rotateY, 
                transformPerspective: 1000,
                transformStyle: 'preserve-3d'
              }}
              className="relative h-[600px] hidden lg:block"
            >
              <HolographicPlant />
            </motion.div>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 2, duration: 1 }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
          className="flex flex-col items-center gap-2"
        >
          <span className="text-xs font-mono text-[#6B7280] uppercase tracking-wider">Scroll to Explore</span>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" className="text-[#00E5FF]">
            <path d="M12 5v14m0 0l-7-7m7 7l7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </motion.div>
      </motion.div>
    </section>
  );
}

// Stat Counter Component
function StatCounter({ label, value, unit }: { label: string; value: number; unit?: string }) {
  return (
    <div className="space-y-1">
      <div className="text-2xl lg:text-3xl font-bold landing-mono text-[#00E5FF]">
        {value.toLocaleString()}{unit && <span className="text-sm">{unit}</span>}
      </div>
      <div className="text-xs text-[#6B7280] uppercase tracking-wide">{label}</div>
    </div>
  );
}

// 3D Holographic Plant Component - Layered Stack Visualization
function HolographicPlant() {
  const equipment = [
    { id: 'AC-001', name: 'Air Compressor', type: 'Compressor', health: 94, temp: 82, color: '#00E5FF', delay: 0 },
    { id: 'AC-002', name: 'Air Compressor', type: 'Compressor', health: 89, temp: 78, color: '#00FF85', delay: 0.2 },
    { id: 'CF-003', name: 'Cooling Fan', type: 'Fan Unit', health: 97, temp: 65, color: '#00E5FF', delay: 0.4 },
    { id: 'RM-005', name: 'Rolling Mill', type: 'Mill', health: 91, temp: 88, color: '#FFC107', delay: 0.6 },
    { id: 'CM-007', name: 'Conveyor Motor', type: 'Motor', health: 96, temp: 72, color: '#00E5FF', delay: 0.8 },
  ];

  return (
    <div className="relative w-full h-full flex items-center justify-center perspective-1000">
      <div className="relative w-full max-w-lg">
        {/* Equipment Cards - Stacked with Depth */}
        <div className="relative" style={{ transformStyle: 'preserve-3d' }}>
          {equipment.map((item, index) => {
            const zOffset = -index * 40;
            const yOffset = index * 15;
            
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 50, rotateX: -20 }}
                animate={{ 
                  opacity: 1, 
                  y: yOffset,
                  rotateX: 0,
                  z: zOffset
                }}
                transition={{ 
                  delay: item.delay,
                  duration: 0.8,
                  type: "spring",
                  stiffness: 100
                }}
                whileHover={{ 
                  scale: 1.05, 
                  z: zOffset + 20,
                  transition: { duration: 0.3 }
                }}
                className="relative mb-4"
                style={{
                  transformStyle: 'preserve-3d',
                  transform: `translateZ(${zOffset}px) translateY(${yOffset}px)`
                }}
              >
                {/* Equipment Card */}
                <div 
                  className="landing-glass rounded-lg p-4 border"
                  style={{
                    borderColor: item.color,
                    boxShadow: `0 0 30px ${item.color}30, inset 0 0 20px ${item.color}10`,
                    backdropFilter: 'blur(20px)',
                    background: 'rgba(10, 10, 10, 0.8)'
                  }}
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="text-sm font-mono font-bold" style={{ color: item.color }}>
                        {item.id}
                      </div>
                      <div className="text-xs text-[#B8C1CC] mt-1">
                        {item.type}
                      </div>
                    </div>
                    
                    {/* Status Indicator */}
                    <motion.div
                      animate={{ 
                        opacity: [0.5, 1, 0.5],
                        scale: [1, 1.2, 1]
                      }}
                      transition={{ 
                        duration: 2, 
                        repeat: Infinity,
                        delay: item.delay 
                      }}
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: item.color }}
                    />
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    {/* Health */}
                    <div>
                      <div className="text-xs text-[#6B7280] mb-1">Health</div>
                      <div className="flex items-center gap-2">
                        <div className="text-lg font-bold font-mono" style={{ color: item.color }}>
                          {item.health}%
                        </div>
                      </div>
                      {/* Health Bar */}
                      <div className="w-full h-1 bg-white/10 rounded-full mt-1 overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.health}%` }}
                          transition={{ delay: item.delay + 0.5, duration: 1 }}
                          className="h-full rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                      </div>
                    </div>

                    {/* Temperature */}
                    <div>
                      <div className="text-xs text-[#6B7280] mb-1">Temp</div>
                      <div className="flex items-center gap-1">
                        <div className="text-lg font-bold font-mono text-[#B8C1CC]">
                          {item.temp}
                        </div>
                        <div className="text-xs text-[#6B7280]">°C</div>
                      </div>
                      {/* Temp Indicator */}
                      <div className="flex gap-1 mt-1">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className="h-1 flex-1 rounded-full"
                            style={{
                              backgroundColor: i < Math.floor(item.temp / 20) 
                                ? item.color 
                                : 'rgba(255,255,255,0.1)'
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Live Data Indicator */}
                  <div className="flex items-center gap-2 mt-3 pt-3 border-t border-white/5">
                    <motion.div
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                      className="text-xs font-mono"
                      style={{ color: item.color }}
                    >
                      ● LIVE
                    </motion.div>
                    <div className="text-xs text-[#6B7280] font-mono">
                      Streaming
                    </div>
                  </div>
                </div>

                {/* Holographic Scan Lines */}
                <motion.div
                  animate={{ y: [0, 100] }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="absolute inset-0 pointer-events-none overflow-hidden rounded-lg"
                >
                  <div 
                    className="w-full h-0.5 opacity-30"
                    style={{
                      background: `linear-gradient(90deg, transparent, ${item.color}, transparent)`
                    }}
                  />
                </motion.div>
              </motion.div>
            );
          })}
        </div>

        {/* Connection Lines in Background */}
        <svg 
          className="absolute inset-0 pointer-events-none -z-10"
          style={{ width: '100%', height: '100%' }}
        >
          {equipment.map((_, index) => {
            if (index === equipment.length - 1) return null;
            return (
              <motion.line
                key={`line-${index}`}
                x1="50%"
                y1={`${20 + index * 20}%`}
                x2="50%"
                y2={`${20 + (index + 1) * 20}%`}
                stroke="#00E5FF"
                strokeWidth="1"
                strokeDasharray="4 4"
                opacity="0.2"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 1 + index * 0.2, duration: 0.5 }}
              />
            );
          })}
        </svg>

        {/* Ambient Glow */}
        <div className="absolute inset-0 -z-20 blur-3xl opacity-30">
          <div 
            className="absolute top-0 left-1/2 w-64 h-64 rounded-full"
            style={{ 
              background: 'radial-gradient(circle, #00E5FF, transparent)',
              transform: 'translate(-50%, -50%)'
            }}
          />
          <div 
            className="absolute bottom-0 right-1/2 w-64 h-64 rounded-full"
            style={{ 
              background: 'radial-gradient(circle, #FF6A00, transparent)',
              transform: 'translate(50%, 50%)'
            }}
          />
        </div>
      </div>
    </div>
  );
}
