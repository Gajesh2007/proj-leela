# Alternative Creative Metaphors in Project Leela

Project Leela implements three alternative metaphors for creative idea generation, each offering a unique perspective on the creative process. This document provides an overview of these metaphors and how they are implemented.

## 1. Mycelial Network Model

The Mycelial Network Model is inspired by fungal networks and their edge-focused decomposition-construction processes.

### Key Concepts:

- **Node Types:** Nutrient (input data), Hypha (processing), Rhizomorph (transport), Fruiting Body (output)
- **Edge Types:** Decomposition, Absorption, Transport, Synthesis, Extension
- **Edge-Focused Growth:** Creativity evolves primarily at network edges through extension
- **Network Seeding:** Starting with a concept that's decomposed into constituent parts
- **Extension Rounds:** Growing the network through multiple rounds of edge extension
- **Synthesis:** Generating ideas from mature fruiting body nodes

### Implementation:

- `MycelialNetwork` class manages a network of nodes with typed connections
- `NodeType` and `EdgeType` enums define the types of nodes and connections
- Network growth occurs through `decompose_content()`, `extend_network()`, and `synthesize_idea()`
- Ideas emerge at fruiting body nodes after network maturation
- Network visualization possible through NetworkX integration

## 2. Erosion Perspective Engine

The Erosion Engine models creativity as a process of persistent application of simple forces over time, inspired by geological erosion.

### Key Concepts:

- **Erosion Forces:** Water (fluid, persistent), Wind (subtle, widespread), Ice (expansion in constraints), Heat (breaking down through intensity), Chemical (transformation through interaction), Biological (living processes)
- **Erosion Patterns:** Canyon (deep cut), Delta (build-up), Cave (hidden spaces), Meandering (changing path), Weathering (surface degradation)
- **Erosion Timeframes:** Instant, Short-Term, Medium-Term, Long-Term, Geological
- **Concept Erosion:** Transforming concepts through multiple erosion stages
- **Idea Generation:** Creating ideas from eroded concepts

### Implementation:

- `ErosionEngine` applies erosion forces, patterns, and timeframes to concepts
- `ErodedConcept` tracks the transformation of concepts through erosion stages
- `_apply_erosion_force()` method transforms concepts based on specified parameters
- Ideas are generated from fully eroded concepts using `generate_idea_from_erosion()`
- Multiple erosion stages can be applied to achieve deeper transformation

## 3. Conceptual Territories System

The Conceptual Territories System maps concepts as geographical territories with boundaries, features, and relationships that can be transformed.

### Key Concepts:

- **Territory Mapping:** Representing concepts as territories with boundaries, topography, landmarks
- **Neighboring Territories:** Modeling relationships with adjacent conceptual spaces
- **Boundary Dissolution:** Revealing hidden connections by dissolving artificial boundaries
- **Territory Transformation:** Applying transformative processes to reshape territories
- **Transformation Processes:** Tectonic Shift, Volcanic Eruption, Glacial Retreat, Desertification, Flooding, Ecological Succession

### Implementation:

- `ConceptualTerritoriesSystem` manages territory mapping, dissolution, and transformation
- `ConceptualTerritory` represents a concept as a territory with features and neighbors
- `TerritoryFeature` models features within territories (mountains, valleys, etc.)
- `NeighboringTerritory` represents relationships with other territories
- `TransformationProcess` enum defines the types of transformation processes
- Three-stage idea generation: mapping, dissolution, transformation

## Usage Examples

### Mycelial Network:

```python
from leela.knowledge_representation.mycelial_network import generate_mycelial_idea
from leela.knowledge_representation.models import Concept

concepts = [
    Concept(name="Urban Transportation", domain="urban planning", definition="..."),
    Concept(name="Social Connection", domain="urban planning", definition="...")
]

idea = await generate_mycelial_idea(
    problem_statement="How can we design transportation systems that enhance social connection?",
    domain="urban planning",
    concepts=concepts,
    extension_rounds=3
)
```

### Erosion Engine:

```python
from leela.core_processing.erosion_engine import generate_eroded_idea
from leela.knowledge_representation.models import Concept

concept = Concept(
    name="Library",
    domain="education",
    definition="A collection of materials, books or media that are accessible for use..."
)

idea = await generate_eroded_idea(
    problem_statement="How might we reimagine libraries for the digital age?",
    domain="education",
    concept=concept,
    erosion_stages=3
)
```

### Conceptual Territories:

```python
from leela.knowledge_representation.conceptual_territories import generate_territory_idea, TransformationProcess
from leela.knowledge_representation.models import Concept

concept = Concept(
    name="Classroom",
    domain="education",
    definition="A space where students gather to learn from teachers through structured lessons..."
)

idea = await generate_territory_idea(
    problem_statement="How might we redesign classrooms for more collaborative learning?",
    domain="education",
    concept=concept,
    transformation_process=TransformationProcess.VOLCANIC_ERUPTION
)
```

## Integration with API

All three creative metaphors are integrated into the Leela API with dedicated endpoints:

- `/api/v1/mycelial` - Generate ideas using the Mycelial Network model
- `/api/v1/erosion` - Generate ideas using the Erosion Engine
- `/api/v1/territory` - Generate ideas using the Conceptual Territories System

Each endpoint accepts domain-specific parameters and returns a standardized `CreativeIdeaResponse` with shock metrics.