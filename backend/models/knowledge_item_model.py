# Knowledge item model
from pydantic import BaseModel
from datetime import datetime

class KnowledgeItem(BaseModel):
    question: str
    answer: str
    created_at: datetime
    updated_at: datetime

