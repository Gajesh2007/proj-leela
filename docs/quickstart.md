# Quick Start Guide

This guide will help you quickly get started with Project Leela.

## Basic Usage

After [installation](installation.md), you can use Leela in several ways:

### Command Line Interface

Generate an idea using the Impossibility Enforcer:

```bash
poetry run leela idea --domain physics --problem "How might we create a fundamentally new approach to energy generation?" --framework impossibility_enforcer
```

Generate ideas using the Cognitive Dissonance Amplifier:

```bash
poetry run leela idea --domain computer_science --problem "How might we overcome the fundamental limits of computation?" --framework cognitive_dissonance_amplifier
```

Generate ideas through dialectic:

```bash
poetry run leela dialectic --domain economics --problem "How might we reimagine economic value?" --perspectives "Radical Agent: Question all assumptions" --perspectives "Conservative Agent: Consider traditional constraints" --perspectives "Future Agent: Imagine 1000 years ahead"
```

Start the API server:

```bash
poetry run leela server
```

### Python API

```python
import asyncio
from leela.api.core_api import LeelaCoreAPI

async def generate_idea():
    # Create API client
    api_client = LeelaCoreAPI()
    
    # Generate idea
    response = await api_client.generate_creative_idea(
        domain="physics",
        problem_statement="How might we create a fundamentally new approach to energy generation?",
        impossibility_constraints=["perpetual_motion", "time_reversal"],
        shock_threshold=0.7,
        thinking_budget=32000,
        creative_framework="impossibility_enforcer"
    )
    
    # Print idea
    print(f"Generated idea: {response.idea}")
    print(f"Shock value: {response.shock_metrics.composite_shock_value:.2f}")

# Run the async function
asyncio.run(generate_idea())
```

### RESTful API

Start the server:

```bash
poetry run leela server
```

Send a request:

```bash
curl -X POST http://localhost:8000/api/v1/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "physics",
    "problem_statement": "How might we create a fundamentally new approach to energy generation?",
    "impossibility_constraints": ["perpetual_motion", "time_reversal"],
    "shock_threshold": 0.7,
    "thinking_budget": 32000,
    "creative_framework": "impossibility_enforcer"
  }'
```

## Example Output

```json
{
  "id": "3a7c9b4e-8f5d-4c2e-b8a1-7d3f5e2c9a6b",
  "idea": "A Temporal Energy Recycling System that harvests energy from the future to power devices in the present, creating a closed temporal loop where energy is borrowed from its future state, used in the present, and then returned to the past. This system violates conventional thermodynamics by exploiting time-symmetry violations at the quantum scale, effectively creating a perpetual motion machine not by generating energy from nothing but by borrowing it across time.",
  "framework": "impossibility_enforcer",
  "shock_metrics": {
    "novelty_score": 0.75,
    "contradiction_score": 0.68,
    "impossibility_score": 0.82,
    "utility_potential": 0.55,
    "expert_rejection_probability": 0.88,
    "composite_shock_value": 0.74
  }
}
```

## Next Steps

- Read the [API Reference](api.md) for detailed documentation
- Explore [example code](examples.md) for more usage patterns
- Learn about the [creative frameworks](frameworks/index.md) to understand how to get the best results