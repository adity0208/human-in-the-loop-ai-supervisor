# Main application entry point
from fastapi import FastAPI
from backend.routes.help_requests import router as help_requests_router
from backend.routes.knowledge_base import router as kb_router
from backend.routes.agent import router as agent_router
from backend.routes.livekit_token import router as livekit_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Human-in-the-Loop AI Supervisor",
    description="Backend for Frontdesk coding assessment",
    version="1.0.0"
)

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(help_requests_router, prefix="/help")
app.include_router(kb_router, prefix="/kb")
app.include_router(agent_router, prefix="/agent")
app.include_router(livekit_router)


@app.get("/")
def index():
    return {"message": "Backend running successfully!"}
