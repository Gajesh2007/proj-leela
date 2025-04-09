"""
Knowledge Representation package for Project Leela.

This package provides models and engines for representing concepts and ideas.
"""
from .models import Concept, ConceptState, CreativeIdea, EntanglementLink, ShockProfile
from .superposition_engine import SuperpositionEngine
from .mycelial_network import MycelialNetwork, generate_mycelial_idea
from .conceptual_territories import (
    ConceptualTerritoriesSystem, 
    ConceptualTerritory, 
    TerritoryFeature, 
    NeighboringTerritory,
    TransformationProcess,
    generate_territory_idea
)

__all__ = [
    'Concept',
    'ConceptState',
    'CreativeIdea',
    'EntanglementLink',
    'ShockProfile',
    'SuperpositionEngine',
    'MycelialNetwork',
    'generate_mycelial_idea',
    'ConceptualTerritoriesSystem',
    'ConceptualTerritory',
    'TerritoryFeature',
    'NeighboringTerritory',
    'TransformationProcess',
    'generate_territory_idea'
]