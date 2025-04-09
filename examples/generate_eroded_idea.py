"""
Example script for generating a creative idea using the Erosion Engine.

This example demonstrates how to:
1. Create a concept to erode
2. Apply erosion forces, patterns, and timeframes
3. Generate a creative idea from the eroded concept
"""
import asyncio
import uuid
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parents[1]
sys.path.append(str(project_root))

from leela.knowledge_representation.models import Concept
from leela.core_processing.erosion_engine import (
    ErosionEngine,
    ErosionForce,
    ErosionPattern,
    ErosionTimeframe,
    generate_eroded_idea
)


async def main():
    """Run the erosion idea generation example."""
    print("=== Erosion Engine Example ===")
    
    # Define inputs
    problem_statement = "How can we create sustainable transportation systems for dense urban areas?"
    domain = "urban planning"
    
    # Define a concept to erode
    concept = Concept(
        id=uuid.uuid4(),
        name="Public Transportation",
        domain=domain,
        definition=(
            "Public transportation is a system of transport for passengers by group travel systems "
            "available for use by the general public, typically managed on a schedule, operated on "
            "established routes, and charging a posted fee for each trip. Examples include city buses, "
            "trolleybuses, trams, passenger trains, rapid transit (metro/subway/underground), ferries, "
            "and water taxis. Most public transport systems run along fixed routes with set embarkation/ "
            "disembarkation points to a prearranged timetable, with the most frequent services running "
            "to a headway (e.g.: 'every 15 minutes')."
        )
    )
    
    print(f"Concept: {concept.name}")
    print(f"Domain: {domain}")
    print(f"Problem: {problem_statement}")
    print("\nEroding concept and generating idea...")
    
    # Create erosion engine directly
    engine = ErosionEngine()
    
    # Register the concept for erosion
    concept_id = engine.register_concept(concept)
    
    # Apply specific erosion forces to demonstrate the process
    await engine.apply_erosion(
        concept_id=concept_id,
        force=ErosionForce.WATER,
        pattern=ErosionPattern.MEANDERING,
        timeframe=ErosionTimeframe.MEDIUM_TERM
    )
    
    await engine.apply_erosion(
        concept_id=concept_id,
        force=ErosionForce.WIND,
        pattern=ErosionPattern.WEATHERING,
        timeframe=ErosionTimeframe.LONG_TERM
    )
    
    await engine.apply_erosion(
        concept_id=concept_id,
        force=ErosionForce.BIOLOGICAL,
        pattern=ErosionPattern.DELTA,
        timeframe=ErosionTimeframe.GEOLOGICAL
    )
    
    # Get the eroded concept
    eroded_concept = engine.get_eroded_concept(concept_id)
    
    # Generate an idea from the eroded concept
    idea = await engine.generate_idea_from_erosion(
        eroded_concept=eroded_concept,
        problem_statement=problem_statement
    )
    
    # Print the results
    print("\n=== Erosion Process ===")
    for i, stage in enumerate(eroded_concept.get_erosion_stages()):
        print(f"Stage {i+1}: {stage['force']} force with {stage['pattern']} pattern over {stage['timeframe']} timeframe")
        print(f"Description: {stage['description']}")
        print()
    
    print("=== Generated Idea ===")
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
    
    # Alternative simplified approach using the helper function
    print("\n=== Alternative Approach Using Helper Function ===")
    simplified_idea = await generate_eroded_idea(
        problem_statement=problem_statement,
        domain=domain,
        concept=concept,
        erosion_stages=3
    )
    
    print(f"Simplified ID: {simplified_idea.id}")
    print(f"Simplified Idea Summary: {simplified_idea.description[:100]}...")


if __name__ == "__main__":
    asyncio.run(main())