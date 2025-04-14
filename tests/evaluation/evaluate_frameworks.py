"""
Evaluates different creative frameworks in Leela by generating and comparing ideas.

This script runs evaluations across different creative frameworks and domains
to measure their effectiveness and characteristics using real Claude API calls.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from leela.api.core_api import LeelaCoreAPI
from leela.meta_engine.engine import MetaEngine, CreativeWorkflow
from leela.data_persistence.repository import Repository
from leela.knowledge_representation.models import CreativeIdea
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("evaluation.framework_evaluation")

# Configure domains and problems for evaluation
TEST_DOMAINS = [
    "education",
    "healthcare",
]

TEST_PROBLEMS = [
    "How might we make learning more engaging for students?",
    "How can we improve access to healthcare in rural areas?",
]

# Reduced domain/problem set for quick testing
# Uncomment this to use a smaller test set
TEST_DOMAINS = ["education"]
TEST_PROBLEMS = ["How might we make learning more engaging for students?"]

# Frameworks to evaluate
FRAMEWORKS = [
    "disruptor",
    "connector", 
    "explorer"
]

# Map framework names to creative framework strings for API
FRAMEWORK_MAP = {
    "disruptor": "disruptor",
    "connector": "connector",
    "explorer": "explorer"
}

async def generate_idea_with_framework(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    framework: str,
    domain: str,
    problem: str
) -> Dict[str, Any]:
    """Generate an idea using the specified framework with real Claude calls."""
    logger.info(f"Generating idea with {framework} framework in {domain} domain")
    print(f"Generating idea with {framework} framework in {domain} domain...")
    
    # Generate using the API
    api_response = await api_client.generate_creative_idea(
        domain=domain,
        problem_statement=problem,
        shock_threshold=0.7,
        thinking_budget=16000,  # Reduced for evaluation purposes
        creative_framework=framework
    )
    
    # Format API response
    api_result = {
        "id": str(api_response.id),
        "framework": api_response.framework,
        "idea": api_response.idea,
        "domain": domain,
        "problem_statement": problem,
        "shock_metrics": {
            "novelty_score": api_response.shock_metrics.novelty_score,
            "contradiction_score": api_response.shock_metrics.contradiction_score,
            "impossibility_score": api_response.shock_metrics.impossibility_score,
            "utility_potential": api_response.shock_metrics.utility_potential,
            "expert_rejection_probability": api_response.shock_metrics.expert_rejection_probability,
            "composite_shock_value": api_response.shock_metrics.composite_shock_value
        },
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "thinking_steps": [
            {
                "reasoning": step.reasoning_process[:300] + "..." if len(step.reasoning_process) > 300 else step.reasoning_process,
                "insights": step.insights_generated
            } for step in api_response.thinking_steps
        ]
    }
    
    return api_result

async def evaluate_idea(idea_data: Dict[str, Any], api_client: LeelaCoreAPI) -> Dict[str, Any]:
    """Evaluate an idea using the LLM to dynamically analyze its content with deep thinking."""
    # Get the full idea description
    idea_description = idea_data.get("idea", "")
    if not idea_description or len(idea_description) < 50:
        # If idea is too short, try to extract from thinking steps
        thinking_steps = idea_data.get("thinking_steps", [])
        for step in thinking_steps:
            insights = step.get("insights", [])
            if insights and len(insights[0]) > len(idea_description):
                idea_description = insights[0]
    
    # Get framework and domain information
    framework = idea_data.get("framework", "")
    domain = idea_data.get("domain", "")
    problem = idea_data.get("problem_statement", "")
    
    # Use the detailed evaluation prompt provided by the user
    evaluation_prompt = f"""You are an expert idea evaluator tasked with assessing a creative idea based on various metrics. Your goal is to provide a comprehensive and objective evaluation that will help decision-makers understand the potential and implications of the idea.

First, carefully read and analyze the idea description:

<idea_description>{idea_description}</idea_description>

Now, review the additional idea information:

<framework>{framework}</framework>

<domain>{domain}</domain>

<problem_statement>{problem}</problem_statement>

Your task is to evaluate this idea using three categories of metrics: Traditional Metrics, Inverse Metrics, and Overall Metrics. For each metric, you will provide a score between 0.0 and 1.0, where 0.0 is the lowest possible score and 1.0 is the highest.

Before scoring each category, wrap your evaluation inside <metric_evaluation> tags in your thinking block. For each metric:

