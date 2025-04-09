"""
Impossibility Enforcer Module - Ensures outputs contain elements that experts 
would consider impossible.

Implements prompt: impossibility_enforcer.txt
"""
from typing import Dict, List, Any, Optional
import uuid
from pydantic import UUID4
from ..config import get_config
from ..knowledge_representation.models import ShockDirective, ThinkingStep, CreativeIdea, ShockProfile
from ..prompt_management import uses_prompt


@uses_prompt("impossibility_enforcer")
class ImpossibilityEnforcer:
    """
    Ensures that generated ideas contain elements that experts would consider impossible.
    
    This class implements the impossibility_enforcer.txt prompt to generate ideas
    that violate established domain constraints.
    """
    
    def __init__(self, domain_impossibilities: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the Impossibility Enforcer.
        
        Args:
            domain_impossibilities: Optional map of domains to impossible elements.
                If not provided, will use the config.
        """
        config = get_config()
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
        weights = config["creativity"]
        
        # Calculate composite shock value
        composite_shock_value = (
            weights["novelty_weight"] * novelty_score +
            weights["contradiction_weight"] * contradiction_score +
            weights["impossibility_weight"] * impossibility_score +
            weights["utility_weight"] * utility_potential +
            weights["expert_rejection_weight"] * expert_rejection_probability
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
            impossibility_elements=impossibility_constraints,
            contradiction_elements=[],  # Would be populated in a real implementation
            related_concepts=[],  # Would be populated in a real implementation
            shock_metrics=shock_profile
        )
        
        return creative_idea
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract the main idea description from thinking text.
        Looks for content between <revolutionary_idea> tags, or falls back to heuristics.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: The extracted idea description
        """
        # Look for <revolutionary_idea> tags
        idea_start = thinking_text.find("<revolutionary_idea>")
        idea_end = thinking_text.find("</revolutionary_idea>")
        
        if idea_start != -1 and idea_end != -1:
            # Extract content between tags
            idea_start += len("<revolutionary_idea>")
            return thinking_text[idea_start:idea_end].strip()
        
        # Look for <idea> tags (as fallback)
        idea_start = thinking_text.find("<idea>")
        idea_end = thinking_text.find("</idea>")
        
        if idea_start != -1 and idea_end != -1:
            # Extract content between tags
            idea_start += len("<idea>")
            return thinking_text[idea_start:idea_end].strip()
        
        # Fallback to previous method if tags not found
        # Look for conclusion markers
        conclusion_markers = [
            "In conclusion", "Therefore", "My shocking idea", "The idea is", 
            "The novel concept", "The impossible concept", "Final idea", 
            "The breakthrough concept", "The innovative approach"
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