"""
Vercel Serverless Entry Point for FastAPI

Vercel has native ASGI support - no Mangum wrapper needed.
Just export the FastAPI app directly.
"""
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from router import app

# Vercel automatically detects and handles ASGI apps
# Export as 'app' for ASGI detection
