import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Lenis from 'lenis';
import '../styles/landing/theme.css';

// Sections
import HeroSection from './landing/sections/HeroSection';
import ScrollStorySection from './landing/sections/ScrollStorySection';
import DigitalTwinSection from './landing/sections/DigitalTwinSection';
import MultiAgentSection from './landing/sections/MultiAgentSection';
import FailureSimulationSection from './landing/sections/FailureSimulationSection';
import SystemArchitectureSection from './landing/sections/SystemArchitectureSection';
import BusinessImpactSection from './landing/sections/BusinessImpactSection';
import AIAssistantSection from './landing/sections/AIAssistantSection';
import FinalCTASection from './landing/sections/FinalCTASection';

export default function LandingPage() {
  const lenisRef = useRef<Lenis | null>(null);
  const navigate = useNavigate();

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

  const handleEnterDashboard = () => {
    navigate('/dashboard');
  };

  return (
    <div className="landing-page landing-smooth-scroll" style={{ backgroundColor: 'var(--landing-bg-primary)' }}>
      {/* Hero Section */}
      <HeroSection onEnterDashboard={handleEnterDashboard} />

      {/* Scroll Story Experience */}
      <ScrollStorySection />

      {/* Digital Twin Command Center */}
      <DigitalTwinSection />

      {/* AI Multi-Agent Orchestration */}
      <MultiAgentSection />

      {/* Failure Simulation */}
      <FailureSimulationSection />

      {/* System Architecture */}
      <SystemArchitectureSection />

      {/* Business Impact */}
      <BusinessImpactSection />

      {/* AI Assistant Showcase */}
      <AIAssistantSection />

      {/* Final CTA */}
      <FinalCTASection onLaunchDashboard={handleEnterDashboard} />
    </div>
  );
}
