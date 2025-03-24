import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  BoltIcon, 
  ArrowPathIcon, 
  UsersIcon, 
  ClockIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';
import api, { CreativeIdeaResponse, Framework, DomainData } from '@/services/api';
import { useLeela } from '@/services/LeelaContext';

// Default domains and workflows while loading from API
const DEFAULT_DOMAINS = [
  { id: 'physics', name: 'Physics', description: 'Fundamental laws and properties of matter and energy' },
  { id: 'biology', name: 'Biology', description: 'Living organisms and their vital processes' },
  { id: 'computer_science', name: 'Computer Science', description: 'Computation, algorithms, and information systems' },
];

// Workflow icons map
const WORKFLOW_ICONS: Record<string, any> = {
  'disruptor': { icon: BoltIcon, color: 'text-yellow-400', bgColor: 'bg-yellow-400/10' },
  'connector': { icon: ArrowPathIcon, color: 'text-blue-400', bgColor: 'bg-blue-400/10' },
  'dialectic': { icon: UsersIcon, color: 'text-green-400', bgColor: 'bg-green-400/10' },
  'temporal': { icon: ClockIcon, color: 'text-purple-400', bgColor: 'bg-purple-400/10' },
  'impossibility_enforcer': { icon: BoltIcon, color: 'text-red-400', bgColor: 'bg-red-400/10' },
  'cognitive_dissonance_amplifier': { icon: SparklesIcon, color: 'text-purple-400', bgColor: 'bg-purple-400/10' },
  'dialectic_synthesis': { icon: UsersIcon, color: 'text-green-400', bgColor: 'bg-green-400/10' },
  'default': { icon: LightBulbIcon, color: 'text-blue-400', bgColor: 'bg-blue-400/10' }
};

