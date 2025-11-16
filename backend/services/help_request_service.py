# Help request service
from backend.database.firestore import db
from datetime import datetime


class HelpRequestService:

    @staticmethod
    def create_help_request(request_id, caller_id, question):
        db.collection("help_requests").document(request_id).set({
            "request_id": request_id,
            "caller_id": caller_id,
            "question": question,
            "status": "pending",
            "supervisor_answer": None,
            "created_at": datetime.utcnow(),
            "resolved_at": None
        })

    @staticmethod
    def resolve_request(request_id, answer):
        db.collection("help_requests").document(request_id).update({
            "status": "resolved",
            "supervisor_answer": answer,
            "resolved_at": datetime.utcnow()
        })

    @staticmethod
    def get_request(request_id):
        doc = db.collection("help_requests").document(request_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    @staticmethod
    def get_pending():
        return [doc.to_dict() for doc in db.collection("help_requests")
                .where("status", "==", "pending")
                .stream()]

    @staticmethod
    def get_history():
        return [doc.to_dict() for doc in db.collection("help_requests").stream()]