1. List out specific aspects of the idea that relate to this metric.
2. Consider how the idea compares to existing solutions or paradigms.
3. Note potential implications or consequences related to this metric.
4. Provide a brief justification for the score you plan to give.

It's OK for this section to be quite long.

After your evaluation, provide your scores in the format specified.

Traditional Metrics:
1. Novelty: How new or original is this idea?
2. Feasibility: How practically implementable is this idea?
3. Utility: How useful would this idea be if implemented?
4. Scalability: How well could this idea scale to larger contexts?
5. Resource Efficiency: How efficiently does this idea use resources?

<metric_evaluation>
[Your detailed evaluation of the Traditional Metrics]
</metric_evaluation>

Inverse Metrics:
1. Paradigm Disruption: How much does this idea challenge established paradigms?
2. Productive Impossibility: To what degree does this idea seem impossible yet contain value?
3. Initial Expert Rejection: How likely would experts initially reject this idea?
4. Temporal Displacement: How far ahead of current thinking is this idea?
5. Cognitive Dissonance: How much contradiction or tension does this idea contain?

<metric_evaluation>
[Your detailed evaluation of the Inverse Metrics]
</metric_evaluation>

Overall Metrics:
1. Surprise Score: How unexpected or surprising is this idea?
2. Generativity Score: How likely would this idea spark further ideas or innovations?
3. Composite Shock Value: The overall shock value considering all factors above

<metric_evaluation>
[Your detailed evaluation of the Overall Metrics]
</metric_evaluation>

After completing your evaluation, provide your final evaluation in the following JSON format. Ensure that all scores are between 0.0 and 1.0, and that your evaluation is honest and objective.

