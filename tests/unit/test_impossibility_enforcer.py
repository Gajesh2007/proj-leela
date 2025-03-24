"""
Unit tests for the Impossibility Enforcer.
"""
import uuid
import pytest
from leela.shock_generation.impossibility_enforcer import ImpossibilityEnforcer
from leela.knowledge_representation.models import ThinkingStep, ShockProfile, CreativeIdea


class TestImpossibilityEnforcer:
    """Test suite for the Impossibility Enforcer."""
    
    def test_check_impossibility(self):
        """Test the check_impossibility method."""
        # Create an enforcer
        enforcer = ImpossibilityEnforcer()
        
        # Test with no constraints
        score = enforcer.check_impossibility(
            idea="This is a simple idea",
            domain="physics",
            impossibility_constraints=[]
        )
        assert score == 0.0
        
        # Test with matching constraints
        score = enforcer.check_impossibility(
            idea="A perpetual motion machine that generates energy from nothing",
            domain="physics",
            impossibility_constraints=["perpetual_motion", "zero_energy_computation"]
        )
        assert score > 0.0
        assert score <= 1.0
        
        # Test with non-matching constraints
        score = enforcer.check_impossibility(
            idea="A simple pendulum that swings back and forth",
            domain="physics",
            impossibility_constraints=["perpetual_motion", "faster_than_light_travel"]
        )
        assert score == 0.0
    
    def test_extract_idea_description(self):
        """Test the _extract_idea_description method."""
        # Create an enforcer
        enforcer = ImpossibilityEnforcer()
        
        # Test with a conclusion marker
        thinking_text = "This is some thinking.\n\nIn conclusion, this is the idea."
        description = enforcer._extract_idea_description(thinking_text)
        assert description == "this is the idea."
        
        # Test with another conclusion marker
        thinking_text = "This is some thinking.\n\nMy shocking idea: this is the idea."
        description = enforcer._extract_idea_description(thinking_text)
        assert description == "this is the idea."
        
        # Test with no conclusion marker
        thinking_text = "This is some thinking.\n\nThis is the last paragraph."
        description = enforcer._extract_idea_description(thinking_text)
        assert description == "This is the last paragraph."
    
    def test_enforce_impossibility(self):
        """Test the enforce_impossibility method."""
        # Create an enforcer
        enforcer = ImpossibilityEnforcer()
        
        # Create a thinking step
        thinking_step = ThinkingStep(
            id=uuid.uuid4(),
            framework="extended_thinking",
            reasoning_process="""
            This is some thinking about perpetual motion.
            
            Step 1: First, we need to understand why perpetual motion is impossible.
            
            Step 2: Then, we need to consider how we might achieve it anyway.
            
            In conclusion: A device that harvests zero-point energy from quantum fluctuations
            to create a perpetual motion machine that violates conventional thermodynamics.
            """,
            insights_generated=["Insight 1", "Insight 2"],
            token_usage=1000
        )
        
        # Test enforcing impossibility
        creative_idea = enforcer.enforce_impossibility(
            thinking_step=thinking_step,
            domain="physics",
            impossibility_constraints=["perpetual_motion", "zero_energy_computation"],
            shock_threshold=0.6
        )
        
        # Check the result
        assert isinstance(creative_idea, CreativeIdea)
        assert creative_idea.description
        assert creative_idea.generative_framework == "impossibility_enforcer"
        assert isinstance(creative_idea.shock_metrics, ShockProfile)
        assert creative_idea.shock_metrics.impossibility_score > 0.0