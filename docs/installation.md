# Installation Guide

This guide will help you install Project Leela and set up your environment.

## Requirements

- Python 3.9 or higher
- [Poetry](https://python-poetry.org/) package manager
- An Anthropic API key for Claude 3.7 Sonnet

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/leela.git
cd leela
```

### 2. Install Dependencies

Using Poetry:

```bash
poetry install
```

Or for development dependencies:

```bash
poetry install --with dev
```

### 3. Set Up Environment Variables

Initialize an environment file:

```bash
poetry run leela init
```

This creates a `.env` file with template values. Edit this file to add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

### 4. Verify Installation

Run a test to verify everything is working:

```bash
poetry run pytest
```

## Using Docker (Optional)

A Dockerfile is provided for containerized deployment:

```bash
# Build the Docker image
docker build -t leela .

# Run the container
docker run -p 8000:8000 --env-file .env leela
```

## Next Steps

Once installed, you can:

- Try the [Quick Start Guide](quickstart.md)
- Explore the [Command Line Interface](cli.md)
- Learn about the [API Reference](api.md)