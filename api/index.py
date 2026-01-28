"""
Vercel Serverless Entry Point for FastAPI

Vercel's Python runtime expects a callable function named 'handler'.
Mangum bridges FastAPI (ASGI) with AWS Lambda/Vercel serverless.
"""
import sys
import os

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mangum import Mangum
from router import app

# Create Mangum adapter (reusable across invocations)
_mangum_handler = Mangum(app, lifespan="off")


def handler(event, context):
    """
    Vercel serverless function entry point.
    
    Vercel expects a function (not an instance), so we wrap Mangum.
    This avoids the issubclass() TypeError that occurs when exporting
    a Mangum instance directly.
    """
    return _mangum_handler(event, context)
