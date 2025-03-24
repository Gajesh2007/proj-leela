import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { BellIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';

// Creative Spiral Logo - representing the creative process
const LeelaLogo = () => (
  <svg width="40" height="40" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="transform scale-75">
    {/* Central circle - representing core creative concepts */}
    <circle cx="60" cy="60" r="10" fill="url(#centralGradient)" className="animate-pulse-slow" />
    
    {/* Outer rings - representing layers of creation/manifestation */}
    {[20, 30, 40, 50].map((radius, i) => (
      <circle 
        key={`ring-${i}`}
        cx="60" 
        cy="60" 
        r={radius} 
        stroke={`url(#ringGradient-${i})`} 
        strokeWidth="1.5"
        strokeDasharray={radius * Math.PI * (0.5 + (i * 0.1))} 
        strokeDashoffset={radius * -Math.PI * 0.2}
        fill="none" 
        className={`animate-spin-slow-${i + 1}`}
        style={{ animationDuration: `${30 + i * 10}s` }}
      />
    ))}
    
    {/* Golden ratio spiral - representing perfect harmony and growth */}
    <path 
      d="M60,60 Q70,50 80,60 T100,60 T60,100 T20,60 T60,20 T100,60"
      stroke="url(#spiralGradient)"
      strokeWidth="2"
      fill="none"
      className="animate-draw"
      strokeLinecap="round"
    />
    
    {/* Creative nodes - seven small circles representing innovative connection points */}
    {[0, 1, 2, 3, 4, 5, 6].map((i) => {
      const angle = (i * Math.PI * 2) / 7;
      const x = 60 + Math.cos(angle) * 25;
      const y = 60 + Math.sin(angle) * 25;
      return (
        <circle 
          key={`point-${i}`} 
          cx={x} 
          cy={y} 
          r="2.5" 
          fill={`url(#pointGradient-${i})`}
          className="animate-pulse-slow"
        />
      );
    })}
    
    {/* Radiant lines - representing the emanation of consciousness */}
    {[0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330].map((angle, i) => {
      const radian = (angle * Math.PI) / 180;
      const x1 = 60 + Math.cos(radian) * 12;
      const y1 = 60 + Math.sin(radian) * 12;
      const x2 = 60 + Math.cos(radian) * 55;
      const y2 = 60 + Math.sin(radian) * 55;
      return (
        <line 
          key={`line-${i}`}
          x1={x1} 
          y1={y1} 
          x2={x2} 
          y2={y2} 
          stroke="url(#rayGradient)" 
          strokeWidth="0.5"
          strokeOpacity="0.5"
          className="animate-pulse-slow"
        />
      );
    })}
    
    {/* Gradients */}
    <defs>
      {/* Central consciousness */}
      <radialGradient id="centralGradient" cx="50%" cy="50%" r="50%" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#FFFFFF" />
        <stop offset="100%" stopColor="#AF7AC5" />
      </radialGradient>
      
      {/* Spiral path */}
      <linearGradient id="spiralGradient" x1="0%" y1="0%" x2="100%" y2="100%" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#5D83E4" />
        <stop offset="50%" stopColor="#7AE9DC" />
        <stop offset="100%" stopColor="#F5CA45" />
      </linearGradient>
      
      {/* Emanating rays */}
      <linearGradient id="rayGradient" x1="0%" y1="0%" x2="100%" y2="0%" gradientUnits="userSpaceOnUse">
        <stop offset="0%" stopColor="#FFFFFF" />
        <stop offset="100%" stopColor="#5D83E4" stopOpacity="0" />
      </linearGradient>
      
      {/* Rings */}
      {[0, 1, 2, 3].map((i) => (
        <linearGradient key={`ring-grad-${i}`} id={`ringGradient-${i}`} x1="0%" y1="0%" x2="100%" y2="100%" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor={i % 2 === 0 ? "#5D83E4" : "#AF7AC5"} />
          <stop offset="50%" stopColor="#7AE9DC" />
          <stop offset="100%" stopColor={i % 2 === 0 ? "#F5CA45" : "#5D83E4"} />
        </linearGradient>
      ))}
      
      {/* Chakra points */}
      {[0, 1, 2, 3, 4, 5, 6].map((i) => {
        // Create colors representing chakra colors from root to crown
        const colors = ["#FF0000", "#FF7F00", "#FFFF00", "#00FF00", "#0000FF", "#4B0082", "#9400D3"];
        return (
          <radialGradient key={`point-grad-${i}`} id={`pointGradient-${i}`} cx="50%" cy="50%" r="50%" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="100%" stopColor={colors[i]} />
          </radialGradient>
        );
      })}
    </defs>
  </svg>
);

const Navbar: React.FC = () => {
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  return (
    <header className="bg-white/70 border-b border-slate-100 sticky top-0 z-50 backdrop-blur-md shadow-soft-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="flex items-center group">
              <div className="relative flex items-center justify-center p-1 mr-3 group-hover:shadow-primary-glow transition-all duration-500">
                <LeelaLogo />
              </div>
              <div>
                <span className="text-2xl font-heading bg-gradient-to-r from-primary via-spiritual to-accent text-transparent bg-clip-text font-semibold tracking-tight">Leela</span>
              </div>
            </Link>
          </div>
          
          <div className="flex items-center space-x-5">
            {mounted ? (
              <>
                <Link 
                  href="/notifications" 
                  className="text-text-light hover:text-primary transition-colors p-2 rounded-full hover:bg-primary/5"
                  aria-label="Notifications"
                >
                  <BellIcon className="w-5 h-5" />
                </Link>
                
                <Link 
                  href="/settings" 
                  className="text-text-light hover:text-primary transition-colors p-2 rounded-full hover:bg-primary/5"
                  aria-label="Settings"
                >
                  <Cog6ToothIcon className="w-5 h-5" />
                </Link>
                
                <a 
                  href="https://github.com/your-username/project-leela" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-text-light hover:text-text-dark transition-colors"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                </a>
                
                <div className="border-l h-6 border-slate-200 mx-2"></div>
                
                <button className="bg-gradient-to-r from-primary to-spiritual hover:shadow-primary-glow text-white py-1.5 px-4 rounded-full text-sm font-medium transition-all duration-300">
                  New Idea
                </button>
              </>
            ) : (
              <div className="flex items-center space-x-5">
                <div className="w-5 h-5 rounded-full bg-slate-200 animate-pulse"></div>
                <div className="w-5 h-5 rounded-full bg-slate-200 animate-pulse"></div>
                <div className="w-5 h-5 rounded-full bg-slate-200 animate-pulse"></div>
                <div className="border-l h-6 border-slate-200 mx-2"></div>
                <div className="w-20 h-8 rounded-full bg-slate-200 animate-pulse"></div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;