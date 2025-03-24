"""
Database interface for Project Leela's data persistence.
"""
import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, ForeignKey, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.future import select

from ..config import get_config
from ..knowledge_representation.models import (
    SpiralState, CreativeIdea, ThinkingStep, ShockProfile, MethodologyChange,
    Concept, ConceptState, EntanglementLink, TemporalVariant, Relationship
)

# Get database config
config = get_config()
db_config = config["db"]

# Create DB URL based on config
DB_URL = f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Create base model
Base = declarative_base()


class DBConceptState(Base):
    """Database model for concept states."""
    __tablename__ = "concept_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False)
    state_definition = Column(Text, nullable=False)
    probability = Column(Float, nullable=False)
    context_triggers = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_pydantic(self) -> ConceptState:
        """Convert DB model to Pydantic model."""
        return ConceptState(
            state_definition=self.state_definition,
            probability=self.probability,
            context_triggers=self.context_triggers,
        )
    
    @classmethod
    def from_pydantic(cls, concept_id: uuid.UUID, state: ConceptState) -> "DBConceptState":
        """Create DB model from Pydantic model."""
        return cls(
            concept_id=concept_id,
            state_definition=state.state_definition,
            probability=state.probability,
            context_triggers=state.context_triggers,
        )


class DBEntanglementLink(Base):
    """Database model for entanglement links."""
    __tablename__ = "entanglement_links"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), nullable=False)
    entanglement_type = Column(String(100), nullable=False)
    correlation_strength = Column(Float, nullable=False)
    evolution_rules = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_pydantic(self) -> EntanglementLink:
        """Convert DB model to Pydantic model."""
        return EntanglementLink(
            target_concept_id=self.target_concept_id,
            entanglement_type=self.entanglement_type,
            correlation_strength=self.correlation_strength,
            evolution_rules=self.evolution_rules,
        )
    
    @classmethod
    def from_pydantic(cls, source_concept_id: uuid.UUID, link: EntanglementLink) -> "DBEntanglementLink":
        """Create DB model from Pydantic model."""
        return cls(
            source_concept_id=source_concept_id,
            target_concept_id=link.target_concept_id,
            entanglement_type=link.entanglement_type,
            correlation_strength=link.correlation_strength,
            evolution_rules=link.evolution_rules,
        )


class DBTemporalVariant(Base):
    """Database model for temporal variants."""
    __tablename__ = "temporal_variants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    concept_id = Column(UUID(as_uuid=True), ForeignKey("concepts.id"), nullable=False)
    era = Column(String(100), nullable=False)
    definition = Column(Text, nullable=False)
    significance = Column(Text, nullable=False)
    applicability_score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_pydantic(self) -> TemporalVariant:
        """Convert DB model to Pydantic model."""
        return TemporalVariant(
            era=self.era,
            definition=self.definition,
            significance=self.significance,
            applicability_score=self.applicability_score,
        )
    
    @classmethod
    def from_pydantic(cls, concept_id: uuid.UUID, era: str, variant: TemporalVariant) -> "DBTemporalVariant":
        """Create DB model from Pydantic model."""
        return cls(
            concept_id=concept_id,
            era=era,
            definition=variant.definition,
            significance=variant.significance,
            applicability_score=variant.applicability_score,
        )


class DBConcept(Base):
    """Database model for concepts."""
    __tablename__ = "concepts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)
    definition = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    states = relationship("DBConceptState", cascade="all, delete-orphan")
    entanglements = relationship("DBEntanglementLink", cascade="all, delete-orphan", 
                                foreign_keys="DBEntanglementLink.source_concept_id")
    temporal_variants = relationship("DBTemporalVariant", cascade="all, delete-orphan")
    
    def to_pydantic(self) -> Concept:
        """Convert DB model to Pydantic model."""
        # Create a simplified version without loading relationships
        return Concept(
            id=self.id,
            name=self.name,
            domain=self.domain,
            definition=self.definition,
            attributes=self.attributes,
            superposition_states=[],  # Avoid loading relationships in synchronous context
            entanglements=[],  # Avoid loading relationships in synchronous context
            temporal_variants={},  # Avoid loading relationships in synchronous context
        )
    
    @classmethod
    def from_pydantic(cls, concept: Concept) -> "DBConcept":
        """Create DB model from Pydantic model."""
        return cls(
            id=concept.id,
            name=concept.name,
            domain=concept.domain,
            definition=concept.definition,
            attributes=concept.attributes,
        )


