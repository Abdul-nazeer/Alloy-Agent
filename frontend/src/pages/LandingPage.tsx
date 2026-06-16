import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Lenis from 'lenis';
import '../styles/landing/theme.css';

// Sections
import HeroSection from './landing/sections/HeroSection';

export default function LandingPage() {
  const lenisRef = useRef<Lenis | null>(null);
  const navigate = useNavigate();
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  // Initialize Lenis smooth scrolling
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    });

    lenisRef.current = lenis;

    function raf(time: number) {
      lenis.raf(time);
      requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);

    return () => {
      lenis.destroy();
    };
  }, []);

  // Track global mouse position
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleEnterDashboard = () => {
    navigate('/dashboard');
  };

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-page landing-smooth-scroll relative" style={{ backgroundColor: 'var(--landing-bg-primary)' }}>
      {/* Global Mouse Glow Effect - Orange Powder (Small, Follows Everywhere) */}
      <motion.div
        className="pointer-events-none fixed z-50 mix-blend-screen"
        animate={{
          x: mousePosition.x - 75,
          y: mousePosition.y - 75,
        }}
        transition={{ type: "spring", damping: 30, stiffness: 200 }}
        style={{
          width: 150,
          height: 150,
          background: 'radial-gradient(circle, rgba(255, 106, 0, 0.6) 0%, rgba(255, 106, 0, 0.3) 40%, transparent 70%)',
          filter: 'blur(25px)',
        }}
      />

      {/* Floating Navigation Header */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, delay: 0.5 }}
        className="fixed top-6 right-6 z-50"
      >
        <div className="flex items-center gap-6 px-6 py-3 rounded-full landing-glass border border-[rgba(255,255,255,0.1)]"
          style={{
            backdropFilter: 'blur(20px)',
            background: 'rgba(10, 10, 10, 0.6)',
          }}
        >
          <button
            onClick={() => scrollToSection('how-it-works')}
            className="text-sm font-medium text-[#B8C1CC] hover:text-[#00E5FF] transition-colors duration-300"
          >
            How it Works
          </button>
          <button
            onClick={() => scrollToSection('features')}
            className="text-sm font-medium text-[#B8C1CC] hover:text-[#00E5FF] transition-colors duration-300"
          >
            Features
          </button>
          <button
            onClick={handleEnterDashboard}
            className="px-4 py-2 rounded-full text-sm font-semibold text-black bg-[#00E5FF] hover:bg-[#00B8CC] transition-all duration-300 hover:scale-105"
          >
            Login
          </button>
        </div>
      </motion.nav>

      {/* Hero Section */}
      <section id="hero">
        <HeroSection onEnterDashboard={handleEnterDashboard} />
      </section>

      {/* How it Works Section */}
      <section
        id="how-it-works"
        className="min-h-screen relative flex items-center justify-center"
        style={{ background: 'linear-gradient(180deg, #050505 0%, #0A0A0A 100%)' }}
      >
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl lg:text-7xl font-black landing-heading mb-6" style={{ color: '#00E5FF' }}>
              How it Works
            </h2>
            <p className="text-xl lg:text-2xl text-[#B8C1CC] max-w-3xl mx-auto mb-12">
              Alloy Agent uses advanced AI and multi-agent orchestration to monitor your equipment 24/7,
              detect anomalies in real-time, and generate actionable maintenance recommendations.
            </p>

            <div className="grid md:grid-cols-3 gap-8 mt-16">
              {[
                {
                  step: '01',
                  title: 'Real-Time Monitoring',
                  description: 'WebSocket streams deliver live sensor data every 15 seconds from all critical equipment.',
                },
                {
                  step: '02',
                  title: 'AI Detection',
                  description: 'Multi-agent system analyzes patterns and detects anomalies using threshold detection and ML models.',
                },
                {
                  step: '03',
                  title: 'Autonomous Action',
                  description: 'System auto-generates reports, alerts maintenance teams, and suggests repair procedures.',
                },
              ].map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.2 }}
                  viewport={{ once: true }}
                  className="landing-glass rounded-xl p-8 border border-[rgba(0,229,255,0.2)]"
                  whileHover={{ scale: 1.05, borderColor: 'rgba(0,229,255,0.5)' }}
                >
                  <div className="text-6xl font-black landing-mono mb-4" style={{ color: '#00E5FF', opacity: 0.3 }}>
                    {item.step}
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-4">{item.title}</h3>
                  <p className="text-[#B8C1CC]">{item.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section
        id="features"
        className="min-h-screen relative flex items-center justify-center"
        style={{ background: 'linear-gradient(180deg, #0A0A0A 0%, #050505 100%)' }}
      >
        <div className="container mx-auto px-6 lg:px-12 text-center">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-5xl lg:text-7xl font-black landing-heading mb-6" style={{ color: '#FF6A00' }}>
              Features
            </h2>
            <p className="text-xl lg:text-2xl text-[#B8C1CC] max-w-3xl mx-auto mb-12">
              Enterprise-grade predictive maintenance platform with autonomous AI agents,
              real-time monitoring, and intelligent diagnostics.
            </p>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mt-16">
              {[
                { icon: '🤖', title: 'Multi-Agent AI', description: '6 specialized agents working together' },
                { icon: '📡', title: 'Real-Time Data', description: 'Live sensor streaming every 15 seconds' },
                { icon: '🔍', title: 'Anomaly Detection', description: 'Threshold + ML pattern recognition' },
                { icon: '📊', title: 'RAG Knowledge', description: '2,606 maintenance manual chunks' },
                { icon: '⚡', title: 'Instant Alerts', description: 'Critical notifications in < 3 seconds' },
                { icon: '📝', title: 'Auto Reports', description: 'AI-generated maintenance documentation' },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="landing-glass rounded-xl p-6 border border-[rgba(255,106,0,0.2)]"
                  whileHover={{ scale: 1.05, borderColor: 'rgba(255,106,0,0.5)' }}
                >
                  <div className="text-5xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-[#B8C1CC]">{feature.description}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
