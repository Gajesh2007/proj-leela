"""
Impossibility Enforcer Module - Ensures outputs contain elements that experts 
would consider impossible.

Implements prompt: impossibility_enforcer.txt
"""
from typing import Dict, List, Any, Optional
import uuid
import asyncio
from pydantic import UUID4
from ..config import get_config
from ..knowledge_representation.models import ShockDirective, ThinkingStep, CreativeIdea, ShockProfile
from ..prompt_management import uses_prompt
from ..directed_thinking.claude_api import ClaudeAPIClient


@uses_prompt("impossibility_enforcer")
class ImpossibilityEnforcer:
    """
    Ensures that generated ideas contain elements that experts would consider impossible.
    
    This class implements the impossibility_enforcer.txt prompt to generate ideas
    that violate established domain constraints.
    """
    
    def __init__(self, api_key: Optional[str] = None, domain_impossibilities: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the Impossibility Enforcer.
        
        Args:
            api_key: Optional API key for Claude API.
            domain_impossibilities: Optional map of domains to impossible elements.
                If not provided, will use the config.
        """
        config = get_config()
        self.api_key = api_key
        self.domain_impossibilities = domain_impossibilities or config["domain_impossibilities"]
    
    def check_impossibility(self, idea: str, domain: str, 
                          impossibility_constraints: List[str]) -> float:
        """
        Check if an idea contains impossible elements.
        
        Args:
            idea: The idea to check
            domain: The domain the idea belongs to
            impossibility_constraints: List of impossibility constraints that
                should be present in the idea
            
        Returns:
            float: Impossibility score (0.0-1.0)
        """
        # Initialize score
        score = 0.0
        constraints_found = 0
        
        # Check each impossibility constraint
        for constraint in impossibility_constraints:
            # Look for explicit mentions
            if constraint.lower() in idea.lower():
                constraints_found += 1
                continue
            
            # Check for conceptual inclusion through related terms
            # This is a simple implementation - in a real system, we'd use NLP
            # to detect conceptual references even when exact phrases aren't used
            constraint_terms = constraint.replace("_", " ").split()
            term_count = 0
            for term in constraint_terms:
                if term.lower() in idea.lower() and len(term) > 3:  # Ignore very short terms
                    term_count += 1
            
            # If most terms are found, consider the constraint partially met
            if term_count / len(constraint_terms) > 0.5:
                constraints_found += 0.5
        
        # Calculate score based on constraints found
        if impossibility_constraints:
            score = constraints_found / len(impossibility_constraints)
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    async def generate_idea(self, domain: str, problem_statement: str, 
                        shock_directive: ShockDirective, thinking_budget: int = 16000) -> CreativeIdea:
        """
        Generate a creative idea using the impossibility enforcer.
        
        Args:
            domain: The domain for idea generation
            problem_statement: The problem to solve
            shock_directive: Directive for controlling shock value
            thinking_budget: Maximum tokens for thinking
            
        Returns:
            CreativeIdea: The generated creative idea
        """
        # Create Claude API client
        claude_client = ClaudeAPIClient(self.api_key)
        
        # Construct prompt
        prompt = f"""
        # Problem Domain
        {domain}
        
        # Problem Statement
        {problem_statement}
        
        # Creative Framework
        Impossibility Enforcer
        
        # Impossibility Constraints
        {', '.join(shock_directive.impossibility_constraints)}
        
        You are an Impossibility Enforcer. Your task is to generate a shocking, novel idea that 
        violates established assumptions in the problem domain. Think step by step about how to 
        generate an idea that experts would consider impossible yet contains hidden value.
        
        Your idea must have a minimum shock threshold of {shock_directive.minimum_shock_threshold}.
        
        Provide your final idea between <revolutionary_idea></revolutionary_idea> tags.
        """
        
        # Generate thinking
        thinking_step = await claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=thinking_budget,
            max_tokens=thinking_budget + 4000  # Ensure max_tokens > thinking_budget
        )
        
        # Convert to CreativeIdea using enforce_impossibility
        idea = self.enforce_impossibility(
            thinking_step=thinking_step,
            domain=domain,
            impossibility_constraints=shock_directive.impossibility_constraints,
            shock_threshold=shock_directive.minimum_shock_threshold
        )
        
        # Add thinking steps
        idea.thinking_steps = [thinking_step]
        
        return idea
        
    def enforce_impossibility(self, thinking_step: ThinkingStep, domain: str,
                           impossibility_constraints: List[str], 
                           shock_threshold: float = 0.6) -> CreativeIdea:
        """
        Enforce impossibility in a generated idea.
        
        Args:
            thinking_step: The thinking step to extract ideas from
            domain: The domain the idea belongs to
            impossibility_constraints: List of impossibility constraints that
                should be present in the idea
            shock_threshold: Minimum required shock value
            
        Returns:
            CreativeIdea: The creative idea with impossibility elements
        """
        # Extract ideas from thinking
        description = self._extract_idea_description(thinking_step.reasoning_process)
        
        # Measure impossibility
        impossibility_score = self.check_impossibility(
            description, domain, impossibility_constraints
        )
        
        # Create a shock profile
        # Note: in a real implementation, we'd measure all shock metrics 
        # more systematically - this is simplified
        novelty_score = 0.7  # Placeholder - would be calculated
        contradiction_score = 0.6  # Placeholder - would be calculated
        utility_potential = 0.5  # Placeholder - would be calculated
        expert_rejection_probability = 0.8  # Placeholder - would be calculated
        
        config = get_config()
        weights = config.get("creativity", {
            "novelty_weight": 0.25,
            "contradiction_weight": 0.25,
            "impossibility_weight": 0.25,
            "utility_weight": 0.15,
            "expert_rejection_weight": 0.10
        })
        
        # Calculate composite shock value
        composite_shock_value = (
            weights.get("novelty_weight", 0.25) * novelty_score +
            weights.get("contradiction_weight", 0.25) * contradiction_score +
            weights.get("impossibility_weight", 0.25) * impossibility_score +
            weights.get("utility_weight", 0.15) * utility_potential +
            weights.get("expert_rejection_weight", 0.10) * expert_rejection_probability
        )
        
        # Create shock profile
        shock_profile = ShockProfile(
            novelty_score=novelty_score,
            contradiction_score=contradiction_score,
            impossibility_score=impossibility_score,
            utility_potential=utility_potential,
            expert_rejection_probability=expert_rejection_probability,
            composite_shock_value=composite_shock_value
        )
        
        # Create creative idea
        creative_idea = CreativeIdea(
            description=description,
            generative_framework="impossibility_enforcer",
            domain=domain,
            impossibility_elements=impossibility_constraints,
            contradiction_elements=[],  # Would be populated in a real implementation
            related_concepts=[],  # Would be populated in a real implementation
            shock_metrics=shock_profile
        )
        
        return creative_idea
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract the main idea description from thinking text.
        Looks for content between various tags or markers, or uses ML processing to find the most idea-like content.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: The extracted idea description
        """
        # First try extracting between different types of tags
        tag_pairs = [
            ("<revolutionary_idea>", "</revolutionary_idea>"),
            ("<idea>", "</idea>"),
            ("<final_idea>", "</final_idea>"),
            ("<creative_idea>", "</creative_idea>"),
            ("<disruptive_idea>", "</disruptive_idea>"),
            ("<synthesis>", "</synthesis>")
        ]
        
        for start_tag, end_tag in tag_pairs:
            idea_start = thinking_text.find(start_tag)
            idea_end = thinking_text.find(end_tag)
            
            if idea_start != -1 and idea_end != -1:
                # Extract content between tags
                idea_start += len(start_tag)
                idea_content = thinking_text[idea_start:idea_end].strip()
                if len(idea_content) > 50:  # Ensure we have substantial content
                    return idea_content
        
        # Look for markdown-style sections indicating the idea
        markdown_headers = [
            "# Final Idea", "## Final Idea", "# The Idea", "## The Idea",
            "# Revolutionary Idea", "## Revolutionary Idea",
            "# Creative Solution", "## Creative Solution",
            "# Proposed Solution", "## Proposed Solution",
            "# Idea", "## Idea"
        ]
        
        for header in markdown_headers:
            if header in thinking_text:
                start_idx = thinking_text.find(header) + len(header)
                # Find the next header or the end of text
                next_header_idx = float('inf')
                for h in ["#", "<"]:
                    next_idx = thinking_text.find(f"\n{h}", start_idx)
                    if next_idx > start_idx:
                        next_header_idx = min(next_header_idx, next_idx)
                
                end_idx = next_header_idx if next_header_idx < float('inf') else len(thinking_text)
                idea_content = thinking_text[start_idx:end_idx].strip()
                if len(idea_content) > 50:
                    return idea_content
        
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "My shocking idea", "The idea is", 
            "The novel concept", "The impossible concept", "Final idea", 
            "The breakthrough concept", "The innovative approach", "My revolutionary idea",
            "My proposal is", "The solution is", "This concept", "The approach is",
            "To summarize the idea", "The key innovation is", "My final idea is",
            "The disruptive concept", "The new model would"
        ]
        
        # Sort markers by position in text to find the earliest substantial one
        marker_positions = []
        for marker in conclusion_markers:
            start_idx = thinking_text.find(marker)
            if start_idx != -1:
                # Extract text after the marker
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                description = thinking_text[start_idx:end_idx].strip()
                
                # Clean up the description
                if description.startswith(marker):
                    description = description[len(marker):].strip()
                    if description.startswith(":"):
                        description = description[1:].strip()
                
                if len(description) > 100:  # Ensure substantial content
                    marker_positions.append((start_idx, description))
        
        # If we found markers, use the one with most content
        if marker_positions:
            # Get the marker with the most content
            best_description = max(marker_positions, key=lambda x: len(x[1]))[1]
            return best_description
        
        # If no markers worked, try a structural approach - look for a substantial paragraph 
        # that appears to be a standalone idea rather than reasoning
        paragraphs = [p.strip() for p in thinking_text.split("\n\n") if p.strip()]
        
        # Filter for paragraphs that look like ideas (more than 100 chars, not starting with reasoning words)
        reasoning_starters = ["first", "second", "third", "next", "then", "now", "let", "if", "so", "thus", "therefore", "hence"]
        
        idea_candidates = []
        for p in paragraphs:
            # Skip short paragraphs or obvious reasoning steps
            if len(p) < 100:
                continue
                
            # Skip if starts with reasoning indicators
            lower_p = p.lower()
            if any(lower_p.startswith(starter) for starter in reasoning_starters):
                continue
                
            # Skip if contains too many question marks (likely reasoning questions)
            if p.count("?") > 2:
                continue
                
            idea_candidates.append(p)
        
        # If we have candidates, return the most substantial one
        if idea_candidates:
            return max(idea_candidates, key=len)
        
        # Last resort - return the last substantial paragraph
        substantial_paragraphs = [p for p in paragraphs if len(p) > 100]
        if substantial_paragraphs:
            return substantial_paragraphs[-1]
        
        # Final fallback - get the largest chunk of text available
        return thinking_text[-1000:].strip() if len(thinking_text) > 1000 else thinking_text.strip()