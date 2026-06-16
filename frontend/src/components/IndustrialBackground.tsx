export default function IndustrialBackground() {
  return (
    <div className="industrial-background">
      {/* Grid layer */}
      <div className="industrial-grid" />
      
      {/* Floating particles */}
      {[...Array(20)].map((_, i) => (
        <div
          key={`particle-${i}`}
          className="particle"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 8}s`,
          }}
        />
      ))}
      
      {/* Data streams */}
      {[...Array(5)].map((_, i) => (
        <div
          key={`stream-${i}`}
          className="data-stream"
          style={{
            left: `${20 + i * 20}%`,
            animationDelay: `${Math.random() * 6}s`,
          }}
        />
      ))}
      
      {/* Glow blobs */}
      <div 
        className="glow-blob" 
        style={{ 
          top: '20%', 
          left: '10%',
          animationDelay: '0s'
        }} 
      />
      <div
        className="glow-blob"
        style={{ 
          top: '60%', 
          right: '15%', 
          animationDelay: '4s' 
        }}
      />
      <div
        className="glow-blob"
        style={{ 
          bottom: '20%', 
          left: '50%', 
          animationDelay: '8s' 
        }}
      />
      
      {/* Orange sparks */}
      {[...Array(10)].map((_, i) => (
        <div
          key={`spark-${i}`}
          className="spark"
          style={{
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            // @ts-ignore - CSS custom properties
            '--spark-x': `${(Math.random() - 0.5) * 200}px`,
            '--spark-y': `${(Math.random() - 0.5) * 200}px`,
            animationDelay: `${Math.random() * 4}s`,
          }}
        />
      ))}
    </div>
  );
}
