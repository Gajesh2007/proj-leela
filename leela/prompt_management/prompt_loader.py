"""
Dynamic prompt loader for Project Leela.
"""
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

from ..config import get_config

class PromptLoader:
    """
    Dynamically loads and renders prompts using Jinja2 templates.
    """
    
    def __init__(self):
        """Initialize the prompt loader."""
        config = get_config()
        self.prompts_dir = Path(config["paths"]["prompts_dir"])
        self.env = Environment(loader=FileSystemLoader(self.prompts_dir))
        
        # Cache for loaded templates
        self.template_cache = {}
    
    def get_available_prompts(self) -> List[str]:
        """
        Get a list of available prompt templates.
        
        Returns:
            List[str]: List of available prompt template names
        """
        prompt_files = [f for f in os.listdir(self.prompts_dir) if f.endswith(".txt")]
        return [os.path.splitext(f)[0] for f in prompt_files]
    
    def load_prompt(self, prompt_name: str) -> Optional[Template]:
        """
        Load a prompt template by name.
        
        Args:
            prompt_name: Name of the prompt template
            
        Returns:
            Optional[Template]: The loaded template, or None if not found
        """
        if prompt_name in self.template_cache:
            return self.template_cache[prompt_name]
        
        try:
            template = self.env.get_template(f"{prompt_name}.txt")
            self.template_cache[prompt_name] = template
            return template
        except Exception as e:
            print(f"Error loading prompt template '{prompt_name}': {e}")
            return None
    
    def render_prompt(self, prompt_name: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Render a prompt with the given context.
        
        Args:
            prompt_name: Name of the prompt template
            context: Dictionary of context variables
            
        Returns:
            Optional[str]: The rendered prompt, or None if template not found
        """
        template = self.load_prompt(prompt_name)
        if template:
            try:
                return template.render(**context)
            except Exception as e:
                print(f"Error rendering prompt '{prompt_name}': {e}")
                return None
        return None
    
    def create_prompt(self, prompt_name: str, content: str) -> bool:
        """
        Create a new prompt template.
        
        Args:
            prompt_name: Name of the new prompt template
            content: Content of the template
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.prompts_dir / f"{prompt_name}.txt"
            with open(file_path, "w") as f:
                f.write(content)
            
            # Invalidate cache
            if prompt_name in self.template_cache:
                del self.template_cache[prompt_name]
            
            return True
        except Exception as e:
            print(f"Error creating prompt '{prompt_name}': {e}")
            return False
    
    def update_prompt(self, prompt_name: str, content: str) -> bool:
        """
        Update an existing prompt template.
        
        Args:
            prompt_name: Name of the prompt template to update
            content: New content
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.create_prompt(prompt_name, content)
    
    def delete_prompt(self, prompt_name: str) -> bool:
        """
        Delete a prompt template.
        
        Args:
            prompt_name: Name of the prompt template to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = self.prompts_dir / f"{prompt_name}.txt"
            if file_path.exists():
                os.remove(file_path)
                
                # Invalidate cache
                if prompt_name in self.template_cache:
                    del self.template_cache[prompt_name]
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting prompt '{prompt_name}': {e}")
            return False