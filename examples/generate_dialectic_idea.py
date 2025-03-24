"""
Example script for generating a dialectic idea using Project Leela.
"""
import asyncio
import sys
import os
import json
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from leela.api.core_api import LeelaCoreAPI


async def main():
    """Main function."""
    # Create API client
    api_client = LeelaCoreAPI()
    
    # Define domain and problem statement
    domain = "computer_science"
    problem_statement = "How might we overcome the fundamental limits of computation?"
    
    # Define perspectives
    perspectives = [
        "Radical Agent: Question all assumptions about computation, including Turing completeness and the Church-Turing thesis. Imagine computation beyond binary logic and deterministic processes.",
        "Conservative Agent: Consider how proven approaches and constraints might be leveraged in novel ways, while respecting fundamental mathematical limits.",
        "Ancient Agent: Apply historical computational paradigms like Babylonian or ancient Chinese mathematics to modern computing.",
        "Future Agent: Imagine computational paradigms that would seem incomprehensible to current computer scientists, as if from 1000 years in the future."
    ]
    
    print(f"Generating dialectic idea for domain: {domain}")
    print(f"Problem statement: {problem_statement}")
    print("Perspectives:")
    for i, perspective in enumerate(perspectives):
        print(f"{i+1}. {perspective}")
    
    # Generate dialectic idea
    response = await api_client.generate_dialectic_idea(
        domain=domain,
        problem_statement=problem_statement,
        perspectives=perspectives,
        thinking_budget=32000
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
    for i, (perspective, idea) in enumerate(zip(perspectives, response.perspective_ideas)):
        print(f"\nPerspective {i+1}: {perspective.split(':')[0]}")
        print(idea)
    
    # Save to file
    output_path = Path(f"dialectic_{domain}.json")
    # Convert to dict for JSON serialization
    result_dict = {
        "id": str(response.id),
        "synthesized_idea": response.synthesized_idea,
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
        "perspectives": [p.split(':')[0] for p in perspectives],
        "perspective_ideas": response.perspective_ideas
    }
    with open(output_path, "w") as f:
        json.dump(result_dict, f, indent=2)
    print(f"\nIdea saved to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())