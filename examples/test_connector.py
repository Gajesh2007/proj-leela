"""
Test script for the enhanced ConnectorModule.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from leela.core_processing.connector import ConnectorModule
from leela.utils.logging import LeelaLogger

# Set up logging
logger = LeelaLogger.get_logger("examples.test_connector")


async def main():
    """Main function for testing the ConnectorModule."""
    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY") or input("Enter Anthropic API Key (or set ANTHROPIC_API_KEY env var): ")
    
    # Create ConnectorModule
    connector = ConnectorModule(api_key=api_key)
    
    # Define test problem and domains
    problem_statement = "How might we create new forms of sustainable transportation?"
    domains = ["physics", "biology"]
    
    # Log the test parameters
    logger.info(f"Testing ConnectorModule with problem: {problem_statement}")
    logger.info(f"Domains: {domains}")
    print(f"Testing ConnectorModule with problem: {problem_statement}")
    print(f"Domains: {domains}")
    
    # Run the connector
    print("\nRunning connector with quantum entanglement...")
    result = await connector.connect(problem_statement, domains)
    
    # Print domains used
    print(f"\nDomains connected: {result['domains'][0]} and {result['domains'][1]}")
    
    # Print concepts
    print("\n--- Concepts ---")
    for domain, concept in result['concepts'].items():
        print(f"{domain}: {concept}")
    
    # Print bridges
    print("\n--- Bridge Mechanisms ---")
    for bridge in result['bridges']:
        print(f"- {bridge}")
    
    # Print quantum blend
    print("\n--- Quantum Blend ---")
    print(result['quantum_blend'].get('blend', 'No blend found'))
    
    # Print entanglement properties
    print("\n--- Entanglement Properties ---")
    print(f"Basis: {result['entanglement_properties']['basis']}")
    print(f"Correlation: {result['entanglement_properties']['correlation']}")
    print(f"Propagation Rules: {result['entanglement_properties']['propagation']}")
    
    # Print characteristics if available
    characteristics = result['entanglement_properties'].get('characteristics', {})
    if characteristics:
        print("\n--- Entanglement Characteristics ---")
        for key, value in characteristics.items():
            print(f"{key}: {value}")
    
    # Print the generated idea
    print("\n--- Generated Idea ---")
    print(result['idea'].description)
    
    # Print shock metrics
    print("\n--- Shock Metrics ---")
    metrics = result['idea'].shock_metrics
    print(f"Novelty: {metrics.novelty_score:.2f}")
    print(f"Contradiction: {metrics.contradiction_score:.2f}")
    print(f"Impossibility: {metrics.impossibility_score:.2f}")
    print(f"Utility Potential: {metrics.utility_potential:.2f}")
    print(f"Expert Rejection: {metrics.expert_rejection_probability:.2f}")
    print(f"Composite Shock: {metrics.composite_shock_value:.2f}")
    
    # Print framework used
    print(f"\nFramework: {result['idea'].generative_framework}")
    
    # Print any impossibility elements
    if result['idea'].impossibility_elements:
        print("\n--- Impossibility Elements ---")
        for element in result['idea'].impossibility_elements:
            print(f"- {element}")


if __name__ == "__main__":
    asyncio.run(main())