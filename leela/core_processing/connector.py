"""
Connector Module - Establishes conceptual entanglement between distant ideas and domains.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from pydantic import UUID4
import numpy as np
from ..config import get_config
from ..knowledge_representation.models import (
    Concept, CreativeIdea, ThinkingStep, ShockProfile, EntanglementLink
)
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..knowledge_representation.superposition_engine import SuperpositionEngine


class ConceptualDistanceCalculator:
    """
    Calculates semantic distance between concepts and domains.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Conceptual Distance Calculator.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Domain distance matrix (precomputed)
        # Higher value = more distant
        self.domain_distances = {
            ("physics", "biology"): 0.6,
            ("physics", "computer_science"): 0.7,
            ("physics", "economics"): 0.8,
            ("physics", "mathematics"): 0.4,
            ("biology", "computer_science"): 0.6,
            ("biology", "economics"): 0.7,
            ("biology", "mathematics"): 0.8,
            ("computer_science", "economics"): 0.6,
            ("computer_science", "mathematics"): 0.5,
            ("economics", "mathematics"): 0.7
        }
    
    def get_domain_distance(self, domain1: str, domain2: str) -> float:
        """
        Get the distance between two domains.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            float: Distance between domains (0.0-1.0)
        """
        # Normalize domain names
        domain1 = domain1.lower().replace(" ", "_")
        domain2 = domain2.lower().replace(" ", "_")
        
        # Return 0 if same domain
        if domain1 == domain2:
            return 0.0
        
        # Check if in precomputed distances
        key = (domain1, domain2) if domain1 < domain2 else (domain2, domain1)
        if key in self.domain_distances:
            return self.domain_distances[key]
        
        # Default distance if not found
        return 0.5
    
    def calculate_concept_distance(self, concept1: Concept, concept2: Concept) -> float:
        """
        Calculate the distance between two concepts.
        
        Args:
            concept1: First concept
            concept2: Second concept
            
        Returns:
            float: Distance between concepts (0.0-1.0)
        """
        # Start with domain distance
        distance = self.get_domain_distance(concept1.domain, concept2.domain)
        
        # Adjust based on attribute similarity
        common_attributes = set(concept1.attributes.keys()) & set(concept2.attributes.keys())
        attribute_similarity = len(common_attributes) / max(1, len(set(concept1.attributes.keys()) | set(concept2.attributes.keys())))
        
        # Invert similarity to get distance component
        attribute_distance = 1.0 - attribute_similarity
        
        # Combine domain and attribute distances
        combined_distance = 0.7 * distance + 0.3 * attribute_distance
        
        return min(1.0, combined_distance)
    
    def find_most_distant_domains(self, domains: List[str]) -> Tuple[str, str]:
        """
        Find the most distant domains in a list.
        
        Args:
            domains: List of domains
            
        Returns:
            Tuple[str, str]: The most distant domain pair
        """
        max_distance = -1
        most_distant_pair = (domains[0], domains[0])
        
        for i, domain1 in enumerate(domains):
            for domain2 in domains[i+1:]:
                distance = self.get_domain_distance(domain1, domain2)
                if distance > max_distance:
                    max_distance = distance
                    most_distant_pair = (domain1, domain2)
        
        return most_distant_pair
    
    async def find_distant_concepts(self, concept_descriptions: List[str], 
                                 domains: List[str]) -> List[Tuple[str, str, float]]:
        """
        Find pairs of distant concepts from descriptions.
        
        Args:
            concept_descriptions: List of concept descriptions
            domains: List of domains for the concepts
            
        Returns:
            List[Tuple[str, str, float]]: List of (concept1, concept2, distance) tuples
        """
        # Generate semantic embeddings for concepts
        # In a real implementation, we would use a proper embedding model
        # Here we'll use a simplified approach
        
        # Create a prompt for semantic distance calculation
        concepts_text = ""
        for i, (desc, domain) in enumerate(zip(concept_descriptions, domains)):
            concepts_text += f"Concept {i+1} ({domain}): {desc}\n\n"
        
        prompt = f"""Analyze the semantic distance between these concepts:

{concepts_text}

For each possible pair of concepts, rate their semantic distance on a scale from 0.0 (very similar) to 1.0 (maximally distant). 
Consider both the domain distance and the conceptual distance.

Format each pair as: "Concept X - Concept Y: [distance score]"

Focus on finding the most distant concept pairs - those that seem to have the least in common."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=9000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract distance pairs
        distance_pairs = self._extract_distance_pairs(thinking_step.reasoning_process, len(concept_descriptions))
        
        return distance_pairs
    
    def _extract_distance_pairs(self, thinking_text: str, num_concepts: int) -> List[Tuple[str, str, float]]:
        """
        Extract distance pairs from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            num_concepts: Number of concepts
            
        Returns:
            List[Tuple[str, str, float]]: List of (concept1, concept2, distance) tuples
        """
        import re
        
        # Pattern for "Concept X - Concept Y: [score]"
        pattern = r'Concept\s+(\d+)\s*-\s*Concept\s+(\d+):\s*(0\.\d+|1\.0)'
        matches = re.findall(pattern, thinking_text)
        
        distance_pairs = []
        for c1, c2, score in matches:
            concept_idx1 = int(c1) - 1  # Convert to 0-based index
            concept_idx2 = int(c2) - 1
            distance = float(score)
            
            # Ensure valid indices
            if 0 <= concept_idx1 < num_concepts and 0 <= concept_idx2 < num_concepts:
                distance_pairs.append((f"Concept {c1}", f"Concept {c2}", distance))
        
        # Sort by distance (descending)
        distance_pairs.sort(key=lambda x: x[2], reverse=True)
        
        return distance_pairs


class BridgeMechanismIdentifier:
    """
    Discovers potential connection points between distant domains and concepts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Bridge Mechanism Identifier.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        
        # Common bridge mechanisms
        self.bridge_mechanisms = {
            ("physics", "biology"): [
                "Energy transfer mechanisms", 
                "Self-organizing systems", 
                "Emergent complexity",
                "Feedback loops",
                "Scale-invariant patterns"
            ],
            ("physics", "computer_science"): [
                "Quantum computing", 
                "Information theory", 
                "Entropy concepts",
                "Parallel processing",
                "Computational irreducibility"
            ],
            ("physics", "economics"): [
                "Flow systems", 
                "Equilibrium concepts", 
                "Asymmetric forces",
                "Network effects",
                "Phase transitions"
            ],
            ("biology", "computer_science"): [
                "Evolutionary algorithms", 
                "Neural networks", 
                "Distributed systems",
                "Information processing",
                "Adaptive systems"
            ],
            ("biology", "economics"): [
                "Resource allocation", 
                "Competitive strategies", 
                "Cooperative behaviors",
                "Growth models",
                "Ecosystem dynamics"
            ],
            ("computer_science", "economics"): [
                "Game theory", 
                "Network theory", 
                "Distributed consensus",
                "Resource optimization",
                "Information markets"
            ]
        }
    
    def get_common_bridges(self, domain1: str, domain2: str) -> List[str]:
        """
        Get common bridge mechanisms between two domains.
        
        Args:
            domain1: First domain
            domain2: Second domain
            
        Returns:
            List[str]: Common bridge mechanisms
        """
        # Normalize domain names
        domain1 = domain1.lower().replace(" ", "_")
        domain2 = domain2.lower().replace(" ", "_")
        
        # Check if in precomputed bridges
        key = (domain1, domain2) if domain1 < domain2 else (domain2, domain1)
        if key in self.bridge_mechanisms:
            return self.bridge_mechanisms[key]
        
        # Default bridges if not found
        return [
            "Structural isomorphisms",
            "Process analogies",
            "Metaphorical mappings",
            "Common mathematical models",
            "Shared systemic principles"
        ]
    
    async def identify_bridges(self, concept1: str, domain1: str, concept2: str, domain2: str) -> List[str]:
        """
        Identify bridge mechanisms between two concepts from different domains.
        
        Args:
            concept1: First concept
            domain1: Domain of first concept
            concept2: Second concept
            domain2: Domain of second concept
            
        Returns:
            List[str]: Identified bridge mechanisms
        """
        # Start with common bridges
        bridges = self.get_common_bridges(domain1, domain2)
        
        # Create a prompt to identify specific bridges
        prompt = f"""Identify potential bridge mechanisms between these two distant concepts from different domains:

Concept 1 ({domain1}): {concept1}

Concept 2 ({domain2}): {concept2}

A bridge mechanism is a conceptual framework, model, principle, or analogy that could connect these seemingly unrelated ideas. 
The best bridges reveal unexpected commonalities or isomorphisms between the concepts.

Identify at least 5 specific bridge mechanisms that could connect these concepts, focusing on:
1. Structural similarities despite surface differences
2. Common underlying principles or patterns
3. Metaphorical mappings that reveal hidden connections
4. Isomorphic processes or dynamics
5. Shared mathematical or logical frameworks

For each bridge, provide a concise name and a brief explanation of how it connects the concepts."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=9000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract bridges from thinking
        identified_bridges = self._extract_bridges(thinking_step.reasoning_process)
        
        # Combine with common bridges
        all_bridges = bridges + [b for b in identified_bridges if b not in bridges]
        
        return all_bridges[:5]  # Limit to 5 bridges
    
    def _extract_bridges(self, thinking_text: str) -> List[str]:
        """
        Extract bridges from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[str]: Extracted bridges
        """
        bridges = []
        
        # Look for numbered or bulleted lists with bridge names
        import re
        
        # Pattern for numbered list items with name + explanation
        numbered_pattern = r'\d+\.\s+(?:Bridge:?\s+)?([^:\n]+)(?:[:\-]|(?=\n))'
        numbered_matches = re.findall(numbered_pattern, thinking_text)
        
        # Pattern for bulleted list items with name + explanation
        bulleted_pattern = r'[-*•]\s+(?:Bridge:?\s+)?([^:\n]+)(?:[:\-]|(?=\n))'
        bulleted_matches = re.findall(bulleted_pattern, thinking_text)
        
        # Combine matches
        matches = numbered_matches + bulleted_matches
        
        # Clean and add to bridges
        for match in matches:
            bridge = match.strip()
            # Only add if not too short and not too long
            if 3 < len(bridge) < 100:
                bridges.append(bridge)
        
        # If no structured list is found, look for quoted bridges
        if not bridges:
            quotes = re.findall(r'"([^"]*)"', thinking_text)
            for quote in quotes:
                if 3 < len(quote) < 100:
                    bridges.append(quote)
        
        return bridges


class ConceptualBlendingEngine:
    """
    Forces integration between distinct conceptual frames.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Conceptual Blending Engine.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def blend_concepts(self, concept1: str, domain1: str, concept2: str, domain2: str, 
                          bridges: List[str]) -> str:
        """
        Blend two concepts from different domains.
        
        Args:
            concept1: First concept
            domain1: Domain of first concept
            concept2: Second concept
            domain2: Domain of second concept
            bridges: Bridge mechanisms
            
        Returns:
            str: Blended concept description
        """
        # Create a prompt for conceptual blending
        bridges_text = "\n".join([f"- {bridge}" for bridge in bridges])
        
        prompt = f"""Create a conceptual blend between these two concepts from different domains:

Input Space 1 ({domain1}): {concept1}

Input Space 2 ({domain2}): {concept2}

Bridge Mechanisms:
{bridges_text}

A conceptual blend creates a new mental space that selectively projects elements from both input spaces, developing emergent structure that wasn't in either input.

Follow these steps to create a powerful conceptual blend:

1. Cross-space mapping: Identify correspondences between elements in the input spaces
2. Selective projection: Choose which elements from each input to include in the blend
3. Composition: Assemble the projected elements into a partial structure
4. Completion: Fill out the blend using background knowledge
5. Elaboration: Develop the emergent structure ("running the blend")

The most creative blends create conceptual clash that forces new, emergent meaning that resolves the tension between the input spaces.

Create a detailed description of a novel conceptual blend that:
- Has a clear, concise name
- Combines elements from both input concepts in unexpected ways
- Creates emergent structure not present in either input
- Uses one or more bridge mechanisms to establish cross-domain connections
- Resolves the conceptual tension in a surprising way"""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract blended concept from thinking
        blended_concept = self._extract_blend(thinking_step.reasoning_process)
        
        return blended_concept
    
    def _extract_blend(self, thinking_text: str) -> str:
        """
        Extract a blended concept from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted blended concept
        """
        # Look for blend indicators
        blend_indicators = [
            "Conceptual Blend:", "Blended Concept:", "The blend is:",
            "Blend Name:", "Blended Space:"
        ]
        
        for indicator in blend_indicators:
            if indicator in thinking_text:
                # Extract text after the indicator until the next double newline
                start_idx = thinking_text.find(indicator) + len(indicator)
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                # Extract and clean the text
                blend = thinking_text[start_idx:end_idx].strip()
                
                return blend
        
        # If no indicator found, look for a section with "blend" in the header
        import re
        sections = re.split(r'\n#+\s+', thinking_text)
        for section in sections:
            if "blend" in section.lower().split('\n')[0]:
                lines = section.split('\n')
                # Remove the header if it's still there
                if "blend" in lines[0].lower():
                    lines = lines[1:]
                return '\n'.join(lines).strip()
        
        # Fallback: return the last paragraph
        paragraphs = thinking_text.split("\n\n")
        if paragraphs:
            return paragraphs[-1].strip()
        
        # Extreme fallback
        return "No blend found"


