"""
Conceptual Territories System - Implements territory-based conceptual mapping and transformation.

This module provides an alternative metaphor for creativity based on territorial mapping,
where ideas are represented as geographical territories with boundaries, features, and relationships.
"""
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import uuid
import asyncio
import random
from datetime import datetime
from pydantic import UUID4
from enum import Enum, auto
import logging

from ..config import get_config
from ..directed_thinking.claude_api import ClaudeAPIClient
from ..prompt_management.prompt_loader import PromptLoader
from ..prompt_management import uses_prompt
from ..knowledge_representation.models import (
    Concept, CreativeIdea, ShockProfile
)


class TransformationProcess(Enum):
    """Types of transformation processes that can reshape territories."""
    TECTONIC_SHIFT = auto()   # Massive fundamental movement
    VOLCANIC_ERUPTION = auto()  # Sudden forceful emergence
    GLACIAL_RETREAT = auto()   # Revealing previously covered areas
    DESERTIFICATION = auto()   # Drying and hardening of flexible areas
    FLOODING = auto()         # Overflow and saturation
    ECOLOGICAL_SUCCESSION = auto()  # Gradual systematic replacement


class TerritoryFeatureType(Enum):
    """Types of features within conceptual territories."""
    BOUNDARY = auto()    # Edges and limits of the concept
    MOUNTAIN = auto()    # High points or strong aspects
    VALLEY = auto()      # Low points or recessive aspects
    RIVER = auto()       # Flows and connections
    FOREST = auto()      # Dense, rich areas
    DESERT = auto()      # Sparse, minimal areas
    LANDMARK = auto()    # Distinctive defining points
    UNEXPLORED = auto()  # Underexplored areas


