interface AlloyAgentIconProps {
  size?: number;
  className?: string;
  animated?: boolean;
}

export default function AlloyAgentIcon({ size = 40, className = '', animated = false }: AlloyAgentIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer hexagon frame */}
      <path
        d="M50 5 L85 27.5 L85 72.5 L50 95 L15 72.5 L15 27.5 Z"
        stroke="url(#gradient1)"
        strokeWidth="2"
        fill="none"
        opacity="0.6"
      />
      
      {/* Inner hexagon */}
      <path
        d="M50 15 L75 30 L75 70 L50 85 L25 70 L25 30 Z"
        fill="url(#gradient2)"
        opacity="0.2"
      />
      
      {/* Central "A" for Alloy - industrial style */}
      <path
        d="M50 35 L60 60 L56 60 L54 54 L46 54 L44 60 L40 60 L50 35 Z M48 50 L52 50 L50 42 Z"
        fill="url(#gradient3)"
      />
      
      {/* Gear teeth pattern - industrial feel */}
      <circle
        cx="50"
        cy="50"
        r="28"
        stroke="url(#gradient4)"
        strokeWidth="1"
        fill="none"
        strokeDasharray="4 4"
        opacity="0.4"
      />
      
      {/* Corner accents - tech feel */}
      <circle cx="50" cy="20" r="2" fill="#00E5FF" opacity="0.8">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" />}
      </circle>
      <circle cx="73" cy="35" r="2" fill="#00E5FF" opacity="0.6">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin="0.3s" repeatCount="indefinite" />}
      </circle>
      <circle cx="73" cy="65" r="2" fill="#FF6A00" opacity="0.6">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin="0.6s" repeatCount="indefinite" />}
      </circle>
      <circle cx="50" cy="80" r="2" fill="#FF6A00" opacity="0.8">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin="0.9s" repeatCount="indefinite" />}
      </circle>
      <circle cx="27" cy="65" r="2" fill="#00E5FF" opacity="0.6">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin="1.2s" repeatCount="indefinite" />}
      </circle>
      <circle cx="27" cy="35" r="2" fill="#FF6A00" opacity="0.6">
        {animated && <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" begin="1.5s" repeatCount="indefinite" />}
      </circle>
      
      {/* Gradients */}
      <defs>
        <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#0099CC" stopOpacity="0.4" />
        </linearGradient>
        <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00E5FF" stopOpacity="0.15" />
          <stop offset="100%" stopColor="#FF6A00" stopOpacity="0.05" />
        </linearGradient>
        <linearGradient id="gradient3" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#00E5FF" />
          <stop offset="100%" stopColor="#0099CC" />
        </linearGradient>
        <linearGradient id="gradient4" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#00E5FF" />
          <stop offset="50%" stopColor="#FF6A00" />
          <stop offset="100%" stopColor="#00E5FF" />
        </linearGradient>
      </defs>
    </svg>
  );
}
