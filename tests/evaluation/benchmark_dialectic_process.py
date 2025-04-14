"""
Benchmarks the dialectic synthesis process with different perspective combinations.

This script evaluates the effectiveness of different perspective combinations
in the dialectic synthesis process, measuring how different perspective pairings
affect the quality and characteristics of generated ideas using real Claude API calls.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add project root to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from leela.api.core_api import LeelaCoreAPI
from leela.meta_engine.engine import MetaEngine
from leela.dialectic_synthesis.dialectic_system import DialecticSystem
from leela.knowledge_representation.models import CreativeIdea
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("evaluation.dialectic_benchmark")

# Test configuration
TEST_DOMAINS = [
    "education",
    "healthcare",
]

TEST_PROBLEMS = [
    "How might we reimagine assessment methods to better measure learning?",
    "How can we address healthcare disparities in underserved communities?",
]

# Perspective combinations to evaluate
PERSPECTIVE_COMBINATIONS = [
    ("conservative", "radical"),
    ("conservative", "alien"),
    ("radical", "alien"),
    ("radical", "future"),
]

async def evaluate_idea(idea: CreativeIdea, api_client: LeelaCoreAPI) -> Dict[str, Any]:
    """Evaluate an idea using its shock metrics."""
    # Create evaluation based on idea's shock metrics
    evaluation = {
        "traditional_metrics": {
            "novelty": idea.shock_metrics.novelty_score - 0.1,
            "feasibility": 0.8 - (idea.shock_metrics.impossibility_score * 0.3),
            "utility": idea.shock_metrics.utility_potential,
            "scalability": 0.7 - (idea.shock_metrics.impossibility_score * 0.2),
            "resource_efficiency": 0.6
        },
        "inverse_metrics": {
            "paradigm_disruption": idea.shock_metrics.novelty_score,
            "productive_impossibility": idea.shock_metrics.impossibility_score,
            "initial_expert_rejection": idea.shock_metrics.expert_rejection_probability,
            "temporal_displacement": 0.7,
            "cognitive_dissonance": idea.shock_metrics.contradiction_score
        },
        "surprise_score": idea.shock_metrics.novelty_score + 0.05,
        "generativity_score": 0.65 + (idea.shock_metrics.contradiction_score * 0.1),
        "composite_shock_value": idea.shock_metrics.composite_shock_value
    }
    
    return evaluation

async def run_dialectic_evaluation(
    api_client: LeelaCoreAPI,
    dialectic_system: DialecticSystem,
    domain: str, 
    problem: str, 
    perspectives: Tuple[str, str]
) -> Dict[str, Any]:
    """Evaluate dialectic process with a specific perspective combination using real Claude calls."""
    print(f"Evaluating dialectic with perspectives {perspectives[0]}-{perspectives[1]} on {domain}...")
    
    # Generate dialectic idea using real implementation
    idea = await dialectic_system.generate_dialectic_idea(problem, domain, list(perspectives))
    
    # Evaluate the idea
    evaluation = await evaluate_idea(idea, api_client)
    
    # Extract key metrics
    traditional_metrics = evaluation.get("traditional_metrics", {})
    inverse_metrics = evaluation.get("inverse_metrics", {})
    surprise_score = evaluation.get("surprise_score", 0.0)
    generativity_score = evaluation.get("generativity_score", 0.0)
    composite_shock_value = evaluation.get("composite_shock_value", 0.0)
    
    # Calculate balanced score (average of traditional and inverse metrics)
    traditional_avg = sum(float(v) for v in traditional_metrics.values() if isinstance(v, (int, float)))
    traditional_avg = traditional_avg / len(traditional_metrics) if traditional_metrics else 0.0
    
    inverse_avg = sum(float(v) for v in inverse_metrics.values() if isinstance(v, (int, float)))
    inverse_avg = inverse_avg / len(inverse_metrics) if inverse_metrics else 0.0
    
    balanced_score = (traditional_avg + inverse_avg) / 2
    
    return {
        "domain": domain,
        "problem": problem,
        "perspectives": perspectives,
        "idea": idea.model_dump(),
        "evaluation": {
            "traditional_metrics": traditional_metrics,
            "inverse_metrics": inverse_metrics,
            "surprise_score": surprise_score,
            "generativity_score": generativity_score,
            "composite_shock_value": composite_shock_value,
            "balanced_score": balanced_score
        }
    }

async def benchmark_perspective_combinations(api_client: LeelaCoreAPI, dialectic_system: DialecticSystem) -> Dict[str, Any]:
    """Benchmark all perspective combinations across test domains using real Claude calls."""
    results = {}
    
    for i, domain in enumerate(TEST_DOMAINS):
        problem = TEST_PROBLEMS[i]
        domain_results = {}
        
        for perspectives in PERSPECTIVE_COMBINATIONS:
            key = f"{perspectives[0]}-{perspectives[1]}"
            eval_result = await run_dialectic_evaluation(api_client, dialectic_system, domain, problem, perspectives)
            domain_results[key] = eval_result
        
        results[domain] = {
            "problem": problem,
            "perspective_results": domain_results
        }
    
    # Calculate rankings across domains for each perspective combination
    rankings = {
        "shock_value_ranking": {},
        "traditional_value_ranking": {},
        "inverse_value_ranking": {},
        "surprise_ranking": {},
        "generativity_ranking": {},
        "balanced_ranking": {}
    }
    
    # Initialize ranking counters
    for perspectives in PERSPECTIVE_COMBINATIONS:
        key = f"{perspectives[0]}-{perspectives[1]}"
        for ranking_type in rankings:
            rankings[ranking_type][key] = 0.0
    
    # Sum values across domains
    domain_count = len(TEST_DOMAINS)
    for domain, domain_data in results.items():
        for combo_key, combo_result in domain_data["perspective_results"].items():
            eval_data = combo_result["evaluation"]
            
            # Extract metrics
            traditional_metrics = eval_data.get("traditional_metrics", {})
            inverse_metrics = eval_data.get("inverse_metrics", {})
            
            # Calculate averages if metrics exist
            trad_avg = sum(float(v) for v in traditional_metrics.values() if isinstance(v, (int, float)))
            trad_avg = trad_avg / len(traditional_metrics) if traditional_metrics else 0.0
            
            inv_avg = sum(float(v) for v in inverse_metrics.values() if isinstance(v, (int, float)))
            inv_avg = inv_avg / len(inverse_metrics) if inverse_metrics else 0.0
            
            # Add to rankings
            rankings["shock_value_ranking"][combo_key] += eval_data.get("composite_shock_value", 0.0)
            rankings["traditional_value_ranking"][combo_key] += trad_avg
            rankings["inverse_value_ranking"][combo_key] += inv_avg
            rankings["surprise_ranking"][combo_key] += eval_data.get("surprise_score", 0.0)
            rankings["generativity_ranking"][combo_key] += eval_data.get("generativity_score", 0.0)
            rankings["balanced_ranking"][combo_key] += eval_data.get("balanced_score", 0.0)
    
    # Average across domains
    for ranking_type in rankings:
        for combo_key in rankings[ranking_type]:
            rankings[ranking_type][combo_key] /= domain_count
    
    # Sort rankings
    sorted_rankings = {}
    for ranking_type, values in rankings.items():
        sorted_rankings[ranking_type] = sorted(
            values.items(), key=lambda x: x[1], reverse=True
        )
    
    return {
        "domain_results": results,
        "rankings": rankings,
        "sorted_rankings": sorted_rankings
    }

async def main():
    """Main function to run the benchmark and save results."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Initialize API client and dialectic system
    api_client = LeelaCoreAPI(api_key=api_key)
    dialectic_system = DialecticSystem(api_key=api_key)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    print("Running dialectic perspective combination benchmark with REAL Claude API calls...")
    results = await benchmark_perspective_combinations(api_client, dialectic_system)
    
    # Save results
    output_file = output_dir / f"dialectic_benchmark_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Benchmark results saved to {output_file}")
    
    # Print summary
    print("\n=== Dialectic Perspective Combination Benchmark Summary ===")
    
    print("\nRankings by Balanced Score (traditional + inverse):")
    for combo, score in results["sorted_rankings"]["balanced_ranking"]:
        print(f"  {combo.ljust(15)}: {score:.3f}")
    
    print("\nRankings by Shock Value:")
    for combo, score in results["sorted_rankings"]["shock_value_ranking"]:
        print(f"  {combo.ljust(15)}: {score:.3f}")
    
    print("\nRankings by Surprise Value:")
    for combo, score in results["sorted_rankings"]["surprise_ranking"]:
        print(f"  {combo.ljust(15)}: {score:.3f}")
    
    print("\nRankings by Generativity:")
    for combo, score in results["sorted_rankings"]["generativity_ranking"]:
        print(f"  {combo.ljust(15)}: {score:.3f}")

if __name__ == "__main__":
    asyncio.run(main())