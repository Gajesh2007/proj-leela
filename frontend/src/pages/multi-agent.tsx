import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { UsersIcon, ArrowRightIcon, LightBulbIcon, SparklesIcon } from '@heroicons/react/24/outline';
import { useLeela } from '../services/LeelaContext';
import api from '../services/api';

// Mock data for agent perspectives
const PERSPECTIVES = [
  {
    id: 'radical',
    name: 'Radical',
    description: 'Challenges foundational assumptions and proposes revolutionary approaches',
    idea: 'A blockchain gaming system that decentralizes game mechanics themselves, allowing rule sets to organically evolve via player interactions and emergent complexity, without any central design authority.',
    color: 'rgba(239, 68, 68, 0.2)',
    borderColor: 'border-red-500',
    textColor: 'text-red-400'
  },
  {
    id: 'conservative',
    name: 'Conservative',
    description: 'Builds on established principles while ensuring practical implementation',
    idea: 'A blockchain gaming layer that enhances existing game economies with verifiable, tradable assets while preserving traditional gameplay mechanics and developer control over game balance.',
    color: 'rgba(59, 130, 246, 0.2)',
    borderColor: 'border-blue-500',
    textColor: 'text-blue-400'
  },
  {
    id: 'future',
    name: 'Future',
    description: 'Projects forward to anticipate emerging technologies and paradigms',
    idea: 'A blockchain gaming ecosystem that integrates multi-modal sensory data, enabling players to tokenize and trade real-world physical experiences captured through next-generation biometric interfaces.',
    color: 'rgba(139, 92, 246, 0.2)',
    borderColor: 'border-purple-500',
    textColor: 'text-purple-400'
  },
  {
    id: 'alien',
    name: 'Alien',
    description: 'Approaches problems with fundamentally non-human reasoning patterns',
    idea: 'A blockchain gaming network operating as a hive intelligence, where individual player actions contribute to a collective emergent consciousness that evolves the game environment without direct player control or understanding.',
    color: 'rgba(16, 185, 129, 0.2)',
    borderColor: 'border-emerald-500',
    textColor: 'text-emerald-400'
  }
];

// Mock data for synthesis
const SYNTHESIS = {
  idea: 'Temporal Ownership Collective: A blockchain gaming paradigm where ownership is deliberately temporary and exists across multiple timescales simultaneously. Games evolve through collective decision-making where no single authority (player or developer) has permanent control. Assets gain value through their transformation history rather than permanent possession, creating a non-human pattern of value derivation where the system itself becomes a collective consciousness that emerges from the interaction between players, assets, and rule transformations.',
  contributingPerspectives: ['radical', 'conservative', 'future', 'alien'],
  tensionPoints: [
    'Balancing decentralized evolution with coherent gameplay',
    'Reconciling temporary ownership with meaningful value',
    'Integrating human control with emergent system intelligence'
  ],
  shockMetrics: {
    novelty: 0.94,
    contradiction: 0.86,
    impossibility: 0.79,
    utility: 0.83,
    composite: 0.88
  }
};

