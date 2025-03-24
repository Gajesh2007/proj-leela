"""
Disruptor Module - Creates conceptual superpositions by forcing paradoxical states and challenging assumptions.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from pydantic import UUID4
from ..config import get_config
from ..knowledge_representation.models import (
    CreativeIdea, ThinkingStep, ShockProfile, Concept, ConceptState
)
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..knowledge_representation.superposition_engine import SuperpositionEngine


class AssumptionDetector:
    """
    Detects implicit assumptions in problem spaces.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Assumption Detector.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Common assumptions by domain
        self.domain_assumptions = {
            "physics": [
                "Locality in space and time",
                "Causal determinism",
                "Conservation laws are inviolable",
                "Uniform arrow of time",
                "Observer independence"
            ],
            "biology": [
                "Cellular basis of life",
                "DNA as primary information carrier",
                "Natural selection as primary evolutionary mechanism",
                "Biochemical basis of metabolism",
                "Species boundaries"
            ],
            "computer_science": [
                "Binary logic",
                "Deterministic computation",
                "Church-Turing thesis",
                "Von Neumann architecture",
                "Sequential processing"
            ],
            "economics": [
                "Rational actors",
                "Scarcity as fundamental",
                "Value derived from scarcity",
                "Growth as essential",
                "Self-interest as driver"
            ],
            "mathematics": [
                "Logical consistency",
                "Set theory foundation",
                "Law of excluded middle",
                "Mathematical Platonism",
                "ZFC axioms"
            ]
        }
    
    async def detect_assumptions(self, problem_statement: str, domain: str) -> List[str]:
        """
        Detect implicit assumptions in a problem statement.
        
        Args:
            problem_statement: The problem statement to analyze
            domain: The domain of the problem
            
        Returns:
            List[str]: Detected assumptions
        """
        # Start with domain-specific assumptions if available
        assumptions = self.domain_assumptions.get(domain, [])[:3]  # Take up to 3
        
        # Create a prompt to detect assumptions
        prompt = f"""Analyze this problem statement in the domain of {domain}:
        
{problem_statement}

Identify the implicit assumptions underlying this problem. These are unstated beliefs, premises, or constraints that are taken for granted. Focus especially on assumptions that:

1. Limit the solution space unnecessarily
2. Are rarely questioned in the domain
3. Might be violated to create breakthrough solutions

List at least 5 specific assumptions, prioritizing those that would be most shocking to violate."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=9000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract assumptions from thinking
        extracted_assumptions = self._extract_assumptions(thinking_step.reasoning_process)
        
        # Combine with domain assumptions
        all_assumptions = assumptions + [a for a in extracted_assumptions if a not in assumptions]
        
        return all_assumptions
    
    def _extract_assumptions(self, thinking_text: str) -> List[str]:
        """
        Extract assumptions from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[str]: Extracted assumptions
        """
        assumptions = []
        
        # Look for numbered or bulleted lists
        import re
        
        # Pattern for numbered list items
        numbered_pattern = r'\d+\.\s+(.*?)(?=\d+\.\s+|\n\n|$)'
        numbered_matches = re.findall(numbered_pattern, thinking_text, re.DOTALL)
        
        # Pattern for bulleted list items
        bulleted_pattern = r'[-*•]\s+(.*?)(?=[-*•]\s+|\n\n|$)'
        bulleted_matches = re.findall(bulleted_pattern, thinking_text, re.DOTALL)
        
        # Combine matches
        matches = numbered_matches + bulleted_matches
        
        # Clean and add to assumptions
        for match in matches:
            assumption = match.strip()
            # Remove any trailing explanation after a colon or dash
            assumption = re.split(r'[:\-–]', assumption)[0].strip()
            
            # Only add if not too short and not too long
            if 5 < len(assumption) < 150:
                assumptions.append(assumption)
        
        # If no structured list is found, try to find sentences with assumption indicators
        if not assumptions:
            sentences = re.split(r'(?<=[.!?])\s+', thinking_text)
            assumption_indicators = [
                "assumes", "assumption", "presupposes", "takes for granted",
                "implicit", "underlying", "unstated"
            ]
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in assumption_indicators):
                    # Clean the sentence
                    clean_sentence = sentence.strip()
                    if 10 < len(clean_sentence) < 150:
                        assumptions.append(clean_sentence)
        
        return assumptions[:5]  # Limit to 5 assumptions


class InversionEngine:
    """
    Generates systematic inversions of identified assumptions.
    """
    
    def invert_assumption(self, assumption: str) -> str:
        """
        Invert an assumption.
        
        Args:
            assumption: The assumption to invert
            
        Returns:
            str: The inverted assumption
        """
        # Common inversion patterns
        inversion_patterns = [
            # Presence/absence inversions
            (r'always', 'never'),
            (r'never', 'always'),
            (r'all', 'none'),
            (r'none', 'all'),
            (r'must', 'cannot'),
            (r'cannot', 'must'),
            
            # Qualitative inversions
            (r'increase', 'decrease'),
            (r'decrease', 'increase'),
            (r'positive', 'negative'),
            (r'negative', 'positive'),
            (r'high', 'low'),
            (r'low', 'high'),
            
            # Relationship inversions
            (r'causes', 'is caused by'),
            (r'precedes', 'follows'),
            (r'follows', 'precedes'),
            (r'contains', 'is contained by'),
            
            # Common concept inversions
            (r'deterministic', 'probabilistic'),
            (r'discrete', 'continuous'),
            (r'linear', 'non-linear'),
            (r'sequential', 'parallel'),
            (r'centralized', 'decentralized'),
            (r'rational', 'irrational'),
            (r'finite', 'infinite')
        ]
        
        # Try direct pattern replacement
        for pattern, replacement in inversion_patterns:
            import re
            if re.search(r'\b' + re.escape(pattern) + r'\b', assumption, re.IGNORECASE):
                return re.sub(r'\b' + re.escape(pattern) + r'\b', replacement, assumption, flags=re.IGNORECASE)
        
        # If no direct pattern, try negation
        negation_prefixes = [
            "Not ", "The absence of ", "The inverse of ", "The opposite of "
        ]
        
        return negation_prefixes[0] + assumption.lower()
    
    def generate_inversions(self, assumptions: List[str]) -> List[Tuple[str, str]]:
        """
        Generate inversions for a list of assumptions.
        
        Args:
            assumptions: List of assumptions to invert
            
        Returns:
            List[Tuple[str, str]]: Pairs of (assumption, inversion)
        """
        inversion_pairs = []
        
        for assumption in assumptions:
            inversion = self.invert_assumption(assumption)
            inversion_pairs.append((assumption, inversion))
        
        return inversion_pairs


class ParadoxGenerator:
    """
    Creates productive contradictions that force new thinking.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Paradox Generator.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def generate_paradox(self, inversion_pairs: List[Tuple[str, str]], domain: str) -> str:
        """
        Generate a productive paradox from inversion pairs.
        
        Args:
            inversion_pairs: Pairs of (assumption, inversion)
            domain: The domain of the problem
            
        Returns:
            str: Generated paradox
        """
        # Select a random pair of inversions
        import random
        selected_pairs = random.sample(inversion_pairs, min(2, len(inversion_pairs)))
        
        # Create a prompt to generate a paradox
        pairs_text = ""
        for i, (assumption, inversion) in enumerate(selected_pairs):
            pairs_text += f"{i+1}. Conventional assumption: {assumption}\n"
            pairs_text += f"   Inverted assumption: {inversion}\n\n"
        
        prompt = f"""In the domain of {domain}, consider these inversions of conventional assumptions:

{pairs_text}

Generate a productive paradox that forces both the conventional assumptions AND their inversions to be simultaneously true. This paradox should:

1. Create cognitive dissonance
2. Force a reconceptualization of the problem space
3. Suggest new creative possibilities precisely because of its paradoxical nature

The paradox should not be a logical contradiction but rather a provocative reframing that challenges conventional thinking while maintaining some form of internal coherence.

Formulate this as a concise paradoxical statement or principle that could guide creative thinking."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=9000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract paradox from thinking
        paradox = self._extract_paradox(thinking_step.reasoning_process)
        
        return paradox
    
    def _extract_paradox(self, thinking_text: str) -> str:
        """
        Extract a paradox from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted paradox
        """
        # Look for paradox indicators
        paradox_indicators = [
            "Paradox:", "Paradoxical principle:", "Productive paradox:",
            "Paradoxical statement:", "The paradox is:"
        ]
        
        for indicator in paradox_indicators:
            if indicator in thinking_text:
                # Extract text after the indicator
                start_idx = thinking_text.find(indicator) + len(indicator)
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                paradox = thinking_text[start_idx:end_idx].strip()
                if paradox:
                    return paradox
        
        # If no structured indicator, look for quotation marks
        import re
        quotes = re.findall(r'"([^"]*)"', thinking_text)
        if quotes:
            return quotes[0]
        
        # Fallback: return the last paragraph
        paragraphs = thinking_text.split("\n\n")
        if paragraphs:
            return paragraphs[-1].strip()
        
        return "No paradox found"


class DisruptorModule:
    """
    Creates conceptual superpositions by forcing paradoxical states and challenging assumptions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Disruptor Module.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.assumption_detector = AssumptionDetector(self.api_key)
        self.inversion_engine = InversionEngine()
        self.paradox_generator = ParadoxGenerator(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.superposition_engine = SuperpositionEngine()
    
    async def disrupt(self, problem_statement: str, domain: str) -> Dict[str, Any]:
        """
        Disrupt a problem by challenging assumptions and generating paradoxes.
        
        Args:
            problem_statement: The problem statement to disrupt
            domain: The domain of the problem
            
        Returns:
            Dict[str, Any]: Results of the disruption including assumptions, inversions, paradoxes, and ideas
        """
        # Step 1: Detect assumptions
        assumptions = await self.assumption_detector.detect_assumptions(problem_statement, domain)
        
        # Step 2: Generate inversions
        inversion_pairs = self.inversion_engine.generate_inversions(assumptions)
        
        # Step 3: Generate paradoxes
        paradox = await self.paradox_generator.generate_paradox(inversion_pairs, domain)
        
        # Step 4: Generate disruptive idea based on paradox
        idea = await self._generate_disruptive_idea(problem_statement, paradox, inversion_pairs, domain)
        
        # Create results
        results = {
            "assumptions": assumptions,
            "inversions": inversion_pairs,
            "paradox": paradox,
            "idea": idea
        }
        
        return results
    
    async def _generate_disruptive_idea(self, problem_statement: str, paradox: str, 
                                     inversion_pairs: List[Tuple[str, str]], domain: str) -> CreativeIdea:
        """
        Generate a disruptive idea based on a paradox.
        
        Args:
            problem_statement: The problem statement
            paradox: The generated paradox
            inversion_pairs: Pairs of (assumption, inversion)
            domain: The domain of the problem
            
        Returns:
            CreativeIdea: The generated disruptive idea
        """
        # Create a prompt for the disruptive idea
        inversions_text = ""
        for i, (assumption, inversion) in enumerate(inversion_pairs):
            inversions_text += f"{i+1}. Conventional: {assumption} ↔ Inverted: {inversion}\n"
        
        prompt = f"""Problem: {problem_statement}

Domain: {domain}

Paradoxical principle: {paradox}

Assumption inversions:
{inversions_text}

Generate a disruptive idea that embraces the paradox above while solving the problem. Your idea should:

1. Make the paradox a central feature, not a bug
2. Violate multiple conventional assumptions in the domain
3. Force a reconceptualization of the problem space itself
4. Create cognitive dissonance in domain experts
5. Maintain internal coherence despite its paradoxical nature

Think step by step, first examining how the paradox changes the problem space, then exploring the solution landscape that emerges when conventional assumptions are violated."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract idea from thinking
        description = self._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the disruptive idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.9,  # High because it's based on paradoxes
            impossibility_score=0.8,
            utility_potential=0.6,
            expert_rejection_probability=0.85,
            composite_shock_value=0.85
        )
        
        # Create a disruptive idea
        disruptive_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="disruptor",
            impossibility_elements=[pair[1] for pair in inversion_pairs[:3]],  # Use inversions as impossibility elements
            contradiction_elements=[paradox],  # Use paradox as contradiction element
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return disruptive_idea
    
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
            "In conclusion", "Therefore", "My disruptive idea", "The idea is", 
            "The disruptive concept", "Final idea", "The breakthrough concept", 
            "The innovative approach"
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