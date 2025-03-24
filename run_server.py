#!/usr/bin/env python
"""
Script to run the Project Leela API server.
"""
import os
import argparse
from leela.api.fastapi_app import run_app


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run the Project Leela API server")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to run on")
    args = parser.parse_args()
    
    if args.port:
        os.environ["PORT"] = str(args.port)
    
    print(f"Starting Leela API server on port {args.port}...")
    run_app()


if __name__ == "__main__":
    main()