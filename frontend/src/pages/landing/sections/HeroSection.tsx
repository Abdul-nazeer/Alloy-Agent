import { useEffect, useRef, useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import Particles from '@tsparticles/react';
import { Play, Factory, Settings, Thermometer, Wind, Wrench, BarChart3, Bot, Zap } from 'lucide-react';

interface HeroSectionProps {
  onEnterDashboard: () => void;
}

export default function HeroSection({ onEnterDashboard }: HeroSectionProps) {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [cursorVisible, setCursorVisible] = useState(true);
  
  // Mouse parallax
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  
  const springConfig = { damping: 25, stiffness: 150 };
  const x = useSpring(mouseX, springConfig);
  const y = useSpring(mouseY, springConfig);
  
  const rotateX = useTransform(y, [-0.5, 0.5], ["5deg", "-5deg"]);
  const rotateY = useTransform(x, [-0.5, 0.5], ["-5deg", "5deg"]);

  // Blinking cursor animation
  useEffect(() => {
    const interval = setInterval(() => {
      setCursorVisible((prev) => !prev);
    }, 530); // Blink every 530ms
    return () => clearInterval(interval);
  }, []);

  // Track mouse position for parallax
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!sectionRef.current) return;
    
    const rect = sectionRef.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    mouseX.set((e.clientX - centerX) / rect.width);
    mouseY.set((e.clientY - centerY) / rect.height);
  };

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

  return (
    <section
      ref={sectionRef}
      onMouseMove={handleMouseMove}
      className="relative w-full h-screen overflow-hidden landing-gpu-accelerated"
      style={{ background: 'linear-gradient(135deg, #050505 0%, #0A0A0A 50%, #050505 100%)' }}
    >
      {/* Fluid Background Wave Effect */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 50%, rgba(0, 229, 255, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(255, 106, 0, 0.08) 0%, transparent 50%),
              radial-gradient(circle at 40% 20%, rgba(0, 229, 255, 0.05) 0%, transparent 40%)
            `,
            backgroundSize: '100% 100%',
          }}
          animate={{
            backgroundPosition: [
              '0% 0%, 100% 100%, 50% 0%',
              '100% 50%, 0% 0%, 100% 100%',
              '0% 100%, 50% 50%, 0% 0%',
              '0% 0%, 100% 100%, 50% 0%',
            ],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      </div>

      {/* Giant Background Text - Animated "Innovation That Matters" Style */}
      <div className="absolute inset-0 flex items-center justify-center overflow-hidden pointer-events-none">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.06 }}
          transition={{ duration: 2 }}
          className="text-center whitespace-nowrap"
          style={{
            fontSize: 'clamp(120px, 18vw, 280px)',
            fontWeight: 900,
            lineHeight: 0.9,
            color: '#B8C1CC',
            textTransform: 'uppercase',
            letterSpacing: '-0.05em',
          }}
        >
          {/* PREDICTIVE - Moving Right to Left */}
          <motion.div
            animate={{ x: [0, -100, 0] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            Predictive
          </motion.div>
          
          {/* MAINTENANCE - Moving Left to Right */}
          <motion.div
            animate={{ x: [0, 100, 0] }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
          >
            Maintenance
          </motion.div>
          
          {/* INTELLIGENCE - Static with Cyan Tint */}
          <div style={{ color: '#00E5FF', opacity: 0.15 }}>Intelligence</div>
        </motion.div>
      </div>

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
              {/* Title with Blinking Cursor */}
              <div className="space-y-4">
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.6 }}
                  className="inline-block px-4 py-2 rounded-full landing-glass border border-[rgba(0,229,255,0.3)]"
                >
                  <span className="text-sm font-mono text-[#00E5FF]">● SYSTEM ONLINE</span>
                </motion.div>

                <h1 
                  className="text-6xl lg:text-8xl xl:text-9xl font-black landing-heading"
                  style={{ 
                    fontWeight: 900,
                    letterSpacing: '-0.04em',
                  }}
                >
                  <span className="block text-white">ALLOY</span>
                  <span className="block landing-text-gradient-cyan inline-flex items-center">
                    AGENT
                    <motion.span
                      animate={{ opacity: cursorVisible ? 1 : 0 }}
                      className="inline-block w-1 lg:w-2 h-16 lg:h-24 xl:h-32 bg-[#00E5FF] ml-2 lg:ml-4"
                      style={{
                        boxShadow: '0 0 20px rgba(0, 229, 255, 0.8)',
                      }}
                    />
                  </span>
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
              <div className="space-y-4">
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

                {/* Demo Access Note */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.5, duration: 1 }}
                  className="flex items-center gap-2 text-sm"
                >
                  <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ backgroundColor: 'rgba(0, 229, 255, 0.1)', border: '1px solid rgba(0, 229, 255, 0.3)' }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="text-[#00E5FF]">
                      <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" stroke="currentColor" strokeWidth="2"/>
                      <path d="M12 16v-4m0-4h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span className="font-mono font-medium text-[#00E5FF]">Demo Access</span>
                  </div>
                  <span className="text-[#B8C1CC]">No login required - Select role to explore</span>
                </motion.div>
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

// Radar Visualization Component - Steel Manufacturing Theme
function HolographicPlant() {
  const [revealedIcons, setRevealedIcons] = useState<Set<number>>(new Set());
  const [radarAngle, setRadarAngle] = useState(0);

  // Equipment/Technology icons positioned on radar - Using Lucide Icons
  const radarIcons = [
    { id: 1, angle: 30, radius: 0.7, Icon: Factory, label: 'Blast Furnace', color: '#FF6A00' },
    { id: 2, angle: 80, radius: 0.5, Icon: Settings, label: 'Compressor', color: '#00E5FF' },
    { id: 3, angle: 135, radius: 0.8, Icon: Thermometer, label: 'Sensors', color: '#00FF85' },
    { id: 4, angle: 170, radius: 0.4, Icon: Wind, label: 'Cooling', color: '#00E5FF' },
    { id: 5, angle: 215, radius: 0.65, Icon: Wrench, label: 'Maintenance', color: '#FFC107' },
    { id: 6, angle: 260, radius: 0.55, Icon: BarChart3, label: 'Analytics', color: '#00E5FF' },
    { id: 7, angle: 310, radius: 0.75, Icon: Bot, label: 'AI Agent', color: '#FF6A00' },
    { id: 8, angle: 350, radius: 0.45, Icon: Zap, label: 'Power', color: '#00FF85' },
  ];

  // Radar sweep animation
  useEffect(() => {
    const interval = setInterval(() => {
      setRadarAngle((prev) => {
        const newAngle = (prev + 2) % 360;
        
        // Check which icons should be revealed
        radarIcons.forEach((icon) => {
          // Calculate if radar line has passed this icon
          const angleDiff = (newAngle - icon.angle + 360) % 360;
          if (angleDiff < 2 || angleDiff > 358) {
            setRevealedIcons((prevSet) => new Set(prevSet).add(icon.id));
          }
          
          // Fade icons after radar passes (simulating radar decay)
          if (angleDiff > 120) {
            setRevealedIcons((prevSet) => {
              const newSet = new Set(prevSet);
              newSet.delete(icon.id);
              return newSet;
            });
          }
        });
        
        return newAngle;
      });
    }, 30); // Smooth 60 FPS animation

    return () => clearInterval(interval);
  }, []);

  const radarSize = 500;
  const centerX = radarSize / 2;
  const centerY = radarSize / 2;

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <div className="relative" style={{ width: radarSize, height: radarSize }}>
        {/* Radar Circles */}
        <svg className="absolute inset-0" width={radarSize} height={radarSize}>
          {/* Background circles */}
          {[0.25, 0.5, 0.75, 1].map((scale, i) => (
            <circle
              key={i}
              cx={centerX}
              cy={centerY}
              r={(radarSize / 2 - 20) * scale}
              fill="none"
              stroke="rgba(0, 229, 255, 0.2)"
              strokeWidth="1"
            />
          ))}
          
          {/* Cross lines */}
          <line
            x1={20}
            y1={centerY}
            x2={radarSize - 20}
            y2={centerY}
            stroke="rgba(0, 229, 255, 0.1)"
            strokeWidth="1"
          />
          <line
            x1={centerX}
            y1={20}
            x2={centerX}
            y2={radarSize - 20}
            stroke="rgba(0, 229, 255, 0.1)"
            strokeWidth="1"
          />
          
          {/* Radar Sweep Line */}
          <motion.line
            x1={centerX}
            y1={centerY}
            x2={
              centerX +
              Math.cos((radarAngle * Math.PI) / 180) * (radarSize / 2 - 20)
            }
            y2={
              centerY +
              Math.sin((radarAngle * Math.PI) / 180) * (radarSize / 2 - 20)
            }
            stroke="url(#radarGradient)"
            strokeWidth="2"
          />
          
          {/* Gradient for sweep line */}
          <defs>
            <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgba(0, 229, 255, 0)" />
              <stop offset="100%" stopColor="rgba(0, 229, 255, 1)" />
            </linearGradient>
            <radialGradient id="sweepGradient">
              <stop offset="0%" stopColor="rgba(0, 229, 255, 0.3)" />
              <stop offset="100%" stopColor="rgba(0, 229, 255, 0)" />
            </radialGradient>
          </defs>
          
          {/* Radar Sweep Cone/Area */}
          <motion.path
            d={`
              M ${centerX} ${centerY}
              L ${centerX + Math.cos((radarAngle * Math.PI) / 180) * (radarSize / 2 - 20)} 
                ${centerY + Math.sin((radarAngle * Math.PI) / 180) * (radarSize / 2 - 20)}
              A ${radarSize / 2 - 20} ${radarSize / 2 - 20} 0 0 0
                ${centerX + Math.cos(((radarAngle - 45) * Math.PI) / 180) * (radarSize / 2 - 20)}
                ${centerY + Math.sin(((radarAngle - 45) * Math.PI) / 180) * (radarSize / 2 - 20)}
              Z
            `}
            fill="url(#sweepGradient)"
            opacity="0.5"
          />
        </svg>

        {/* Center Core */}
        <div
          className="absolute"
          style={{
            top: centerY - 30,
            left: centerX - 30,
            width: 60,
            height: 60,
          }}
        >
          <motion.div
            animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-full h-full rounded-full landing-glass border-2 border-[#00E5FF] flex items-center justify-center"
            style={{
              boxShadow: '0 0 40px rgba(0, 229, 255, 0.5)',
            }}
          >
            <span className="text-xs font-mono font-bold text-[#00E5FF]">ALLOY</span>
          </motion.div>
        </div>

        {/* Equipment Icons */}
        {radarIcons.map((item) => {
          const x =
            centerX +
            Math.cos((item.angle * Math.PI) / 180) *
              (radarSize / 2 - 50) *
              item.radius;
          const y =
            centerY +
            Math.sin((item.angle * Math.PI) / 180) *
              (radarSize / 2 - 50) *
              item.radius;
          
          const isRevealed = revealedIcons.has(item.id);
          const IconComponent = item.Icon;

          return (
            <motion.div
              key={item.id}
              className="absolute"
              style={{
                left: x - 25,
                top: y - 25,
              }}
              initial={{ opacity: 0, scale: 0 }}
              animate={{
                opacity: isRevealed ? 1 : 0.15,
                scale: isRevealed ? 1 : 0.6,
              }}
              transition={{ 
                duration: 0.4,
                ease: "easeOut"
              }}
            >
              <motion.div
                whileHover={{ scale: 1.2 }}
                className="relative w-12 h-12 rounded-lg landing-glass border flex items-center justify-center cursor-pointer"
                style={{
                  borderColor: isRevealed ? item.color : 'rgba(255,255,255,0.1)',
                  boxShadow: isRevealed
                    ? `0 0 20px ${item.color}40`
                    : 'none',
                  transition: 'all 0.4s ease-out',
                }}
              >
                <IconComponent 
                  size={24} 
                  style={{ 
                    color: isRevealed ? item.color : '#6B7280',
                    transition: 'color 0.4s ease-out'
                  }} 
                />
                
                {/* Pulse effect when revealed */}
                {isRevealed && (
                  <motion.div
                    className="absolute inset-0 rounded-lg border-2"
                    style={{ borderColor: item.color }}
                    initial={{ scale: 1, opacity: 0.8 }}
                    animate={{ scale: 1.5, opacity: 0 }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </motion.div>
              
              {/* Label */}
              <div className="absolute -bottom-6 left-1/2 transform -translate-x-1/2 whitespace-nowrap">
                <motion.span
                  className="text-xs font-mono"
                  style={{ color: isRevealed ? item.color : '#6B7280' }}
                  animate={{ opacity: isRevealed ? 1 : 0.4 }}
                  transition={{ duration: 0.4 }}
                >
                  {item.label}
                </motion.span>
              </div>
            </motion.div>
          );
        })}

        {/* Grid Lines (subtle background) */}
        <svg className="absolute inset-0 pointer-events-none opacity-10" width={radarSize} height={radarSize}>
          {/* Radial lines */}
          {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
            <line
              key={angle}
              x1={centerX}
              y1={centerY}
              x2={
                centerX +
                Math.cos((angle * Math.PI) / 180) * (radarSize / 2 - 20)
              }
              y2={
                centerY +
                Math.sin((angle * Math.PI) / 180) * (radarSize / 2 - 20)
              }
              stroke="rgba(0, 229, 255, 0.3)"
              strokeWidth="1"
            />
          ))}
        </svg>

        {/* Ambient Glow */}
        <div className="absolute inset-0 -z-10 blur-3xl opacity-30 pointer-events-none">
          <div
            className="absolute top-1/2 left-1/2 w-full h-full rounded-full"
            style={{
              background: 'radial-gradient(circle, #00E5FF, transparent)',
              transform: 'translate(-50%, -50%)',
            }}
          />
        </div>
      </div>
    </div>
  );
}
