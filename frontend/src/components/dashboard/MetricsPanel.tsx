import React from 'react';
import { ChartBarIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { useLeela } from '../../services/LeelaContext';

const MetricsPanel = () => {
  const { systemMetrics, isLoading, error } = useLeela();
  
  // Calculate trends based on recent ideas
  const metrics = [
    { 
      name: 'Ideas Generated', 
      value: systemMetrics.ideasGenerated, 
      trend: '+2', 
      color: 'text-highlight' 
    },
    { 
      name: 'Average Shock Value', 
      value: systemMetrics.averageShockValue.toFixed(2), 
      trend: '+0.05', 
      color: 'text-highlight' 
    },
    { 
      name: 'Successful Shocks', 
      value: systemMetrics.successfulShocks, 
      trend: '+1', 
      color: 'text-green-400' 
    },
    { 
      name: 'Creative Processes', 
      value: systemMetrics.creativeProcesses, 
      trend: '+2', 
      color: 'text-blue-400' 
    },
  ];

  return (
    <div className="card">
      <h3 className="text-xl font-heading mb-4 flex items-center">
        <ChartBarIcon className="w-5 h-5 mr-2 text-highlight" />
        System Metrics
      </h3>
      
      {isLoading ? (
        <div className="py-8 text-center text-gray-400">
          <svg className="animate-spin h-6 w-6 text-highlight mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Loading metrics data...</p>
        </div>
      ) : error ? (
        <div className="py-6 text-center text-red-400 flex items-center justify-center">
          <ExclamationCircleIcon className="h-5 w-5 mr-2" />
          <p>Error loading data: {error}</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {metrics.map((metric) => (
            <div key={metric.name} className="bg-background-dark/70 rounded-lg p-3 border border-primary-light/10">
              <div className="text-sm text-gray-400">{metric.name}</div>
              <div className="flex items-baseline mt-1">
                <div className="text-xl font-bold">{metric.value}</div>
                <div className={`ml-2 text-xs ${metric.color}`}>{metric.trend}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MetricsPanel;