# Help requests routes
from fastapi import APIRouter
from backend.services.help_request_service import HelpRequestService
from backend.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("/requests/pending")
def get_pending_requests():
    return HelpRequestService.get_pending()


@router.get("/requests/history")
def get_request_history():
    return HelpRequestService.get_history()


@router.post("/requests/resolve")
def resolve_request(request_id: str, answer: str):
    # Resolve the request in the DB
    HelpRequestService.resolve_request(request_id, answer)

    # Fetch the original help request to obtain the question text
    req = HelpRequestService.get_request(request_id)
    if req and "question" in req:
        KnowledgeService.save_answer(req["question"], answer)
        print(f"[AI AGENT] Follow-up sent: {answer}")

    return {"message": "Help request resolved"}
