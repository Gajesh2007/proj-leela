"""
Command-line interface for Project Leela.
"""
import argparse
import sys
import os
import asyncio
import json
from typing import List, Optional
from pathlib import Path
import uuid

from .api.core_api import LeelaCoreAPI
from .config import get_config, get_env_file_template


def create_env_file():
    """Create a .env file template."""
    template = get_env_file_template()
    env_path = Path.cwd() / ".env"
    
    if env_path.exists():
        overwrite = input(".env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != "y":
            print("Aborted.")
            return
    
    with open(env_path, "w") as f:
        f.write(template)
    
    print(f".env template created at {env_path}")


async def generate_idea(args):
    """Generate a creative idea."""
    # Create API client
    api_client = LeelaCoreAPI()
    
    # Get impossibility constraints
    impossibility_constraints = []
    if args.impossibility:
        impossibility_constraints = args.impossibility
    
    # Get contradiction requirements
    contradiction_requirements = []
    if args.contradiction:
        contradiction_requirements = args.contradiction
    
    # Generate idea
    response = await api_client.generate_creative_idea(
        domain=args.domain,
        problem_statement=args.problem,
        impossibility_constraints=impossibility_constraints,
        contradiction_requirements=contradiction_requirements,
        shock_threshold=args.shock_threshold,
        thinking_budget=args.thinking_budget,
        creative_framework=args.framework
    )
    
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
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        # Convert to dict for JSON serialization
        result_dict = {
            "id": str(response.id),
            "framework": response.framework,
            "idea": response.idea,
            "shock_metrics": {
                "novelty_score": response.shock_metrics.novelty_score,
                "contradiction_score": response.shock_metrics.contradiction_score,
                "impossibility_score": response.shock_metrics.impossibility_score,
                "utility_potential": response.shock_metrics.utility_potential,
                "expert_rejection_probability": response.shock_metrics.expert_rejection_probability,
                "composite_shock_value": response.shock_metrics.composite_shock_value
            }
        }
        with open(output_path, "w") as f:
            json.dump(result_dict, f, indent=2)
        print(f"\nIdea saved to {output_path}")


async def generate_dialectic(args):
    """Generate a dialectic idea."""
    # Create API client
    api_client = LeelaCoreAPI()
    
    # Generate dialectic idea
    response = await api_client.generate_dialectic_idea(
        domain=args.domain,
        problem_statement=args.problem,
        perspectives=args.perspectives,
        thinking_budget=args.thinking_budget
    )
    
    # Print synthesized idea
    print("\n=== SYNTHESIZED IDEA ===")
    print(f"ID: {response.id}")
    print("\nSynthesized Idea:")
    print(response.synthesized_idea)
    print("\nShock Metrics:")
    print(f"- Novelty: {response.shock_metrics.novelty_score:.2f}")
    print(f"- Contradiction: {response.shock_metrics.contradiction_score:.2f}")
    print(f"- Impossibility: {response.shock_metrics.impossibility_score:.2f}")
    print(f"- Utility Potential: {response.shock_metrics.utility_potential:.2f}")
    print(f"- Expert Rejection Probability: {response.shock_metrics.expert_rejection_probability:.2f}")
    print(f"- Composite Shock Value: {response.shock_metrics.composite_shock_value:.2f}")
    
    # Print perspective ideas
    print("\n=== PERSPECTIVE IDEAS ===")
    for i, (perspective, idea) in enumerate(zip(args.perspectives, response.perspective_ideas)):
        print(f"\nPerspective {i+1}: {perspective}")
        print(idea)
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        # Convert to dict for JSON serialization
        result_dict = {
            "id": str(response.id),
            "synthesized_idea": response.synthesized_idea,
            "shock_metrics": {
                "novelty_score": response.shock_metrics.novelty_score,
                "contradiction_score": response.shock_metrics.contradiction_score,
                "impossibility_score": response.shock_metrics.impossibility_score,
                "utility_potential": response.shock_metrics.utility_potential,
                "expert_rejection_probability": response.shock_metrics.expert_rejection_probability,
                "composite_shock_value": response.shock_metrics.composite_shock_value
            },
            "perspectives": args.perspectives,
            "perspective_ideas": response.perspective_ideas
        }
        with open(output_path, "w") as f:
            json.dump(result_dict, f, indent=2)
        print(f"\nIdea saved to {output_path}")


def run_server(args):
    """Run the FastAPI server."""
    from .api.fastapi_app import run_app
    run_app()


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Project Leela - Meta-Creative Intelligence System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize Project Leela")
    
    # Idea generation command
    idea_parser = subparsers.add_parser("idea", help="Generate a creative idea")
    idea_parser.add_argument("--domain", "-d", required=True, help="Domain to generate idea for")
    idea_parser.add_argument("--problem", "-p", required=True, help="Problem statement")
    idea_parser.add_argument("--framework", "-f", default="impossibility_enforcer", 
                           choices=["impossibility_enforcer", "cognitive_dissonance_amplifier"],
                           help="Creative framework to use")
    idea_parser.add_argument("--impossibility", "-i", action="append", 
                          help="Impossibility constraints (can be specified multiple times)")
    idea_parser.add_argument("--contradiction", "-c", action="append", 
                          help="Contradiction requirements (can be specified multiple times)")
    idea_parser.add_argument("--shock-threshold", "-s", type=float, default=0.6, 
                          help="Minimum shock threshold (0.0-1.0)")
    idea_parser.add_argument("--thinking-budget", "-t", type=int, default=16000, 
                          help="Thinking budget in tokens")
    idea_parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    # Dialectic command
    dialectic_parser = subparsers.add_parser("dialectic", help="Generate a dialectic idea")
    dialectic_parser.add_argument("--domain", "-d", required=True, help="Domain to generate idea for")
    dialectic_parser.add_argument("--problem", "-p", required=True, help="Problem statement")
    dialectic_parser.add_argument("--perspectives", "-P", action="append", required=True,
                               help="Perspectives for dialectic (can be specified multiple times)")
    dialectic_parser.add_argument("--thinking-budget", "-t", type=int, default=16000, 
                               help="Thinking budget in tokens")
    dialectic_parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run on")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    if args.command == "init":
        create_env_file()
    elif args.command == "idea":
        asyncio.run(generate_idea(args))
    elif args.command == "dialectic":
        asyncio.run(generate_dialectic(args))
    elif args.command == "server":
        if args.port:
            os.environ["PORT"] = str(args.port)
        run_server(args)


if __name__ == "__main__":
    main()