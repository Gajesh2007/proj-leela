"""
Repository layer for data persistence.
"""
from typing import Dict, List, Any, Optional, Union, Type
import uuid
from datetime import datetime

from ..knowledge_representation.models import (
    SpiralState, CreativeIdea, ThinkingStep, ShockProfile, MethodologyChange,
    Concept, ConceptState, EntanglementLink, TemporalVariant, Relationship
)
from .db_interface import DatabaseManager


class Repository:
    """
    Repository for data persistence operations.
    Provides a simplified interface for storing and retrieving data.
    """
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the repository.
        
        Args:
            db_url: Optional database URL
        """
        self.db_manager = DatabaseManager(db_url)
    
    async def initialize(self):
        """Initialize the repository."""
        await self.db_manager.initialize_db()
    
    # Concept operations
    async def save_concept(self, concept: Concept) -> Concept:
        """
        Save a concept.
        
        Args:
            concept: The concept to save
            
        Returns:
            Concept: The saved concept
        """
        return await self.db_manager.save_concept(concept)
    
    async def get_concept(self, concept_id: Union[uuid.UUID, str]) -> Optional[Concept]:
        """
        Get a concept by ID.
        
        Args:
            concept_id: The concept ID (UUID or string)
            
        Returns:
            Optional[Concept]: The concept if found
        """
        # Convert string ID to UUID if necessary
        if isinstance(concept_id, str):
            concept_id = uuid.UUID(concept_id)
            
        return await self.db_manager.get_concept(concept_id)
    
    async def get_concepts_by_domain(self, domain: str) -> List[Concept]:
        """
        Get concepts by domain.
        
        Args:
            domain: The domain name
            
        Returns:
            List[Concept]: List of concepts in the domain
        """
        return await self.db_manager.get_concepts_by_domain(domain)
    
    # Relationship operations
    async def save_relationship(self, relationship: Relationship) -> Relationship:
        """
        Save a relationship.
        
        Args:
            relationship: The relationship to save
            
        Returns:
            Relationship: The saved relationship
        """
        return await self.db_manager.save_relationship(relationship)
    
    async def get_relationships_for_concept(self, concept_id: Union[uuid.UUID, str]) -> List[Relationship]:
        """
        Get relationships for a concept.
        
        Args:
            concept_id: The concept ID (UUID or string)
            
        Returns:
            List[Relationship]: List of relationships
        """
        # Convert string ID to UUID if necessary
        if isinstance(concept_id, str):
            concept_id = uuid.UUID(concept_id)
            
        return await self.db_manager.get_relationships_for_concept(concept_id)
    
    # Creative idea operations
    async def save_idea(self, idea: CreativeIdea, spiral_state_id: Optional[Union[uuid.UUID, str]] = None) -> CreativeIdea:
        """
        Save a creative idea.
        
        Args:
            idea: The idea to save
            spiral_state_id: Optional spiral state ID (UUID or string)
            
        Returns:
            CreativeIdea: The saved idea
        """
        print(f"[Repository] Saving idea with ID: {idea.id}")
        try:
            # Convert string ID to UUID if necessary
            if spiral_state_id is not None and isinstance(spiral_state_id, str):
                spiral_state_id = uuid.UUID(spiral_state_id)
                
            saved_idea = await self.db_manager.save_creative_idea(idea, spiral_state_id)
            print(f"[Repository] Successfully saved idea: {idea.id}")
            return saved_idea
        except Exception as e:
            print(f"[Repository] Error saving idea: {e}")
            # Re-raise the exception to allow the caller to handle it
            raise
    
    async def get_idea(self, idea_id: Union[uuid.UUID, str]) -> Optional[CreativeIdea]:
        """
        Get an idea by ID.
        
        Args:
            idea_id: The idea ID (UUID or string)
            
        Returns:
            Optional[CreativeIdea]: The idea if found
        """
        # Convert string ID to UUID if necessary
        if isinstance(idea_id, str):
            idea_id = uuid.UUID(idea_id)
            
        return await self.db_manager.get_creative_idea(idea_id)
    
    async def get_ideas_by_framework(self, framework: str) -> List[CreativeIdea]:
        """
        Get ideas by generative framework.
        
        Args:
            framework: The framework name
            
        Returns:
            List[CreativeIdea]: List of ideas
        """
        return await self.db_manager.get_ideas_by_framework(framework)
    
    async def get_all_ideas(self, limit: int = 50, offset: int = 0) -> List[CreativeIdea]:
        """
        Get all creative ideas with pagination.
        
        Args:
            limit: Maximum number of ideas to return
            offset: Number of ideas to skip
            
        Returns:
            List[CreativeIdea]: List of creative ideas
        """
        print(f"[Repository] Getting all creative ideas with limit={limit}, offset={offset}")
        try:
            # If this fails, it might be a database connectivity issue
            ideas = await self.db_manager.get_all_creative_ideas(limit, offset)
            
            # Return empty list instead of error if no ideas are found
            if ideas is None:
                print("[Repository] No ideas found, returning empty list")
                return []
                
            print(f"[Repository] Retrieved {len(ideas)} creative ideas")
            return ideas
        except Exception as e:
            print(f"[Repository] Error getting all creative ideas: {e}")
            # In production you might want to return an empty list instead of raising
            # but during development, we'll raise to see the actual error
            raise
    
    # Thinking step operations
    async def save_thinking_step(self, step: ThinkingStep, 
                                spiral_state_id: Optional[Union[uuid.UUID, str]] = None) -> ThinkingStep:
        """
        Save a thinking step.
        
        Args:
            step: The thinking step to save
            spiral_state_id: Optional spiral state ID (UUID or string)
            
        Returns:
            ThinkingStep: The saved thinking step
        """
        # Convert string ID to UUID if necessary
        if spiral_state_id is not None and isinstance(spiral_state_id, str):
            spiral_state_id = uuid.UUID(spiral_state_id)
            
        return await self.db_manager.save_thinking_step(step, spiral_state_id)
    
    # Spiral state operations
    async def save_spiral_state(self, state: SpiralState) -> SpiralState:
        """
        Save a spiral state.
        
        Args:
            state: The spiral state to save
            
        Returns:
            SpiralState: The saved spiral state
        """
        return await self.db_manager.save_spiral_state(state)
    
    async def get_spiral_state(self, state_id: Union[uuid.UUID, str]) -> Optional[SpiralState]:
        """
        Get a spiral state by ID.
        
        Args:
            state_id: The spiral state ID (UUID or string)
            
        Returns:
            Optional[SpiralState]: The spiral state if found
        """
        # Convert string ID to UUID if necessary
        if isinstance(state_id, str):
            state_id = uuid.UUID(state_id)
            
        return await self.db_manager.get_spiral_state(state_id)
    
    async def get_latest_spiral_state(self) -> Optional[SpiralState]:
        """
        Get the latest spiral state.
        
        Returns:
            Optional[SpiralState]: The latest spiral state
        """
        return await self.db_manager.get_latest_spiral_state()
    
    # Creative state operations
    async def save_creative_state(self, creative_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save the creative state.
        
        Args:
            creative_state: The creative state to save
            
        Returns:
            Dict[str, Any]: The saved creative state
        """
        # Extract components from creative state
        ideas = creative_state.get("ideas", [])
        thinking_steps = creative_state.get("thinking_steps", [])
        
        # Save ideas
        for idea in ideas:
            await self.save_idea(idea)
        
        # Save thinking steps
        for step in thinking_steps:
            await self.save_thinking_step(step)
        
        return creative_state