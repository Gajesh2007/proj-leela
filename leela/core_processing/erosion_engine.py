"""
Erosion Perspective Engine - Implements time-as-creative-force algorithms inspired by geological erosion.

This module provides an alternative metaphor for creativity based on erosion processes,
where ideas evolve through persistent application of simple forces over time.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
import asyncio
import random
from datetime import datetime
from pydantic import UUID4
from enum import Enum, auto
import logging
import copy

from ..config import get_config
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..prompt_management.prompt_loader import PromptLoader
from ..prompt_management import uses_prompt
from ..knowledge_representation.models import (
    Concept, CreativeIdea, ShockProfile
)


class ErosionForce(Enum):
    """Types of erosion forces that can be applied to concepts."""
    WATER = auto()   # Fluid, persistent, finds path of least resistance
    WIND = auto()    # Subtle, widespread, gradual impact
    ICE = auto()     # Expansion in constraints, forceful
    HEAT = auto()    # Breaking down through intensity
    CHEMICAL = auto() # Transformation through interaction
    BIOLOGICAL = auto() # Living processes that break down


class ErosionPattern(Enum):
    """Patterns that emerge from erosion processes."""
    CANYON = auto()   # Deep cut through persistent force
    DELTA = auto()    # Build-up of deposited material
    CAVE = auto()     # Hidden spaces created by dissolution
    MEANDERING = auto() # Path that changes over time
    WEATHERING = auto() # Surface degradation revealing layers


class ErosionTimeframe(Enum):
    """Timeframes for erosion processes."""
    INSTANT = auto()      # Immediate, catastrophic
    SHORT_TERM = auto()   # Days to years
    MEDIUM_TERM = auto()  # Decades to centuries
    LONG_TERM = auto()    # Millennia
    GEOLOGICAL = auto()   # Millions of years


class ErodedConcept:
    """
    Represents a concept undergoing erosion forces over time.
    
    This class tracks the original concept and its transformations
    through various erosion stages.
    """
    
    def __init__(self, 
                concept: Concept,
                erosion_profile: Optional[Dict[str, Any]] = None):
        """
        Initialize an eroded concept.
        
        Args:
            concept: The original concept to erode.
            erosion_profile: Optional initial erosion profile.
        """
        self.id = uuid.uuid4()
        self.original_concept = concept
        self.current_state = copy.deepcopy(concept)
        self.creation_time = datetime.now()
        self.last_erosion = self.creation_time
        
        # Initialize erosion profile
        self.erosion_profile = erosion_profile or {
            "forces": {},
            "patterns": {},
            "timeframes": {},
            "erosion_stages": []
        }
    
    def add_erosion_stage(self, 
                        force: ErosionForce,
                        pattern: ErosionPattern,
                        timeframe: ErosionTimeframe,
                        description: str,
                        eroded_definition: str) -> None:
        """
        Add an erosion stage to the concept.
        
        Args:
            force: The erosion force applied.
            pattern: The pattern that emerged.
            timeframe: The timeframe of the erosion.
            description: Description of the erosion process.
            eroded_definition: The new definition after erosion.
        """
        # Update the current state
        self.current_state.definition = eroded_definition
        
        # Add to erosion profile forces
        force_name = force.name
        self.erosion_profile["forces"][force_name] = self.erosion_profile["forces"].get(force_name, 0) + 1
        
        # Add to erosion profile patterns
        pattern_name = pattern.name
        self.erosion_profile["patterns"][pattern_name] = self.erosion_profile["patterns"].get(pattern_name, 0) + 1
        
        # Add to erosion profile timeframes
        timeframe_name = timeframe.name
        self.erosion_profile["timeframes"][timeframe_name] = self.erosion_profile["timeframes"].get(timeframe_name, 0) + 1
        
        # Add stage to erosion history
        stage = {
            "timestamp": datetime.now().isoformat(),
            "force": force.name,
            "pattern": pattern.name,
            "timeframe": timeframe.name,
            "description": description,
            "eroded_definition": eroded_definition
        }
        self.erosion_profile["erosion_stages"].append(stage)
        
        # Update last erosion time
        self.last_erosion = datetime.now()
    
    def get_dominant_force(self) -> Optional[str]:
        """
        Get the dominant erosion force applied to this concept.
        
        Returns:
            Optional[str]: The name of the dominant force, or None if no forces applied.
        """
        forces = self.erosion_profile["forces"]
        if not forces:
            return None
        
        return max(forces.items(), key=lambda x: x[1])[0]
    
    def get_dominant_pattern(self) -> Optional[str]:
        """
        Get the dominant erosion pattern that emerged.
        
        Returns:
            Optional[str]: The name of the dominant pattern, or None if no patterns emerged.
        """
        patterns = self.erosion_profile["patterns"]
        if not patterns:
            return None
        
        return max(patterns.items(), key=lambda x: x[1])[0]
    
    def get_erosion_stages(self) -> List[Dict[str, Any]]:
        """
        Get all erosion stages applied to this concept.
        
        Returns:
            List[Dict[str, Any]]: The list of erosion stages.
        """
        return self.erosion_profile["erosion_stages"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the eroded concept to a dictionary.
        
        Returns:
            Dict[str, Any]: The eroded concept as a dictionary.
        """
        return {
            "id": str(self.id),
            "original_concept": {
                "id": str(self.original_concept.id),
                "name": self.original_concept.name,
                "domain": self.original_concept.domain,
                "definition": self.original_concept.definition
            },
            "current_state": {
                "id": str(self.current_state.id),
                "name": self.current_state.name,
                "domain": self.current_state.domain,
                "definition": self.current_state.definition
            },
            "creation_time": self.creation_time.isoformat(),
            "last_erosion": self.last_erosion.isoformat(),
            "erosion_profile": self.erosion_profile
        }