const GeneratePage = () => {
  // Get data from Leela context
  const { 
    frameworks, 
    domains, 
    loadFrameworks, 
    loadDomains, 
    addCreativeIdea,
    isLoading: contextLoading,
    error: contextError
  } = useLeela();
  
  // Local state for form
  const [selectedDomain, setSelectedDomain] = useState('');
  const [selectedWorkflow, setSelectedWorkflow] = useState('');
  const [problemStatement, setProblemStatement] = useState('');
  const [shockThreshold, setShockThreshold] = useState(0.7);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedIdea, setGeneratedIdea] = useState<CreativeIdeaResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Format domains for display
  const formattedDomains = Object.keys(domains).map(domainKey => ({
    id: domainKey,
    name: domainKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    description: `Domain with impossibility constraints: ${domains[domainKey].join(', ')}`
  }));
  
  // Format workflows with icons
  const formattedWorkflows = frameworks.map(framework => {
    const iconConfig = WORKFLOW_ICONS[framework.id] || WORKFLOW_ICONS.default;
    return {
      ...framework,
      icon: iconConfig.icon,
      color: iconConfig.color,
      bgColor: iconConfig.bgColor
    };
  });
  
  // Load frameworks and domains on mount if not already loaded
  useEffect(() => {
    if (frameworks.length === 0) {
      loadFrameworks();
    }
    
    if (Object.keys(domains).length === 0) {
      loadDomains();
    }
  }, [frameworks.length, Object.keys(domains).length, loadFrameworks, loadDomains]);
  
  const handleGenerate = async () => {
    if (!selectedDomain || !selectedWorkflow || !problemStatement) {
      alert('Please fill out all required fields');
      return;
    }

    setIsGenerating(true);
    setError(null);
    
    try {
      let response;
      
      // Use different API endpoints based on workflow
      if (selectedWorkflow === 'dialectic_synthesis') {
        // For dialectic workflow
        response = await api.generateDialecticIdea({
          domain: selectedDomain,
          problem_statement: problemStatement,
          perspectives: ['radical', 'conservative', 'futurist'], // Default perspectives
          thinking_budget: 8000
        });
        
        // Transform dialectic response to creative idea format for display
        const transformedResponse = {
          id: response.id,
          idea: response.synthesized_idea,
          framework: 'dialectic_synthesis',
          shock_metrics: response.shock_metrics,
          thinking_steps: response.thinking_steps
        };
        
        setGeneratedIdea(transformedResponse as any);
      } else {
        // For other creative frameworks
        response = await api.generateCreativeIdea({
          domain: selectedDomain,
          problem_statement: problemStatement,
          shock_threshold: shockThreshold,
          creative_framework: selectedWorkflow,
          thinking_budget: 8000
        });
        
        setGeneratedIdea(response);
        
        // Add to context for global state
        addCreativeIdea(response);
      }
    } catch (err) {
      console.error('Error generating idea:', err);
      setError(err instanceof Error ? err.message : 'Failed to generate idea');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <>
      <Head>
        <title>Generate | Project Leela</title>
        <meta name="description" content="Generate shocking, novel ideas with Project Leela" />
      </Head>

      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <h1 className="text-3xl font-heading flex items-center">
            <SparklesIcon className="w-8 h-8 mr-2 text-highlight" />
            Generate New Idea
          </h1>
          <p className="text-text-light mt-2">
            Create genuinely shocking, novel outputs that transcend conventional thinking
          </p>
        </div>

        {!generatedIdea ? (
          <div className="card">
            <h2 className="text-xl font-heading mb-6">Idea Parameters</h2>
            
            <div className="space-y-6">
              {/* Domain Selection */}
              <div>
                <label className="block text-sm font-medium text-text mb-2">Domain</label>
                {contextLoading ? (
                  <div className="p-4 text-center">
                    <span className="text-text-muted">Loading domains...</span>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                    {(formattedDomains.length > 0 ? formattedDomains : DEFAULT_DOMAINS).map((domain) => (
                      <div
                        key={domain.id}
                        className={`
                          cursor-pointer rounded-lg p-3 border-2 transition-all
                          ${selectedDomain === domain.id 
                            ? 'border-highlight bg-highlight/10 shadow-glow-sm' 
                            : 'border-primary-light/20 hover:border-highlight/50 bg-background-light/50'}
                        `}
                        onClick={() => setSelectedDomain(domain.id)}
                      >
                        <div className="font-medium text-text-dark">{domain.name}</div>
                        <div className="text-xs text-text-muted mt-1">{domain.description}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Creative Workflow */}
              <div>
                <label className="block text-sm font-medium text-text mb-2">Creative Workflow</label>
                {contextLoading ? (
                  <div className="p-4 text-center">
                    <span className="text-text-muted">Loading workflows...</span>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {formattedWorkflows.map((workflow) => (
                      <div
                        key={workflow.id}
                        className={`
                          cursor-pointer rounded-lg p-3 border-2 transition-all flex items-center
                          ${selectedWorkflow === workflow.id 
                            ? 'border-highlight bg-highlight/10 shadow-glow-sm' 
                            : 'border-primary-light/20 hover:border-highlight/50 bg-background-light/50'}
                        `}
                        onClick={() => setSelectedWorkflow(workflow.id)}
                      >
                        <div className={`${workflow.bgColor} p-2 rounded-lg mr-3`}>
                          <workflow.icon className={`h-5 w-5 ${workflow.color}`} />
                        </div>
                        <div>
                          <div className="font-medium text-text-dark">{workflow.name}</div>
                          <div className="text-xs text-text-muted mt-0.5">{workflow.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Problem Statement */}
              <div>
                <label htmlFor="problem-statement" className="block text-sm font-medium text-text mb-2">
                  Problem Statement
                </label>
                <textarea
                  id="problem-statement"
                  rows={3}
                  className="input w-full"
                  placeholder="How might we..."
                  value={problemStatement}
                  onChange={(e) => setProblemStatement(e.target.value)}
                />
                <p className="mt-1 text-xs text-text-muted">
                  Frame your problem as a "How might we..." question for best results
                </p>
              </div>
              
              {/* Shock Threshold */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <label htmlFor="shock-threshold" className="block text-sm font-medium text-text">
                    Shock Threshold
                  </label>
                  <span className="text-sm font-mono text-highlight">{shockThreshold.toFixed(2)}</span>
                </div>
                <input
                  id="shock-threshold"
                  type="range"
                  min="0.1"
                  max="1"
                  step="0.01"
                  value={shockThreshold}
                  onChange={(e) => setShockThreshold(parseFloat(e.target.value))}
                  className="w-full h-2 bg-background-dark rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-text-muted mt-1">
                  <span>Conventional</span>
                  <span>Balanced</span>
                  <span>Shocking</span>
                </div>
              </div>
              
              {/* Error Message */}
              {error && (
                <div className="rounded-md bg-red-900/30 border border-red-500 p-3 mb-2">
                  <p className="text-sm text-red-300">{error}</p>
                </div>
              )}
              
              {contextError && (
                <div className="rounded-md bg-red-900/30 border border-red-500 p-3 mb-2">
                  <p className="text-sm text-red-300">Error loading API data: {contextError}</p>
                </div>
              )}
              
              {/* Generate Button */}
              <div className="pt-4">
                <button
                  type="button"
                  className={`
                    w-full btn bg-gradient-to-r from-secondary to-highlight text-white font-heading py-3 rounded-lg
                    transition-all duration-300 ${isGenerating || contextLoading ? 'opacity-70 cursor-not-allowed' : 'hover:shadow-glow-md'}
                  `}
                  onClick={handleGenerate}
                  disabled={isGenerating || contextLoading}
                >
                  {isGenerating ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <SparklesIcon className="w-5 h-5 mr-2" />
                      Generate
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="space-y-6"
          >
            <div className="glow-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-heading text-highlight">Generated Idea</h2>
                <div className="flex items-center space-x-2">
                  <span className="badge-accent">
                    {Object.keys(domains).includes(selectedDomain) 
                      ? selectedDomain.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                      : selectedDomain}
                  </span>
                  <span className="badge-highlight">
                    {frameworks.find(f => f.id === generatedIdea?.framework)?.name || generatedIdea?.framework}
                  </span>
                </div>
              </div>
              
              <p className="text-text mb-6 leading-relaxed">{generatedIdea?.idea}</p>
              
              <div className="bg-background-dark/50 rounded-lg p-4 mb-6">
                <h3 className="text-sm font-medium mb-2">Shock Metrics</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                  {generatedIdea?.shock_metrics && Object.entries(generatedIdea.shock_metrics).map(([key, value]: [string, any]) => (
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
              
              <div className="flex items-center justify-end space-x-3">
                <button 
                  className="btn btn-outline flex items-center"
                  onClick={() => setGeneratedIdea(null)}
                >
                  <LightBulbIcon className="w-4 h-4 mr-1" />
                  Generate New Idea
                </button>
                <button 
                  className="btn btn-primary flex items-center"
                  onClick={() => window.location.href = "/explorer?highlight=" + generatedIdea?.id}
                >
                  <SparklesIcon className="w-4 h-4 mr-1" />
                  View in Explorer
                </button>
              </div>
            </div>
            
            <div className="card">
              <h3 className="text-xl font-heading mb-4">Thinking Process</h3>
              
              <div className="space-y-6">
                {generatedIdea?.thinking_steps && generatedIdea.thinking_steps.map((step, index) => (
                  <div key={step.id || index} className="border-l-2 border-primary-light pl-4">
                    <h4 className="text-sm font-medium text-text-dark mb-2">Step {index + 1}</h4>
                    <p className="text-sm text-text mb-3 whitespace-pre-wrap">{step.reasoning_process}</p>
                    
                    {step.insights_generated && step.insights_generated.length > 0 && (
                      <div className="bg-background-dark/50 rounded p-3">
                        <h5 className="text-xs font-medium text-text-muted mb-1">Insights</h5>
                        <ul className="list-disc pl-4 text-xs text-text space-y-1">
                          {step.insights_generated.map((insight, i) => (
                            <li key={i}>{insight}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </>
  );
};

export default GeneratePage;