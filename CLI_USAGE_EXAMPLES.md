# Project Leela CLI Usage Examples

This document provides examples of how to use Project Leela's CLI commands for generating creative ideas through various frameworks.

## Setup

Make sure you have all dependencies installed:

```bash
pip install -r requirements.txt
```

## Basic Idea Generation

Generate a creative idea using the impossibility enforcer:

```bash
python -m leela idea \
  --domain "architecture" \
  --problem "How might we design buildings that adapt to climate change?" \
  --framework "impossibility_enforcer"
```

## Alternative Creative Metaphors

### 1. Territory-Based Idea Generation

Generate an idea using the conceptual territories system:

```bash
python -m leela territory \
  --domain "education" \
  --problem "How might we redesign classrooms for more collaborative learning?" \
  --concept "Classroom" \
  --definition "A space where students gather to learn from teachers through structured lessons and activities" \
  --transformation VOLCANIC_ERUPTION
```

Available transformation processes:
- `TECTONIC_SHIFT`: Massive fundamental movement of conceptual foundations
- `VOLCANIC_ERUPTION`: Sudden, forceful emergence of ideas from deep below
- `GLACIAL_RETREAT`: Withdrawal of long-standing structures, revealing previously covered terrain
- `DESERTIFICATION`: Drying and hardening of previously flexible areas
- `FLOODING`: Overflow and saturation with new elements
- `ECOLOGICAL_SUCCESSION`: Gradual, systematic replacement of elements

### 2. Erosion-Based Idea Generation

Generate an idea using the erosion engine:

```bash
python -m leela erosion \
  --domain "healthcare" \
  --problem "How might we improve patient experience in hospitals?" \
  --concept "Hospital" \
  --definition "A healthcare institution providing patient treatment with specialized staff and equipment" \
  --erosion-stages 3
```

### 3. Mycelial Network Idea Generation

Generate an idea using the mycelial network model:

```bash
python -m leela mycelial \
  --domain "transportation" \
  --problem "How might we create more sustainable urban mobility systems?" \
  --concept "Public transportation is a system of transport for passengers by group travel systems available for use by the general public" \
  --concept "Personal vehicles are privately owned transportation devices used for individual or small group travel" \
  --extension-rounds 3
```

## Multi-Agent Dialectic System

### Basic Dialectic Generation

Generate an idea through dialectic synthesis of multiple perspectives:

```bash
python -m leela dialectic \
  --domain "finance" \
  --problem "How might we make financial services more accessible to underserved communities?" \
  --perspectives "progressive" "conservative" "technological" "historical"
```

### Advanced Dialectic with Strategy Selection

Generate an idea using a specific dialectic synthesis strategy:

```bash
python -m leela advanced-dialectic \
  --domain "agriculture" \
  --problem "How might we design farming systems that are more resilient to climate change?" \
  --perspectives "scientific" "indigenous" "futuristic" \
  --strategy TENSION_MAINTENANCE
```

Available synthesis strategies:
- `INTEGRATION`: Seeks to integrate contradictory perspectives
- `TENSION_MAINTENANCE`: Deliberately maintains creative tensions
- `META_PERSPECTIVE`: Creates a perspective about perspectives
- `QUANTUM_SUPERPOSITION`: Holds contradictions in superposition
- `IMPOSSIBILITY_FOCUS`: Focuses on impossible aspects of contradictions

### Multi-Strategy Synthesis

Generate an idea using multiple synthesis strategies integrated into a meta-synthesis:

```bash
python -m leela multi-strategy \
  --domain "energy" \
  --problem "How might we accelerate the transition to renewable energy sources?"
```

## Output Options

All commands support saving the output to a JSON file:

```bash
python -m leela territory \
  --domain "urban planning" \
  --problem "How might we design cities that are more resilient to natural disasters?" \
  --concept "City" \
  --definition "A large human settlement with complex systems for housing, transportation, utilities, governance, and economics" \
  --transformation FLOODING \
  --output "flooding_city_idea.json"
```

## API Server

Start the API server:

```bash
python run_server.py
```

The server will be available at http://localhost:8000 by default.

## Frontend

If you've installed the frontend dependencies:

```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000 by default.