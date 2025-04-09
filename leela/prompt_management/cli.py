"""
Command-line interface for prompt management.
"""
import argparse
import sys
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import yaml

from ..config import get_config
from .prompt_loader import PromptLoader
from .prompt_version_manager import PromptVersionManager
from .prompt_implementation_manager import PromptImplementationManager


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )


def create_parser():
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Prompt Management CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List prompts
    list_parser = subparsers.add_parser("list", help="List available prompts")
    list_parser.add_argument("--with-versions", action="store_true", help="Include versions")
    list_parser.add_argument("--with-metadata", action="store_true", help="Include metadata")
    list_parser.add_argument("--format", choices=["text", "json", "yaml"], default="text", help="Output format")
    
    # Validate implementations
    validate_parser = subparsers.add_parser("validate", help="Validate prompt implementations")
    validate_parser.add_argument("--with-stats", action="store_true", help="Include implementation statistics")
    validate_parser.add_argument("--format", choices=["text", "json", "yaml"], default="text", help="Output format")
    
    # Version prompt
    version_parser = subparsers.add_parser("version", help="Create a new version of a prompt")
    version_parser.add_argument("prompt_name", help="Name of the prompt")
    version_parser.add_argument("--author", required=True, help="Author of the change")
    version_parser.add_argument("--change-type", choices=["major", "minor", "patch"], default="patch", 
                             help="Type of change (default: patch)")
    version_parser.add_argument("--message", help="Commit message for the version")
    
    # Compare versions
    compare_parser = subparsers.add_parser("compare", help="Compare two versions of a prompt")
    compare_parser.add_argument("prompt_name", help="Name of the prompt")
    compare_parser.add_argument("version1", help="First version")
    compare_parser.add_argument("version2", help="Second version")
    
    # Rollback to version
    rollback_parser = subparsers.add_parser("rollback", help="Rollback to a specific version")
    rollback_parser.add_argument("prompt_name", help="Name of the prompt")
    rollback_parser.add_argument("version", help="Version to rollback to")
    
    # Version all unversioned prompts
    version_all_parser = subparsers.add_parser("version-all", help="Version all unversioned prompts")
    version_all_parser.add_argument("--author", required=True, help="Author of the changes")
    version_all_parser.add_argument("--message", default="Initial versioning", help="Commit message")
    
    return parser


def list_prompts(args):
    """List available prompts."""
    loader = PromptLoader()
    version_manager = PromptVersionManager()
    
    prompts = loader.get_available_prompts()
    
    result = {}
    
    for prompt_name in prompts:
        prompt_data = {"name": prompt_name}
        
        if args.with_versions:
            all_versions = version_manager.get_all_prompt_versions()
            versions = all_versions.get(prompt_name, [])
            prompt_data["versions"] = versions
        
        if args.with_metadata:
            metadata = version_manager.get_prompt_metadata(prompt_name)
            prompt_data["metadata"] = metadata
        
        result[prompt_name] = prompt_data
    
    # Output results based on format
    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "yaml":
        print(yaml.dump(result, default_flow_style=False))
    else:  # text format
        print(f"Found {len(prompts)} prompts:")
        for prompt_name, data in result.items():
            print(f"- {prompt_name}")
            
            if args.with_versions and "versions" in data:
                versions = data["versions"]
                if versions:
                    print(f"  Versions: {', '.join(versions)}")
                else:
                    print(f"  Versions: None")
            
            if args.with_metadata and "metadata" in data:
                metadata = data["metadata"]
                if metadata:
                    print(f"  Metadata:")
                    for key, value in metadata.items():
                        if isinstance(value, dict):
                            print(f"    {key}: <complex data>")
                        else:
                            print(f"    {key}: {value}")
                else:
                    print(f"  Metadata: None")
            
            print()


