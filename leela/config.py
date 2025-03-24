"""
Configuration module for Project Leela.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
PROMPTS_DIR = BASE_DIR / "prompts"

# Create directories if they don't exist
for dir_path in [DATA_DIR, MODELS_DIR, PROMPTS_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# API Configuration
API_CONFIG = {
    "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY", ""),
    "model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620"),
    "extended_thinking": os.getenv("EXTENDED_THINKING", "true").lower() == "true",
}

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "database": os.getenv("DB_NAME", "leela"),
}

# Redis Configuration
REDIS_CONFIG = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": int(os.getenv("REDIS_PORT", "6379")),
    "db": int(os.getenv("REDIS_DB", "0")),
    "password": os.getenv("REDIS_PASSWORD", None),
}

# System Configuration
SYSTEM_CONFIG = {
    # Default shock threshold (0.0-1.0)
    "minimum_shock_threshold": float(os.getenv("MIN_SHOCK_THRESHOLD", "0.6")),
    
    # Maximum token budget for creativity operations
    "max_token_budget": int(os.getenv("MAX_TOKEN_BUDGET", "100000")),
    
    # Development/Production mode
    "environment": os.getenv("ENVIRONMENT", "development"),
    
    # Logging level
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
}

# Creativity Parameters
CREATIVITY_CONFIG = {
    # Weight factors for shock metrics
    "novelty_weight": float(os.getenv("NOVELTY_WEIGHT", "0.25")),
    "contradiction_weight": float(os.getenv("CONTRADICTION_WEIGHT", "0.25")),
    "impossibility_weight": float(os.getenv("IMPOSSIBILITY_WEIGHT", "0.30")),
    "utility_weight": float(os.getenv("UTILITY_WEIGHT", "0.10")),
    "expert_rejection_weight": float(os.getenv("EXPERT_REJECTION_WEIGHT", "0.10")),
    
    # Spiral phase durations (in generations)
    "create_phase_duration": int(os.getenv("CREATE_PHASE_DURATION", "3")),
    "reflect_phase_duration": int(os.getenv("REFLECT_PHASE_DURATION", "2")),
    "abstract_phase_duration": int(os.getenv("ABSTRACT_PHASE_DURATION", "2")),
    "evolve_phase_duration": int(os.getenv("EVOLVE_PHASE_DURATION", "2")),
    "transcend_phase_duration": int(os.getenv("TRANSCEND_PHASE_DURATION", "1")),
    "return_phase_duration": int(os.getenv("RETURN_PHASE_DURATION", "1")),
}

# Domains and their impossibility constraints
DOMAIN_IMPOSSIBILITIES = {
    "physics": [
        "perpetual_motion", 
        "faster_than_light_travel", 
        "time_reversal",
        "observer_independent_reality"
    ],
    "biology": [
        "spontaneous_generation", 
        "non_carbon_based_life",
        "non_dna_inheritance",
        "conscious_single_cells"
    ],
    "computer_science": [
        "zero_energy_computation",
        "perfect_security",
        "algorithm_beyond_turing_completeness",
        "general_purpose_quantum_advantage"
    ],
    "economics": [
        "infinite_growth",
        "perfect_market_efficiency",
        "value_without_scarcity",
        "utility_without_subjective_preference"
    ],
    "mathematics": [
        "non_axiomatic_proof",
        "squaring_the_circle",
        "trisecting_arbitrary_angle_with_compass_and_straightedge",
        "mathematical_theory_of_everything"
    ],
    # Add more domains as needed
}

def get_config() -> Dict[str, Any]:
    """
    Returns the complete configuration dictionary.
    """
    return {
        "api": API_CONFIG,
        "db": DB_CONFIG,
        "redis": REDIS_CONFIG,
        "system": SYSTEM_CONFIG,
        "creativity": CREATIVITY_CONFIG,
        "domain_impossibilities": DOMAIN_IMPOSSIBILITIES,
        "paths": {
            "base_dir": str(BASE_DIR),
            "data_dir": str(DATA_DIR),
            "models_dir": str(MODELS_DIR),
            "prompts_dir": str(PROMPTS_DIR),
        }
    }

def get_env_file_template() -> str:
    """
    Returns a template for the .env file.
    """
    return """# Project Leela Environment Variables

# API Configuration
ANTHROPIC_API_KEY=your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20240620
EXTENDED_THINKING=true

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=leela

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# System Configuration
ENVIRONMENT=development  # development, production
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
MIN_SHOCK_THRESHOLD=0.6
MAX_TOKEN_BUDGET=100000

# Creativity Parameters
NOVELTY_WEIGHT=0.25
CONTRADICTION_WEIGHT=0.25
IMPOSSIBILITY_WEIGHT=0.30
UTILITY_WEIGHT=0.10
EXPERT_REJECTION_WEIGHT=0.10

# Spiral Phase Durations
CREATE_PHASE_DURATION=3
REFLECT_PHASE_DURATION=2
ABSTRACT_PHASE_DURATION=2
EVOLVE_PHASE_DURATION=2
TRANSCEND_PHASE_DURATION=1
RETURN_PHASE_DURATION=1
"""