"""
Meta-Engine - Coordinates interactions between modules and manages the creative quantum state.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
import asyncio
from pydantic import UUID4
from enum import Enum, auto
from datetime import datetime
from ..config import get_config
from ..knowledge_representation.models import (
    SpiralState, CreativeIdea, ThinkingStep, ShockProfile, MethodologyChange
)
from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from ..shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier
from ..knowledge_representation.superposition_engine import SuperpositionEngine
from ..core_processing.disruptor import DisruptorModule
from ..core_processing.connector import ConnectorModule
from ..core_processing.explorer import ExplorerModule, PerspectiveType
from ..evaluation.evaluator import EvaluatorModule
from ..meta_creative.spiral_engine import MetaCreativeSpiral, SpiralPhase
from ..data_persistence.repository import Repository
from ..prompt_management.prompt_loader import PromptLoader


class CreativeWorkflow(Enum):
    """Types of creative workflows to use."""
    DISRUPTOR = auto()  # Challenge assumptions
    CONNECTOR = auto()  # Connect distant domains
    DIALECTIC = auto()  # Multiple perspectives
    TEMPORAL = auto()  # Historical and future viewpoints
    SPIRAL = auto()  # Meta-creative spiral
    META_SYNTHESIS = auto()  # Synthesize across workflows


class EmergenceDetector:
    """
    Identifies emergent patterns in the creative state.
    """
    
    def __init__(self):
        """Initialize the Emergence Detector."""
        pass
    
    def detect_emergence(self, ideas: List[CreativeIdea]) -> Dict[str, float]:
        """
        Detect emergent patterns in a set of ideas.
        
        Args:
            ideas: List of creative ideas
            
        Returns:
            Dict[str, float]: Map of emergence indicator to value (0.0-1.0)
        """
        if not ideas:
            return {}
        
        indicators = {}
        
        # Framework diversity
        frameworks = set(idea.generative_framework for idea in ideas)
        indicators["framework_diversity"] = min(1.0, len(frameworks) / 5.0)
        
        # Concept recurrence
        # Count occurrences of words across all ideas
        word_counts = {}
        for idea in ideas:
            words = idea.description.lower().split()
            for word in words:
                if len(word) > 4:  # Ignore short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Find recurring concepts (words that appear in multiple ideas)
        recurring_concepts = [word for word, count in word_counts.items() if count >= len(ideas) / 3]
        indicators["concept_recurrence"] = min(1.0, len(recurring_concepts) / 10.0)
        
        # Novelty trend
        if len(ideas) >= 3:
            recent_ideas = ideas[-3:]
            novelty_trend = sum(idea.shock_metrics.novelty_score for idea in recent_ideas) / 3.0
            indicators["novelty_trend"] = novelty_trend
        
        # Shock value consistency
        if len(ideas) >= 3:
            shock_values = [idea.shock_metrics.composite_shock_value for idea in ideas]
            import numpy as np
            shock_std = np.std(shock_values) if len(shock_values) > 1 else 0
            # High consistency = low standard deviation
            indicators["shock_consistency"] = 1.0 - min(1.0, shock_std * 2)
        
        # Pattern evolution
        if len(ideas) >= 5:
            # Look at difference between earlier and later ideas
            early_ideas = ideas[:len(ideas)//2]
            late_ideas = ideas[len(ideas)//2:]
            
            early_shock = sum(idea.shock_metrics.composite_shock_value for idea in early_ideas) / len(early_ideas)
            late_shock = sum(idea.shock_metrics.composite_shock_value for idea in late_ideas) / len(late_ideas)
            
            # Positive = improving over time
            shock_evolution = late_shock - early_shock
            indicators["pattern_evolution"] = max(0.0, min(1.0, shock_evolution + 0.5))
        
        return indicators


class CreativeStateManager:
    """
    Initializes and maintains the creative quantum state.
    """
    
    def __init__(self):
        """Initialize the Creative State Manager."""
        self.superposition_engine = SuperpositionEngine()
        self.emergence_detector = EmergenceDetector()
        self.creative_state = {
            "ideas": [],
            "thinking_steps": [],
            "methodology_changes": [],
            "emergence_indicators": {},
            "quantum_state": {},
            "creative_potential": 0.5
        }
    
    def update_state(self, 
                   ideas: Optional[List[CreativeIdea]] = None,
                   thinking_steps: Optional[List[ThinkingStep]] = None,
                   methodology_changes: Optional[List[MethodologyChange]] = None) -> Dict[str, Any]:
        """
        Update the creative state with new elements.
        
        Args:
            ideas: Optional list of new ideas
            thinking_steps: Optional list of new thinking steps
            methodology_changes: Optional list of new methodology changes
            
        Returns:
            Dict[str, Any]: Updated creative state
        """
        # Add new ideas
        if ideas:
            self.creative_state["ideas"].extend(ideas)
        
        # Add new thinking steps
        if thinking_steps:
            self.creative_state["thinking_steps"].extend(thinking_steps)
        
        # Add new methodology changes
        if methodology_changes:
            self.creative_state["methodology_changes"].extend(methodology_changes)
        
        # Detect emergence if we have ideas
        if ideas or self.creative_state["ideas"]:
            self.creative_state["emergence_indicators"] = self.emergence_detector.detect_emergence(
                self.creative_state["ideas"]
            )
        
        # Update creative potential
        self._update_creative_potential()
        
        return self.creative_state
    
    def _update_creative_potential(self):
        """Update the creative potential based on emergence indicators."""
        indicators = self.creative_state["emergence_indicators"]
        if not indicators:
            return
        
        # Average the indicators to get a creative potential value
        potential = sum(indicators.values()) / len(indicators)
        self.creative_state["creative_potential"] = potential


class FluctuationGenerator:
    """
    Applies quantum-inspired fluctuations to the creative state.
    """
    
    def apply_fluctuations(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply quantum-inspired fluctuations to the creative state.
        
        Args:
            state: The creative state
            
        Returns:
            Dict[str, Any]: State with fluctuations applied
        """
        import random
        import copy
        
        # Create a copy of the state to modify
        fluctuated_state = copy.deepcopy(state)
        
        # Apply fluctuations to creative potential
        fluctuation = (random.random() - 0.5) * 0.2  # Random fluctuation between -0.1 and 0.1
        fluctuated_state["creative_potential"] = max(0.0, min(1.0, 
                                                        fluctuated_state["creative_potential"] + fluctuation))
        
        # Apply fluctuations to emergence indicators
        for indicator in fluctuated_state["emergence_indicators"]:
            fluctuation = (random.random() - 0.5) * 0.2
            fluctuated_state["emergence_indicators"][indicator] = max(0.0, min(1.0, 
                                                                   fluctuated_state["emergence_indicators"][indicator] + fluctuation))
        
        return fluctuated_state


