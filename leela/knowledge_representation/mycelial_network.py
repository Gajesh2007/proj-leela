"""
Mycelial Network Model - Implements edge-focused decomposition-construction creative processes.

This module provides an alternative metaphor for creativity based on mycelial networks,
where ideas grow through decomposition, interconnection, and nutrient exchange at the edges.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import uuid
import random
import networkx as nx
from datetime import datetime
from pydantic import UUID4
from enum import Enum, auto
import logging
import asyncio

from ..config import get_config
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..prompt_management.prompt_loader import PromptLoader
from ..prompt_management import uses_prompt
from ..knowledge_representation.models import (
    Concept, ConceptState, EntanglementLink, CreativeIdea, ShockProfile
)


class NodeType(Enum):
    """Types of nodes in the mycelial network."""
    NUTRIENT = auto()  # Raw materials or input data
    HYPHA = auto()     # Processing nodes that decompose and transform
    RHIZOMORPH = auto() # Specialized transport structures
    FRUITING_BODY = auto() # Output structures that produce creative ideas


class EdgeType(Enum):
    """Types of edges in the mycelial network."""
    DECOMPOSITION = auto()  # Breaking down into constituent parts
    ABSORPTION = auto()     # Taking in nutrients or information
    TRANSPORT = auto()      # Moving resources through the network
    SYNTHESIS = auto()      # Combining elements into new forms
    EXTENSION = auto()      # Growing the network at the edges


class MycelialNode:
    """
    Represents a node in the mycelial network.
    
    Each node can store content, process information, and connect to other nodes
    through typed edges.
    """
    
    def __init__(self, 
                node_id: Optional[UUID4] = None,
                node_type: NodeType = NodeType.HYPHA,
                content: Optional[str] = None,
                attributes: Optional[Dict[str, Any]] = None):
        """
        Initialize a mycelial node.
        
        Args:
            node_id: Optional node ID. If None, a new UUID is generated.
            node_type: Type of node.
            content: Optional textual content for the node.
            attributes: Optional additional attributes.
        """
        self.id = node_id or uuid.uuid4()
        self.node_type = node_type
        self.content = content or ""
        self.attributes = attributes or {}
        self.connections: Dict[UUID4, EdgeType] = {}
        self.created_at = datetime.now()
        self.last_updated = self.created_at
        
    def connect_to(self, target_node: "MycelialNode", edge_type: EdgeType) -> None:
        """
        Connect this node to another node.
        
        Args:
            target_node: The target node to connect to.
            edge_type: The type of edge to create.
        """
        self.connections[target_node.id] = edge_type
        self.last_updated = datetime.now()
        
    def disconnect_from(self, target_id: UUID4) -> bool:
        """
        Disconnect this node from another node.
        
        Args:
            target_id: The ID of the target node to disconnect from.
            
        Returns:
            bool: True if the connection was removed, False if it didn't exist.
        """
        if target_id in self.connections:
            del self.connections[target_id]
            self.last_updated = datetime.now()
            return True
        return False
    
    def update_content(self, new_content: str) -> None:
        """
        Update the content of this node.
        
        Args:
            new_content: The new content for the node.
        """
        self.content = new_content
        self.last_updated = datetime.now()
        
    def add_attribute(self, key: str, value: Any) -> None:
        """
        Add or update an attribute for this node.
        
        Args:
            key: The attribute key.
            value: The attribute value.
        """
        self.attributes[key] = value
        self.last_updated = datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: The node as a dictionary.
        """
        return {
            "id": str(self.id),
            "node_type": self.node_type.name,
            "content": self.content,
            "attributes": self.attributes,
            "connections": {str(k): v.name for k, v in self.connections.items()},
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MycelialNode":
        """
        Create a node from a dictionary.
        
        Args:
            data: The dictionary to create the node from.
            
        Returns:
            MycelialNode: The created node.
        """
        node = cls(
            node_id=uuid.UUID(data["id"]),
            node_type=NodeType[data["node_type"]],
            content=data["content"],
            attributes=data["attributes"]
        )
        node.connections = {uuid.UUID(k): EdgeType[v] for k, v in data.get("connections", {}).items()}
        node.created_at = datetime.fromisoformat(data["created_at"])
        node.last_updated = datetime.fromisoformat(data["last_updated"])
        return node


@uses_prompt("mycelial_decomposition", dependencies=["mycelial_synthesis", "mycelial_extension"])
class MycelialNetwork:
    """
    Implements a mycelial network model for creative idea generation.
    
    This class models creativity as a process similar to fungal networks:
    - Decomposition of inputs into constituent parts
    - Absorption of these parts through the network
    - Transport and transformation through connected structures
    - Synthesis of new ideas at the network edges
    - Growth and extension based on environmental factors
    
    Depends on prompts: mycelial_decomposition.txt, mycelial_synthesis.txt, mycelial_extension.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the mycelial network.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.prompt_loader = PromptLoader()
        
        # Initialize the network
        self.nodes: Dict[UUID4, MycelialNode] = {}
        self.node_index: Dict[NodeType, List[UUID4]] = {
            node_type: [] for node_type in NodeType
        }
        
        # Track network statistics
        self.stats = {
            "node_counts": {node_type.name: 0 for node_type in NodeType},
            "edge_counts": {edge_type.name: 0 for edge_type in EdgeType},
            "decompositions": 0,
            "syntheses": 0,
            "extensions": 0
        }
    
    def add_node(self, node: MycelialNode) -> UUID4:
        """
        Add a node to the network.
        
        Args:
            node: The node to add.
            
        Returns:
            UUID4: The ID of the added node.
        """
        self.nodes[node.id] = node
        self.node_index[node.node_type].append(node.id)
        self.stats["node_counts"][node.node_type.name] += 1
        return node.id
    
    def get_node(self, node_id: UUID4) -> Optional[MycelialNode]:
        """
        Get a node from the network.
        
        Args:
            node_id: The ID of the node to get.
            
        Returns:
            Optional[MycelialNode]: The node, or None if not found.
        """
        return self.nodes.get(node_id)
    
    def connect_nodes(self, source_id: UUID4, target_id: UUID4, edge_type: EdgeType) -> bool:
        """
        Connect two nodes in the network.
        
        Args:
            source_id: The ID of the source node.
            target_id: The ID of the target node.
            edge_type: The type of edge to create.
            
        Returns:
            bool: True if the connection was created, False otherwise.
        """
        source_node = self.get_node(source_id)
        target_node = self.get_node(target_id)
        
        if not source_node or not target_node:
            return False
        
        source_node.connect_to(target_node, edge_type)
        self.stats["edge_counts"][edge_type.name] += 1
        return True
    
    async def seed_network_from_concept(self, concept: Concept) -> Dict[str, Any]:
        """
        Seed the network with a concept as the starting point.
        
        Args:
            concept: The concept to seed the network with.
            
        Returns:
            Dict[str, Any]: Information about the seeded network.
        """
        # Create a nutrient node for the concept
        nutrient_node = MycelialNode(
            node_type=NodeType.NUTRIENT,
            content=concept.definition,
            attributes={
                "name": concept.name,
                "domain": concept.domain,
                "concept_id": str(concept.id)
            }
        )
        nutrient_id = self.add_node(nutrient_node)
        
        # Decompose the concept into constituent parts
        decomposed_parts = await self._decompose_content(
            content=concept.definition,
            domain=concept.domain,
            additional_context=f"This content represents the concept of '{concept.name}'."
        )
        
        # Create hypha nodes for each decomposed part
        hypha_ids = []
        for part in decomposed_parts:
            hypha_node = MycelialNode(
                node_type=NodeType.HYPHA,
                content=part,
                attributes={
                    "source_concept": concept.name,
                    "domain": concept.domain
                }
            )
            hypha_id = self.add_node(hypha_node)
            hypha_ids.append(hypha_id)
            
            # Connect the nutrient node to the hypha node
            self.connect_nodes(nutrient_id, hypha_id, EdgeType.DECOMPOSITION)
        
        # Create a rhizomorph node to transport resources
        rhizomorph_node = MycelialNode(
            node_type=NodeType.RHIZOMORPH,
            content="Transport node for " + concept.name,
            attributes={
                "source_concept": concept.name,
                "domain": concept.domain,
                "transport_capacity": len(hypha_ids)
            }
        )
        rhizomorph_id = self.add_node(rhizomorph_node)
        
        # Connect hypha nodes to the rhizomorph node
        for hypha_id in hypha_ids:
            self.connect_nodes(hypha_id, rhizomorph_id, EdgeType.TRANSPORT)
        
        # Create a fruiting body node for future idea generation
        fruiting_node = MycelialNode(
            node_type=NodeType.FRUITING_BODY,
            content="Potential idea generation point for " + concept.name,
            attributes={
                "source_concept": concept.name,
                "domain": concept.domain,
                "maturity": 0.0  # Not mature yet
            }
        )
        fruiting_id = self.add_node(fruiting_node)
        
        # Connect the rhizomorph to the fruiting body
        self.connect_nodes(rhizomorph_id, fruiting_id, EdgeType.SYNTHESIS)
        
        # Track decomposition in stats
        self.stats["decompositions"] += 1
        
        # Return information about the seeded network
        return {
            "nutrient_id": nutrient_id,
            "hypha_ids": hypha_ids,
            "rhizomorph_id": rhizomorph_id,
            "fruiting_id": fruiting_id,
            "decomposed_parts": decomposed_parts
        }
    
    async def extend_network(self, 
                         starting_node_id: UUID4, 
                         extension_factor: float = 1.0) -> Dict[str, Any]:
        """
        Extend the network from a starting node.
        
        Args:
            starting_node_id: The ID of the node to start extending from.
            extension_factor: Factor controlling the extent of growth (0.0-2.0).
            
        Returns:
            Dict[str, Any]: Information about the extended network.
        """
        starting_node = self.get_node(starting_node_id)
        if not starting_node:
            raise ValueError(f"Node with ID {starting_node_id} not found in the network")
        
        # Determine number of new nodes to create based on extension factor
        # Random value between 1-3, modified by extension factor
        num_new_nodes = max(1, min(5, int(random.uniform(1, 3) * extension_factor)))
        
        # Get all nodes connected to the starting node
        connected_nodes = [
            self.get_node(node_id) 
            for node_id in starting_node.connections.keys()
            if self.get_node(node_id) is not None
        ]
        
        # Get domain and context information
        domain = starting_node.attributes.get("domain", "general")
        context = self._build_context_from_nodes([starting_node] + connected_nodes)
        
        # Generate extension content
        extension_parts = await self._generate_extensions(
            starting_content=starting_node.content,
            connected_content=[node.content for node in connected_nodes],
            domain=domain,
            context=context,
            num_extensions=num_new_nodes
        )
        
        # Create new nodes for each extension part
        new_node_ids = []
        for part in extension_parts:
            # Determine node type based on starting node and randomness
            weights = self._get_node_type_weights(starting_node.node_type)
            node_type = random.choices(
                list(weights.keys()),
                weights=list(weights.values()),
                k=1
            )[0]
            
            # Create the new node
            new_node = MycelialNode(
                node_type=node_type,
                content=part,
                attributes={
                    "domain": domain,
                    "source_node_id": str(starting_node_id),
                    "extension_round": self.stats["extensions"] + 1
                }
            )
            new_id = self.add_node(new_node)
            new_node_ids.append(new_id)
            
            # Determine edge type based on node types
            edge_type = self._determine_edge_type(starting_node.node_type, node_type)
            
            # Connect the starting node to the new node
            self.connect_nodes(starting_node_id, new_id, edge_type)
            
            # Also connect to a random connected node with probability 0.3
            if connected_nodes and random.random() < 0.3:
                random_connected = random.choice(connected_nodes)
                conn_edge_type = self._determine_edge_type(random_connected.node_type, node_type)
                self.connect_nodes(random_connected.id, new_id, conn_edge_type)
        
        # Track extension in stats
        self.stats["extensions"] += 1
        
        # Return information about the extension
        return {
            "starting_node_id": starting_node_id,
            "new_node_ids": new_node_ids,
            "extension_parts": extension_parts,
            "extension_round": self.stats["extensions"]
        }
    
    async def synthesize_idea(self, 
                          fruiting_node_id: UUID4,
                          problem_statement: str) -> CreativeIdea:
        """
        Synthesize a creative idea from a fruiting body node.
        
        Args:
            fruiting_node_id: The ID of the fruiting body node.
            problem_statement: The problem statement to address.
            
        Returns:
            CreativeIdea: The synthesized creative idea.
        """
        fruiting_node = self.get_node(fruiting_node_id)
        if not fruiting_node:
            raise ValueError(f"Node with ID {fruiting_node_id} not found in the network")
        
        if fruiting_node.node_type != NodeType.FRUITING_BODY:
            raise ValueError(f"Node with ID {fruiting_node_id} is not a fruiting body node")
        
        # Get the connected nodes (going back up the network)
        connected_nodes = self._get_upstream_nodes(fruiting_node_id)
        
        # Extract domain information
        domain = fruiting_node.attributes.get("domain", "general")
        
        # Build context from connected nodes
        context = self._build_context_from_nodes([fruiting_node] + connected_nodes)
        
        # Generate the creative idea
        idea_description = await self._synthesize_from_nodes(
            nodes=connected_nodes,
            problem_statement=problem_statement,
            domain=domain,
            context=context
        )
        
        # Create shock profile for the idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.75,
            impossibility_score=0.7,
            utility_potential=0.8,
            expert_rejection_probability=0.7,
            composite_shock_value=0.8
        )
        
        # Create the creative idea
        idea = CreativeIdea(
            id=uuid.uuid4(),
            description=idea_description,
            generative_framework="mycelial_network",
            domain=domain,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[],
            shock_metrics=shock_profile
        )
        
        # Update the fruiting body node with the idea
        fruiting_node.add_attribute("idea_id", str(idea.id))
        fruiting_node.add_attribute("maturity", 1.0)  # Mark as mature
        fruiting_node.update_content(f"Idea: {idea_description[:100]}...")
        
        # Track synthesis in stats
        self.stats["syntheses"] += 1
        
        return idea
    
    def _get_node_type_weights(self, starting_type: NodeType) -> Dict[NodeType, float]:
        """
        Get weights for selecting a node type based on the starting node type.
        
        Args:
            starting_type: The type of the starting node.
            
        Returns:
            Dict[NodeType, float]: A dictionary mapping node types to weights.
        """
        if starting_type == NodeType.NUTRIENT:
            return {
                NodeType.NUTRIENT: 0.1,
                NodeType.HYPHA: 0.7,
                NodeType.RHIZOMORPH: 0.2,
                NodeType.FRUITING_BODY: 0.0
            }
        elif starting_type == NodeType.HYPHA:
            return {
                NodeType.NUTRIENT: 0.0,
                NodeType.HYPHA: 0.6,
                NodeType.RHIZOMORPH: 0.3,
                NodeType.FRUITING_BODY: 0.1
            }
        elif starting_type == NodeType.RHIZOMORPH:
            return {
                NodeType.NUTRIENT: 0.0,
                NodeType.HYPHA: 0.2,
                NodeType.RHIZOMORPH: 0.3,
                NodeType.FRUITING_BODY: 0.5
            }
        elif starting_type == NodeType.FRUITING_BODY:
            return {
                NodeType.NUTRIENT: 0.0,
                NodeType.HYPHA: 0.1,
                NodeType.RHIZOMORPH: 0.1,
                NodeType.FRUITING_BODY: 0.8
            }
        return {node_type: 0.25 for node_type in NodeType}
    
    def _determine_edge_type(self, source_type: NodeType, target_type: NodeType) -> EdgeType:
        """
        Determine the appropriate edge type based on the source and target node types.
        
        Args:
            source_type: The type of the source node.
            target_type: The type of the target node.
            
        Returns:
            EdgeType: The appropriate edge type.
        """
        if source_type == NodeType.NUTRIENT:
            if target_type == NodeType.HYPHA:
                return EdgeType.DECOMPOSITION
            else:
                return EdgeType.ABSORPTION
        elif source_type == NodeType.HYPHA:
            if target_type == NodeType.RHIZOMORPH:
                return EdgeType.TRANSPORT
            elif target_type == NodeType.FRUITING_BODY:
                return EdgeType.SYNTHESIS
            else:
                return EdgeType.EXTENSION
        elif source_type == NodeType.RHIZOMORPH:
            if target_type == NodeType.FRUITING_BODY:
                return EdgeType.SYNTHESIS
            else:
                return EdgeType.TRANSPORT
        elif source_type == NodeType.FRUITING_BODY:
            return EdgeType.EXTENSION
        return EdgeType.EXTENSION
    
    def _get_upstream_nodes(self, node_id: UUID4) -> List[MycelialNode]:
        """
        Get all nodes that contribute to the given node (upstream in the network).
        
        Args:
            node_id: The ID of the node to get upstream nodes for.
            
        Returns:
            List[MycelialNode]: The upstream nodes.
        """
        node = self.get_node(node_id)
        if not node:
            return []
        
        # Find nodes that connect to this node
        upstream_nodes = []
        for potential_id, potential_node in self.nodes.items():
            if node_id in potential_node.connections:
                upstream_nodes.append(potential_node)
                
                # Recursively add upstream nodes with decreasing depth
                upstream_of_upstream = self._get_upstream_nodes(potential_id)
                upstream_nodes.extend(upstream_of_upstream)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_nodes = []
        for n in upstream_nodes:
            if n.id not in seen:
                seen.add(n.id)
                unique_nodes.append(n)
        
        return unique_nodes
    
    def _build_context_from_nodes(self, nodes: List[MycelialNode]) -> str:
        """
        Build a context string from a list of nodes.
        
        Args:
            nodes: The nodes to build context from.
            
        Returns:
            str: The context string.
        """
        if not nodes:
            return ""
        
        context_parts = []
        
        # Add domain information if available
        domains = set()
        for node in nodes:
            domain = node.attributes.get("domain")
            if domain:
                domains.add(domain)
        
        if domains:
            context_parts.append(f"Domain(s): {', '.join(domains)}")
        
        # Add node information
        node_type_counts = {node_type: 0 for node_type in NodeType}
        for node in nodes:
            node_type_counts[node.node_type] += 1
        
        context_parts.append("Network composition:")
        for node_type, count in node_type_counts.items():
            if count > 0:
                context_parts.append(f"- {node_type.name}: {count} nodes")
        
        # Add content snippets
        content_snippets = []
        for node in nodes[:5]:  # Limit to first 5 nodes
            snippet = node.content[:50] + "..." if len(node.content) > 50 else node.content
            content_snippets.append(f"{node.node_type.name}: {snippet}")
        
        if content_snippets:
            context_parts.append("Content samples:")
            context_parts.extend([f"- {snippet}" for snippet in content_snippets])
        
        return "\n".join(context_parts)
    
    async def _decompose_content(self,
                              content: str,
                              domain: str,
                              additional_context: str = "") -> List[str]:
        """
        Decompose content into constituent parts using the mycelial_decomposition prompt.
        
        Args:
            content: The content to decompose.
            domain: The domain of the content.
            additional_context: Additional context for the prompt.
            
        Returns:
            List[str]: The decomposed parts.
        """
        # Render the decomposition prompt template
        context = {
            "content": content,
            "domain": domain,
            "additional_context": additional_context
        }
        
        decomposition_prompt = self.prompt_loader.render_prompt(
            "mycelial_decomposition",
            context
        )
        
        # Fallback if prompt rendering fails
        if not decomposition_prompt:
            logging.warning("Failed to render mycelial_decomposition prompt template, using fallback")
            
            decomposition_prompt = f"""
            Decompose the following content into its constituent parts, similar to how mycelial networks break down organic matter:

            Content:
            {content}

            Domain: {domain}

            {additional_context}

            Identify 5-7 distinct components that could form the basis for a creative network. For each component:
            1. Extract a key concept, principle, or element
            2. Provide a concise description (1-2 sentences)
            3. Note potential connections to other components

            Format your response with <decomposition> tags and list each component on a new line.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=decomposition_prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract the decomposed parts
        decomposition = self._extract_tagged_content(thinking_step.reasoning_process, "decomposition")
        
        if not decomposition:
            # Fallback to just separating paragraphs
            parts = [p.strip() for p in content.split("\n\n") if p.strip()]
            if len(parts) < 2:
                parts = [content]
            return parts
        
        # Split the decomposition into parts
        parts = [p.strip() for p in decomposition.split("\n") if p.strip()]
        
        # If no parts were found, fallback to the entire decomposition
        if not parts:
            parts = [decomposition]
        
        return parts
    
    async def _generate_extensions(self,
                                starting_content: str,
                                connected_content: List[str],
                                domain: str,
                                context: str,
                                num_extensions: int = 3) -> List[str]:
        """
        Generate extensions from existing content.
        
        Args:
            starting_content: The content of the starting node.
            connected_content: The content of connected nodes.
            domain: The domain to generate extensions in.
            context: Additional context information.
            num_extensions: Number of extensions to generate.
            
        Returns:
            List[str]: The generated extensions.
        """
        # Render the extension prompt template
        context_dict = {
            "starting_content": starting_content,
            "connected_content": "\n".join(connected_content),
            "domain": domain,
            "context": context,
            "num_extensions": num_extensions
        }
        
        extension_prompt = self.prompt_loader.render_prompt(
            "mycelial_extension",
            context_dict
        )
        
        # Fallback if prompt rendering fails
        if not extension_prompt:
            logging.warning("Failed to render mycelial_extension prompt template, using fallback")
            
            connected_text = "\n".join([f"- {c[:100]}..." if len(c) > 100 else f"- {c}" for c in connected_content])
            
            extension_prompt = f"""
            Generate {num_extensions} extensions from the following content, similar to how mycelial networks extend at their edges:

            Starting Content:
            {starting_content}

            Connected Content:
            {connected_text}

            Domain: {domain}

            Context:
            {context}

            Create {num_extensions} new extensions that could emerge from these existing elements. Each extension should:
            1. Build upon existing content in a non-obvious way
            2. Introduce a novel element or connection
            3. Have potential for further growth and connection

            Format your response with <extensions> tags and list each extension on a new line.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=extension_prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract the extensions
        extensions = self._extract_tagged_content(thinking_step.reasoning_process, "extensions")
        
        if not extensions:
            # Fallback to using insights from thinking step
            return thinking_step.insights_generated or [thinking_step.reasoning_process]
        
        # Split the extensions into parts
        parts = [p.strip() for p in extensions.split("\n") if p.strip()]
        
        # If not enough parts were found, duplicate some or add from the thinking step
        while len(parts) < num_extensions:
            if parts:
                parts.append(random.choice(parts))
            else:
                parts.append(thinking_step.reasoning_process[:100])
        
        # Limit to the requested number
        return parts[:num_extensions]
    
    async def _synthesize_from_nodes(self,
                                 nodes: List[MycelialNode],
                                 problem_statement: str,
                                 domain: str,
                                 context: str) -> str:
        """
        Synthesize a creative idea from a set of nodes.
        
        Args:
            nodes: The nodes to synthesize from.
            problem_statement: The problem statement to address.
            domain: The domain to generate the idea in.
            context: Additional context information.
            
        Returns:
            str: The synthesized idea description.
        """
        # Extract content from nodes by type
        content_by_type = {node_type: [] for node_type in NodeType}
        for node in nodes:
            content_by_type[node.node_type].append(node.content)
        
        # Render the synthesis prompt template
        context_dict = {
            "nutrient_content": "\n".join(content_by_type[NodeType.NUTRIENT]),
            "hypha_content": "\n".join(content_by_type[NodeType.HYPHA]),
            "rhizomorph_content": "\n".join(content_by_type[NodeType.RHIZOMORPH]),
            "fruiting_content": "\n".join(content_by_type[NodeType.FRUITING_BODY]),
            "problem_statement": problem_statement,
            "domain": domain,
            "context": context
        }
        
        synthesis_prompt = self.prompt_loader.render_prompt(
            "mycelial_synthesis",
            context_dict
        )
        
        # Fallback if prompt rendering fails
        if not synthesis_prompt:
            logging.warning("Failed to render mycelial_synthesis prompt template, using fallback")
            
            # Build a simple content summary
            content_summary = ""
            for node_type, contents in content_by_type.items():
                if contents:
                    content_summary += f"\n{node_type.name} Content:\n"
                    content_summary += "\n".join([f"- {c[:100]}..." if len(c) > 100 else f"- {c}" for c in contents[:3]])
            
            synthesis_prompt = f"""
            Synthesize a creative idea from the following mycelial network content:

            {content_summary}

            Problem Statement:
            {problem_statement}

            Domain: {domain}

            Context:
            {context}

            Generate a creative solution that:
            1. Addresses the problem statement in a novel way
            2. Synthesizes insights from different parts of the network
            3. Creates something greater than the sum of its parts
            4. Challenges conventional thinking in the domain

            Format your response with <synthesis> tags.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=synthesis_prompt,
            thinking_budget=12000,
            max_tokens=3000
        )
        
        # Extract the synthesis
        synthesis = self._extract_tagged_content(thinking_step.reasoning_process, "synthesis")
        
        if not synthesis:
            # Fallback to using the reasoning process
            synthesis = thinking_step.reasoning_process
        
        return synthesis
    
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
    
    def to_graph(self) -> nx.DiGraph:
        """
        Convert the mycelial network to a NetworkX directed graph.
        
        Returns:
            nx.DiGraph: The network as a directed graph.
        """
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node in self.nodes.items():
            G.add_node(
                str(node_id),
                type=node.node_type.name,
                content=node.content[:50] + "..." if len(node.content) > 50 else node.content,
                attributes=node.attributes
            )
        
        # Add edges
        for source_id, source_node in self.nodes.items():
            for target_id, edge_type in source_node.connections.items():
                G.add_edge(
                    str(source_id),
                    str(target_id),
                    type=edge_type.name
                )
        
        return G
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the mycelial network to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: The network as a dictionary.
        """
        return {
            "nodes": {str(k): v.to_dict() for k, v in self.nodes.items()},
            "node_index": {k.name: [str(i) for i in v] for k, v in self.node_index.items()},
            "stats": self.stats
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], api_key: Optional[str] = None) -> "MycelialNetwork":
        """
        Create a mycelial network from a dictionary.
        
        Args:
            data: The dictionary to create the network from.
            api_key: Optional API key for Claude.
            
        Returns:
            MycelialNetwork: The created network.
        """
        network = cls(api_key=api_key)
        
        # Load nodes
        for node_id, node_data in data.get("nodes", {}).items():
            node = MycelialNode.from_dict(node_data)
            network.nodes[node.id] = node
        
        # Load node index
        for node_type_name, node_ids in data.get("node_index", {}).items():
            node_type = NodeType[node_type_name]
            network.node_index[node_type] = [uuid.UUID(node_id) for node_id in node_ids]
        
        # Load stats
        network.stats = data.get("stats", network.stats)
        
        return network


async def generate_mycelial_idea(
    problem_statement: str,
    domain: str,
    concepts: List[Concept],
    extension_rounds: int = 3
) -> CreativeIdea:
    """
    Generate a creative idea using the mycelial network model.
    
    Args:
        problem_statement: Problem statement to address.
        domain: Domain of the problem.
        concepts: List of concepts to seed the network with.
        extension_rounds: Number of extension rounds to perform.
        
    Returns:
        CreativeIdea: The generated creative idea.
    """
    if not concepts:
        raise ValueError("At least one concept is required to seed the network")
    
    # Create the mycelial network
    network = MycelialNetwork()
    
    # Seed the network with the concepts
    seed_results = []
    for concept in concepts:
        seed_result = await network.seed_network_from_concept(concept)
        seed_results.append(seed_result)
    
    # Extract fruiting node IDs
    fruiting_ids = []
    for result in seed_results:
        fruiting_ids.append(result["fruiting_id"])
    
    # Extract some random nodes for extension
    extension_candidates = []
    for result in seed_results:
        extension_candidates.extend(result["hypha_ids"])
    
    # Run extension rounds
    for _ in range(extension_rounds):
        # Choose random nodes to extend
        num_extensions = min(3, len(extension_candidates))
        nodes_to_extend = random.sample(extension_candidates, num_extensions)
        
        # Extend from each chosen node
        for node_id in nodes_to_extend:
            extension_result = await network.extend_network(node_id)
            
            # Add new nodes to extension candidates
            extension_candidates.extend(extension_result["new_node_ids"])
    
    # Synthesize an idea from a random fruiting node
    idea = await network.synthesize_idea(
        fruiting_node_id=random.choice(fruiting_ids),
        problem_statement=problem_statement
    )
    
    # Set the domain
    if not idea.domain:
        idea.domain = domain
    
    return idea