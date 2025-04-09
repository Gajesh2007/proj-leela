# Command Line Interface

Project Leela provides a powerful command-line interface for generating creative ideas, managing dialectic processes, running the API server, and managing prompts.

## Global Options

All commands support these options:

- `--help, -h`: Display help information

## Commands

### Initialize

Create a template `.env` file:

```bash
leela init
```

### Generate Idea

Generate a creative idea:

```bash
leela idea --domain DOMAIN --problem "PROBLEM_STATEMENT" [OPTIONS]
```

#### Options

- `--domain, -d`: Domain to generate idea for (required)
- `--problem, -p`: Problem statement (required)
- `--framework, -f`: Creative framework to use (default: impossibility_enforcer)
  - `impossibility_enforcer`: Forces inclusion of "impossible" elements
  - `cognitive_dissonance_amplifier`: Forces contradictory concepts to coexist
- `--impossibility, -i`: Impossibility constraints (can be specified multiple times)
- `--contradiction, -c`: Contradiction requirements (can be specified multiple times)
- `--shock-threshold, -s`: Minimum shock threshold (0.0-1.0, default: 0.6)
- `--thinking-budget, -t`: Thinking budget in tokens (default: 16000)
- `--output, -o`: Output file path (JSON)

#### Examples

```bash
# Generate an idea in physics with specific impossibility constraints
leela idea --domain physics --problem "How might we create a fundamentally new approach to energy generation?" --impossibility perpetual_motion --impossibility time_reversal

# Generate an idea using the cognitive dissonance amplifier
leela idea --domain biology --problem "How might we create a new framework for understanding cellular communication?" --framework cognitive_dissonance_amplifier --contradiction "competition|cooperation" --output idea.json
```

### Generate Dialectic Idea

Generate an idea through dialectic thinking from multiple perspectives:

```bash
leela dialectic --domain DOMAIN --problem "PROBLEM_STATEMENT" --perspectives "PERSPECTIVE1" --perspectives "PERSPECTIVE2" [OPTIONS]
```

#### Options

- `--domain, -d`: Domain to generate idea for (required)
- `--problem, -p`: Problem statement (required)
- `--perspectives, -P`: Perspectives for dialectic (can be specified multiple times, at least 2 required)
- `--thinking-budget, -t`: Thinking budget in tokens (default: 16000)
- `--output, -o`: Output file path (JSON)

#### Examples

```bash
# Generate a dialectic idea with three perspectives
leela dialectic --domain economics --problem "How might we reimagine value in a post-scarcity economy?" --perspectives "Radical Agent: Question all assumptions about economic value" --perspectives "Conservative Agent: Consider how traditional economic constraints might still apply" --perspectives "Future Agent: Imagine economic systems 1000 years in the future" --output dialectic.json
```

### Run Server

Run the API server:

```bash
leela server [OPTIONS]
```

#### Options

- `--port, -p`: Port to run on (default: 8000)

#### Examples

```bash
# Run the server on the default port (8000)
leela server

# Run the server on a custom port
leela server --port 9000
```

### Prompt Management

Manage prompts and their implementations:

```bash
leela prompt [SUBCOMMAND] [OPTIONS]
```

#### Subcommands

##### List Prompts

List all available prompts:

```bash
leela prompt list [OPTIONS]
```

Options:
- `--with-versions`: Include prompt versions
- `--with-metadata`: Include prompt metadata
- `--format`: Output format (text, json, yaml)

Examples:
```bash
# List all prompts
leela prompt list

# List all prompts with their versions and metadata in JSON format
leela prompt list --with-versions --with-metadata --format json
```

##### Validate Implementations

Validate prompt implementations and report issues:

```bash
leela prompt validate [OPTIONS]
```

Options:
- `--with-stats`: Include implementation statistics
- `--format`: Output format (text, json, yaml)

Examples:
```bash
# Validate all implementations and show statistics
leela prompt validate --with-stats
```

##### Version Prompt

Create a new version of a prompt:

```bash
leela prompt version PROMPT_NAME [OPTIONS]
```

Options:
- `--author`: Author of the change (required)
- `--change-type`: Type of change (major, minor, patch)
- `--message`: Commit message for the version

Examples:
```bash
# Create a new minor version of a prompt
leela prompt version impossibility_enforcer --author "Jane Doe" --change-type minor --message "Improved impossibility elements detection"
```

##### Compare Versions

Compare two versions of a prompt:

```bash
leela prompt compare PROMPT_NAME VERSION1 VERSION2
```

Examples:
```bash
# Compare versions 1.0.0 and 1.1.0 of a prompt
leela prompt compare impossibility_enforcer 1.0.0 1.1.0
```

##### Rollback to Version

Rollback to a specific version of a prompt:

```bash
leela prompt rollback PROMPT_NAME VERSION
```

Examples:
```bash
# Rollback to version 1.0.0
leela prompt rollback impossibility_enforcer 1.0.0
```

##### Version All Prompts

Version all unversioned prompts:

```bash
leela prompt version-all [OPTIONS]
```

Options:
- `--author`: Author of the changes (required)
- `--message`: Commit message for the versions

Examples:
```bash
# Version all unversioned prompts
leela prompt version-all --author "Jane Doe" --message "Initial versioning"
```

## Environment Variables

The CLI respects these environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `CLAUDE_MODEL`: Claude model to use (default: claude-3-7-sonnet-20250219)
- `EXTENDED_THINKING`: Enable extended thinking mode (true/false)
- `THINKING_BUDGET`: Token budget for thinking steps
- `PORT`: Port to run the server on
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`: Database configuration
- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`: Neo4j configuration

You can set these in your `.env` file or directly in your environment.