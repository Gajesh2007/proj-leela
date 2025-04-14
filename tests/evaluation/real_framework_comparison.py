"""
Real framework comparison - runs evaluations of Leela's creative frameworks with actual Claude calls.

This script tests different creative frameworks across domains, measuring their effectiveness
by running actual calls to Claude through the full Leela stack.
"""
import asyncio
import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from leela.api.core_api import LeelaCoreAPI
from leela.meta_engine.engine import MetaEngine, CreativeWorkflow
from leela.data_persistence.repository import Repository
from leela.knowledge_representation.models import CreativeIdea, ShockProfile
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("evaluation.real_framework_comparison")

# Configuration
TEST_DOMAINS = [
    "education",
    "healthcare"
]

TEST_PROBLEMS = [
    "How might we personalize learning to adapt to each student's unique needs?",
    "How can we make preventative healthcare more engaging and accessible?"
]

# Creative frameworks to test
FRAMEWORKS = [
    "disruptor",
    "connector",
    "explorer"
]

# Map framework names to CreativeWorkflow enum values
WORKFLOW_MAP = {
    "disruptor": CreativeWorkflow.DISRUPTOR,
    "connector": CreativeWorkflow.CONNECTOR,
    "explorer": CreativeWorkflow.EXPLORER
}

async def generate_idea_with_framework(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    framework: str,
    domain: str,
    problem: str
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Generate an idea using the specified framework with real Claude calls."""
    logger.info(f"Generating idea with {framework} framework in {domain} domain")
    print(f"Generating idea with {framework} framework in {domain} domain...")
    
    # Generate using the API
    api_response = await api_client.generate_creative_idea(
        domain=domain,
        problem_statement=problem,
        shock_threshold=0.7,
        thinking_budget=12000,  # Reduced for quicker evaluation
        creative_framework=framework
    )
    
    # Generate using the Meta-Engine
    workflow = WORKFLOW_MAP.get(framework, CreativeWorkflow.DISRUPTOR)
    meta_result = await meta_engine.generate_idea(
        problem_statement=problem,
        domain=domain,
        workflow=workflow
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
        "source": "api"
    }
    
    # Format Meta-Engine result
    engine_result = {}
    if meta_result and "idea" in meta_result and meta_result["idea"]:
        engine_result = {
            "id": str(meta_result["idea"].id),
            "framework": meta_result["workflow"],
            "idea": meta_result["idea"].description,
            "domain": domain,
            "problem_statement": problem,
            "shock_metrics": {
                "novelty_score": meta_result["idea"].shock_metrics.novelty_score,
                "contradiction_score": meta_result["idea"].shock_metrics.contradiction_score,
                "impossibility_score": meta_result["idea"].shock_metrics.impossibility_score,
                "utility_potential": meta_result["idea"].shock_metrics.utility_potential,
                "expert_rejection_probability": meta_result["idea"].shock_metrics.expert_rejection_probability,
                "composite_shock_value": meta_result["idea"].shock_metrics.composite_shock_value
            },
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "source": "meta_engine"
        }
    
    return api_result, engine_result

async def run_framework_evaluation(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    framework: str,
    domain: str,
    problem: str
) -> Dict[str, Any]:
    """Run a complete evaluation for a framework on a domain/problem with real Claude calls."""
    print(f"Evaluating {framework} framework on {domain} domain...")
    
    # Generate idea
    api_result, engine_result = await generate_idea_with_framework(
        api_client, meta_engine, framework, domain, problem
    )
    
    # Create comprehensive result
    result = {
        "framework": framework,
        "domain": domain,
        "problem": problem,
        "api_result": api_result,
        "engine_result": engine_result
    }
    
    return result

async def compare_frameworks_in_domain(
    api_client: LeelaCoreAPI,
    meta_engine: MetaEngine,
    domain: str,
    problem: str
) -> Dict[str, Any]:
    """Compare all frameworks within a single domain/problem with real Claude calls."""
    results = {}
    
    for framework in FRAMEWORKS:
        result = await run_framework_evaluation(api_client, meta_engine, framework, domain, problem)
        results[framework] = result
    
    # Compute comparisons across frameworks
    comparisons = {
        "shock_values": {},
        "traditional_values": {},
        "generativity_values": {},
        "surprise_values": {}
    }
    
    for framework, result in results.items():
        # Use API results for comparison
        api_data = result["api_result"]
        shock_metrics = api_data.get("shock_metrics", {})
        
        # Extract key metrics for comparison
        comparisons["shock_values"][framework] = shock_metrics.get("composite_shock_value", 0.0)
        comparisons["surprise_values"][framework] = shock_metrics.get("novelty_score", 0.0) + 0.05
        
        # Approximate generativity as a function of novelty and contradiction
        novelty = shock_metrics.get("novelty_score", 0.0)
        contradiction = shock_metrics.get("contradiction_score", 0.0)
        comparisons["generativity_values"][framework] = (novelty + contradiction) / 2
        
        # Approximate traditional value as utility and inverse of impossibility
        utility = shock_metrics.get("utility_potential", 0.0)
        impossibility = shock_metrics.get("impossibility_score", 0.0)
        comparisons["traditional_values"][framework] = (utility + (1.0 - impossibility)) / 2
    
    return {
        "domain": domain,
        "problem": problem,
        "framework_results": results,
        "comparisons": comparisons
    }

async def run_comprehensive_evaluation(api_client: LeelaCoreAPI, meta_engine: MetaEngine) -> Dict[str, Any]:
    """Run a comprehensive evaluation across domains and frameworks with real Claude calls."""
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
        for framework in rankings[ranking_type]:
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
    output_file = output_dir / f"real_framework_evaluation_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation results saved to {output_file}")
    
    # Print summary
    print("\n=== Framework Evaluation Summary (REAL Claude API Results) ===")
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