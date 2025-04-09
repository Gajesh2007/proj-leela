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
import importlib
from enum import Enum

from .api.core_api import LeelaCoreAPI
from .config import get_config, get_env_file_template
from .core_processing.explorer import PerspectiveType
from .dialectic_synthesis.dialectic_system import SynthesisStrategy
from .knowledge_representation.conceptual_territories import TransformationProcess


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


async def generate_advanced_dialectic(args):
    """Generate an advanced dialectic idea using sophisticated synthesis strategies."""
    # Convert perspective strings to enum values
    perspective_types = []
    valid_perspectives = [p.value for p in PerspectiveType]
    
    for p in args.perspectives:
        if p.lower() in valid_perspectives:
            perspective_types.append(PerspectiveType(p.lower()))
        else:
            print(f"Warning: Ignoring invalid perspective '{p}'. Valid perspectives: {valid_perspectives}")
    
    if not perspective_types:
        print("Error: No valid perspectives specified.")
        return
    
    # Convert strategy string to enum value
    synthesis_strategy = SynthesisStrategy[args.strategy.upper()]
    
    # Import here to avoid circular imports
    from .dialectic_synthesis.dialectic_system import DialecticSystem
    
    # Create Dialectic System
    dialectic_system = DialecticSystem()
    
    print(f"Generating advanced dialectic idea for problem: {args.problem} in domain: {args.domain}")
    print(f"Using perspectives: {[p.value for p in perspective_types]}")
    print(f"Using synthesis strategy: {synthesis_strategy.name}")
    
    # Generate advanced dialectic idea
    result = await dialectic_system.generate_direct_synthesis(
        problem_statement=args.problem,
        domain=args.domain,
        perspectives=perspective_types,
        synthesis_strategy=synthesis_strategy,
        thinking_budget=args.thinking_budget
    )
    
    # Print result summary
    print("\n=== ADVANCED DIALECTIC SYNTHESIS ===")
    print(f"Strategy: {synthesis_strategy.name}")
    print("\nSynthesized Idea:")
    print(result['synthesized_idea'])
    
    # Print shock metrics if available
    if 'idea' in result and hasattr(result['idea'], 'shock_metrics'):
        shock = result['idea'].shock_metrics
        print("\nShock Metrics:")
        print(f"- Novelty: {shock.novelty_score:.2f}")
        print(f"- Contradiction: {shock.contradiction_score:.2f}")
        print(f"- Impossibility: {shock.impossibility_score:.2f}")
        print(f"- Utility Potential: {shock.utility_potential:.2f}")
        print(f"- Expert Rejection Probability: {shock.expert_rejection_probability:.2f}")
        print(f"- Composite Shock Value: {shock.composite_shock_value:.2f}")
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        
        # Convert result to serializable format
        serializable = {
            "synthesized_idea": result['synthesized_idea'],
            "domain": args.domain,
            "problem": args.problem,
            "perspectives": [p.value for p in perspective_types],
            "synthesis_strategy": synthesis_strategy.name
        }
        
        # Add CreativeIdea to serialization if available
        if 'idea' in result:
            serializable["idea"] = result['idea'].model_dump()
        
        with open(output_path, "w") as f:
            json.dump(serializable, f, indent=2)
        print(f"\nIdea saved to {output_path}")


