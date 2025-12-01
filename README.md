
### **AI Agent**

* Receives a query from a caller (simulated via `/agent/ask`).
* If the answer exists in the Knowledge Base (KB), it responds immediately.
* If not, it:

  * Tells the caller *“Let me check with my supervisor.”*
  * Creates a **help request**.
  * Notifies the supervisor (console alert).

---

### **Supervisor Dashboard (Frontend UI)**

A simple, clean Bootstrap UI:

* **Pending Requests**
  View escalated customer questions waiting for human review.

* **Resolve Request**
  Provide the correct answer → AI follows up with the caller instantly.

* **Request History**
  All previous queries with timestamps and supervisor answers.

* **Knowledge Base**
  View all learned question–answer pairs used by the AI agent.

---

### **Knowledge Base**

* Stores learned answers.
* Automatically updates after supervisor resolves a request.
* Agent immediately uses newly learned answers for future calls.

---

## 🏗 **Architecture Overview**

```
backend/
 ├─ main.py                # FastAPI app
 ├─ routes/
 │    ├─ agent.py          # AI agent simulation endpoints
 │    ├─ help_requests.py  # Supervisor actions
 │    └─ knowledge_base.py # Knowledge base endpoints
 ├─ services/
 │    ├─ help_request_service.py
 │    └─ knowledge_service.py
 ├─ database/
 │    └─ firestore.py      # Firebase initialization
frontend/
 ├─ index.html             # Dashboard home
 ├─ pending.html
 ├─ resolve.html
 ├─ history.html
 ├─ kb.html
 └─ style.css
```

---

## 🛠 **Tech Stack**

### **Backend**

* Python
* FastAPI
* Firestore (Firebase)

### **Frontend**

* HTML
* Bootstrap
* Vanilla JS (fetch API)

---

## 🚀 **How to Run the Project**

### **1. Clone Repository**

```bash
git clone https://github.com/adity0208/human-in-the-loop-ai-supervisor.git
cd human-in-the-loop-ai-supervisor
```

---

### **2. Create Virtual Environment**

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

---

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

---

### **4. Add Firebase Credentials**

Place your Firebase Admin SDK JSON file here:

```
backend/firebase_credentials.json
```

Firestore must be in **Production Mode**.

Enable required APIs:

* Firestore API
* Identity Toolkit API

---

### **5. Run Backend Server**

```bash
uvicorn backend.main:app --reload
```

Backend will start at:

```
http://127.0.0.1:8000
```

---

### **6. Run Frontend**

You can use VSCode Live Server or Python:

**Using Python**

```bash
cd frontend
python -m http.server 5500
```

Frontend opens at:

```
http://127.0.0.1:5500/index.html
```

---

## 🔄 **How the Workflow Looks (End-to-End)**

### **1️⃣ Caller asks a question**

```
GET /agent/ask?caller_id=customer1&question=What are your salon hours?
```

### **2️⃣ AI cannot answer → escalates**

* Creates help request
* Logs supervisor alert
* Returns request_id

### **3️⃣ Supervisor opens Pending Requests**

UI shows the escalated question.

### **4️⃣ Supervisor resolves**

Supervisor types correct answer → AI sends follow-up response.

### **5️⃣ Knowledge Base updates**

The resolved question/answer is stored permanently.

### **6️⃣ Caller asks again**

AI instantly answers using the KB.

**FULL WORKFLOW: PASSED ✔**

---

## 🧪 **Testing**

Run these endpoints in order to validate:

1. `/agent/ask`
2. `/help/requests/pending`
3. `/help/requests/resolve`
4. `/help/requests/history`
5. `/kb/all`

All endpoints are functional and tested.

---

## 📌 **Design Considerations**

* Clear separation between **agent logic**, **help request logic**, and **knowledge base service**.
* Firestore chosen for ease of setup and document-based structure.
* Simple, clean, professional supervisor UI.
* Fully functional state transitions:
  `pending → resolved → learned → reusable`

---

## 📈 **Possible Improvements**

(Optional features if needed)

* Supervisor login page
* Dark/light theme toggle
* Search/filter in history
* Pagination
* Automated tests in CI
* Real SMS/Whatsapp integration via Twilio
* Actual LiveKit voice agent integration

---

## 🎉 **Project Completed**

This implementation fully matches the expected assessment requirements:

* Agent behavior ✔
* Escalation ✔
* Supervisor UI ✔
* Knowledge base ✔
* Learning loop ✔

---
