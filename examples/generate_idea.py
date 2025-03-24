"""
Example script for generating a creative idea using Project Leela.
"""
import asyncio
import sys
import os
import json
import uuid
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from leela.api.core_api import LeelaCoreAPI
from leela.data_persistence.repository import Repository
from leela.meta_engine.engine import MetaEngine, CreativeWorkflow
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("examples.generate_idea")


async def main():
    """Main function."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Create Meta-Engine and initialize DB
    meta_engine = MetaEngine(api_key=api_key)
    await meta_engine.initialize()
    
    # Create API client for easier API-like access
    api_client = LeelaCoreAPI(api_key=api_key)
    
    # Define domains and problem statements
    domains = [
        "physics",
        "biology", 
        "computer_science",
        "economics",
        "mathematics"
    ]
    
    problem_statements = {
        "physics": "How might we create a fundamentally new approach to energy generation?",
        "biology": "How might we create a new framework for understanding cellular communication?",
        "computer_science": "How might we overcome the fundamental limits of computation?",
        "economics": "How might we reimagine the concept of value in a post-scarcity world?",
        "mathematics": "How might we develop a mathematical framework that transcends the limitations of set theory?"
    }
    
    # Select a domain
    domain = domains[0]  # Change this to try different domains
    problem_statement = problem_statements[domain]
    
    logger.info(f"Generating idea for domain: {domain}")
    logger.info(f"Problem statement: {problem_statement}")
    print(f"Generating idea for domain: {domain}")
    print(f"Problem statement: {problem_statement}")
    
    # Define the workflow
    workflow = CreativeWorkflow.DISRUPTOR
    
    # Generate idea using the meta-engine directly for more control
    print("\nGenerating idea using Meta-Engine...")
    result = await meta_engine.generate_idea(
        problem_statement=problem_statement, 
        domain=domain,
        workflow=workflow
    )
    
    # For comparison, also use the API
    print("\nGenerating idea using API...")
    api_response = await api_client.generate_creative_idea(
        domain=domain,
        problem_statement=problem_statement,
        shock_threshold=0.7,
        thinking_budget=32000,
        creative_framework="impossibility_enforcer"
    )
    
    # Use the result from meta-engine
    response = api_response
    
    # Print idea
    print("\n=== GENERATED IDEA ===")
    print(f"ID: {response.id}")
    print(f"Framework: {response.framework}")
    print("\nIdea:")
    print(response.idea)
    print("\nShock Metrics:")
    print(f"- Novelty: {response.shock_metrics.novelty_score:.2f}")
    print(f"- Contradiction: {response.shock_metrics.contradiction_score:.2f}")
    print(f"- Impossibility: {response.shock_metrics.impossibility_score:.2f}")
    print(f"- Utility Potential: {response.shock_metrics.utility_potential:.2f}")
    print(f"- Expert Rejection Probability: {response.shock_metrics.expert_rejection_probability:.2f}")
    print(f"- Composite Shock Value: {response.shock_metrics.composite_shock_value:.2f}")
    
    # Print thinking steps (truncated for brevity)
    print("\n=== THINKING PROCESS (TRUNCATED) ===")
    for step in response.thinking_steps:
        thinking_preview = step.reasoning_process[:500] + "..." if len(step.reasoning_process) > 500 else step.reasoning_process
        print(thinking_preview)
        print("\nInsights:")
        for insight in step.insights_generated:
            print(f"- {insight}")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    data_dir = Path("data/ideas")
    data_dir.mkdir(exist_ok=True, parents=True)
    output_path = data_dir / f"{domain}_{timestamp}.json"
    
    # Save API response
    api_result_dict = {
        "id": str(response.id),
        "framework": response.framework,
        "idea": response.idea,
        "domain": domain,
        "problem_statement": problem_statement,
        "shock_metrics": {
            "novelty_score": response.shock_metrics.novelty_score,
            "contradiction_score": response.shock_metrics.contradiction_score,
            "impossibility_score": response.shock_metrics.impossibility_score,
            "utility_potential": response.shock_metrics.utility_potential,
            "expert_rejection_probability": response.shock_metrics.expert_rejection_probability,
            "composite_shock_value": response.shock_metrics.composite_shock_value
        },
        "timestamp": timestamp,
        "source": "api"
    }
    
    # Save meta-engine result
    if result and "idea" in result and result["idea"]:
        meta_result_dict = {
            "id": str(result["idea"].id),
            "framework": result["workflow"],
            "idea": result["idea"].description,
            "domain": domain,
            "problem_statement": problem_statement,
            "shock_metrics": {
                "novelty_score": result["idea"].shock_metrics.novelty_score,
                "contradiction_score": result["idea"].shock_metrics.contradiction_score,
                "impossibility_score": result["idea"].shock_metrics.impossibility_score,
                "utility_potential": result["idea"].shock_metrics.utility_potential,
                "expert_rejection_probability": result["idea"].shock_metrics.expert_rejection_probability,
                "composite_shock_value": result["idea"].shock_metrics.composite_shock_value
            },
            "timestamp": timestamp,
            "source": "meta_engine"
        }
        
        meta_output_path = data_dir / f"{domain}_meta_{timestamp}.json"
        with open(meta_output_path, "w") as f:
            json.dump(meta_result_dict, f, indent=2)
        print(f"\nMeta-Engine idea saved to {meta_output_path}")
    
    # Save API result
    with open(output_path, "w") as f:
        json.dump(api_result_dict, f, indent=2)
    print(f"\nAPI idea saved to {output_path}")
    
    # Log completion
    logger.info(f"Ideas generated and saved successfully at {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())