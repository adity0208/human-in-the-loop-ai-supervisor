# Knowledge base routes
from fastapi import APIRouter
from backend.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("/all")
def get_all_learned():
    docs = KnowledgeService.get_all()
    return docs
