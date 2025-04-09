"""
Prompt Version Manager for Project Leela.
Implements the prompt versioning and management system described in REBUILD_PREPARATION.md.
"""
import os
import re
import json
import yaml
import shutil
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import semver
import difflib

from ..config import get_config
from .prompt_loader import PromptLoader


class PromptVersionManager:
    """
    Manages versioning of prompts with semantic versioning and metadata tracking.
    """
    
    def __init__(self):
        """Initialize the prompt version manager."""
        config = get_config()
        self.base_prompts_dir = Path(config["paths"]["prompts_dir"])
        self.versioned_prompts_dir = self.base_prompts_dir / "versions"
        
        # Create versioned prompts directory if it doesn't exist
        os.makedirs(self.versioned_prompts_dir, exist_ok=True)
        
        # Initialize prompt loader
        self.prompt_loader = PromptLoader()
        
        # Dictionary to store prompt metadata
        self.prompt_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Load existing metadata
        self._load_metadata()
    
    def _load_metadata(self):
        """Load prompt metadata from the metadata.json file."""
        metadata_path = self.versioned_prompts_dir / "metadata.json"
        
        if metadata_path.exists():
            try:
                with open(metadata_path, "r") as f:
                    self.prompt_metadata = json.load(f)
            except json.JSONDecodeError:
                print(f"Error parsing metadata file. Using empty metadata.")
                self.prompt_metadata = {}
        else:
            self.prompt_metadata = {}
    
    def _save_metadata(self):
        """Save prompt metadata to the metadata.json file."""
        metadata_path = self.versioned_prompts_dir / "metadata.json"
        
        with open(metadata_path, "w") as f:
            json.dump(self.prompt_metadata, f, indent=2)
    
    def _compute_content_hash(self, content: str) -> str:
        """
        Compute a hash of the prompt content to detect changes.
        
        Args:
            content: The prompt content
            
        Returns:
            str: Hash of the content
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from the prompt content if it contains YAML frontmatter.
        
        Args:
            content: The prompt content
            
        Returns:
            Dict[str, Any]: Extracted metadata
        """
        # Look for YAML frontmatter between --- markers
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        
        if frontmatter_match:
            try:
                # Parse YAML frontmatter
                frontmatter = frontmatter_match.group(1)
                metadata = yaml.safe_load(frontmatter)
                
                # Remove frontmatter from content
                content_without_frontmatter = content[frontmatter_match.end():]
                
                return {
                    "metadata": metadata if isinstance(metadata, dict) else {},
                    "content": content_without_frontmatter
                }
            except yaml.YAMLError:
                # If YAML parsing fails, assume it's not valid frontmatter
                pass
        
        # No valid frontmatter found
        return {
            "metadata": {},
            "content": content
        }
    
    def _add_frontmatter_to_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """
        Add YAML frontmatter to prompt content.
        
        Args:
            content: The prompt content
            metadata: The metadata to add
            
        Returns:
            str: Content with frontmatter
        """
        # Check if content already has frontmatter
        if content.startswith("---\n"):
            # Remove existing frontmatter
            frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
            if frontmatter_match:
                content = content[frontmatter_match.end():]
        
        # Create YAML frontmatter
        frontmatter = yaml.dump(metadata)
        
        # Add frontmatter to content
        return f"---\n{frontmatter}---\n\n{content.strip()}"
    
    def get_all_prompt_versions(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of all prompt names and their available versions.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping prompt names to lists of versions
        """
        result = {}
        
        # Iterate over all subdirectories in the versioned prompts directory
        for item in os.listdir(self.versioned_prompts_dir):
            prompt_dir = self.versioned_prompts_dir / item
            
            if not prompt_dir.is_dir() or item == ".git":
                continue
            
            # Get all version files for this prompt
            versions = []
            for version_file in os.listdir(prompt_dir):
                if version_file.endswith(".txt"):
                    version = version_file.replace(".txt", "")
                    versions.append(version)
            
            # Sort versions using semver
            versions.sort(key=lambda v: semver.VersionInfo.parse(v))
            
            result[item] = versions
        
        return result
    
    def get_prompt_metadata(self, prompt_name: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metadata for a specific prompt version.
        
        Args:
            prompt_name: Name of the prompt
            version: Optional version of the prompt. If not provided, gets latest version.
            
        Returns:
            Dict[str, Any]: Prompt metadata
        """
        if prompt_name not in self.prompt_metadata:
            return {}
        
        if version is None:
            # Get metadata for the latest version
            versions = self.prompt_metadata[prompt_name].get("versions", {})
            if not versions:
                return {}
            
            # Sort versions using semver
            sorted_versions = sorted(versions.keys(), key=lambda v: semver.VersionInfo.parse(v))
            latest_version = sorted_versions[-1]
            return versions.get(latest_version, {})
        
        # Get metadata for specific version
        versions = self.prompt_metadata[prompt_name].get("versions", {})
        return versions.get(version, {})
    
    def get_prompt_content(self, prompt_name: str, version: Optional[str] = None) -> Optional[str]:
        """
        Get the content of a specific prompt version.
        
        Args:
            prompt_name: Name of the prompt
            version: Optional version of the prompt. If not provided, gets latest version.
            
        Returns:
            Optional[str]: Prompt content, or None if not found
        """
        if version is None:
            # Get latest version
            all_versions = self.get_all_prompt_versions()
            versions = all_versions.get(prompt_name, [])
            
            if not versions:
                # If no versioned prompts, try to get from base directory
                return self.prompt_loader.load_prompt_content(prompt_name)
            
            # Get latest version
            version = versions[-1]
        
        # Get content for specific version
        prompt_path = self.versioned_prompts_dir / prompt_name / f"{version}.txt"
        
        if not prompt_path.exists():
            return None
        
        with open(prompt_path, "r") as f:
            content = f.read()
        
        # Extract content from frontmatter if present
        extracted = self._extract_metadata_from_content(content)
        return extracted["content"]
    
    def check_for_changes(self, prompt_name: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a prompt has changed compared to its latest version.
        
        Args:
            prompt_name: Name of the prompt to check
            
        Returns:
            Tuple[bool, Dict[str, Any]]: (has_changed, current_metadata)
        """
        # Get current prompt content from the base directory
        current_content = self.prompt_loader.load_prompt_content(prompt_name)
        
        if current_content is None:
            return False, {}
        
        # Compute hash of current content
        current_hash = self._compute_content_hash(current_content)
        
        # Extract metadata
        extracted = self._extract_metadata_from_content(current_content)
        current_content_without_frontmatter = extracted["content"]
        current_metadata = extracted["metadata"]
        
        # Get latest version
        all_versions = self.get_all_prompt_versions()
        versions = all_versions.get(prompt_name, [])
        
        if not versions:
            # No versioned prompt, so it's a new prompt
            return True, current_metadata
        
        # Get latest version content
        latest_version = versions[-1]
        latest_content = self.get_prompt_content(prompt_name, latest_version)
        
        if latest_content is None:
            # Latest version not found, which shouldn't happen
            return True, current_metadata
        
        # Get metadata of latest version
        latest_metadata = self.get_prompt_metadata(prompt_name, latest_version)
        
        # Compare content hash from metadata
        if "content_hash" in latest_metadata and latest_metadata["content_hash"] == current_hash:
            return False, current_metadata
        
        # Compare content directly
        if latest_content.strip() == current_content_without_frontmatter.strip():
            return False, current_metadata
        
        return True, current_metadata
    
    def create_new_version(self, 
                         prompt_name: str, 
                         author: str, 
                         change_type: str = "patch",
                         commit_message: Optional[str] = None,
                         dependencies: Optional[List[str]] = None,
                         performance_metrics: Optional[Dict[str, float]] = None) -> str:
        """
        Create a new version of a prompt.
        
        Args:
            prompt_name: Name of the prompt
            author: Author of the change
            change_type: Type of change ("major", "minor", or "patch")
            commit_message: Optional message describing the change
            dependencies: Optional list of prompt dependencies
            performance_metrics: Optional performance metrics
            
        Returns:
            str: New version number
        """
        # Get current content
        current_content = self.prompt_loader.load_prompt_content(prompt_name)
        
        if current_content is None:
            raise ValueError(f"Prompt '{prompt_name}' not found in base directory")
        
        # Extract any existing metadata
        extracted = self._extract_metadata_from_content(current_content)
        content_without_frontmatter = extracted["content"]
        existing_metadata = extracted["metadata"]
        
        # Compute content hash
        content_hash = self._compute_content_hash(current_content)
        
        # Get latest version (if any)
        all_versions = self.get_all_prompt_versions()
        versions = all_versions.get(prompt_name, [])
        
        if versions:
            latest_version = versions[-1]
            # Parse into semver
            latest_semver = semver.VersionInfo.parse(latest_version)
            
            # Create new version based on change type
            if change_type == "major":
                new_version = str(latest_semver.bump_major())
            elif change_type == "minor":
                new_version = str(latest_semver.bump_minor())
            else:  # Default to patch
                new_version = str(latest_semver.bump_patch())
        else:
            # If no existing version, start with 0.1.0
            new_version = "0.1.0"
        
        # Create directory for prompt if it doesn't exist
        prompt_dir = self.versioned_prompts_dir / prompt_name
        os.makedirs(prompt_dir, exist_ok=True)
        
        # Get change log by diffing against previous version
        changes = ""
        if versions:
            previous_content = self.get_prompt_content(prompt_name, latest_version)
            if previous_content:
                diff = difflib.unified_diff(
                    previous_content.splitlines(),
                    content_without_frontmatter.splitlines(),
                    fromfile=f"{prompt_name} v{latest_version}",
                    tofile=f"{prompt_name} v{new_version}",
                    lineterm=""
                )
                changes = "\n".join(list(diff))
        
        # Create metadata for new version
        version_metadata = {
            "version": new_version,
            "author": author,
            "date": datetime.now().isoformat(),
            "content_hash": content_hash,
            "change_type": change_type,
            "commit_message": commit_message or "No message provided",
            "dependencies": dependencies or [],
            "performance_metrics": performance_metrics or {},
            "change_log": changes
        }
        
        # Update prompt metadata
        if prompt_name not in self.prompt_metadata:
            self.prompt_metadata[prompt_name] = {
                "versions": {}
            }
        
        self.prompt_metadata[prompt_name]["versions"][new_version] = version_metadata
        
        # Add existing metadata to version metadata
        for key, value in existing_metadata.items():
            if key not in version_metadata:
                version_metadata[key] = value
        
        # Create new version file with metadata as frontmatter
        version_content = self._add_frontmatter_to_content(content_without_frontmatter, version_metadata)
        
        # Write to version file
        version_path = prompt_dir / f"{new_version}.txt"
        with open(version_path, "w") as f:
            f.write(version_content)
        
        # Save metadata
        self._save_metadata()
        
        return new_version
    
    def compare_versions(self, prompt_name: str, version1: str, version2: str) -> str:
        """
        Compare two versions of a prompt and return the diff.
        
        Args:
            prompt_name: Name of the prompt
            version1: First version
            version2: Second version
            
        Returns:
            str: Diff between the two versions
        """
        content1 = self.get_prompt_content(prompt_name, version1)
        content2 = self.get_prompt_content(prompt_name, version2)
        
        if content1 is None or content2 is None:
            raise ValueError(f"One or both versions of prompt '{prompt_name}' not found")
        
        diff = difflib.unified_diff(
            content1.splitlines(),
            content2.splitlines(),
            fromfile=f"{prompt_name} v{version1}",
            tofile=f"{prompt_name} v{version2}",
            lineterm=""
        )
        
        return "\n".join(list(diff))
    
    def rollback_to_version(self, prompt_name: str, version: str) -> bool:
        """
        Rollback to a specific version of a prompt.
        
        Args:
            prompt_name: Name of the prompt
            version: Version to rollback to
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get version content
        content = self.get_prompt_content(prompt_name, version)
        
        if content is None:
            return False
        
        # Write content to base directory
        prompt_path = self.base_prompts_dir / f"{prompt_name}.txt"
        
        with open(prompt_path, "w") as f:
            f.write(content)
        
        return True
    
    def get_performance_history(self, prompt_name: str) -> Dict[str, Dict[str, float]]:
        """
        Get performance history for a prompt across versions.
        
        Args:
            prompt_name: Name of the prompt
            
        Returns:
            Dict[str, Dict[str, float]]: Dictionary mapping versions to performance metrics
        """
        if prompt_name not in self.prompt_metadata:
            return {}
        
        versions = self.prompt_metadata[prompt_name].get("versions", {})
        performance_history = {}
        
        for version, metadata in versions.items():
            metrics = metadata.get("performance_metrics", {})
            if metrics:
                performance_history[version] = metrics
        
        return performance_history
    
    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get a dependency graph of all prompts.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping prompts to their dependencies
        """
        dependency_graph = {}
        
        for prompt_name, metadata in self.prompt_metadata.items():
            latest_versions = sorted(metadata.get("versions", {}).keys(), 
                                   key=lambda v: semver.VersionInfo.parse(v))
            
            if not latest_versions:
                continue
                
            latest_version = latest_versions[-1]
            version_metadata = metadata["versions"].get(latest_version, {})
            dependencies = version_metadata.get("dependencies", [])
            
            dependency_graph[prompt_name] = dependencies
        
        return dependency_graph
    
    def version_all_unversioned_prompts(self, 
                                      author: str, 
                                      commit_message: str = "Initial versioning") -> List[str]:
        """
        Version all prompts in the base directory that don't have versions yet.
        
        Args:
            author: Author of the change
            commit_message: Message for the version
            
        Returns:
            List[str]: List of prompts that were versioned
        """
        # Get all prompts in base directory
        base_prompts = self.prompt_loader.get_available_prompts()
        
        # Get all versioned prompts
        versioned_prompts = self.get_all_prompt_versions()
        
        # Find prompts that don't have versions
        unversioned_prompts = [p for p in base_prompts if p not in versioned_prompts]
        
        # Version each prompt
        versioned = []
        for prompt_name in unversioned_prompts:
            self.create_new_version(
                prompt_name=prompt_name,
                author=author,
                change_type="minor",  # Use minor for initial versioning
                commit_message=commit_message
            )
            versioned.append(prompt_name)
        
        return versioned


def test_prompt_version_manager():
    """Test function for PromptVersionManager."""
    manager = PromptVersionManager()
    
    # Get available prompts
    loader = PromptLoader()
    available_prompts = loader.get_available_prompts()
    print(f"Available prompts: {available_prompts}")
    
    if not available_prompts:
        print("No prompts available for testing.")
        return
    
    # Use the first prompt for testing
    test_prompt = available_prompts[0]
    print(f"Using prompt '{test_prompt}' for testing.")
    
    # Check if prompt has changed
    has_changed, current_metadata = manager.check_for_changes(test_prompt)
    print(f"Prompt has changed: {has_changed}")
    
    # Create a new version
    version = manager.create_new_version(
        prompt_name=test_prompt,
        author="Claude",
        change_type="minor",
        commit_message="Test versioning"
    )
    print(f"Created new version: {version}")
    
    # Get all versions
    versions = manager.get_all_prompt_versions()
    print(f"All versions: {versions}")
    
    # Get metadata for latest version
    metadata = manager.get_prompt_metadata(test_prompt)
    print(f"Metadata for latest version: {metadata}")
    
    # Get content for latest version
    content = manager.get_prompt_content(test_prompt)
    print(f"Content preview: {content[:100]}...")


if __name__ == "__main__":
    test_prompt_version_manager()