"""
Unit tests for the prompt implementation manager.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from leela.prompt_management import (
    PromptLoader, 
    PromptVersionManager, 
    PromptImplementationManager,
    uses_prompt
)

# Test decorator usage
@uses_prompt("test_prompt")
def test_decorated_function():
    """A test function decorated with uses_prompt."""
    return "test"

@uses_prompt("test_prompt_with_deps", dependencies=["dep1", "dep2"])
class TestDecoratedClass:
    """A test class decorated with uses_prompt and dependencies."""
    
    def method(self):
        """Test method."""
        return "test"


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    return {
        "paths": {
            "base_dir": "/test/base/dir",
            "prompts_dir": "/test/prompts/dir"
        },
        "project": {
            "module_name": "leela"
        }
    }


@pytest.fixture
def prompt_implementation_manager(mock_config):
    """Create a PromptImplementationManager instance for testing."""
    with patch("leela.prompt_management.prompt_implementation_manager.get_config", 
              return_value=mock_config):
        with patch("leela.prompt_management.prompt_implementation_manager.PromptLoader"):
            with patch("leela.prompt_management.prompt_implementation_manager.PromptVersionManager"):
                manager = PromptImplementationManager()
                # Mock the logger to avoid actual logging
                manager.logger = MagicMock()
                return manager


def test_implementation_discovery_local_objects():
    """Test discovery of implementations in local module objects."""
    # This test checks that the decorator correctly sets attributes on the decorated objects
    assert hasattr(test_decorated_function, "__prompt__")
    assert test_decorated_function.__prompt__ == "test_prompt"
    assert hasattr(test_decorated_function, "prompt_dependencies")
    assert test_decorated_function.prompt_dependencies == []
    
    assert hasattr(TestDecoratedClass, "__prompt__")
    assert TestDecoratedClass.__prompt__ == "test_prompt_with_deps"
    assert hasattr(TestDecoratedClass, "prompt_dependencies")
    assert TestDecoratedClass.prompt_dependencies == ["dep1", "dep2"]


def test_extract_implementation_info(prompt_implementation_manager):
    """Test extraction of implementation info from decorated objects."""
    prompt_base_names = {"test_prompt": "test_prompt", "test_prompt_with_deps": "test_prompt_with_deps"}
    
    # Test extraction from decorated function
    impl_info = prompt_implementation_manager._extract_implementation_info(
        "test_decorated_function", test_decorated_function, prompt_base_names
    )
    
    assert impl_info is not None
    prompt_name, info = impl_info
    assert prompt_name == "test_prompt"
    assert info["name"] == "test_decorated_function"
    assert info["type"] == "function"
    assert info["dependencies"] == []
    
    # Test extraction from decorated class
    impl_info = prompt_implementation_manager._extract_implementation_info(
        "TestDecoratedClass", TestDecoratedClass, prompt_base_names
    )
    
    assert impl_info is not None
    prompt_name, info = impl_info
    assert prompt_name == "test_prompt_with_deps"
    assert info["name"] == "TestDecoratedClass"
    assert info["type"] == "class"
    assert info["dependencies"] == ["dep1", "dep2"]


def test_find_matching_prompt(prompt_implementation_manager):
    """Test finding matching prompts based on various criteria."""
    prompt_base_names = {"test": "test_prompt", "cognitive_dissonance": "cognitive_dissonance_amplifier"}
    
    # Test with explicit prompt_name attribute
    class TestWithAttr:
        prompt_name = "test_prompt"
    
    assert prompt_implementation_manager._find_matching_prompt(
        "TestWithAttr", TestWithAttr, prompt_base_names
    ) == "test_prompt"
    
    # Test with @uses_prompt decorator
    assert prompt_implementation_manager._find_matching_prompt(
        "test_decorated_function", test_decorated_function, prompt_base_names
    ) == "test_prompt"
    
    # Test with docstring reference
    class TestWithDocstring:
        """
        Test class.
        
        Implements prompt: "test_prompt"
        """
    
    with patch("leela.prompt_management.prompt_implementation_manager.inspect.getdoc", 
              return_value=TestWithDocstring.__doc__):
        with patch("leela.prompt_management.prompt_loader.PromptLoader.get_available_prompts", 
                  return_value=["test_prompt"]):
            assert prompt_implementation_manager._find_matching_prompt(
                "TestWithDocstring", TestWithDocstring, prompt_base_names
            ) == "test_prompt"
    
    # Test with naming pattern
    class CognitiveDissonanceEngine:
        """Test class with name matching a prompt."""
        pass
    
    assert prompt_implementation_manager._find_matching_prompt(
        "CognitiveDissonanceEngine", CognitiveDissonanceEngine, prompt_base_names
    ) == "cognitive_dissonance_amplifier"


def test_implementation_manager_integration():
    """
    Integration test that verifies the PromptImplementationManager can find
    actual implementations in the codebase.
    """
    # This test will only run if the shock_generation module exists
    try:
        from leela.shock_generation.impossibility_enforcer import ImpossibilityEnforcer
        from leela.shock_generation.cognitive_dissonance_amplifier import CognitiveDissonanceAmplifier
    except ImportError:
        pytest.skip("Shock generation modules not available")
    
    # Create a manager with actual config
    manager = PromptImplementationManager()
    
    # Discover implementations
    implementations = manager.discover_implementations()
    
    # Check that the shock generation implementations were discovered
    assert "impossibility_enforcer" in implementations
    assert "cognitive_dissonance_amplifier" in implementations
    
    # Verify implementation details
    impossibility_impls = manager.get_implementation("impossibility_enforcer", "class")
    assert len(impossibility_impls) > 0
    assert impossibility_impls[0]["name"] == "ImpossibilityEnforcer"
    
    dissonance_impls = manager.get_implementation("cognitive_dissonance_amplifier", "class")
    assert len(dissonance_impls) > 0
    assert dissonance_impls[0]["name"] == "CognitiveDissonanceAmplifier"
    
    # Check that dependencies were correctly extracted
    dependencies = manager.get_prompt_dependencies("cognitive_dissonance_amplifier")
    assert "dialectic_synthesis" in dependencies


if __name__ == "__main__":
    # Run tests manually if file is executed directly
    pytest.main(["-xvs", __file__])