class ConnectorModule:
    """
    Establishes conceptual entanglement between distant ideas and domains.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Connector Module.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.distance_calculator = ConceptualDistanceCalculator(self.api_key)
        self.bridge_identifier = BridgeMechanismIdentifier(self.api_key)
        self.blending_engine = ConceptualBlendingEngine(self.api_key)
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.superposition_engine = SuperpositionEngine()
    
    async def connect(self, problem_statement: str, domains: List[str]) -> Dict[str, Any]:
        """
        Connect distant concepts to generate creative ideas.
        
        Args:
            problem_statement: The problem statement
            domains: List of domains to connect
            
        Returns:
            Dict[str, Any]: Results of the connection process
        """
        # Step 1: Find most distant domains
        if len(domains) >= 2:
            distant_domains = self.distance_calculator.find_most_distant_domains(domains)
        else:
            # If only one domain provided, pair it with a distant domain
            all_domains = ["physics", "biology", "computer_science", "economics", "mathematics"]
            other_domains = [d for d in all_domains if d != domains[0]]
            import random
            distant_domains = (domains[0], random.choice(other_domains))
        
        # Step 2: Generate concepts in each domain
        concepts = await self._generate_domain_concepts(problem_statement, distant_domains)
        
        # Step 3: Identify bridge mechanisms
        bridges = await self.bridge_identifier.identify_bridges(
            concepts[distant_domains[0]], distant_domains[0],
            concepts[distant_domains[1]], distant_domains[1]
        )
        
        # Step 4: Blend concepts
        blend = await self.blending_engine.blend_concepts(
            concepts[distant_domains[0]], distant_domains[0],
            concepts[distant_domains[1]], distant_domains[1],
            bridges
        )
        
        # Step 5: Generate connected idea
        idea = await self._generate_connected_idea(problem_statement, concepts, bridges, blend, distant_domains)
        
        # Create results
        results = {
            "domains": distant_domains,
            "concepts": concepts,
            "bridges": bridges,
            "blend": blend,
            "idea": idea
        }
        
        return results
    
    async def _generate_domain_concepts(self, problem_statement: str, 
                                     domains: Tuple[str, str]) -> Dict[str, str]:
        """
        Generate concepts in each domain relevant to the problem.
        
        Args:
            problem_statement: The problem statement
            domains: Tuple of domains
            
        Returns:
            Dict[str, str]: Map of domain to concept
        """
        concepts = {}
        
        for domain in domains:
            # Create a prompt to generate a domain-specific concept
            prompt = f"""Generate a concept in the domain of {domain} that could be relevant to this problem:

