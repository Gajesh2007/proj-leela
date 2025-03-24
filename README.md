# Project Leela

A meta-creative intelligence system designed to generate genuinely shocking, novel outputs that transcend conventional thinking.

## Overview

Project Leela leverages Claude 3.7 Sonnet's Extended Thinking capabilities to implement revolutionary creative frameworks that force the emergence of ideas beyond what experts would consider possible. It uses a quantum-inspired architecture that enables conceptual superposition, entanglement, and emergence to generate ideas that would be inaccessible to traditional AI systems or human thinkers alone.

Leela employs a structured tag-based approach to prompt engineering and response processing, ensuring consistent extraction of creative insights and ideas across different generative frameworks.

## Core Features

- **Quantum-Inspired Knowledge Representation**: Maintains concepts in superposition states until measured
- **Shock Generation Frameworks**: Impossibility Enforcer, Cognitive Dissonance Amplifier
- **Core Processing Modules**: Disruptor, Connector, Explorer, Evaluator
- **Meta-Creative Spiral**: Create→Reflect→Abstract→Evolve→Transcend→Return cycle
- **Multi-Agent Dialectic System**: Different perspective types (Radical, Conservative, Alien, etc.)
- **Temporal Perspective Shifting**: Viewing problems through different historical eras
- **Multi-Dimensional Evaluation**: Traditional and inverse metrics with measurement-induced collapse
- **Data Persistence**: Store and retrieve generated ideas, thinking steps, and creative states
- **Tag-Based Prompt Architecture**: Structured XML-like tags for consistent extraction of insights and ideas
- **Extended Thinking Integration**: Full support for Claude 3.7's Extended Thinking capabilities
- **Dynamic Prompt Management**: Template-based prompts with dynamic rendering

## Architecture

Project Leela is built on a modular architecture with clear separation of concerns:

1. **Directed Thinking Layer**: Leverages Claude 3.7's Extended Thinking mode with specialized prompting frameworks
2. **Knowledge Representation Layer**: Maintains quantum-inspired concept representations with superposition and entanglement
3. **Core Processing Modules**: Specialized modules for different aspects of creative thinking
4. **Meta-Engine**: Coordinates all modules and manages the creative quantum state
5. **Meta-Creative Spiral**: Implements a self-evolving creative methodology
6. **Data Persistence Layer**: Stores and retrieves creative artifacts and states
7. **Application Layer**: API and interfaces for interacting with the system

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Redis (optional for caching)
- Anthropic API key with access to Claude 3.7 Sonnet models

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Gajesh2007/proj-leela.git
   cd project-leela
   ```

2. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

3. Create a `.env` file with your configuration:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   CLAUDE_MODEL=claude-3-7-sonnet-20250219
   EXTENDED_THINKING=true
   THINKING_BUDGET=16000
   
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_NAME=leela
   ```

4. Set up the database:
   ```bash
   # Start the database using Docker Compose
   docker-compose up -d postgres
   
   # Initialize the database
   python scripts/create_db.py
   ```

### Usage

#### Running the API Server

```bash
python -m leela.api.fastapi_app
# or
poetry run uvicorn leela.api.fastapi_app:app --reload
```

#### Running the Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000 to access the Leela interface.

#### Running with Docker

```bash
docker-compose up
```

#### Using the CLI

```bash
poetry run leela generate --domain physics --problem "How might we create a fundamentally new approach to energy generation?"
```

#### Running the Examples

```bash
python examples/generate_idea.py
python examples/generate_dialectic_idea.py
```

## Development

### Prompt and Extraction Architecture

Leela uses a structured tag-based approach for prompt engineering and response extraction:

#### Tag Types

- **Context Tags**: `<domain>`, `<problem_statement>`, etc. - Used to structure input context
- **Analysis Tags**: `<contradiction_analysis>`, `<dialectic_analysis>`, `<ideation_process>`, `<synthesis_process>` - Used to extract thinking processes
- **Output Tags**: `<idea>`, `<final_idea>`, `<revolutionary_idea>`, `<synthesis>` - Used to extract generated ideas
  
All extraction methods support graceful fallback to traditional marker-based extraction for backward compatibility.

### Project Structure

#### Backend

```
leela/
├── __init__.py
├── __main__.py
├── api/                  # API interfaces
├── application/          # Application-specific implementations
├── core_processing/      # Core processing modules (Disruptor, Connector, Explorer, Evaluator)
├── data_persistence/     # Database and storage
├── directed_thinking/    # Claude API and Extended Thinking integration
├── evaluation/           # Evaluation metrics 
├── knowledge_representation/ # Concept models and superposition
├── meta_creative/        # Meta-creative spiral
├── meta_engine/          # Orchestration engine
├── output_filtering/     # Output filtering and verification
├── prompt_management/    # Prompt templates and rendering
├── shock_generation/     # Frameworks for generating shock (Impossibility Enforcer, Cognitive Dissonance)
└── utils/                # Utility functions
```

#### Frontend

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── dashboard/   # Dashboard-specific components
│   │   └── layout/      # Layout components (Navbar, Sidebar)
│   ├── pages/           # Page components (Next.js routes)
│   │   ├── _app.tsx     # Application wrapper
│   │   ├── index.tsx    # Dashboard page
│   │   ├── generate.tsx # Idea generation page
│   │   ├── explorer.tsx # Idea explorer page
│   │   ├── quantum-canvas.tsx # Quantum visualization
│   │   └── ...
│   ├── services/        # API and state management
│   │   ├── api.ts       # API client
│   │   └── LeelaContext.tsx # Global state context
│   └── styles/          # Global styles
└── tailwind.config.js   # Tailwind CSS configuration
```

### Testing

```bash
pytest tests/
```

## Configuration

Configuration is handled through environment variables and the `.env` file. See `leela/config.py` for all available options.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by the creative potential of Claude 3.7 Sonnet's Extended Thinking capabilities
- Built on quantum-inspired creative methodologies to transcend conventional thinking