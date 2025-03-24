"""
FastAPI wrapper for Project Leela API.
"""
from typing import Dict, List, Any, Optional
import uuid
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import os

from .core_api import LeelaCoreAPI, CreativeIdeaRequest, CreativeIdeaResponse, DialecticIdeaRequest, DialecticIdeaResponse
from ..config import get_config
from ..data_persistence.repository import Repository
from ..prompt_management.prompt_loader import PromptLoader
from ..meta_engine.engine import MetaEngine
from ..utils.logging import LeelaLogger, api_logger

# Initialize FastAPI app
app = FastAPI(
    title="Project Leela API",
    description="API for Project Leela, a meta-creative intelligence system designed to generate shocking, novel outputs that transcend conventional thinking.",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get config
config = get_config()

# Initialize database repository
repository = Repository()

# Initialize prompt loader
prompt_loader = PromptLoader()

# Initialize meta-engine
meta_engine: Optional[MetaEngine] = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    api_logger.info("Initializing Leela API components...")
    
    # Initialize database
    try:
        api_logger.info("Initializing database...")
        await repository.initialize()
        api_logger.info("Database initialized successfully")
    except Exception as e:
        api_logger.error(f"Error initializing database: {e}")
        # Continue anyway, as we might be running without a database
    
    # Initialize meta-engine
    try:
        api_logger.info("Initializing meta-engine...")
        global meta_engine
        
        # Get API key from config
        api_key = config["api"]["anthropic_api_key"]
        if not api_key:
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            
        if api_key:
            meta_engine = MetaEngine(api_key=api_key)
            await meta_engine.initialize()
            api_logger.info("Meta-engine initialized successfully")
        else:
            api_logger.warning("No API key provided, meta-engine not initialized")
    except Exception as e:
        api_logger.error(f"Error initializing meta-engine: {e}")
    
    api_logger.info("Leela API startup complete")


def get_leela_api() -> LeelaCoreAPI:
    """
    Dependency to get the Leela API client.
    
    Returns:
        LeelaCoreAPI: The Leela API client
    """
    # Get API key from config
    api_key = config["api"]["anthropic_api_key"]
    
    if not api_key:
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
    if not api_key:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")
    
    # Create and return the API client
    return LeelaCoreAPI(api_key)


def get_meta_engine() -> MetaEngine:
    """
    Dependency to get the Meta-Engine.
    
    Returns:
        MetaEngine: The Meta-Engine
    """
    if meta_engine is None:
        raise HTTPException(status_code=500, detail="Meta-Engine not initialized")
    
    return meta_engine


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to Project Leela API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/v1/ideas", response_model=CreativeIdeaResponse)
async def generate_idea(
    request: CreativeIdeaRequest,
    leela_api: LeelaCoreAPI = Depends(get_leela_api)
):
    """
    Generate a creative idea.
    """
    try:
        # Step 1: Generate the idea
        api_logger.info("Generating creative idea...")
        try:
            response = await leela_api.generate_creative_idea(
                domain=request.domain,
                problem_statement=request.problem_statement,
                impossibility_constraints=request.impossibility_constraints,
                contradiction_requirements=request.contradiction_requirements,
                shock_threshold=request.shock_threshold,
                thinking_budget=request.thinking_budget,
                creative_framework=request.creative_framework
            )
            api_logger.info(f"Successfully generated idea with ID: {response.id}")
        except Exception as gen_error:
            api_logger.error(f"Error generating idea: {str(gen_error)}")
            print(f"Error generating idea: {str(gen_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating idea: {str(gen_error)}"
            )
        
        # Step 2: Save the idea to the database
        api_logger.info(f"Saving idea to database: {response.id}")
        print(f"Saving idea to database: {response.id}")
        
        try:
            # Convert the API response to CreativeIdea model
            from ..knowledge_representation.models import CreativeIdea, ShockProfile
            
            creative_idea = CreativeIdea(
                id=response.id,
                description=response.idea,
                generative_framework=response.framework,
                domain=request.domain,  # Store the domain from the request
                impossibility_elements=request.impossibility_constraints if request.impossibility_constraints else [],
                contradiction_elements=request.contradiction_requirements if request.contradiction_requirements else [],
                related_concepts=[],
                shock_metrics=ShockProfile(
                    novelty_score=response.shock_metrics.novelty_score,
                    contradiction_score=response.shock_metrics.contradiction_score,
                    impossibility_score=response.shock_metrics.impossibility_score,
                    utility_potential=response.shock_metrics.utility_potential,
                    expert_rejection_probability=response.shock_metrics.expert_rejection_probability,
                    composite_shock_value=response.shock_metrics.composite_shock_value
                )
            )
            
            # Save the idea using the repository - this part might fail
            saved_idea = await repository.save_idea(creative_idea)
            api_logger.info(f"Idea successfully saved to database: {saved_idea.id}")
            print(f"Idea successfully saved to database: {saved_idea.id}")
        except Exception as save_error:
            # Log the error but still return the generated idea
            api_logger.error(f"Error saving idea: {str(save_error)}")
            print(f"Error saving idea: {str(save_error)}")
            # We continue and return the generated idea even if saving failed
            
        # Return the generated idea regardless of whether saving succeeded
        return response
        
    except Exception as e:
        # This handles any other unexpected errors
        api_logger.error(f"Unexpected error in idea generation endpoint: {str(e)}")
        print(f"Unexpected error in idea generation endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ideas")
async def get_all_ideas(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all creative ideas with pagination.
    
    Args:
        limit: Maximum number of ideas to return (default: 50, max: 100)
        offset: Number of ideas to skip for pagination
        
    Returns:
        List of creative ideas
    """
    try:
        api_logger.info(f"API: Getting all creative ideas with limit={limit}, offset={offset}")
        print(f"API: Getting all creative ideas with limit={limit}, offset={offset}")
        
        try:
            ideas = await repository.get_all_ideas(limit=limit, offset=offset)
        except Exception as db_error:
            # Log the database error
            api_logger.error(f"API: Database error: {str(db_error)}")
            print(f"API: Database error: {str(db_error)}")
            
            # In production, we might want to return empty results instead of error
            # but during development, it's better to raise the error
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(db_error)}"
            )
        
        # If we get here, we have successfully retrieved ideas (might be empty list)
        idea_count = len(ideas)
        idea_ids = [str(idea.id) for idea in ideas[:5]] if ideas else []
        id_list = ', '.join(idea_ids) if idea_ids else 'none'
        
        api_logger.info(f"API: Found {idea_count} creative ideas. First few IDs: {id_list}")
        print(f"API: Found {idea_count} creative ideas. First few IDs: {id_list}")
        
        # Convert database model format to API response format
        api_ideas = []
        for idea in ideas:
            api_idea = {
                "id": str(idea.id),
                "idea": idea.description,  # Map database 'description' to API 'idea'
                "description": idea.description,  # Also include as description for compatibility
                "framework": idea.generative_framework,  # Map database 'generative_framework' to API 'framework'
                "generative_framework": idea.generative_framework,  # Also include original field
                "domain": getattr(idea, "domain", None),  # Include domain if available
                "impossibility_elements": idea.impossibility_elements if hasattr(idea, "impossibility_elements") else [],
                "contradiction_elements": idea.contradiction_elements if hasattr(idea, "contradiction_elements") else [],
                "shock_metrics": {
                    "novelty_score": idea.shock_metrics.novelty_score if idea.shock_metrics else 0.7,
                    "contradiction_score": idea.shock_metrics.contradiction_score if idea.shock_metrics else 0.7,
                    "impossibility_score": idea.shock_metrics.impossibility_score if idea.shock_metrics else 0.7,
                    "utility_potential": idea.shock_metrics.utility_potential if idea.shock_metrics else 0.7,
                    "expert_rejection_probability": idea.shock_metrics.expert_rejection_probability if idea.shock_metrics else 0.7,
                    "composite_shock_value": idea.shock_metrics.composite_shock_value if idea.shock_metrics else 0.7
                },
                "thinking_steps": []  # Empty list as we don't load these by default
            }
            api_ideas.append(api_idea)
        
        # Return the converted ideas - even if it's an empty list
        return {"ideas": api_ideas}
    except Exception as e:
        # General error handling
        error_msg = f"API: Error getting creative ideas: {str(e)}"
        api_logger.error(error_msg)
        print(error_msg)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/dialectic", response_model=DialecticIdeaResponse)
async def generate_dialectic_idea(
    request: DialecticIdeaRequest,
    leela_api: LeelaCoreAPI = Depends(get_leela_api)
):
    """
    Generate an idea through dialectic thinking.
    """
    try:
        # Step 1: Generate the dialectic idea
        api_logger.info("Generating dialectic idea...")
        try:
            response = await leela_api.generate_dialectic_idea(
                domain=request.domain,
                problem_statement=request.problem_statement,
                perspectives=request.perspectives,
                thinking_budget=request.thinking_budget
            )
            api_logger.info(f"Successfully generated dialectic idea with ID: {response.id}")
        except Exception as gen_error:
            api_logger.error(f"Error generating dialectic idea: {str(gen_error)}")
            print(f"Error generating dialectic idea: {str(gen_error)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error generating dialectic idea: {str(gen_error)}"
            )
        
        # Step 2: Save the idea to the database
        api_logger.info(f"Saving dialectic idea to database: {response.id}")
        print(f"Saving dialectic idea to database: {response.id}")
        
        try:
            # Convert the API response to CreativeIdea model
            from ..knowledge_representation.models import CreativeIdea, ShockProfile
            
            creative_idea = CreativeIdea(
                id=response.id,
                description=response.synthesized_idea,
                generative_framework="dialectic_synthesis",
                domain=request.domain,  # Store the domain from the request
                impossibility_elements=[],  # No explicit impossibility constraints in dialectic
                contradiction_elements=request.perspectives,  # Store perspectives as contradiction elements
                related_concepts=[],
                shock_metrics=ShockProfile(
                    novelty_score=response.shock_metrics.novelty_score,
                    contradiction_score=response.shock_metrics.contradiction_score,
                    impossibility_score=response.shock_metrics.impossibility_score,
                    utility_potential=response.shock_metrics.utility_potential,
                    expert_rejection_probability=response.shock_metrics.expert_rejection_probability,
                    composite_shock_value=response.shock_metrics.composite_shock_value
                )
            )
            
            # Save the idea using the repository - this part might fail
            saved_idea = await repository.save_idea(creative_idea)
            api_logger.info(f"Dialectic idea successfully saved to database: {saved_idea.id}")
            print(f"Dialectic idea successfully saved to database: {saved_idea.id}")
        except Exception as save_error:
            # Log the error but still return the generated idea
            api_logger.error(f"Error saving dialectic idea: {str(save_error)}")
            print(f"Error saving dialectic idea: {str(save_error)}")
            # We continue and return the generated idea even if saving failed
            
        # Return the generated idea regardless of whether saving succeeded
        return response
        
    except Exception as e:
        # This handles any other unexpected errors
        api_logger.error(f"Unexpected error in dialectic idea endpoint: {str(e)}")
        print(f"Unexpected error in dialectic idea endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/domains")
async def get_domains():
    """
    Get available domains and their impossibility constraints.
    """
    return {"domains": config["domain_impossibilities"]}


@app.get("/api/v1/frameworks")
async def get_frameworks():
    """
    Get available creative frameworks.
    """
    # Get available prompt templates
    available_prompts = prompt_loader.get_available_prompts()
    
    # Define standard frameworks
    standard_frameworks = [
        {
            "id": "impossibility_enforcer",
            "name": "Impossibility Enforcer",
            "description": "Ensures outputs contain elements that experts would consider impossible"
        },
        {
            "id": "cognitive_dissonance_amplifier",
            "name": "Cognitive Dissonance Amplifier",
            "description": "Forces contradictory yet simultaneously necessary concepts to coexist"
        },
        {
            "id": "dialectic_synthesis",
            "name": "Dialectic Synthesis",
            "description": "Generates ideas through dialectic thinking from multiple perspectives"
        }
    ]
    
    # Add any additional prompt templates not in standard frameworks
    frameworks = standard_frameworks.copy()
    standard_ids = [f["id"] for f in standard_frameworks]
    
    for prompt in available_prompts:
        if prompt not in standard_ids:
            frameworks.append({
                "id": prompt,
                "name": prompt.replace("_", " ").title(),
                "description": "Custom creative framework",
                "is_custom": True
            })
    
    return {"frameworks": frameworks}


@app.get("/api/v1/prompts")
async def get_prompts():
    """
    Get available prompt templates.
    """
    available_prompts = prompt_loader.get_available_prompts()
    return {"prompts": available_prompts}


@app.get("/api/v1/prompts/{prompt_name}")
async def get_prompt(prompt_name: str):
    """
    Get a specific prompt template.
    """
    # Check if prompt exists
    available_prompts = prompt_loader.get_available_prompts()
    if prompt_name not in available_prompts:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
    
    # Get the prompt file path
    prompts_dir = config["paths"]["prompts_dir"]
    prompt_path = os.path.join(prompts_dir, f"{prompt_name}.txt")
    
    # Read the prompt content
    try:
        with open(prompt_path, "r") as f:
            content = f.read()
        return {"name": prompt_name, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading prompt: {str(e)}")


@app.post("/api/v1/prompts/{prompt_name}")
async def create_or_update_prompt(prompt_name: str, content: Dict[str, str]):
    """
    Create or update a prompt template.
    """
    if "content" not in content:
        raise HTTPException(status_code=400, detail="Prompt content required")
    
    # Create or update the prompt
    success = prompt_loader.create_prompt(prompt_name, content["content"])
    
    if success:
        return {"message": f"Prompt '{prompt_name}' created/updated successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Error creating/updating prompt '{prompt_name}'")


@app.delete("/api/v1/prompts/{prompt_name}")
async def delete_prompt(prompt_name: str):
    """
    Delete a prompt template.
    """
    # Check if prompt exists
    available_prompts = prompt_loader.get_available_prompts()
    if prompt_name not in available_prompts:
        raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
    
    # Delete the prompt
    success = prompt_loader.delete_prompt(prompt_name)
    
    if success:
        return {"message": f"Prompt '{prompt_name}' deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail=f"Error deleting prompt '{prompt_name}'")


@app.post("/api/v1/meta/idea")
async def generate_meta_idea(
    request: Dict[str, Any],
    meta_engine: MetaEngine = Depends(get_meta_engine)
):
    """
    Generate an idea using the Meta-Engine.
    """
    if "problem_statement" not in request:
        raise HTTPException(status_code=400, detail="Problem statement required")
    
    if "domain" not in request:
        raise HTTPException(status_code=400, detail="Domain required")
    
    # Get workflow
    workflow_str = request.get("workflow", "DISRUPTOR")
    try:
        from ..meta_engine.engine import CreativeWorkflow
        workflow = getattr(CreativeWorkflow, workflow_str.upper())
    except (AttributeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid workflow: {workflow_str}")
    
    # Additional contexts
    additional_contexts = request.get("contexts", {})
    
    try:
        # Generate idea
        result = await meta_engine.generate_idea(
            problem_statement=request["problem_statement"],
            domain=request["domain"],
            workflow=workflow,
            additional_contexts=additional_contexts
        )
        
        return result
    except Exception as e:
        api_logger.error(f"Error generating meta idea: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run_app():
    """Run the FastAPI app with Uvicorn."""
    import uvicorn
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    run_app()