async def generate_multi_strategy(args):
    """Generate a creative idea using multiple synthesis strategies integrated into a meta-synthesis."""
    # Import here to avoid circular imports
    from .dialectic_synthesis.dialectic_system import DialecticSystem
    
    # Create Dialectic System
    dialectic_system = DialecticSystem()
    
    print(f"Generating multi-strategy dialectic idea for problem: {args.problem} in domain: {args.domain}")
    
    # Generate multi-strategy synthesis
    result = await dialectic_system.generate_multi_strategy_synthesis(
        problem_statement=args.problem,
        domain=args.domain,
        thinking_budget=args.thinking_budget
    )
    
    # Print result summary
    print("\n=== MULTI-STRATEGY META-SYNTHESIS ===")
    print("\nMeta-Synthesis:")
    print(result['meta_synthesis'])
    
    # Print individual strategy results
    print("\n=== INDIVIDUAL STRATEGY SYNTHESES ===")
    for strategy, synthesis in result['strategy_syntheses'].items():
        print(f"\nStrategy: {strategy}")
        print(synthesis[:200] + "..." if len(synthesis) > 200 else synthesis)
    
    # Print shock metrics if available
    if 'idea' in result and hasattr(result['idea'], 'shock_metrics'):
        shock = result['idea'].shock_metrics
        print("\nShock Metrics:")
        print(f"- Novelty: {shock.novelty_score:.2f}")
        print(f"- Contradiction: {shock.contradiction_score:.2f}")
        print(f"- Impossibility: {shock.impossibility_score:.2f}")
        print(f"- Utility Potential: {shock.utility_potential:.2f}")
        print(f"- Expert Rejection Probability: {shock.expert_rejection_probability:.2f}")
        print(f"- Composite Shock Value: {shock.composite_shock_value:.2f}")
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        
        # Convert result to serializable format
        serializable = {
            "meta_synthesis": result['meta_synthesis'],
            "domain": args.domain,
            "problem": args.problem,
            "strategy_syntheses": result['strategy_syntheses']
        }
        
        # Add CreativeIdea to serialization if available
        if 'idea' in result:
            serializable["idea"] = result['idea'].model_dump()
        
        with open(output_path, "w") as f:
            json.dump(serializable, f, indent=2)
        print(f"\nIdea saved to {output_path}")


async def generate_territory_idea_cmd(args):
    """Generate a creative idea using the conceptual territories system."""
    # Import here to avoid circular imports
    from .knowledge_representation.conceptual_territories import (
        ConceptualTerritoriesSystem, 
        TransformationProcess,
        generate_territory_idea
    )
    from .knowledge_representation.models import Concept
    
    print(f"Generating conceptual territory idea for problem: {args.problem} in domain: {args.domain}")
    
    # Create a concept from input
    concept = Concept(
        id=uuid.uuid4(),
        name=args.concept,
        domain=args.domain,
        definition=args.definition
    )
    
    # Determine transformation process if specified
    transformation_process = None
    if args.transformation:
        transformation_process = TransformationProcess[args.transformation.upper()]
        print(f"Using transformation process: {transformation_process.name}")
    
    # Generate territory-based idea
    idea = await generate_territory_idea(
        problem_statement=args.problem,
        domain=args.domain,
        concept=concept,
        transformation_process=transformation_process
    )
    
    # Print idea
    print("\n=== TERRITORY-BASED IDEA ===")
    print(f"ID: {idea.id}")
    print(f"Framework: {idea.generative_framework}")
    print("\nIdea:")
    print(idea.description)
    
    # Print shock metrics
    if hasattr(idea, 'shock_metrics') and idea.shock_metrics:
        shock = idea.shock_metrics
        print("\nShock Metrics:")
        print(f"- Novelty: {shock.novelty_score:.2f}")
        print(f"- Contradiction: {shock.contradiction_score:.2f}")
        print(f"- Impossibility: {shock.impossibility_score:.2f}")
        print(f"- Utility Potential: {shock.utility_potential:.2f}")
        print(f"- Expert Rejection Probability: {shock.expert_rejection_probability:.2f}")
        print(f"- Composite Shock Value: {shock.composite_shock_value:.2f}")
    
    # Save to file if specified
    if args.output:
        output_path = Path(args.output)
        
        # Convert to serializable format
        serializable = {
            "id": str(idea.id),
            "framework": idea.generative_framework,
            "idea": idea.description,
            "domain": idea.domain,
            "problem": args.problem,
            "concept": {
                "name": concept.name,
                "definition": concept.definition
            }
        }
        
        # Add shock metrics if available
        if hasattr(idea, 'shock_metrics') and idea.shock_metrics:
            serializable["shock_metrics"] = {
                "novelty_score": idea.shock_metrics.novelty_score,
                "contradiction_score": idea.shock_metrics.contradiction_score,
                "impossibility_score": idea.shock_metrics.impossibility_score,
                "utility_potential": idea.shock_metrics.utility_potential,
                "expert_rejection_probability": idea.shock_metrics.expert_rejection_probability,
                "composite_shock_value": idea.shock_metrics.composite_shock_value
            }
        
        with open(output_path, "w") as f:
            json.dump(serializable, f, indent=2)
        print(f"\nIdea saved to {output_path}")


