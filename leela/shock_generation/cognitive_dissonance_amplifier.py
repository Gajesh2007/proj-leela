"""
Cognitive Dissonance Amplifier - Forces contradictory yet simultaneously necessary 
concepts to coexist.

Implements prompt: cognitive_dissonance_amplifier.txt
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import random
from pydantic import UUID4
from ..knowledge_representation.models import ShockDirective, ThinkingStep, CreativeIdea, ShockProfile
from ..prompt_management import uses_prompt


@uses_prompt("cognitive_dissonance_amplifier", dependencies=["dialectic_synthesis"])
class CognitiveDissonanceAmplifier:
    """
    Forces contradictory yet simultaneously necessary concepts to coexist in creative ideas.
    
    This class implements the cognitive_dissonance_amplifier.txt prompt to generate
    ideas that embrace opposing concepts simultaneously, creating productive tension.
    
    Depends on prompt: dialectic_synthesis.txt
    """
    
    def __init__(self):
        """Initialize the Cognitive Dissonance Amplifier."""
        # Common contradictory concept pairs by domain
        self.contradiction_pairs = {
            "physics": [
                ("determinism", "quantum randomness"),
                ("locality", "non-locality"),
                ("continuity", "discreteness"),
                ("relativity", "quantum mechanics"),
                ("causality", "retrocausality")
            ],
            "biology": [
                ("competition", "cooperation"),
                ("centralized control", "emergent behavior"),
                ("genetic determinism", "epigenetic plasticity"),
                ("individual selection", "group selection"),
                ("physiological stability", "constant change")
            ],
            "computer_science": [
                ("security", "accessibility"),
                ("efficiency", "generality"),
                ("abstraction", "implementation detail"),
                ("centralization", "decentralization"),
                ("deterministic", "probabilistic")
            ],
            "economics": [
                ("free market", "regulation"),
                ("individualism", "collectivism"),
                ("scarcity", "abundance"),
                ("competition", "cooperation"),
                ("rationality", "irrationality")
            ],
            "mathematics": [
                ("discrete", "continuous"),
                ("deterministic", "probabilistic"),
                ("finite", "infinite"),
                ("constructive", "existential"),
                ("local", "global")
            ]
        }
    
    def generate_contradiction_pairs(self, domain: str, 
                                   num_pairs: int = 2) -> List[Tuple[str, str]]:
        """
        Generate pairs of contradictory concepts for a given domain.
        
        Args:
            domain: The domain to generate contradiction pairs for
            num_pairs: Number of contradiction pairs to generate
            
        Returns:
            List[Tuple[str, str]]: List of contradiction pairs
        """
        # If domain exists in our predefined pairs, use those
        if domain in self.contradiction_pairs:
            pairs = self.contradiction_pairs[domain]
            # Randomly select the requested number of pairs
            if len(pairs) > num_pairs:
                return random.sample(pairs, num_pairs)
            return pairs
        
        # For unknown domains, generate generic contradictions
        generic_pairs = [
            ("simplicity", "complexity"),
            ("certainty", "uncertainty"),
            ("unity", "diversity"),
            ("stability", "change"),
            ("objectivity", "subjectivity"),
            ("reductionism", "holism"),
            ("determinism", "randomness"),
            ("continuity", "discreteness"),
            ("structure", "function"),
            ("centralization", "decentralization")
        ]
        
        # Randomly select the requested number of pairs
        if len(generic_pairs) > num_pairs:
            return random.sample(generic_pairs, num_pairs)
        return generic_pairs
    
    def measure_dissonance(self, idea: str, contradiction_pairs: List[Tuple[str, str]]) -> float:
        """
        Measure the cognitive dissonance in an idea based on contradiction pairs.
        
        Args:
            idea: The idea to measure
            contradiction_pairs: List of contradiction pairs to look for
            
        Returns:
            float: Dissonance score (0.0-1.0)
        """
        # Initialize score
        score = 0.0
        pairs_found = 0
        
        # Check each contradiction pair
        for concept1, concept2 in contradiction_pairs:
            # Check if both concepts are mentioned
            concept1_found = concept1.lower() in idea.lower()
            concept2_found = concept2.lower() in idea.lower()
            
            # Check for conceptual presence through related terms
            # This is a simple implementation - in a real system, we'd use NLP
            # to detect conceptual references even when exact phrases aren't used
            if not concept1_found:
                concept1_terms = concept1.split()
                term_count = 0
                for term in concept1_terms:
                    if term.lower() in idea.lower() and len(term) > 3:  # Ignore very short terms
                        term_count += 1
                if term_count / len(concept1_terms) > 0.5:
                    concept1_found = True
            
            if not concept2_found:
                concept2_terms = concept2.split()
                term_count = 0
                for term in concept2_terms:
                    if term.lower() in idea.lower() and len(term) > 3:  # Ignore very short terms
                        term_count += 1
                if term_count / len(concept2_terms) > 0.5:
                    concept2_found = True
            
            # If both concepts are found, increment score
            if concept1_found and concept2_found:
                pairs_found += 1
        
        # Calculate score based on pairs found
        if contradiction_pairs:
            score = pairs_found / len(contradiction_pairs)
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def amplify_dissonance(self, thinking_step: ThinkingStep, domain: str,
                         contradiction_requirements: Optional[List[str]] = None) -> CreativeIdea:
        """
        Amplify cognitive dissonance in a generated idea.
        
        Args:
            thinking_step: The thinking step to extract ideas from
            domain: The domain the idea belongs to
            contradiction_requirements: Optional list of specific contradictions to enforce
            
        Returns:
            CreativeIdea: The creative idea with amplified dissonance
        """
        # Extract ideas from thinking
        description = self._extract_idea_description(thinking_step.reasoning_process)
        
        # Generate contradiction pairs
        contradiction_pairs = []
        if contradiction_requirements:
            # Convert requirements to pairs
            # This assumes requirements are formatted as "concept1|concept2"
            for requirement in contradiction_requirements:
                if "|" in requirement:
                    concepts = requirement.split("|")
                    contradiction_pairs.append((concepts[0].strip(), concepts[1].strip()))
                else:
                    # For single concepts, try to find an opposing concept
                    opposing_concept = self._find_opposing_concept(requirement, domain)
                    if opposing_concept:
                        contradiction_pairs.append((requirement, opposing_concept))
        
        # If no valid pairs were created from requirements, generate some
        if not contradiction_pairs:
            contradiction_pairs = self.generate_contradiction_pairs(domain)
        
        # Measure dissonance
        dissonance_score = self.measure_dissonance(description, contradiction_pairs)
        
        # Create contradiction elements list
        contradiction_elements = []
        for concept1, concept2 in contradiction_pairs:
            contradiction_elements.append(f"{concept1}|{concept2}")
        
        # Create a shock profile
        # Note: in a real implementation, we'd measure all shock metrics 
        # more systematically - this is simplified
        novelty_score = 0.65  # Placeholder - would be calculated
        impossibility_score = 0.7  # Placeholder - would be calculated
        utility_potential = 0.4  # Placeholder - would be calculated
        expert_rejection_probability = 0.75  # Placeholder - would be calculated
        
        # Calculate composite shock value
        composite_shock_value = (
            0.25 * novelty_score +
            0.25 * dissonance_score +
            0.30 * impossibility_score +
            0.10 * utility_potential +
            0.10 * expert_rejection_probability
        )
        
        # Create shock profile
        shock_profile = ShockProfile(
            novelty_score=novelty_score,
            contradiction_score=dissonance_score,
            impossibility_score=impossibility_score,
            utility_potential=utility_potential,
            expert_rejection_probability=expert_rejection_probability,
            composite_shock_value=composite_shock_value
        )
        
        # Create creative idea
        creative_idea = CreativeIdea(
            description=description,
            generative_framework="cognitive_dissonance_amplifier",
            impossibility_elements=[],  # Would be populated in a real implementation
            contradiction_elements=contradiction_elements,
            related_concepts=[],  # Would be populated in a real implementation
            shock_metrics=shock_profile
        )
        
        return creative_idea
    
    def _extract_idea_description(self, thinking_text: str) -> str:
        """
        Extract the main idea description from thinking text.
        Looks for content between <idea> tags, or falls back to heuristics.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: The extracted idea description
        """
        # Look for <idea> tags
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
            "The breakthrough concept", "The innovative approach", "Paradoxical concept"
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
    
    def _find_opposing_concept(self, concept: str, domain: str) -> Optional[str]:
        """
        Find an opposing concept for a given concept.
        
        Args:
            concept: The concept to find an opposing concept for
            domain: The domain to look in
            
        Returns:
            Optional[str]: The opposing concept, if found
        """
        # Check if the concept appears in any contradiction pairs for the domain
        if domain in self.contradiction_pairs:
            for concept1, concept2 in self.contradiction_pairs[domain]:
                if concept.lower() == concept1.lower():
                    return concept2
                if concept.lower() == concept2.lower():
                    return concept1
        
        # Common opposing concept pairs across domains
        common_oppositions = {
            "simplicity": "complexity",
            "order": "chaos",
            "determinism": "randomness",
            "unity": "diversity",
            "centralized": "decentralized",
            "continuous": "discrete",
            "linear": "non-linear",
            "reductionist": "holistic",
            "objective": "subjective",
            "local": "global",
            "concrete": "abstract",
            "static": "dynamic",
            "individual": "collective",
            "competition": "cooperation",
            "scarcity": "abundance"
        }
        
        # Check in common oppositions
        for concept1, concept2 in common_oppositions.items():
            if concept.lower() == concept1.lower():
                return concept2
            if concept.lower() == concept2.lower():
                return concept1
        
        # No opposing concept found
        return None