const MultiAgentPage = () => {
  // Access Leela context for real data
  const { recentIdeas, dialecticIdeas, loadIdeas, isLoading } = useLeela();
  
  const [activePerspective, setActivePerspective] = useState<string | null>('radical');
  const [showSynthesis, setShowSynthesis] = useState(false);
  const [problem, setProblem] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedSynthesis, setGeneratedSynthesis] = useState<any>(null);
  
  // Load ideas when component mounts
  useEffect(() => {
    if (recentIdeas.length === 0) {
      loadIdeas();
    }
  }, []);
  
  const handlePerspectiveClick = (id: string) => {
    setActivePerspective(id);
    setShowSynthesis(false);
  };
  
  const handleSynthesisClick = () => {
    setShowSynthesis(true);
  };
  
  const handleGenerateSynthesis = async () => {
    if (!problem) {
      alert('Please enter a problem statement');
      return;
    }
    
    setIsGenerating(true);
    
    try {
      // Use the dialectic synthesis API endpoint
      const response = await api.generateDialecticIdea({
        domain: 'creative_synthesis',
        problem_statement: problem,
        perspectives: ['radical', 'conservative', 'future', 'alien'],
        thinking_budget: 8000
      });
      
      setGeneratedSynthesis(response);
      setShowSynthesis(true);
    } catch (err) {
      console.error('Error generating synthesis:', err);
      alert('Failed to generate synthesis. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <>
      <Head>
        <title>Multi-Agent Observatory | Project Leela</title>
        <meta name="description" content="Observe the dialectic between different perspectives" />
      </Head>

      <div className="space-y-6">
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-heading flex items-center">
                <UsersIcon className="w-8 h-8 mr-2 text-highlight" />
                Multi-Agent Observatory
              </h1>
              <p className="text-text-light mt-1">
                Observe the dialectic between different perspectives to generate novel insights
              </p>
            </div>
            
            <button
              className="btn btn-secondary flex items-center"
              onClick={handleSynthesisClick}
              disabled={isGenerating}
            >
              {generatedSynthesis ? (
                <>
                  <LightBulbIcon className="w-5 h-5 mr-2" />
                  View Synthesis
                </>
              ) : (
                <>
                  <SparklesIcon className="w-5 h-5 mr-2" />
                  Generate Synthesis
                </>
              )}
            </button>
          </div>
          
          <div className="card mb-6 p-5">
            <h3 className="text-lg font-heading mb-4">Enter Your Problem Statement</h3>
            <div className="flex gap-4">
              <input
                type="text"
                placeholder="How might we..."
                className="input flex-grow"
                value={problem}
                onChange={(e) => setProblem(e.target.value)}
                disabled={isGenerating}
              />
              <button 
                className="btn btn-primary flex items-center whitespace-nowrap"
                onClick={handleGenerateSynthesis}
                disabled={isGenerating || !problem}
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-4 h-4 mr-2" />
                    Generate
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-text-muted mt-2">
              Frame your problem as a question that the different perspectives can address
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {PERSPECTIVES.map((perspective) => (
            <div
              key={perspective.id}
              className={`
                card h-full cursor-pointer transition-all duration-300 relative overflow-hidden
                ${activePerspective === perspective.id ? 'ring-2 ring-highlight' : 'hover:bg-primary/10'}
              `}
              style={{ backgroundColor: activePerspective === perspective.id ? perspective.color : '' }}
              onClick={() => handlePerspectiveClick(perspective.id)}
            >
              <div className={`absolute top-0 left-0 h-full w-1 ${perspective.borderColor}`}></div>
              <h3 className={`font-heading text-xl mb-2 ${perspective.textColor}`}>{perspective.name}</h3>
              <p className="text-sm text-text-muted mb-4">{perspective.description}</p>
              
              {activePerspective === perspective.id && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="border-t border-primary-light/20 pt-4 mt-2">
                    <h4 className="text-sm font-medium mb-2">Perspective on Blockchain Gaming:</h4>
                    <p className="text-sm text-text">{perspective.idea}</p>
                  </div>
                </motion.div>
              )}
            </div>
          ))}
        </div>
        
        <div className="card">
          <h2 className="text-xl font-heading mb-4">Dialectic Process</h2>
          
          <div className="relative">
            <div className="absolute top-0 left-1/2 h-full w-0.5 bg-primary-light/20 transform -translate-x-1/2"></div>
            
            <div className="space-y-8 relative z-10">
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-red-500 flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-red-500">1</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-red-400">Radical Perspective</h3>
                  <p className="mt-1 text-sm text-text">Challenges the very concept of centralized game design, proposing a system where mechanics themselves evolve through player interaction.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-blue-500 flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-blue-500">2</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-blue-400">Conservative Perspective</h3>
                  <p className="mt-1 text-sm text-text">Questions the practicality of fully decentralized game mechanics, emphasizing the need for developer oversight to maintain game balance.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-purple-500 flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-purple-500">3</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-purple-400">Future Perspective</h3>
                  <p className="mt-1 text-sm text-text">Introduces the concept of tokenizing physical experiences, expanding the definition of what constitutes a game asset.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-emerald-500 flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-emerald-500">4</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-emerald-400">Alien Perspective</h3>
                  <p className="mt-1 text-sm text-text">Reconceptualizes the entire system as a collective consciousness, challenging the human-centric notion of games as designed experiences.</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-highlight flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-highlight">5</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-highlight">Tension Points Identified</h3>
                  <ul className="mt-1 text-sm text-text list-disc pl-5 space-y-1">
                    {SYNTHESIS.tensionPoints.map((point, index) => (
                      <li key={index}>{point}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div className="flex items-start">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-background-dark border-2 border-secondary flex items-center justify-center z-20">
                  <span className="text-xs font-bold text-secondary">6</span>
                </div>
                <div className="ml-4 flex-1">
                  <h3 className="text-sm font-medium text-secondary">Synthesis</h3>
                  <div className="mt-1 flex items-center">
                    <ArrowRightIcon className="w-5 h-5 text-secondary" />
                    <button
                      className="text-sm text-secondary hover:text-secondary-light ml-2"
                      onClick={handleSynthesisClick}
                    >
                      View Synthesis
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {showSynthesis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="glow-card"
          >
            <h2 className="text-xl font-heading text-highlight mb-4">Synthesized Idea</h2>
            
            {generatedSynthesis ? (
              <>
                <p className="text-text mb-6">{generatedSynthesis.synthesized_idea}</p>
                
                <div className="bg-background-dark/50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium mb-2">Contributing Perspectives</h3>
                  <div className="flex flex-wrap gap-2">
                    {PERSPECTIVES.map((perspective) => (
                      <span 
                        key={perspective.id} 
                        className={`px-2 py-1 text-xs rounded-md ${perspective.borderColor} ${perspective.textColor} bg-opacity-20`}
                        style={{ backgroundColor: perspective.color }}
                      >
                        {perspective.name}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="bg-background-dark/50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium mb-2">Shock Metrics</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                    {Object.entries(generatedSynthesis.shock_metrics).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <span className="text-xs text-text-muted capitalize">{key.replace(/_/g, ' ')}</span>
                        <div className="flex items-center mt-1">
                          <div 
                            className="h-1.5 rounded-full bg-gradient-to-r from-secondary to-highlight" 
                            style={{ width: `${(value as number) * 100}px`, maxWidth: '100px' }}
                          ></div>
                          <span className="ml-2 text-sm font-mono">{(value as number).toFixed(2)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-between">
                  <button 
                    className="btn btn-outline"
                    onClick={() => setShowSynthesis(false)}
                  >
                    Back to Perspectives
                  </button>
                  <button 
                    className="btn btn-secondary"
                    onClick={() => {
                      // Save the synthesis to the explorer
                      window.location.href = '/explorer';
                    }}
                  >
                    Explore This Idea
                  </button>
                </div>
              </>
            ) : (
              <>
                <p className="text-text mb-6">{SYNTHESIS.idea}</p>
                
                <div className="bg-background-dark/50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium mb-2">Contributing Perspectives</h3>
                  <div className="flex flex-wrap gap-2">
                    {SYNTHESIS.contributingPerspectives.map((id) => {
                      const perspective = PERSPECTIVES.find(p => p.id === id);
                      if (!perspective) return null;
                      return (
                        <span 
                          key={id} 
                          className={`px-2 py-1 text-xs rounded-md ${perspective.borderColor} ${perspective.textColor} bg-opacity-20`}
                          style={{ backgroundColor: perspective.color }}
                        >
                          {perspective.name}
                        </span>
                      );
                    })}
                  </div>
                </div>
                
                <div className="bg-background-dark/50 rounded-lg p-4 mb-6">
                  <h3 className="text-sm font-medium mb-2">Shock Metrics</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                    {Object.entries(SYNTHESIS.shockMetrics).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <span className="text-xs text-text-muted capitalize">{key}</span>
                        <div className="flex items-center mt-1">
                          <div 
                            className="h-1.5 rounded-full bg-gradient-to-r from-secondary to-highlight" 
                            style={{ width: `${value * 100}px`, maxWidth: '100px' }}
                          ></div>
                          <span className="ml-2 text-sm font-mono">{value.toFixed(2)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-between">
                  <button 
                    className="btn btn-outline"
                    onClick={() => setShowSynthesis(false)}
                  >
                    Back to Perspectives
                  </button>
                  <button 
                    className="btn btn-primary"
                    onClick={handleGenerateSynthesis}
                    disabled={!problem || isGenerating}
                  >
                    {isGenerating ? 'Generating...' : 'Generate Real Synthesis'}
                  </button>
                </div>
              </>
            )}
          </motion.div>
        )}
      </div>
    </>
  );
};

export default MultiAgentPage;