import React from 'react';
import Link from 'next/link';
import { LightBulbIcon, ArrowRightIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { useLeela } from '../../services/LeelaContext';

const RecentIdeasPanel = () => {
  const { recentIdeas, dialecticIdeas, isLoading, error } = useLeela();
  
  // Combine and format ideas for display
  const getFormattedIdeas = () => {
    const formattedIdeas = [];
    
    // Format regular ideas
    recentIdeas.forEach(idea => {
      // Extract a title from the idea text (first sentence or first N characters)
      const title = idea.idea.split('.')[0];
      // Extract a domain from the framework (simplified)
      const domain = idea.framework.includes('impossibility') ? 'Physics' : 
                     idea.framework.includes('cognitive') ? 'Conceptual' : 'Cross-Domain';
      
      formattedIdeas.push({
        id: idea.id,
        title: title,
        domain: domain,
        framework: idea.framework
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1))
          .join(' '),
        shockValue: idea.shock_metrics.composite_shock_value,
        snippet: idea.idea.substring(0, 120) + '...'
      });
    });
    
    // Format dialectic ideas
    dialecticIdeas.forEach(idea => {
      formattedIdeas.push({
        id: idea.id,
        title: idea.synthesized_idea.split('.')[0],
        domain: 'Synthesis',
        framework: 'Dialectic Synthesis',
        shockValue: idea.shock_metrics.composite_shock_value,
        snippet: idea.synthesized_idea.substring(0, 120) + '...'
      });
    });
    
    // Sort by shock value (highest first)
    return formattedIdeas
      .sort((a, b) => b.shockValue - a.shockValue)
      .slice(0, 3); // Show only top 3
  };

  const ideas = getFormattedIdeas();

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-heading flex items-center">
          <LightBulbIcon className="w-5 h-5 mr-2 text-highlight" />
          Recent Ideas
        </h3>
        <Link href="/explorer" className="text-xs text-primary-light hover:text-highlight transition-colors flex items-center">
          View all
          <ArrowRightIcon className="w-3 h-3 ml-1" />
        </Link>
      </div>
      
      {isLoading ? (
        <div className="py-8 text-center text-gray-400">
          <svg className="animate-spin h-6 w-6 text-highlight mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Loading idea data...</p>
        </div>
      ) : error ? (
        <div className="py-6 text-center text-red-400 flex items-center justify-center">
          <ExclamationCircleIcon className="h-5 w-5 mr-2" />
          <p>Error loading data: {error}</p>
        </div>
      ) : ideas.length === 0 ? (
        <div className="py-8 text-center text-gray-400">
          <p>No ideas generated yet</p>
          <p className="text-sm mt-2">Generate your first idea to see it here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {ideas.map((idea) => (
            <div key={idea.id} className="bg-background-dark/70 p-4 rounded-lg border border-primary-light/10 hover:border-primary-light/30 transition-all">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{idea.title}</h4>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 rounded-full bg-highlight"></div>
                  <span className="text-xs font-mono text-highlight">{idea.shockValue.toFixed(2)}</span>
                </div>
              </div>
              
              <p className="text-sm text-gray-400 mb-3 line-clamp-2">{idea.snippet}</p>
              
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <span className="badge-accent">{idea.domain}</span>
                  <span className="badge-primary">{idea.framework}</span>
                </div>
                
                <Link href={`/explorer/${idea.id}`} className="text-xs text-primary-light hover:text-highlight">
                  View details
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RecentIdeasPanel;