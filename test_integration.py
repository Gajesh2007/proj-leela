#!/usr/bin/env python3
"""
Simple integration test script to verify Leela's functionality.
"""
import asyncio
import uuid
from leela.knowledge_representation.models import Concept
from leela.knowledge_representation.conceptual_territories import (
    TransformationProcess,
    generate_territory_idea
)
from leela.core_processing.erosion_engine import generate_eroded_idea

async def test_territory_idea():
    """Test generating a territory-based idea"""
    print("\n=== Testing Territory Idea Generation ===")
    
    concept = Concept(
        id=uuid.uuid4(),
        name="Garden",
        domain="landscaping",
        definition=(
            "A garden is a planned space, usually outdoors, set aside for the display, "
            "cultivation, or enjoyment of plants and other forms of nature. The garden can "
            "incorporate both natural and human-made materials."
        )
    )
    
    print(f"Concept: {concept.name}")
    print(f"Generating idea...")
    
    try:
        # Use a very small thinking budget for quick testing
        idea = await generate_territory_idea(
            problem_statement="How can we create gardens that adapt to climate change?",
            domain="landscaping",
            concept=concept,
            transformation_process=TransformationProcess.GLACIAL_RETREAT
        )
        
        print(f"Success! Generated idea with ID: {idea.id}")
        print(f"Idea excerpt: {idea.description[:100]}...")
        return True
    except Exception as e:
        print(f"Error generating territory idea: {e}")
        return False

async def test_erosion_idea():
    """Test generating an erosion-based idea"""
    print("\n=== Testing Erosion Idea Generation ===")
    
    concept = Concept(
        id=uuid.uuid4(),
        name="Library",
        domain="education",
        definition=(
            "A library is a collection of materials, books or media that are accessible "
            "for use and not just for display purposes. A library provides physical or "
            "digital access to material and may be a physical location or a virtual space."
        )
    )
    
    print(f"Concept: {concept.name}")
    print(f"Generating idea...")
    
    try:
        # Use a very small thinking budget for quick testing
        idea = await generate_eroded_idea(
            problem_statement="How might we reimagine libraries for the digital age?",
            domain="education",
            concept=concept,
            erosion_stages=2  # Use fewer erosion stages for faster testing
        )
        
        print(f"Success! Generated idea with ID: {idea.id}")
        print(f"Idea excerpt: {idea.description[:100]}...")
        return True
    except Exception as e:
        print(f"Error generating erosion idea: {e}")
        return False

async def main():
    """Run the integration tests"""
    print("Running integration tests...")
    
    # Test territory idea generation
    territory_success = await test_territory_idea()
    
    # Test erosion idea generation
    erosion_success = await test_erosion_idea()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Territory idea generation: {'✅ PASSED' if territory_success else '❌ FAILED'}")
    print(f"Erosion idea generation: {'✅ PASSED' if erosion_success else '❌ FAILED'}")

if __name__ == "__main__":
    asyncio.run(main())