class FeedbackIntegrator:
    """
    Incorporates evaluation results back into the creative state.
    """
    
    def integrate_feedback(self, state: Dict[str, Any], 
                        evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integrate evaluation feedback into the creative state.
        
        Args:
            state: The creative state
            evaluation_results: Results from evaluator
            
        Returns:
            Dict[str, Any]: State with feedback integrated
        """
        import copy
        
        # Create a copy of the state to modify
        updated_state = copy.deepcopy(state)
        
        # Update ideas with evaluated idea
        if "collapsed_idea" in evaluation_results:
            collapsed_idea = evaluation_results["collapsed_idea"]
            
            # Replace existing idea with collapsed version if it exists
            for i, idea in enumerate(updated_state["ideas"]):
                if idea.id == collapsed_idea.id:
                    updated_state["ideas"][i] = collapsed_idea
                    break
        
        # Add spinoff ideas if they exist
        if "spinoff_ideas" in evaluation_results and evaluation_results["spinoff_ideas"]:
            framework = "evaluation_spinoff"
            if "collapsed_idea" in evaluation_results:
                framework = evaluation_results["collapsed_idea"].generative_framework + "_spinoff"
            
            for spinoff in evaluation_results["spinoff_ideas"]:
                # Create a basic shock profile for spinoffs
                shock_profile = ShockProfile(
                    novelty_score=0.7,
                    contradiction_score=0.6,
                    impossibility_score=0.6,
                    utility_potential=0.7,
                    expert_rejection_probability=0.6,
                    composite_shock_value=0.65
                )
                
                # Create a spinoff idea
                spinoff_idea = CreativeIdea(
                    id=uuid.uuid4(),
                    description=spinoff,
                    generative_framework=framework,
                    impossibility_elements=[],
                    contradiction_elements=[],
                    related_concepts=[],
                    shock_metrics=shock_profile
                )
                
                updated_state["ideas"].append(spinoff_idea)
        
        # Update creative potential based on evaluation
        if "generativity_score" in evaluation_results:
            # Bias potential towards generativity
            current = updated_state["creative_potential"]
            generativity = evaluation_results["generativity_score"]
            updated_state["creative_potential"] = current * 0.7 + generativity * 0.3
        
        return updated_state


class MetaEngine:
    """
    Coordinates interactions between modules and manages the creative quantum state.
    """
    
    def __init__(self, api_key: Optional[str] = None, db_url: Optional[str] = None):
        """
        Initialize the Meta-Engine.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
            db_url: Optional database URL for persistence.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.config = config
        
        # Initialize components
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.disruptor = DisruptorModule(self.api_key)
        self.connector = ConnectorModule(self.api_key)
        self.explorer = ExplorerModule(self.api_key)
        self.evaluator = EvaluatorModule(self.api_key)
        self.spiral = MetaCreativeSpiral(self.api_key)
        
        # Initialize state management
        self.state_manager = CreativeStateManager()
        self.fluctuation_generator = FluctuationGenerator()
        self.feedback_integrator = FeedbackIntegrator()
        
        # Initialize data persistence
        self.repository = Repository(db_url)
        
        # Initialize prompt management
        self.prompt_loader = PromptLoader()
    
    async def initialize(self):
        """Initialize the engine, including database setup."""
        await self.repository.initialize()
    
    async def generate_idea(self, 
                         problem_statement: str, 
                         domain: str,
                         workflow: CreativeWorkflow = CreativeWorkflow.DISRUPTOR,
                         additional_contexts: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an idea using a specified creative workflow.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            workflow: The creative workflow to use
            additional_contexts: Optional additional context information
            
        Returns:
            Dict[str, Any]: Results including the generated idea and state information
        """
        # Default additional contexts
        if additional_contexts is None:
            additional_contexts = {}
        
        # Initialize result
        result = {
            "problem_statement": problem_statement,
            "domain": domain,
            "workflow": workflow.name,
            "idea": None,
            "thinking_steps": [],
            "state_update": None
        }
        
        # Generate idea based on workflow
        if workflow == CreativeWorkflow.DISRUPTOR:
            disruptor_result = await self.disruptor.disrupt(problem_statement, domain)
            result["idea"] = disruptor_result["idea"]
            result["disruptor_details"] = {
                "assumptions": disruptor_result["assumptions"],
                "inversions": disruptor_result["inversions"],
                "paradox": disruptor_result["paradox"]
            }
        
        elif workflow == CreativeWorkflow.CONNECTOR:
            # Get domains to connect
            domains = [domain]
            if "secondary_domain" in additional_contexts:
                domains.append(additional_contexts["secondary_domain"])
            
            connector_result = await self.connector.connect(problem_statement, domains)
            result["idea"] = connector_result["idea"]
            result["connector_details"] = {
                "domains": connector_result["domains"],
                "concepts": connector_result["concepts"],
                "bridges": connector_result["bridges"],
                "blend": connector_result["blend"]
            }
        
        elif workflow == CreativeWorkflow.DIALECTIC:
            # Get perspectives to use
            perspectives = [
                PerspectiveType.RADICAL,
                PerspectiveType.CONSERVATIVE,
                PerspectiveType.FUTURE
            ]
            if "perspectives" in additional_contexts:
                perspectives = [PerspectiveType[p.upper()] for p in additional_contexts["perspectives"]
                          if p.upper() in PerspectiveType.__members__]
            
            dialectic_result = await self.explorer.explore_dialectic(
                problem_statement, domain, perspectives
            )
            result["idea"] = dialectic_result["idea"]
            result["thinking_steps"] = dialectic_result["thinking_steps"]
            result["dialectic_details"] = {
                "perspective_types": dialectic_result["perspective_types"],
                "perspective_ideas": dialectic_result["perspective_ideas"],
                "synthesized_idea": dialectic_result["synthesized_idea"]
            }
        
        elif workflow == CreativeWorkflow.TEMPORAL:
            # Get eras to use
            eras = ["ancient", "renaissance", "future"]
            if "eras" in additional_contexts:
                eras = additional_contexts["eras"]
            
            temporal_result = await self.explorer.explore_temporal(
                problem_statement, domain, eras
            )
            result["idea"] = temporal_result["idea"]
            result["thinking_steps"] = temporal_result["thinking_steps"]
            result["temporal_details"] = {
                "eras": temporal_result["eras"],
                "temporal_ideas": temporal_result["temporal_ideas"],
                "synthesized_idea": temporal_result["synthesized_idea"]
            }
        
        elif workflow == CreativeWorkflow.SPIRAL:
            # Initialize spiral if needed
            if "spiral_state" not in additional_contexts:
                spiral_state = self.spiral.initialize_spiral(
                    problem_statement,
                    ["impossibility_enforcer", "cognitive_dissonance_amplifier"]
                )
            else:
                spiral_state = additional_contexts["spiral_state"]
            
            # Advance the spiral
            updated_spiral, idea = await self.spiral.advance_spiral()
            result["idea"] = idea
            result["spiral_details"] = {
                "current_phase": updated_spiral.current_phase,
                "generated_ideas": [idea.description for idea in updated_spiral.generated_ideas[-3:]],
                "emergence_indicators": updated_spiral.emergence_indicators
            }
            result["spiral_state"] = updated_spiral
        
        elif workflow == CreativeWorkflow.META_SYNTHESIS:
            # Generate ideas using multiple workflows then synthesize
            # This is a simplified implementation
            
            # Generate a disruptor idea
            disruptor_result = await self.disruptor.disrupt(problem_statement, domain)
            disruptor_idea = disruptor_result["idea"]
            
            # Generate a dialectic idea
            dialectic_result = await self.explorer.explore_dialectic(
                problem_statement, domain, 
                [PerspectiveType.RADICAL, PerspectiveType.CONSERVATIVE]
            )
            dialectic_idea = dialectic_result["idea"]
            
            # Create a synthesis prompt
            synthesis_prompt = f"""Synthesize these ideas into a meta-creative approach to the problem:

Problem in {domain}: {problem_statement}

Idea 1 (Disruptor approach): {disruptor_idea.description}

Idea 2 (Dialectic approach): {dialectic_idea.description}

Create a meta-synthesis that:
1. Draws on elements from both approaches
2. Transcends each individual approach
3. Creates emergent properties not present in either source
4. Transforms the problem space itself
5. Maintains productive tensions rather than resolving them

Your meta-synthesis should not simply combine the ideas but generate a genuinely new approach that emerges from their interaction."""
            
            # Generate synthesis thinking
            synthesis_step = await self.claude_client.generate_thinking(
                prompt=synthesis_prompt,
                thinking_budget=16000,
                max_tokens=4000
            )
            
            # Extract synthesized idea
            synthesized_idea = self._extract_idea_description(synthesis_step.reasoning_process)
            
            # Create a shock profile for the meta-synthesis
            shock_profile = ShockProfile(
                novelty_score=0.9,
                contradiction_score=0.85,
                impossibility_score=0.8,
                utility_potential=0.7,
                expert_rejection_probability=0.85,
                composite_shock_value=0.85
            )
            
            # Create a meta-synthesis idea
            meta_idea = CreativeIdea(
                id=uuid.uuid4(),
                description=synthesized_idea,
                generative_framework="meta_synthesis",
                impossibility_elements=[],
                contradiction_elements=[],
                related_concepts=[],
                shock_metrics=shock_profile
            )
            
            result["idea"] = meta_idea
            result["thinking_steps"] = [synthesis_step]
            result["meta_synthesis_details"] = {
                "disruptor_idea": disruptor_idea.description,
                "dialectic_idea": dialectic_idea.description,
                "synthesized_idea": synthesized_idea
            }
        
        # Update creative state
        ideas = [result["idea"]] if result["idea"] else []
        thinking_steps = result["thinking_steps"] if "thinking_steps" in result else []
        
        updated_state = self.state_manager.update_state(
            ideas=ideas,
            thinking_steps=thinking_steps
        )
        
        # Apply quantum fluctuations
        fluctuated_state = self.fluctuation_generator.apply_fluctuations(updated_state)
        
        result["state_update"] = fluctuated_state
        
        # Persist data
        if result["idea"]:
            try:
                await self.repository.save_idea(result["idea"])
            except Exception as e:
                print(f"Warning: Failed to save idea: {e}")
        
        if "thinking_steps" in result and result["thinking_steps"]:
            for step in result["thinking_steps"]:
                try:
                    await self.repository.save_thinking_step(step)
                except Exception as e:
                    print(f"Warning: Failed to save thinking step: {e}")
        
        # If spiral workflow, persist spiral state
        if workflow == CreativeWorkflow.SPIRAL and "spiral_state" in result:
            try:
                await self.repository.save_spiral_state(result["spiral_state"])
            except Exception as e:
                print(f"Warning: Failed to save spiral state: {e}")
        
        return result
    
    async def evaluate_idea(self, idea: CreativeIdea, domain: str) -> Dict[str, Any]:
        """
        Evaluate an idea and update the creative state.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            Dict[str, Any]: Evaluation results and updated state
        """
        # Run evaluation
        evaluation_results = await self.evaluator.evaluate(idea, domain)
        
        # Integrate feedback into state
        updated_state = self.feedback_integrator.integrate_feedback(
            self.state_manager.creative_state,
            evaluation_results
        )
        
        # Create result
        result = {
            "idea": idea,
            "domain": domain,
            "evaluation_results": evaluation_results,
            "state_update": updated_state
        }
        
        # Persist data
        try:
            await self.repository.save_idea(idea)
        except Exception as e:
            print(f"Warning: Failed to save evaluated idea: {e}")
        
        return result
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract idea description from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted idea description
        """
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "The synthesis", "The meta-synthesis", 
            "The synthesized idea", "Final synthesis", "Synthesized approach"
        ]
        
        for marker in conclusion_markers:
            if marker in thinking_text:
                # Extract text after the marker until the next double newline
                start_idx = thinking_text.find(marker)
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                # Extract and clean the text
                description = thinking_text[start_idx:end_idx].strip()
                
                # Remove the marker itself if at the beginning
                if description.startswith(marker):
                    description = description[len(marker):].strip()
                    # Remove any leading colon
                    if description.startswith(":"):
                        description = description[1:].strip()
                
                return description
        
        # If no conclusion marker found, take the last paragraph
        paragraphs = thinking_text.split("\n\n")
        if paragraphs:
            return paragraphs[-1].strip()
        
        # Fallback
        return thinking_text[-500:].strip()  # Last 500 characters