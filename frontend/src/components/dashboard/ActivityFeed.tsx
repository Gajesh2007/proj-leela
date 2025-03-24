import React, { useEffect, useState } from 'react';
import { 
  SparklesIcon, 
  ArrowPathIcon, 
  BoltIcon,
  BeakerIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { useLeela } from '../../services/LeelaContext';

// Helper function to get the icon based on workflow
const getWorkflowIcon = (workflow: string) => {
  const icons: Record<string, any> = {
    'disruptor': { icon: BoltIcon, color: 'text-yellow-400', bgColor: 'bg-yellow-400/10' },
    'connector': { icon: ArrowPathIcon, color: 'text-blue-400', bgColor: 'bg-blue-400/10' },
    'dialectic': { icon: ArrowPathIcon, color: 'text-green-400', bgColor: 'bg-green-400/10' },
    'dialectic_synthesis': { icon: ArrowPathIcon, color: 'text-green-400', bgColor: 'bg-green-400/10' },
    'meta-synthesis': { icon: BeakerIcon, color: 'text-purple-400', bgColor: 'bg-purple-400/10' },
    'impossibility_enforcer': { icon: BoltIcon, color: 'text-red-400', bgColor: 'bg-red-400/10' },
    'cognitive_dissonance_amplifier': { icon: SparklesIcon, color: 'text-purple-400', bgColor: 'bg-purple-400/10' },
  };
  
  return icons[workflow.toLowerCase()] || { icon: BoltIcon, color: 'text-gray-400', bgColor: 'bg-gray-400/10' };
};

const ActivityFeed = () => {
  const { recentIdeas, dialecticIdeas, isLoading, error } = useLeela();
  
  // Combine ideas and format them for the activity feed
  const getActivityItems = () => {
    const activities = [];
    
    // Add regular ideas
    recentIdeas.forEach(idea => {
      const iconConfig = getWorkflowIcon(idea.framework);
      activities.push({
        id: idea.id,
        type: 'generation',
        workflow: idea.framework,
        domain: idea.idea.split(' ').slice(0, 3).join(' ') + '...', // Use first few words as domain
        timestamp: 'Recent',
        icon: iconConfig.icon,
        iconColor: iconConfig.color,
        bgColor: iconConfig.bgColor
      });
    });
    
    // Add dialectic ideas
    dialecticIdeas.forEach(idea => {
      const iconConfig = getWorkflowIcon('dialectic_synthesis');
      activities.push({
        id: idea.id,
        type: 'synthesis',
        workflow: 'Dialectic Synthesis',
        domain: idea.synthesized_idea.split(' ').slice(0, 3).join(' ') + '...', // Use first few words as domain
        timestamp: 'Recent',
        icon: iconConfig.icon,
        iconColor: iconConfig.color,
        bgColor: iconConfig.bgColor
      });
    });
    
    // Sort by most recent (assuming newer ideas have higher IDs)
    return activities.sort((a, b) => b.id.localeCompare(a.id)).slice(0, 5);
  };
  
  const activities = getActivityItems();
  
  return (
    <div className="card">
      <h3 className="text-xl font-heading mb-4 flex items-center">
        <SparklesIcon className="w-5 h-5 mr-2 text-highlight" />
        Recent Activity
      </h3>
      
      {isLoading ? (
        <div className="py-8 text-center text-gray-400">
          <svg className="animate-spin h-6 w-6 text-highlight mx-auto mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p>Loading activity data...</p>
        </div>
      ) : error ? (
        <div className="py-6 text-center text-red-400 flex items-center justify-center">
          <ExclamationCircleIcon className="h-5 w-5 mr-2" />
          <p>Error loading data: {error}</p>
        </div>
      ) : activities.length === 0 ? (
        <div className="py-8 text-center text-gray-400">
          <p>No activity recorded yet</p>
          <p className="text-sm mt-2">Generate your first idea to see activity here</p>
        </div>
      ) : (
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className={`${activity.bgColor} p-2 rounded-lg mt-0.5`}>
                <activity.icon className={`h-4 w-4 ${activity.iconColor}`} />
              </div>
              
              <div>
                <div className="text-sm font-medium flex items-center">
                  <span>{activity.type === 'generation' ? 'Generated new idea' : activity.type === 'synthesis' ? 'Synthesized perspectives' : 'Meta-synthesized approach'}</span>
                  <span className="mx-1.5 text-gray-500">&middot;</span>
                  <span className="text-gray-400 text-xs">{activity.timestamp}</span>
                </div>
                
                <div className="text-xs text-gray-400 mt-0.5 flex space-x-2">
                  <span className="badge-primary">{activity.workflow}</span>
                  <span className="badge-accent">{activity.domain}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {activities.length > 0 && (
        <div className="mt-4 pt-4 border-t border-primary-light/10">
          <button className="text-xs text-primary-light hover:text-highlight transition-colors">
            View all activity
          </button>
        </div>
      )}
    </div>
  );
};

export default ActivityFeed;