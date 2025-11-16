from fastapi import APIRouter
from backend.services.help_request_service import HelpRequestService
from backend.services.knowledge_service import KnowledgeService
import uuid

router = APIRouter()


@router.get("/ask")
def ask_agent(caller_id: str, question: str):

    # 1. Check knowledge base first
    answer = KnowledgeService.find_answer(question)

    if answer:
        return {
            "response": answer,
            "from": "ai",
            "status": "answered"
        }

    # 2. Unknown → escalate to human
    request_id = str(uuid.uuid4())
    HelpRequestService.create_help_request(request_id, caller_id, question)

    print(f"[SUPERVISOR ALERT] Need help answering: {question}")

    return {
        "response": "Let me check with my supervisor and get back to you.",
        "from": "ai",
        "status": "escalated",
        "request_id": request_id
    }
