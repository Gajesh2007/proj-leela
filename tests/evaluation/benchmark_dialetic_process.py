"""
Benchmarks the dialectic synthesis process with different perspective combinations.

This script evaluates the effectiveness of different perspective combinations
in the dialectic synthesis process, measuring how different perspective pairings
affect the quality and characteristics of generated ideas.
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

from leela.dialectic_synthesis.dialectic_system import DialecticSystem
from leela.evaluation.evaluator import EvaluatorModule
from leela.knowledge_representation.models import CreativeIdea
from leela.config import get_config

# Test configuration
TEST_DOMAINS = [
    "education",
    "healthcare",
    "energy"
]

TEST_PROBLEMS = [
    "How might we reimagine assessment methods to better measure learning?",
    "How can we address healthcare disparities in underserved communities?",
    "How might we accelerate the transition to sustainable energy systems?"
]

# Perspective combinations to evaluate
PERSPECTIVE_COMBINATIONS = [
    ("conservative", "radical"),
    ("conservative", "alien"),
    ("radical", "alien"),
    ("conservative", "future"),
    ("radical", "future"),
    ("alien", "future")
]

async def evaluate_idea(idea: CreativeIdea, domain: str) -> Dict[str, Any]:
    """Evaluate an idea using the EvaluatorModule."""
    evaluator = EvaluatorModule()
    return await evaluator.evaluate(idea, domain)

async def run_dialectic_evaluation(
    domain: str, 
    problem: str, 
    perspectives: Tuple[str, str]
) -> Dict[str, Any]:
    """Evaluate dialectic process with a specific perspective combination."""
    print(f"Evaluating dialectic with perspectives {perspectives[0]}-{perspectives[1]} on {domain}...")
    
    # Initialize the dialectic system
    dialectic = DialecticSystem()
    
    # Generate dialectic idea
    idea = await dialectic.generate_dialectic_idea(problem, domain, list(perspectives))
    
    # Evaluate the idea
    evaluation = await evaluate_idea(idea, domain)
    
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

async def benchmark_perspective_combinations() -> Dict[str, Any]:
    """Benchmark all perspective combinations across test domains."""
    results = {}
    
    for i, domain in enumerate(TEST_DOMAINS):
        problem = TEST_PROBLEMS[i]
        domain_results = {}
        
        for perspectives in PERSPECTIVE_COMBINATIONS:
            key = f"{perspectives[0]}-{perspectives[1]}"
            eval_result = await run_dialectic_evaluation(domain, problem, perspectives)
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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    print("Running dialectic perspective combination benchmark...")
    results = await benchmark_perspective_combinations()
    
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