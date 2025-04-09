"""
Example script for generating a creative idea using the Conceptual Territories System.

This example demonstrates how to:
1. Map a concept as a territory
2. Dissolve boundaries between territories
3. Transform the territory using a specified process
4. Generate a creative idea based on the transformed territory
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
from leela.knowledge_representation.conceptual_territories import (
    ConceptualTerritoriesSystem,
    TransformationProcess,
    generate_territory_idea
)


async def main():
    """Run the territory idea generation example."""
    print("=== Conceptual Territories System Example ===")
    
    # Define inputs
    problem_statement = "How can we design urban environments that enhance social connection?"
    domain = "urban planning"
    
    # Define a concept to map as a territory
    concept = Concept(
        id=uuid.uuid4(),
        name="Neighborhood",
        domain=domain,
        definition=(
            "A neighborhood is a geographic area within a larger city, town, suburb or rural area, "
            "typically with distinguishing characteristics. Neighborhoods are often social communities "
            "with face-to-face interaction among members, and they may represent specific spatial or "
            "historical boundaries, demographics, or economic contexts. Neighborhoods typically have "
            "physical and social components, creating spaces where human activities blend with the "
            "built environment."
        )
    )
    
    print(f"Concept: {concept.name}")
    print(f"Domain: {domain}")
    print(f"Problem: {problem_statement}")
    print("\nGenerating territory-based creative idea...")
    
    # Use a specific transformation process
    transformation_process = TransformationProcess.VOLCANIC_ERUPTION
    print(f"Using transformation process: {transformation_process.name}")
    
    # Generate the idea
    idea = await generate_territory_idea(
        problem_statement=problem_statement,
        domain=domain,
        concept=concept,
        transformation_process=transformation_process
    )
    
    # Print the results
    print("\n=== Generated Idea ===")
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


if __name__ == "__main__":
    asyncio.run(main())