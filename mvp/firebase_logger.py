import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")

cred = credentials.Certificate(KEY_PATH)
firebase_admin.initialize_app(cred)

db = firestore.client()

def log_event(data):
    data["timestamp"] = datetime.utcnow()
    data["event_id"] = str(uuid.uuid4())
    db.collection("events").add(data)

