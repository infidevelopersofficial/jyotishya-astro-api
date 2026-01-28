"""
Vercel Serverless Entry Point for FastAPI

Vercel's Python runtime expects a callable 'handler' that wraps the ASGI app.
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

# Mangum handler - this is the ASGI adapter for serverless
# Vercel will invoke this as the entry point
handler = Mangum(app, lifespan="off")

# Also expose the app directly for local testing
application = app
