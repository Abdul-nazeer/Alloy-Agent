import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import Lenis from 'lenis';
import '../styles/landing/theme.css';

// Sections
import HeroSection from './landing/sections/HeroSection';
import SystemFlowSection from './landing/sections/SystemFlowSection';
import FeaturesSection from './landing/sections/FeaturesSection';
import FineTuningSection from './landing/sections/FineTuningSection';

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
            onClick={() => scrollToSection('system-flow')}
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
            onClick={() => scrollToSection('fine-tuning')}
            className="text-sm font-medium text-[#B8C1CC] hover:text-[#00E5FF] transition-colors duration-300"
          >
            AI Model
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

      {/* How it Works - Detailed System Flow */}
      <SystemFlowSection />

      {/* Features Section */}
      <FeaturesSection />

      {/* Fine-Tuning Section */}
      <FineTuningSection />
    </div>
  );
}
