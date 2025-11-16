# Firestore database configuration
import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to credentials file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CRED_PATH = os.path.join(BASE_DIR, "..", "firebase_credentials.json")

# Normalize path for Windows
CRED_PATH = os.path.normpath(CRED_PATH)

# Initialize app if not already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate(CRED_PATH)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()
