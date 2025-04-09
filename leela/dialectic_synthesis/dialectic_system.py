"""
Multi-Agent Dialectic System - Implements advanced dialectic synthesis between opposing perspectives.

This module extends the Explorer Module's perspective generation capabilities with more
sophisticated synthesis mechanisms that deliberately maintain creative tensions.
"""
from typing import Dict, List, Any, Optional, Tuple, Union
import uuid
import asyncio
from pydantic import UUID4
from enum import Enum, auto
from ..config import get_config
from ..knowledge_representation.models import (
    CreativeIdea, ThinkingStep, ShockProfile
)
from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..prompt_management.prompt_loader import PromptLoader
from ..prompt_management import uses_prompt
from ..core_processing.explorer import PerspectiveType, MultiAgentDialecticSystem


class SynthesisStrategy(Enum):
    """Types of dialectic synthesis strategies."""
    INTEGRATION = auto()  # Seeks to integrate contradictory perspectives
    TENSION_MAINTENANCE = auto()  # Deliberately maintains creative tensions
    META_PERSPECTIVE = auto()  # Creates a perspective about perspectives
    QUANTUM_SUPERPOSITION = auto()  # Holds contradictions in superposition
    IMPOSSIBILITY_FOCUS = auto()  # Focuses on impossible aspects of contradictions


@uses_prompt("dialectic_synthesis_integration", dependencies=["dialectic_synthesis"])
class DialecticSynthesisEngine:
    """
    Advanced engine for dialectic synthesis between opposing perspectives.
    
    This class extends basic synthesis capabilities to create more sophisticated
    dialectic interactions that deliberately maintain creative tensions.
    
    Depends on prompts: dialectic_synthesis.txt, dialectic_synthesis_integration.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dialectic Synthesis Engine.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.prompt_loader = PromptLoader()
        
        # Initialize the base dialectic system
        self.base_system = MultiAgentDialecticSystem(self.api_key)
        
        # Synthesis strategy configurations
        self.strategy_descriptions = {
            SynthesisStrategy.INTEGRATION: (
                "Integrate opposing perspectives into a unified whole that transcends each individual viewpoint. "
                "Look for higher-order principles that can reconcile contradictions. "
                "Create a synthesis that incorporates the strengths of each perspective while addressing their weaknesses."
            ),
            SynthesisStrategy.TENSION_MAINTENANCE: (
                "Deliberately maintain the creative tensions between opposing perspectives. "
                "Resist the urge to resolve contradictions and instead leverage them as sources of creative energy. "
                "Create a synthesis that preserves paradoxes and contradictions as features, not bugs."
            ),
            SynthesisStrategy.META_PERSPECTIVE: (
                "Develop a meta-perspective that can view the interplay of opposing perspectives. "
                "Step outside the dialectic to observe how different viewpoints interact and complement each other. "
                "Create a synthesis that reflects on the dialectic process itself."
            ),
            SynthesisStrategy.QUANTUM_SUPERPOSITION: (
                "Hold contradictory perspectives in quantum superposition. "
                "Allow multiple contradictory viewpoints to exist simultaneously without collapsing to a single state. "
                "Create a synthesis that maintains the validity of mutually exclusive perspectives."
            ),
            SynthesisStrategy.IMPOSSIBILITY_FOCUS: (
                "Focus on the aspects of the problem that all perspectives consider impossible. "
                "Identify and amplify impossibilities to generate creative breakthroughs. "
                "Create a synthesis that embraces impossibility as a creativity trigger."
            )
        }
    
    async def generate_dialectic_synthesis(self,
                                         problem_statement: str,
                                         domain: str,
                                         perspective_ideas: Dict[str, str],
                                         synthesis_strategy: SynthesisStrategy = SynthesisStrategy.TENSION_MAINTENANCE,
                                         thinking_budget: int = 16000) -> Tuple[ThinkingStep, str]:
        """
        Generate a sophisticated dialectic synthesis from multiple perspective ideas.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspective_ideas: Dictionary mapping perspective names to their ideas
            synthesis_strategy: Strategy for synthesis
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Tuple[ThinkingStep, str]: Synthesis thinking step and synthesized idea
        """
        # Render the dialectic synthesis integration prompt template
        context = {
            "domain": domain,
            "problem_statement": problem_statement,
            "perspective_ideas": [(perspective, idea) for perspective, idea in perspective_ideas.items()],
            "synthesis_strategy": synthesis_strategy.name.lower().replace('_', ' ')
        }
        
        synthesis_prompt = self.prompt_loader.render_prompt(
            "dialectic_synthesis_integration",
            context
        )
        
        if not synthesis_prompt:
            # Fallback if prompt loading fails
            synthesis_prompt = self._create_fallback_synthesis_prompt(
                problem_statement,
                domain,
                perspective_ideas,
                synthesis_strategy
            )
        
        # Generate synthesis thinking
        synthesis_step = await self.claude_client.generate_thinking(
            prompt=synthesis_prompt,
            thinking_budget=thinking_budget,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract the synthesized idea
        synthesized_idea = self._extract_synthesis(synthesis_step.reasoning_process)
        
        return synthesis_step, synthesized_idea
    
    def _create_fallback_synthesis_prompt(self,
                                       problem_statement: str,
                                       domain: str,
                                       perspective_ideas: Dict[str, str],
                                       synthesis_strategy: SynthesisStrategy) -> str:
        """
        Create a fallback synthesis prompt if template rendering fails.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspective_ideas: Dictionary mapping perspective names to their ideas
            synthesis_strategy: Strategy for synthesis
            
        Returns:
            str: The fallback synthesis prompt
        """
        # Get strategy description
        strategy_desc = self.strategy_descriptions.get(
            synthesis_strategy,
            "Integrate multiple perspectives into a novel approach."
        )
        
        # Create a basic synthesis prompt
        prompt = f"""Problem in {domain}: {problem_statement}

