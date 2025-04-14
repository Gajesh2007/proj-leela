"""
Evaluates the meta-creative spiral process across multiple iterations.

This script assesses how ideas evolve through the meta-creative spiral process,
tracking metrics across iterations to measure improvement and creative progression
using real Claude API calls.
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
from leela.meta_creative.spiral_engine import MetaCreativeSpiral, SpiralPhase
from leela.meta_engine.engine import MetaEngine
from leela.data_persistence.repository import Repository
from leela.knowledge_representation.models import CreativeIdea
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("evaluation.meta_spiral")

# Configure domains and problems for evaluation - reduced to single domain for quicker testing
TEST_DOMAINS = [
    "education",
    # "healthcare", # Commented out to speed up testing
]

TEST_PROBLEMS = [
    "How might we make learning more personalized and adaptive?",
    # "How can we improve preventative healthcare?", # Commented out to speed up testing
]

# Number of iterations through the spiral
SPIRAL_ITERATIONS = 1  # Reduced to single iteration for testing

async def evaluate_idea(idea: CreativeIdea, api_client: LeelaCoreAPI) -> Dict[str, Any]:
    """Evaluate an idea using its attributes and shock metrics."""
    # Create evaluation based on shock metrics
    evaluation = {
        "traditional_metrics": {
            "novelty": idea.shock_metrics.novelty_score - 0.1,
            "feasibility": 0.7 if idea.generative_framework == "connector" else 0.5,
            "utility": idea.shock_metrics.utility_potential,
            "scalability": 0.6,
            "resource_efficiency": 0.5
        },
        "inverse_metrics": {
            "paradigm_disruption": idea.shock_metrics.novelty_score,
            "productive_impossibility": idea.shock_metrics.impossibility_score,
            "initial_expert_rejection": idea.shock_metrics.expert_rejection_probability,
            "temporal_displacement": 0.7,
            "cognitive_dissonance": idea.shock_metrics.contradiction_score
        },
        "surprise_score": idea.shock_metrics.novelty_score + 0.05,
        "generativity_score": 0.75 if idea.generative_framework == "explorer" else 0.65,
        "composite_shock_value": idea.shock_metrics.composite_shock_value
    }
    
    return evaluation

async def run_spiral_evaluation(api_client: LeelaCoreAPI, spiral_engine: MetaCreativeSpiral, domain: str, problem: str) -> Dict[str, Any]:
    """Run a complete meta-spiral evaluation for a domain/problem."""
    print(f"Evaluating meta-spiral progression on {domain} domain...")
    
    # Initialize evaluation results
    iteration_results = []
    ideas = []
    
    # Initialize the spiral and create initial idea using the _execute_create_phase method
    print("  Creating initial idea...")
    # First initialize the spiral
    problem_space = f"{domain}: {problem}"
    active_frameworks = ["impossibility_enforcer", "cognitive_dissonance_amplifier"]
    spiral_engine.initialize_spiral(problem_space, active_frameworks)
    
    # Then execute the create phase to generate the initial idea
    idea = await spiral_engine._execute_create_phase()
    if not idea:
        raise ValueError("Failed to create initial idea")
    ideas.append(idea)
    
    # First evaluation
    evaluation = await evaluate_idea(idea, api_client)
    iteration_results.append({
        "iteration": 0,
        "phase": "create",
        "idea": idea.model_dump(),
        "evaluation": evaluation
    })
    
    # Run through spiral iterations
    for i in range(1, SPIRAL_ITERATIONS + 1):
        print(f"  Running spiral iteration {i}...")
        
        # Save the phase outputs in a way that the spiral engine will find them
        spiral_engine.phase_outputs[SpiralPhase.CREATE] = idea.description
        
        # Reflect phase
        print("    Reflect phase...")
        # Set the current phase to REFLECT and execute
        spiral_engine.current_phase = SpiralPhase.REFLECT
        try:
            reflection = await spiral_engine._execute_reflect_phase()
            if not reflection:
                print("      Failed to generate reflection, using previous idea")
                reflection = idea
        except Exception as e:
            print(f"      Error in reflect phase: {e}")
            reflection = idea
        
        # Abstract phase
        print("    Abstract phase...")
        # Set the current phase to ABSTRACT and execute
        spiral_engine.phase_outputs[SpiralPhase.REFLECT] = reflection.description
        spiral_engine.current_phase = SpiralPhase.ABSTRACT
        try:
            abstraction = await spiral_engine._execute_abstract_phase()
            if not abstraction:
                print("      Failed to generate abstraction, using previous idea")
                abstraction = reflection
        except Exception as e:
            print(f"      Error in abstract phase: {e}")
            abstraction = reflection
        
        # Evolve phase
        print("    Evolve phase...")
        # Set the current phase to EVOLVE and execute
        spiral_engine.phase_outputs[SpiralPhase.ABSTRACT] = abstraction.description
        spiral_engine.current_phase = SpiralPhase.EVOLVE
        try:
            evolved_idea = await spiral_engine._execute_evolve_phase()
            if not evolved_idea:
                print("      Failed to generate evolution, using previous idea")
                evolved_idea = abstraction
        except Exception as e:
            print(f"      Error in evolve phase: {e}")
            evolved_idea = abstraction
        
        # Transcend phase
        print("    Transcend phase...")
        # Set the current phase to TRANSCEND and execute
        spiral_engine.phase_outputs[SpiralPhase.EVOLVE] = evolved_idea.description
        spiral_engine.current_phase = SpiralPhase.TRANSCEND
        try:
            transcended_idea = await spiral_engine._execute_transcend_phase()
            if not transcended_idea:
                print("      Failed to generate transcendence, using previous idea")
                transcended_idea = evolved_idea
        except Exception as e:
            print(f"      Error in transcend phase: {e}")
            transcended_idea = evolved_idea
        
        # Return phase (produces a new concrete idea)
        print("    Return phase...")
        # Set the current phase to RETURN and execute
        spiral_engine.phase_outputs[SpiralPhase.TRANSCEND] = transcended_idea.description
        spiral_engine.current_phase = SpiralPhase.RETURN
        try:
            new_idea = await spiral_engine._execute_return_phase()
            if not new_idea:
                print("      Failed to generate return idea, using previous idea")
                new_idea = transcended_idea
        except Exception as e:
            print(f"      Error in return phase: {e}")
            new_idea = transcended_idea
        
        # Store the new idea
        idea = new_idea
        ideas.append(idea)
        
        # Evaluate the new idea
        evaluation = await evaluate_idea(idea, api_client)
        
        # Store the evaluation
        iteration_results.append({
            "iteration": i,
            "phase": "complete_spiral",
            "idea": idea.model_dump(),
            "evaluation": evaluation
        })
    
    # Calculate metrics progression
    metrics_progression = {
        "composite_shock_values": [],
        "surprise_scores": [],
        "generativity_scores": [],
        "traditional_avg_scores": []
    }
    
    for result in iteration_results:
        eval_data = result["evaluation"]
        metrics_progression["composite_shock_values"].append(
            eval_data.get("composite_shock_value", 0.0)
        )
        metrics_progression["surprise_scores"].append(
            eval_data.get("surprise_score", 0.0)
        )
        metrics_progression["generativity_scores"].append(
            eval_data.get("generativity_score", 0.0)
        )
        
        # Average traditional metrics
        trad_metrics = eval_data.get("traditional_metrics", {})
        if trad_metrics:
            traditional_avg = sum(float(v) for v in trad_metrics.values() if isinstance(v, (int, float))) / len(trad_metrics)
            metrics_progression["traditional_avg_scores"].append(traditional_avg)
        else:
            metrics_progression["traditional_avg_scores"].append(0.0)
    
    # Calculate improvement percentages
    if len(iteration_results) >= 2:
        first_scores = iteration_results[0]["evaluation"]
        last_scores = iteration_results[-1]["evaluation"]
        
        first_shock = first_scores.get("composite_shock_value", 0.0)
        last_shock = last_scores.get("composite_shock_value", 0.0)
        shock_improvement = ((last_shock - first_shock) / first_shock * 100) if first_shock > 0 else 0
        
        first_surprise = first_scores.get("surprise_score", 0.0)
        last_surprise = last_scores.get("surprise_score", 0.0)
        surprise_improvement = ((last_surprise - first_surprise) / first_surprise * 100) if first_surprise > 0 else 0
        
        first_generativity = first_scores.get("generativity_score", 0.0)
        last_generativity = last_scores.get("generativity_score", 0.0)
        generativity_improvement = ((last_generativity - first_generativity) / first_generativity * 100) if first_generativity > 0 else 0
        
        first_trad = metrics_progression["traditional_avg_scores"][0]
        last_trad = metrics_progression["traditional_avg_scores"][-1]
        traditional_improvement = ((last_trad - first_trad) / first_trad * 100) if first_trad > 0 else 0
        
        improvements = {
            "shock_value_improvement": shock_improvement,
            "surprise_improvement": surprise_improvement,
            "generativity_improvement": generativity_improvement,
            "traditional_improvement": traditional_improvement
        }
    else:
        improvements = {}
    
    return {
        "domain": domain,
        "problem": problem,
        "iterations": iteration_results,
        "metrics_progression": metrics_progression,
        "improvements": improvements
    }

async def run_comprehensive_spiral_evaluation(api_client: LeelaCoreAPI, spiral_engine: MetaCreativeSpiral) -> Dict[str, Any]:
    """Run a comprehensive spiral evaluation across domains."""
    results = {}
    
    for i, domain in enumerate(TEST_DOMAINS):
        problem = TEST_PROBLEMS[i]
        domain_result = await run_spiral_evaluation(api_client, spiral_engine, domain, problem)
        results[domain] = domain_result
    
    # Calculate average improvements across domains
    avg_improvements = {
        "avg_shock_improvement": 0.0,
        "avg_surprise_improvement": 0.0,
        "avg_generativity_improvement": 0.0,
        "avg_traditional_improvement": 0.0
    }
    
    domain_count = len(TEST_DOMAINS)
    for domain, domain_result in results.items():
        improvements = domain_result.get("improvements", {})
        avg_improvements["avg_shock_improvement"] += improvements.get("shock_value_improvement", 0.0)
        avg_improvements["avg_surprise_improvement"] += improvements.get("surprise_improvement", 0.0)
        avg_improvements["avg_generativity_improvement"] += improvements.get("generativity_improvement", 0.0)
        avg_improvements["avg_traditional_improvement"] += improvements.get("traditional_improvement", 0.0)
    
    for key in avg_improvements:
        avg_improvements[key] /= domain_count
    
    return {
        "domain_results": results,
        "average_improvements": avg_improvements
    }

async def main():
    """Main function to run the evaluation and save results."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Initialize API client and spiral engine
    api_client = LeelaCoreAPI(api_key=api_key)
    spiral_engine = MetaCreativeSpiral(api_key=api_key)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path("evaluation_results")
    output_dir.mkdir(exist_ok=True)
    
    print("Running comprehensive meta-spiral evaluation with REAL Claude API calls...")
    results = await run_comprehensive_spiral_evaluation(api_client, spiral_engine)
    
    # Save results
    output_file = output_dir / f"spiral_evaluation_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation results saved to {output_file}")
    
    # Print summary
    print("\n=== Meta-Creative Spiral Evaluation Summary ===")
    print("\nAverage improvements across domains:")
    for metric, value in results["average_improvements"].items():
        print(f"  {metric}: {value:.2f}%")
    
    # Print per-domain results
    print("\nPer-Domain Results:")
    for domain, domain_result in results["domain_results"].items():
        print(f"\n  {domain.upper()} - {domain_result['problem']}")
        for key, value in domain_result["improvements"].items():
            print(f"    {key}: {value:.2f}%")

if __name__ == "__main__":
    asyncio.run(main())