def validate_implementations(args):
    """Validate prompt implementations."""
    impl_manager = PromptImplementationManager()
    
    # Discover implementations
    impl_manager.discover_implementations()
    
    # Verify implementations
    issues = impl_manager.verify_implementations()
    
    # Get statistics if requested
    stats = impl_manager.get_implementation_stats() if args.with_stats else None
    
    # Create result data
    result = {
        "issues": issues,
    }
    
    if stats:
        result["stats"] = stats
    
    # Output results based on format
    if args.format == "json":
        print(json.dumps(result, indent=2))
    elif args.format == "yaml":
        print(yaml.dump(result, default_flow_style=False))
    else:  # text format
        print("Prompt Implementation Validation Results:")
        print("\nIssues:")
        
        for issue_type, affected_prompts in issues.items():
            print(f"- {issue_type}: {len(affected_prompts)}")
            if affected_prompts:
                for prompt in affected_prompts:
                    print(f"  - {prompt}")
        
        if stats:
            print("\nStatistics:")
            print(f"- Total prompts: {stats['total_prompts']}")
            print(f"- Implemented prompts: {stats['implemented_prompts']}")
            print(f"- Implementation percentage: {stats['implementation_percentage']:.1f}%")
            
            print("\n- Implementation types:")
            for impl_type, count in stats['implementation_types'].items():
                print(f"  - {impl_type}: {count}")
            
            print("\n- Dependency statistics:")
            dep_stats = stats['dependency_stats']
            print(f"  - Maximum dependencies: {dep_stats['max_dependencies']}")
            print(f"  - Average dependencies: {dep_stats['avg_dependencies']:.2f}")
            print(f"  - Total dependencies: {dep_stats['total_dependencies']}")


def version_prompt(args):
    """Create a new version of a prompt."""
    version_manager = PromptVersionManager()
    
    try:
        new_version = version_manager.create_new_version(
            prompt_name=args.prompt_name,
            author=args.author,
            change_type=args.change_type,
            commit_message=args.message
        )
        
        print(f"Created new version {new_version} for prompt '{args.prompt_name}'")
    except Exception as e:
        print(f"Error creating version: {e}")
        sys.exit(1)


def compare_versions(args):
    """Compare two versions of a prompt."""
    version_manager = PromptVersionManager()
    
    try:
        diff = version_manager.compare_versions(
            prompt_name=args.prompt_name,
            version1=args.version1,
            version2=args.version2
        )
        
        print(f"Differences between {args.prompt_name} v{args.version1} and v{args.version2}:")
        print(diff)
    except Exception as e:
        print(f"Error comparing versions: {e}")
        sys.exit(1)


def rollback_to_version(args):
    """Rollback to a specific version of a prompt."""
    version_manager = PromptVersionManager()
    
    try:
        success = version_manager.rollback_to_version(
            prompt_name=args.prompt_name,
            version=args.version
        )
        
        if success:
            print(f"Successfully rolled back {args.prompt_name} to version {args.version}")
        else:
            print(f"Failed to rollback {args.prompt_name} to version {args.version}")
            sys.exit(1)
    except Exception as e:
        print(f"Error rolling back: {e}")
        sys.exit(1)


def version_all_prompts(args):
    """Version all unversioned prompts."""
    version_manager = PromptVersionManager()
    
    try:
        versioned_prompts = version_manager.version_all_unversioned_prompts(
            author=args.author,
            commit_message=args.message
        )
        
        if versioned_prompts:
            print(f"Versioned {len(versioned_prompts)} prompts:")
            for prompt in versioned_prompts:
                print(f"- {prompt}")
        else:
            print("No unversioned prompts found")
    except Exception as e:
        print(f"Error versioning prompts: {e}")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    setup_logging()
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "list":
        list_prompts(args)
    elif args.command == "validate":
        validate_implementations(args)
    elif args.command == "version":
        version_prompt(args)
    elif args.command == "compare":
        compare_versions(args)
    elif args.command == "rollback":
        rollback_to_version(args)
    elif args.command == "version-all":
        version_all_prompts(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()