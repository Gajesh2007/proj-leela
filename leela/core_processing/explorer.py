"""
Explorer Module - Navigates probability fields of potential solutions through multi-perspective exploration.

Implements prompts: explorer_agent_radical.txt, explorer_agent_conservative.txt, explorer_agent_alien.txt, explorer_agent_future.txt, explorer_synthesis.txt, temporal_framework_ancient.txt, temporal_framework_quantum.txt
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from pydantic import UUID4
from enum import Enum
from ..config import get_config
from ..knowledge_representation.models import (
    CreativeIdea, ThinkingStep, ShockProfile
)
from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..prompt_management import uses_prompt


class PerspectiveType(Enum):
    """Types of perspectives for multi-agent dialectic."""
    RADICAL = "radical"  # Challenges all assumptions
    CONSERVATIVE = "conservative"  # Preserves useful patterns
    ALIEN = "alien"  # Non-human viewpoints
    ANCIENT = "ancient"  # Historical perspectives
    FUTURE = "future"  # Beyond current paradigms
    SYNTHESIS = "synthesis"  # Identifies connections
    ANTI_SYNTHESIS = "anti_synthesis"  # Maintains tensions


@uses_prompt("explorer_synthesis", dependencies=["explorer_agent_radical", "explorer_agent_conservative", "explorer_agent_alien", "explorer_agent_future", "dialectic_synthesis"])
class MultiAgentDialecticSystem:
    """
    Creates dialogues between opposing perspectives.
    
    This class implements the explorer_synthesis.txt prompt and multiple agent prompts to
    generate ideas from different perspectives and synthesize them into novel approaches.
    
    Depends on prompts: explorer_agent_radical.txt, explorer_agent_conservative.txt, 
    explorer_agent_alien.txt, explorer_agent_future.txt, dialectic_synthesis.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Multi-Agent Dialectic System.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.thinking_manager = ExtendedThinkingManager(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Perspective descriptions
        self.perspective_descriptions = {
            PerspectiveType.RADICAL: (
                "You fundamentally question all assumptions about the problem. "
                "Consider approaches that experts would dismiss as impossible. "
                "Deliberately invert conventional wisdom and established paradigms. "
                "Your goal is to propose an approach that violates core assumptions in the domain."
            ),
            PerspectiveType.CONSERVATIVE: (
                "You value established wisdom and proven approaches. "
                "Look for how conventional methods might be adapted rather than abandoned. "
                "Consider evolutionary rather than revolutionary changes. "
                "Your goal is to propose an approach that builds on solid foundations while addressing the challenge."
            ),
            PerspectiveType.ALIEN: (
                "You have a completely non-human perspective, free from anthropocentric biases. "
                "Consider the problem from a radically different cognitive framework. "
                "Imagine how an intelligence with different sensory and conceptual systems would approach this. "
                "Your goal is to propose an approach that no human would naturally consider."
            ),
            PerspectiveType.ANCIENT: (
                "You view the problem through historical frameworks from ancient civilizations. "
                "Draw on wisdom traditions and approaches from at least 1000 years ago. "
                "Consider how the problem would be conceptualized before modern paradigms existed. "
                "Your goal is to propose an approach that recovers lost ways of thinking."
            ),
            PerspectiveType.FUTURE: (
                "You view the problem from 1000 years in the future, where today's paradigms seem primitive. "
                "Consider approaches that depend on conceptual frameworks not yet developed. "
                "Imagine how the problem would be framed after multiple paradigm shifts. "
                "Your goal is to propose an approach from beyond the current intellectual horizon."
            ),
            PerspectiveType.SYNTHESIS: (
                "You identify hidden connections and unity where others see only differences. "
                "Look for ways to integrate apparently opposing perspectives. "
                "Seek reconciliation of contradictions through higher-order frameworks. "
                "Your goal is to propose an approach that creates unexpected harmony from discord."
            ),
            PerspectiveType.ANTI_SYNTHESIS: (
                "You deliberately maintain creative tensions and contradictions. "
                "Resist premature resolution or simplification of complex problems. "
                "Preserve paradoxes rather than resolving them. "
                "Your goal is to propose an approach that derives power from unresolved contradictions."
            )
        }
    
    async def generate_perspectives(self, 
                                 problem_statement: str, 
                                 domain: str,
                                 perspective_types: List[PerspectiveType],
                                 thinking_budget: int = 16000) -> Tuple[List[ThinkingStep], List[str]]:
        """
        Generate thinking from multiple perspectives.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspective_types: List of perspective types to use
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Tuple[List[ThinkingStep], List[str]]: Thinking steps and perspective ideas
        """
        # Create prompts for each perspective
        prompts = []
        for perspective_type in perspective_types:
            perspective_desc = self.perspective_descriptions[perspective_type]
            prompt = self._create_perspective_prompt(problem_statement, domain, perspective_type.value, perspective_desc)
            prompts.append(prompt)
        
        # Generate thinking from multiple perspectives
        thinking_steps = await self.thinking_manager.dialectic_thinking(
            prompt=f"Solve this problem in {domain}: {problem_statement}",
            perspectives=[self._create_short_perspective_desc(pt) for pt in perspective_types],
            thinking_budget=thinking_budget,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract ideas from thinking steps
        perspective_ideas = []
        for step in thinking_steps:
            # Extract idea from thinking
            idea = self._extract_idea_description(step.reasoning_process)
            perspective_ideas.append(idea)
        
        return thinking_steps, perspective_ideas
    
    def _create_perspective_prompt(self, problem_statement: str, domain: str, 
                               perspective_name: str, perspective_desc: str) -> str:
        """
        Create a prompt for a specific perspective.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspective_name: Name of the perspective
            perspective_desc: Description of the perspective
            
        Returns:
            str: The perspective prompt
        """
        # Use the prompt_loader to get the appropriate perspective prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Determine which prompt template to use based on perspective name
        prompt_template_map = {
            "radical": "explorer_agent_radical",
            "conservative": "explorer_agent_conservative",
            "alien": "explorer_agent_alien",
            "future": "explorer_agent_future"
        }
        
        prompt_template = prompt_template_map.get(perspective_name.lower())
        
        if prompt_template:
            # Use the specific perspective prompt template
            prompt = prompt_loader.render_prompt(
                prompt_template,
                {
                    "domain": domain,
                    "problem_statement": problem_statement
                }
            )
            
            if not prompt:
                # Fallback in case prompt loading fails
                raise ValueError(f"Failed to load {prompt_template} prompt template")
        else:
            # If no specific template is available, use a generic format
            prompt = f"""Problem in {domain}: {problem_statement}

You are the {perspective_name.upper()} AGENT in a multi-agent dialectic system.

{perspective_desc}

Generate a solution to the problem from your unique perspective. Be true to your perspective's fundamental assumptions rather than moderating your approach to make it more conventional.

Think step by step, explaining how your perspective reveals insights and approaches that would be invisible from conventional viewpoints."""
        
        return prompt
    
    def _create_short_perspective_desc(self, perspective_type: PerspectiveType) -> str:
        """
        Create a short description for a perspective type.
        
        Args:
            perspective_type: The perspective type
            
        Returns:
            str: Short description
        """
        name = perspective_type.value.capitalize()
        desc = self.perspective_descriptions[perspective_type].split(".")[0] + "."
        return f"{name} Agent: {desc}"
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract idea description from thinking text.
        Looks for content between various tag types, or falls back to heuristics.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted idea description
        """
        # Tags to check in order of preference
        tag_pairs = [
            ("<synthesis>", "</synthesis>"),   # For dialectic_synthesis_integration
            ("<final_idea>", "</final_idea>"), # For dialectic_synthesis
            ("<revolutionary_idea>", "</revolutionary_idea>"), # For impossibility_enforcer
            ("<idea>", "</idea>")            # Generic fallback
        ]
        
        for start_tag, end_tag in tag_pairs:
            idea_start = thinking_text.find(start_tag)
            idea_end = thinking_text.find(end_tag)
            
            if idea_start != -1 and idea_end != -1:
                # Extract content between tags
                idea_start += len(start_tag)
                return thinking_text[idea_start:idea_end].strip()
        
        # Fallback to previous method if tags not found
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "My solution", "The idea is", 
            "Proposed approach", "Final solution", "My proposal"
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
    
    async def synthesize_perspectives(self, 
                                   problem_statement: str, 
                                   domain: str,
                                   perspective_ideas: List[str],
                                   perspective_types: List[PerspectiveType],
                                   thinking_budget: int = 16000) -> Tuple[ThinkingStep, str]:
        """
        Synthesize multiple perspectives into a unified approach.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspective_ideas: Ideas from different perspectives
            perspective_types: Types of perspectives used
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Tuple[ThinkingStep, str]: Synthesis thinking step and synthesized idea
        """
        # Use the prompt_loader to get the explorer_synthesis prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Create perspective dictionaries for the template
        perspective_dict = {}
        for i, (idea, perspective) in enumerate(zip(perspective_ideas, perspective_types)):
            perspective_type = perspective.value.lower()
            perspective_dict[f"{perspective_type}_perspective"] = idea
        
        # Add the problem statement to the context dictionary
        perspective_dict["problem_statement"] = problem_statement
        
        # Render the prompt template with context
        synthesis_prompt = prompt_loader.render_prompt(
            "explorer_synthesis",
            perspective_dict
        )
        
        if not synthesis_prompt:
            # Fallback in case prompt loading fails
            # Create a fallback synthesis prompt
            ideas_text = ""
            for i, (idea, perspective) in enumerate(zip(perspective_ideas, perspective_types)):
                ideas_text += f"Perspective {i+1} ({perspective.value.upper()}): {idea}\n\n"
            
            synthesis_prompt = f"""Problem in {domain}: {problem_statement}

You've received these different perspectives on the problem:

{ideas_text}

Your task is to synthesize these perspectives into a unified approach. But this should not be a simple compromise or "middle ground" between perspectives.

Instead, create a dialectical synthesis that:

1. Maintains the creative tension between opposing viewpoints rather than diluting them
2. Preserves paradoxes and contradictions as features, not bugs
3. Emerges as something genuinely new, not just a combination of parts
4. Transforms the problem space itself through the interaction of perspectives
5. Creates cognitive dissonance while maintaining coherence at a higher level

Think step by step about how these different perspectives reveal different aspects of the problem, and how their interaction generates an emergent approach that transcends each individual perspective."""
        
        # Generate synthesis thinking
        synthesis_step = await self.claude_client.generate_thinking(
            prompt=synthesis_prompt,
            thinking_budget=thinking_budget,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract synthesized idea
        synthesized_idea = self._extract_idea_description(synthesis_step.reasoning_process)
        
        return synthesis_step, synthesized_idea


@uses_prompt("temporal_framework_ancient", dependencies=["temporal_framework_quantum"])
class TemporalPerspectiveShifter:
    """
    Applies historical and future viewpoints to problems.
    
    This class implements the temporal_framework_ancient.txt and temporal_framework_quantum.txt
    prompts to view problems through different historical and future frames of reference.
    
    Depends on prompt: temporal_framework_quantum.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Temporal Perspective Shifter.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Temporal eras
        self.eras = [
            "ancient", "medieval", "renaissance", "industrial", 
            "modern", "information_age", "future", "post_singularity"
        ]
        
        # Era-specific paradigms
        self.era_paradigms = {
            "ancient": (
                "Mythic-associative thinking. Metaphor and analogy as primary tools. "
                "Cyclic view of time and processes. Anthropomorphism of natural forces. "
                "Qualitative rather than quantitative understanding."
            ),
            "medieval": (
                "Authority and tradition as sources of truth. Hierarchical organization of knowledge. "
                "Symbolic and allegorical thinking. Teleological explanations. "
                "Integration of spiritual and material understanding."
            ),
            "renaissance": (
                "Empirical observation combined with classical knowledge. "
                "Perspective and proportion as organizing principles. "
                "Humanism and individual genius. "
                "Synthesis across disciplines. Direct observation over authority."
            ),
            "industrial": (
                "Mechanistic worldview. Standardization and interchangeable parts. "
                "Linear processes and progress. "
                "Reductionism and specialization. "
                "Efficiency and optimization as goals."
            ),
            "modern": (
                "Relativistic and probabilistic thinking. "
                "Systems approaches and feedback loops. "
                "Information as a fundamental quantity. "
                "Interdisciplinary collaboration. "
                "Complexity and emergence as frameworks."
            ),
            "information_age": (
                "Network-centric thinking. Distributed systems and decentralization. "
                "Nonlinear dynamics and complexity science. "
                "Digital representation and simulation. "
                "Rapid iteration and continuous evolution."
            ),
            "future": (
                "Post-scarcity economics. Integration of biological and technological systems. "
                "Quantum computing paradigms. "
                "Multi-scale optimization. "
                "Enhanced cognitive frameworks beyond current human capabilities."
            ),
            "post_singularity": (
                "Radically transformed cognition beyond current comprehension. "
                "Transcendence of biological and digital distinction. "
                "Access to effectively unlimited computational resources. "
                "Integration of previously incompatible frameworks. "
                "Simultaneous multi-paradigmatic thinking."
            )
        }
    
    async def apply_temporal_perspective(self, 
                                      problem_statement: str, 
                                      domain: str,
                                      era: str,
                                      thinking_budget: int = 16000) -> Tuple[ThinkingStep, str]:
        """
        Apply a temporal perspective to a problem.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            era: The temporal era to apply
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Tuple[ThinkingStep, str]: Thinking step and temporal perspective idea
        """
        # Use the prompt_loader to get the appropriate temporal framework prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Determine which temporal framework to use
        prompt_template = None
        if era == "ancient":
            prompt_template = "temporal_framework_ancient"
        elif era == "future" or era == "post_singularity":
            prompt_template = "temporal_framework_quantum"
        
        if prompt_template:
            # Use the specific temporal framework prompt template
            prompt = prompt_loader.render_prompt(
                prompt_template,
                {
                    "domain": domain,
                    "problem_statement": problem_statement,
                    "era": era.replace('_', ' ')
                }
            )
            
            if not prompt:
                # Fallback in case prompt loading fails
                prompt = self._create_fallback_temporal_prompt(problem_statement, domain, era)
        else:
            # If no specific template is available, use a generic format
            prompt = self._create_fallback_temporal_prompt(problem_statement, domain, era)
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=thinking_budget,
            max_tokens=4000
        )
        
        # Extract temporal perspective idea
        idea = self._extract_idea_description(thinking_step.reasoning_process)
        
        return thinking_step, idea
        
    def _create_fallback_temporal_prompt(self, problem_statement: str, domain: str, era: str) -> str:
        """
        Create a fallback temporal prompt if prompt loading fails.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            era: The temporal era to apply
            
        Returns:
            str: The temporal prompt
        """
        # Get era paradigm
        era_paradigm = self.era_paradigms.get(era, "Unknown era paradigm")
        
        # Create a temporal perspective prompt
        prompt = f"""Problem in {domain}: {problem_statement}

Apply the cognitive framework of the {era.replace('_', ' ').upper()} era to this problem.

Era characteristics:
{era_paradigm}

Imagine how this problem would be approached using the thinking patterns, tools, concepts, and paradigms of this era. Don't simply use modern concepts with period decoration - truly shift your cognitive framework to match the era.

Your solution should:
1. Reflect the fundamental weltanschauung of the {era.replace('_', ' ')} era
2. Use methodologies authentic to that time period
3. Frame the problem in terms that would make sense in that era
4. Generate solutions that emerge naturally from that era's paradigms
5. Reveal insights hidden by modern assumptions

Think step by step, exploring how the {era.replace('_', ' ')} perspective transforms the problem and opens novel solution paths."""
        
        return prompt
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract idea description from thinking text.
        Looks for content between various tag types, or falls back to heuristics.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted idea description
        """
        # Tags to check in order of preference
        tag_pairs = [
            ("<synthesis>", "</synthesis>"),   # For dialectic_synthesis_integration
            ("<final_idea>", "</final_idea>"), # For dialectic_synthesis
            ("<revolutionary_idea>", "</revolutionary_idea>"), # For impossibility_enforcer
            ("<idea>", "</idea>")            # Generic fallback
        ]
        
        for start_tag, end_tag in tag_pairs:
            idea_start = thinking_text.find(start_tag)
            idea_end = thinking_text.find(end_tag)
            
            if idea_start != -1 and idea_end != -1:
                # Extract content between tags
                idea_start += len(start_tag)
                return thinking_text[idea_start:idea_end].strip()
                
        # Fallback to previous method if none of the tag pairs were found
        
        # Fallback to previous method if tags not found
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "The solution", "My approach", 
            "Proposed solution", "Final approach", "From this perspective"
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


@uses_prompt("explorer_synthesis", dependencies=["explorer_agent_radical", "explorer_agent_conservative", "explorer_agent_alien", "explorer_agent_future", "temporal_framework_ancient", "temporal_framework_quantum"])
class ExplorerModule:
    """
    Navigates probability fields of potential solutions through multi-perspective exploration.
    
    This class coordinates the multi-agent dialectic system and temporal perspective shifting
    to explore a problem space from multiple angles and generate novel solutions.
    
    Depends on prompts: explorer_agent_radical.txt, explorer_agent_conservative.txt,
    explorer_agent_alien.txt, explorer_agent_future.txt, temporal_framework_ancient.txt,
    temporal_framework_quantum.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Explorer Module.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.dialectic_system = MultiAgentDialecticSystem(self.api_key)
        self.temporal_shifter = TemporalPerspectiveShifter(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def explore_dialectic(self, 
                             problem_statement: str, 
                             domain: str,
                             perspectives: Optional[List[PerspectiveType]] = None,
                             thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Explore a problem through dialectic between multiple perspectives.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspectives: Optional list of perspectives to use
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of exploration including perspective ideas and synthesis
        """
        # Use default perspectives if none provided
        if not perspectives:
            perspectives = [
                PerspectiveType.RADICAL,
                PerspectiveType.CONSERVATIVE,
                PerspectiveType.FUTURE,
                PerspectiveType.ANTI_SYNTHESIS
            ]
        
        # Step 1: Generate perspectives
        thinking_steps, perspective_ideas = await self.dialectic_system.generate_perspectives(
            problem_statement, domain, perspectives, thinking_budget
        )
        
        # Step 2: Synthesize perspectives
        synthesis_step, synthesized_idea = await self.dialectic_system.synthesize_perspectives(
            problem_statement, domain, perspective_ideas, perspectives, thinking_budget
        )
        
        # Step 3: Create a creative idea from synthesis
        idea = self._create_dialectic_idea(synthesized_idea, perspective_ideas, perspectives)
        
        # Add synthesis step to thinking steps
        all_thinking_steps = thinking_steps + [synthesis_step]
        
        # Create results
        results = {
            "perspective_types": [p.value for p in perspectives],
            "perspective_ideas": perspective_ideas,
            "synthesized_idea": synthesized_idea,
            "thinking_steps": all_thinking_steps,
            "idea": idea
        }
        
        return results
    
    async def explore_temporal(self, 
                            problem_statement: str, 
                            domain: str,
                            eras: Optional[List[str]] = None,
                            thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Explore a problem through temporal perspective shifting.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            eras: Optional list of eras to use
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of exploration including temporal ideas and synthesis
        """
        # Use default eras if none provided
        if not eras:
            eras = ["ancient", "renaissance", "future"]
        
        # Step 1: Apply temporal perspectives
        temporal_results = []
        for era in eras:
            thinking_step, idea = await self.temporal_shifter.apply_temporal_perspective(
                problem_statement, domain, era, thinking_budget
            )
            temporal_results.append((thinking_step, idea))
        
        # Extract thinking steps and ideas
        thinking_steps = [result[0] for result in temporal_results]
        temporal_ideas = [result[1] for result in temporal_results]
        
        # Step 2: Synthesize temporal perspectives
        synthesis_prompt = f"""Problem in {domain}: {problem_statement}

You've explored this problem through these temporal perspectives:

"""
        for i, (era, idea) in enumerate(zip(eras, temporal_ideas)):
            synthesis_prompt += f"{era.capitalize()} Era Perspective:\n{idea}\n\n"
        
        synthesis_prompt += """
Create a temporal synthesis that draws on insights from multiple eras. This synthesis should:

1. Integrate valuable elements from different temporal perspectives
2. Reveal insights that are invisible within any single temporal framework
3. Transcend the limitations of each era's paradigms
4. Create a solution that would seem both familiar and alien to each era
5. Transform the problem by viewing it through a multi-temporal lens

Think step by step about how these different temporal perspectives reveal different aspects of the problem, and how their integration generates an approach that transcends historical limitations."""
        
        # Generate synthesis thinking
        synthesis_step = await self.claude_client.generate_thinking(
            prompt=synthesis_prompt,
            thinking_budget=thinking_budget,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract synthesized temporal idea
        synthesized_idea = self._extract_idea_description(synthesis_step.reasoning_process)
        
        # Step 3: Create a creative idea from synthesis
        idea = self._create_temporal_idea(synthesized_idea, temporal_ideas, eras)
        
        # Add synthesis step to thinking steps
        all_thinking_steps = thinking_steps + [synthesis_step]
        
        # Create results
        results = {
            "eras": eras,
            "temporal_ideas": temporal_ideas,
            "synthesized_idea": synthesized_idea,
            "thinking_steps": all_thinking_steps,
            "idea": idea
        }
        
        return results
    
    def _create_dialectic_idea(self, 
                            synthesized_idea: str, 
                            perspective_ideas: List[str],
                            perspectives: List[PerspectiveType]) -> CreativeIdea:
        """
        Create a creative idea from dialectic synthesis.
        
        Args:
            synthesized_idea: The synthesized idea
            perspective_ideas: Ideas from different perspectives
            perspectives: Types of perspectives used
            
        Returns:
            CreativeIdea: The creative idea
        """
        # Create a shock profile for the dialectic idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.9,  # High because of dialectic tension
            impossibility_score=0.8,
            utility_potential=0.7,
            expert_rejection_probability=0.8,
            composite_shock_value=0.85
        )
        
        # Create a dialectic idea
        dialectic_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=synthesized_idea,
            generative_framework="dialectic_synthesis",
            impossibility_elements=[],
            contradiction_elements=[p.value for p in perspectives],  # Use perspectives as contradiction elements
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return dialectic_idea
    
    def _create_temporal_idea(self, 
                           synthesized_idea: str, 
                           temporal_ideas: List[str],
                           eras: List[str]) -> CreativeIdea:
        """
        Create a creative idea from temporal synthesis.
        
        Args:
            synthesized_idea: The synthesized idea
            temporal_ideas: Ideas from different temporal perspectives
            eras: Temporal eras used
            
        Returns:
            CreativeIdea: The creative idea
        """
        # Create a shock profile for the temporal idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.8,
            impossibility_score=0.85,  # High because of temporal impossibilities
            utility_potential=0.75,
            expert_rejection_probability=0.8,
            composite_shock_value=0.85
        )
        
        # Create a temporal idea
        temporal_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=synthesized_idea,
            generative_framework="temporal_synthesis",
            impossibility_elements=[],
            contradiction_elements=eras,  # Use eras as contradiction elements
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return temporal_idea
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract idea description from thinking text.
        Looks for content between various tag types, or falls back to heuristics.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted idea description
        """
        # Tags to check in order of preference
        tag_pairs = [
            ("<synthesis>", "</synthesis>"),   # For dialectic_synthesis_integration
            ("<final_idea>", "</final_idea>"), # For dialectic_synthesis
            ("<revolutionary_idea>", "</revolutionary_idea>"), # For impossibility_enforcer
            ("<idea>", "</idea>")            # Generic fallback
        ]
        
        for start_tag, end_tag in tag_pairs:
            idea_start = thinking_text.find(start_tag)
            idea_end = thinking_text.find(end_tag)
            
            if idea_start != -1 and idea_end != -1:
                # Extract content between tags
                idea_start += len(start_tag)
                return thinking_text[idea_start:idea_end].strip()
        
        # Fallback to previous method if tags not found
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "The synthesis", "The integrated approach", 
            "The synthesized solution", "Final synthesis", "Synthesized idea"
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