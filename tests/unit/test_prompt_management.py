"""
Unit tests for prompt management module.
"""
import os
import tempfile
import pytest
from pathlib import Path
from leela.prompt_management.prompt_loader import PromptLoader


@pytest.fixture
def temp_prompts_dir():
    """Create a temporary prompts directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test prompts
        tmp_path = Path(tmp_dir)
        test_prompt1 = tmp_path / "test_prompt1.txt"
        test_prompt2 = tmp_path / "test_prompt2.txt"
        
        with open(test_prompt1, "w") as f:
            f.write("This is test prompt 1 with {{variable}}")
        
        with open(test_prompt2, "w") as f:
            f.write("This is test prompt 2 with {% for item in items %}{{item}}{% endfor %}")
        
        # Mock get_config to return our temp directory
        def mock_get_config():
            return {
                "paths": {
                    "prompts_dir": str(tmp_path)
                }
            }
        
        # Patch get_config in the prompt_loader module
        import leela.prompt_management.prompt_loader
        original_get_config = leela.prompt_management.prompt_loader.get_config
        leela.prompt_management.prompt_loader.get_config = mock_get_config
        
        yield tmp_path
        
        # Restore original get_config
        leela.prompt_management.prompt_loader.get_config = original_get_config


def test_get_available_prompts(temp_prompts_dir):
    """Test getting available prompts."""
    loader = PromptLoader()
    prompts = loader.get_available_prompts()
    
    assert "test_prompt1" in prompts
    assert "test_prompt2" in prompts
    assert len(prompts) == 2


def test_load_prompt(temp_prompts_dir):
    """Test loading a prompt."""
    loader = PromptLoader()
    template = loader.load_prompt("test_prompt1")
    
    assert template is not None


def test_render_prompt(temp_prompts_dir):
    """Test rendering a prompt with context."""
    loader = PromptLoader()
    rendered = loader.render_prompt("test_prompt1", {"variable": "hello"})
    
    assert rendered == "This is test prompt 1 with hello"


def test_render_prompt_with_loop(temp_prompts_dir):
    """Test rendering a prompt with a loop."""
    loader = PromptLoader()
    rendered = loader.render_prompt("test_prompt2", {"items": ["a", "b", "c"]})
    
    assert rendered == "This is test prompt 2 with abc"


def test_create_prompt(temp_prompts_dir):
    """Test creating a new prompt."""
    loader = PromptLoader()
    success = loader.create_prompt("new_prompt", "This is a new prompt")
    
    assert success
    assert "new_prompt" in loader.get_available_prompts()
    
    # Check prompt content
    new_prompt_path = temp_prompts_dir / "new_prompt.txt"
    with open(new_prompt_path, "r") as f:
        content = f.read()
    
    assert content == "This is a new prompt"


def test_update_prompt(temp_prompts_dir):
    """Test updating an existing prompt."""
    loader = PromptLoader()
    success = loader.update_prompt("test_prompt1", "Updated content")
    
    assert success
    
    # Check prompt content
    prompt_path = temp_prompts_dir / "test_prompt1.txt"
    with open(prompt_path, "r") as f:
        content = f.read()
    
    assert content == "Updated content"


def test_delete_prompt(temp_prompts_dir):
    """Test deleting a prompt."""
    loader = PromptLoader()
    success = loader.delete_prompt("test_prompt1")
    
    assert success
    assert "test_prompt1" not in loader.get_available_prompts()
    assert not (temp_prompts_dir / "test_prompt1.txt").exists()


def test_delete_nonexistent_prompt(temp_prompts_dir):
    """Test deleting a prompt that doesn't exist."""
    loader = PromptLoader()
    success = loader.delete_prompt("nonexistent_prompt")
    
    assert not success