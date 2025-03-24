import React, { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { ArrowPathIcon } from '@heroicons/react/24/outline';
import dynamic from 'next/dynamic';

const SpiralPhases = [
  { id: 'create', name: 'Create', description: 'Generating initial ideas and concepts' },
  { id: 'reflect', name: 'Reflect', description: 'Analysis and evaluation of generated ideas' },
  { id: 'abstract', name: 'Abstract', description: 'Identifying patterns and principles' },
  { id: 'evolve', name: 'Evolve', description: 'Transforming methodologies based on insights' },
  { id: 'transcend', name: 'Transcend', description: 'Breaking through to new creative paradigms' },
  { id: 'return', name: 'Return', description: 'Applying transcendent insights to new contexts' },
];

const SPIRAL_DATA = {
  currentPhase: 'evolve',
  problemSpace: 'blockchain gaming',
  activeShockFrameworks: ['impossibility_enforcer', 'cognitive_dissonance_amplifier'],
  generatedIdeas: [
    {
      id: 'idea-1',
      title: 'Non-Ownership Possession',
      phase: 'create',
      shockValue: 0.67
    },
    {
      id: 'idea-2',
      title: 'Temporal Asset Transformation',
      phase: 'create',
      shockValue: 0.71
    },
    {
      id: 'idea-3',
      title: 'Collective Value Emergence',
      phase: 'reflect',
      shockValue: 0.75
    },
    {
      id: 'idea-4',
      title: 'Anti-Scarcity Economics',
      phase: 'reflect',
      shockValue: 0.82
    },
    {
      id: 'idea-5',
      title: 'Multi-Temporal Ownership',
      phase: 'abstract',
      shockValue: 0.88
    },
    {
      id: 'idea-6',
      title: 'Ephemerality-Based Value System',
      phase: 'abstract',
      shockValue: 0.91
    },
    {
      id: 'idea-7',
      title: 'Temporal Ownership Collective',
      phase: 'evolve',
      shockValue: 0.94
    }
  ],
  methodologyChanges: [
    {
      id: 'method-1',
      phase: 'reflect',
      description: 'Increased emphasis on temporal paradoxes'
    },
    {
      id: 'method-2',
      phase: 'abstract',
      description: 'Integration of collective intelligence patterns'
    },
    {
      id: 'method-3',
      phase: 'evolve',
      description: 'Synthesis of temporal and value contradictions'
    }
  ],
  emergenceIndicators: {
    framework_diversity: 0.85,
    concept_recurrence: 0.62,
    novelty_trend: 0.91,
    shock_consistency: 0.73
  }
};

// Helper function to get color for phase
function getPhaseColor(phase: string): string {
  switch(phase) {
    case 'create': return 'rgb(239, 68, 68)'; // red-500
    case 'reflect': return 'rgb(59, 130, 246)'; // blue-500
    case 'abstract': return 'rgb(139, 92, 246)'; // purple-500
    case 'evolve': return 'rgb(16, 185, 129)'; // emerald-500
    case 'transcend': return 'rgb(245, 158, 11)'; // amber-500
    case 'return': return 'rgb(236, 72, 153)'; // pink-500
    default: return 'rgb(209, 213, 219)'; // gray-300
  }
}

function SpiralVisualization() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [hoveredPoint, setHoveredPoint] = useState<any>(null);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    // Set canvas dimensions
    const updateCanvasSize = () => {
      const container = canvas.parentElement;
      if (!container) return;
      
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
      
      drawSpiral();
    };
    
    // Initial size
    updateCanvasSize();
    
    // Resize handler
    window.addEventListener('resize', updateCanvasSize);
    
    // Points to draw along the spiral
    let points: any[] = [];
    
    // Draw the spiral
    function drawSpiral() {
      if (!ctx) return;
      points = [];
      
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const maxRadius = Math.min(centerX, centerY) * 0.85;
      
      // Draw spiral
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      const startAngle = 0;
      const endAngle = Math.PI * 8; // 4 full turns
      const angleStep = 0.05;
      const growthFactor = maxRadius / endAngle;
      
      for (let angle = startAngle; angle <= endAngle; angle += angleStep) {
        const radius = angle * growthFactor;
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        if (angle === startAngle) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      
      ctx.stroke();
      
      // Place ideas along the spiral
      SPIRAL_DATA.generatedIdeas.forEach((idea, index) => {
        // Calculate position
        const phaseIndex = SpiralPhases.findIndex(phase => phase.id === idea.phase);
        const angleOffset = (phaseIndex / SpiralPhases.length) * Math.PI * 2;
        const angle = Math.PI * (index + 3) + angleOffset; // Start from the middle of the spiral
        const radius = angle * growthFactor;
        
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        // Store point data
        points.push({
          x, y, 
          radius: 6 + idea.shockValue * 10,
          color: getPhaseColor(idea.phase),
          data: idea
        });
      });
      
      // Draw methodology changes
      SPIRAL_DATA.methodologyChanges.forEach((change, index) => {
        // Calculate position
        const phaseIndex = SpiralPhases.findIndex(phase => phase.id === change.phase);
        const angleOffset = (phaseIndex / SpiralPhases.length) * Math.PI * 2;
        const angle = Math.PI * (index + 5) + angleOffset; // Place later in the spiral
        const radius = angle * growthFactor;
        
        const x = centerX + Math.cos(angle) * radius;
        const y = centerY + Math.sin(angle) * radius;
        
        // Store point data
        points.push({
          x, y, 
          radius: 6,
          color: 'rgb(250, 204, 21)', // yellow-400
          isSquare: true,
          data: change
        });
      });
      
      // Draw points
      points.forEach(point => {
        ctx.save();
        
        // Glow effect
        ctx.shadowColor = point.color;
        ctx.shadowBlur = 10;
        ctx.fillStyle = point.color;
        
        if (point.isSquare) {
          // Draw square for methodology changes
          ctx.fillRect(point.x - point.radius, point.y - point.radius, point.radius * 2, point.radius * 2);
        } else {
          // Draw circle for ideas
          ctx.beginPath();
          ctx.arc(point.x, point.y, point.radius, 0, Math.PI * 2);
          ctx.fill();
        }
        
        ctx.restore();
      });
      
      // Highlight current phase
      const currentPhaseIndex = SpiralPhases.findIndex(phase => phase.id === SPIRAL_DATA.currentPhase);
      if (currentPhaseIndex >= 0) {
        const phaseAngle = (currentPhaseIndex / SpiralPhases.length) * Math.PI * 2;
        
        ctx.save();
        ctx.strokeStyle = getPhaseColor(SPIRAL_DATA.currentPhase);
        ctx.lineWidth = 3;
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        const rayLength = maxRadius * 1.2;
        const rayX = centerX + Math.cos(phaseAngle) * rayLength;
        const rayY = centerY + Math.sin(phaseAngle) * rayLength;
        ctx.lineTo(rayX, rayY);
        ctx.stroke();
        ctx.restore();
      }
    }
    
    // Handle mouse movement
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // Check if mouse is over any point
      let found = null;
      for (const point of points) {
        const dx = x - point.x;
        const dy = y - point.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance <= point.radius + 2) { // Adding 2px for easier selection
          found = point;
          break;
        }
      }
      
      if (found !== hoveredPoint) {
        setHoveredPoint(found);
      }
    };
    
    canvas.addEventListener('mousemove', handleMouseMove);
    
    // Clean up
    return () => {
      window.removeEventListener('resize', updateCanvasSize);
      canvas.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);
  
  return (
    <div className="relative h-full w-full">
      <canvas ref={canvasRef} className="w-full h-full" />
      
      {hoveredPoint && (
        <div 
          className="absolute bg-background-dark/80 p-3 rounded-lg shadow-lg backdrop-blur-sm z-10 border border-primary-light/20"
          style={{ left: hoveredPoint.x + 10, top: hoveredPoint.y + 10 }}
        >
          <div className="font-medium text-sm">{hoveredPoint.data.title || hoveredPoint.data.description}</div>
          <div className="text-xs text-gray-400 mt-1 capitalize">
            Phase: <span className="text-white">{hoveredPoint.data.phase}</span>
          </div>
          {hoveredPoint.data.shockValue && (
            <div className="text-xs text-gray-400 mt-0.5">
              Shock Value: <span className="text-highlight">{hoveredPoint.data.shockValue.toFixed(2)}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

const CreativeSpiralPage = () => {
  return (
    <>
      <Head>
        <title>Creative Spiral | Project Leela</title>
        <meta name="description" content="Visualize the meta-creative spiral process" />
      </Head>

      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-heading flex items-center">
            <ArrowPathIcon className="w-8 h-8 mr-2 text-highlight" />
            Creative Spiral
          </h1>
          <p className="text-gray-300 mt-1">
            Visualize the meta-creative spiral through Create→Reflect→Abstract→Evolve→Transcend→Return
          </p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <div className="card" style={{ height: '500px' }}>
              <h2 className="text-xl font-heading mb-4">Spiral Visualization</h2>
              <div className="h-[calc(100%-2rem)] w-full">
                <SpiralVisualization />
              </div>
            </div>
            
            <div className="card">
              <h2 className="text-xl font-heading mb-4">Spiral Journey</h2>
              
              <div className="relative">
                <div className="absolute top-0 left-1/2 h-full w-0.5 bg-primary-light/20 transform -translate-x-1/2"></div>
                
                <div className="space-y-6 relative z-10">
                  {SpiralPhases.map((phase, index) => {
                    const isActive = phase.id === SPIRAL_DATA.currentPhase;
                    const isPast = SpiralPhases.findIndex(p => p.id === SPIRAL_DATA.currentPhase) > index;
                    
                    const phaseColor = getPhaseColor(phase.id);
                    const ideas = SPIRAL_DATA.generatedIdeas.filter(idea => idea.phase === phase.id);
                    const methodChanges = SPIRAL_DATA.methodologyChanges.filter(change => change.phase === phase.id);
                    
                    return (
                      <div key={phase.id} className="flex items-start relative">
                        <div 
                          className={`
                            flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center z-20
                            ${isActive ? 'bg-background-dark' : 'bg-background-dark/50'}
                            ${isActive ? `border-2 border-[${phaseColor}]` : isPast ? 'border border-gray-500' : 'border border-gray-700'}
                          `}
                          style={{ borderColor: isActive ? phaseColor : '' }}
                        >
                          <span 
                            className={`text-xs font-bold ${isActive ? `text-[${phaseColor}]` : isPast ? 'text-gray-300' : 'text-gray-600'}`}
                            style={{ color: isActive ? phaseColor : '' }}
                          >
                            {index + 1}
                          </span>
                        </div>
                        
                        <div className="ml-4 flex-1">
                          <h3 
                            className={`text-sm font-medium ${isActive ? `text-[${phaseColor}]` : isPast ? 'text-gray-300' : 'text-gray-500'}`}
                            style={{ color: isActive ? phaseColor : '' }}
                          >
                            {phase.name} Phase
                          </h3>
                          
                          <p className={`mt-1 text-xs ${isPast || isActive ? 'text-gray-400' : 'text-gray-600'}`}>
                            {phase.description}
                          </p>
                          
                          {(ideas.length > 0 || methodChanges.length > 0) && (
                            <div className="mt-2 space-y-2">
                              {ideas.map(idea => (
                                <div key={idea.id} className="bg-background-dark/50 p-2 rounded text-xs">
                                  <div className="font-medium text-white">{idea.title}</div>
                                  <div className="text-gray-400 mt-0.5">
                                    Shock Value: <span className="text-highlight">{idea.shockValue.toFixed(2)}</span>
                                  </div>
                                </div>
                              ))}
                              
                              {methodChanges.map(change => (
                                <div key={change.id} className="bg-yellow-900/20 border border-yellow-900/30 p-2 rounded text-xs">
                                  <div className="font-medium text-yellow-400">Methodology Change</div>
                                  <div className="text-gray-300 mt-0.5">{change.description}</div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-xl font-heading mb-4">Current State</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm text-gray-400 mb-1">Current Phase</h4>
                  <div className="flex items-center">
                    <div 
                      className="w-3 h-3 rounded-full mr-2"
                      style={{ backgroundColor: getPhaseColor(SPIRAL_DATA.currentPhase) }}
                    ></div>
                    <div className="text-lg font-heading capitalize">{SPIRAL_DATA.currentPhase}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm text-gray-400 mb-1">Problem Space</h4>
                  <div className="text-white">{SPIRAL_DATA.problemSpace}</div>
                </div>
                
                <div>
                  <h4 className="text-sm text-gray-400 mb-1">Active Frameworks</h4>
                  <div className="flex flex-wrap gap-2">
                    {SPIRAL_DATA.activeShockFrameworks.map(framework => (
                      <span 
                        key={framework} 
                        className="px-2 py-1 text-xs rounded-md bg-primary-light/20 text-secondary-light border border-secondary/20"
                      >
                        {framework.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div>
                  <h4 className="text-sm text-gray-400 mb-1">Latest Idea</h4>
                  <div className="bg-background-dark/50 p-3 rounded">
                    <div className="font-medium">{SPIRAL_DATA.generatedIdeas[SPIRAL_DATA.generatedIdeas.length - 1].title}</div>
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-xs text-gray-400 capitalize">
                        {SPIRAL_DATA.generatedIdeas[SPIRAL_DATA.generatedIdeas.length - 1].phase} phase
                      </span>
                      <span className="text-xs font-mono text-highlight">
                        {SPIRAL_DATA.generatedIdeas[SPIRAL_DATA.generatedIdeas.length - 1].shockValue.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-heading mb-4">Emergence Indicators</h3>
              
              <div className="space-y-3">
                {Object.entries(SPIRAL_DATA.emergenceIndicators).map(([key, value]) => (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm capitalize">{key.replace(/_/g, ' ')}</span>
                    <div className="flex items-center">
                      <div className="w-24 h-2 bg-background-dark rounded-full overflow-hidden mr-2">
                        <div 
                          className="h-full bg-gradient-to-r from-secondary to-highlight rounded-full"
                          style={{ width: `${value * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-mono">{value.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-primary-light/20 flex justify-end">
                <button className="btn btn-outline">Advance Spiral</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default CreativeSpiralPage;