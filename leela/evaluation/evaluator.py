"""
Evaluator Module - Causes measurement-induced collapse into concrete ideas through multi-dimensional evaluation.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import asyncio
from pydantic import UUID4
from ..config import get_config
from ..knowledge_representation.models import (
    CreativeIdea, ThinkingStep, ShockProfile
)
from ..knowledge_representation.superposition_engine import SuperpositionEngine
from ..directed_thinking.claude_api import ClaudeAPIClient


class TraditionalEvaluationSystem:
    """
    Applies conventional metrics to evaluate ideas.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Traditional Evaluation System.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def evaluate(self, idea: str, domain: str) -> Dict[str, float]:
        """
        Evaluate an idea using traditional metrics.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            Dict[str, float]: Map of metric name to score (0.0-1.0)
        """
        # Create an evaluation prompt
        prompt = f"""Evaluate this idea in the domain of {domain}:

{idea}

Assess the idea on each of these traditional metrics:

1. Novelty: How original is this idea compared to existing approaches? (0.0-1.0)
2. Feasibility: How technically feasible is this idea to implement? (0.0-1.0)
3. Utility: How well does this idea solve the intended problem? (0.0-1.0)
4. Scalability: How well would this idea scale to larger or more complex scenarios? (0.0-1.0)
5. Resource Efficiency: How efficient is this idea in terms of resources required? (0.0-1.0)

For each metric, provide:
- A numerical score from 0.0 (lowest) to 1.0 (highest)
- A brief justification for the score

Format each metric as: "Metric: [score] - Justification"

Finally, calculate an overall traditional value score as the average of all metrics."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract metrics from thinking
        metrics = self._extract_metrics(thinking_step.reasoning_process)
        
        return metrics
    
    def _extract_metrics(self, thinking_text: str) -> Dict[str, float]:
        """
        Extract metrics from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Dict[str, float]: Map of metric name to score
        """
        import re
        
        # Pattern for "Metric: [score] - Justification"
        pattern = r'(\w+):\s*(0\.\d+|1\.0)\s*-'
        matches = re.findall(pattern, thinking_text)
        
        metrics = {}
        for metric, score in matches:
            metrics[metric.lower()] = float(score)
        
        # Look for overall score
        overall_pattern = r'overall\s+\w+\s+score:?\s*(0\.\d+|1\.0)'
        overall_match = re.search(overall_pattern, thinking_text, re.IGNORECASE)
        if overall_match:
            metrics["overall"] = float(overall_match.group(1))
        else:
            # Calculate overall as average of other metrics
            if metrics:
                metrics["overall"] = sum(metrics.values()) / len(metrics)
        
        return metrics


class InverseEvaluationSystem:
    """
    Applies deliberately reversed metrics to evaluate ideas.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Inverse Evaluation System.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def evaluate(self, idea: str, domain: str) -> Dict[str, float]:
        """
        Evaluate an idea using inverse metrics.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            Dict[str, float]: Map of metric name to score (0.0-1.0)
        """
        # Create an evaluation prompt
        prompt = f"""Evaluate this idea in the domain of {domain} using INVERSE metrics:

{idea}

Conventional evaluation prizes feasibility, practicality, and immediate utility. In contrast, inverse evaluation deliberately values qualities that conventional metrics would penalize.

Assess the idea on each of these inverse metrics:

1. Paradigm Disruption: How much does this idea violate core assumptions in the domain? (0.0-1.0)
2. Productive Impossibility: How well does the idea utilize concepts considered "impossible" in productive ways? (0.0-1.0)
3. Initial Expert Rejection: How likely would domain experts be to initially reject this idea? (0.0-1.0)
4. Temporal Displacement: How far ahead of current thinking timeframes does this idea seem to be? (0.0-1.0)
5. Cognitive Dissonance: How much productive tension between contradictory elements does this idea maintain? (0.0-1.0)

For each metric, provide:
- A numerical score from 0.0 (lowest) to 1.0 (highest) 
- A brief justification for the score

Format each metric as: "Metric: [score] - Justification"

Finally, calculate an overall inverse value score as the average of all metrics."""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract metrics from thinking
        metrics = self._extract_metrics(thinking_step.reasoning_process)
        
        return metrics
    
    def _extract_metrics(self, thinking_text: str) -> Dict[str, float]:
        """
        Extract metrics from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Dict[str, float]: Map of metric name to score
        """
        import re
        
        # Pattern for "Metric: [score] - Justification"
        pattern = r'(\w+(?:\s+\w+)?):\s*(0\.\d+|1\.0)\s*-'
        matches = re.findall(pattern, thinking_text)
        
        metrics = {}
        for metric, score in matches:
            # Convert metric name to lowercase and replace spaces with underscores
            metric_key = metric.lower().replace(" ", "_")
            metrics[metric_key] = float(score)
        
        # Look for overall score
        overall_pattern = r'overall\s+\w+\s+score:?\s*(0\.\d+|1\.0)'
        overall_match = re.search(overall_pattern, thinking_text, re.IGNORECASE)
        if overall_match:
            metrics["overall"] = float(overall_match.group(1))
        else:
            # Calculate overall as average of other metrics
            if metrics:
                metrics["overall"] = sum(metrics.values()) / len(metrics)
        
        return metrics


