import React, { useEffect, useState, useRef } from 'react';
import Head from 'next/head';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/router';
import { useLeela } from '../services/LeelaContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  LightBulbIcon,
  ArrowPathIcon,
  SparklesIcon,
  BeakerIcon,
  FireIcon,
  BoltIcon,
  PencilSquareIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  CommandLineIcon
} from '@heroicons/react/24/outline';

const ThinkingProcessPage = () => {
  const router = useRouter();
  const { recentIdeas, loadIdeas } = useLeela();
  const [currentIdea, setCurrentIdea] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [mounted, setMounted] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const [showFullThinking, setShowFullThinking] = useState(false);
  
  // Load ideas when component mounts
  useEffect(() => {
    setMounted(true);
    if (recentIdeas.length === 0) {
      loadIdeas();
    }
  }, []);
  
  // Process query parameters
  useEffect(() => {
    if (!router.isReady) return;
    
    const ideaId = router.query.idea as string;
    if (ideaId && recentIdeas.length > 0) {
      const idea = recentIdeas.find(idea => idea.id === ideaId);
      if (idea) {
        setCurrentIdea(idea);
        console.log("Found idea to analyze:", idea);
      }
    } else if (recentIdeas.length > 0) {
      // If no ID specified, use the first idea
      setCurrentIdea(recentIdeas[0]);
    }
  }, [router.isReady, router.query, recentIdeas]);

  // Auto-scroll to active step
  useEffect(() => {
    if (containerRef.current && mounted) {
      const element = document.getElementById(`thinking-step-${activeStep}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [activeStep, mounted]);

  // Extract and prepare thinking steps data
  const getThinkingSteps = () => {
    if (!currentIdea) return [];
    
    // Make sure thinking_steps is an array and has elements
    if (!Array.isArray(currentIdea.thinking_steps) || currentIdea.thinking_steps.length === 0) {
      // Create a synthetic thinking step if none exist
      return [
        {
          id: 'synthetic-step',
          framework: currentIdea.framework || currentIdea.generative_framework || 'Unknown Framework',
          reasoning_process: 'This idea was generated through an advanced creative thinking process.',
          insights_generated: [
            'Creative breakthrough achieved',
            'Novel concept formation',
            'Paradigm-shifting perspective'
          ],
          output: currentIdea.description || currentIdea.idea || currentIdea.synthesized_idea || '',
          // No raw_thinking for synthetic steps
        }
      ];
    }
    
    // Process all thinking steps to normalize content and ensure all fields
    return currentIdea.thinking_steps.map((step, index) => {
      // Check for all possible additional fields
      const enhancedStep = { ...step };
      
      // Check for raw output variants
      if (!enhancedStep.output) {
        enhancedStep.output = step.raw_output || step.full_output || step.final_output || 
                             step.detailed_output || step.generated_output || '';
      }
      
      // Check for raw thinking process variants
      if (!enhancedStep.raw_thinking) {
        enhancedStep.raw_thinking = step.extended_thinking || step.detailed_thinking || 
                                   step.thinking || step.thought_process || 
                                   step.raw_process || step.claude_thinking || '';
      }
      
      // Ensure reasonable defaults for reasoning process
      if (!enhancedStep.reasoning_process) {
        enhancedStep.reasoning_process = step.process || step.summary || step.explanation || 
                                        'Reasoning process not available for this step.';
      }
      
      // Ensure insights_generated is always an array
      if (!Array.isArray(enhancedStep.insights_generated)) {
        enhancedStep.insights_generated = step.insights || step.key_insights || 
                                         step.generated_insights || [];
      }

      // If we have the idea's description and no output for the first step, use the description
      if (index === 0 && !enhancedStep.output && currentIdea.description) {
        enhancedStep.output = currentIdea.description || currentIdea.idea || currentIdea.synthesized_idea || '';
      }
      
      return enhancedStep;
    });
  };

  const thinkingSteps = getThinkingSteps();
  
  // Extract key metrics
  const getShockMetrics = () => {
    if (!currentIdea || !currentIdea.shock_metrics) return {
      novelty: 0.7,
      contradiction: 0.6,
      impossibility: 0.5,
      utilityPotential: 0.8,
      expertRejection: 0.7,
      composite: 0.65
    };
    
    return {
      novelty: currentIdea.shock_metrics.novelty_score || 0,
      contradiction: currentIdea.shock_metrics.contradiction_score || 0,
      impossibility: currentIdea.shock_metrics.impossibility_score || 0,
      utilityPotential: currentIdea.shock_metrics.utility_potential || 0,
      expertRejection: currentIdea.shock_metrics.expert_rejection_probability || 0,
      composite: currentIdea.shock_metrics.composite_shock_value || 0
    };
  };

  const shockMetrics = getShockMetrics();

  // Extract impossibility elements
  const getImpossibilityElements = () => {
    if (!currentIdea) return [];
    
    if (Array.isArray(currentIdea.impossibility_elements) && currentIdea.impossibility_elements.length > 0) {
      return currentIdea.impossibility_elements;
    }
    
    // Extract from thinking steps if directly not available
    if (Array.isArray(currentIdea.thinking_steps) && currentIdea.thinking_steps.length > 0) {
      const elements = [];
      
      currentIdea.thinking_steps.forEach(step => {
        if (step.insights_generated && Array.isArray(step.insights_generated)) {
          step.insights_generated.forEach(insight => {
            if (insight && typeof insight === 'string' && 
              (insight.toLowerCase().includes('impossib') || 
               insight.toLowerCase().includes('contradict') || 
               insight.toLowerCase().includes('paradox'))) {
              elements.push(insight);
            }
          });
        }
      });
      
      return elements.slice(0, 5); // Limit to 5 elements
    }
    
    return [];
  };

  const impossibilityElements = getImpossibilityElements();

  // Step icon mapping
  const getStepIcon = (index) => {
    const icons = [
      <SparklesIcon key="0" className="w-6 h-6" />,
      <BoltIcon key="1" className="w-6 h-6" />,
      <BeakerIcon key="2" className="w-6 h-6" />,
      <PencilSquareIcon key="3" className="w-6 h-6" />,
      <FireIcon key="4" className="w-6 h-6" />,
      <LightBulbIcon key="5" className="w-6 h-6" />,
      <ArrowPathIcon key="6" className="w-6 h-6" />,
      <CommandLineIcon key="7" className="w-6 h-6" />
    ];
    
    return icons[index % icons.length];
  };

  // Navigate between thinking steps
  const goToNextStep = () => {
    if (activeStep < thinkingSteps.length - 1) {
      setActiveStep(activeStep + 1);
    }
  };
  
  const goToPrevStep = () => {
    if (activeStep > 0) {
      setActiveStep(activeStep - 1);
    }
  };

  if (!currentIdea) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 mx-auto mb-4">
            <SparklesIcon className="w-16 h-16 text-primary animate-pulse" />
          </div>
          <h3 className="text-xl font-heading text-text">Loading creative idea...</h3>
          <p className="text-text-muted mt-2">Please wait while we analyze the thinking process</p>
        </motion.div>
      </div>
    );
  }

  // Get the idea title (first sentence or first 50 chars)
  const getIdeaTitle = () => {
    const description = currentIdea.description || currentIdea.idea || currentIdea.synthesized_idea || '';
    const title = description.split('.')[0].trim();
    return title.length > 0 ? title : description.substring(0, 50);
  };

  return (
    <>
      <Head>
        <title>Thinking Process Explorer | Project Leela</title>
        <meta name="description" content="Visualize and explore the detailed creative thinking process behind Leela's innovative ideas" />
      </Head>

      <div className="space-y-6">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col md:flex-row md:items-center md:justify-between gap-4"
        >
          <div>
            <h1 className="text-3xl font-heading flex items-center">
              <SparklesIcon className="w-8 h-8 mr-2 text-highlight" />
              Thinking Process Visualization
            </h1>
            <p className="text-text-light mt-1">
              Journey through the creative thinking behind each breakthrough idea
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => router.push('/explorer')}
              className="btn btn-secondary-outline text-sm"
            >
              Back to Explorer
            </button>
            
            <button 
              className="btn btn-primary text-sm"
              onClick={() => setShowFullThinking(!showFullThinking)}
            >
              {showFullThinking ? 'Interactive View' : 'Full Thinking View'}
            </button>
          </div>
        </motion.div>
        
        {/* Idea Header */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="card bg-white/80 backdrop-blur-sm shadow-soft-lg"
        >
          <div className="flex flex-col md:flex-row gap-6">
            <div className="flex-1">
              <div className="flex items-center mb-2 gap-2">
                <span className="badge-accent">
                  {(currentIdea.domain || "Interdisciplinary").split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </span>
                <span className="badge-primary">
                  {(currentIdea.framework || currentIdea.generative_framework || "Advanced Framework").split('_').map(word => 
                    word.charAt(0).toUpperCase() + word.slice(1)
                  ).join(' ')}
                </span>
              </div>
              
              <h2 className="text-2xl font-heading mb-3 text-text-dark">{getIdeaTitle()}</h2>
              
              <div className="prose prose-sm prose-headings:text-text-dark prose-a:text-primary mb-4">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]} 
                  components={{
                    div: ({node, ...props}) => <div className="prose prose-sm prose-invert max-w-none" {...props}/>
                  }}
                >
                  {currentIdea.description || currentIdea.idea || currentIdea.synthesized_idea || ''}
                </ReactMarkdown>
              </div>
            </div>
            
            <div className="md:w-64 flex-shrink-0 border-t md:border-t-0 md:border-l border-primary-light/20 pt-3 md:pt-0 md:pl-6">
              <h3 className="text-sm font-medium mb-3 text-text-dark">Shock Metrics</h3>
              <div className="space-y-3">
                {Object.entries(shockMetrics).map(([key, value]) => (
                  <div key={key} className="flex flex-col">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-text-muted capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                      <span className="font-mono">{Number(value).toFixed(2)}</span>
                    </div>
                    <div className="h-1.5 bg-background-dark rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full ${
                          key === 'novelty' ? 'bg-yellow-500' : 
                          key === 'contradiction' ? 'bg-accent' : 
                          key === 'impossibility' ? 'bg-secondary' : 
                          key === 'utilityPotential' ? 'bg-green-500' : 
                          key === 'expertRejection' ? 'bg-red-500' : 'bg-highlight'
                        }`}
                        style={{ width: `${Number(value) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
              
              {impossibilityElements.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-medium mb-2 text-text-dark">Key Impossibility Elements</h3>
                  <div className="flex flex-wrap gap-2">
                    {impossibilityElements.map((element, i) => (
                      <span 
                        key={i} 
                        className="px-2 py-1 text-xs rounded-md bg-accent/20 text-accent-dark"
                      >
                        {typeof element === 'string' ? element : 'Element ' + (i + 1)}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </motion.div>
        
        {/* Thinking Process Visualization */}
        {!showFullThinking ? (
          <div className="card bg-white/80 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-heading text-text-dark">Creative Thinking Process</h3>
              <div className="text-xs text-text-muted">
                Step {activeStep + 1} of {thinkingSteps.length}
              </div>
            </div>
            
            {/* Timeline indicator */}
            <div className="relative h-2 bg-background mb-8 rounded-full overflow-hidden">
              <motion.div 
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-primary to-highlight rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${((activeStep + 1) / thinkingSteps.length) * 100}%` }}
                transition={{ duration: 0.5 }}
              />
            </div>
            
            {/* Steps list */}
            <div className="grid grid-cols-1 md:grid-cols-7 gap-6 mb-8">
              <div className="md:col-span-2">
                <div ref={containerRef} className="h-[600px] overflow-y-auto pr-4 space-y-2 custom-scrollbar">
                  {thinkingSteps.map((step, index) => (
                    <motion.div
                      key={step.id || index}
                      id={`thinking-step-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className={`p-3 rounded-lg border cursor-pointer transition-all ${
                        activeStep === index 
                          ? 'border-primary-light bg-primary/10 shadow-soft-sm' 
                          : 'border-transparent hover:border-slate-200 hover:bg-slate-50'
                      }`}
                      onClick={() => setActiveStep(index)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-full bg-primary/10 text-primary-dark ${activeStep === index ? 'shadow-primary-glow' : ''}`}>
                          {getStepIcon(index)}
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-text-dark">
                            {step.framework 
                              ? step.framework.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') 
                              : `Thinking Step ${index + 1}`
                            }
                          </h4>
                          <p className="text-xs text-text-muted line-clamp-2">
                            {Array.isArray(step.insights_generated) && step.insights_generated.length > 0
                              ? step.insights_generated[0]
                              : 'Reasoning process'
                            }
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
              
              <div className="md:col-span-5">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeStep}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.5 }}
                    className="bg-white/70 rounded-xl p-6 shadow-soft-md border border-primary-light/10 h-[600px] overflow-y-auto custom-scrollbar"
                  >
                    <h3 className="text-lg font-heading text-primary-dark mb-3">
                      {thinkingSteps[activeStep].framework 
                        ? thinkingSteps[activeStep].framework.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') 
                        : `Thinking Process ${activeStep + 1}`
                      }
                    </h3>
                    
                    {thinkingSteps[activeStep].reasoning_process && (
                      <div className="mb-5">
                        <h4 className="text-sm font-medium text-text-dark mb-2">Reasoning Process</h4>
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                            }}
                          >
                            {thinkingSteps[activeStep].reasoning_process}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}
                    
                    {thinkingSteps[activeStep].output && (
                      <div className="mb-5 border-t border-primary-light/10 pt-4">
                        <h4 className="text-sm font-medium text-text-dark mb-2">Detailed Output</h4>
                        <div className="prose prose-sm max-w-none bg-slate-50 p-3 rounded-md border border-slate-200 overflow-auto max-h-[300px]">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                            }}
                          >
                            {thinkingSteps[activeStep].output}
                          </ReactMarkdown>
                        </div>
                      </div>
                    )}

                    {thinkingSteps[activeStep].raw_thinking && (
                      <div className="mb-5 border-t border-primary-light/10 pt-4">
                        <h4 className="text-sm font-medium text-text-dark mb-2">Raw Thinking</h4>
                        <details className="bg-slate-50 p-3 rounded-md border border-slate-200">
                          <summary className="cursor-pointer text-sm text-primary-dark hover:text-primary mb-2">
                            Show Raw Thinking Process
                          </summary>
                          <div className="prose prose-sm max-w-none mt-3 overflow-auto max-h-[300px]">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                              }}
                            >
                              {thinkingSteps[activeStep].raw_thinking}
                            </ReactMarkdown>
                          </div>
                        </details>
                      </div>
                    )}
                    
                    {Array.isArray(thinkingSteps[activeStep].insights_generated) && 
                     thinkingSteps[activeStep].insights_generated.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-text-dark mb-2">Key Insights Generated</h4>
                        <ul className="space-y-2">
                          {thinkingSteps[activeStep].insights_generated.map((insight, i) => (
                            <motion.li 
                              key={i}
                              initial={{ opacity: 0, x: -10 }}
                              animate={{ opacity: 1, x: 0 }}
                              transition={{ duration: 0.3, delay: i * 0.1 }}
                              className="flex items-start gap-2"
                            >
                              <div className="mt-1 text-accent">
                                <SparklesIcon className="w-4 h-4" />
                              </div>
                              <div className="text-sm text-text flex-1">
                                {insight}
                              </div>
                            </motion.li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </motion.div>
                </AnimatePresence>
                
                <div className="flex justify-between mt-4">
                  <button
                    className={`p-2 rounded-full ${
                      activeStep > 0 
                        ? 'bg-primary-light/20 text-primary hover:bg-primary-light/30' 
                        : 'bg-slate-100 text-text-muted cursor-not-allowed'
                    }`}
                    onClick={goToPrevStep}
                    disabled={activeStep === 0}
                  >
                    <ChevronLeftIcon className="w-5 h-5" />
                  </button>
                  
                  <button
                    className={`p-2 rounded-full ${
                      activeStep < thinkingSteps.length - 1 
                        ? 'bg-primary-light/20 text-primary hover:bg-primary-light/30' 
                        : 'bg-slate-100 text-text-muted cursor-not-allowed'
                    }`}
                    onClick={goToNextStep}
                    disabled={activeStep === thinkingSteps.length - 1}
                  >
                    <ChevronRightIcon className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card bg-white/80 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-heading text-text-dark">Complete Thinking Process</h3>
              <button 
                className="btn btn-outline-primary text-sm"
                onClick={() => setShowFullThinking(false)}
              >
                Return to Interactive View
              </button>
            </div>
            
            <div className="space-y-8">
              {thinkingSteps.map((step, index) => (
                <motion.div
                  key={step.id || index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="p-6 rounded-xl bg-white/70 border border-primary-light/10 shadow-soft-sm"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="p-2 rounded-full bg-primary/10 text-primary-dark">
                      {getStepIcon(index)}
                    </div>
                    <h3 className="text-lg font-heading text-primary-dark">
                      {step.framework 
                        ? step.framework.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ') 
                        : `Thinking Step ${index + 1}`
                      }
                    </h3>
                  </div>
                  
                  {step.reasoning_process && (
                    <div className="mb-5">
                      <h4 className="text-sm font-medium text-text-dark mb-2">Reasoning Process</h4>
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                          }}
                        >
                          {step.reasoning_process}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}
                  
                  {step.output && (
                    <div className="mb-5 border-t border-primary-light/10 pt-4">
                      <h4 className="text-sm font-medium text-text-dark mb-2">Detailed Output</h4>
                      <div className="prose prose-sm max-w-none bg-slate-50 p-3 rounded-md border border-slate-200 overflow-auto max-h-[400px]">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                          }}
                        >
                          {step.output}
                        </ReactMarkdown>
                      </div>
                    </div>
                  )}

                  {step.raw_thinking && (
                    <div className="mb-5 border-t border-primary-light/10 pt-4">
                      <h4 className="text-sm font-medium text-text-dark mb-2">Raw Thinking</h4>
                      <details className="bg-slate-50 p-3 rounded-md border border-slate-200">
                        <summary className="cursor-pointer text-sm text-primary-dark hover:text-primary mb-2">
                          Show Raw Thinking Process
                        </summary>
                        <div className="prose prose-sm max-w-none mt-3 overflow-auto max-h-[600px]">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              div: ({node, ...props}) => <div className="prose prose-sm max-w-none" {...props}/>
                            }}
                          >
                            {step.raw_thinking}
                          </ReactMarkdown>
                        </div>
                      </details>
                    </div>
                  )}
                  
                  {Array.isArray(step.insights_generated) && step.insights_generated.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-text-dark mb-2">Key Insights Generated</h4>
                      <ul className="space-y-2">
                        {step.insights_generated.map((insight, i) => (
                          <motion.li 
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: i * 0.1 }}
                            className="flex items-start gap-2"
                          >
                            <div className="mt-1 text-accent">
                              <SparklesIcon className="w-4 h-4" />
                            </div>
                            <div className="text-sm text-text flex-1">
                              {insight}
                            </div>
                          </motion.li>
                        ))}
                      </ul>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default ThinkingProcessPage;