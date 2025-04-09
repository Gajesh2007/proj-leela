"""
Prompt Implementation Manager for Project Leela.
This module manages the connections between prompts and their code implementations.
"""
import importlib
import inspect
import logging
from typing import Dict, List, Any, Optional, Callable, Type, Set, Tuple
from importlib.util import find_spec
from pathlib import Path
import re

from ..config import get_config
from .prompt_loader import PromptLoader
from .prompt_version_manager import PromptVersionManager


class PromptImplementationManager:
    """
    Manages the connections between prompts and their Python implementations.
    
    This class is responsible for connecting prompt templates in the prompts directory
    with the Python code that implements them. It allows for:
    
    1. Discovering prompt implementations across the codebase
    2. Mapping prompts to their implementing classes/functions
    3. Validating prompt-code connections
    4. Tracking prompt dependencies
    5. Providing runtime access to implementations for a given prompt
    """
    
    def __init__(self):
        """Initialize the prompt implementation manager."""
        config = get_config()
        self.base_dir = Path(config["paths"]["base_dir"])
        self.module_name = config.get("project", {}).get("module_name", "leela")
        
        # Initialize prompt loader and version manager
        self.prompt_loader = PromptLoader()
        self.version_manager = PromptVersionManager()
        
        # Dictionary to store prompt implementations
        self.implementations: Dict[str, Dict[str, Any]] = {}
        
        # Dictionary to store prompt dependencies
        self.dependencies: Dict[str, Set[str]] = {}
        
        # Dictionary to store performance metrics for each implementation
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        
        # Logger
        self.logger = logging.getLogger(__name__)
    
    def discover_implementations(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover prompt implementations across the codebase.
        
        This method scans the codebase for classes and functions that are decorated with
        prompt-related decorators or contain prompt-related metadata.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping prompt names to their implementations
        """
        self.implementations = {}
        
        # Get all available prompts
        available_prompts = self.prompt_loader.get_available_prompts()
        prompt_base_names = {self._get_base_name(p): p for p in available_prompts}
        
        # Scan the codebase for modules
        module_specs = self._discover_modules(self.module_name)
        
        for module_name in module_specs:
            try:
                # Import the module
                module = importlib.import_module(module_name)
                
                # Look for prompt implementations in the module
                for name, obj in inspect.getmembers(module):
                    implementation = self._extract_implementation_info(name, obj, prompt_base_names)
                    
                    if implementation:
                        prompt_name, impl_info = implementation
                        
                        if prompt_name not in self.implementations:
                            self.implementations[prompt_name] = {}
                        
                        # Store implementation by type
                        impl_type = impl_info["type"]
                        if impl_type not in self.implementations[prompt_name]:
                            self.implementations[prompt_name][impl_type] = []
                        
                        self.implementations[prompt_name][impl_type].append(impl_info)
                        
                        # Log discovery
                        self.logger.debug(f"Discovered implementation for prompt '{prompt_name}': {name} "
                                         f"({module_name}.{name})")
            
            except (ImportError, AttributeError) as e:
                self.logger.warning(f"Error importing module {module_name}: {e}")
        
        return self.implementations
    
    def _discover_modules(self, package_name: str) -> List[str]:
        """
        Discover all modules in a package recursively.
        
        Args:
            package_name: Name of the package to scan
            
        Returns:
            List[str]: List of module names
        """
        modules = []
        
        try:
            package_spec = find_spec(package_name)
            if package_spec is None or package_spec.submodule_search_locations is None:
                return modules
            
            package_path = package_spec.submodule_search_locations[0]
            for path in Path(package_path).glob("**/*.py"):
                if path.name.startswith("_") and path.name != "__init__.py":
                    continue
                
                module_rel_path = path.relative_to(package_path)
                module_parts = list(module_rel_path.parts)
                module_parts[-1] = module_parts[-1].replace(".py", "")
                
                # Skip if the module is __pycache__
                if "__pycache__" in module_parts:
                    continue
                
                # Construct full module name
                module_name = package_name + "." + ".".join(module_parts)
                if module_name.endswith(".__init__"):
                    module_name = module_name[:-9]
                
                modules.append(module_name)
        
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"Error discovering modules in {package_name}: {e}")
        
        return modules
    
    def _extract_implementation_info(self, name: str, obj: Any, 
                                   prompt_base_names: Dict[str, str]) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Extract implementation information from an object.
        
        Args:
            name: Name of the object
            obj: The object to inspect
            prompt_base_names: Dictionary mapping base prompt names to full prompt names
            
        Returns:
            Optional[Tuple[str, Dict[str, Any]]]: Tuple of (prompt_name, implementation_info) or None
        """
        # Skip built-in objects and modules
        if inspect.isbuiltin(obj) or inspect.ismodule(obj):
            return None
        
        # Check for prompt-related metadata or naming patterns
        prompt_name = self._find_matching_prompt(name, obj, prompt_base_names)
        
        if not prompt_name:
            return None
        
        # Create implementation info dictionary
        implementation_info = {
            "name": name,
            "module": obj.__module__,
            "object": obj,
            "type": self._get_implementation_type(obj),
            "doc": inspect.getdoc(obj) or "",
            "file": inspect.getfile(obj) if hasattr(obj, "__file__") else "",
            "line": inspect.getsourcelines(obj)[1] if inspect.isclass(obj) or inspect.isfunction(obj) else 0,
            "dependencies": self._extract_dependencies(obj)
        }
        
        return prompt_name, implementation_info
    
    def _find_matching_prompt(self, name: str, obj: Any, 
                             prompt_base_names: Dict[str, str]) -> Optional[str]:
        """
        Find the matching prompt for an object.
        
        Args:
            name: Name of the object
            obj: The object to inspect
            prompt_base_names: Dictionary mapping base prompt names to full prompt names
            
        Returns:
            Optional[str]: Prompt name if found, None otherwise
        """
        # Check for prompt_name attribute
        if hasattr(obj, "prompt_name"):
            return obj.prompt_name
        
        # Check for @uses_prompt decorator
        if hasattr(obj, "__prompt__"):
            return obj.__prompt__
        
        # Check class docstring for prompt reference
        doc = inspect.getdoc(obj) or ""
        prompt_doc_match = re.search(r"Implements prompt[:\s]+(['\"](.*?)['\"])", doc)
        if prompt_doc_match:
            prompt_name = prompt_doc_match.group(2)
            return prompt_name if prompt_name in self.prompt_loader.get_available_prompts() else None
        
        # Check for naming patterns
        obj_name = name.lower()
        
        for base_name, full_name in prompt_base_names.items():
            # Check if object name contains the base prompt name
            if base_name in obj_name:
                # Additional check for specificity (to avoid false positives)
                # For example, if the prompt is "disruptor_inversion", the class should be
                # something like "DisruptorInversionEngine" or "InversionDisruptor"
                name_parts = base_name.split("_")
                match_count = sum(1 for part in name_parts if part in obj_name)
                
                # If more than half of the parts match, consider it a match
                if match_count >= len(name_parts) / 2:
                    return full_name
        
        return None
    
    def _get_implementation_type(self, obj: Any) -> str:
        """
        Get the implementation type of an object.
        
        Args:
            obj: The object to inspect
            
        Returns:
            str: Implementation type ("class", "function", or "other")
        """
        if inspect.isclass(obj):
            return "class"
        elif inspect.isfunction(obj):
            return "function"
        else:
            return "other"
    
    def _extract_dependencies(self, obj: Any) -> List[str]:
        """
        Extract prompt dependencies from an object.
        
        Args:
            obj: The object to inspect
            
        Returns:
            List[str]: List of prompt dependencies
        """
        dependencies = []
        
        # Check for explicit dependencies attribute
        if hasattr(obj, "prompt_dependencies"):
            dependencies.extend(obj.prompt_dependencies)
        
        # Check for implicit dependencies in docstring
        doc = inspect.getdoc(obj) or ""
        dependency_matches = re.finditer(r"Depends on prompt[:\s]+(['\"](.*?)['\"])", doc)
        
        for match in dependency_matches:
            dependency = match.group(2)
            if dependency in self.prompt_loader.get_available_prompts():
                dependencies.append(dependency)
        
        return dependencies
    
    def _get_base_name(self, prompt_name: str) -> str:
        """
        Get the base name of a prompt (without file extension).
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            str: Base name of the prompt
        """
        return prompt_name.lower().replace("-", "_")
    
    def get_implementation(self, prompt_name: str, impl_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get implementations for a prompt.
        
        Args:
            prompt_name: Name of the prompt
            impl_type: Optional implementation type filter ("class", "function", or None for all)
            
        Returns:
            List[Dict[str, Any]]: List of implementation details
        """
        if not self.implementations:
            self.discover_implementations()
        
        if prompt_name not in self.implementations:
            return []
        
        if impl_type:
            return self.implementations[prompt_name].get(impl_type, [])
        
        # Return all implementations
        all_implementations = []
        for impl_list in self.implementations[prompt_name].values():
            all_implementations.extend(impl_list)
        
        return all_implementations
    
    def get_prompt_dependencies(self, prompt_name: str) -> Set[str]:
        """
        Get dependencies for a prompt based on its implementations.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Set[str]: Set of prompt dependencies
        """
        if prompt_name not in self.dependencies:
            # Get all implementations for the prompt
            implementations = self.get_implementation(prompt_name)
            
            # Collect dependencies from all implementations
            deps = set()
            for impl in implementations:
                deps.update(impl.get("dependencies", []))
            
            # Store in dependencies cache
            self.dependencies[prompt_name] = deps
        
        return self.dependencies[prompt_name]
    
    def verify_implementations(self) -> Dict[str, List[str]]:
        """
        Verify that all prompts have implementations and report issues.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping issue types to lists of affected prompts
        """
        if not self.implementations:
            self.discover_implementations()
        
        all_prompts = self.prompt_loader.get_available_prompts()
        all_implementations = self.implementations.keys()
        
        # Check for prompts without implementations
        missing_implementations = set(all_prompts) - set(all_implementations)
        
        # Check for implementations without prompts
        missing_prompts = set(all_implementations) - set(all_prompts)
        
        # Check for circular dependencies
        circular_dependencies = self._check_circular_dependencies()
        
        return {
            "missing_implementations": sorted(list(missing_implementations)),
            "missing_prompts": sorted(list(missing_prompts)),
            "circular_dependencies": sorted(list(circular_dependencies))
        }
    
    def _check_circular_dependencies(self) -> Set[str]:
        """
        Check for circular dependencies in prompt implementations.
        
        Returns:
            Set[str]: Set of prompts with circular dependencies
        """
        circular = set()
        
        for prompt_name in self.implementations:
            # Get dependencies
            deps = self.get_prompt_dependencies(prompt_name)
            
            # Check for circular dependencies
            visited = {prompt_name}
            for dep in deps:
                if self._has_circular_dependency(dep, visited, set()):
                    circular.add(prompt_name)
                    break
        
        return circular
    
    def _has_circular_dependency(self, 
                               prompt_name: str, 
                               visited: Set[str], 
                               path: Set[str]) -> bool:
        """
        Check if a prompt has circular dependencies.
        
        Args:
            prompt_name: Name of the prompt to check
            visited: Set of visited prompts
            path: Current dependency path
            
        Returns:
            bool: True if circular dependency found, False otherwise
        """
        if prompt_name in path:
            return True
        
        if prompt_name in visited:
            return False
        
        visited.add(prompt_name)
        path.add(prompt_name)
        
        # Get dependencies
        deps = self.get_prompt_dependencies(prompt_name)
        
        for dep in deps:
            if self._has_circular_dependency(dep, visited, path):
                return True
        
        path.remove(prompt_name)
        return False
    
    def get_implementation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about prompt implementations.
        
        Returns:
            Dict[str, Any]: Dictionary of implementation statistics
        """
        if not self.implementations:
            self.discover_implementations()
        
        all_prompts = self.prompt_loader.get_available_prompts()
        
        stats = {
            "total_prompts": len(all_prompts),
            "implemented_prompts": len(self.implementations),
            "implementation_percentage": 0,
            "implementation_types": {
                "class": 0,
                "function": 0,
                "other": 0
            },
            "dependency_stats": {
                "max_dependencies": 0,
                "avg_dependencies": 0,
                "total_dependencies": 0
            }
        }
        
        # Calculate implementation percentage
        if all_prompts:
            stats["implementation_percentage"] = (len(self.implementations) / len(all_prompts)) * 100
        
        # Count implementation types
        for prompt_impls in self.implementations.values():
            for impl_type, impls in prompt_impls.items():
                stats["implementation_types"][impl_type] += len(impls)
        
        # Calculate dependency statistics
        all_dependency_counts = []
        for prompt_name in self.implementations:
            deps = self.get_prompt_dependencies(prompt_name)
            all_dependency_counts.append(len(deps))
        
        if all_dependency_counts:
            stats["dependency_stats"]["max_dependencies"] = max(all_dependency_counts, default=0)
            stats["dependency_stats"]["avg_dependencies"] = sum(all_dependency_counts) / len(all_dependency_counts)
            stats["dependency_stats"]["total_dependencies"] = sum(all_dependency_counts)
        
        return stats
    
    def record_performance_metrics(self, 
                                prompt_name: str, 
                                metrics: Dict[str, float]) -> bool:
        """
        Record performance metrics for a prompt implementation.
        
        Args:
            prompt_name: Name of the prompt
            metrics: Dictionary of performance metrics
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store in performance metrics dictionary
            self.performance_metrics[prompt_name] = metrics
            
            # If versioning is enabled, add metrics to the prompt version
            version_metadata = self.version_manager.get_prompt_metadata(prompt_name)
            if version_metadata:
                # Get the current version
                version = version_metadata.get("version")
                if version:
                    # Create a new version with updated metrics
                    self.version_manager.create_new_version(
                        prompt_name=prompt_name,
                        author=version_metadata.get("author", "system"),
                        change_type="patch",
                        commit_message="Update performance metrics",
                        performance_metrics=metrics
                    )
            
            return True
        except Exception as e:
            self.logger.error(f"Error recording performance metrics for '{prompt_name}': {e}")
            return False
    
    def get_performance_metrics(self, prompt_name: str) -> Dict[str, float]:
        """
        Get performance metrics for a prompt implementation.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Dict[str, float]: Dictionary of performance metrics
        """
        # Check current metrics
        if prompt_name in self.performance_metrics:
            return self.performance_metrics[prompt_name]
        
        # Check version history
        performance_history = self.version_manager.get_performance_history(prompt_name)
        
        if performance_history:
            # Get the latest version's metrics
            versions = sorted(performance_history.keys(), key=lambda v: semver.VersionInfo.parse(v))
            latest_version = versions[-1]
            return performance_history[latest_version]
        
        return {}


# Helper decorator for identifying prompt implementations
def uses_prompt(prompt_name: str, dependencies: Optional[List[str]] = None):
    """
    Decorator to mark a class or function as implementing a specific prompt.
    
    Args:
        prompt_name: Name of the prompt this implements
        dependencies: Optional list of prompt dependencies
        
    Returns:
        Callable: Decorator function
    """
    def decorator(obj):
        obj.__prompt__ = prompt_name
        obj.prompt_dependencies = dependencies or []
        return obj
    
    return decorator


def test_prompt_implementation_manager():
    """Test function for PromptImplementationManager."""
    manager = PromptImplementationManager()
    
    # Discover implementations
    implementations = manager.discover_implementations()
    
    print(f"Discovered {len(implementations)} prompt implementations:")
    for prompt_name, impls in implementations.items():
        print(f"  - {prompt_name}:")
        for impl_type, impl_list in impls.items():
            print(f"    - {impl_type}: {len(impl_list)}")
    
    # Verify implementations
    issues = manager.verify_implementations()
    
    print("\nImplementation issues:")
    for issue_type, affected_prompts in issues.items():
        print(f"  - {issue_type}: {len(affected_prompts)}")
        if affected_prompts:
            for prompt in affected_prompts[:5]:  # Show only first 5
                print(f"    - {prompt}")
            if len(affected_prompts) > 5:
                print(f"    - ... ({len(affected_prompts) - 5} more)")
    
    # Get implementation stats
    stats = manager.get_implementation_stats()
    
    print("\nImplementation statistics:")
    print(f"  - Total prompts: {stats['total_prompts']}")
    print(f"  - Implemented prompts: {stats['implemented_prompts']}")
    print(f"  - Implementation percentage: {stats['implementation_percentage']:.1f}%")
    print(f"  - Implementation types:")
    for impl_type, count in stats['implementation_types'].items():
        print(f"    - {impl_type}: {count}")


if __name__ == "__main__":
    test_prompt_implementation_manager()