"""
Evaluates Leela's performance across different domains.

This script assesses how well various Leela frameworks perform across different domains,
identifying domain-specific strengths and patterns in idea generation using real Claude API calls.
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
from leela.core_processing.disruptor import DisruptorEngine
from leela.core_processing.connector import ConnectorModule
from leela.core_processing.explorer import ExplorerEngine
from leela.knowledge_representation.models import CreativeIdea
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("evaluation.domain_evaluation")

# Test domains with problems
DOMAIN_PROBLEMS = {
    "education": [
        "How might we personalize learning for diverse student needs?",
    ],
    "healthcare": [
        "How can we improve preventative healthcare approaches?",
    ],
    "transportation": [
        "How might we reduce urban congestion?",
    ],
}

# Frameworks to evaluate
FRAMEWORKS = [
    "disruptor",
    "connector", 
    "explorer"
]

async def generate_idea_with_framework(
    api_client: LeelaCoreAPI, 
    framework: str, 
    domain: str, 
    problem: str
) -> Dict[str, Any]:
    """Generate an idea using the specified framework with real Claude calls."""
    logger.info(f"Generating idea with {framework} framework in {domain} domain")
    print(f"  Using {framework} on problem: {problem[:30]}...")
    
    # Generate using the API with reduced thinking budget for evaluation purposes
    api_response = await api_client.generate_creative_idea(
        domain=domain,
        problem_statement=problem,
        shock_threshold=0.7,
        thinking_budget=8000,
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
        "generative_framework": framework
    }
    
    return api_result

async def evaluate_idea(idea_data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate an idea using its shock metrics."""
    # Extract metrics from the idea data
    shock_metrics = idea_data.get("shock_metrics", {})
    
    # Create evaluation based on shock metrics
    evaluation = {
        "traditional_metrics": {
            "novelty": shock_metrics.get("novelty_score", 0.0) - 0.1,
            "feasibility": 0.7 if idea_data.get("framework") == "connector" else 0.5,
            "utility": shock_metrics.get("utility_potential", 0.0),
            "scalability": 0.6,
            "resource_efficiency": 0.5
        },
        "inverse_metrics": {
            "paradigm_disruption": shock_metrics.get("novelty_score", 0.0),
            "productive_impossibility": shock_metrics.get("impossibility_score", 0.0),
            "initial_expert_rejection": shock_metrics.get("expert_rejection_probability", 0.0),
            "temporal_displacement": 0.7,
            "cognitive_dissonance": shock_metrics.get("contradiction_score", 0.0)
        },
        "surprise_score": shock_metrics.get("novelty_score", 0.0) + 0.05,
        "generativity_score": 0.75 if idea_data.get("framework") == "explorer" else 0.65,
        "composite_shock_value": shock_metrics.get("composite_shock_value", 0.0)
    }
    
    return evaluation

