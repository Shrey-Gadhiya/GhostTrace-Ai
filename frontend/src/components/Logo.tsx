import React from 'react';

interface LogoProps {
  className?: string;
  size?: number;
  showText?: boolean;
  subtitle?: string;
}

export const Logo: React.FC<LogoProps> = ({
  className = '',
  size = 32,
  showText = false,
  subtitle = 'Enterprise Privacy Audit',
}) => {
  return (
    <div className={`flex items-center space-x-3 ${className}`}>
      {/* Bespoke Rose Gold Insignia SVG */}
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 drop-shadow-sm"
      >
        <defs>
          {/* Metallic Rose Gold Gradients */}
          <linearGradient id="roseGoldLinear" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#F9DFE2" />
            <stop offset="35%" stopColor="#DCA3AC" />
            <stop offset="70%" stopColor="#B76E79" />
            <stop offset="100%" stopColor="#7E3743" />
          </linearGradient>

          <linearGradient id="roseGoldInner" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFF2F4" />
            <stop offset="45%" stopColor="#E2A6AF" />
            <stop offset="100%" stopColor="#9C4F5B" />
          </linearGradient>

          <radialGradient id="roseGoldGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#B76E79" stopOpacity="0.25" />
            <stop offset="100%" stopColor="#B76E79" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Ambient Halo */}
        <circle cx="32" cy="32" r="30" fill="url(#roseGoldGlow)" />

        {/* Outer Faceted Geometric Shield / Crest */}
        <polygon
          points="32,4 56,16 56,44 32,58 8,44 8,16"
          stroke="url(#roseGoldLinear)"
          strokeWidth="2.5"
          strokeLinejoin="round"
          fill="#1C1114"
        />

        {/* Inner Precision Verification Diamond */}
        <polygon
          points="32,13 47,32 32,51 17,32"
          stroke="url(#roseGoldInner)"
          strokeWidth="2"
          strokeLinejoin="round"
          fill="none"
        />

        {/* Forensic Lens / Trace Crosshairs */}
        <circle
          cx="32"
          cy="32"
          r="8"
          stroke="url(#roseGoldLinear)"
          strokeWidth="2"
          fill="#2A161B"
        />
        <circle
          cx="32"
          cy="32"
          r="3"
          fill="url(#roseGoldInner)"
        />

        {/* Calibrated Forensic Tick Marks */}
        <line x1="32" y1="18" x2="32" y2="21" stroke="#F9DFE2" strokeWidth="2" strokeLinecap="round" />
        <line x1="32" y1="43" x2="32" y2="46" stroke="#F9DFE2" strokeWidth="2" strokeLinecap="round" />
        <line x1="18" y1="32" x2="21" y2="32" stroke="#F9DFE2" strokeWidth="2" strokeLinecap="round" />
        <line x1="43" y1="32" x2="46" y2="32" stroke="#F9DFE2" strokeWidth="2" strokeLinecap="round" />
      </svg>

      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center space-x-1.5">
            <span className="font-bold tracking-tight text-white text-base font-serif">
              GhostTrace
            </span>
            <span className="text-[10px] font-semibold tracking-widest px-1.5 py-0.2 rounded uppercase bg-gradient-to-r from-[#DCA3AC] to-[#B76E79] text-[#1E0F13] font-sans">
              AI
            </span>
          </div>
          <span className="text-[11px] text-[#C59B9F] font-medium tracking-wide">
            {subtitle}
          </span>
        </div>
      )}
    </div>
  );
};
