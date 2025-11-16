# Help request model
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HelpRequest(BaseModel):
    request_id: str
    caller_id: str
    question: str
    status: str  # pending | resolved | timeout
    supervisor_answer: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None

