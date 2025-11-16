"""
ASGI handler for Vercel serverless deployment
Routes all requests through FastAPI app
"""
from backend.main import app

# Vercel calls this handler


async def handler(request):
    return app(request)