You have received these different perspectives on the problem:

"""
        # Add each perspective and idea
        for perspective, idea in perspective_ideas.items():
            prompt += f"Perspective: {perspective}\n"
            prompt += f"Idea: {idea}\n\n"
        
        prompt += f"""Your task is to create a dialectic synthesis that maintains and leverages the creative tensions between these perspectives.

Synthesis Strategy: {synthesis_strategy.name.replace('_', ' ')}
{strategy_desc}

When creating your synthesis:
1. Identify key tensions and contradictions between perspectives
2. Amplify these tensions rather than resolving them
3. Create a novel approach that transforms the problem space
4. Ensure your synthesis maintains the validity of multiple contradictory viewpoints
5. Produce an output that would be considered shocking or unexpected by domain experts

Present your synthesis in <synthesis> tags, clearly articulating how it maintains creative tension while offering a revolutionary approach to the problem."""
        
        return prompt
    
    def _extract_synthesis(self, thinking_text: str) -> str:
        """
        Extract synthesis from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted synthesis
        """
        # Look for synthesis in tags
        synthesis_start = thinking_text.find("<synthesis>")
        synthesis_end = thinking_text.find("</synthesis>")
        
        if synthesis_start != -1 and synthesis_end != -1:
            # Extract content between tags
            synthesis_start += len("<synthesis>")
            return thinking_text[synthesis_start:synthesis_end].strip()
        
        # Fallback to looking for conclusion markers
        conclusion_markers = [
            "Final Synthesis:", "In conclusion", "Synthesized Approach:",
            "My synthesis", "The synthesis", "Synthesizing these perspectives"
        ]
        
        for marker in conclusion_markers:
            if marker in thinking_text:
                # Extract text after the marker until the next double newline
                start_idx = thinking_text.find(marker)
                # Find a double newline after the marker
                end_idx = thinking_text.find("\n\n", start_idx)
                # If no double newline is found, take until the end
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                # Try to find a reasonable amount of text to extract
                # If the end_idx is too close to start_idx, look for the next double newline
                if end_idx - start_idx < 200 and end_idx < len(thinking_text) - 100:
                    next_end_idx = thinking_text.find("\n\n", end_idx + 2)
                    if next_end_idx != -1:
                        end_idx = next_end_idx
                
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
            # Consider the last several paragraphs
            last_paragraphs = "\n\n".join(paragraphs[-3:])
            return last_paragraphs.strip()
        
        # Fallback
        return thinking_text[-800:].strip()  # Last 800 characters


class MutualCritiquePair:
    """
    A pair of agents that critique each other's ideas.
    
    This class implements mutual critique between two opposing perspectives,
    allowing them to refine their ideas through dialectic interaction.
    """
    
    def __init__(self, 
               perspective_a: PerspectiveType,
               perspective_b: PerspectiveType,
               api_key: Optional[str] = None):
        """
        Initialize the Mutual Critique Pair.
        
        Args:
            perspective_a: First perspective type
            perspective_b: Second perspective type
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        self.perspective_a = perspective_a
        self.perspective_b = perspective_b
        
        # Initialize the base dialectic system for perspective generation
        self.base_system = MultiAgentDialecticSystem(self.api_key)
    
    async def generate_critique_cycle(self,
                                    problem_statement: str,
                                    domain: str,
                                    critique_rounds: int = 2,
                                    thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Generate a cycle of mutual critiques between two perspectives.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            critique_rounds: Number of critique rounds
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of the critique cycle including all interactions
        """
        # Initialize the critique cycle
        cycle_results = {
            "problem_statement": problem_statement,
            "domain": domain,
            "perspective_a": self.perspective_a.value,
            "perspective_b": self.perspective_b.value,
            "interactions": [],
            "critique_rounds": critique_rounds,
            "final_ideas": {}
        }
        
        # Step 1: Generate initial ideas from both perspectives
        perspectives = [self.perspective_a, self.perspective_b]
        thinking_steps, initial_ideas = await self.base_system.generate_perspectives(
            problem_statement, domain, perspectives, thinking_budget
        )
        
        # Map perspectives to their initial ideas
        idea_a = initial_ideas[0]
        idea_b = initial_ideas[1]
        
        # Store initial ideas
        cycle_results["interactions"].append({
            "round": 0,
            "type": "initial_ideas",
            "idea_a": idea_a,
            "idea_b": idea_b
        })
        
        # Step 2: Perform critique rounds
        for round_num in range(1, critique_rounds + 1):
            # A critiques B
            critique_a_of_b, idea_a_improved = await self._generate_critique(
                problem_statement,
                domain,
                self.perspective_a,
                idea_a,
                self.perspective_b,
                idea_b,
                thinking_budget
            )
            
            # B critiques A
            critique_b_of_a, idea_b_improved = await self._generate_critique(
                problem_statement,
                domain,
                self.perspective_b,
                idea_b,
                self.perspective_a,
                idea_a,
                thinking_budget
            )
            
            # Store critiques and improved ideas
            cycle_results["interactions"].append({
                "round": round_num,
                "type": "critiques",
                "critique_a_of_b": critique_a_of_b,
                "critique_b_of_a": critique_b_of_a,
                "idea_a_improved": idea_a_improved,
                "idea_b_improved": idea_b_improved
            })
            
            # Update ideas for next round
            idea_a = idea_a_improved
            idea_b = idea_b_improved
        
        # Store final ideas
        cycle_results["final_ideas"] = {
            self.perspective_a.value: idea_a,
            self.perspective_b.value: idea_b
        }
        
        return cycle_results
    
    async def _generate_critique(self,
                              problem_statement: str,
                              domain: str,
                              critic_perspective: PerspectiveType,
                              critic_idea: str,
                              target_perspective: PerspectiveType,
                              target_idea: str,
                              thinking_budget: int = 16000) -> Tuple[str, str]:
        """
        Generate a critique from one perspective of another's idea, and an improved idea.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            critic_perspective: Perspective type of the critic
            critic_idea: The critic's current idea
            target_perspective: Perspective type being critiqued
            target_idea: The idea being critiqued
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Tuple[str, str]: The critique and the improved idea from the critic
        """
        # Create a prompt for the critique
        critique_prompt = f"""Problem in {domain}: {problem_statement}

Your Perspective: {critic_perspective.value.upper()}
Your Current Idea: {critic_idea}

You are critiquing an idea from the {target_perspective.value.upper()} perspective:
{target_idea}

Step 1: Critique this idea from your perspective. What are its strengths and weaknesses? 
What assumptions does it make that you disagree with? What aspects of the problem does it overlook?

Step 2: After your critique, refine your own idea in light of this critique process. 
Your refined idea should maintain your fundamental perspective while potentially incorporating 
valuable insights gained from analyzing the other perspective's approach.

Present your critique in <critique> tags and your improved idea in <improved_idea> tags.
Maintain the integrity of your perspective - don't compromise your core assumptions.
"""
        
        # Generate critique thinking
        critique_step = await self.claude_client.generate_thinking(
            prompt=critique_prompt,
            thinking_budget=thinking_budget,
            max_tokens=4000
        )
        
        # Extract critique and improved idea
        critique = self._extract_tagged_content(critique_step.reasoning_process, "critique")
        improved_idea = self._extract_tagged_content(critique_step.reasoning_process, "improved_idea")
        
        # Fallback if extraction fails
        if not critique:
            critique = critique_step.reasoning_process[:500]
        
        if not improved_idea:
            # Look for conclusion markers
            conclusion_markers = [
                "Improved Idea:", "My refined idea", "In conclusion",
                "My improved approach", "Refined solution"
            ]
            
            for marker in conclusion_markers:
                if marker in critique_step.reasoning_process:
                    start_idx = critique_step.reasoning_process.find(marker)
                    improved_idea = critique_step.reasoning_process[start_idx:].strip()
                    break
            
            # If still not found, use the latter part of the text
            if not improved_idea:
                improved_idea = critique_step.reasoning_process[-500:].strip()
        
        return critique, improved_idea
    
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


@uses_prompt("dialectic_synthesis", dependencies=["dialectic_synthesis_integration"])
class DialecticSystem:
    """
    Comprehensive system for dialectic synthesis and multi-perspective creativity.
    
    This class coordinates different dialectic engines and synthesis strategies
    to create a sophisticated multi-agent dialectic system.
    
    Depends on prompts: dialectic_synthesis.txt, dialectic_synthesis_integration.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Dialectic System.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.synthesis_engine = DialecticSynthesisEngine(self.api_key)
        self.base_system = MultiAgentDialecticSystem(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def generate_direct_synthesis(self,
                                      problem_statement: str,
                                      domain: str,
                                      perspectives: Optional[List[PerspectiveType]] = None,
                                      synthesis_strategy: SynthesisStrategy = SynthesisStrategy.TENSION_MAINTENANCE,
                                      thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Generate a dialectic synthesis directly from multiple perspectives.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspectives: Optional list of perspectives to use
            synthesis_strategy: Strategy for synthesis
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of dialectic synthesis
        """
        # Use default perspectives if none provided
        if not perspectives:
            perspectives = [
                PerspectiveType.RADICAL,
                PerspectiveType.CONSERVATIVE,
                PerspectiveType.ALIEN,
                PerspectiveType.FUTURE
            ]
        
        # Step 1: Generate perspectives
        thinking_steps, perspective_ideas = await self.base_system.generate_perspectives(
            problem_statement, domain, perspectives, thinking_budget
        )
        
        # Convert perspectives and ideas to a dictionary
        perspective_ideas_dict = {
            perspective.value: idea for perspective, idea in zip(perspectives, perspective_ideas)
        }
        
        # Step 2: Generate synthesis
        synthesis_step, synthesized_idea = await self.synthesis_engine.generate_dialectic_synthesis(
            problem_statement, domain, perspective_ideas_dict, synthesis_strategy, thinking_budget
        )
        
        # Step 3: Create a creative idea
        idea = self._create_dialectic_idea(
            synthesized_idea, perspective_ideas, perspectives, synthesis_strategy
        )
        
        # Add synthesis step to thinking steps
        all_thinking_steps = thinking_steps + [synthesis_step]
        
        # Create results
        results = {
            "perspective_types": [p.value for p in perspectives],
            "perspective_ideas": perspective_ideas,
            "perspective_ideas_dict": perspective_ideas_dict,
            "synthesis_strategy": synthesis_strategy.name,
            "synthesized_idea": synthesized_idea,
            "thinking_steps": all_thinking_steps,
            "idea": idea
        }
        
        return results
    
    async def generate_critique_synthesis(self,
                                        problem_statement: str,
                                        domain: str,
                                        critique_pairs: Optional[List[Tuple[PerspectiveType, PerspectiveType]]] = None,
                                        synthesis_strategy: SynthesisStrategy = SynthesisStrategy.TENSION_MAINTENANCE,
                                        critique_rounds: int = 2,
                                        thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Generate a synthesis after multiple rounds of mutual critique.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            critique_pairs: Optional list of perspective type pairs for mutual critique
            synthesis_strategy: Strategy for synthesis
            critique_rounds: Number of critique rounds
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of dialectic synthesis
        """
        # Use default critique pairs if none provided
        if not critique_pairs:
            critique_pairs = [
                (PerspectiveType.RADICAL, PerspectiveType.CONSERVATIVE),
                (PerspectiveType.ALIEN, PerspectiveType.FUTURE)
            ]
        
        # Step 1: Generate critique cycles for each pair
        critique_cycles = []
        final_ideas = {}
        
        for pair in critique_pairs:
            perspective_a, perspective_b = pair
            
            # Create critique pair
            critique_pair = MutualCritiquePair(
                perspective_a, perspective_b, self.api_key
            )
            
            # Generate critique cycle
            cycle_results = await critique_pair.generate_critique_cycle(
                problem_statement, domain, critique_rounds, thinking_budget
            )
            
            # Store results
            critique_cycles.append(cycle_results)
            
            # Add final ideas to combined dictionary
            final_ideas.update(cycle_results["final_ideas"])
        
        # Step 2: Generate synthesis from final ideas
        synthesis_step, synthesized_idea = await self.synthesis_engine.generate_dialectic_synthesis(
            problem_statement, domain, final_ideas, synthesis_strategy, thinking_budget
        )
        
        # Step 3: Create a creative idea
        # Extract perspectives from the keys of final_ideas
        perspectives = [PerspectiveType(p) for p in final_ideas.keys()]
        idea = self._create_dialectic_idea(
            synthesized_idea, list(final_ideas.values()), perspectives, synthesis_strategy
        )
        
        # Create results
        results = {
            "critique_cycles": critique_cycles,
            "final_ideas": final_ideas,
            "synthesis_strategy": synthesis_strategy.name,
            "synthesized_idea": synthesized_idea,
            "idea": idea
        }
        
        return results
    
    async def generate_multi_strategy_synthesis(self,
                                             problem_statement: str,
                                             domain: str,
                                             perspectives: Optional[List[PerspectiveType]] = None,
                                             strategies: Optional[List[SynthesisStrategy]] = None,
                                             thinking_budget: int = 16000) -> Dict[str, Any]:
        """
        Generate multiple syntheses using different strategies and meta-synthesize them.
        
        Args:
            problem_statement: The problem statement
            domain: The domain of the problem
            perspectives: Optional list of perspectives to use
            strategies: Optional list of synthesis strategies to use
            thinking_budget: Maximum tokens to use for thinking
            
        Returns:
            Dict[str, Any]: Results of multi-strategy dialectic synthesis
        """
        # Use default perspectives if none provided
        if not perspectives:
            perspectives = [
                PerspectiveType.RADICAL,
                PerspectiveType.CONSERVATIVE,
                PerspectiveType.ALIEN,
                PerspectiveType.FUTURE
            ]
        
        # Use default strategies if none provided
        if not strategies:
            strategies = [
                SynthesisStrategy.INTEGRATION,
                SynthesisStrategy.TENSION_MAINTENANCE,
                SynthesisStrategy.META_PERSPECTIVE
            ]
        
        # Step 1: Generate perspectives
        thinking_steps, perspective_ideas = await self.base_system.generate_perspectives(
            problem_statement, domain, perspectives, thinking_budget
        )
        
        # Convert perspectives and ideas to a dictionary
        perspective_ideas_dict = {
            perspective.value: idea for perspective, idea in zip(perspectives, perspective_ideas)
        }
        
        # Step 2: Generate synthesis for each strategy
        strategy_syntheses = {}
        
        for strategy in strategies:
            synthesis_step, synthesized_idea = await self.synthesis_engine.generate_dialectic_synthesis(
                problem_statement, domain, perspective_ideas_dict, strategy, thinking_budget
            )
            
            strategy_syntheses[strategy.name] = synthesized_idea
        
        # Step 3: Generate meta-synthesis
        meta_synthesis_prompt = f"""Problem in {domain}: {problem_statement}

You have received these different dialectic syntheses, each created using a different strategy:

"""
        # Add each strategy synthesis
        for strategy_name, synthesis in strategy_syntheses.items():
            meta_synthesis_prompt += f"Strategy: {strategy_name}\n"
            meta_synthesis_prompt += f"Synthesis: {synthesis}\n\n"
        
        meta_synthesis_prompt += """Your task is to create a meta-synthesis that integrates these different dialectic approaches. This meta-synthesis should:

1. Identify the unique strengths of each synthesis strategy
2. Extract the most valuable elements from each approach
3. Create a higher-order synthesis that transcends all previous approaches
4. Generate a revolutionary solution that maintains the creative tensions found in each strategy
5. Transform the problem space in ways that would be impossible with any single strategy

Think about how these different synthesis strategies reveal different aspects of the problem, and how their integration generates an emergent approach that transcends each individual strategy.

Present your meta-synthesis in <meta_synthesis> tags, clearly articulating how it integrates and transcends all previous syntheses."""
        
        # Generate meta-synthesis thinking
        meta_synthesis_step = await self.claude_client.generate_thinking(
            prompt=meta_synthesis_prompt,
            thinking_budget=thinking_budget,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract meta-synthesis
        meta_synthesis = self._extract_tagged_content(meta_synthesis_step.reasoning_process, "meta_synthesis")
        
        # Fallback if extraction fails
        if not meta_synthesis:
            meta_synthesis = self.synthesis_engine._extract_synthesis(meta_synthesis_step.reasoning_process)
        
        # Step 4: Create a creative idea
        idea = self._create_dialectic_idea(
            meta_synthesis, list(perspective_ideas_dict.values()), perspectives, SynthesisStrategy.META_PERSPECTIVE
        )
        
        # Create results
        results = {
            "perspective_types": [p.value for p in perspectives],
            "perspective_ideas": perspective_ideas,
            "strategy_syntheses": strategy_syntheses,
            "meta_synthesis": meta_synthesis,
            "idea": idea
        }
        
        return results
    
    def _create_dialectic_idea(self,
                            synthesized_idea: str,
                            perspective_ideas: List[str],
                            perspectives: List[PerspectiveType],
                            synthesis_strategy: SynthesisStrategy) -> CreativeIdea:
        """
        Create a creative idea from dialectic synthesis.
        
        Args:
            synthesized_idea: The synthesized idea
            perspective_ideas: Ideas from different perspectives
            perspectives: Types of perspectives used
            synthesis_strategy: Strategy used for synthesis
            
        Returns:
            CreativeIdea: The creative idea
        """
        # Create a shock profile for the dialectic idea
        shock_profile = ShockProfile(
            novelty_score=0.9,  # Higher for dialectic synthesis
            contradiction_score=0.95,  # Very high due to maintained tensions
            impossibility_score=0.85,
            utility_potential=0.75,
            expert_rejection_probability=0.85,
            composite_shock_value=0.9
        )
        
        # Create a dialectic idea
        dialectic_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=synthesized_idea,
            generative_framework=f"dialectic_{synthesis_strategy.name.lower()}",
            domain=None,  # Will be set by caller if needed
            impossibility_elements=[],
            contradiction_elements=[p.value for p in perspectives],  # Use perspectives as contradiction elements
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return dialectic_idea
    
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