"""
Core API module for Project Leela.
"""
from typing import Dict, List, Any, Optional, Union
import uuid
import asyncio
from pydantic import BaseModel, Field, UUID4
import json

from ..directed_thinking.claude_api import ClaudeAPIClient, ExtendedThinkingManager
from ..shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from ..shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier
from ..knowledge_representation.superposition_engine import SuperpositionEngine
from ..knowledge_representation.models import (
    ShockDirective, CreativeIdea, ShockProfile, ThinkingStep
)
from ..config import get_config


class CreativeIdeaRequest(BaseModel):
    """
    Request model for generating creative ideas.
    """
    domain: str = Field(..., description="Domain for idea generation")
    problem_statement: str = Field(..., description="Problem statement to generate ideas for")
    impossibility_constraints: List[str] = Field(default_factory=list, 
                                              description="Impossibility constraints to include")
    contradiction_requirements: List[str] = Field(default_factory=list, 
                                               description="Contradiction requirements to include")
    shock_threshold: float = Field(0.6, ge=0.0, le=1.0, description="Minimum shock threshold")
    thinking_budget: int = Field(16000, ge=1000, description="Thinking budget in tokens")
    creative_framework: str = Field("impossibility_enforcer", 
                                  description="Creative framework to use")


class CreativeIdeaResponse(BaseModel):
    """
    Response model for creative idea generation.
    """
    id: UUID4 = Field(..., description="Unique identifier")
    idea: str = Field(..., description="Generated idea")
    framework: str = Field(..., description="Framework used")
    shock_metrics: ShockProfile = Field(..., description="Shock metrics")
    thinking_steps: List[ThinkingStep] = Field(default_factory=list, 
                                            description="Thinking steps")


class DialecticIdeaRequest(BaseModel):
    """
    Request model for generating ideas through dialectic.
    """
    domain: str = Field(..., description="Domain for idea generation")
    problem_statement: str = Field(..., description="Problem statement to generate ideas for")
    perspectives: List[str] = Field(..., min_items=2, 
                                  description="Perspectives for dialectic")
    thinking_budget: int = Field(16000, ge=1000, description="Thinking budget in tokens")


class DialecticIdeaResponse(BaseModel):
    """
    Response model for dialectic idea generation.
    """
    id: UUID4 = Field(..., description="Unique identifier")
    synthesized_idea: str = Field(..., description="Synthesized idea")
    shock_metrics: ShockProfile = Field(..., description="Shock metrics")
    perspective_ideas: List[str] = Field(..., description="Ideas from each perspective")
    thinking_steps: List[ThinkingStep] = Field(default_factory=list, 
                                            description="Thinking steps")


