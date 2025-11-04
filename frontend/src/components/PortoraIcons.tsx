import React from 'react';

interface IconProps {
  size?: number;
  color?: string;
  className?: string;
}

export const PortfolioIcon: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Stacked layers representing consolidated portfolios */}
      <rect x="4" y="13" width="16" height="2" rx="1" fill={color} opacity="0.3" />
      <rect x="4" y="9" width="16" height="2" rx="1" fill={color} opacity="0.6" />
      <rect x="4" y="5" width="16" height="2" rx="1" fill={color} />
      {/* Upward arrow indicating growth */}
      <path 
        d="M12 13L12 19M9 16L12 19L15 16" 
        stroke={color} 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
      />
    </svg>
  );
};

export const InsightsIcon: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Chart bars with upward trend */}
      <rect x="4" y="14" width="3" height="6" rx="1.5" fill={color} opacity="0.4" />
      <rect x="9" y="10" width="3" height="10" rx="1.5" fill={color} opacity="0.6" />
      <rect x="14" y="6" width="3" height="14" rx="1.5" fill={color} />
      {/* Trend line */}
      <path 
        d="M5 15L10 11L15 7L19 4" 
        stroke={color} 
        strokeWidth="1.5" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        opacity="0.5"
      />
      {/* Data point */}
      <circle cx="19" cy="4" r="2" fill={color} />
    </svg>
  );
};

export const CommunityIcon: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Three overlapping circles representing people */}
      <circle cx="9" cy="9" r="3.5" stroke={color} strokeWidth="1.5" fill="none" />
      <circle cx="15" cy="9" r="3.5" stroke={color} strokeWidth="1.5" fill="none" />
      <circle cx="12" cy="14" r="3.5" stroke={color} strokeWidth="1.5" fill="none" />
      {/* Connection points */}
      <circle cx="9" cy="9" r="1" fill={color} opacity="0.6" />
      <circle cx="15" cy="9" r="1" fill={color} opacity="0.6" />
      <circle cx="12" cy="14" r="1" fill={color} opacity="0.6" />
    </svg>
  );
};

// Alternative simpler versions
export const PortfolioIconSimple: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Briefcase/folder style */}
      <rect x="4" y="8" width="16" height="11" rx="2" stroke={color} strokeWidth="1.5" fill="none" />
      <path d="M8 8V7C8 5.89543 8.89543 5 10 5H14C15.1046 5 16 5.89543 16 7V8" stroke={color} strokeWidth="1.5" />
      <line x1="4" y1="12" x2="20" y2="12" stroke={color} strokeWidth="1.5" opacity="0.3" />
    </svg>
  );
};

export const InsightsIconSimple: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Lightbulb or spark representing insight */}
      <circle cx="12" cy="10" r="4.5" stroke={color} strokeWidth="1.5" fill="none" />
      <path d="M10 15.5C10 15.5 10 17 10 17.5C10 18.3284 10.6716 19 11.5 19H12.5C13.3284 19 14 18.3284 14 17.5C14 17 14 15.5 14 15.5" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="12" y1="5" x2="12" y2="6" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="6" y1="10" x2="7" y2="10" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
      <line x1="17" y1="10" x2="18" y2="10" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
};

export const CommunityIconSimple: React.FC<IconProps> = ({ 
  size = 24, 
  color = 'currentColor',
  className = '' 
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Simple people icons */}
      <circle cx="8" cy="8" r="2.5" stroke={color} strokeWidth="1.5" fill="none" />
      <path d="M3 18C3 15.7909 4.79086 14 7 14H9C11.2091 14 13 15.7909 13 18V19H3V18Z" stroke={color} strokeWidth="1.5" fill="none" />
      <circle cx="17" cy="8" r="2.5" stroke={color} strokeWidth="1.5" fill="none" />
      <path d="M21 19V18C21 16.3431 19.6569 15 18 15H17" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
};