class DBRelationship(Base):
    """Database model for relationships."""
    __tablename__ = "relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_concept_id = Column(UUID(as_uuid=True), nullable=False)
    target_concept_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(String(100), nullable=False)
    strength = Column(Float, nullable=False)
    properties = Column(JSONB, nullable=False, default=dict)
    bidirectional = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_pydantic(self) -> Relationship:
        """Convert DB model to Pydantic model."""
        return Relationship(
            id=self.id,
            source_concept_id=self.source_concept_id,
            target_concept_id=self.target_concept_id,
            type=self.type,
            strength=self.strength,
            properties=self.properties,
            bidirectional=self.bidirectional,
        )
    
    @classmethod
    def from_pydantic(cls, relationship: Relationship) -> "DBRelationship":
        """Create DB model from Pydantic model."""
        return cls(
            id=relationship.id,
            source_concept_id=relationship.source_concept_id,
            target_concept_id=relationship.target_concept_id,
            type=relationship.type,
            strength=relationship.strength,
            properties=relationship.properties,
            bidirectional=relationship.bidirectional,
        )


class DBShockProfile(Base):
    """Database model for shock profiles."""
    __tablename__ = "shock_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    idea_id = Column(UUID(as_uuid=True), ForeignKey("creative_ideas.id"), nullable=False)
    novelty_score = Column(Float, nullable=False)
    contradiction_score = Column(Float, nullable=False)
    impossibility_score = Column(Float, nullable=False)
    utility_potential = Column(Float, nullable=False)
    expert_rejection_probability = Column(Float, nullable=False)
    composite_shock_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_pydantic(self) -> ShockProfile:
        """Convert DB model to Pydantic model."""
        return ShockProfile(
            novelty_score=self.novelty_score,
            contradiction_score=self.contradiction_score,
            impossibility_score=self.impossibility_score,
            utility_potential=self.utility_potential,
            expert_rejection_probability=self.expert_rejection_probability,
            composite_shock_value=self.composite_shock_value,
        )
    
    @classmethod
    def from_pydantic(cls, idea_id: uuid.UUID, profile: ShockProfile) -> "DBShockProfile":
        """Create DB model from Pydantic model."""
        return cls(
            idea_id=idea_id,
            novelty_score=profile.novelty_score,
            contradiction_score=profile.contradiction_score,
            impossibility_score=profile.impossibility_score,
            utility_potential=profile.utility_potential,
            expert_rejection_probability=profile.expert_rejection_probability,
            composite_shock_value=profile.composite_shock_value,
        )


