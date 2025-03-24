"""
Models for quantum-inspired knowledge representation.
"""
from typing import Dict, List, Any, Optional, Union
import uuid
from datetime import datetime
from pydantic import BaseModel, Field, UUID4


class ConceptState(BaseModel):
    """
    Represents a possible interpretation of a concept - one state in its superposition.
    """
    state_definition: str = Field(..., description="Definition of this concept state")
    probability: float = Field(..., ge=0.0, le=1.0, description="Weight of this interpretation")
    context_triggers: List[str] = Field(default_factory=list, 
                                        description="Contexts that trigger this state")


class EntanglementLink(BaseModel):
    """
    Represents a quantum-inspired connection between concepts.
    """
    target_concept_id: UUID4 = Field(..., description="ID of the target concept")
    entanglement_type: str = Field(..., description="Nature of quantum connection")
    correlation_strength: float = Field(..., ge=0.0, le=1.0, 
                                        description="Strength of correlation")
    evolution_rules: str = Field(..., description="How changes propagate")


class TemporalVariant(BaseModel):
    """
    Represents how a concept was understood in a specific historical era.
    """
    era: str = Field(..., description="Historical era (e.g., 'ancient', 'medieval')")
    definition: str = Field(..., description="Era-specific understanding")
    significance: str = Field(..., description="Historical context and importance")
    applicability_score: float = Field(..., ge=0.0, le=1.0, 
                                      description="Relevance to modern problems")


class Concept(BaseModel):
    """
    Represents a concept with quantum properties like superposition and entanglement.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    name: str = Field(..., description="Name of the concept")
    domain: str = Field(..., description="Domain this concept belongs to")
    definition: str = Field(..., description="Base definition of the concept")
    attributes: Dict[str, Any] = Field(default_factory=dict, 
                                     description="Attributes of the concept")
    superposition_states: List[ConceptState] = Field(default_factory=list, 
                                                   description="Possible interpretations")
    entanglements: List[EntanglementLink] = Field(default_factory=list, 
                                                description="Connected concepts")
    temporal_variants: Dict[str, TemporalVariant] = Field(default_factory=dict, 
                                                        description="Historical variants")


class Relationship(BaseModel):
    """
    Represents a relationship between two concepts.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    source_concept_id: UUID4 = Field(..., description="ID of the source concept")
    target_concept_id: UUID4 = Field(..., description="ID of the target concept")
    type: str = Field(..., description="Relationship type (e.g., 'is-a', 'part-of')")
    strength: float = Field(..., ge=0.0, le=1.0, description="Relationship strength")
    properties: Dict[str, Any] = Field(default_factory=dict, 
                                     description="Additional properties")
    bidirectional: bool = Field(default=False, 
                              description="Whether relationship applies in both directions")


class ShockProfile(BaseModel):
    """
    Represents various metrics for evaluating the shock value of an idea.
    """
    novelty_score: float = Field(..., ge=0.0, le=1.0, 
                               description="Distance from conventional approaches")
    contradiction_score: float = Field(..., ge=0.0, le=1.0, 
                                     description="Presence of unresolved paradoxes")
    impossibility_score: float = Field(..., ge=0.0, le=1.0, 
                                     description="Violation of domain assumptions")
    utility_potential: float = Field(..., ge=0.0, le=1.0, 
                                   description="Potential value despite shock")
    expert_rejection_probability: float = Field(..., ge=0.0, le=1.0, 
                                              description="Likelihood of expert dismissal")
    composite_shock_value: float = Field(..., ge=0.0, le=1.0, 
                                       description="Overall shock rating")


class CreativeIdea(BaseModel):
    """
    Represents a creative idea generated by the system.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    description: str = Field(..., description="Description of the idea")
    generative_framework: str = Field(..., description="Framework used to generate the idea")
    domain: Optional[str] = Field(None, description="Domain of the idea")
    impossibility_elements: List[str] = Field(default_factory=list, 
                                            description="Impossible elements included")
    contradiction_elements: List[str] = Field(default_factory=list, 
                                           description="Contradictory elements included")
    related_concepts: List[Any] = Field(default_factory=list, 
                                        description="Related concept IDs")
    shock_metrics: Optional[ShockProfile] = Field(None, description="Metrics for shock value")


class ThinkingStep(BaseModel):
    """
    Represents a single step in the thinking process.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    framework: str = Field(..., description="Thinking framework used")
    reasoning_process: str = Field(..., description="Detailed reasoning process")
    insights_generated: List[str] = Field(default_factory=list, 
                                       description="Insights generated in this step")
    token_usage: int = Field(..., ge=0, description="Tokens used in this step")


class MethodologyChange(BaseModel):
    """
    Represents a change in creative methodology.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    previous_methodology: str = Field(..., description="Previous methodology")
    new_methodology: str = Field(..., description="New methodology")
    evolution_rationale: str = Field(..., description="Rationale for the evolution")
    performance_change: float = Field(..., description="Performance improvement/decline")
    iteration_number: int = Field(..., ge=0, description="Iteration number")


class SpiralState(BaseModel):
    """
    Represents the state of the meta-creative spiral.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    timestamp: datetime = Field(default_factory=datetime.now, 
                              description="When this state was created")
    current_phase: str = Field(..., 
                             description="Create, Reflect, Abstract, Evolve, Transcend, or Return")
    problem_space: str = Field(..., description="Problem domain being explored")
    active_shock_frameworks: List[str] = Field(default_factory=list, 
                                            description="Active shock frameworks")
    generated_ideas: List[CreativeIdea] = Field(default_factory=list, 
                                             description="Ideas generated in this state")
    thinking_history: List[ThinkingStep] = Field(default_factory=list, 
                                              description="Thinking steps in this state")
    methodology_evolution: List[MethodologyChange] = Field(default_factory=list, 
                                                       description="Methodology changes")
    emergence_indicators: Dict[str, float] = Field(default_factory=dict, 
                                               description="Indicators of emergence")


class ShockDirective(BaseModel):
    """
    Represents instructions for generating shocking outputs.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, description="Unique identifier")
    shock_framework: str = Field(..., description="Shock framework to apply")
    problem_domain: str = Field(..., description="Domain to generate shock for")
    impossibility_constraints: List[str] = Field(default_factory=list, 
                                              description="Impossible elements to include")
    contradiction_requirements: List[str] = Field(default_factory=list, 
                                               description="Contradictions to maintain")
    antipattern_instructions: str = Field(..., description="Patterns to violate")
    thinking_instructions: str = Field(..., description="How to approach the problem")
    minimum_shock_threshold: float = Field(..., ge=0.0, le=1.0, 
                                        description="Required shock value")
    thinking_budget: int = Field(..., ge=0, description="Maximum thinking tokens to use")