class SurpriseCalculator:
    """
    Measures unexpectedness of solutions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Surprise Calculator.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def calculate_surprise(self, idea: str, domain: str) -> float:
        """
        Calculate the surprise value of an idea.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            float: Surprise score (0.0-1.0)
        """
        # Create a surprise evaluation prompt
        prompt = f"""Evaluate the SURPRISE VALUE of this idea in the domain of {domain}:

{idea}

Surprise value measures how unexpected and astonishing this idea would be to domain experts. Consider:

1. How much does this idea violate expert expectations?
2. Does it combine elements that are rarely or never combined?
3. Does it invert or subvert fundamental assumptions?
4. Would experts need to reconsider basic principles upon encountering it?
5. Does it create an "aha!" moment where something seemingly impossible suddenly appears possible?

Rank the surprise value on a scale from 0.0 (completely expected) to 1.0 (maximally surprising).

Provide:
- A numerical surprise score from 0.0 to 1.0
- A detailed justification explaining why the idea is surprising
- Specific examples of expert expectations it violates"""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract surprise score from thinking
        surprise_score = self._extract_surprise_score(thinking_step.reasoning_process)
        
        return surprise_score
    
    def _extract_surprise_score(self, thinking_text: str) -> float:
        """
        Extract surprise score from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            float: Surprise score
        """
        import re
        
        # Pattern for "Surprise Score: 0.X" or similar
        pattern = r'surprise\s+(?:value|score):\s*(0\.\d+|1\.0)'
        match = re.search(pattern, thinking_text, re.IGNORECASE)
        
        if match:
            return float(match.group(1))
        
        # Fallback: look for any number between 0 and 1
        number_pattern = r'(0\.\d+|1\.0)'
        numbers = re.findall(number_pattern, thinking_text)
        
        if numbers:
            # Take the first number that's likely a score
            return float(numbers[0])
        
        # Default fallback
        return 0.5


class GenerativityAssessor:
    """
    Evaluates a solution's ability to spawn further ideas.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Generativity Assessor.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        self.claude_client = ClaudeAPIClient(self.api_key)
    
    async def assess_generativity(self, idea: str, domain: str) -> Tuple[float, List[str]]:
        """
        Assess the generativity of an idea.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            Tuple[float, List[str]]: Generativity score and generated spin-off ideas
        """
        # Create a generativity evaluation prompt
        prompt = f"""Evaluate the GENERATIVITY of this idea in the domain of {domain}:

{idea}

Generativity measures how well this idea can spawn new ideas and approaches. The most valuable ideas aren't just solutions themselves but ones that open new solution spaces.

First, generate 3-5 spin-off ideas that could emerge from this original idea. These should be distinct but related concepts that build on the original in different ways.

Then, evaluate the idea's generativity considering:
1. How many diverse directions does this idea open up?
2. Does it create a new paradigm that could generate multiple applications?
3. Does it connect previously separate domains or concepts?
4. Does it introduce new tools, methods, or frameworks?
5. Could it lead to a cascade of follow-on innovations?

Rank the generativity on a scale from 0.0 (creative dead end) to 1.0 (extraordinarily generative).

Format:
- List 3-5 spin-off ideas
- Provide a numerical generativity score from 0.0 to 1.0
- Explain your reasoning for the generativity assessment"""
        
        # Generate thinking
        thinking_step = await self.claude_client.generate_thinking(
            prompt=prompt,
            thinking_budget=8000,
            max_tokens=2000
        )
        
        # Extract generativity score and spin-off ideas from thinking
        generativity_score, spinoff_ideas = self._extract_generativity(thinking_step.reasoning_process)
        
        return generativity_score, spinoff_ideas
    
    def _extract_generativity(self, thinking_text: str) -> Tuple[float, List[str]]:
        """
        Extract generativity score and spin-off ideas from thinking text.
        
        Args:
            thinking_text: The thinking text to extract from
            
        Returns:
            Tuple[float, List[str]]: Generativity score and spin-off ideas
        """
        import re
        
        # Extract spin-off ideas
        spinoff_ideas = []
        
        # Look for numbered or bulleted lists
        numbered_pattern = r'\d+\.\s+(.*?)(?=\d+\.\s+|\n\n|$)'
        numbered_matches = re.findall(numbered_pattern, thinking_text, re.DOTALL)
        
        bulleted_pattern = r'[-*•]\s+(.*?)(?=[-*•]\s+|\n\n|$)'
        bulleted_matches = re.findall(bulleted_pattern, thinking_text, re.DOTALL)
        
        # Combine matches
        matches = numbered_matches + bulleted_matches
        
        # Clean and add to spinoff ideas
        for match in matches:
            idea = match.strip()
            # Only add if not too short and not too long
            if 10 < len(idea) < 300:
                spinoff_ideas.append(idea)
        
        # Extract generativity score
        pattern = r'generativity\s+(?:value|score):\s*(0\.\d+|1\.0)'
        match = re.search(pattern, thinking_text, re.IGNORECASE)
        
        if match:
            generativity_score = float(match.group(1))
        else:
            # Fallback: look for any number between 0 and 1
            number_pattern = r'(0\.\d+|1\.0)'
            numbers = re.findall(number_pattern, thinking_text)
            
            if numbers:
                # Take the first number that's likely a score
                generativity_score = float(numbers[0])
            else:
                # Default fallback
                generativity_score = 0.5
        
        return generativity_score, spinoff_ideas[:5]  # Limit to 5 ideas