class DBCreativeIdea(Base):
    """Database model for creative ideas."""
    __tablename__ = "creative_ideas"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False)
    generative_framework = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=True)  # Domain field added
    impossibility_elements = Column(JSONB, nullable=False, default=list)
    contradiction_elements = Column(JSONB, nullable=False, default=list)
    related_concepts = Column(JSONB, nullable=False, default=list)
    spiral_state_id = Column(UUID(as_uuid=True), ForeignKey("spiral_states.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    shock_metrics = relationship("DBShockProfile", cascade="all, delete-orphan", uselist=False)
    
    def to_pydantic(self) -> CreativeIdea:
        """Convert DB model to Pydantic model."""
        # Make synchronous version that doesn't rely on related items that need async access
        return CreativeIdea(
            id=self.id,
            description=self.description,
            generative_framework=self.generative_framework,
            domain=self.domain,  # Include domain field
            impossibility_elements=self.impossibility_elements,
            contradiction_elements=self.contradiction_elements,
            related_concepts=self.related_concepts,
            # Don't try to access shock_metrics which might need an async call
            shock_metrics=None,
        )
    
    @classmethod
    def from_pydantic(cls, idea: CreativeIdea, spiral_state_id: Optional[uuid.UUID] = None) -> "DBCreativeIdea":
        """Create DB model from Pydantic model."""
        return cls(
            id=idea.id,
            description=idea.description,
            generative_framework=idea.generative_framework,
            domain=idea.domain,  # Include domain field
            impossibility_elements=idea.impossibility_elements,
            contradiction_elements=idea.contradiction_elements,
            related_concepts=[str(concept_id) for concept_id in idea.related_concepts],
            spiral_state_id=spiral_state_id,
        )


class DBThinkingStep(Base):
    """Database model for thinking steps."""
    __tablename__ = "thinking_steps"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework = Column(String(100), nullable=False)
    reasoning_process = Column(Text, nullable=False)
    insights_generated = Column(JSONB, nullable=False, default=list)
    token_usage = Column(Integer, nullable=False)
    spiral_state_id = Column(UUID(as_uuid=True), ForeignKey("spiral_states.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_pydantic(self) -> ThinkingStep:
        """Convert DB model to Pydantic model."""
        return ThinkingStep(
            id=self.id,
            framework=self.framework,
            reasoning_process=self.reasoning_process,
            insights_generated=self.insights_generated,
            token_usage=self.token_usage,
        )
    
    @classmethod
    def from_pydantic(cls, step: ThinkingStep, spiral_state_id: Optional[uuid.UUID] = None) -> "DBThinkingStep":
        """Create DB model from Pydantic model."""
        return cls(
            id=step.id,
            framework=step.framework,
            reasoning_process=step.reasoning_process,
            insights_generated=step.insights_generated,
            token_usage=step.token_usage,
            spiral_state_id=spiral_state_id,
        )


class DBMethodologyChange(Base):
    """Database model for methodology changes."""
    __tablename__ = "methodology_changes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    previous_methodology = Column(Text, nullable=False)
    new_methodology = Column(Text, nullable=False)
    evolution_rationale = Column(Text, nullable=False)
    performance_change = Column(Float, nullable=False)
    iteration_number = Column(Integer, nullable=False)
    spiral_state_id = Column(UUID(as_uuid=True), ForeignKey("spiral_states.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_pydantic(self) -> MethodologyChange:
        """Convert DB model to Pydantic model."""
        return MethodologyChange(
            id=self.id,
            previous_methodology=self.previous_methodology,
            new_methodology=self.new_methodology,
            evolution_rationale=self.evolution_rationale,
            performance_change=self.performance_change,
            iteration_number=self.iteration_number,
        )
    
    @classmethod
    def from_pydantic(cls, change: MethodologyChange, spiral_state_id: uuid.UUID) -> "DBMethodologyChange":
        """Create DB model from Pydantic model."""
        return cls(
            id=change.id,
            previous_methodology=change.previous_methodology,
            new_methodology=change.new_methodology,
            evolution_rationale=change.evolution_rationale,
            performance_change=change.performance_change,
            iteration_number=change.iteration_number,
            spiral_state_id=spiral_state_id,
        )


class DBSpiralState(Base):
    """Database model for spiral states."""
    __tablename__ = "spiral_states"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)
    current_phase = Column(String(50), nullable=False)
    problem_space = Column(Text, nullable=False)
    active_shock_frameworks = Column(JSONB, nullable=False, default=list)
    emergence_indicators = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    generated_ideas = relationship("DBCreativeIdea", cascade="all, delete-orphan")
    thinking_history = relationship("DBThinkingStep", cascade="all, delete-orphan")
    methodology_evolution = relationship("DBMethodologyChange", cascade="all, delete-orphan")
    
    def to_pydantic(self) -> SpiralState:
        """Convert DB model to Pydantic model."""
        # Create simple version without relationship loading
        return SpiralState(
            id=self.id,
            timestamp=self.timestamp,
            current_phase=self.current_phase,
            problem_space=self.problem_space,
            active_shock_frameworks=self.active_shock_frameworks,
            # Don't load relationships in synchronous method
            generated_ideas=[],  # These will be loaded separately if needed
            thinking_history=[],  # These will be loaded separately if needed
            methodology_evolution=[],  # These will be loaded separately if needed
            emergence_indicators=self.emergence_indicators,
        )
    
    @classmethod
    def from_pydantic(cls, state: SpiralState) -> "DBSpiralState":
        """Create DB model from Pydantic model."""
        return cls(
            id=state.id,
            timestamp=state.timestamp,
            current_phase=state.current_phase,
            problem_space=state.problem_space,
            active_shock_frameworks=state.active_shock_frameworks,
            emergence_indicators=state.emergence_indicators,
        )


class DatabaseManager:
    """Manages database operations for Project Leela."""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            db_url: Optional database URL. If not provided, uses the URL from config.
        """
        self.db_url = db_url or DB_URL
        self.engine = create_async_engine(self.db_url, echo=False)
        self.async_session = async_sessionmaker(self.engine, expire_on_commit=False)
    
    async def initialize_db(self):
        """Initialize database schema."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def save_concept(self, concept: Concept) -> Concept:
        """
        Save a concept to the database.
        
        Args:
            concept: The concept to save
            
        Returns:
            Concept: The saved concept with updated ID
        """
        async with self.async_session() as session:
            async with session.begin():
                # Check if concept exists
                result = await session.execute(
                    select(DBConcept).where(DBConcept.id == concept.id)
                )
                db_concept = result.scalars().first()
                
                if not db_concept:
                    # Create new concept
                    db_concept = DBConcept.from_pydantic(concept)
                    session.add(db_concept)
                    await session.flush()
                else:
                    # Update existing concept
                    db_concept.name = concept.name
                    db_concept.domain = concept.domain
                    db_concept.definition = concept.definition
                    db_concept.attributes = concept.attributes
                
                # Handle superposition states
                # Delete existing states
                await session.execute(
                    select(DBConceptState).where(DBConceptState.concept_id == db_concept.id)
                )
                
                # Add new states
                for state in concept.superposition_states:
                    db_state = DBConceptState.from_pydantic(db_concept.id, state)
                    session.add(db_state)
                
                # Handle entanglements
                # Delete existing entanglements
                await session.execute(
                    select(DBEntanglementLink).where(DBEntanglementLink.source_concept_id == db_concept.id)
                )
                
                # Add new entanglements
                for link in concept.entanglements:
                    db_link = DBEntanglementLink.from_pydantic(db_concept.id, link)
                    session.add(db_link)
                
                # Handle temporal variants
                # Delete existing variants
                await session.execute(
                    select(DBTemporalVariant).where(DBTemporalVariant.concept_id == db_concept.id)
                )
                
                # Add new variants
                for era, variant in concept.temporal_variants.items():
                    db_variant = DBTemporalVariant.from_pydantic(db_concept.id, era, variant)
                    session.add(db_variant)
                
                await session.commit()
                
                # Reload the concept with all relationships
                result = await session.execute(
                    select(DBConcept).where(DBConcept.id == db_concept.id)
                )
                db_concept = result.scalars().first()
                
                return db_concept.to_pydantic()
    
    async def get_concept(self, concept_id: uuid.UUID) -> Optional[Concept]:
        """
        Get a concept by ID.
        
        Args:
            concept_id: The concept ID
            
        Returns:
            Optional[Concept]: The concept if found, None otherwise
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(DBConcept).where(DBConcept.id == concept_id)
            )
            db_concept = result.scalars().first()
            
            if db_concept:
                return db_concept.to_pydantic()
            return None
    
    async def get_concepts_by_domain(self, domain: str) -> List[Concept]:
        """
        Get all concepts in a domain.
        
        Args:
            domain: The domain name
            
        Returns:
            List[Concept]: List of concepts in the domain
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(DBConcept).where(DBConcept.domain == domain)
            )
            db_concepts = result.scalars().all()
            
            return [db_concept.to_pydantic() for db_concept in db_concepts]
    
    async def save_relationship(self, relationship: Relationship) -> Relationship:
        """
        Save a relationship to the database.
        
        Args:
            relationship: The relationship to save
            
        Returns:
            Relationship: The saved relationship with updated ID
        """
        async with self.async_session() as session:
            async with session.begin():
                # Check if relationship exists
                result = await session.execute(
                    select(DBRelationship).where(DBRelationship.id == relationship.id)
                )
                db_relationship = result.scalars().first()
                
                if not db_relationship:
                    # Create new relationship
                    db_relationship = DBRelationship.from_pydantic(relationship)
                    session.add(db_relationship)
                else:
                    # Update existing relationship
                    db_relationship.source_concept_id = relationship.source_concept_id
                    db_relationship.target_concept_id = relationship.target_concept_id
                    db_relationship.type = relationship.type
                    db_relationship.strength = relationship.strength
                    db_relationship.properties = relationship.properties
                    db_relationship.bidirectional = relationship.bidirectional
                
                await session.commit()
                
                return db_relationship.to_pydantic()
    
    async def get_relationships_for_concept(self, concept_id: uuid.UUID) -> List[Relationship]:
        """
        Get all relationships for a concept.
        
        Args:
            concept_id: The concept ID
            
        Returns:
            List[Relationship]: List of relationships for the concept
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(DBRelationship).where(
                    (DBRelationship.source_concept_id == concept_id) | 
                    (DBRelationship.target_concept_id == concept_id)
                )
            )
            db_relationships = result.scalars().all()
            
            return [db_relationship.to_pydantic() for db_relationship in db_relationships]
    
    async def save_creative_idea(self, idea: CreativeIdea, spiral_state_id: Optional[uuid.UUID] = None) -> CreativeIdea:
        """
        Save a creative idea to the database.
        
        Args:
            idea: The idea to save
            spiral_state_id: Optional spiral state ID to associate with the idea
            
        Returns:
            CreativeIdea: The saved idea with updated ID
        """
        # Use context manager for session to ensure it gets closed properly
        async with self.async_session() as session:
            # Use a single transaction for the entire operation
            async with session.begin():
                try:
                    # Check if idea exists
                    result = await session.execute(
                        select(DBCreativeIdea).where(DBCreativeIdea.id == idea.id)
                    )
                    db_idea = result.scalars().first()
                    
                    if not db_idea:
                        # Create new idea
                        print(f"[DatabaseManager] Creating new idea with ID: {idea.id}")
                        db_idea = DBCreativeIdea.from_pydantic(idea, spiral_state_id)
                        session.add(db_idea)
                        # Flush but don't commit yet
                        await session.flush()
                    else:
                        # Update existing idea
                        print(f"[DatabaseManager] Updating existing idea with ID: {idea.id}")
                        db_idea.description = idea.description
                        db_idea.generative_framework = idea.generative_framework
                        db_idea.impossibility_elements = idea.impossibility_elements
                        db_idea.contradiction_elements = idea.contradiction_elements
                        db_idea.related_concepts = [str(concept_id) for concept_id in idea.related_concepts]
                        db_idea.spiral_state_id = spiral_state_id
                    
                    # Handle shock metrics
                    if idea.shock_metrics:
                        # Check if shock profile exists
                        result = await session.execute(
                            select(DBShockProfile).where(DBShockProfile.idea_id == db_idea.id)
                        )
                        db_profile = result.scalars().first()
                        
                        if not db_profile:
                            # Create new shock profile
                            print(f"[DatabaseManager] Creating new shock profile for idea: {db_idea.id}")
                            db_profile = DBShockProfile.from_pydantic(db_idea.id, idea.shock_metrics)
                            session.add(db_profile)
                        else:
                            # Update existing shock profile
                            print(f"[DatabaseManager] Updating existing shock profile for idea: {db_idea.id}")
                            db_profile.novelty_score = idea.shock_metrics.novelty_score
                            db_profile.contradiction_score = idea.shock_metrics.contradiction_score
                            db_profile.impossibility_score = idea.shock_metrics.impossibility_score
                            db_profile.utility_potential = idea.shock_metrics.utility_potential
                            db_profile.expert_rejection_probability = idea.shock_metrics.expert_rejection_probability
                            db_profile.composite_shock_value = idea.shock_metrics.composite_shock_value
                    
                    # Commit happens automatically at the end of the context manager
                    
                    # Create a return object with shock metrics
                    return_idea = CreativeIdea(
                        id=db_idea.id,
                        description=db_idea.description,
                        generative_framework=db_idea.generative_framework,
                        impossibility_elements=db_idea.impossibility_elements,
                        contradiction_elements=db_idea.contradiction_elements,
                        related_concepts=db_idea.related_concepts,
                        shock_metrics=idea.shock_metrics  # Use the original shock metrics to avoid reload issues
                    )
                    
                    print(f"[DatabaseManager] Successfully saved idea: {return_idea.id}")
                    return return_idea
                    
                except Exception as e:
                    print(f"[DatabaseManager] Error saving creative idea: {e}")
                    raise
    
    async def get_creative_idea(self, idea_id: uuid.UUID) -> Optional[CreativeIdea]:
        """
        Get a creative idea by ID.
        
        Args:
            idea_id: The idea ID
            
        Returns:
            Optional[CreativeIdea]: The idea if found, None otherwise
        """
        async with self.async_session() as session:
            # First get the idea
            result = await session.execute(
                select(DBCreativeIdea).where(DBCreativeIdea.id == idea_id)
            )
            db_idea = result.scalars().first()
            
            if not db_idea:
                return None
                
            # Convert to Pydantic model
            idea_model = db_idea.to_pydantic()
            
            # Get shock metrics separately to avoid async issues
            shock_result = await session.execute(
                select(DBShockProfile).where(DBShockProfile.idea_id == idea_id)
            )
            db_shock_profile = shock_result.scalars().first()
            
            if db_shock_profile:
                idea_model.shock_metrics = db_shock_profile.to_pydantic()
            else:
                # Create default shock metrics if none found
                idea_model.shock_metrics = ShockProfile(
                    novelty_score=0.7,
                    contradiction_score=0.7,
                    impossibility_score=0.7,
                    utility_potential=0.7,
                    expert_rejection_probability=0.7,
                    composite_shock_value=0.7
                )
                
            return idea_model
    
    async def get_ideas_by_framework(self, framework: str) -> List[CreativeIdea]:
        """
        Get all ideas generated by a specific framework.
        
        Args:
            framework: The generative framework
            
        Returns:
            List[CreativeIdea]: List of ideas generated by the framework
        """
        async with self.async_session() as session:
            # Get all ideas for this framework
            result = await session.execute(
                select(DBCreativeIdea).where(DBCreativeIdea.generative_framework == framework)
            )
            db_ideas = result.scalars().all()
            
            # Process each idea separately
            ideas = []
            for db_idea in db_ideas:
                try:
                    # Get the base idea
                    idea_model = db_idea.to_pydantic()
                    
                    # Get shock metrics separately to avoid async issues
                    if db_idea.id:
                        shock_result = await session.execute(
                            select(DBShockProfile).where(DBShockProfile.idea_id == db_idea.id)
                        )
                        db_shock_profile = shock_result.scalars().first()
                        
                        if db_shock_profile:
                            idea_model.shock_metrics = db_shock_profile.to_pydantic()
                        else:
                            # Create default shock metrics if none found
                            idea_model.shock_metrics = ShockProfile(
                                novelty_score=0.7,
                                contradiction_score=0.7,
                                impossibility_score=0.7,
                                utility_potential=0.7,
                                expert_rejection_probability=0.7,
                                composite_shock_value=0.7
                            )
                    else:
                        # Default shock metrics if ID is missing
                        idea_model.shock_metrics = ShockProfile(
                            novelty_score=0.7,
                            contradiction_score=0.7,
                            impossibility_score=0.7,
                            utility_potential=0.7,
                            expert_rejection_probability=0.7,
                            composite_shock_value=0.7
                        )
                        
                    ideas.append(idea_model)
                except Exception as e:
                    print(f"[DatabaseManager] Error processing idea for framework {framework}: {e}")
            
            return ideas
    
    async def save_thinking_step(self, step: ThinkingStep, spiral_state_id: Optional[uuid.UUID] = None) -> ThinkingStep:
        """
        Save a thinking step to the database.
        
        Args:
            step: The thinking step to save
            spiral_state_id: Optional spiral state ID to associate with the step
            
        Returns:
            ThinkingStep: The saved thinking step with updated ID
        """
        async with self.async_session() as session:
            async with session.begin():
                db_step = DBThinkingStep.from_pydantic(step, spiral_state_id)
                session.add(db_step)
                await session.commit()
                
                return db_step.to_pydantic()
    
    async def save_spiral_state(self, state: SpiralState) -> SpiralState:
        """
        Save a spiral state to the database.
        
        Args:
            state: The spiral state to save
            
        Returns:
            SpiralState: The saved spiral state with updated ID
        """
        async with self.async_session() as session:
            async with session.begin():
                # Create/update the spiral state
                db_state = DBSpiralState.from_pydantic(state)
                session.add(db_state)
                await session.flush()
                
                # Save ideas
                for idea in state.generated_ideas:
                    await self.save_creative_idea(idea, db_state.id)
                
                # Save thinking steps
                for step in state.thinking_history:
                    await self.save_thinking_step(step, db_state.id)
                
                # Save methodology changes
                for change in state.methodology_evolution:
                    db_change = DBMethodologyChange.from_pydantic(change, db_state.id)
                    session.add(db_change)
                
                await session.commit()
                
                # Reload the state with all relationships
                result = await session.execute(
                    select(DBSpiralState).where(DBSpiralState.id == db_state.id)
                )
                db_state = result.scalars().first()
                
                return db_state.to_pydantic()
    
    async def get_spiral_state(self, state_id: uuid.UUID) -> Optional[SpiralState]:
        """
        Get a spiral state by ID.
        
        Args:
            state_id: The spiral state ID
            
        Returns:
            Optional[SpiralState]: The spiral state if found, None otherwise
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(DBSpiralState).where(DBSpiralState.id == state_id)
            )
            db_state = result.scalars().first()
            
            if db_state:
                return db_state.to_pydantic()
            return None
    
    async def get_latest_spiral_state(self) -> Optional[SpiralState]:
        """
        Get the latest spiral state.
        
        Returns:
            Optional[SpiralState]: The latest spiral state if found, None otherwise
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(DBSpiralState).order_by(DBSpiralState.timestamp.desc()).limit(1)
            )
            db_state = result.scalars().first()
            
            if db_state:
                return db_state.to_pydantic()
            return None
            
    async def get_all_creative_ideas(self, limit: int = 50, offset: int = 0) -> List[CreativeIdea]:
        """
        Get all creative ideas with pagination.
        
        Args:
            limit: Maximum number of ideas to return
            offset: Number of ideas to skip
            
        Returns:
            List[CreativeIdea]: List of creative ideas
        """
        print(f"[DatabaseManager] Getting all creative ideas with limit={limit}, offset={offset}")
        
        # Create a new session for this operation
        async with self.async_session() as session:
            try:
                # Execute the query but don't start a transaction
                query = select(DBCreativeIdea).order_by(DBCreativeIdea.created_at.desc()).offset(offset).limit(limit)
                print(f"[DatabaseManager] Executing query: {query}")
                result = await session.execute(query)
                db_ideas = result.scalars().all()
                
                # Convert DB models to Pydantic models
                ideas = []
                for db_idea in db_ideas:
                    try:
                        # Get the base idea model
                        idea_model = db_idea.to_pydantic()
                        
                        # Always create default ShockProfile for retrieved ideas if not available
                        if not idea_model.shock_metrics:
                            # If we have shock metrics relationship, query it explicitly
                            if db_idea.id:
                                shock_profile_query = select(DBShockProfile).where(DBShockProfile.idea_id == db_idea.id)
                                shock_result = await session.execute(shock_profile_query)
                                db_shock_profile = shock_result.scalars().first()
                                
                                if db_shock_profile:
                                    idea_model.shock_metrics = db_shock_profile.to_pydantic()
                                else:
                                    # Create default shock metrics if none found
                                    idea_model.shock_metrics = ShockProfile(
                                        novelty_score=0.7,
                                        contradiction_score=0.7,
                                        impossibility_score=0.7,
                                        utility_potential=0.7,
                                        expert_rejection_probability=0.7,
                                        composite_shock_value=0.7
                                    )
                            else:
                                # Create default shock metrics if ID is missing
                                idea_model.shock_metrics = ShockProfile(
                                    novelty_score=0.7,
                                    contradiction_score=0.7,
                                    impossibility_score=0.7,
                                    utility_potential=0.7,
                                    expert_rejection_probability=0.7,
                                    composite_shock_value=0.7
                                )
                                
                        ideas.append(idea_model)
                    except Exception as e:
                        print(f"[DatabaseManager] Error converting idea to pydantic: {e}")
                
                print(f"[DatabaseManager] Found {len(ideas)} creative ideas")
                return ideas
            except Exception as e:
                print(f"[DatabaseManager] Error getting creative ideas: {e}")
                raise