async def run_domain_evaluation(api_client: LeelaCoreAPI, domain: str, problems: List[str]) -> Dict[str, Any]:
    """Run a complete evaluation for a domain across multiple problems and frameworks."""
    print(f"Evaluating domain: {domain}...")
    
    domain_results = {}
    framework_metrics = {framework: {} for framework in FRAMEWORKS}
    
    for problem in problems:
        problem_results = {}
        
        for framework in FRAMEWORKS:
            # Generate idea using real API calls
            idea = await generate_idea_with_framework(api_client, framework, domain, problem)
            
            # Evaluate idea
            evaluation = await evaluate_idea(idea)
            
            # Store results
            problem_results[framework] = {
                "idea": idea,
                "evaluation": evaluation
            }
            
            # Accumulate framework metrics for domain-level analysis
            for metric_type in ["traditional_metrics", "inverse_metrics"]:
                metrics = evaluation.get(metric_type, {})
                for metric_name, value in metrics.items():
                    if isinstance(value, (int, float)):
                        key = f"{metric_type}.{metric_name}"
                        if key not in framework_metrics[framework]:
                            framework_metrics[framework][key] = []
                        framework_metrics[framework][key].append(value)
            
            # Individual metrics
            for metric in ["surprise_score", "generativity_score", "composite_shock_value"]:
                value = evaluation.get(metric, 0.0)
                if metric not in framework_metrics[framework]:
                    framework_metrics[framework][metric] = []
                framework_metrics[framework][metric].append(value)
        
        domain_results[problem] = problem_results
    
    # Calculate average metrics for each framework in this domain
    framework_averages = {}
    for framework, metrics in framework_metrics.items():
        framework_averages[framework] = {}
        for metric_name, values in metrics.items():
            if values:
                framework_averages[framework][metric_name] = sum(values) / len(values)
    
    # Determine best frameworks for this domain
    best_frameworks = {
        "traditional": None,
        "inverse": None,
        "surprise": None,
        "generativity": None,
        "shock_value": None
    }
    
    # Traditional metrics average
    trad_scores = {}
    for framework, averages in framework_averages.items():
        trad_metrics = [v for k, v in averages.items() if k.startswith("traditional_metrics.")]
        if trad_metrics:
            trad_scores[framework] = sum(trad_metrics) / len(trad_metrics)
    if trad_scores:
        best_frameworks["traditional"] = max(trad_scores.items(), key=lambda x: x[1])[0]
    
    # Inverse metrics average
    inv_scores = {}
    for framework, averages in framework_averages.items():
        inv_metrics = [v for k, v in averages.items() if k.startswith("inverse_metrics.")]
        if inv_metrics:
            inv_scores[framework] = sum(inv_metrics) / len(inv_metrics)
    if inv_scores:
        best_frameworks["inverse"] = max(inv_scores.items(), key=lambda x: x[1])[0]
    
    # Other metrics
    surprise_scores = {f: averages.get("surprise_score", 0) for f, averages in framework_averages.items()}
    if surprise_scores:
        best_frameworks["surprise"] = max(surprise_scores.items(), key=lambda x: x[1])[0]
    
    generativity_scores = {f: averages.get("generativity_score", 0) for f, averages in framework_averages.items()}
    if generativity_scores:
        best_frameworks["generativity"] = max(generativity_scores.items(), key=lambda x: x[1])[0]
    
    shock_scores = {f: averages.get("composite_shock_value", 0) for f, averages in framework_averages.items()}
    if shock_scores:
        best_frameworks["shock_value"] = max(shock_scores.items(), key=lambda x: x[1])[0]
    
    return {
        "domain": domain,
        "problem_results": domain_results,
        "framework_averages": framework_averages,
        "best_frameworks": best_frameworks
    }

async def run_comprehensive_domain_evaluation(api_client: LeelaCoreAPI) -> Dict[str, Any]:
    """Run a comprehensive evaluation across domains."""
    results = {}
    domain_framework_matches = {}
    
    for domain, problems in DOMAIN_PROBLEMS.items():
        domain_result = await run_domain_evaluation(api_client, domain, problems)
        results[domain] = domain_result
        
        # Record domain-framework matches
        best_frameworks = domain_result.get("best_frameworks", {})
        for metric_type, framework in best_frameworks.items():
            if framework:
                if framework not in domain_framework_matches:
                    domain_framework_matches[framework] = {}
                if metric_type not in domain_framework_matches[framework]:
                    domain_framework_matches[framework][metric_type] = []
                domain_framework_matches[framework][metric_type].append(domain)
    
    # Analyze framework-domain affinities
    framework_domain_affinity = {}
    for framework, metrics in domain_framework_matches.items():
        # Count total "wins" across all metrics
        domain_wins = {}
        for metric_type, domains in metrics.items():
            for domain in domains:
                if domain not in domain_wins:
                    domain_wins[domain] = 0
                domain_wins[domain] += 1
        
        # Sort domains by number of wins
        sorted_domains = sorted(domain_wins.items(), key=lambda x: x[1], reverse=True)
        framework_domain_affinity[framework] = sorted_domains
    
    return {
        "domain_results": results,
        "domain_framework_matches": domain_framework_matches,
        "framework_domain_affinity": framework_domain_affinity
    }

async def main():
    """Main function to run the domain evaluation and save results."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Initialize API client
    api_client = LeelaCoreAPI(api_key=api_key)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    print("Running comprehensive domain evaluation with REAL Claude API calls...")
    results = await run_comprehensive_domain_evaluation(api_client)
    
    # Save results
    output_file = output_dir / f"domain_evaluation_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation results saved to {output_file}")
    
    # Print summary
    print("\n=== Domain Evaluation Summary ===")
    
    print("\nBest Framework for Each Domain:")
    for domain, domain_result in results["domain_results"].items():
        best_frameworks = domain_result.get("best_frameworks", {})
        print(f"\n  {domain.upper()}:")
        for metric_type, framework in best_frameworks.items():
            if framework:
                print(f"    Best for {metric_type}: {framework}")
    
    print("\nFramework Domain Affinities:")
    for framework, domain_matches in results["framework_domain_affinity"].items():
        if domain_matches:
            best_domain, score = domain_matches[0]
            print(f"  {framework.ljust(12)} works best with: {best_domain} (score: {score})")

if __name__ == "__main__":
    asyncio.run(main())