class EvaluatorModule:
    """
    Causes measurement-induced collapse into concrete ideas through multi-dimensional evaluation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Evaluator Module.
        
        Args:
            api_key: Optional API key for Claude. If not provided, will try to get from config.
        """
        config = get_config()
        self.api_key = api_key or config["api"]["anthropic_api_key"]
        
        # Initialize components
        self.traditional_evaluator = TraditionalEvaluationSystem(self.api_key)
        self.inverse_evaluator = InverseEvaluationSystem(self.api_key)
        self.surprise_calculator = SurpriseCalculator(self.api_key)
        self.generativity_assessor = GenerativityAssessor(self.api_key)
        self.superposition_engine = SuperpositionEngine()
    
    async def evaluate(self, idea: CreativeIdea, domain: str) -> Dict[str, Any]:
        """
        Evaluate an idea across multiple dimensions and cause measurement-induced collapse.
        
        Args:
            idea: The idea to evaluate
            domain: The domain of the idea
            
        Returns:
            Dict[str, Any]: Comprehensive evaluation results
        """
        # Store description for evaluation
        description = idea.description
        
        # Run evaluations in parallel
        traditional_metrics_task = self.traditional_evaluator.evaluate(description, domain)
        inverse_metrics_task = self.inverse_evaluator.evaluate(description, domain)
        surprise_score_task = self.surprise_calculator.calculate_surprise(description, domain)
        generativity_task = self.generativity_assessor.assess_generativity(description, domain)
        
        # Await all tasks
        traditional_metrics = await traditional_metrics_task
        inverse_metrics = await inverse_metrics_task
        surprise_score = await surprise_score_task
        generativity_score, spinoff_ideas = await generativity_task
        
        # Calculate composite shock value
        # Weight the different evaluation components
        config = get_config()
        weights = config["creativity"]
        
        # Get relevant metrics
        novelty = traditional_metrics.get("novelty", 0.5)
        utility = traditional_metrics.get("utility", 0.5)
        feasibility = traditional_metrics.get("feasibility", 0.5)
        
        paradigm_disruption = inverse_metrics.get("paradigm_disruption", 0.5)
        productive_impossibility = inverse_metrics.get("productive_impossibility", 0.5)
        cognitive_dissonance = inverse_metrics.get("cognitive_dissonance", 0.5)
        
        # Calculate composite shock value
        composite_shock_value = (
            weights["novelty_weight"] * novelty +
            weights["contradiction_weight"] * cognitive_dissonance +
            weights["impossibility_weight"] * productive_impossibility +
            weights["utility_weight"] * utility +
            weights["expert_rejection_weight"] * inverse_metrics.get("initial_expert_rejection", 0.5)
        )
        
        # Update the idea's shock profile
        updated_shock_profile = ShockProfile(
            novelty_score=novelty,
            contradiction_score=cognitive_dissonance,
            impossibility_score=productive_impossibility,
            utility_potential=utility,
            expert_rejection_probability=inverse_metrics.get("initial_expert_rejection", 0.5),
            composite_shock_value=composite_shock_value
        )
        
        # Create the collapsed idea
        collapsed_idea = CreativeIdea(
            id=idea.id,
            description=idea.description,
            generative_framework=idea.generative_framework,
            impossibility_elements=idea.impossibility_elements,
            contradiction_elements=idea.contradiction_elements,
            related_concepts=idea.related_concepts,
            shock_metrics=updated_shock_profile
        )
        
        # Create evaluation results
        results = {
            "traditional_metrics": traditional_metrics,
            "inverse_metrics": inverse_metrics,
            "surprise_score": surprise_score,
            "generativity_score": generativity_score,
            "spinoff_ideas": spinoff_ideas,
            "composite_shock_value": composite_shock_value,
            "collapsed_idea": collapsed_idea
        }
        
        return results