def run_server(args):
    """Run the FastAPI server."""
    from .api.fastapi_app import run_app
    run_app()


def run_prompt_management_cli(args):
    """Run the prompt management CLI."""
    try:
        from .prompt_management.cli import main as prompt_cli_main
        
        # Create a new argv based on the prompt subcommand arguments
        argv = [sys.argv[0]]
        if hasattr(args, 'prompt_args') and args.prompt_args:
            argv.extend(args.prompt_args)
        
        # Run the prompt management CLI
        sys.argv = argv
        prompt_cli_main()
    except ImportError as e:
        print(f"Error: {e}")
        print("Please make sure the prompt management module is installed.")
        sys.exit(1)


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
    
    # Advanced dialectic command
    adv_dialectic_parser = subparsers.add_parser("advanced-dialectic", 
                                              help="Generate an advanced dialectic idea using sophisticated synthesis strategies")
    adv_dialectic_parser.add_argument("--domain", "-d", required=True, help="Domain to generate idea for")
    adv_dialectic_parser.add_argument("--problem", "-p", required=True, help="Problem statement")
    adv_dialectic_parser.add_argument("--perspectives", "-P", action="append", required=True,
                                   help="Perspectives for dialectic (can be specified multiple times)")
    adv_dialectic_parser.add_argument("--strategy", "-s", default="TENSION_MAINTENANCE", 
                                   choices=[s.name for s in SynthesisStrategy],
                                   help="Synthesis strategy to use")
    adv_dialectic_parser.add_argument("--thinking-budget", "-t", type=int, default=16000, 
                                   help="Thinking budget in tokens")
    adv_dialectic_parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    # Multi-strategy command
    multi_parser = subparsers.add_parser("multi-strategy", 
                                      help="Generate a creative idea using multiple synthesis strategies")
    multi_parser.add_argument("--domain", "-d", required=True, help="Domain to generate idea for")
    multi_parser.add_argument("--problem", "-p", required=True, help="Problem statement")
    multi_parser.add_argument("--thinking-budget", "-t", type=int, default=16000, 
                           help="Thinking budget in tokens")
    multi_parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    # Territory command
    territory_parser = subparsers.add_parser("territory", 
                                         help="Generate a creative idea using the conceptual territories system")
    territory_parser.add_argument("--domain", "-d", required=True, help="Domain to generate idea for")
    territory_parser.add_argument("--problem", "-p", required=True, help="Problem statement")
    territory_parser.add_argument("--concept", "-c", required=True, help="Concept name to map as a territory")
    territory_parser.add_argument("--definition", "-D", required=True, help="Definition of the concept")
    territory_parser.add_argument("--transformation", "-T", 
                               choices=[t.name for t in TransformationProcess],
                               help="Transformation process to apply (optional)")
    territory_parser.add_argument("--output", "-o", help="Output file path (JSON)")
    
    # Server command
    server_parser = subparsers.add_parser("server", help="Run the API server")
    server_parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run on")
    
    # Prompt management command
    prompt_parser = subparsers.add_parser("prompt", help="Manage prompts and their implementations")
    prompt_parser.add_argument('prompt_args', nargs='*', help="Arguments for the prompt management CLI")
    
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
    elif args.command == "advanced-dialectic":
        asyncio.run(generate_advanced_dialectic(args))
    elif args.command == "multi-strategy":
        asyncio.run(generate_multi_strategy(args))
    elif args.command == "territory":
        asyncio.run(generate_territory_idea_cmd(args))
    elif args.command == "server":
        if args.port:
            os.environ["PORT"] = str(args.port)
        run_server(args)
    elif args.command == "prompt":
        run_prompt_management_cli(args)


if __name__ == "__main__":
    main()