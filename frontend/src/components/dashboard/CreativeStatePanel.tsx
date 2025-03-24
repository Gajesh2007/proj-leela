import React from 'react';
import { CubeTransparentIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { useLeela } from '../../services/LeelaContext';

const CreativeStatePanel = () => {
  const { creativeState, getAverageShockMetrics, isLoading, error } = useLeela();
  const averageMetrics = getAverageShockMetrics();
  
  // Map shock metrics to a display format
  const metricsDisplay = [
    { name: 'Novelty', value: averageMetrics.novelty_score },
    { name: 'Contradiction', value: averageMetrics.contradiction_score },
    { name: 'Impossibility', value: averageMetrics.impossibility_score },
    { name: 'Utility', value: averageMetrics.utility_potential },
  ];

  const phases = ['Create', 'Reflect', 'Abstract', 'Evolve', 'Transcend', 'Return'];
  const currentPhaseIndex = phases.indexOf(creativeState.phase);

  // Format framework names for display
  const formattedFrameworks = creativeState.activeShockFrameworks.map(framework => {
    return framework
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  });

  return (
    <div className="card">
      <h3 className="text-xl font-heading mb-4 flex items-center">
        <CubeTransparentIcon className="w-5 h-5 mr-2 text-highlight" />
        Creative State
      </h3>
      
      {isLoading ? (
        <div className="py-8 text-center text-gray-400">
          <svg className="animate-spin h-6 w-6 text-highlight mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Loading creative state data...</p>
        </div>
      ) : error ? (
        <div className="py-6 text-center text-red-400 flex items-center justify-center">
          <ExclamationCircleIcon className="h-5 w-5 mr-2" />
          <p>Error loading data: {error}</p>
        </div>
      ) : (
        <>
          <div className="mb-4">
            <div className="text-sm text-gray-400 mb-2">Meta-Creative Spiral Phase</div>
            <div className="flex items-center space-x-1">
              {phases.map((phase, index) => (
                <React.Fragment key={phase}>
                  <div 
                    className={`h-8 px-2 flex items-center justify-center text-xs font-medium rounded ${
                      index === currentPhaseIndex ? 'bg-highlight text-background-dark' : 'bg-background-dark text-gray-400'
                    }`}
                  >
                    {phase}
                  </div>
                  {index < phases.length - 1 && (
                    <div className={`h-0.5 w-4 ${
                      index < currentPhaseIndex ? 'bg-highlight' : 'bg-gray-700'
                    }`}></div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
          
          <div className="mb-4">
            <div className="text-sm text-gray-400 mb-2">Emergence Indicators</div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-2">
              {metricsDisplay.map((metric) => (
                <div key={metric.name} className="flex flex-col">
                  <div className="flex justify-between text-xs">
                    <span>{metric.name}</span>
                    <span className="font-mono">{metric.value.toFixed(2)}</span>
                  </div>
                  <div className="h-1.5 bg-background-dark mt-1 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-gradient-to-r from-primary to-highlight rounded-full"
                      style={{ width: `${metric.value * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div>
            <div className="text-sm text-gray-400 mb-2">Active Shock Frameworks</div>
            <div className="flex flex-wrap gap-2">
              {formattedFrameworks.map((framework) => (
                <div key={framework} className="badge-highlight">
                  {framework}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default CreativeStatePanel;