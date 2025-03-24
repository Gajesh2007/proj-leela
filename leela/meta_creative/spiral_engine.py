"""
Meta-Creative Spiral Engine - Implements the Create→Reflect→Abstract→Evolve→Transcend→Return cycle.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from datetime import datetime
from pydantic import UUID4
from enum import Enum, auto
from ..config import get_config
from ..knowledge_representation.models import (
    SpiralState, CreativeIdea, ThinkingStep, MethodologyChange, ShockProfile
)
from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from ..shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier


class SpiralPhase(Enum):
    """Enum for the phases of the meta-creative spiral."""
    CREATE = auto()
    REFLECT = auto()
    ABSTRACT = auto()
    EVOLVE = auto()
    TRANSCEND = auto()
    RETURN = auto()


class MetaCreativeSpiral:
    """
    Implements the Meta-Creative Spiral that continuously evolves creative methodologies.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Meta-Creative Spiral.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        self.config = get_config()
        self.api_key = api_key or self.config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.thinking_manager = ExtendedThinkingManager(self.api_key)
        self.impossibility_enforcer = ImpossibilityEnforcer()
        self.dissonance_amplifier = CognitiveDissonanceAmplifier()
        
        # Initialize state
        self.current_phase = SpiralPhase.CREATE
        self.spiral_state = None
        self.iteration_count = 0
        self.methodology_history = []
        
        # Phase durations
        self.phase_durations = {
            SpiralPhase.CREATE: self.config["creativity"]["create_phase_duration"],
            SpiralPhase.REFLECT: self.config["creativity"]["reflect_phase_duration"],
            SpiralPhase.ABSTRACT: self.config["creativity"]["abstract_phase_duration"],
            SpiralPhase.EVOLVE: self.config["creativity"]["evolve_phase_duration"],
            SpiralPhase.TRANSCEND: self.config["creativity"]["transcend_phase_duration"],
            SpiralPhase.RETURN: self.config["creativity"]["return_phase_duration"]
        }
        
        # Phase counters
        self.phase_counters = {phase: 0 for phase in SpiralPhase}
    
    def initialize_spiral(self, problem_space: str, active_frameworks: List[str]) -> SpiralState:
        """
        Initialize the spiral state for a new creative process.
        
        Args:
            problem_space: Problem domain being explored
            active_frameworks: List of active shock frameworks
            
        Returns:
            SpiralState: The initialized spiral state
        """
        self.spiral_state = SpiralState(
            id=uuid.uuid4(),
            timestamp=datetime.now(),
            current_phase=self.current_phase.name,
            problem_space=problem_space,
            active_shock_frameworks=active_frameworks,
            generated_ideas=[],
            thinking_history=[],
            methodology_evolution=[],
            emergence_indicators={}
        )
        
        # Reset phase counters
        self.phase_counters = {phase: 0 for phase in SpiralPhase}
        self.iteration_count = 0
        
        return self.spiral_state
    
    async def advance_spiral(self) -> Tuple[SpiralState, Optional[CreativeIdea]]:
        """
        Advance the spiral to the next phase or iteration.
        
        Returns:
            Tuple[SpiralState, Optional[CreativeIdea]]: Updated spiral state and any new idea generated
        """
        if not self.spiral_state:
            raise ValueError("Spiral must be initialized before advancing")
        
        # Increment the counter for the current phase
        self.phase_counters[self.current_phase] += 1
        
        # Check if we should move to the next phase
        if self.phase_counters[self.current_phase] >= self.phase_durations[self.current_phase]:
            # Reset this phase's counter
            self.phase_counters[self.current_phase] = 0
            
            # Move to the next phase
            self._advance_to_next_phase()
        
        # Execute the current phase
        new_idea = await self._execute_current_phase()
        
        # Update the spiral state
        self.spiral_state.timestamp = datetime.now()
        self.spiral_state.current_phase = self.current_phase.name
        
        if new_idea:
            self.spiral_state.generated_ideas.append(new_idea)
        
        return self.spiral_state, new_idea
    
    def _advance_to_next_phase(self):
        """Advance to the next phase in the spiral."""
        # Get all phases in order
        phases = list(SpiralPhase)
        
        # Find the current phase index
        current_idx = phases.index(self.current_phase)
        
        # Calculate the next phase index
        next_idx = (current_idx + 1) % len(phases)
        
        # Set the new phase
        self.current_phase = phases[next_idx]
        
        # If we've completed a full cycle, increment the iteration count
        if next_idx == 0:
            self.iteration_count += 1
    
    async def _execute_current_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the current phase of the spiral.
        
        Returns:
            Optional[CreativeIdea]: Any new idea generated during this phase
        """
        if self.current_phase == SpiralPhase.CREATE:
            return await self._execute_create_phase()
        elif self.current_phase == SpiralPhase.REFLECT:
            return await self._execute_reflect_phase()
        elif self.current_phase == SpiralPhase.ABSTRACT:
            return await self._execute_abstract_phase()
        elif self.current_phase == SpiralPhase.EVOLVE:
            return await self._execute_evolve_phase()
        elif self.current_phase == SpiralPhase.TRANSCEND:
            return await self._execute_transcend_phase()
        elif self.current_phase == SpiralPhase.RETURN:
            return await self._execute_return_phase()
        
        return None
    
    async def _execute_create_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Create phase - generate novel ideas and approaches.
        
        Returns:
            Optional[CreativeIdea]: The creative idea generated
        """
        # Get a random framework from active frameworks
        import random
        framework = random.choice(self.spiral_state.active_shock_frameworks)
        
        # Create a prompt for the chosen framework
        thinking_prompt = f"Generate a novel solution to the following problem: {self.spiral_state.problem_space}\n\n"
        thinking_prompt += f"Use the {framework} framework to generate an idea that violates conventional assumptions."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=thinking_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Generate creative idea based on framework
        creative_idea = None
        if framework == "impossibility_enforcer":
            creative_idea = self.impossibility_enforcer.enforce_impossibility(
                thinking_step, 
                self.spiral_state.problem_space.split()[0],  # Simple domain extraction
                [],  # No specific constraints
                0.6  # Default threshold
            )
        elif framework == "cognitive_dissonance_amplifier":
            creative_idea = self.dissonance_amplifier.amplify_dissonance(
                thinking_step, 
                self.spiral_state.problem_space.split()[0],  # Simple domain extraction
                []  # No specific requirements
            )
        else:
            # Default to impossibility enforcer
            creative_idea = self.impossibility_enforcer.enforce_impossibility(
                thinking_step, 
                self.spiral_state.problem_space.split()[0],
                [],
                0.6
            )
        
        return creative_idea
    
    async def _execute_reflect_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Reflect phase - analyze the creative process itself.
        
        Returns:
            Optional[CreativeIdea]: Any new insights as a creative idea
        """
        # If we don't have any ideas yet, skip
        if not self.spiral_state.generated_ideas:
            return None
        
        # Create a reflection prompt
        reflection_prompt = "Analyze the creative process that generated the following ideas:\n\n"
        
        # Add recent ideas (up to 3)
        for i, idea in enumerate(self.spiral_state.generated_ideas[-3:]):
            reflection_prompt += f"Idea {i+1}: {idea.description}\n"
            reflection_prompt += f"Framework: {idea.generative_framework}\n"
            reflection_prompt += f"Shock metrics: Novelty: {idea.shock_metrics.novelty_score}, "
            reflection_prompt += f"Contradiction: {idea.shock_metrics.contradiction_score}, "
            reflection_prompt += f"Impossibility: {idea.shock_metrics.impossibility_score}\n\n"
        
        reflection_prompt += "Identify patterns in the creative process. What's working well? What could be improved? "
        reflection_prompt += "How might the creative process itself be enhanced?"
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=reflection_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract insights as a creative idea
        description = "Reflective analysis: " + self.impossibility_enforcer._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the reflection
        # This is different from regular ideas - we're evaluating the reflection itself
        shock_profile = ShockProfile(
            novelty_score=0.5,  # Reflections are typically less "novel"
            contradiction_score=0.4,
            impossibility_score=0.3,
            utility_potential=0.8,  # But potentially more useful
            expert_rejection_probability=0.4,
            composite_shock_value=0.5
        )
        
        # Create a "meta-idea" about the creative process
        meta_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="meta_reflection",
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return meta_idea
    
    async def _execute_abstract_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Abstract phase - identify patterns and principles in creative methods.
        
        Returns:
            Optional[CreativeIdea]: Any new insights as a creative idea
        """
        # If we don't have enough history, skip
        if len(self.spiral_state.thinking_history) < 3:
            return None
        
        # Create an abstraction prompt
        abstraction_prompt = "Analyze the following thinking processes and extract abstract principles of creativity:\n\n"
        
        # Add recent thinking steps (up to 3)
        for i, step in enumerate(self.spiral_state.thinking_history[-3:]):
            abstraction_prompt += f"Thinking Process {i+1} (Framework: {step.framework}):\n"
            # Add a preview of the reasoning (first 300 chars)
            preview = step.reasoning_process[:300] + "..." if len(step.reasoning_process) > 300 else step.reasoning_process
            abstraction_prompt += preview + "\n\n"
            
            # Add insights if available
            if step.insights_generated:
                abstraction_prompt += "Insights:\n"
                for insight in step.insights_generated[:3]:  # Limit to 3 insights
                    abstraction_prompt += f"- {insight}\n"
                abstraction_prompt += "\n"
        
        abstraction_prompt += "Extract abstract creative principles that could apply across domains. "
        abstraction_prompt += "Identify meta-patterns in how ideas are generated. "
        abstraction_prompt += "What fundamental creative operations are occurring? "
        abstraction_prompt += "How might these be generalized into a methodology?"
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=abstraction_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract abstract principles as a creative idea
        description = "Abstract principles: " + self.impossibility_enforcer._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the abstraction
        shock_profile = ShockProfile(
            novelty_score=0.6,
            contradiction_score=0.5,
            impossibility_score=0.4,
            utility_potential=0.9,  # Abstractions are highly useful
            expert_rejection_probability=0.5,
            composite_shock_value=0.6
        )
        
        # Create a "meta-idea" about creative principles
        meta_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="meta_abstraction",
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return meta_idea
    
    async def _execute_evolve_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Evolve phase - generate new creative methodologies.
        
        Returns:
            Optional[CreativeIdea]: Any new methodology as a creative idea
        """
        # Need at least one abstraction to evolve
        has_abstraction = any(idea.generative_framework == "meta_abstraction" 
                           for idea in self.spiral_state.generated_ideas)
        if not has_abstraction:
            return None
        
        # Get the most recent abstraction
        abstractions = [idea for idea in self.spiral_state.generated_ideas 
                     if idea.generative_framework == "meta_abstraction"]
        latest_abstraction = abstractions[-1] if abstractions else None
        
        if not latest_abstraction:
            return None
        
        # Create an evolution prompt
        evolution_prompt = f"Based on these abstract principles:\n\n{latest_abstraction.description}\n\n"
        evolution_prompt += "Design a new creative methodology or framework that could generate even more shocking ideas. "
        evolution_prompt += "This methodology should:\n"
        evolution_prompt += "1. Push beyond current frameworks like impossibility enforcement or cognitive dissonance amplification\n"
        evolution_prompt += "2. Generate ideas that would be shocking even to users of those frameworks\n"
        evolution_prompt += "3. Introduce novel cognitive operations not present in existing approaches\n"
        evolution_prompt += "4. Be implementable as a concrete prompt or algorithm\n\n"
        evolution_prompt += "Design this new creative methodology in detail, including its key operations, principles, and an example prompt."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=evolution_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract the new methodology
        new_methodology = self.impossibility_enforcer._extract_idea_description(thinking_step.reasoning_process)
        
        # Extract the methodology name from the text (simple approach)
        import re
        methodology_name = "new_methodology"  # Default name
        name_match = re.search(r"([A-Z][a-zA-Z\s]+)(?:Framework|Methodology|Approach)", new_methodology)
        if name_match:
            methodology_name = name_match.group(1).strip().lower().replace(" ", "_")
        
        # Create a shock profile for the new methodology
        shock_profile = ShockProfile(
            novelty_score=0.8,
            contradiction_score=0.7,
            impossibility_score=0.6,
            utility_potential=0.7,
            expert_rejection_probability=0.6,
            composite_shock_value=0.75
        )
        
        # Create a record of methodology evolution
        if self.methodology_history:
            previous_methodology = self.methodology_history[-1]
        else:
            # Default to a basic methodology if none exists
            previous_methodology = "impossibility_enforcer"
        
        methodology_change = MethodologyChange(
            id=uuid.uuid4(),
            previous_methodology=previous_methodology,
            new_methodology=methodology_name,
            evolution_rationale=new_methodology,
            performance_change=0.1,  # Assumed improvement
            iteration_number=self.iteration_count
        )
        
        # Add to methodology evolution
        self.spiral_state.methodology_evolution.append(methodology_change)
        self.methodology_history.append(methodology_name)
        
        # Create a "meta-idea" about the new methodology
        meta_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=f"New methodology: {new_methodology}",
            generative_framework="methodology_evolution",
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return meta_idea
    
    async def _execute_transcend_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Transcend phase - apply new methodologies to create ideas.
        
        Returns:
            Optional[CreativeIdea]: A new idea using the transcendent methodology
        """
        # Need a new methodology to transcend
        if not self.spiral_state.methodology_evolution:
            return None
        
        # Get the most recent methodology
        latest_methodology = self.spiral_state.methodology_evolution[-1]
        
        # Create a transcendence prompt
        transcendence_prompt = f"Apply this new creative methodology:\n\n{latest_methodology.evolution_rationale}\n\n"
        transcendence_prompt += f"To generate a revolutionary solution to the problem: {self.spiral_state.problem_space}\n\n"
        transcendence_prompt += "Generate an idea that transcends conventional frameworks and even pushes beyond impossibility enforcement "
        transcendence_prompt += "and cognitive dissonance amplification. The idea should shock even those familiar with these approaches."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=transcendence_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract the transcendent idea
        description = self.impossibility_enforcer._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the transcendent idea
        # This should be higher than normal ideas since it uses an evolved methodology
        shock_profile = ShockProfile(
            novelty_score=0.9,
            contradiction_score=0.85,
            impossibility_score=0.8,
            utility_potential=0.7,
            expert_rejection_probability=0.85,
            composite_shock_value=0.85
        )
        
        # Create a transcendent idea
        transcendent_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework=latest_methodology.new_methodology,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return transcendent_idea
    
    async def _execute_return_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Return phase - bring transcendent insights back to original problem.
        
        Returns:
            Optional[CreativeIdea]: A new idea that applies transcendent insights to the original problem
        """
        # Need some ideas generated already
        if len(self.spiral_state.generated_ideas) < 2:
            return None
        
        # Get a transcendent idea if available
        transcendent_ideas = [idea for idea in self.spiral_state.generated_ideas 
                           if hasattr(idea, 'generative_framework') and 
                           idea.generative_framework not in ["impossibility_enforcer", "cognitive_dissonance_amplifier"]]
        
        transcendent_idea = transcendent_ideas[-1] if transcendent_ideas else None
        
        if not transcendent_idea:
            # Fall back to the most recent idea
            transcendent_idea = self.spiral_state.generated_ideas[-1]
        
        # Create a return prompt
        return_prompt = f"You've generated this transcendent idea:\n\n{transcendent_idea.description}\n\n"
        return_prompt += f"Now, return to the original problem: {self.spiral_state.problem_space}\n\n"
        return_prompt += "Using the insights gained from your creative exploration, generate a practical solution "
        return_prompt += "that maintains the revolutionary spirit of your transcendent idea but can be communicated "
        return_prompt += "and potentially implemented in the real world. The solution should still be shocking and novel, "
        return_prompt += "but should connect more directly to the original problem domain."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=return_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract the return idea
        description = self.impossibility_enforcer._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the return idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.8,
            impossibility_score=0.75,
            utility_potential=0.8,  # Higher utility as it's more practical
            expert_rejection_probability=0.75,
            composite_shock_value=0.8
        )
        
        # Create a return idea
        return_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="spiral_return",
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return return_idea
    
    def get_current_state(self) -> SpiralState:
        """Get the current spiral state."""
        if not self.spiral_state:
            raise ValueError("Spiral must be initialized first")
        return self.spiral_state
    
    def calculate_emergence_indicators(self) -> Dict[str, float]:
        """
        Calculate indicators of emergent properties in the creative process.
        
        Returns:
            Dict[str, float]: Map of indicator names to values
        """
        if not self.spiral_state or not self.spiral_state.generated_ideas:
            return {}
        
        indicators = {}
        
        # Diversity of frameworks
        frameworks = set(idea.generative_framework for idea in self.spiral_state.generated_ideas)
        indicators["framework_diversity"] = min(1.0, len(frameworks) / 5.0)
        
        # Novelty trend
        if len(self.spiral_state.generated_ideas) >= 3:
            recent_ideas = self.spiral_state.generated_ideas[-3:]
            novelty_trend = sum(idea.shock_metrics.novelty_score for idea in recent_ideas) / 3.0
            indicators["novelty_trend"] = novelty_trend
        
        # Methodology evolution rate
        if self.iteration_count > 0:
            evolution_rate = len(self.spiral_state.methodology_evolution) / self.iteration_count
            indicators["methodology_evolution_rate"] = min(1.0, evolution_rate)
        
        # Insight density
        if self.spiral_state.thinking_history:
            total_insights = sum(len(step.insights_generated) for step in self.spiral_state.thinking_history)
            insight_density = min(1.0, total_insights / (len(self.spiral_state.thinking_history) * 5.0))
            indicators["insight_density"] = insight_density
        
        # Update the spiral state
        self.spiral_state.emergence_indicators = indicators
        
        return indicators