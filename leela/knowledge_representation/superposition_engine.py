"""
Superposition Engine - Maintains concepts in probabilistic superposition states.
"""
from typing import Dict, List, Any, Optional, Tuple
import uuid
import random
import math
from pydantic import UUID4
from ..knowledge_representation.models import Concept, ConceptState, EntanglementLink


class SuperpositionEngine:
    """
    Maintains concepts in probabilistic superposition states until measurements collapse them
    to specific interpretations.
    """
    
    def __init__(self):
        """Initialize the Superposition Engine."""
        self.concepts = {}  # Dict[UUID4, Concept]
    
    def add_concept(self, concept: Concept) -> UUID4:
        """
        Add a concept to the superposition engine.
        
        Args:
            concept: The concept to add
            
        Returns:
            UUID4: The ID of the added concept
        """
        # Generate ID if not present
        if not concept.id:
            concept.id = uuid.uuid4()
        
        # Add to concepts dictionary
        self.concepts[concept.id] = concept
        
        return concept.id
    
    def get_concept(self, concept_id: UUID4) -> Optional[Concept]:
        """
        Get a concept by ID.
        
        Args:
            concept_id: The ID of the concept to get
            
        Returns:
            Optional[Concept]: The concept, if found
        """
        return self.concepts.get(concept_id)
    
    def create_superposition(self, concept_id: UUID4, 
                          states: List[Tuple[str, float, List[str]]]) -> bool:
        """
        Create a superposition for a concept with multiple states.
        
        Args:
            concept_id: The ID of the concept to create a superposition for
            states: List of tuples (state_definition, probability, context_triggers)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the concept
        concept = self.get_concept(concept_id)
        if not concept:
            return False
        
        # Create concept states
        concept_states = []
        total_probability = 0.0
        
        for state_def, prob, triggers in states:
            concept_states.append(ConceptState(
                state_definition=state_def,
                probability=prob,
                context_triggers=triggers
            ))
            total_probability += prob
        
        # Normalize probabilities if not summing to 1.0
        if abs(total_probability - 1.0) > 0.001:  # Allow small floating point errors
            for state in concept_states:
                state.probability /= total_probability
        
        # Set the superposition states
        concept.superposition_states = concept_states
        
        return True
    
    def measure_concept(self, concept_id: UUID4, 
                      context: Optional[str] = None) -> Optional[str]:
        """
        Measure a concept, collapsing its superposition to a single state.
        
        Args:
            concept_id: The ID of the concept to measure
            context: Optional context to influence the measurement
            
        Returns:
            Optional[str]: The collapsed state definition, or None if not found
        """
        # Get the concept
        concept = self.get_concept(concept_id)
        if not concept or not concept.superposition_states:
            return None
        
        # Check if context triggers a specific state
        if context:
            for state in concept.superposition_states:
                for trigger in state.context_triggers:
                    if trigger.lower() in context.lower():
                        return state.state_definition
        
        # No context match, do probabilistic collapse
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for state in concept.superposition_states:
            cumulative_prob += state.probability
            if rand_val <= cumulative_prob:
                return state.state_definition
        
        # Fallback to the last state if probabilities don't sum to 1.0 due to floating point errors
        if concept.superposition_states:
            return concept.superposition_states[-1].state_definition
        
        return None
    
    def entangle_concepts(self, source_id: UUID4, target_id: UUID4, 
                        entanglement_type: str, correlation_strength: float,
                        evolution_rules: str) -> bool:
        """
        Entangle two concepts so changes to one affect the other.
        
        Args:
            source_id: ID of the source concept
            target_id: ID of the target concept
            entanglement_type: Nature of the quantum connection
            correlation_strength: Strength of correlation (0.0-1.0)
            evolution_rules: Rules for how changes propagate
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get the concepts
        source = self.get_concept(source_id)
        target = self.get_concept(target_id)
        
        if not source or not target:
            return False
        
        # Create entanglement links
        source_entanglement = EntanglementLink(
            target_concept_id=target_id,
            entanglement_type=entanglement_type,
            correlation_strength=correlation_strength,
            evolution_rules=evolution_rules
        )
        
        target_entanglement = EntanglementLink(
            target_concept_id=source_id,
            entanglement_type=entanglement_type,
            correlation_strength=correlation_strength,
            evolution_rules=evolution_rules
        )
        
        # Add entanglements
        source.entanglements.append(source_entanglement)
        target.entanglements.append(target_entanglement)
        
        return True
    
    def propagate_entanglement(self, concept_id: UUID4, 
                             measured_state: str) -> Dict[UUID4, str]:
        """
        Propagate the effects of measuring one concept to entangled concepts.
        
        Args:
            concept_id: ID of the measured concept
            measured_state: The state the concept collapsed to
            
        Returns:
            Dict[UUID4, str]: Map of concept IDs to their new collapsed states
        """
        # Get the concept
        concept = self.get_concept(concept_id)
        if not concept or not concept.entanglements:
            return {}
        
        # Track propagated effects
        propagated_states = {}
        
        # Process each entanglement
        for entanglement in concept.entanglements:
            target_id = entanglement.target_concept_id
            target = self.get_concept(target_id)
            
            if not target or not target.superposition_states:
                continue
            
            # Apply entanglement based on correlation strength
            if random.random() <= entanglement.correlation_strength:
                # In a real implementation, we'd use the evolution rules to determine
                # how to correlate the states. This is a simplified version.
                
                # Simple approach: Based on the entanglement correlation, either
                # pick a related state or do a standard probabilistic measurement
                if entanglement.entanglement_type == "correlated":
                    # For correlated entanglement, try to find a state that matches
                    # the measured state in some way
                    matched_state = self._find_correlated_state(
                        target.superposition_states, measured_state
                    )
                    propagated_states[target_id] = matched_state
                elif entanglement.entanglement_type == "anti-correlated":
                    # For anti-correlated entanglement, try to find a state that
                    # is opposite to the measured state
                    matched_state = self._find_anti_correlated_state(
                        target.superposition_states, measured_state
                    )
                    propagated_states[target_id] = matched_state
                else:
                    # Default: standard measurement
                    propagated_states[target_id] = self.measure_concept(target_id)
        
        return propagated_states
    
    def _find_correlated_state(self, states: List[ConceptState], 
                             reference_state: str) -> str:
        """
        Find a state that is correlated with the reference state.
        
        Args:
            states: List of possible states
            reference_state: The reference state to correlate with
            
        Returns:
            str: The correlated state definition
        """
        # In a real implementation, we'd use NLP or semantic similarity
        # to find truly correlated states. This is a simplified version.
        
        # Look for states with similar words
        reference_words = set(reference_state.lower().split())
        max_similarity = 0
        most_similar_state = None
        
        for state in states:
            state_words = set(state.state_definition.lower().split())
            # Simple Jaccard similarity
            intersection = len(reference_words.intersection(state_words))
            union = len(reference_words.union(state_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_state = state
        
        # If we found a similar state, return it
        if most_similar_state and max_similarity > 0:
            return most_similar_state.state_definition
        
        # Otherwise, do a standard probabilistic measurement
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for state in states:
            cumulative_prob += state.probability
            if rand_val <= cumulative_prob:
                return state.state_definition
        
        # Fallback
        return states[-1].state_definition if states else "Unknown state"
    
    def _find_anti_correlated_state(self, states: List[ConceptState], 
                                 reference_state: str) -> str:
        """
        Find a state that is anti-correlated (opposite) to the reference state.
        
        Args:
            states: List of possible states
            reference_state: The reference state to anti-correlate with
            
        Returns:
            str: The anti-correlated state definition
        """
        # In a real implementation, we'd use NLP or semantic analysis
        # to find truly opposite states. This is a simplified version.
        
        # Look for states with differing words
        reference_words = set(reference_state.lower().split())
        min_similarity = float('inf')
        least_similar_state = None
        
        for state in states:
            state_words = set(state.state_definition.lower().split())
            # Simple Jaccard similarity (we want minimum similarity)
            intersection = len(reference_words.intersection(state_words))
            union = len(reference_words.union(state_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity < min_similarity:
                min_similarity = similarity
                least_similar_state = state
        
        # If we found a dissimilar state, return it
        if least_similar_state:
            return least_similar_state.state_definition
        
        # Otherwise, do a standard probabilistic measurement
        rand_val = random.random()
        cumulative_prob = 0.0
        
        for state in states:
            cumulative_prob += state.probability
            if rand_val <= cumulative_prob:
                return state.state_definition
        
        # Fallback
        return states[-1].state_definition if states else "Unknown state"