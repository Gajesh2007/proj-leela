"""
Meta-Creative Spiral Engine - Implements the Create→Reflect→Abstract→Evolve→Transcend→Return cycle.
"""
from typing import Dict, List, Any, Optional, Tuple, Callable, Type
import uuid
import asyncio
from datetime import datetime
from pydantic import UUID4
from enum import Enum, auto
import logging
import functools
from ..config import get_config
from ..knowledge_representation.models import (
    SpiralState, CreativeIdea, ThinkingStep, MethodologyChange, ShockProfile
)
from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from ..shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier
from ..prompt_management.prompt_loader import PromptLoader


def uses_prompt(primary_prompt: str, dependencies: List[str] = None) -> Callable:
    """
    Decorator to indicate a class uses prompts.
    
    Args:
        primary_prompt: The primary prompt used by the class
        dependencies: Optional list of other prompt dependencies
        
    Returns:
        Callable: The decorator function
    """
    def decorator(cls: Type) -> Type:
        """Inner decorator function"""
        cls.primary_prompt = primary_prompt
        cls.prompt_dependencies = dependencies or []
        return cls
    return decorator


class SpiralPhase(Enum):
    """Enum for the phases of the meta-creative spiral."""
    CREATE = auto()
    REFLECT = auto()
    ABSTRACT = auto()
    EVOLVE = auto()
    TRANSCEND = auto()
    RETURN = auto()


