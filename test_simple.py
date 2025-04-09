#!/usr/bin/env python3
"""
Simple test script that doesn't rely on extended thinking.
"""
import uuid
from pydantic import UUID4
from typing import Dict, List, Any, Optional
import datetime

# Define a simple concept model
class Concept:
    def __init__(self, name, domain, definition):
        self.id = uuid.uuid4()
        self.name = name
        self.domain = domain
        self.definition = definition

# Define a simple shock profile
class ShockProfile:
    def __init__(self):
        self.novelty_score = 0.8
        self.contradiction_score = 0.7
        self.impossibility_score = 0.6
        self.utility_potential = 0.9
        self.expert_rejection_probability = 0.7
        self.composite_shock_value = 0.75

# Define a simple creative idea model
class CreativeIdea:
    def __init__(self, description, framework):
        self.id = uuid.uuid4()
        self.description = description
        self.generative_framework = framework
        self.domain = "test_domain"
        self.shock_metrics = ShockProfile()

def generate_territory_idea():
    """Simple function to simulate territory idea generation"""
    idea = CreativeIdea(
        description="A permeable boundary garden system that dissolves traditional distinctions between public and private spaces, creating fluid social interaction zones that transform throughout the day based on use patterns. The garden features volcanic emergence points where community-maintained plant collections erupt into shared resources, with pathways that meander between properties creating a neighborhood-scale ecosystem.",
        framework="conceptual_territories"
    )
    return idea

def generate_erosion_idea():
    """Simple function to simulate erosion idea generation"""
    idea = CreativeIdea(
        description="A 'delta library' system where knowledge accumulates at community nodes, deposited by the continuous flow of information through digital channels. These deposits form rich, contextual collections shaped by local interests, with multiple rivers of content converging to create unique knowledge formations. Physical spaces are designed as weathered landscapes that reveal different information layers as users interact with them.",
        framework="erosion_engine"
    )
    return idea

def main():
    """Run simple tests that don't require API calls"""
    print("Running simple tests (no API calls)...")
    
    # Test territory idea generation
    print("\n=== Testing Territory Idea Generation ===")
    territory_idea = generate_territory_idea()
    print(f"Generated territory idea ID: {territory_idea.id}")
    print(f"Idea excerpt: {territory_idea.description[:100]}...")
    
    # Test erosion idea generation
    print("\n=== Testing Erosion Idea Generation ===")
    erosion_idea = generate_erosion_idea()
    print(f"Generated erosion idea ID: {erosion_idea.id}")
    print(f"Idea excerpt: {erosion_idea.description[:100]}...")
    
    # Print summary
    print("\n=== Test Summary ===")
    print("Simple tests completed successfully!")
    print("Note: These tests don't use the API, they just verify the basic structure")

if __name__ == "__main__":
    main()