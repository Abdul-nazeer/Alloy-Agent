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
              style={{ rotateX, rotateY, transformPerspective: 1000 }}
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

// 3D Holographic Plant Component
function HolographicPlant() {
  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Central Hub */}
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
        className="relative"
      >
        {/* Plant Components in circular layout */}
        {[
          { name: 'Blast Furnace', angle: 0, color: '#00E5FF' },
          { name: 'Conveyor', angle: 72, color: '#FF6A00' },
          { name: 'Cooling Tower', angle: 144, color: '#00E5FF' },
          { name: 'Compressor', angle: 216, color: '#FF6A00' },
          { name: 'Rolling Mill', angle: 288, color: '#00E5FF' },
        ].map((component, i) => {
          const radius = 200;
          const x = Math.cos((component.angle * Math.PI) / 180) * radius;
          const y = Math.sin((component.angle * Math.PI) / 180) * radius;

          return (
            <motion.div
              key={component.name}
              className="absolute"
              style={{
                left: `calc(50% + ${x}px)`,
                top: `calc(50% + ${y}px)`,
                transform: 'translate(-50%, -50%)',
              }}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.2 + 0.5 }}
            >
              <div className="relative">
                {/* Holographic Node */}
                <div
                  className="w-20 h-20 rounded-lg landing-holographic flex items-center justify-center"
                  style={{
                    borderColor: component.color,
                    boxShadow: `0 0 20px ${component.color}40`,
                  }}
                >
                  <div className="w-12 h-12 rounded-lg border-2 landing-pulse"
                    style={{ borderColor: component.color }}
                  />
                </div>

                {/* Label */}
                <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                  <span className="text-xs font-mono text-[#B8C1CC]">{component.name}</span>
                </div>

                {/* Connection Line to Center */}
                <svg
                  className="absolute top-1/2 left-1/2 pointer-events-none"
                  style={{
                    width: radius * 2,
                    height: radius * 2,
                    transform: 'translate(-50%, -50%)',
                  }}
                >
                  <line
                    x1={radius}
                    y1={radius}
                    x2={radius - x}
                    y2={radius - y}
                    stroke={component.color}
                    strokeWidth="1"
                    strokeDasharray="4 4"
                    opacity="0.3"
                  >
                    <animate
                      attributeName="stroke-dashoffset"
                      from="0"
                      to="8"
                      dur="1s"
                      repeatCount="indefinite"
                    />
                  </line>
                </svg>
              </div>
            </motion.div>
          );
        })}

        {/* Center Core */}
        <div className="w-32 h-32 rounded-full landing-glass flex items-center justify-center relative"
          style={{
            border: '2px solid #00E5FF',
            boxShadow: '0 0 40px rgba(0, 229, 255, 0.5), inset 0 0 40px rgba(0, 229, 255, 0.2)',
          }}
        >
          <motion.div
            animate={{ scale: [1, 1.1, 1], opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-24 h-24 rounded-full"
            style={{
              background: 'radial-gradient(circle, #00E5FF40 0%, transparent 70%)',
            }}
          />
          <span className="absolute text-sm font-mono font-bold text-[#00E5FF]">CORE</span>
        </div>
      </motion.div>
    </div>
  );
}