@uses_prompt("meta_spiral_create", dependencies=[
    "meta_spiral_reflect", 
    "meta_spiral_abstract",
    "meta_spiral_evolve",
    "meta_spiral_transcend",
    "meta_spiral_return"
])
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
        self.prompt_loader = PromptLoader()
        
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
        
        # Initialize outputs from each phase
        self.phase_outputs = {
            SpiralPhase.CREATE: None,
            SpiralPhase.REFLECT: None,
            SpiralPhase.ABSTRACT: None,
            SpiralPhase.EVOLVE: None,
            SpiralPhase.TRANSCEND: None,
            SpiralPhase.RETURN: None
        }
        
        # Prompt templates for each phase
        self.phase_prompts = {
            SpiralPhase.CREATE: "meta_spiral_create",
            SpiralPhase.REFLECT: "meta_spiral_reflect",
            SpiralPhase.ABSTRACT: "meta_spiral_abstract",
            SpiralPhase.EVOLVE: "meta_spiral_evolve",
            SpiralPhase.TRANSCEND: "meta_spiral_transcend",
            SpiralPhase.RETURN: "meta_spiral_return"
        }
    
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
        # Extract the domain from the problem space
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Render the create phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "creative_state": self._get_creative_state_summary()
        }
        
        create_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.CREATE], context)
        
        # Fallback if prompt rendering fails
        if not create_prompt:
            logging.warning("Failed to render CREATE phase prompt template, using fallback prompt")
            import random
            framework = random.choice(self.spiral_state.active_shock_frameworks)
            create_prompt = f"Generate novel approaches to the following problem: {self.spiral_state.problem_space}\n\n"
            create_prompt += f"Use the {framework} framework to generate an idea that violates conventional assumptions."
        
        # Generate thinking with reduced token limits to use streaming
        thinking_step = await self.claude_client.generate_thinking(
            prompt=create_prompt,
            thinking_budget=4000,  # Reduced further to avoid timeouts
            max_tokens=8000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract create_phase_output from thinking process
        create_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "create_phase_output")
        if not create_phase_output:
            create_phase_output = thinking_step.reasoning_process
        
        # Store the output for future phases
        self.phase_outputs[SpiralPhase.CREATE] = create_phase_output
        
        # Generate a creative idea from the output
        # Create shock profile for the create phase idea
        shock_profile = ShockProfile(
            novelty_score=0.7,
            contradiction_score=0.6,
            impossibility_score=0.5,
            utility_potential=0.7,
            expert_rejection_probability=0.6,
            composite_shock_value=0.65
        )
        
        # Extract the main idea description from the output
        idea_description = self._extract_idea_description(create_phase_output)
        
        # Create the creative idea
        creative_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=idea_description,
            generative_framework="meta_spiral_create",
            domain=domain,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return creative_idea
        
    def _extract_tagged_content(self, text: str, tag_name: str) -> Optional[str]:
        """
        Extract content between opening and closing tags.
        
        Args:
            text: The text to search
            tag_name: The name of the tag to find
            
        Returns:
            Optional[str]: The extracted content, or None if not found
        """
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        start_pos = text.find(start_tag)
        if start_pos == -1:
            return None
            
        start_pos += len(start_tag)
        end_pos = text.find(end_tag, start_pos)
        
        if end_pos == -1:
            return None
            
        return text[start_pos:end_pos].strip()
        
    def _extract_idea_description(self, text: str) -> str:
        """
        Extract the main idea description from create phase output.
        
        Args:
            text: The text to extract from
            
        Returns:
            str: The extracted idea description
        """
        # First try to extract from generative_seeds section if it exists
        seeds = self._extract_tagged_content(text, "generative_seeds")
        if seeds:
            return seeds
            
        # Then try novel_approaches
        approaches = self._extract_tagged_content(text, "novel_approaches")
        if approaches:
            return approaches
            
        # Fallback to the first 500 characters of the text
        if len(text) > 500:
            return text[:500] + "..."
        return text
    
    async def _execute_reflect_phase(self) -> Optional[CreativeIdea]:
        """
        Execute the Reflect phase - analyze the creative process itself.
        
        Returns:
            Optional[CreativeIdea]: Any new insights as a creative idea
        """
        # If we don't have any ideas yet, skip
        if not self.spiral_state.generated_ideas:
            return None
        
        # Extract domain
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Ensure we have the CREATE phase output
        create_phase_output = self.phase_outputs[SpiralPhase.CREATE]
        if not create_phase_output:
            # If no CREATE output stored, try to reconstruct from the most recent idea
            recent_idea = self.spiral_state.generated_ideas[-1]
            create_phase_output = recent_idea.description
        
        # Render the reflect phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "create_phase_output": create_phase_output,
            "creative_state": self._get_creative_state_summary()
        }
        
        reflect_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.REFLECT], context)
        
        # Fallback if prompt rendering fails
        if not reflect_prompt:
            logging.warning("Failed to render REFLECT phase prompt template, using fallback prompt")
            
            # Create a fallback reflection prompt
            reflect_prompt = "Analyze the creative process that generated the following ideas:\n\n"
            
            # Add recent ideas (up to 3)
            for i, idea in enumerate(self.spiral_state.generated_ideas[-3:]):
                reflect_prompt += f"Idea {i+1}: {idea.description}\n"
                reflect_prompt += f"Framework: {idea.generative_framework}\n"
                reflect_prompt += f"Shock metrics: Novelty: {idea.shock_metrics.novelty_score}, "
                reflect_prompt += f"Contradiction: {idea.shock_metrics.contradiction_score}, "
                reflect_prompt += f"Impossibility: {idea.shock_metrics.impossibility_score}\n\n"
            
            reflect_prompt += "Identify patterns in the creative process. What's working well? What could be improved? "
            reflect_prompt += "How might the creative process itself be enhanced?"
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=reflect_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract reflect_phase_output from thinking process
        reflect_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "reflect_phase_output")
        if not reflect_phase_output:
            reflect_phase_output = thinking_step.reasoning_process
        
        # Store the output for future phases
        self.phase_outputs[SpiralPhase.REFLECT] = reflect_phase_output
        
        # Create a shock profile for the reflection
        shock_profile = ShockProfile(
            novelty_score=0.5,  # Reflections are typically less "novel"
            contradiction_score=0.4,
            impossibility_score=0.3,
            utility_potential=0.8,  # But potentially more useful
            expert_rejection_probability=0.4,
            composite_shock_value=0.5
        )
        
        # Extract meta insights
        description = ""
        meta_insights = self._extract_tagged_content(reflect_phase_output, "meta_insights")
        if meta_insights:
            description = "Meta-insights: " + meta_insights
        else:
            description = "Reflective analysis: " + reflect_phase_output[:500] + ("..." if len(reflect_phase_output) > 500 else "")
        
        # Create a "meta-idea" about the creative process
        meta_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="meta_reflection",
            domain=domain,
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
        # If we don't have previous phase outputs, skip
        if not self.phase_outputs[SpiralPhase.CREATE] or not self.phase_outputs[SpiralPhase.REFLECT]:
            logging.warning("Cannot execute ABSTRACT phase without outputs from CREATE and REFLECT phases")
            return None
        
        # Extract domain
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Render the abstract phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "create_phase_output": self.phase_outputs[SpiralPhase.CREATE],
            "reflect_phase_output": self.phase_outputs[SpiralPhase.REFLECT],
            "creative_state": self._get_creative_state_summary()
        }
        
        abstract_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.ABSTRACT], context)
        
        # Fallback if prompt rendering fails
        if not abstract_prompt:
            logging.warning("Failed to render ABSTRACT phase prompt template, using fallback prompt")
            
            # Create a fallback abstraction prompt
            abstract_prompt = "Analyze the following thinking processes and extract abstract principles of creativity:\n\n"
            
            # Add recent thinking steps (up to 3)
            for i, step in enumerate(self.spiral_state.thinking_history[-3:]):
                abstract_prompt += f"Thinking Process {i+1} (Framework: {step.framework}):\n"
                # Add a preview of the reasoning (first 300 chars)
                preview = step.reasoning_process[:300] + "..." if len(step.reasoning_process) > 300 else step.reasoning_process
                abstract_prompt += preview + "\n\n"
                
                # Add insights if available
                if step.insights_generated:
                    abstract_prompt += "Insights:\n"
                    for insight in step.insights_generated[:3]:  # Limit to 3 insights
                        abstract_prompt += f"- {insight}\n"
                    abstract_prompt += "\n"
            
            abstract_prompt += "Extract abstract creative principles that could apply across domains. "
            abstract_prompt += "Identify meta-patterns in how ideas are generated. "
            abstract_prompt += "What fundamental creative operations are occurring? "
            abstract_prompt += "How might these be generalized into a methodology?"
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=abstract_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract abstract_phase_output from thinking process
        abstract_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "abstract_phase_output")
        if not abstract_phase_output:
            abstract_phase_output = thinking_step.reasoning_process
        
        # Store the output for future phases
        self.phase_outputs[SpiralPhase.ABSTRACT] = abstract_phase_output
        
        # Extract core principles
        description = ""
        core_principles = self._extract_tagged_content(abstract_phase_output, "core_principles")
        meta_framework = self._extract_tagged_content(abstract_phase_output, "meta_framework")
        
        if core_principles:
            description = "Core principles: " + core_principles
            if meta_framework:
                description += "\n\nMeta-framework: " + meta_framework
        else:
            description = "Abstract analysis: " + abstract_phase_output[:500] + ("..." if len(abstract_phase_output) > 500 else "")
        
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
            domain=domain,
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
        # We need outputs from previous phases
        if not self.phase_outputs[SpiralPhase.CREATE] or \
           not self.phase_outputs[SpiralPhase.REFLECT] or \
           not self.phase_outputs[SpiralPhase.ABSTRACT]:
            logging.warning("Cannot execute EVOLVE phase without outputs from previous phases")
            return None
            
        # Extract domain
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Render the evolve phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "create_phase_output": self.phase_outputs[SpiralPhase.CREATE],
            "reflect_phase_output": self.phase_outputs[SpiralPhase.REFLECT],
            "abstract_phase_output": self.phase_outputs[SpiralPhase.ABSTRACT],
            "creative_state": self._get_creative_state_summary()
        }
        
        evolve_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.EVOLVE], context)
        
        # Fallback if prompt rendering fails
        if not evolve_prompt:
            logging.warning("Failed to render EVOLVE phase prompt template, using fallback prompt")
            
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
            
            # Create a fallback evolution prompt
            evolve_prompt = f"Based on these abstract principles:\n\n{latest_abstraction.description}\n\n"
            evolve_prompt += "Design a new creative methodology or framework that could generate even more shocking ideas. "
            evolve_prompt += "This methodology should:\n"
            evolve_prompt += "1. Push beyond current frameworks like impossibility enforcement or cognitive dissonance amplification\n"
            evolve_prompt += "2. Generate ideas that would be shocking even to users of those frameworks\n"
            evolve_prompt += "3. Introduce novel cognitive operations not present in existing approaches\n"
            evolve_prompt += "4. Be implementable as a concrete prompt or algorithm\n\n"
            evolve_prompt += "Design this new creative methodology in detail, including its key operations, principles, and an example prompt."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=evolve_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract evolve_phase_output from thinking process
        evolve_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "evolve_phase_output")
        if not evolve_phase_output:
            evolve_phase_output = thinking_step.reasoning_process
        
        # Store the output for future phases
        self.phase_outputs[SpiralPhase.EVOLVE] = evolve_phase_output
        
        # Extract the new methodology from enhanced_methodologies or novel_recombinations
        enhanced_methodologies = self._extract_tagged_content(evolve_phase_output, "enhanced_methodologies")
        novel_recombinations = self._extract_tagged_content(evolve_phase_output, "novel_recombinations")
        
        # Combine the methodologies
        new_methodology = ""
        if enhanced_methodologies:
            new_methodology += "Enhanced Methodologies: " + enhanced_methodologies
        if novel_recombinations:
            if new_methodology:
                new_methodology += "\n\n"
            new_methodology += "Novel Recombinations: " + novel_recombinations
        
        # If we couldn't extract structured content, use the whole output
        if not new_methodology:
            new_methodology = evolve_phase_output[:1000] + ("..." if len(evolve_phase_output) > 1000 else "")
        
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
            domain=domain,
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
        # We need outputs from all previous phases
        if not self.phase_outputs[SpiralPhase.CREATE] or \
           not self.phase_outputs[SpiralPhase.REFLECT] or \
           not self.phase_outputs[SpiralPhase.ABSTRACT] or \
           not self.phase_outputs[SpiralPhase.EVOLVE]:
            logging.warning("Cannot execute TRANSCEND phase without outputs from previous phases")
            return None
        
        # Extract domain
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Render the transcend phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "create_phase_output": self.phase_outputs[SpiralPhase.CREATE],
            "reflect_phase_output": self.phase_outputs[SpiralPhase.REFLECT],
            "abstract_phase_output": self.phase_outputs[SpiralPhase.ABSTRACT],
            "evolve_phase_output": self.phase_outputs[SpiralPhase.EVOLVE],
            "creative_state": self._get_creative_state_summary()
        }
        
        transcend_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.TRANSCEND], context)
        
        # Fallback if prompt rendering fails
        if not transcend_prompt:
            logging.warning("Failed to render TRANSCEND phase prompt template, using fallback prompt")
            
            # Need a new methodology to transcend
            if not self.spiral_state.methodology_evolution:
                return None
            
            # Get the most recent methodology
            latest_methodology = self.spiral_state.methodology_evolution[-1]
            
            # Create a fallback transcendence prompt
            transcend_prompt = f"Apply this new creative methodology:\n\n{latest_methodology.evolution_rationale}\n\n"
            transcend_prompt += f"To generate a revolutionary solution to the problem: {self.spiral_state.problem_space}\n\n"
            transcend_prompt += "Generate an idea that transcends conventional frameworks and even pushes beyond impossibility enforcement "
            transcend_prompt += "and cognitive dissonance amplification. The idea should shock even those familiar with these approaches."
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=transcend_prompt,
            thinking_budget=16000,
            max_tokens=4000
        )
        
        # Add to thinking history
        self.spiral_state.thinking_history.append(thinking_step)
        
        # Extract transcend_phase_output from thinking process
        transcend_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "transcend_phase_output")
        if not transcend_phase_output:
            transcend_phase_output = thinking_step.reasoning_process
        
        # Store the output for future phases
        self.phase_outputs[SpiralPhase.TRANSCEND] = transcend_phase_output
        
        # Extract content sections
        meta_paradigms = self._extract_tagged_content(transcend_phase_output, "meta_paradigms")
        trans_categorical = self._extract_tagged_content(transcend_phase_output, "trans_categorical_approaches")
        beyond_creativity = self._extract_tagged_content(transcend_phase_output, "beyond_creativity")
        
        # Combine into a transcendent description
        description = ""
        if meta_paradigms:
            description += "Meta-Paradigms: " + meta_paradigms
        if trans_categorical:
            if description:
                description += "\n\n"
            description += "Trans-Categorical Approaches: " + trans_categorical
        if beyond_creativity:
            if description:
                description += "\n\n"
            description += "Beyond Creativity: " + beyond_creativity
        
        # If we couldn't extract structured content, use the whole output
        if not description:
            description = transcend_phase_output[:1000] + ("..." if len(transcend_phase_output) > 1000 else "")
        
        # Get the framework name from methodology history
        framework_name = "transcendent_methodology"
        if self.methodology_history:
            framework_name = self.methodology_history[-1] + "_transcended"
        
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
            generative_framework=framework_name,
            domain=domain,
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
        # We need outputs from all previous phases
        if not self.phase_outputs[SpiralPhase.CREATE] or \
           not self.phase_outputs[SpiralPhase.REFLECT] or \
           not self.phase_outputs[SpiralPhase.ABSTRACT] or \
           not self.phase_outputs[SpiralPhase.EVOLVE] or \
           not self.phase_outputs[SpiralPhase.TRANSCEND]:
            logging.warning("Cannot execute RETURN phase without outputs from previous phases")
            return None
        
        # Extract domain
        domain = self.spiral_state.problem_space.split()[0] if self.spiral_state.problem_space else "general"
        
        # Render the return phase prompt template
        context = {
            "domain": domain,
            "problem_statement": self.spiral_state.problem_space,
            "create_phase_output": self.phase_outputs[SpiralPhase.CREATE],
            "reflect_phase_output": self.phase_outputs[SpiralPhase.REFLECT],
            "abstract_phase_output": self.phase_outputs[SpiralPhase.ABSTRACT],
            "evolve_phase_output": self.phase_outputs[SpiralPhase.EVOLVE],
            "transcend_phase_output": self.phase_outputs[SpiralPhase.TRANSCEND],
            "creative_state": self._get_creative_state_summary()
        }
        
        return_prompt = self.prompt_loader.render_prompt(self.phase_prompts[SpiralPhase.RETURN], context)
        
        # Fallback if prompt rendering fails
        if not return_prompt:
            logging.warning("Failed to render RETURN phase prompt template, using fallback prompt")
            
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
            
            # Create a fallback return prompt
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
        
        # Extract return_phase_output from thinking process
        return_phase_output = self._extract_tagged_content(thinking_step.reasoning_process, "return_phase_output")
        if not return_phase_output:
            return_phase_output = thinking_step.reasoning_process
        
        # Store the output
        self.phase_outputs[SpiralPhase.RETURN] = return_phase_output
        
        # Extract content sections
        practical_applications = self._extract_tagged_content(return_phase_output, "practical_applications")
        implementation_steps = self._extract_tagged_content(return_phase_output, "implementation_steps")
        final_synthesis = self._extract_tagged_content(return_phase_output, "final_synthesis")
        
        # Combine into a return description
        description = ""
        if practical_applications:
            description += "Practical Applications: " + practical_applications
        if implementation_steps:
            if description:
                description += "\n\n"
            description += "Implementation Steps: " + implementation_steps
        if final_synthesis:
            if description:
                description += "\n\n"
            description += "Final Synthesis: " + final_synthesis
        
        # If we couldn't extract structured content, use the whole output
        if not description:
            description = return_phase_output[:1000] + ("..." if len(return_phase_output) > 1000 else "")
        
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
            domain=domain,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        # Reset phase outputs for next iteration
        # Do not reset in advance_spiral to allow for inspection of outputs
        if self.current_phase == SpiralPhase.RETURN:
            self.phase_outputs = {phase: None for phase in SpiralPhase}
        
        return return_idea
    
    def get_current_state(self) -> SpiralState:
        """Get the current spiral state."""
        if not self.spiral_state:
            raise ValueError("Spiral must be initialized first")
        return self.spiral_state
    
    def _get_creative_state_summary(self) -> str:
        """
        Generate a summary of the current creative state for use in prompts.
        
        Returns:
            str: A summary of the current creative state
        """
        if not self.spiral_state:
            return "No creative process has been initialized yet."
        
        # Calculate indicators to ensure they're up to date
        indicators = self.calculate_emergence_indicators()
        
        # Build a summary
        summary = []
        
        # Basic state info
        summary.append(f"Current Phase: {self.spiral_state.current_phase}")
        summary.append(f"Iteration Count: {self.iteration_count}")
        
        # Ideas generated
        summary.append(f"Ideas Generated: {len(self.spiral_state.generated_ideas)}")
        
        # Recent ideas
        if self.spiral_state.generated_ideas:
            summary.append("\nRecent Ideas:")
            for i, idea in enumerate(self.spiral_state.generated_ideas[-3:]):
                summary.append(f"- {idea.description[:100]}..." if len(idea.description) > 100 else f"- {idea.description}")
        
        # Methodology evolution
        if self.spiral_state.methodology_evolution:
            summary.append("\nMethodology Evolution:")
            latest = self.spiral_state.methodology_evolution[-1]
            summary.append(f"- From {latest.previous_methodology} to {latest.new_methodology}")
        
        # Emergence indicators
        if indicators:
            summary.append("\nEmergence Indicators:")
            for name, value in indicators.items():
                summary.append(f"- {name}: {value:.2f}")
        
        return "\n".join(summary)
    
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