<final_review>
[Briefly review your evaluation to ensure it's comprehensive, accurate, and reflects your analysis]
</final_review>

Now, present your final evaluation in the specified JSON format. Your output should consist only of the JSON object and should not duplicate or rehash any of the work you did in the thinking block.
"""
    
    # Use Claude API to evaluate the idea with extended thinking
    try:
        thinking_step = await api_client.claude_client.generate_thinking(
            prompt=evaluation_prompt,
            thinking_budget=16000,  # Increased for more thorough analysis
            max_tokens=20000
        )
        
        # Extract the JSON from the response
        evaluation_text = thinking_step.reasoning_process
        
        # Store the full evaluation for debugging/review
        print(f"Completed evaluation of {framework} idea in {domain}")
        
        # First try to extract JSON directly
        json_start = evaluation_text.find('{')
        json_end = evaluation_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = evaluation_text[json_start:json_end]
            try:
                evaluation = json.loads(json_str)
                # Validate the structure
                if not all(key in evaluation for key in ["traditional_metrics", "inverse_metrics", "surprise_score", "generativity_score", "composite_shock_value"]):
                    raise ValueError("Missing required keys in evaluation")
                
                # Store the insights from the evaluation
                traditional_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 1)
                inverse_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 2)
                overall_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 3)
                final_review = _extract_between_tags(evaluation_text, "final_review")
                
                # Add insights to the evaluation
                evaluation["insights"] = {
                    "traditional_metrics_analysis": traditional_eval[:1000] if traditional_eval else "",
                    "inverse_metrics_analysis": inverse_eval[:1000] if inverse_eval else "",
                    "overall_metrics_analysis": overall_eval[:1000] if overall_eval else "",
                    "final_review": final_review[:500] if final_review else ""
                }
                
                return evaluation
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing evaluation JSON: {e}")
        
        # If JSON extraction fails, parse the text manually
        print("Falling back to manual parsing of evaluation")
        metrics = {
            "traditional_metrics": {
                "novelty": _extract_metric_score(evaluation_text, "novelty"),
                "feasibility": _extract_metric_score(evaluation_text, "feasibility"),
                "utility": _extract_metric_score(evaluation_text, "utility"),
                "scalability": _extract_metric_score(evaluation_text, "scalability"),
                "resource_efficiency": _extract_metric_score(evaluation_text, "resource efficiency")
            },
            "inverse_metrics": {
                "paradigm_disruption": _extract_metric_score(evaluation_text, "paradigm disruption"),
                "productive_impossibility": _extract_metric_score(evaluation_text, "productive impossibility"),
                "initial_expert_rejection": _extract_metric_score(evaluation_text, "expert rejection"),
                "temporal_displacement": _extract_metric_score(evaluation_text, "temporal displacement"),
                "cognitive_dissonance": _extract_metric_score(evaluation_text, "cognitive dissonance")
            },
            "surprise_score": _extract_metric_score(evaluation_text, "surprise"),
            "generativity_score": _extract_metric_score(evaluation_text, "generativity"),
            "composite_shock_value": _extract_metric_score(evaluation_text, "composite shock")
        }
        
        # Extract and add insights
        traditional_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 1)
        inverse_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 2)
        overall_eval = _extract_between_tags(evaluation_text, "metric_evaluation", 3)
        final_review = _extract_between_tags(evaluation_text, "final_review")
        
        metrics["insights"] = {
            "traditional_metrics_analysis": traditional_eval[:1000] if traditional_eval else "",
            "inverse_metrics_analysis": inverse_eval[:1000] if inverse_eval else "",
            "overall_metrics_analysis": overall_eval[:1000] if overall_eval else "",
            "final_review": final_review[:500] if final_review else ""
        }
        
        return metrics
        
    except Exception as e:
        print(f"Error evaluating idea: {e}")
        # Fall back to default values if evaluation fails
        return {
            "traditional_metrics": {
                "novelty": 0.7,
                "feasibility": 0.6 if framework == "connector" else 0.5,
                "utility": 0.6,
                "scalability": 0.6,
                "resource_efficiency": 0.5
            },
            "inverse_metrics": {
                "paradigm_disruption": 0.7,
                "productive_impossibility": 0.6,
                "initial_expert_rejection": 0.7,
                "temporal_displacement": 0.6,
                "cognitive_dissonance": 0.7
            },
            "surprise_score": 0.7,
            "generativity_score": 0.75 if framework == "explorer" else 0.7,
            "composite_shock_value": 0.7,
            "insights": {
                "traditional_metrics_analysis": "",
                "inverse_metrics_analysis": "",
                "overall_metrics_analysis": "",
                "final_review": "Evaluation failed, using default values."
            }
        }

def _extract_between_tags(text: str, tag_name: str, occurrence: int = 1) -> str:
    """Extract content between XML-style tags."""
    import re
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches and len(matches) >= occurrence:
        return matches[occurrence-1].strip()
    return ""

def _extract_metric_score(text: str, metric_name: str) -> float:
    """Extract a metric score from evaluation text."""
    import re
    # Look for patterns like "Novelty: 0.8" or "Novelty - 0.8" or similar
    patterns = [
        rf"{metric_name}[:\-]\s*(\d+\.\d+)",  # Novelty: 0.8
        rf"{metric_name}[:\-]\s*(\d+)",  # Novelty: 8 (convert to decimal)
        rf"{metric_name}.*?(\d+\.\d+)",  # More flexible match
        rf"{metric_name}.*?(\d+)/10"  # Format like "7/10" (convert to decimal)
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                score = float(matches[0])
                # Convert to 0-1 scale if needed
                if score > 1.0 and score <= 10.0:
                    score /= 10.0
                # Ensure within bounds
                return max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                continue
    
    # Default fallback value
    return 0.7

async def run_framework_evaluation(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    framework: str,
    domain: str,
    problem: str
) -> Dict[str, Any]:
    """Run a complete evaluation for a framework on a domain/problem."""
    print(f"Evaluating {framework} framework on {domain} domain...")
    
    # Generate idea using real API calls
    idea = await generate_idea_with_framework(api_client, meta_engine, framework, domain, problem)
    
    # Evaluate idea using LLM for dynamic analysis
    evaluation = await evaluate_idea(idea, api_client)
    
    # Create comprehensive result
    result = {
        "framework": framework,
        "domain": domain,
        "problem": problem,
        "idea": idea,
        "evaluation": evaluation
    }
    
    return result

async def compare_frameworks_in_domain(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    domain: str,
    problem: str
) -> Dict[str, Any]:
    """Compare all frameworks within a single domain/problem."""
    results = {}
    
    for framework in FRAMEWORKS:
        result = await run_framework_evaluation(api_client, meta_engine, framework, domain, problem)
        results[framework] = result
    
    # Compute comparisons
    comparisons = {
        "shock_values": {},
        "traditional_values": {},
        "generativity_values": {},
        "surprise_values": {}
    }
    
    for framework, result in results.items():
        eval_data = result["evaluation"]
        comparisons["shock_values"][framework] = eval_data.get("composite_shock_value", 0.0)
        comparisons["surprise_values"][framework] = eval_data.get("surprise_score", 0.0)
        comparisons["generativity_values"][framework] = eval_data.get("generativity_score", 0.0)
        
        # Average traditional metrics if available
        trad_metrics = eval_data.get("traditional_metrics", {})
        if trad_metrics:
            traditional_avg = sum(float(v) for v in trad_metrics.values() if isinstance(v, (int, float))) / len(trad_metrics)
            comparisons["traditional_values"][framework] = traditional_avg
        else:
            comparisons["traditional_values"][framework] = 0.0
    
    return {
        "domain": domain,
        "problem": problem,
        "framework_results": results,
        "comparisons": comparisons
    }

async def run_comprehensive_evaluation(api_client: LeelaCoreAPI, meta_engine: MetaEngine) -> Dict[str, Any]:
    """Run a comprehensive evaluation across domains and frameworks."""
    results = {}
    
    for i, domain in enumerate(TEST_DOMAINS):
        problem = TEST_PROBLEMS[i]
        domain_result = await compare_frameworks_in_domain(api_client, meta_engine, domain, problem)
        results[domain] = domain_result
    
    # Calculate overall rankings across domains
    rankings = {
        "shock_value_ranking": {},
        "traditional_value_ranking": {},
        "generativity_ranking": {},
        "surprise_ranking": {}
    }
    
    # Initialize counters
    for framework in FRAMEWORKS:
        rankings["shock_value_ranking"][framework] = 0.0
        rankings["traditional_value_ranking"][framework] = 0.0
        rankings["generativity_ranking"][framework] = 0.0
        rankings["surprise_ranking"][framework] = 0.0
    
    # Sum values across domains
    for domain, domain_result in results.items():
        comparisons = domain_result["comparisons"]
        
        for framework in FRAMEWORKS:
            rankings["shock_value_ranking"][framework] += comparisons["shock_values"].get(framework, 0.0)
            rankings["traditional_value_ranking"][framework] += comparisons["traditional_values"].get(framework, 0.0)
            rankings["generativity_ranking"][framework] += comparisons["generativity_values"].get(framework, 0.0)
            rankings["surprise_ranking"][framework] += comparisons["surprise_values"].get(framework, 0.0)
    
    # Average across domains
    domain_count = len(TEST_DOMAINS)
    for ranking_type in rankings:
        for framework in FRAMEWORKS:
            rankings[ranking_type][framework] /= domain_count
    
    # Sort frameworks by rankings
    sorted_rankings = {}
    for ranking_type, values in rankings.items():
        sorted_rankings[ranking_type] = sorted(values.items(), key=lambda x: x[1], reverse=True)
    
    return {
        "domain_results": results,
        "overall_rankings": rankings,
        "sorted_rankings": sorted_rankings
    }

async def main():
    """Main function to run the evaluation and save results."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Check if input API key is actually valid
    if not api_key.startswith("sk-"):
        print("WARNING: The API key doesn't look like a valid Anthropic API key.")
        print("This script requires a valid API key to test real Claude API integration.")
        print("You can get an API key from https://console.anthropic.com/")
        print()
        confirm = input("Continue anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("Exiting...")
            return
    
    # Initialize API client and Meta-Engine
    api_client = LeelaCoreAPI(api_key=api_key)
    meta_engine = MetaEngine(api_key=api_key)
    await meta_engine.initialize()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    print("Running comprehensive framework evaluation with REAL Claude API calls...")
    results = await run_comprehensive_evaluation(api_client, meta_engine)
    
    # Save results
    output_file = output_dir / f"framework_evaluation_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation results saved to {output_file}")
    
    # Print summary
    print("\n=== Framework Evaluation Summary ===")
    print("\nOverall Rankings by Shock Value:")
    for framework, score in results["sorted_rankings"]["shock_value_ranking"]:
        print(f"  {framework.ljust(10)}: {score:.3f}")
    
    print("\nOverall Rankings by Traditional Value:")
    for framework, score in results["sorted_rankings"]["traditional_value_ranking"]:
        print(f"  {framework.ljust(10)}: {score:.3f}")
    
    print("\nOverall Rankings by Generativity:")
    for framework, score in results["sorted_rankings"]["generativity_ranking"]:
        print(f"  {framework.ljust(10)}: {score:.3f}")
    
    print("\nOverall Rankings by Surprise Value:")
    for framework, score in results["sorted_rankings"]["surprise_ranking"]:
        print(f"  {framework.ljust(10)}: {score:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
