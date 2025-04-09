"""
Connector Module - Establishes conceptual entanglement between distant ideas and domains.

Implements prompts: connector_bridge_mechanism.txt, connector_conceptual_distance.txt
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
from ..prompt_management import uses_prompt


@uses_prompt("connector_conceptual_distance")
class ConceptualDistanceCalculator:
    """
    Calculates semantic distance between concepts and domains.
    
    This class implements the connector_conceptual_distance.txt prompt to measure
    semantic and conceptual distance between ideas from different domains.
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
        if not concept_descriptions or len(concept_descriptions) < 2:
            return []
        
        # Use the prompt_loader to get the prompt template
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Format the concepts and domains for the prompt
        primary_domain = domains[0]
        focal_concept = concept_descriptions[0]
        
        # If we have multiple concepts, include them in the focal concept description
        if len(concept_descriptions) > 1:
            concepts_text = "\n\n".join([f"Concept from {domain}: {desc}" for desc, domain in 
                                       zip(concept_descriptions[1:], domains[1:])])
            focal_concept = f"{focal_concept}\n\nAdditional concepts to consider:\n{concepts_text}"
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "connector_conceptual_distance",
            {
                "primary_domain": primary_domain,
                "focal_concept": focal_concept
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load connector_conceptual_distance prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=12000,  # Increased for more comprehensive analysis
            max_tokens=15000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract distance pairs using structured extraction
        distance_pairs = self._extract_distance_pairs_structured(thinking_step.reasoning_process)
        
        # If structured extraction fails, fall back to simple extraction
        if not distance_pairs:
            distance_pairs = self._extract_distance_pairs(thinking_step.reasoning_process, len(concept_descriptions))
        
        return distance_pairs
    
    def _extract_distance_pairs_structured(self, thinking_text: str) -> List[Tuple[str, str, float]]:
        """
        Extract distance pairs from thinking text using structured extraction.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[Tuple[str, str, float]]: List of (domain1, domain2, distance) tuples
        """
        import re
        pairs = []
        
        # Extract from distance_metrics section
        metrics_match = re.search(r'<distance_metrics>(.*?)</distance_metrics>', thinking_text, re.DOTALL)
        if metrics_match:
            metrics_text = metrics_match.group(1).strip()
            
            # Look for domain pairs with distance scores
            domain_pairs = re.finditer(r'(\w+)(?:\s+and\s+|\s*-\s*)(\w+)(?:.*?)(\d+(?:\.\d+)?)', metrics_text, re.DOTALL)
            
            for match in domain_pairs:
                try:
                    domain1 = match.group(1).strip()
                    domain2 = match.group(2).strip()
                    distance = float(match.group(3))
                    
                    # Normalize distance to 0.0-1.0 scale if needed
                    if distance > 10.0:
                        distance = distance / 100.0
                    elif distance > 1.0:
                        distance = distance / 10.0
                    
                    pairs.append((domain1, domain2, distance))
                except (ValueError, IndexError):
                    # Skip if parsing fails
                    continue
        
        # Try another section if the first attempt failed
        if not pairs:
            unexpected_match = re.search(r'<unexpected_connections>(.*?)</unexpected_connections>', 
                                       thinking_text, re.DOTALL)
            if unexpected_match:
                connections_text = unexpected_match.group(1).strip()
                
                # Look for domain mentions with potential distance indicators
                domains = re.findall(r'(?:^|\n)(?:\d+\.\s*|\*\s*|\-\s*)(?:From\s+)?(\w+)(?:\s+to\s+|\s+and\s+)(\w+)', 
                                    connections_text)
                
                for domain1, domain2 in domains:
                    # Assign a high distance score since these are unexpected connections
                    pairs.append((domain1, domain2, 0.8))
        
        # Sort by distance (descending)
        pairs.sort(key=lambda x: x[2], reverse=True)
        
        return pairs
    
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


@uses_prompt("connector_bridge_mechanism")
class BridgeMechanismIdentifier:
    """
    Discovers potential connection points between distant domains and concepts.
    
    This class implements the connector_bridge_mechanism.txt prompt to identify
    conceptual bridges that can connect seemingly unrelated domains and concepts.
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
        
        # Use the prompt_loader to get the prompt template
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Create the bridging challenge from the concepts
        bridging_challenge = f"Discover bridge mechanisms between '{concept1}' from {domain1} and '{concept2}' from {domain2}."
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "connector_bridge_mechanism",
            {
                "domain_a": f"{domain1}: {concept1}",
                "domain_b": f"{domain2}: {concept2}",
                "bridging_challenge": bridging_challenge
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load connector_bridge_mechanism prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=12000,  # Increased budget for more comprehensive analysis
            max_tokens=15000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract bridges from thinking using structural extraction
        identified_bridges = self._extract_bridges_structured(thinking_step.reasoning_process)
        
        # If structured extraction fails, fall back to simple extraction
        if not identified_bridges:
            identified_bridges = self._extract_bridges(thinking_step.reasoning_process)
        
        # Combine with common bridges, prioritizing the identified ones
        all_bridges = identified_bridges + [b for b in bridges if b not in identified_bridges]
        
        return all_bridges[:5]  # Limit to 5 bridges
    
    def _extract_bridges_structured(self, thinking_text: str) -> List[str]:
        """
        Extract bridges from thinking text using structured extraction.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            List[str]: Extracted bridges
        """
        import re
        bridges = []
        
        # Look for structured bridge sections
        bridge_sections = [
            (r'<conceptual_bridges>(.*?)</conceptual_bridges>', 'Conceptual Bridge: '),
            (r'<methodological_bridges>(.*?)</methodological_bridges>', 'Methodological Bridge: '),
            (r'<structural_bridges>(.*?)</structural_bridges>', 'Structural Bridge: '),
            (r'<emergent_frameworks>(.*?)</emergent_frameworks>', 'Emergent Framework: ')
        ]
        
        for pattern, prefix in bridge_sections:
            section_match = re.search(pattern, thinking_text, re.DOTALL)
            if section_match:
                section_text = section_match.group(1).strip()
                
                # Extract individual bridges from the section
                # Look for numbered or bulleted items
                items = re.findall(r'(?:\d+\.\s*|\*\s*|\-\s*)([^\n]+)', section_text)
                
                for item in items:
                    # Clean up and add prefix
                    bridge = prefix + item.strip()
                    bridges.append(bridge)
        
        return bridges
    
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


@uses_prompt("connector_bridge_mechanism", dependencies=["connector_conceptual_distance"])
class ConceptualBlendingEngine:
    """
    Forces integration between distinct conceptual frames.
    
    This class implements conceptual blending based on identified bridge mechanisms
    to create novel conceptual integrations across domains.
    
    Depends on prompt: connector_conceptual_distance.txt
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
                          bridges: List[str]) -> Dict[str, Any]:
        """
        Blend two concepts from different domains using quantum-inspired entanglement.
        
        Args:
            concept1: First concept
            domain1: Domain of first concept
            concept2: Second concept
            domain2: Domain of second concept
            bridges: Bridge mechanisms
            
        Returns:
            Dict[str, Any]: Entangled blend with quantum properties
        """
        # Use the prompt_loader to get the quantum entanglement prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # First, establish quantum entanglement between the concepts
        entanglement_prompt = prompt_loader.render_prompt(
            "quantum_entanglement",
            {
                "concept_a": f"{concept1} ({domain1})",
                "concept_b": f"{concept2} ({domain2})",
                "domain": f"Bridge between {domain1} and {domain2}",
                "problem_statement": f"Create a conceptual entanglement using these bridge mechanisms: {', '.join(bridges[:3])}"
            }
        )
        
        if not entanglement_prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load quantum_entanglement prompt template")
        
        # Generate thinking for quantum entanglement
        entanglement_thinking = await self.claude_client.generate_thinking(
            prompt=entanglement_prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract quantum entanglement properties
        entanglement = self._extract_quantum_entanglement(entanglement_thinking.reasoning_process)
        
        # Format bridges as a list of bullet points
        bridges_text = "\n".join([f"- {bridge}" for bridge in bridges])
        
        # Use the quantum_blend prompt template
        quantum_blend_prompt = prompt_loader.render_prompt(
            "quantum_blend",
            {
                "concept1": concept1,
                "domain1": domain1,
                "concept2": concept2,
                "domain2": domain2,
                "bridges": bridges_text,
                "entanglement_basis": entanglement.get('entanglement_basis', 'Unknown'),
                "correlation_properties": entanglement.get('correlation_properties', 'Unknown'),
                "propagation_rules": entanglement.get('propagation_rules', 'Unknown'),
                "measurement_implications": entanglement.get('measurement_implications', 'Unknown')
            }
        )
        
        if not quantum_blend_prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load quantum_blend prompt template")
        
        # Generate thinking for the blend
        blend_thinking = await self.claude_client.generate_thinking(
            prompt=quantum_blend_prompt,
            thinking_budget=16000,
            max_tokens=20000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract blended concept from thinking
        blended_concept = self._extract_blend(blend_thinking.reasoning_process)
        
        # Combine the entanglement and blend information
        result = {
            "blend": blended_concept,
            "entanglement_basis": entanglement.get("entanglement_basis", ""),
            "correlation_properties": entanglement.get("correlation_properties", ""),
            "propagation_rules": entanglement.get("propagation_rules", ""),
            "entanglement_characteristics": entanglement.get("entanglement_characteristics", {}),
            "measurement_implications": entanglement.get("measurement_implications", ""),
            "creative_applications": entanglement.get("creative_applications", "")
        }
        
        return result
    
    def _extract_quantum_entanglement(self, thinking_text: str) -> Dict[str, Any]:
        """
        Extract quantum entanglement properties from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Dict[str, Any]: Extracted quantum entanglement properties
        """
        import re
        result = {}
        
        # Extract entanglement basis
        basis_match = re.search(r'<entanglement_basis>(.*?)</entanglement_basis>', thinking_text, re.DOTALL)
        if basis_match:
            result["entanglement_basis"] = basis_match.group(1).strip()
        
        # Extract correlation properties
        correlation_match = re.search(r'<correlation_properties>(.*?)</correlation_properties>', thinking_text, re.DOTALL)
        if correlation_match:
            result["correlation_properties"] = correlation_match.group(1).strip()
        
        # Extract propagation rules
        propagation_match = re.search(r'<propagation_rules>(.*?)</propagation_rules>', thinking_text, re.DOTALL)
        if propagation_match:
            result["propagation_rules"] = propagation_match.group(1).strip()
        
        # Extract entanglement characteristics
        characteristics_match = re.search(r'<entanglement_characteristics>(.*?)</entanglement_characteristics>', 
                                        thinking_text, re.DOTALL)
        if characteristics_match:
            characteristics_text = characteristics_match.group(1).strip()
            # Try to parse JSON-like format
            try:
                import json
                # Clean up the text to make it valid JSON
                json_text = re.sub(r'//.*', '', characteristics_text)  # Remove comments
                json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
                characteristics = json.loads(json_text)
                result["entanglement_characteristics"] = characteristics
            except:
                # If parsing fails, extract individual metrics
                strength_match = re.search(r'"strength":\s*(\d+\.\d+)', characteristics_text)
                if strength_match:
                    result["entanglement_characteristics"] = {
                        "strength": float(strength_match.group(1))
                    }
                    
                    # Try to extract other metrics
                    for metric in ["symmetry", "stability", "transfer_potential"]:
                        metric_match = re.search(fr'"{metric}":\s*(\d+\.\d+)', characteristics_text)
                        if metric_match:
                            result["entanglement_characteristics"][metric] = float(metric_match.group(1))
        
        # Extract measurement implications
        measurement_match = re.search(r'<measurement_implications>(.*?)</measurement_implications>', 
                                     thinking_text, re.DOTALL)
        if measurement_match:
            result["measurement_implications"] = measurement_match.group(1).strip()
        
        # Extract creative applications
        applications_match = re.search(r'<creative_applications>(.*?)</creative_applications>', 
                                     thinking_text, re.DOTALL)
        if applications_match:
            result["creative_applications"] = applications_match.group(1).strip()
        
        return result
    
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


@uses_prompt("connector_bridge_mechanism", dependencies=[
    "connector_conceptual_distance", 
    "quantum_entanglement", 
    "domain_concept_generation",
    "quantum_blend",
    "quantum_connected_idea",
    "connected_idea"
])
class ConnectorModule:
    """
    Establishes conceptual entanglement between distant ideas and domains.
    
    This class coordinates distance calculation, bridge identification, and conceptual blending
    to create novel connections between distant domains and concepts.
    
    Depends on prompts: 
    - connector_conceptual_distance.txt - For calculating conceptual distance
    - quantum_entanglement.txt - For entangling concepts 
    - domain_concept_generation.txt - For generating domain-specific concepts
    - quantum_blend.txt - For blending concepts using quantum principles
    - quantum_connected_idea.txt - For generating quantum-inspired creative ideas
    - connected_idea.txt - For generating blended creative ideas
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
        Connect distant concepts to generate creative ideas using quantum-inspired processes.
        
        Args:
            problem_statement: The problem statement
            domains: List of domains to connect
            
        Returns:
            Dict[str, Any]: Results of the connection process including quantum entanglement properties
        """
        # Step 1: Find most distant domains using enhanced distance calculator
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
        
        # Step 3: Identify bridge mechanisms using enhanced bridge identifier
        bridges = await self.bridge_identifier.identify_bridges(
            concepts[distant_domains[0]], distant_domains[0],
            concepts[distant_domains[1]], distant_domains[1]
        )
        
        # Step 4: Blend concepts using quantum-inspired entanglement
        quantum_blend = await self.blending_engine.blend_concepts(
            concepts[distant_domains[0]], distant_domains[0],
            concepts[distant_domains[1]], distant_domains[1],
            bridges
        )
        
        # Step 5: Create quantum-entangled concept objects for superposition engine
        await self._create_entangled_concepts(
            concepts, 
            distant_domains, 
            quantum_blend,
            problem_statement
        )
        
        # Step 6: Generate connected idea with quantum properties
        idea = await self._generate_quantum_connected_idea(
            problem_statement, 
            concepts, 
            bridges, 
            quantum_blend, 
            distant_domains
        )
        
        # Create comprehensive results with quantum properties
        results = {
            "domains": distant_domains,
            "concepts": concepts,
            "bridges": bridges,
            "quantum_blend": quantum_blend,
            "idea": idea,
            "entanglement_properties": {
                "basis": quantum_blend.get("entanglement_basis", ""),
                "correlation": quantum_blend.get("correlation_properties", ""),
                "propagation": quantum_blend.get("propagation_rules", ""),
                "measurement": quantum_blend.get("measurement_implications", ""),
                "characteristics": quantum_blend.get("entanglement_characteristics", {})
            }
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
        
        # Use the prompt_loader to get the domain concept generation prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        for domain in domains:
            # Render the prompt template with context
            prompt = prompt_loader.render_prompt(
                "domain_concept_generation",
                {
                    "domain": domain,
                    "problem_statement": problem_statement
                }
            )
            
            if not prompt:
                # Fallback in case prompt loading fails
                raise ValueError(f"Failed to load domain_concept_generation prompt template")
            
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
    
    async def _create_entangled_concepts(self, concepts: Dict[str, str], 
                                  domains: Tuple[str, str], 
                                  quantum_blend: Dict[str, Any],
                                  problem_statement: str) -> Dict[UUID4, Concept]:
        """
        Create quantum-entangled concept objects in the superposition engine.
        
        Args:
            concepts: Map of domain to concept
            domains: Tuple of domains
            quantum_blend: Results of quantum blending
            problem_statement: The problem statement
            
        Returns:
            Dict[UUID4, Concept]: Map of concept IDs to created concept objects
        """
        concept_objects = {}
        
        # Extract entanglement properties
        entanglement_type = "correlated"
        correlation_strength = quantum_blend.get("entanglement_characteristics", {}).get("strength", 0.8)
        evolution_rules = quantum_blend.get("propagation_rules", "Changes propagate based on conceptual similarity")
        
        # Create concept objects for each domain
        for domain in domains:
            # Create basic concept
            concept_obj = Concept(
                name=f"{domain.capitalize()} Concept",
                domain=domain,
                definition=concepts[domain],
                attributes={
                    "problem_context": problem_statement,
                    "entanglement_basis": quantum_blend.get("entanglement_basis", ""),
                    "domain_specific_lens": domain
                }
            )
            
            # Add concept to superposition engine
            concept_id = self.superposition_engine.add_concept(concept_obj)
            concept_objects[domain] = concept_id
            
            # Create possible superposition states
            superposition_states = [
                # Standard interpretation
                (concepts[domain], 0.5, ["standard", domain]),
                
                # Blend-influenced interpretation
                (quantum_blend.get("blend", ""), 0.3, ["blended", "quantum"]),
                
                # Emergent interpretation (with elements from both domains)
                (f"Emergent {domain} perspective: {concepts[domain]} with elements of quantum entanglement", 
                 0.2, ["emergent", "quantum"])
            ]
            
            # Add superposition states
            self.superposition_engine.create_superposition(concept_id, superposition_states)
        
        # Create entanglement between the concepts
        self.superposition_engine.entangle_concepts(
            concept_objects[domains[0]], 
            concept_objects[domains[1]],
            entanglement_type,
            correlation_strength,
            evolution_rules
        )
        
        return {domain: concept_id for domain, concept_id in concept_objects.items()}
    
    async def _generate_quantum_connected_idea(self, problem_statement: str, 
                                            concepts: Dict[str, str], 
                                            bridges: List[str], 
                                            quantum_blend: Dict[str, Any], 
                                            domains: Tuple[str, str]) -> CreativeIdea:
        """
        Generate a connected idea based on quantum-entangled blended concepts.
        
        Args:
            problem_statement: The problem statement
            concepts: Map of domain to concept
            bridges: Bridge mechanisms
            quantum_blend: Quantum blend results
            domains: Tuple of domains
            
        Returns:
            CreativeIdea: The generated connected idea with quantum properties
        """
        # Use the prompt_loader to get the quantum connected idea prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Format the concepts text
        concepts_text = ""
        for domain, concept in concepts.items():
            concepts_text += f"{domain.capitalize()} Concept: {concept}\n\n"
        
        # Format bridges text
        bridges_text = "\n".join([f"- {bridge}" for bridge in bridges])
        
        # Get the blended concept
        blend = quantum_blend.get("blend", "")
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "quantum_connected_idea",
            {
                "problem_statement": problem_statement,
                "concepts_text": concepts_text,
                "bridges_text": bridges_text,
                "blend": blend,
                "entanglement_basis": quantum_blend.get('entanglement_basis', 'Unknown'),
                "correlation_properties": quantum_blend.get('correlation_properties', 'Unknown'),
                "propagation_rules": quantum_blend.get('propagation_rules', 'Unknown'),
                "measurement_implications": quantum_blend.get('measurement_implications', 'Unknown'),
                "domain1": domains[0],
                "domain2": domains[1]
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load quantum_connected_idea prompt template")
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=18000,  # Increased to allow for more thorough quantum exploration
            max_tokens=22000  # Ensure max_tokens > thinking_budget
        )
        
        # Extract idea from thinking
        description = self._extract_quantum_idea_description(thinking_step.reasoning_process)
        
        # Create a shock profile for the connected idea with quantum-enhanced metrics
        # Quantum-entangled ideas tend to be more novel and impossible, but also more potentially useful
        shock_profile = ShockProfile(
            novelty_score=0.95,  # Higher novelty for quantum-entangled ideas
            contradiction_score=0.85,  # Higher contradiction due to superposition
            impossibility_score=0.9,  # Higher impossibility score
            utility_potential=0.8,  # Higher utility potential despite impossibility
            expert_rejection_probability=0.9,  # Higher rejection due to quantum framing
            composite_shock_value=0.9  # Higher composite shock
        )
        
        # Extract potential impossibility elements from the quantum entanglement
        impossibility_elements = self._extract_impossibility_elements(
            thinking_step.reasoning_process,
            quantum_blend
        )
        
        # Create a connected idea with quantum properties
        connected_idea = CreativeIdea(
            id=uuid.uuid4(),
            description=description,
            generative_framework="quantum_connector",  # Label as quantum-enhanced
            domain=f"{domains[0]}-{domains[1]} entanglement",  # Combined domain
            impossibility_elements=impossibility_elements,
            contradiction_elements=[bridge for bridge in bridges[:3]],  # Use bridges as contradiction elements
            related_concepts=[],  # Will be populated by concept IDs in a full implementation
            shock_metrics=shock_profile
        )
        
        return connected_idea
    
    def _extract_quantum_idea_description(self, thinking_text: str) -> str:
        """
        Extract a quantum-enhanced idea description from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            str: Extracted quantum idea description
        """
        import re
        
        # Look for a quantum solution section
        quantum_section_match = re.search(r'<quantum_solution>(.*?)</quantum_solution>', 
                                         thinking_text, re.DOTALL)
        if quantum_section_match:
            return quantum_section_match.group(1).strip()
        
        # Try finding a final solution section
        final_solution_match = re.search(r'<final_solution>(.*?)</final_solution>', 
                                       thinking_text, re.DOTALL)
        if final_solution_match:
            return final_solution_match.group(1).strip()
        
        # Look for quantum-specific conclusion markers
        quantum_markers = [
            "Quantum Solution:", "Entangled Solution:", "Superposition Solution:",
            "The quantum-inspired approach", "Through quantum entanglement", 
            "The entangled concept solution"
        ]
        
        for marker in quantum_markers:
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
        
        # Fall back to the standard extraction method
        return self._extract_idea_description(thinking_text)
    
    def _extract_impossibility_elements(self, thinking_text: str, 
                                      quantum_blend: Dict[str, Any]) -> List[str]:
        """
        Extract impossibility elements from thinking text and quantum blend.
        
        Args:
            thinking_text: The thinking text to extract from
            quantum_blend: Quantum blend results
            
        Returns:
            List[str]: Extracted impossibility elements
        """
        impossibility_elements = []
        
        # Look for impossibility patterns in the thinking
        import re
        
        # Try to find a structured section for impossibilities
        impossibility_match = re.search(r'<impossibility_elements>(.*?)</impossibility_elements>', 
                                      thinking_text, re.DOTALL)
        if impossibility_match:
            elements_text = impossibility_match.group(1).strip()
            # Extract list items
            elements = re.findall(r'(?:\d+\.\s*|\*\s*|\-\s*)([^\n]+)', elements_text)
            impossibility_elements.extend([e.strip() for e in elements if e.strip()])
        
        # If no structured section, look for statements about impossibility
        if not impossibility_elements:
            impossibility_patterns = [
                r'impossible to (\w+[^.,;:!?]*)',
                r'violates (\w+[^.,;:!?]*)',
                r'contradicts (\w+[^.,;:!?]*)',
                r'breaks (\w+[^.,;:!?]*) assumptions',
                r'paradoxical (\w+[^.,;:!?]*)'
            ]
            
            for pattern in impossibility_patterns:
                matches = re.findall(pattern, thinking_text, re.IGNORECASE)
                for match in matches:
                    impossibility_elements.append(match.strip())
            
            # Limit to unique elements
            impossibility_elements = list(set(impossibility_elements))
        
        # Add elements from the quantum blend if available
        measurement_implications = quantum_blend.get("measurement_implications", "")
        if measurement_implications:
            # Extract potential impossibilities from measurement implications
            implications = re.findall(r'(?:\d+\.\s*|\*\s*|\-\s*)([^\n]+)', measurement_implications)
            for implication in implications:
                if any(keyword in implication.lower() for keyword in 
                      ["impossible", "violate", "contradict", "break", "paradox"]):
                    impossibility_elements.append(implication.strip())
        
        # Return a reasonable number of elements
        return impossibility_elements[:5]
    
    async def _generate_connected_idea(self, problem_statement: str, concepts: Dict[str, str], 
                                    bridges: List[str], blend: Dict[str, Any], 
                                    domains: Tuple[str, str]) -> CreativeIdea:
        """
        Legacy method kept for backward compatibility. 
        Use _generate_quantum_connected_idea instead for new development.
        
        Args:
            problem_statement: The problem statement
            concepts: Map of domain to concept
            bridges: Bridge mechanisms
            blend: Blended concept
            domains: Tuple of domains
            
        Returns:
            CreativeIdea: The generated connected idea
        """
        # Use the prompt_loader to get the connected idea prompt
        from ..prompt_management.prompt_loader import PromptLoader
        prompt_loader = PromptLoader()
        
        # Format the concepts text
        concepts_text = ""
        for domain, concept in concepts.items():
            concepts_text += f"{domain.capitalize()} Concept: {concept}\n\n"
        
        # Format bridges text
        bridges_text = "\n".join([f"- {bridge}" for bridge in bridges])
        
        # Get the blended concept string from the blend dictionary
        blend_text = blend.get("blend", "") if isinstance(blend, dict) else blend
        
        # Render the prompt template with context
        prompt = prompt_loader.render_prompt(
            "connected_idea",
            {
                "problem_statement": problem_statement,
                "concepts_text": concepts_text,
                "bridges_text": bridges_text,
                "blend_text": blend_text,
                "domain1": domains[0],
                "domain2": domains[1]
            }
        )
        
        if not prompt:
            # Fallback in case prompt loading fails
            raise ValueError(f"Failed to load connected_idea prompt template")
        
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