{problem_statement}

The concept should be:
1. Deeply rooted in the principles and paradigms of {domain}
2. Specific and well-defined, not generic
3. Potentially useful for approaching the problem, but from a domain-specific perspective
4. Expressed in the native terminology and frameworks of {domain}

Formulate this as a concise concept definition (2-4 sentences) with a clear title."""
            
            # Generate thinking
            thinking_step = await self.claude_client.generate_thinking(
                prompt=prompt,
                thinking_budget=8000,
                max_tokens=9000  # Ensure max_tokens > thinking_budget
            )
            
            # Extract concept from thinking
            concept = self._extract_concept(thinking_step.reasoning_process)
            concepts[domain] = concept
        
        return concepts
    
    def _extract_concept(self, thinking_text: str) -> str:
        """
        Extract a concept from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted concept
        """
        # Look for concept indicators
        concept_indicators = [
            "Concept:", "Definition:", "Title:", 
            "Concept Title:", "Domain Concept:"
        ]
        
        for indicator in concept_indicators:
            if indicator in thinking_text:
                # Extract text after the indicator until the next double newline
                start_idx = thinking_text.find(indicator) + len(indicator)
                end_idx = thinking_text.find("\n\n", start_idx)
                if end_idx == -1:
                    end_idx = len(thinking_text)
                
                # Extract and clean the text
                concept = thinking_text[start_idx:end_idx].strip()
                
                return concept
        
        # If no indicator found, look for a bolded or all-caps title followed by text
        import re
        bold_pattern = r'\*\*([^*]+)\*\*\s*((?:.+\n)+)'
        bold_match = re.search(bold_pattern, thinking_text)
        if bold_match:
            return f"{bold_match.group(1)}: {bold_match.group(2).strip()}"
        
        caps_pattern = r'([A-Z][A-Z\s]+[A-Z])\s*((?:.+\n)+)'
        caps_match = re.search(caps_pattern, thinking_text)
        if caps_match:
            return f"{caps_match.group(1)}: {caps_match.group(2).strip()}"
        
        # Fallback: return the first paragraph
        paragraphs = thinking_text.split("\n\n")
        if paragraphs:
            return paragraphs[0].strip()
        
        # Extreme fallback
        return "No concept found"
    
    async def _generate_connected_idea(self, problem_statement: str, concepts: Dict[str, str], 
                                    bridges: List[str], blend: str, 
                                    domains: Tuple[str, str]) -> CreativeIdea:
        """
        Generate a connected idea based on blended concepts.
        
        Args:
            problem_statement: The problem statement
            concepts: Map of domain to concept
            bridges: Bridge mechanisms
            blend: Blended concept
            domains: Tuple of domains
            
        Returns:
            CreativeIdea: The generated connected idea
        """
        # Create a prompt for the connected idea
        concepts_text = ""
        for domain, concept in concepts.items():
            concepts_text += f"{domain.capitalize()} Concept: {concept}\n\n"
        
        bridges_text = "\n".join([f"- {bridge}" for bridge in bridges])
        
        prompt = f"""Problem: {problem_statement}

Domain Concepts:
{concepts_text}

Bridge Mechanisms:
{bridges_text}

Conceptual Blend:
{blend}

Generate a creative solution to the problem that leverages the conceptual blend. Your solution should:

1. Apply the blended concept to the problem in a non-obvious way
2. Draw on insights from both domains ({domains[0]} and {domains[1]})
3. Use at least one bridge mechanism to maintain coherence
4. Create cognitive dissonance while remaining potentially valuable
5. Transform the problem space itself through the cross-domain connection

Think step by step, exploring how the conceptual blend reveals a solution path that neither domain could access independently."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract idea from thinking
        description = self._extract_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the connected idea
        shock_profile = ShockProfile(
            novelty_score=0.9,
            contradiction_score=0.7,
            impossibility_score=0.8,
            utility_potential=0.7,
            expert_rejection_probability=0.85,
            composite_shock_value=0.8
        )
        
        # Create a connected idea
        connected_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="connector",
            impossibility_elements=[],
            contradiction_elements=[bridge for bridge in bridges[:2]],  # Use bridges as contradiction elements
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        return connected_idea
    
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
            "In conclusion", "Therefore", "My connected idea", "The solution is", 
            "The connected concept", "Final idea", "The breakthrough solution", 
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