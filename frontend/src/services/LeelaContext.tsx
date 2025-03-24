import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import api, { 
  CreativeIdeaResponse, 
  DialecticIdeaResponse, 
  Framework, 
  DomainData,
  ShockProfile
} from './api';

interface LeelaContextType {
  // API States
  isLoading: boolean;
  error: string | null;
  
  // Data States
  frameworks: Framework[];
  domains: DomainData;
  recentIdeas: CreativeIdeaResponse[];
  dialecticIdeas: DialecticIdeaResponse[];
  
  // Creative State
  creativeState: {
    phase: string;
    activeShockFrameworks: string[];
    emergenceIndicators: Record<string, number>;
  };
  
  // Metrics
  systemMetrics: {
    ideasGenerated: number;
    averageShockValue: number;
    successfulShocks: number;
    creativeProcesses: number;
  };
  
  // Methods
  loadFrameworks: () => Promise<void>;
  loadDomains: () => Promise<void>;
  loadIdeas: () => Promise<void>;
  addCreativeIdea: (idea: CreativeIdeaResponse) => void;
  addDialecticIdea: (idea: DialecticIdeaResponse) => void;
  getAverageShockMetrics: () => ShockProfile;
}

const defaultCreativeState = {
  phase: 'Create',
  activeShockFrameworks: ['impossibility_enforcer', 'cognitive_dissonance_amplifier'],
  emergenceIndicators: {
    'novelty': 0.75,
    'surprise': 0.82,
    'utility': 0.65,
    'paradox': 0.79
  }
};

const defaultSystemMetrics = {
  ideasGenerated: 32,
  averageShockValue: 0.74,
  successfulShocks: 28,
  creativeProcesses: 12
};

const LeelaContext = createContext<LeelaContextType | undefined>(undefined);

export function LeelaProvider({ children }: { children: ReactNode }) {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [domains, setDomains] = useState<DomainData>({});
  const [recentIdeas, setRecentIdeas] = useState<CreativeIdeaResponse[]>([]);
  const [dialecticIdeas, setDialecticIdeas] = useState<DialecticIdeaResponse[]>([]);
  
  const [creativeState, setCreativeState] = useState(defaultCreativeState);
  const [systemMetrics, setSystemMetrics] = useState(defaultSystemMetrics);

  // Load initial data on mount
  useEffect(() => {
    loadFrameworks();
    loadDomains();
    loadIdeas();
  }, []);

  // Load frameworks
  const loadFrameworks = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.getFrameworks();
      setFrameworks(response.frameworks);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load frameworks');
      console.error('Failed to load frameworks:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load domains
  const loadDomains = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await api.getDomains();
      setDomains(response.domains);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load domains');
      console.error('Failed to load domains:', err);
    } finally {
      setIsLoading(false);
    }
  };
  
  // Load ideas
  const loadIdeas = async () => {
    setIsLoading(true);
    setError(null);
    
    console.log('Frontend: Loading ideas...');
    
    try {
      const response = await api.getAllIdeas();
      console.log('Frontend: Ideas loaded successfully:', response.ideas.length);
      console.log('Frontend: First few ideas:', response.ideas.slice(0, 2));
      
      setRecentIdeas(response.ideas);
      
      // Update metrics after loading ideas
      if (response.ideas.length > 0) {
        setSystemMetrics(prev => ({
          ...prev,
          ideasGenerated: response.ideas.length,
          successfulShocks: response.ideas.filter(
            idea => idea.shock_metrics.composite_shock_value > 0.6
          ).length
        }));
        console.log('Frontend: Metrics updated with loaded ideas');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load ideas';
      setError(errorMessage);
      console.error('Frontend: Failed to load ideas:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Add creative idea
  const addCreativeIdea = (idea: CreativeIdeaResponse) => {
    setRecentIdeas(prevIdeas => [idea, ...prevIdeas]);
    
    // Update metrics
    setSystemMetrics(prev => ({
      ...prev,
      ideasGenerated: prev.ideasGenerated + 1,
      successfulShocks: idea.shock_metrics.composite_shock_value > 0.6 ? prev.successfulShocks + 1 : prev.successfulShocks
    }));
  };

  // Add dialectic idea
  const addDialecticIdea = (idea: DialecticIdeaResponse) => {
    setDialecticIdeas(prevIdeas => [idea, ...prevIdeas]);
    
    // Update metrics
    setSystemMetrics(prev => ({
      ...prev,
      ideasGenerated: prev.ideasGenerated + 1,
      successfulShocks: idea.shock_metrics.composite_shock_value > 0.6 ? prev.successfulShocks + 1 : prev.successfulShocks
    }));
  };

  // Get average shock metrics
  const getAverageShockMetrics = (): ShockProfile => {
    if (recentIdeas.length === 0) {
      return {
        novelty_score: 0,
        contradiction_score: 0,
        impossibility_score: 0,
        utility_potential: 0,
        expert_rejection_probability: 0,
        composite_shock_value: 0
      };
    }

    const total = recentIdeas.reduce(
      (acc, idea) => {
        return {
          novelty_score: acc.novelty_score + idea.shock_metrics.novelty_score,
          contradiction_score: acc.contradiction_score + idea.shock_metrics.contradiction_score,
          impossibility_score: acc.impossibility_score + idea.shock_metrics.impossibility_score,
          utility_potential: acc.utility_potential + idea.shock_metrics.utility_potential,
          expert_rejection_probability: acc.expert_rejection_probability + idea.shock_metrics.expert_rejection_probability,
          composite_shock_value: acc.composite_shock_value + idea.shock_metrics.composite_shock_value
        };
      },
      {
        novelty_score: 0,
        contradiction_score: 0,
        impossibility_score: 0,
        utility_potential: 0,
        expert_rejection_probability: 0,
        composite_shock_value: 0
      }
    );

    const count = recentIdeas.length;
    return {
      novelty_score: total.novelty_score / count,
      contradiction_score: total.contradiction_score / count,
      impossibility_score: total.impossibility_score / count,
      utility_potential: total.utility_potential / count,
      expert_rejection_probability: total.expert_rejection_probability / count,
      composite_shock_value: total.composite_shock_value / count
    };
  };

  const value = {
    isLoading,
    error,
    frameworks,
    domains,
    recentIdeas,
    dialecticIdeas,
    creativeState,
    systemMetrics,
    loadFrameworks,
    loadDomains,
    loadIdeas,
    addCreativeIdea,
    addDialecticIdea,
    getAverageShockMetrics
  };

  return (
    <LeelaContext.Provider value={value}>
      {children}
    </LeelaContext.Provider>
  );
}

export function useLeela() {
  const context = useContext(LeelaContext);
  if (context === undefined) {
    throw new Error('useLeela must be used within a LeelaProvider');
  }
  return context;
}