class LeelaCoreAPI:
    """
    Core API for Project Leela.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Leela Core API.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        self.config = get_config()
        self.api_key = api_key or self.config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.claude_client = ClaudeAPIClient(self.api_key)
        self.thinking_manager = ExtendedThinkingManager(self.api_key)
        self.impossibility_enforcer = ImpossibilityEnforcer()
        self.dissonance_amplifier = CognitiveDissonanceAmplifier()
        self.superposition_engine = SuperpositionEngine()
    
    async def generate_creative_idea(self, 
                                   domain: str,
                                   problem_statement: str,
                                   impossibility_constraints: Optional[List[str]] = None,
                                   contradiction_requirements: Optional[List[str]] = None,
                                   shock_threshold: float = 0.6,
                                   thinking_budget: int = 16000,
                                   creative_framework: str = "impossibility_enforcer") -> CreativeIdeaResponse:
        """
        Generate a creative idea.
        
        Args:
            domain: Domain for idea generation
            problem_statement: Problem statement to generate ideas for
            impossibility_constraints: Impossibility constraints to include
            contradiction_requirements: Contradiction requirements to include
            shock_threshold: Minimum shock threshold
            thinking_budget: Thinking budget in tokens
            creative_framework: Creative framework to use
            
        Returns:
            CreativeIdeaResponse: The generated creative idea
        """
        # Prepare impossibility constraints
        if not impossibility_constraints and domain in self.config["domain_impossibilities"]:
            # Use domain-specific impossibility constraints from config
            impossibility_constraints = self.config["domain_impossibilities"][domain]
        elif not impossibility_constraints:
            impossibility_constraints = []
        
        # Prepare contradiction requirements
        if not contradiction_requirements:
            contradiction_requirements = []
        
        # Create shock directive
        directive = ShockDirective(
            id=uuid.uuid4(),
            shock_framework=creative_framework,
            problem_domain=domain,
            impossibility_constraints=impossibility_constraints,
            contradiction_requirements=contradiction_requirements,
            antipattern_instructions=f"Violate conventional patterns in {domain}.",
            thinking_instructions=f"Think about how to solve the following problem in a way that violates conventional assumptions: {problem_statement}",
            minimum_shock_threshold=shock_threshold,
            thinking_budget=thinking_budget
        )
        
        # Execute the directive
        thinking_step = await self.claude_client.execute_shock_directive(directive)
        
        # Generate creative idea based on framework
        creative_idea = None
        if creative_framework == "impossibility_enforcer":
            creative_idea = self.impossibility_enforcer.enforce_impossibility(
                thinking_step, domain, impossibility_constraints, shock_threshold
            )
        elif creative_framework == "cognitive_dissonance_amplifier":
            creative_idea = self.dissonance_amplifier.amplify_dissonance(
                thinking_step, domain, contradiction_requirements
            )
        else:
            # Default to impossibility enforcer
            creative_idea = self.impossibility_enforcer.enforce_impossibility(
                thinking_step, domain, impossibility_constraints, shock_threshold
            )
        
        # Prepare response
        response = CreativeIdeaResponse(
            id=creative_idea.id,
            idea=creative_idea.description,
            framework=creative_idea.generative_framework,
            shock_metrics=creative_idea.shock_metrics,
            thinking_steps=[thinking_step]
        )
        
        return response
    
    async def generate_dialectic_idea(self,
                                    domain: str,
                                    problem_statement: str,
                                    perspectives: List[str],
                                    thinking_budget: int = 16000) -> DialecticIdeaResponse:
        """
        Generate an idea through dialectic thinking from multiple perspectives.
        
        Args:
            domain: Domain for idea generation
            problem_statement: Problem statement to generate ideas for
            perspectives: Perspectives for dialectic
            thinking_budget: Thinking budget in tokens
            
        Returns:
            DialecticIdeaResponse: The generated dialectic idea
        """
        # Generate thinking from multiple perspectives
        # Ensure max_tokens is greater than thinking_budget
        max_tokens_value = thinking_budget + 1000
        
        thinking_steps = await self.thinking_manager.dialectic_thinking(
            prompt=f"Generate a creative solution to the following problem in {domain}: {problem_statement}",
            perspectives=perspectives,
            thinking_budget=thinking_budget,
            max_tokens=max_tokens_value
        )
        
        # Extract ideas from thinking steps
        perspective_ideas = []
        for step in thinking_steps:
            # Use same extraction method as in impossibility enforcer
            idea = self.impossibility_enforcer._extract_idea_description(step.reasoning_process)
            perspective_ideas.append(idea)
        
        # Create synthesis prompt
        synthesis_prompt = f"Synthesize the following ideas into a single creative solution to the problem in {domain}: {problem_statement}\n\n"
        for i, idea in enumerate(perspective_ideas):
            synthesis_prompt += f"Idea {i+1} (from {perspectives[i]} perspective):\n{idea}\n\n"
        synthesis_prompt += "Create a synthesis that maintains the creative tension between these perspectives rather than resolving it conventionally."
        
        # Generate synthesis thinking
        synthesis_step = await self.claude_client.generate_thinking(
            prompt=synthesis_prompt,
            thinking_budget=thinking_budget,
            max_tokens=max_tokens_value  # Reuse the same max_tokens value
        )
        
        # Extract synthesized idea
        synthesized_idea = self.impossibility_enforcer._extract_idea_description(
            synthesis_step.reasoning_process
        )
        
        # Generate shock metrics for synthesized idea
        # For simplicity, we're using a placeholder shock profile
        # In a real implementation, we'd evaluate the shock value more systematically
        shock_profile = ShockProfile(
            novelty_score=0.8,
            contradiction_score=0.85,
            impossibility_score=0.7,
            utility_potential=0.6,
            expert_rejection_probability=0.75,
            composite_shock_value=0.75
        )
        
        # Add synthesis step to thinking steps
        all_steps = thinking_steps + [synthesis_step]
        
        # Prepare response
        response = DialecticIdeaResponse(
            id=uuid.uuid4(),
            synthesized_idea=synthesized_idea,
            shock_metrics=shock_profile,
            perspective_ideas=perspective_ideas,
            thinking_steps=all_steps
        )
        
        return response