class TerritoryFeature:
    """
    Represents a feature within a conceptual territory.
    
    Each feature has a type, name, description, and attributes.
    """
    
    def __init__(self, 
                feature_id: Optional[UUID4] = None,
                feature_type: TerritoryFeatureType = TerritoryFeatureType.LANDMARK,
                name: str = "",
                description: str = "",
                attributes: Optional[Dict[str, Any]] = None):
        """
        Initialize a territory feature.
        
        Args:
            feature_id: Optional feature ID. If None, a new UUID is generated.
            feature_type: Type of feature.
            name: Name of the feature.
            description: Description of the feature.
            attributes: Optional additional attributes.
        """
        self.id = feature_id or uuid.uuid4()
        self.feature_type = feature_type
        self.name = name
        self.description = description
        self.attributes = attributes or {}
        self.created_at = datetime.now()
        self.last_updated = self.created_at
    
    def update_description(self, new_description: str) -> None:
        """
        Update the description of this feature.
        
        Args:
            new_description: The new description for the feature.
        """
        self.description = new_description
        self.last_updated = datetime.now()
    
    def add_attribute(self, key: str, value: Any) -> None:
        """
        Add or update an attribute for this feature.
        
        Args:
            key: The attribute key.
            value: The attribute value.
        """
        self.attributes[key] = value
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the feature to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: The feature as a dictionary.
        """
        return {
            "id": str(self.id),
            "feature_type": self.feature_type.name,
            "name": self.name,
            "description": self.description,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TerritoryFeature":
        """
        Create a feature from a dictionary.
        
        Args:
            data: The dictionary to create the feature from.
            
        Returns:
            TerritoryFeature: The created feature.
        """
        feature = cls(
            feature_id=uuid.UUID(data["id"]) if "id" in data else None,
            feature_type=TerritoryFeatureType[data["feature_type"]],
            name=data["name"],
            description=data["description"],
            attributes=data["attributes"]
        )
        if "created_at" in data:
            feature.created_at = datetime.fromisoformat(data["created_at"])
        if "last_updated" in data:
            feature.last_updated = datetime.fromisoformat(data["last_updated"])
        return feature


class NeighboringTerritory:
    """
    Represents a neighboring territory to a conceptual territory.
    
    Each neighboring territory has a name, description, relationship type,
    and information about shared boundaries.
    """
    
    def __init__(self,
                territory_id: Optional[UUID4] = None,
                name: str = "",
                description: str = "",
                relationship: str = "",
                shared_boundary: str = "",
                tension_points: Optional[List[str]] = None):
        """
        Initialize a neighboring territory.
        
        Args:
            territory_id: Optional territory ID. If None, a new UUID is generated.
            name: Name of the neighboring territory.
            description: Description of the neighboring territory.
            relationship: Description of the relationship to the main territory.
            shared_boundary: Description of the shared boundary.
            tension_points: Optional list of tension points between territories.
        """
        self.id = territory_id or uuid.uuid4()
        self.name = name
        self.description = description
        self.relationship = relationship
        self.shared_boundary = shared_boundary
        self.tension_points = tension_points or []
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the neighboring territory to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: The neighboring territory as a dictionary.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "relationship": self.relationship,
            "shared_boundary": self.shared_boundary,
            "tension_points": self.tension_points,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeighboringTerritory":
        """
        Create a neighboring territory from a dictionary.
        
        Args:
            data: The dictionary to create the neighboring territory from.
            
        Returns:
            NeighboringTerritory: The created neighboring territory.
        """
        territory = cls(
            territory_id=uuid.UUID(data["id"]) if "id" in data else None,
            name=data["name"],
            description=data["description"],
            relationship=data["relationship"],
            shared_boundary=data["shared_boundary"],
            tension_points=data["tension_points"]
        )
        if "created_at" in data:
            territory.created_at = datetime.fromisoformat(data["created_at"])
        return territory


class ConceptualTerritory:
    """
    Represents a concept as a geographical territory with features and relationships.
    
    This class models a concept as a territory with boundaries, features, landmarks,
    neighboring territories, and more.
    """
    
    def __init__(self,
                territory_id: Optional[UUID4] = None,
                concept: Optional[Concept] = None,
                name: str = "",
                domain: str = "",
                territory_map: str = "",
                boundaries: str = "",
                features: Optional[List[TerritoryFeature]] = None,
                neighbors: Optional[List[NeighboringTerritory]] = None,
                attributes: Optional[Dict[str, Any]] = None):
        """
        Initialize a conceptual territory.
        
        Args:
            territory_id: Optional territory ID. If None, a new UUID is generated.
            concept: Optional related concept.
            name: Name of the territory.
            domain: Domain of the territory.
            territory_map: Textual description of the territory map.
            boundaries: Description of territory boundaries.
            features: Optional list of territory features.
            neighbors: Optional list of neighboring territories.
            attributes: Optional additional attributes.
        """
        self.id = territory_id or uuid.uuid4()
        self.concept = concept
        self.name = name or (concept.name if concept else "")
        self.domain = domain or (concept.domain if concept else "")
        self.territory_map = territory_map
        self.boundaries = boundaries
        self.features = features or []
        self.neighbors = neighbors or []
        self.attributes = attributes or {}
        self.created_at = datetime.now()
        self.last_updated = self.created_at
        
        # Dissolution and transformation state
        self.dissolved_boundaries = ""
        self.transformation_process = None
        self.transformed_territory = ""
    
    def add_feature(self, feature: TerritoryFeature) -> UUID4:
        """
        Add a feature to the territory.
        
        Args:
            feature: The feature to add.
            
        Returns:
            UUID4: The ID of the added feature.
        """
        self.features.append(feature)
        self.last_updated = datetime.now()
        return feature.id
    
    def add_neighbor(self, neighbor: NeighboringTerritory) -> UUID4:
        """
        Add a neighboring territory.
        
        Args:
            neighbor: The neighboring territory to add.
            
        Returns:
            UUID4: The ID of the added neighbor.
        """
        self.neighbors.append(neighbor)
        self.last_updated = datetime.now()
        return neighbor.id
    
    def get_features_by_type(self, feature_type: TerritoryFeatureType) -> List[TerritoryFeature]:
        """
        Get all features of a specific type.
        
        Args:
            feature_type: The type of features to get.
            
        Returns:
            List[TerritoryFeature]: The features of the specified type.
        """
        return [f for f in self.features if f.feature_type == feature_type]
    
    def update_boundaries(self, new_boundaries: str) -> None:
        """
        Update the boundaries description.
        
        Args:
            new_boundaries: The new boundaries description.
        """
        self.boundaries = new_boundaries
        self.last_updated = datetime.now()
    
    def update_territory_map(self, new_map: str) -> None:
        """
        Update the territory map description.
        
        Args:
            new_map: The new territory map description.
        """
        self.territory_map = new_map
        self.last_updated = datetime.now()
    
    def add_dissolution(self, dissolved_boundaries: str) -> None:
        """
        Add a boundary dissolution description.
        
        Args:
            dissolved_boundaries: Description of dissolved boundaries.
        """
        self.dissolved_boundaries = dissolved_boundaries
        self.last_updated = datetime.now()
    
    def add_transformation(self, 
                          transformation_process: TransformationProcess, 
                          transformed_territory: str) -> None:
        """
        Add a territory transformation.
        
        Args:
            transformation_process: The transformation process applied.
            transformed_territory: Description of the transformed territory.
        """
        self.transformation_process = transformation_process
        self.transformed_territory = transformed_territory
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conceptual territory to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: The conceptual territory as a dictionary.
        """
        return {
            "id": str(self.id),
            "name": self.name,
            "domain": self.domain,
            "concept": self.concept.to_dict() if self.concept else None,
            "territory_map": self.territory_map,
            "boundaries": self.boundaries,
            "features": [f.to_dict() for f in self.features],
            "neighbors": [n.to_dict() for n in self.neighbors],
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "dissolved_boundaries": self.dissolved_boundaries,
            "transformation_process": self.transformation_process.name if self.transformation_process else None,
            "transformed_territory": self.transformed_territory
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConceptualTerritory":
        """
        Create a conceptual territory from a dictionary.
        
        Args:
            data: The dictionary to create the territory from.
            
        Returns:
            ConceptualTerritory: The created territory.
        """
        concept = None
        if data.get("concept"):
            concept = Concept.from_dict(data["concept"])
        
        territory = cls(
            territory_id=uuid.UUID(data["id"]) if "id" in data else None,
            concept=concept,
            name=data["name"],
            domain=data["domain"],
            territory_map=data["territory_map"],
            boundaries=data["boundaries"],
            features=[TerritoryFeature.from_dict(f) for f in data.get("features", [])],
            neighbors=[NeighboringTerritory.from_dict(n) for n in data.get("neighbors", [])],
            attributes=data.get("attributes", {})
        )
        
        if "created_at" in data:
            territory.created_at = datetime.fromisoformat(data["created_at"])
        if "last_updated" in data:
            territory.last_updated = datetime.fromisoformat(data["last_updated"])
        if "dissolved_boundaries" in data:
            territory.dissolved_boundaries = data["dissolved_boundaries"]
        if "transformation_process" in data and data["transformation_process"]:
            territory.transformation_process = TransformationProcess[data["transformation_process"]]
        if "transformed_territory" in data:
            territory.transformed_territory = data["transformed_territory"]
            
        return territory


@uses_prompt("territory_mapping", dependencies=["territory_dissolution", "territory_transformation"])
class ConceptualTerritoriesSystem:
    """
    Implements territorial mapping and transformation for creative idea generation.
    
    This class models creativity as a process of mapping concepts as territories,
    dissolving boundaries between them, and transforming them through various processes.
    
    Depends on prompts: territory_mapping.txt, territory_dissolution.txt, territory_transformation.txt
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the conceptual territories system.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.prompt_loader = PromptLoader()
        
        # Track territories
        self.territories: Dict[UUID4, ConceptualTerritory] = {}
        
        # Configure transformation process descriptions
        self.transformation_descriptions = {
            TransformationProcess.TECTONIC_SHIFT: (
                "Like tectonic plates shifting, this process represents massive, fundamental "
                "movement of core conceptual foundations. It causes radical restructuring "
                "of the entire conceptual landscape with new mountains, valleys, and "
                "boundary configurations."
            ),
            TransformationProcess.VOLCANIC_ERUPTION: (
                "Like a volcanic eruption, this process involves sudden, forceful emergence "
                "of ideas from deep below the conceptual surface. It creates new formations, "
                "deposits rich new material across the landscape, and permanently alters "
                "the territory."
            ),
            TransformationProcess.GLACIAL_RETREAT: (
                "Like a glacier retreating, this process involves the withdrawal of "
                "long-standing conceptual structures, revealing previously covered terrain. "
                "It exposes new areas for exploration, leaves behind transformative deposits, "
                "and allows new growth in formerly restricted areas."
            ),
            TransformationProcess.DESERTIFICATION: (
                "Like desertification, this process involves the drying and hardening of "
                "previously flexible or fertile areas. It creates stark clarity, removes "
                "extraneous elements, and forces adaptation to more minimal conditions."
            ),
            TransformationProcess.FLOODING: (
                "Like a flood, this process involves overflow and saturation of the "
                "conceptual landscape with new elements. It dissolves existing structures, "
                "redistributes resources, and creates new connections between previously "
                "separate areas."
            ),
            TransformationProcess.ECOLOGICAL_SUCCESSION: (
                "Like ecological succession, this process involves gradual, systematic "
                "replacement of conceptual elements with new ones. It follows predictable "
                "stages, builds increasing complexity, and eventually reaches a stable "
                "but transformed state."
            )
        }
    
    def register_territory(self, territory: ConceptualTerritory) -> UUID4:
        """
        Register a territory in the system.
        
        Args:
            territory: The territory to register.
            
        Returns:
            UUID4: The ID of the registered territory.
        """
        self.territories[territory.id] = territory
        return territory.id
    
    def get_territory(self, territory_id: UUID4) -> Optional[ConceptualTerritory]:
        """
        Get a territory by ID.
        
        Args:
            territory_id: The ID of the territory.
            
        Returns:
            Optional[ConceptualTerritory]: The territory, or None if not found.
        """
        return self.territories.get(territory_id)
    
    async def map_concept_territory(self, concept: Concept) -> ConceptualTerritory:
        """
        Map a concept as a conceptual territory.
        
        Args:
            concept: The concept to map.
            
        Returns:
            ConceptualTerritory: The mapped conceptual territory.
        """
        # Create an initial empty territory
        territory = ConceptualTerritory(
            concept=concept,
            name=concept.name,
            domain=concept.domain
        )
        
        # Register the territory
        self.register_territory(territory)
        
        # Generate the territory map
        territory_map, boundaries, features, neighbors = await self._generate_territory_map(
            concept=concept
        )
        
        # Update the territory
        territory.update_territory_map(territory_map)
        territory.update_boundaries(boundaries)
        
        # Add features
        for feature in features:
            territory.add_feature(feature)
        
        # Add neighbors
        for neighbor in neighbors:
            territory.add_neighbor(neighbor)
        
        return territory
    
    async def dissolve_boundaries(self, territory_id: UUID4) -> ConceptualTerritory:
        """
        Dissolve the boundaries of a territory to reveal connections with neighbors.
        
        Args:
            territory_id: The ID of the territory.
            
        Returns:
            ConceptualTerritory: The territory with dissolved boundaries.
        """
        territory = self.get_territory(territory_id)
        if not territory:
            raise ValueError(f"Territory with ID {territory_id} not found")
        
        # Check if the territory has neighbors
        if not territory.neighbors:
            raise ValueError(f"Territory {territory.name} has no neighbors for boundary dissolution")
        
        # Generate the dissolved boundaries
        dissolved_boundaries = await self._generate_dissolved_boundaries(
            territory=territory
        )
        
        # Update the territory
        territory.add_dissolution(dissolved_boundaries)
        
        return territory
    
    async def transform_territory(self, 
                              territory_id: UUID4,
                              problem_statement: str,
                              transformation_process: Optional[TransformationProcess] = None) -> Tuple[ConceptualTerritory, str]:
        """
        Transform a territory through a specified process.
        
        Args:
            territory_id: The ID of the territory to transform.
            problem_statement: The problem statement to address.
            transformation_process: Optional specific transformation process to apply.
                                    If None, one is chosen randomly.
            
        Returns:
            Tuple[ConceptualTerritory, str]: The transformed territory and the creative solution.
        """
        territory = self.get_territory(territory_id)
        if not territory:
            raise ValueError(f"Territory with ID {territory_id} not found")
        
        # Check if boundaries have been dissolved
        if not territory.dissolved_boundaries:
            raise ValueError(f"Territory {territory.name} needs boundary dissolution before transformation")
        
        # Choose a random transformation process if not specified
        transformation_process = transformation_process or random.choice(list(TransformationProcess))
        
        # Get the transformation description
        transformation_description = self.transformation_descriptions.get(
            transformation_process, 
            "A transformative process that reshapes the conceptual landscape."
        )
        
        # Generate the transformed territory and creative solution
        transformed_territory, creative_solution = await self._generate_transformed_territory(
            territory=territory,
            problem_statement=problem_statement,
            transformation_process=transformation_process,
            transformation_description=transformation_description
        )
        
        # Update the territory
        territory.add_transformation(
            transformation_process=transformation_process,
            transformed_territory=transformed_territory
        )
        
        return territory, creative_solution
    
    async def generate_creative_idea(self, 
                                 territory_id: UUID4, 
                                 problem_statement: str) -> CreativeIdea:
        """
        Generate a creative idea from a transformed territory.
        
        Args:
            territory_id: The ID of the territory.
            problem_statement: The problem statement to address.
            
        Returns:
            CreativeIdea: The generated creative idea.
        """
        territory = self.get_territory(territory_id)
        if not territory:
            raise ValueError(f"Territory with ID {territory_id} not found")
        
        # Check if the territory has been transformed
        if not territory.transformed_territory:
            # Transform the territory if it hasn't been transformed yet
            territory, creative_solution = await self.transform_territory(
                territory_id=territory_id,
                problem_statement=problem_statement
            )
        else:
            # Extract creative solution from existing transformation
            creative_solution = await self._extract_creative_solution(
                territory=territory,
                problem_statement=problem_statement
            )
        
        # Create shock profile for the idea
        shock_profile = ShockProfile(
            novelty_score=0.85,
            contradiction_score=0.7,
            impossibility_score=0.65,
            utility_potential=0.8,
            expert_rejection_probability=0.7,
            composite_shock_value=0.75
        )
        
        # Create the creative idea
        idea = CreativeIdea(
            id=uuid.uuid4(),
            description=creative_solution,
            generative_framework="conceptual_territories",
            domain=territory.domain,
            impossibility_elements=[],
            contradiction_elements=[],
            related_concepts=[territory.name] + [n.name for n in territory.neighbors],
            shock_metrics=shock_profile
        )
        
        return idea
    
    async def _generate_territory_map(self, concept: Concept) -> Tuple[str, str, List[TerritoryFeature], List[NeighboringTerritory]]:
        """
        Generate a territory map for a concept using the territory_mapping prompt.
        
        Args:
            concept: The concept to map.
            
        Returns:
            Tuple[str, str, List[TerritoryFeature], List[NeighboringTerritory]]: 
                The territory map, boundaries, features, and neighbors.
        """
        # Render the territory mapping prompt template
        context = {
            "concept_name": concept.name,
            "concept_definition": concept.definition,
            "domain": concept.domain,
            "additional_context": f"This concept is from the domain of {concept.domain}."
        }
        
        territory_prompt = self.prompt_loader.render_prompt("territory_mapping", context)
        
        # Fallback if prompt rendering fails
        if not territory_prompt:
            logging.warning("Failed to render territory_mapping prompt template, using fallback")
            
            territory_prompt = f"""
            Map this concept as if it were a geographical territory with features and relationships:

            Concept Name: {concept.name}
            Domain: {concept.domain}
            Definition: {concept.definition}

            Define the territory with:
            1. Boundaries - What are the edges of this concept?
            2. Topographical features - What are the landscapes within this territory?
            3. Landmarks - What are the key defining points?
            4. Neighboring territories - What concepts are adjacent?
            5. Unexplored regions - What areas are underdeveloped?
            6. Indigenous concepts - What ideas naturally reside in this space?
            7. Territorial conflicts - Where are there boundary disputes?

            Format your response with <territory_map> tags.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=territory_prompt,
            thinking_budget=10000,
            max_tokens=2500
        )
        
        # Extract the territory map
        territory_map = self._extract_tagged_content(thinking_step.reasoning_process, "territory_map")
        
        if not territory_map:
            # Fallback to using the full reasoning process
            territory_map = thinking_step.reasoning_process
        
        # Parse the territory map to extract boundaries, features, and neighbors
        boundaries = self._extract_section(territory_map, "TERRITORY BOUNDARIES", "TOPOGRAPHICAL FEATURES")
        if not boundaries:
            boundaries = self._extract_section(territory_map, "BOUNDARIES", "TOPOGRAPHICAL")
        
        # Extract feature information
        features = []
        
        # Extract landmarks
        landmarks_text = self._extract_section(territory_map, "LANDMARKS", "NEIGHBORING")
        if landmarks_text:
            landmarks = self._extract_list_items(landmarks_text)
            for i, landmark in enumerate(landmarks):
                name = f"Landmark {i+1}"
                if ":" in landmark:
                    parts = landmark.split(":", 1)
                    name = parts[0].strip()
                    description = parts[1].strip()
                else:
                    description = landmark
                
                features.append(TerritoryFeature(
                    feature_type=TerritoryFeatureType.LANDMARK,
                    name=name,
                    description=description
                ))
        
        # Extract topographical features
        topo_text = self._extract_section(territory_map, "TOPOGRAPHICAL FEATURES", "LANDMARKS")
        if topo_text:
            topo_features = self._extract_list_items(topo_text)
            for topo in topo_features:
                feature_type = TerritoryFeatureType.MOUNTAIN  # Default
                
                if "mountain" in topo.lower():
                    feature_type = TerritoryFeatureType.MOUNTAIN
                elif "valley" in topo.lower():
                    feature_type = TerritoryFeatureType.VALLEY
                elif "river" in topo.lower():
                    feature_type = TerritoryFeatureType.RIVER
                elif "forest" in topo.lower():
                    feature_type = TerritoryFeatureType.FOREST
                elif "desert" in topo.lower():
                    feature_type = TerritoryFeatureType.DESERT
                
                name = f"{feature_type.name.title()} Feature"
                if ":" in topo:
                    parts = topo.split(":", 1)
                    name = parts[0].strip()
                    description = parts[1].strip()
                else:
                    description = topo
                
                features.append(TerritoryFeature(
                    feature_type=feature_type,
                    name=name,
                    description=description
                ))
        
        # Extract unexplored regions
        unexplored_text = self._extract_section(territory_map, "UNEXPLORED REGIONS", "INDIGENOUS")
        if unexplored_text:
            unexplored = self._extract_list_items(unexplored_text)
            for i, region in enumerate(unexplored):
                name = f"Unexplored Region {i+1}"
                if ":" in region:
                    parts = region.split(":", 1)
                    name = parts[0].strip()
                    description = parts[1].strip()
                else:
                    description = region
                
                features.append(TerritoryFeature(
                    feature_type=TerritoryFeatureType.UNEXPLORED,
                    name=name,
                    description=description
                ))
        
        # Extract neighbors
        neighbors = []
        neighbors_text = self._extract_section(territory_map, "NEIGHBORING TERRITORIES", "UNEXPLORED")
        if neighbors_text:
            neighbor_items = self._extract_list_items(neighbors_text)
            for i, neighbor in enumerate(neighbor_items):
                name = f"Neighbor {i+1}"
                description = neighbor
                relationship = ""
                shared_boundary = ""
                tension_points = []
                
                if ":" in neighbor:
                    parts = neighbor.split(":", 1)
                    name = parts[0].strip()
                    description = parts[1].strip()
                
                # Extract relationships if mentioned
                if "relate" in description.lower() or "connection" in description.lower():
                    relationship = description
                
                # Extract boundary information
                if "border" in description.lower() or "boundary" in description.lower():
                    shared_boundary = description
                
                # Extract tension points
                conflicts_text = self._extract_section(territory_map, "TERRITORIAL CONFLICTS", "")
                if conflicts_text and name.lower() in conflicts_text.lower():
                    tension_points.append(conflicts_text)
                
                neighbors.append(NeighboringTerritory(
                    name=name,
                    description=description,
                    relationship=relationship,
                    shared_boundary=shared_boundary,
                    tension_points=tension_points
                ))
        
        return territory_map, boundaries, features, neighbors
    
    async def _generate_dissolved_boundaries(self, territory: ConceptualTerritory) -> str:
        """
        Generate dissolved boundaries for a territory using the territory_dissolution prompt.
        
        Args:
            territory: The territory to dissolve boundaries for.
            
        Returns:
            str: The dissolved boundaries description.
        """
        # Build neighboring territories text
        neighboring_territories = []
        for neighbor in territory.neighbors:
            neighboring_territories.append(f"Name: {neighbor.name}")
            neighboring_territories.append(f"Description: {neighbor.description}")
            if neighbor.shared_boundary:
                neighboring_territories.append(f"Shared Boundary: {neighbor.shared_boundary}")
            if neighbor.tension_points:
                neighboring_territories.append(f"Tension Points: {', '.join(neighbor.tension_points)}")
            neighboring_territories.append("")
        
        neighboring_territories_text = "\n".join(neighboring_territories)
        
        # Render the territory dissolution prompt template
        context = {
            "territory_map": territory.territory_map,
            "neighboring_territories": neighboring_territories_text,
            "additional_context": f"This territory represents the concept of {territory.name} in the domain of {territory.domain}."
        }
        
        dissolution_prompt = self.prompt_loader.render_prompt("territory_dissolution", context)
        
        # Fallback if prompt rendering fails
        if not dissolution_prompt:
            logging.warning("Failed to render territory_dissolution prompt template, using fallback")
            
            dissolution_prompt = f"""
            Dissolve the boundaries between this conceptual territory and its neighbors:

            Territory Map:
            {territory.territory_map}

            Neighboring Territories:
            {neighboring_territories_text}

            Identify:
            1. Border permeability - Where are boundaries already porous?
            2. Shared foundations - What underlying principles connect these territories?
            3. Bridging concepts - What concepts belong to both territories?
            4. Artificial separations - Where are territories artificially separated?
            5. Revealed connections - What new insights emerge when viewing as continuous?
            6. Merged landscape - What does the combined landscape look like?

            Format your response with <dissolved_boundaries> tags.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=dissolution_prompt,
            thinking_budget=10000,
            max_tokens=2500
        )
        
        # Extract the dissolved boundaries
        dissolved_boundaries = self._extract_tagged_content(thinking_step.reasoning_process, "dissolved_boundaries")
        
        if not dissolved_boundaries:
            # Fallback to using the full reasoning process
            dissolved_boundaries = thinking_step.reasoning_process
        
        return dissolved_boundaries
    
    async def _generate_transformed_territory(self, 
                                         territory: ConceptualTerritory,
                                         problem_statement: str,
                                         transformation_process: TransformationProcess,
                                         transformation_description: str) -> Tuple[str, str]:
        """
        Generate a transformed territory using the territory_transformation prompt.
        
        Args:
            territory: The territory to transform.
            problem_statement: The problem statement to address.
            transformation_process: The transformation process to apply.
            transformation_description: Description of the transformation process.
            
        Returns:
            Tuple[str, str]: The transformed territory description and creative solution.
        """
        # Render the territory transformation prompt template
        context = {
            "territory_map": territory.territory_map,
            "dissolved_boundaries": territory.dissolved_boundaries,
            "transformation_process": transformation_process.name,
            "transformation_description": transformation_description,
            "problem_statement": problem_statement,
            "additional_context": f"This transformation is aimed at generating creative solutions in the domain of {territory.domain}."
        }
        
        transformation_prompt = self.prompt_loader.render_prompt("territory_transformation", context)
        
        # Fallback if prompt rendering fails
        if not transformation_prompt:
            logging.warning("Failed to render territory_transformation prompt template, using fallback")
            
            transformation_prompt = f"""
            Transform this conceptual territory to address a problem:

            Territory Map:
            {territory.territory_map}

            Dissolved Boundaries:
            {territory.dissolved_boundaries}

            Transformation Process: {transformation_process.name}
            Description: {transformation_description}

            Problem Statement:
            {problem_statement}

            Transform the territory through this process and address the problem by:
            1. Describing transformation forces at work
            2. Detailing how boundaries shift or merge
            3. Describing new topographical features that form
            4. Identifying new properties that emerge
            5. Explaining how concepts adapt
            6. Describing new relationships with neighbors
            7. Generating a specific creative solution

            Format your response with <transformed_territory> tags around the transformation and <creative_solution> tags around your solution.
            """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=transformation_prompt,
            thinking_budget=12000,
            max_tokens=3000
        )
        
        # Extract the transformed territory and creative solution
        transformed_territory = self._extract_tagged_content(thinking_step.reasoning_process, "transformed_territory")
        creative_solution = self._extract_tagged_content(thinking_step.reasoning_process, "creative_solution")
        
        # Fallbacks if extraction fails
        if not transformed_territory:
            # Look for substantial sections
            paragraphs = [p.strip() for p in thinking_step.reasoning_process.split("\n\n") if p.strip()]
            if len(paragraphs) > 2:
                # Take earlier paragraphs for transformation
                transformed_territory = "\n\n".join(paragraphs[:-1])
            else:
                transformed_territory = thinking_step.reasoning_process
        
        if not creative_solution:
            # Take the last paragraph or section
            paragraphs = [p.strip() for p in thinking_step.reasoning_process.split("\n\n") if p.strip()]
            if paragraphs:
                creative_solution = paragraphs[-1]
            else:
                creative_solution = "A creative solution emerged from the transformed territory."
        
        return transformed_territory, creative_solution
    
    async def _extract_creative_solution(self, 
                                    territory: ConceptualTerritory,
                                    problem_statement: str) -> str:
        """
        Extract a creative solution from an already transformed territory.
        
        Args:
            territory: The transformed territory.
            problem_statement: The problem statement to address.
            
        Returns:
            str: The creative solution.
        """
        # Check if territory has been transformed
        if not territory.transformed_territory:
            raise ValueError(f"Territory {territory.name} has not been transformed yet")
        
        # Extract from existing transformation if it contains a creative solution
        solution = self._extract_section(territory.transformed_territory, "CREATIVE SOLUTION", "")
        if solution:
            return solution
        
        # Generate a new creative solution based on the transformed territory
        prompt = f"""
        Generate a creative solution to this problem based on the transformed conceptual territory:

        Problem Statement:
        {problem_statement}

        Transformed Territory:
        {territory.transformed_territory}

        Create a specific, innovative solution that directly leverages insights from the transformed territory.
        Focus on how the transformation reveals new approaches to addressing the problem.

        Format your response with <solution> tags.
        """
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=6000,
            max_tokens=1500
        )
        
        # Extract the solution
        solution = self._extract_tagged_content(thinking_step.reasoning_process, "solution")
        
        if not solution:
            # Fallback to using the full reasoning process
            solution = thinking_step.reasoning_process
        
        return solution
    
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
    
    def _extract_section(self, text: str, start_section: str, end_section: str) -> Optional[str]:
        """
        Extract a section from the text between start and end section headers.
        
        Args:
            text: The text to search
            start_section: The section header to start from
            end_section: The section header to end at (if empty, goes to end of text)
            
        Returns:
            Optional[str]: The extracted section, or None if not found
        """
        start_pos = text.find(start_section)
        if start_pos == -1:
            return None
        
        start_pos += len(start_section)
        if end_section:
            end_pos = text.find(end_section, start_pos)
            if end_pos == -1:
                content = text[start_pos:].strip()
            else:
                content = text[start_pos:end_pos].strip()
        else:
            content = text[start_pos:].strip()
        
        return content
    
    def _extract_list_items(self, text: str) -> List[str]:
        """
        Extract list items from a text, looking for numbered or bulleted lists.
        
        Args:
            text: The text to extract list items from
            
        Returns:
            List[str]: The extracted list items
        """
        items = []
        
        # Split by newlines
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Look for numbered items (1. 2. 3. etc.)
            if line[0].isdigit() and len(line) > 1 and line[1] in ['.', ')']:
                item_text = line[2:].strip()
                items.append(item_text)
                continue
            
            # Look for bulleted items
            if line[0] in ['-', '*', '•']:
                item_text = line[1:].strip()
                items.append(item_text)
                continue
            
            # If we have items already, this might be a continuation
            if items:
                items[-1] += " " + line
        
        # If no items were found, treat the entire text as one item
        if not items:
            items = [text.strip()]
        
        return items


async def generate_territory_idea(
    problem_statement: str,
    domain: str,
    concept: Concept,
    transformation_process: Optional[TransformationProcess] = None
) -> CreativeIdea:
    """
    Generate a creative idea using the conceptual territories system.
    
    Args:
        problem_statement: Problem statement to address.
        domain: Domain of the problem.
        concept: Concept to map as a territory.
        transformation_process: Optional specific transformation process to apply.
        
    Returns:
        CreativeIdea: The generated creative idea.
    """
    # Create the territories system
    system = ConceptualTerritoriesSystem()
    
    # Map the concept as a territory
    territory = await system.map_concept_territory(concept)
    
    # Dissolve boundaries
    await system.dissolve_boundaries(territory.id)
    
    # Generate idea (this will transform the territory if not already done)
    idea = await system.generate_creative_idea(
        territory_id=territory.id,
        problem_statement=problem_statement
    )
    
    # Set the domain if not already set
    if not idea.domain:
        idea.domain = domain
    
    return idea