@uses_prompt("erosion_force", dependencies=["erosion_pattern", "erosion_timeframe"])
class ErosionEngine:
    """
    Implements time-as-creative-force algorithms inspired by geological erosion.
    
    This class models creativity as a process similar to geological erosion:
    - Persistent application of simple forces over time
    - Forces that reveal underlying structures
    - Processes that deposit material in new formations
    - Transformation through patient, persistent change
    
    Depends on prompts: erosion_force.txt, erosion_pattern.txt, erosion_timeframe.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the erosion engine.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.prompt_loader = PromptLoader()
        
        # Track eroded concepts
        self.eroded_concepts: Dict[UUID4, ErodedConcept] = {}
        
        # Configure force descriptions
        self.force_descriptions = {
            ErosionForce.WATER: (
                "Like flowing water, this force follows the path of least resistance, "
                "persistently wearing away at surfaces over time. It finds and exploits "
                "weaknesses, creating channels and revealing underlying structures."
            ),
            ErosionForce.WIND: (
                "Like wind, this force works subtly across broad areas, gradually "
                "reshaping exposed surfaces. It removes loose material and deposits "
                "it elsewhere, creating new formations."
            ),
            ErosionForce.ICE: (
                "Like freezing water, this force works through expansion within "
                "constraints. It exploits cracks and fissures, wedging them apart "
                "with tremendous pressure to fragment larger structures."
            ),
            ErosionForce.HEAT: (
                "Like intense heat, this force breaks down structures through thermal "
                "stress. It causes expansion, contraction, and transformation of "
                "material properties, fundamentally altering composition."
            ),
            ErosionForce.CHEMICAL: (
                "Like acid rain or oxidation, this force transforms through chemical "
                "interaction. It dissolves certain elements while leaving others intact, "
                "creating selective patterns of decay."
            ),
            ErosionForce.BIOLOGICAL: (
                "Like lichens or root systems, this force works through living processes. "
                "It breaks down structures through organic activity, creating symbiotic "
                "relationships with what it erodes."
            )
        }
        
        # Configure pattern descriptions
        self.pattern_descriptions = {
            ErosionPattern.CANYON: (
                "Like a river canyon, this pattern creates a deep, narrow cut through "
                "persistent application of force in one direction. It reveals layers "
                "and structures not visible from the surface."
            ),
            ErosionPattern.DELTA: (
                "Like a river delta, this pattern accumulates deposited material in new "
                "formations. It builds up gradually through layering and settlement, "
                "creating fertile ground for new growth."
            ),
            ErosionPattern.CAVE: (
                "Like a limestone cave, this pattern creates hidden spaces through "
                "dissolution and removal. It forms internal structures with unique "
                "properties, revealing what was previously unseen."
            ),
            ErosionPattern.MEANDERING: (
                "Like a meandering river, this pattern follows a path that changes "
                "over time. It explores different routes, sometimes doubling back "
                "on itself, creating a winding journey."
            ),
            ErosionPattern.WEATHERING: (
                "Like rock weathering, this pattern gradually degrades exposed surfaces, "
                "revealing layers beneath. It creates texture and character through "
                "the exposure of internal composition."
            )
        }
        
        # Configure timeframe descriptions
        self.timeframe_descriptions = {
            ErosionTimeframe.INSTANT: (
                "Like a flash flood or landslide, this timeframe represents immediate, "
                "catastrophic change. It transforms rapidly through intense force, "
                "creating sudden, dramatic results."
            ),
            ErosionTimeframe.SHORT_TERM: (
                "Like seasonal flooding, this timeframe operates over days to years. "
                "It creates visible changes within human timeframes, with effects "
                "that can be directly observed."
            ),
            ErosionTimeframe.MEDIUM_TERM: (
                "Like river migration, this timeframe spans decades to centuries. "
                "It works beyond a single human lifetime, creating changes that "
                "span generations."
            ),
            ErosionTimeframe.LONG_TERM: (
                "Like mountain erosion, this timeframe extends over millennia. "
                "It transforms landscapes completely, operating at a pace "
                "that makes change imperceptible to humans."
            ),
            ErosionTimeframe.GEOLOGICAL: (
                "Like continental drift, this timeframe spans millions of years. "
                "It works at the scale of entire geological epochs, fundamentally "
                "reshaping environments and ecosystems."
            )
        }
    
    def register_concept(self, concept: Concept) -> UUID4:
        """
        Register a concept for erosion processing.
        
        Args:
            concept: The concept to register.
            
        Returns:
            UUID4: The ID of the registered eroded concept.
        """
        eroded = ErodedConcept(concept)
        self.eroded_concepts[eroded.id] = eroded
        return eroded.id
    
    def get_eroded_concept(self, concept_id: UUID4) -> Optional[ErodedConcept]:
        """
        Get an eroded concept by ID.
        
        Args:
            concept_id: The ID of the eroded concept.
            
        Returns:
            Optional[ErodedConcept]: The eroded concept, or None if not found.
        """
        return self.eroded_concepts.get(concept_id)
    
    async def apply_erosion(self,
                         concept_id: UUID4,
                         force: Optional[ErosionForce] = None,
                         pattern: Optional[ErosionPattern] = None,
                         timeframe: Optional[ErosionTimeframe] = None) -> bool:
        """
        Apply an erosion force to a concept.
        
        Args:
            concept_id: The ID of the eroded concept.
            force: Optional specific erosion force to apply. If None, one is chosen randomly.
            pattern: Optional specific erosion pattern to apply. If None, one is chosen.
            timeframe: Optional specific timeframe to apply. If None, one is chosen.
            
        Returns:
            bool: True if erosion was applied successfully, False otherwise.
        """
        eroded = self.get_eroded_concept(concept_id)
        if not eroded:
            return False
        
        # Choose random force, pattern, and timeframe if not specified
        force = force or random.choice(list(ErosionForce))
        pattern = pattern or random.choice(list(ErosionPattern))
        timeframe = timeframe or random.choice(list(ErosionTimeframe))
        
        # Get descriptions
        force_desc = self.force_descriptions.get(force, "Unknown force")
        pattern_desc = self.pattern_descriptions.get(pattern, "Unknown pattern")
        timeframe_desc = self.timeframe_descriptions.get(timeframe, "Unknown timeframe")
        
        # Apply erosion using the prompt
        eroded_definition, description = await self._apply_erosion_force(
            concept=eroded.current_state,
            original_concept=eroded.original_concept,
            force=force,
            pattern=pattern,
            timeframe=timeframe,
            force_desc=force_desc,
            pattern_desc=pattern_desc,
            timeframe_desc=timeframe_desc
        )
        
        # Update the eroded concept
        eroded.add_erosion_stage(
            force=force,
            pattern=pattern,
            timeframe=timeframe,
            description=description,
            eroded_definition=eroded_definition
        )
        
        return True
    
    async def erode_concept(self,
                         concept: Concept,
                         erosion_stages: int = 3) -> ErodedConcept:
        """
        Erode a concept through multiple stages.
        
        Args:
            concept: The concept to erode.
            erosion_stages: Number of erosion stages to apply.
            
        Returns:
            ErodedConcept: The eroded concept after all stages.
        """
        # Register the concept
        concept_id = self.register_concept(concept)
        
        # Apply multiple erosion stages
        for _ in range(erosion_stages):
            # Choose random force, pattern, and timeframe
            force = random.choice(list(ErosionForce))
            pattern = random.choice(list(ErosionPattern))
            timeframe = random.choice(list(ErosionTimeframe))
            
            # Apply erosion
            await self.apply_erosion(
                concept_id=concept_id,
                force=force,
                pattern=pattern,
                timeframe=timeframe
            )
        
        # Return the eroded concept
        return self.get_eroded_concept(concept_id)
    
    async def generate_idea_from_erosion(self,
                                     eroded_concept: ErodedConcept,
                                     problem_statement: str) -> CreativeIdea:
        """
        Generate a creative idea from an eroded concept.
        
        Args:
            eroded_concept: The eroded concept to generate an idea from.
            problem_statement: The problem statement to address.
            
        Returns:
            CreativeIdea: The generated creative idea.
        """
        # Extract domain
        domain = eroded_concept.current_state.domain
        
        # Get erosion history
        erosion_stages = eroded_concept.get_erosion_stages()
        dominant_force = eroded_concept.get_dominant_force()
        dominant_pattern = eroded_concept.get_dominant_pattern()
        
        # Generate idea from eroded concept
        idea_description = await self._generate_idea_from_erosion(
            original_concept=eroded_concept.original_concept,
            eroded_concept=eroded_concept.current_state,
            dominant_force=dominant_force,
            dominant_pattern=dominant_pattern,
            erosion_stages=erosion_stages,
            problem_statement=problem_statement,
            domain=domain
        )
        
        # Create shock profile for the idea
        shock_profile = ShockProfile(
            novelty_score=0.8,
            contradiction_score=0.7,
            impossibility_score=0.75,
            utility_potential=0.7,
            expert_rejection_probability=0.7,
            composite_shock_value=0.75
        )
        
        # Create the creative idea
        idea = CreativeIdea(
            id=uuid.uuid4(),
            description=idea_description,
            generative_framework="erosion_engine",
            domain=domain,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return idea
    
    async def _apply_erosion_force(self,
                                concept: Concept,
                                original_concept: Concept,
                                force: ErosionForce,
                                pattern: ErosionPattern,
                                timeframe: ErosionTimeframe,
                                force_desc: str,
                                pattern_desc: str,
                                timeframe_desc: str) -> Tuple[str, str]:
        """
        Apply an erosion force to a concept using the erosion_force prompt.
        
        Args:
            concept: The current concept state to erode.
            original_concept: The original concept before any erosion.
            force: The erosion force to apply.
            pattern: The erosion pattern to apply.
            timeframe: The erosion timeframe to apply.
            force_desc: Description of the force.
            pattern_desc: Description of the pattern.
            timeframe_desc: Description of the timeframe.
            
        Returns:
            Tuple[str, str]: The eroded definition and a description of the erosion process.
        """
        # Render the erosion force prompt template
        context = {
            "concept_name": concept.name,
            "concept_definition": concept.definition,
            "original_definition": original_concept.definition,
            "domain": concept.domain,
            "force": force.name,
            "force_description": force_desc,
            "pattern": pattern.name,
            "pattern_description": pattern_desc,
            "timeframe": timeframe.name,
            "timeframe_description": timeframe_desc
        }
        
        erosion_prompt = self.prompt_loader.render_prompt("erosion_force", context)
        
        # Fallback if prompt rendering fails
        if not erosion_prompt:
            logging.warning("Failed to render erosion_force prompt template, using fallback prompt")
            
            erosion_prompt = f"""
            Apply erosion forces to transform this concept:

            Concept Name: {concept.name}
            Domain: {concept.domain}

            Current Definition:
            {concept.definition}

            Original Definition:
            {original_concept.definition}

            Erosion Force: {force.name}
            {force_desc}

            Erosion Pattern: {pattern.name}
            {pattern_desc}

            Timeframe: {timeframe.name}
            {timeframe_desc}

            Transform the concept definition by applying these erosion forces, patterns, and timeframes. 
            Consider how the concept would change if subjected to these natural processes over time.

            Return your response with <eroded_definition> tags around the new definition and <erosion_description> tags around a description of the erosion process.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=erosion_prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract the eroded definition and description
        eroded_def = self._extract_tagged_content(thinking_step.reasoning_process, "eroded_definition")
        erosion_desc = self._extract_tagged_content(thinking_step.reasoning_process, "erosion_description")
        
        # Fallbacks if extraction fails
        if not eroded_def:
            # Look for any substantial paragraph in the response
            paragraphs = [p.strip() for p in thinking_step.reasoning_process.split("\n\n") if p.strip()]
            if paragraphs:
                eroded_def = paragraphs[-1]  # Take the last paragraph
            else:
                eroded_def = thinking_step.reasoning_process[-500:]  # Take the last 500 chars
        
        if not erosion_desc:
            # Take a middle paragraph if available
            paragraphs = [p.strip() for p in thinking_step.reasoning_process.split("\n\n") if p.strip()]
            if len(paragraphs) > 1:
                erosion_desc = paragraphs[len(paragraphs) // 2]
            else:
                erosion_desc = f"Applied {force.name} erosion with a {pattern.name} pattern over a {timeframe.name} timeframe."
        
        return eroded_def, erosion_desc
    
    async def _generate_idea_from_erosion(self,
                                      original_concept: Concept,
                                      eroded_concept: Concept,
                                      dominant_force: Optional[str],
                                      dominant_pattern: Optional[str],
                                      erosion_stages: List[Dict[str, Any]],
                                      problem_statement: str,
                                      domain: str) -> str:
        """
        Generate a creative idea from an eroded concept using the erosion_pattern prompt.
        
        Args:
            original_concept: The original concept before erosion.
            eroded_concept: The current eroded concept.
            dominant_force: The dominant erosion force.
            dominant_pattern: The dominant erosion pattern.
            erosion_stages: List of erosion stages.
            problem_statement: The problem statement to address.
            domain: The domain of the problem.
            
        Returns:
            str: The generated idea description.
        """
        # Build erosion history text
        erosion_history = []
        for i, stage in enumerate(erosion_stages):
            erosion_history.append(f"Stage {i+1}: {stage['force']} force with {stage['pattern']} pattern over {stage['timeframe']} timeframe")
            erosion_history.append(f"Description: {stage['description']}")
            erosion_history.append("")
        
        erosion_history_text = "\n".join(erosion_history)
        
        # Render the erosion pattern prompt template
        context = {
            "concept_name": eroded_concept.name,
            "original_definition": original_concept.definition,
            "eroded_definition": eroded_concept.definition,
            "domain": domain,
            "problem_statement": problem_statement,
            "dominant_force": dominant_force or "NONE",
            "dominant_pattern": dominant_pattern or "NONE",
            "erosion_history": erosion_history_text
        }
        
        idea_prompt = self.prompt_loader.render_prompt("erosion_pattern", context)
        
        # Fallback if prompt rendering fails
        if not idea_prompt:
            logging.warning("Failed to render erosion_pattern prompt template, using fallback prompt")
            
            idea_prompt = f"""
            Generate a creative idea based on this eroded concept:

            Concept Name: {eroded_concept.name}
            Domain: {domain}

            Original Definition:
            {original_concept.definition}

            Eroded Definition:
            {eroded_concept.definition}

            Problem Statement:
            {problem_statement}

            Dominant Erosion Force: {dominant_force or "NONE"}
            Dominant Erosion Pattern: {dominant_pattern or "NONE"}

            Erosion History:
            {erosion_history_text}

            Based on this eroded concept and its transformation history, generate a creative solution to the problem statement.
            Consider how the erosion process has revealed new aspects of the concept that might address the problem in novel ways.

            Return your response with <idea> tags around the creative idea description.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=idea_prompt,
            thinking_budget=12000,
            max_tokens=3000
        )
        
        # Extract the idea
        idea = self._extract_tagged_content(thinking_step.reasoning_process, "idea")
        
        # Fallback if extraction fails
        if not idea:
            # Look for any substantial paragraph in the response
            paragraphs = [p.strip() for p in thinking_step.reasoning_process.split("\n\n") if p.strip() and len(p) > 100]
            if paragraphs:
                idea = paragraphs[-1]  # Take the last substantial paragraph
            else:
                idea = thinking_step.reasoning_process[-1000:]  # Take the last 1000 chars
        
        return idea
    
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


async def generate_eroded_idea(
    problem_statement: str,
    domain: str,
    concept: Concept,
    erosion_stages: int = 3
) -> CreativeIdea:
    """
    Generate a creative idea using the erosion engine.
    
    Args:
        problem_statement: Problem statement to address.
        domain: Domain of the problem.
        concept: Concept to erode.
        erosion_stages: Number of erosion stages to apply.
        
    Returns:
        CreativeIdea: The generated creative idea.
    """
    # Create the erosion engine
    engine = ErosionEngine()
    
    # Erode the concept
    eroded_concept = await engine.erode_concept(
        concept=concept,
        erosion_stages=erosion_stages
    )
    
    # Generate idea from eroded concept
    idea = await engine.generate_idea_from_erosion(
        eroded_concept=eroded_concept,
        problem_statement=problem_statement
    )
    
    # Set the domain
    if not idea.domain:
        idea.domain = domain
    
    return idea