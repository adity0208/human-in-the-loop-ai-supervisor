# Knowledge service
from backend.database.firestore import db
from datetime import datetime


class KnowledgeService:

    @staticmethod
    def find_answer(question: str):
        docs = db.collection("knowledge_base").stream()
        for doc in docs:
            data = doc.to_dict()
            if data["question"].lower() == question.lower():
                return data["answer"]
        return None

    @staticmethod
    def save_answer(question: str, answer: str):
        db.collection("knowledge_base").add({
            "question": question,
            "answer": answer,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        })

    @staticmethod
    def get_all():
        return [doc.to_dict() for doc in db.collection("knowledge_base").stream()]
