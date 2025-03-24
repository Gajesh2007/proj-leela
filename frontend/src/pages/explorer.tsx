import React, { useState, useEffect } from 'react';
import Head from 'next/head';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  MagnifyingGlassIcon, 
  ListBulletIcon,
  Squares2X2Icon,
  AdjustmentsHorizontalIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';
import { useLeela } from '../services/LeelaContext';
import api, { CreativeIdeaResponse, DialecticIdeaResponse } from '../services/api';

// Interface for formatted idea display
interface FormattedIdea {
  id: string;
  title: string;
  description: string;
  domain: string;
  framework: string;
  timestamp: string;
  shockMetrics: {
    novelty: number;
    contradiction: number;
    impossibility: number;
    utilityPotential: number;
    expertRejection: number;
    composite: number;
  };
  impossibilityElements: string[];
}

// Format date for display
const formatTimestamp = (date: Date): string => {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  
  if (diffMins < 60) {
    return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
  }
  
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) {
    return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  }
  
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) {
    return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  }
  
  return date.toLocaleDateString();
};

const ExplorerPage = () => {
  const { recentIdeas, dialecticIdeas, domains, frameworks, isLoading, error, loadIdeas } = useLeela();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('all');
  const [selectedFramework, setSelectedFramework] = useState('all');
  const [sortOption, setSortOption] = useState('timestamp');
  const [showFilters, setShowFilters] = useState(false);
  const [expandedIdea, setExpandedIdea] = useState<string | null>(null);
  const [formattedIdeas, setFormattedIdeas] = useState<FormattedIdea[]>([]);
  
  // Refresh ideas data
  // Highlight idea from URL parameter (when redirected from generate page)
  useEffect(() => {
    loadIdeas();
    
    // Check for highlight parameter in URL
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const highlightedIdeaId = urlParams.get('highlight');
      
      if (highlightedIdeaId) {
        // Set the highlighted idea as expanded
        setExpandedIdea(highlightedIdeaId);
        
        // Scroll to the highlighted idea after a short delay to ensure it's rendered
        setTimeout(() => {
          const element = document.getElementById(`idea-${highlightedIdeaId}`);
          if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Add a temporary highlight effect
            element.classList.add('highlight-pulse');
            setTimeout(() => {
              element.classList.remove('highlight-pulse');
            }, 3000);
          }
        }, 500);
      }
    }
  }, []);
  
  // Format ideas from the API responses
  useEffect(() => {
    const formatIdeas = () => {
      const formatted: FormattedIdea[] = [];
      
      console.log(`Explorer: Formatting ${recentIdeas.length} ideas for display`);
      console.log("Explorer: Example idea:", recentIdeas[0]);
      
      // Format regular ideas
      recentIdeas.forEach((idea, index) => {
        // Validate the idea has all required properties before processing it
        if (!idea || !idea.id || !idea.description || !idea.framework || !idea.shock_metrics) {
          console.warn(`Explorer: Skipping invalid idea at index ${index}:`, idea);
          return;
        }
        
        // Extract a title from the idea text (first sentence or first 50 characters)
        const title = idea.description.split('.')[0].trim();
        
        // Direct domain extraction from API if available
        let domain = 'cross_domain';
        
        // Check if the domain is already provided in the idea itself
        if (idea.domain) {
          domain = idea.domain.toLowerCase().replace(/\s+/g, '_');
        } else {
          // Extract domain from description content using content analysis
          const description = idea.description.toLowerCase();
          
          // Define domain keywords and categories for better matching
          const domainKeywords: Record<string, string[]> = {
            'physics': ['physics', 'quantum', 'energy', 'particles', 'gravity', 'spacetime', 'relativity', 'mechanics'],
            'biology': ['biology', 'dna', 'cells', 'organism', 'evolution', 'genes', 'protein', 'ecology'],
            'computer_science': ['algorithm', 'software', 'hardware', 'data', 'network', 'programming', 'computation', 'ai', 'machine learning'],
            'cognitive_science': ['cognition', 'consciousness', 'cognitive', 'brain', 'mind', 'neural', 'perception', 'psychology'],
            'philosophy': ['philosophy', 'ethics', 'metaphysics', 'epistemology', 'ontology', 'existential', 'dialectic'],
            'economics': ['economics', 'market', 'finance', 'economy', 'trade', 'currency', 'value', 'capital'],
            'art': ['art', 'aesthetic', 'design', 'visual', 'creative', 'expression', 'medium', 'sculpture', 'painting'],
            'mathematics': ['mathematics', 'math', 'theorem', 'proof', 'equation', 'geometry', 'algebra', 'calculus'],
            'medicine': ['medicine', 'medical', 'treatment', 'healthcare', 'therapy', 'disease', 'diagnosis', 'clinical'],
            'astronomy': ['astronomy', 'cosmos', 'stars', 'planets', 'galaxy', 'universe', 'celestial', 'solar']
          };
          
          // Check for keywords in the description
          let maxMatches = 0;
          let bestDomain = 'cross_domain';
          
          for (const [domainName, keywords] of Object.entries(domainKeywords)) {
            const matches = keywords.filter(keyword => description.includes(keyword)).length;
            if (matches > maxMatches) {
              maxMatches = matches;
              bestDomain = domainName;
            }
          }
          
          // Only use the detected domain if we have at least 2 keyword matches
          if (maxMatches >= 2) {
            domain = bestDomain;
          } else {
            // Fallback to framework-based mapping if content analysis didn't yield results
            const domainMapping: Record<string, string> = {
              'impossibility_enforcer': 'physics',
              'cognitive_dissonance_amplifier': 'cognitive_science',
              'disruptor': 'computer_science',
              'dialectic_synthesis': 'philosophy',
            };
            
            const framework = idea.framework || idea.generative_framework;
            domain = domainMapping[framework] || 'cross_domain';
          }
        }
        
        // Extract impossibility elements and key innovation points
        const impossibilityElements: string[] = [];
        
        // First try to extract from thinking steps if available
        if (idea.thinking_steps && idea.thinking_steps.length > 0) {
          // Extract elements from insights
          idea.thinking_steps.forEach(step => {
            if (step.insights_generated && Array.isArray(step.insights_generated)) {
              step.insights_generated.forEach(insight => {
                if (insight && typeof insight === 'string' && 
                   (insight.toLowerCase().includes('impossib') || 
                    insight.toLowerCase().includes('contradict') || 
                    insight.toLowerCase().includes('paradox') ||
                    insight.toLowerCase().includes('innovation') ||
                    insight.toLowerCase().includes('breakthrough'))) {
                  // Better extraction of the key concept
                  let element;
                  if (insight.includes(':')) {
                    element = insight.split(':').pop()?.trim() || insight;
                  } else if (insight.includes('-')) {
                    element = insight.split('-').pop()?.trim() || insight;
                  } else {
                    element = insight;
                  }
                  
                  // Limit length of the element
                  if (element.length > 40) {
                    element = element.substring(0, 40) + '...';
                  }
                  
                  impossibilityElements.push(element);
                }
              });
            }
          });
        }
        
        // If not enough elements found, extract from the description itself
        if (impossibilityElements.length < 3) {
          // Extract keyphrases from the description
          const sentences = idea.description.split(/[.!?]+/).filter(s => s.trim().length > 0);
          const keyPhrases = [];
          
          sentences.forEach(sentence => {
            const lowercaseSentence = sentence.toLowerCase();
            // Look for sentences that mention innovative aspects
            if (lowercaseSentence.includes('impossib') || 
                lowercaseSentence.includes('contradict') || 
                lowercaseSentence.includes('paradox') ||
                lowercaseSentence.includes('novel') ||
                lowercaseSentence.includes('innovat') ||
                lowercaseSentence.includes('transform') ||
                lowercaseSentence.includes('break') ||
                lowercaseSentence.includes('revolutio')) {
              
              // Clean up and trim the sentence
              let cleanSentence = sentence.trim();
              if (cleanSentence.length > 40) {
                const words = cleanSentence.split(' ');
                if (words.length > 5) {
                  cleanSentence = words.slice(0, 5).join(' ') + '...';
                } else {
                  cleanSentence = cleanSentence.substring(0, 40) + '...';
                }
              }
              
              keyPhrases.push(cleanSentence);
            }
          });
          
          // Add extracted phrases to the impossibility elements
          impossibilityElements.push(...keyPhrases);
        }
        
        // If still no elements found, generate domain-specific ones based on detected domain
        if (impossibilityElements.length === 0) {
          const domainKeywords: Record<string, string[]> = {
            'physics': ['Quantum Entanglement at Macro Scale', 'Time Reversal Symmetry', 'Negative Mass Properties'],
            'biology': ['Non-DNA Based Evolution', 'Reverse Aging Process', 'Multi-Consciousness Organisms'],
            'computer_science': ['Self-Modifying Logic', 'Anti-Algorithmic Processing', 'Quantum State Programming'],
            'cognitive_science': ['Non-Neural Consciousness', 'Negative Information Processing', 'Paradoxical Cognition'],
            'philosophy': ['Reality Without Observer', 'Simultaneous Truth States', 'Purpose Without Teleology'],
            'economics': ['Non-Scarcity Valuation', 'Anti-Market Equilibrium', 'Negative Value Exchange'],
            'art': ['Observer-Dependent Medium', 'Self-Creating Artwork', 'Perception-Altering Aesthetics'],
            'mathematics': ['Consistent Contradictions', 'Beyond-Infinity Mathematics', 'Multi-Truth Logic'],
            'cross_domain': ['Conceptual Inversion', 'Domain Transcendence', 'Emergent Property'],
          };
          
          // Get domain-specific elements or default to cross-domain
          const elements = domainKeywords[domain] || domainKeywords['cross_domain'];
          elements.forEach(keyword => impossibilityElements.push(keyword));
        }
        
        // Limit to unique elements
        const uniqueElements = Array.from(new Set(impossibilityElements)).slice(0, 3);
        
        formatted.push({
          id: idea.id,
          title: title.length > 0 ? title : idea.description.substring(0, 50),
          description: idea.description,
          domain: domain,
          framework: idea.framework || idea.generative_framework, // Handle both possible field names
          timestamp: formatTimestamp(new Date()), // No timestamp in API, use current time
          shockMetrics: {
            novelty: idea.shock_metrics.novelty_score,
            contradiction: idea.shock_metrics.contradiction_score,
            impossibility: idea.shock_metrics.impossibility_score,
            utilityPotential: idea.shock_metrics.utility_potential,
            expertRejection: idea.shock_metrics.expert_rejection_probability,
            composite: idea.shock_metrics.composite_shock_value
          },
          impossibilityElements: uniqueElements
        });
      });
      
      // Format dialectic ideas
      dialecticIdeas.forEach(idea => {
        if (!idea || !idea.id || !idea.synthesized_idea || !idea.shock_metrics) {
          console.warn(`Explorer: Skipping invalid dialectic idea:`, idea);
          return;
        }
        
        // Similar formatting for dialectic ideas
        const title = idea.synthesized_idea.split('.')[0].trim();
        
        formatted.push({
          id: idea.id,
          title: title.length > 0 ? title : idea.synthesized_idea.substring(0, 50),
          description: idea.synthesized_idea,
          domain: 'synthesis',
          framework: 'dialectic',
          timestamp: formatTimestamp(new Date()), // No timestamp in API, use current time
          shockMetrics: {
            novelty: idea.shock_metrics.novelty_score,
            contradiction: idea.shock_metrics.contradiction_score,
            impossibility: idea.shock_metrics.impossibility_score,
            utilityPotential: idea.shock_metrics.utility_potential,
            expertRejection: idea.shock_metrics.expert_rejection_probability,
            composite: idea.shock_metrics.composite_shock_value
          },
          impossibilityElements: (idea.perspective_ideas || []).map((p, i) => `perspective_${i+1}`).slice(0, 3)
        });
      });
      
      setFormattedIdeas(formatted);
    };
    
    formatIdeas();
  }, [recentIdeas, dialecticIdeas]);
  
  // Domain options for filtering - derived from API data
  const domainOptions = [
    { id: 'all', name: 'All Domains' },
    ...Object.keys(domains).map(domain => ({ 
      id: domain.toLowerCase().replace(/\s+/g, '_'), 
      name: domain 
    }))
  ];
  
  // Framework options for filtering - derived from API data
  const frameworkOptions = [
    { id: 'all', name: 'All Frameworks' },
    ...frameworks.map(framework => ({
      id: framework.id,
      name: framework.name
    }))
  ];
  
  // Filter and sort ideas
  const filteredIdeas = formattedIdeas.filter(idea => {
    // Search query filter
    if (searchQuery && !idea.title.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !idea.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Domain filter
    if (selectedDomain !== 'all' && idea.domain !== selectedDomain) {
      return false;
    }
    
    // Framework filter
    if (selectedFramework !== 'all' && idea.framework !== selectedFramework) {
      return false;
    }
    
    return true;
  }).sort((a, b) => {
    // Sort based on selected option
    switch (sortOption) {
      case 'timestamp':
        // Compare by id (newer ideas have higher IDs)
        return b.id.localeCompare(a.id);
      case 'shock':
        return b.shockMetrics.composite - a.shockMetrics.composite;
      case 'novelty':
        return b.shockMetrics.novelty - a.shockMetrics.novelty;
      case 'contradiction':
        return b.shockMetrics.contradiction - a.shockMetrics.contradiction;
      case 'impossibility':
        return b.shockMetrics.impossibility - a.shockMetrics.impossibility;
      default:
        return 0;
    }
  });
  
  const toggleIdeaExpansion = (id: string) => {
    if (expandedIdea === id) {
      setExpandedIdea(null);
    } else {
      setExpandedIdea(id);
    }
  };
  
  return (
    <>
      <Head>
        <title>Idea Explorer | Project Leela</title>
        <meta name="description" content="Explore generated ideas from Project Leela" />
      </Head>

      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-heading flex items-center">
            <MagnifyingGlassIcon className="w-8 h-8 mr-2 text-highlight" />
            Idea Explorer
          </h1>
          
          <div className="flex space-x-2">
            <button
              className={`p-2 rounded ${viewMode === 'grid' ? 'bg-primary text-white' : 'text-text-muted hover:text-primary'}`}
              onClick={() => setViewMode('grid')}
              title="Grid View"
            >
              <Squares2X2Icon className="w-5 h-5" />
            </button>
            <button
              className={`p-2 rounded ${viewMode === 'list' ? 'bg-primary text-white' : 'text-text-muted hover:text-primary'}`}
              onClick={() => setViewMode('list')}
              title="List View"
            >
              <ListBulletIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
        
        <div className="card space-y-4">
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <div className="relative flex-1">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-text-muted" />
              <input
                type="text"
                placeholder="Search ideas..."
                className="input w-full pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="flex space-x-2">
              <select
                className="input bg-background-dark text-white border-primary-light/30"
                value={sortOption}
                onChange={(e) => setSortOption(e.target.value)}
              >
                <option value="timestamp">Latest First</option>
                <option value="shock">Highest Shock Value</option>
                <option value="novelty">Most Novel</option>
                <option value="contradiction">Most Contradictory</option>
                <option value="impossibility">Most Impossible</option>
              </select>
              
              <button
                className={`p-2 rounded ${showFilters ? 'bg-primary text-white' : 'text-text-muted hover:text-primary border border-primary-light/30'}`}
                onClick={() => setShowFilters(!showFilters)}
                title="Filters"
                disabled={isLoading}
              >
                <AdjustmentsHorizontalIcon className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="pt-4 border-t border-primary-light/20 grid grid-cols-1 md:grid-cols-2 gap-4"
            >
              <div>
                <label className="block text-sm font-medium text-text mb-2">Domain</label>
                <select
                  className="input w-full bg-background-light text-text-dark border-primary-light/30"
                  value={selectedDomain}
                  onChange={(e) => setSelectedDomain(e.target.value)}
                  disabled={isLoading}
                >
                  {domainOptions.map(domain => (
                    <option key={domain.id} value={domain.id}>{domain.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-text mb-2">Framework</label>
                <select
                  className="input w-full bg-background-light text-text-dark border-primary-light/30"
                  value={selectedFramework}
                  onChange={(e) => setSelectedFramework(e.target.value)}
                  disabled={isLoading}
                >
                  {frameworkOptions.map(framework => (
                    <option key={framework.id} value={framework.id}>{framework.name}</option>
                  ))}
                </select>
              </div>
            </motion.div>
          )}
          
          {!isLoading && !error && (
            <div className="pt-3 border-t border-primary-light/20 flex justify-between items-center text-sm">
              <div className="text-text-muted">
                {filteredIdeas.length} {filteredIdeas.length === 1 ? 'idea' : 'ideas'} found
              </div>
              
              {filteredIdeas.length > 0 && (
                <div className="text-secondary">
                  Avg. Shock Value: {(filteredIdeas.reduce((sum, idea) => sum + idea.shockMetrics.composite, 0) / filteredIdeas.length).toFixed(2)}
                </div>
              )}
            </div>
          )}
        </div>
        
        {isLoading ? (
          <div className="card flex flex-col items-center justify-center py-12">
            <svg className="animate-spin h-10 w-10 text-highlight mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-text-muted">Loading ideas...</p>
          </div>
        ) : error ? (
          <div className="card flex flex-col items-center justify-center py-12">
            <div className="rounded-full bg-red-500/20 p-4 mb-4">
              <ExclamationCircleIcon className="w-8 h-8 text-red-400" />
            </div>
            <h3 className="text-xl font-heading mb-2">Error loading ideas</h3>
            <p className="text-text-muted mb-4">{error}</p>
          </div>
        ) : filteredIdeas.length === 0 ? (
          <div className="card flex flex-col items-center justify-center py-12">
            <div className="rounded-full bg-background-dark p-4 mb-4">
              <MagnifyingGlassIcon className="w-8 h-8 text-text-light" />
            </div>
            <h3 className="text-xl font-heading mb-2">No ideas found</h3>
            <p className="text-text-muted mb-4">Try adjusting your search filters</p>
            <button 
              className="btn btn-outline"
              onClick={() => {
                setSearchQuery('');
                setSelectedDomain('all');
                setSelectedFramework('all');
              }}
            >
              Clear Filters
            </button>
          </div>
        ) : (
          <>
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredIdeas.map(idea => (
                  <div key={idea.id} id={`idea-${idea.id}`} className="card hover:shadow-glow-sm transition-shadow">
                    <div className="flex justify-between mb-1">
                      <span className="badge-accent">{
                        // Convert domain ID to display name, capitalizing words
                        idea.domain.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')
                      }</span>
                      <span className="text-xs text-text-muted">{idea.timestamp}</span>
                    </div>
                    
                    <h3 className="text-xl font-heading mb-3">{idea.title}</h3>
                    
                    <div className="text-sm text-text mb-4 max-h-24 overflow-hidden">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          div: ({node, ...props}) => <div className="prose prose-sm prose-invert max-w-none" {...props}/>
                        }}
                      >
                        {idea.description}
                      </ReactMarkdown>
                    </div>
                    
                    <div className="space-y-3 mb-4">
                      <div>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-text-muted">Framework</span>
                          <span className="text-text-dark">{
                            idea.framework.split('_').map(word => 
                              word.charAt(0).toUpperCase() + word.slice(1)
                            ).join(' ')
                          }</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-text-muted">Shock Value</span>
                          <span className="text-highlight font-mono">{idea.shockMetrics.composite.toFixed(2)}</span>
                        </div>
                      </div>
                      
                      <div className="h-1.5 w-full bg-background-dark rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-yellow-500 rounded-full"
                          style={{ width: `${idea.shockMetrics.novelty * 100 / 3}%` }}
                        ></div>
                        <div 
                          className="h-full bg-accent rounded-full -mt-1.5"
                          style={{ width: `${idea.shockMetrics.contradiction * 100 / 3}%`, marginLeft: `${idea.shockMetrics.novelty * 100 / 3}%` }}
                        ></div>
                        <div 
                          className="h-full bg-secondary rounded-full -mt-1.5"
                          style={{ width: `${idea.shockMetrics.impossibility * 100 / 3}%`, marginLeft: `${(idea.shockMetrics.novelty + idea.shockMetrics.contradiction) * 100 / 3}%` }}
                        ></div>
                      </div>
                    </div>
                    
                    <div className="flex justify-between">
                      <button
                        className="text-xs text-secondary hover:text-secondary-light"
                        onClick={() => toggleIdeaExpansion(idea.id)}
                      >
                        {expandedIdea === idea.id ? 'Collapse' : 'Expand'}
                      </button>
                      
                      <button 
                        className="text-xs text-highlight hover:text-highlight-light"
                        onClick={() => {
                          // Redirect to quantum-canvas.tsx with idea ID as parameter
                          window.location.href = `/quantum-canvas?idea=${idea.id}`;
                        }}
                      >
                        Explore
                      </button>
                    </div>
                    
                    {expandedIdea === idea.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="mt-4 pt-4 border-t border-primary-light/20"
                      >
                        <div className="mb-3">
                          <h4 className="text-sm font-medium mb-2">Full Description</h4>
                          <div className="text-sm text-text">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                div: ({node, ...props}) => <div className="prose prose-sm prose-invert max-w-none" {...props}/>
                              }}
                            >
                              {idea.description}
                            </ReactMarkdown>
                          </div>
                        </div>
                        
                        <div className="mb-3">
                          <h4 className="text-sm font-medium mb-2">Impossibility Elements</h4>
                          <div className="flex flex-wrap gap-2">
                            {idea.impossibilityElements.map(element => (
                              <span 
                                key={element} 
                                className="px-2 py-1 text-xs rounded-md bg-accent/20 text-accent-light"
                              >
                                {element.replace(/_/g, ' ')}
                              </span>
                            ))}
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium mb-2">Shock Metrics</h4>
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            {Object.entries(idea.shockMetrics).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-text-muted capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                                <span className="font-mono">{value.toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredIdeas.map(idea => (
                  <div key={idea.id} id={`idea-${idea.id}`} className="card hover:shadow-glow-sm transition-shadow">
                    <div className="flex flex-col md:flex-row md:items-start gap-4">
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <h3 className="text-xl font-heading">{idea.title}</h3>
                            <span className="badge-accent ml-3">{
                              idea.domain.split('_').map(word => 
                                word.charAt(0).toUpperCase() + word.slice(1)
                              ).join(' ')
                            }</span>
                          </div>
                          <span className="text-xs text-text-muted">{idea.timestamp}</span>
                        </div>
                        
                        <div className="text-sm text-text mb-3 line-clamp-2">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              div: ({node, ...props}) => <div className="prose prose-sm prose-invert max-w-none" {...props}/>
                            }}
                          >
                            {idea.description}
                          </ReactMarkdown>
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {idea.impossibilityElements.map(element => (
                            <span 
                              key={element} 
                              className="px-2 py-1 text-xs rounded-md bg-accent/20 text-accent-light"
                            >
                              {element.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="md:w-64 flex-shrink-0 border-t md:border-t-0 md:border-l border-primary-light/20 pt-3 md:pt-0 md:pl-4">
                        <div className="space-y-3">
                          <div>
                            <div className="flex justify-between text-xs mb-1">
                              <span className="text-text-muted">Framework</span>
                              <span className="text-text-dark">{
                                idea.framework.split('_').map(word => 
                                  word.charAt(0).toUpperCase() + word.slice(1)
                                ).join(' ')
                              }</span>
                            </div>
                            <div className="flex justify-between text-xs">
                              <span className="text-text-muted">Shock Value</span>
                              <span className="text-highlight font-mono">{idea.shockMetrics.composite.toFixed(2)}</span>
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            {Object.entries(idea.shockMetrics).slice(0, 3).map(([key, value]) => (
                              <div key={key} className="flex items-center justify-between text-xs">
                                <span className="text-text-muted capitalize w-24">{key.replace(/([A-Z])/g, ' $1')}</span>
                                <div className="flex-1 mx-2">
                                  <div className="h-1.5 bg-background-dark rounded-full overflow-hidden">
                                    <div 
                                      className={`h-full rounded-full ${
                                        key === 'novelty' ? 'bg-yellow-500' : 
                                        key === 'contradiction' ? 'bg-accent' : 
                                        key === 'impossibility' ? 'bg-secondary' : 'bg-highlight'
                                      }`}
                                      style={{ width: `${value * 100}%` }}
                                    ></div>
                                  </div>
                                </div>
                                <span className="font-mono w-10 text-right">{value.toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                          
                          <div className="flex justify-between">
                            <button
                              className="text-xs text-secondary hover:text-secondary-light"
                              onClick={() => toggleIdeaExpansion(idea.id)}
                            >
                              {expandedIdea === idea.id ? 'Collapse' : 'Expand'}
                            </button>
                            
                            <button 
                              className="text-xs text-highlight hover:text-highlight-light"
                              onClick={() => {
                                // Redirect to quantum-canvas.tsx with idea ID as parameter
                                window.location.href = `/quantum-canvas?idea=${idea.id}`;
                              }}
                            >
                              Explore
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {expandedIdea === idea.id && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.3 }}
                        className="mt-4 pt-4 border-t border-primary-light/20"
                      >
                        <div className="mb-3">
                          <h4 className="text-sm font-medium mb-2">Full Description</h4>
                          <div className="text-sm text-text">
                            <ReactMarkdown
                              remarkPlugins={[remarkGfm]}
                              components={{
                                div: ({node, ...props}) => <div className="prose prose-sm prose-invert max-w-none" {...props}/>
                              }}
                            >
                              {idea.description}
                            </ReactMarkdown>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="text-sm font-medium mb-2">All Shock Metrics</h4>
                          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-xs">
                            {Object.entries(idea.shockMetrics).map(([key, value]) => (
                              <div key={key} className="flex flex-col">
                                <span className="text-text-muted capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                                <div className="flex items-center mt-1">
                                  <div 
                                    className="h-1.5 rounded-full bg-gradient-to-r from-secondary to-highlight" 
                                    style={{ width: `${value * 100}px`, maxWidth: '80px' }}
                                  ></div>
                                  <span className="ml-2 font-mono">{value.toFixed(2)}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
};

export default ExplorerPage;