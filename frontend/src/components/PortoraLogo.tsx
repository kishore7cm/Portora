import React from 'react';

interface PortoraLogoProps {
  size?: number;
  variant?: 'default' | 'light' | 'dark';
  iconOnly?: boolean;
  className?: string;
}

export const PortoraLogo: React.FC<PortoraLogoProps> = ({ 
  size = 40, 
  variant = 'default',
  iconOnly = false,
  className = ''
}) => {
  // Use brand colors from design system
  const textColor = variant === 'light' ? '#FFFFFF' : variant === 'dark' ? '#000000' : '#171717'; // neutral-900
  const iconColor = variant === 'light' ? '#FFFFFF' : '#0ea5e9'; // brand-500
  
  if (iconOnly) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className={className}
      >
        {/* P with integrated upward arrow */}
        {/* Vertical stem (arrow shaft) */}
        <path
          d="M 35 75 L 35 25"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Arrow head at top */}
        <path
          d="M 25 35 L 35 25 L 45 35"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        
        {/* P bowl */}
        <path
          d="M 35 35 L 55 35 C 65 35 70 40 70 48 C 70 56 65 61 55 61 L 35 61"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        
        {/* Insights: Ascending chart bars inside the P bowl */}
        <rect x="48" y="52" width="4" height="6" rx="1" fill={iconColor} opacity="0.4" />
        <rect x="54" y="48" width="4" height="10" rx="1" fill={iconColor} opacity="0.6" />
        <rect x="60" y="43" width="4" height="15" rx="1" fill={iconColor} opacity="0.8" />
        
        {/* Data trend line connecting the bars */}
        <path
          d="M 50 52 L 56 48 L 62 43"
          stroke={iconColor}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.5"
        />
        
        {/* Insight spark - data point at trend peak */}
        <circle cx="62" cy="43" r="2" fill={iconColor}>
          <animate
            attributeName="r"
            values="2;3;2"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>
    );
  }
  
  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* P with integrated upward arrow */}
        {/* Vertical stem (arrow shaft) */}
        <path
          d="M 35 75 L 35 25"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
        />
        
        {/* Arrow head at top */}
        <path
          d="M 25 35 L 35 25 L 45 35"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        
        {/* P bowl */}
        <path
          d="M 35 35 L 55 35 C 65 35 70 40 70 48 C 70 56 65 61 55 61 L 35 61"
          stroke={iconColor}
          strokeWidth="8"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
        
        {/* Insights: Ascending chart bars inside the P bowl */}
        <rect x="48" y="52" width="4" height="6" rx="1" fill={iconColor} opacity="0.4" />
        <rect x="54" y="48" width="4" height="10" rx="1" fill={iconColor} opacity="0.6" />
        <rect x="60" y="43" width="4" height="15" rx="1" fill={iconColor} opacity="0.8" />
        
        {/* Data trend line connecting the bars */}
        <path
          d="M 50 52 L 56 48 L 62 43"
          stroke={iconColor}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.5"
        />
        
        {/* Insight spark - data point at trend peak */}
        <circle cx="62" cy="43" r="2" fill={iconColor}>
          <animate
            attributeName="r"
            values="2;3;2"
            dur="2s"
            repeatCount="indefinite"
          />
        </circle>
      </svg>
      
      <svg
        height={size * 0.5}
        viewBox="0 0 420 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ height: size * 0.5 }}
      >
        <text
          x="0"
          y="72"
          fill={textColor}
          style={{
            fontSize: '88px',
            fontFamily: 'system-ui, -apple-system, "Segoe UI", sans-serif',
            fontWeight: '600',
            letterSpacing: '-0.025em'
          }}
        >
          portora
        </text>
      </svg>
    </div>
  );
};

