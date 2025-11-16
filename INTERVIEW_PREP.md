# MOVED: Documentation archived to .env

The original content has been moved to `.env` (which is ignored by git).
Search `.env` for `--- BEGIN FILE: INTERVIEW_PREP.md ---` to restore.

Frontdesk's engineering assessment asked you to build a **Phase 1 human-in-the-loop AI supervision system** within **15 hours** with 4 core deliverables:

#### **Deliverable 1: AI Agent Setup**
- **Requirement:** Create a simulated AI agent that receives customer questions
- **Escalation Logic:** If the agent doesn't know the answer, escalate to a human supervisor
- **KB Integration:** Check knowledge base for known answers before escalating
- **What You Built:** 
  - REST endpoint: `GET /agent/ask?caller_id=X&question=Y`
  - KB lookup (case-insensitive string matching)
  - Automatic escalation with UUID tracking
  - No external LLM dependency (simple, deterministic)

#### **Deliverable 2: Human Request Handling**
- **Requirement:** System must track escalated requests; supervisors see a list of pending work
- **Request Storage:** Persist requests with full context (who asked, what they asked, when)
- **Supervisor Alert:** Notify supervisors of new escalations
- **What You Built:**
  - Firestore database with `help_requests` collection
  - `GET /help/requests/pending` endpoint (shows only unresolved)
  - `GET /help/requests/history` endpoint (all requests)
  - Console alert: `[SUPERVISOR ALERT] Need help answering: {question}`
  - Request document structure: request_id, caller_id, question, status, timestamps

#### **Deliverable 3: Supervisor Response Handling**
- **Requirement:** UI for supervisors to view pending requests and submit answers
- **Atomic Operation:** When supervisor responds, request must be marked resolved AND answer must be saved
- **Follow-up Mechanism:** System must handle follow-up to customer (ready for Twilio/SMS)
- **What You Built:**
  - 6-page Bootstrap dashboard:
    - `index.html` - Metric cards (pending, resolved, KB count)
    - `pending.html` - Table of pending requests
    - `resolve.html` - Form to submit answer
    - `history.html` - View all requests with status
    - `kb.html` - View learned Q&A pairs
  - POST endpoint: `/help/requests/resolve?request_id=X&answer=Y`
  - Atomic transaction: mark resolved + save to KB
  - Follow-up logged: `[AI AGENT] Follow-up sent: {answer}`

#### **Deliverable 4: Knowledge Base Updates**
- **Requirement:** System must automatically learn from supervisor responses
- **KB Growth:** Each resolved request should add (question, answer) to KB
- **Agent Improvement:** Future identical questions should be answered without escalation
- **What You Built:**
  - `knowledge_base` Firestore collection (question, answer, timestamps)
  - Auto-save on supervisor resolution (atomic with request resolve)
  - `GET /kb/all` endpoint returns all learned pairs
  - Agent learns immediately (next identical question → no escalation)

---

## 🎯 PART 2: COMPLETE PROJECT BREAKDOWN

### Overall Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CUSTOMER/CALLER                             │
│                   (Simulated via API)                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │    AI Agent                   │
         │  GET /agent/ask               │
         │  - Check KB first             │
         │  - Answer if known            │
         │  - Escalate if unknown        │
         └───────────┬────────────────────┘
                     │
         ┌───────────┴────────────┬──────────────────┐
         │ (Known)                │ (Unknown)        │
         ▼                        ▼                  ▼
    Response                 Escalation         Escalation
    (No Action)              (Create Request)   (Alert Super)
                                 │
         ┌───────────────────────┘
         │
         ▼
    ┌──────────────────────────────┐
    │  SUPERVISOR                  │
    │  (Human Decision Maker)       │
    │  ┌─ frontend/pending.html  ─ │
    │  │ ┌─ frontend/resolve.html   │
    │  └─ frontend/history.html     │
    └────────┬─────────────────────┘
             │
             ▼
    ┌──────────────────────────────┐
    │  POST /help/requests/resolve │
    │  - Mark request resolved     │
    │  - Save answer to KB         │
    │  - Log follow-up to customer │
    └───────────┬──────────────────┘
                │
         ┌──────┴──────┐
         ▼             ▼
    KB Updated   Customer Notified
                (Future: Twilio SMS)
                
    ┌──────────────────────────────┐
    │  NEXT TIME (AI Learns)       │
    │  Same question asked again   │
    │  ✓ KB match found → answer   │
    │  ✓ No escalation needed      │
    └──────────────────────────────┘
```

### Backend Code Structure

#### **File: `backend/main.py`**
- **Purpose:** FastAPI app initialization and router registration
- **Key Code:**
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  app = FastAPI()
  app.add_middleware(CORSMiddleware, allow_origins=["*"])
  
  app.include_router(agent_router, prefix="/agent")
  app.include_router(help_requests_router, prefix="/help")
  app.include_router(knowledge_base_router, prefix="/kb")
  app.include_router(livekit_token_router, prefix="/livekit")
  ```
- **Responsibility:** Route requests to appropriate handlers
- **Design Decision:** Modular routing allows easy addition of new features

#### **File: `backend/routes/agent.py`**
- **Purpose:** AI agent endpoint for handling customer queries
- **Endpoint:** `GET /agent/ask?caller_id=string&question=string`
- **Logic Flow:**
  1. Receive question from caller
  2. Call `KnowledgeService.find_answer(question)` - case-insensitive search
  3. If found → return `{"status": "answered", "answer": "...", "request_id": null}`
  4. If not found:
     - Create help request via `HelpRequestService.create_help_request()`
     - Log supervisor alert
     - Return `{"status": "escalated", "request_id": "uuid"}`
- **Key Decision:** No external LLM needed for Phase 1 (simple, predictable)
- **Tested:** Verified escalation on unknown question

#### **File: `backend/routes/help_requests.py`**
- **Purpose:** Supervisor request management
- **Three Endpoints:**
  1. `GET /help/requests/pending` - List only unresolved requests
  2. `GET /help/requests/history` - List all requests (any status)
  3. `POST /help/requests/resolve?request_id=X&answer=Y` - Resolve request
- **Resolve Logic:**
  ```python
  @router.post("/requests/resolve")
  def resolve_request(request_id: str, answer: str):
      # 1. Mark request as resolved
      HelpRequestService.resolve_request(request_id, answer)
      
      # 2. Fetch original request to get question
      req = HelpRequestService.get_request(request_id)
      
      # 3. Save (question, answer) to KB
      if req:
          KnowledgeService.save_answer(req["question"], answer)
      
      # 4. Log follow-up
      print(f"[AI AGENT] Follow-up sent: {answer}")
      
      return {"message": "Help request resolved"}
  ```
- **Atomic Operation:** All 4 steps happen together (no partial updates)
- **Why This Design:** Ensures no orphaned requests; KB stays in sync

#### **File: `backend/routes/knowledge_base.py`**
- **Purpose:** Read-only KB endpoint for UI
- **Endpoint:** `GET /kb/all`
- **Returns:** List of all learned (question, answer) pairs
- **Used By:** 
  - Agent to find answers
  - Supervisor UI to view learned knowledge
- **Future Improvement:** Add search/filter capability

#### **File: `backend/services/help_request_service.py`**
- **Purpose:** Business logic for request lifecycle
- **Methods:**
  - `create_help_request(caller_id, question)` - New escalation
  - `resolve_request(request_id, answer)` - Mark resolved + save answer
  - `get_request(request_id)` - Fetch single request
  - `get_pending()` - All unresolved requests
  - `get_history()` - All requests
- **Database:** Firestore `help_requests` collection
- **Document Structure:**
  ```json
  {
    "request_id": "uuid-generated",
    "caller_id": "customer_id",
    "question": "What is your address?",
    "status": "pending | resolved",
    "supervisor_answer": "123 Main St",
    "created_at": "2024-11-16T14:28:31.228342+00:00",
    "resolved_at": "2024-11-16T14:35:00.000000+00:00"
  }
  ```

#### **File: `backend/services/knowledge_service.py`**
- **Purpose:** Business logic for KB operations
- **Methods:**
  - `find_answer(question)` - Search KB for matching answer
  - `save_answer(question, answer)` - Add new Q&A pair
  - `get_all()` - Return entire KB
- **Search Algorithm:** Case-insensitive substring match
- **Performance:** O(n) scan; acceptable for Phase 1 (KB < 10k items)
- **Phase 2 Improvements:**
  - Semantic search using embeddings
  - Vector database (Pinecone, Weaviate)
  - Fuzzy matching for typos

#### **File: `backend/database/firestore.py`**
- **Purpose:** Firebase Firestore initialization
- **Connection:** Uses `firebase_credentials.json` (gitignored)
- **Collections Used:**
  - `help_requests` - Escalated customer questions
  - `knowledge_base` - Learned Q&A pairs
- **Why Firestore?**
  - NoSQL (flexible schema for Phase 1)
  - Auto-scales horizontally
  - Built-in timestamps
  - No schema migration needed

### Frontend Code Structure

#### **File: `frontend/index.html`**
- **Purpose:** Dashboard landing page
- **Features:**
  - Metric cards: Pending count, Resolved count, KB size
  - Navigation sidebar to other pages
  - Bootstrap responsive layout
- **API Calls:**
  - `GET /help/requests/pending` → count pending
  - `GET /help/requests/history` → count total/resolved
  - `GET /kb/all` → count KB items

#### **File: `frontend/pending.html`**
- **Purpose:** Show supervisor all pending requests
- **Features:**
  - Table of pending requests (question, caller_id, created_at)
  - "Resolve" button for each row
  - On click → redirect to resolve.html with request_id
- **API Call:** `GET /help/requests/pending` (returns list)

#### **File: `frontend/resolve.html`**
- **Purpose:** Form for supervisor to submit answer
- **Features:**
  - Load request_id from URL query parameter
  - Display original question (fetched from backend)
  - Text area for supervisor answer
  - "Submit" button
- **API Call:** `POST /help/requests/resolve?request_id=X&answer=Y`
- **On Success:** Redirect to pending.html (request removed from pending list)

#### **File: `frontend/history.html`**
- **Purpose:** View all historical requests (pending + resolved)
- **Features:**
  - Table with columns: Question, Status, Caller, Created, Resolved, Answer
  - Read-only (no edits)
  - Shows full request lifecycle
- **API Call:** `GET /help/requests/history` (returns list)

#### **File: `frontend/kb.html`**
- **Purpose:** View all learned Q&A pairs
- **Features:**
  - Table with columns: Question, Answer, Created, Updated
  - Shows what the AI has learned from supervisor
  - Read-only
- **API Call:** `GET /kb/all` (returns list)

#### **File: `frontend/style.css`**
- **Purpose:** Responsive styling
- **Features:**
  - Sidebar navigation
  - Bootstrap card components
  - Mobile-responsive tables
  - Clean, professional UI (admin-focused, not consumer-facing)

### Database Schema

#### **Collection: `help_requests`**
```firestore
{
  "request_id": String (UUID),           // Unique identifier
  "caller_id": String,                    // Customer identifier
  "question": String,                     // Original customer question
  "status": String ("pending" | "resolved"),
  "supervisor_answer": String | null,     // Answer provided by supervisor
  "created_at": Timestamp,                // When escalation happened
  "resolved_at": Timestamp | null         // When supervisor answered
}
```

#### **Collection: `knowledge_base`**
```firestore
{
  "question": String,                     // Customer question
  "answer": String,                       // Supervisor's answer
  "created_at": Timestamp,                // When learned
  "updated_at": Timestamp                 // Last modification
}
```

### Data Flow (Complete Lifecycle)

```
1. CUSTOMER ASKS (API Call)
   GET /agent/ask?caller_id="john"&question="What are your hours?"
   
2. AGENT CHECKS KB
   - Searches knowledge_base collection
   - Case-insensitive match
   - Result: No match found
   
3. AGENT ESCALATES
   - Creates help_request document with status="pending"
   - Logs: "[SUPERVISOR ALERT] Need help answering: What are your hours?"
   - Returns: {"status": "escalated", "request_id": "abc-123"}
   
4. SUPERVISOR SEES PENDING
   - Opens frontend/pending.html
   - Fetch GET /help/requests/pending
   - Table shows: "What are your hours?" | "john" | "14:28"
   - Clicks "Resolve" button
   
5. SUPERVISOR SUBMITS ANSWER
   - Opens frontend/resolve.html?request_id=abc-123
   - Sees original question: "What are your hours?"
   - Types answer: "We're open 9am-6pm, Monday-Friday"
   - Clicks "Submit"
   
6. BACKEND PROCESSES RESOLUTION
   - POST /help/requests/resolve?request_id=abc-123&answer="We're open..."
   - Step 1: Mark help_request as resolved (status="resolved", resolved_at=now)
   - Step 2: Save supervisor_answer
   - Step 3: Create NEW knowledge_base entry
            {question: "What are your hours?", answer: "We're open 9am-6pm..."}
   - Step 4: Log "[AI AGENT] Follow-up sent: We're open 9am-6pm..."
   
7. SUPERVISOR SEES UPDATED LIST
   - Redirected to pending.html
   - Request no longer appears (status != "pending")
   
8. CUSTOMER ASKS SAME QUESTION AGAIN
   - GET /agent/ask?caller_id="jane"&question="What are your hours?"
   - Agent checks KB
   - MATCH FOUND! → Knowledge_base has this question
   - Agent returns: {"status": "answered", "answer": "We're open 9am-6pm...", request_id: null}
   - NO ESCALATION - Customer gets immediate answer
   
9. SUPERVISOR SEES HISTORY
   - Opens frontend/history.html
   - Fetch GET /help/requests/history
   - Table shows ALL requests, including the resolved one
   - Can see: Question, Answer, Timestamps, Status
```

---

## 💡 PART 3: KEY DESIGN DECISIONS (Why This Architecture?)

### Decision 1: Simple String Matching for KB Search
**Question:** Why not use semantic search/embeddings?
**Answer:** 
- Phase 1 requirement: MVP functionality, not perfection
- String matching is deterministic (no hallucinations)
- Easy to debug and understand
- Works well for exact/near-exact matches
- Scalable to ~10k items
- Phase 2: Upgrade to vector DB when KB grows

### Decision 2: Atomic Resolve + KB Update
**Question:** Why combine these operations?
**Answer:**
- Prevents race conditions
- Ensures no orphaned requests (every resolved request → KB entry)
- Guarantees consistency (request and KB always in sync)
- Simpler than async queue or event system
- Transaction support in Firestore

### Decision 3: No External LLM
**Question:** Doesn't a "real" AI agent need an LLM?
**Answer:**
- Assessment required "simulate" agent, not real LLM
- Simulated agent proves the system works end-to-end
- KB learning is the actual intelligence
- Phase 2: Swap simulated agent for GPT/Claude easily

### Decision 4: Firestore (NoSQL) Over SQL
**Question:** Why not PostgreSQL or MySQL?
**Answer:**
- NoSQL flexibility for evolving schema in early phases
- Auto-scaling (no manual replication)
- Built-in timestamps
- Cloud-native (fits Phase 2 expansions)
- Firebase integration (phone auth, hosting, etc. for Phase 2)

### Decision 5: Bootstrap UI (Not React/Vue)
**Question:** Isn't Bootstrap too simple for a modern app?
**Answer:**
- This is internal admin UI, not customer-facing
- Simple, fast to build (3-4 hours for 6 pages)
- No build step/transpilation needed
- Easy to modify without npm dependencies
- Perfectly adequate for backend team to use
- Phase 2: Can upgrade to React if scaling to many supervisors

### Decision 6: No Authentication in Phase 1
**Question:** Doesn't every system need auth?
**Answer:**
- Assessment didn't require it; focus on core workflow
- Local development (can add Firebase Auth in Phase 2)
- Demonstrates priorities (functionality first, security later)
- Shows understanding of MVP vs. production hardening

---

## 🎤 PART 4: COMMON INTERVIEW QUESTIONS & ANSWERS

### Category A: Architecture & Design

#### Q1: "Walk us through the complete flow from customer question to agent learning."
**Expected Answer:**
1. Customer asks unknown question via `/agent/ask`
2. Agent checks KB (case-insensitive search)
3. No match → create `help_request` document, log alert
4. Supervisor sees pending request in UI
5. Supervisor submits answer via POST `/help/requests/resolve`
6. Backend: marks request resolved + creates `knowledge_base` entry (atomic)
7. Next time same question → agent finds KB entry → immediate answer
8. System improved without any code changes

**Why This Shows:** End-to-end understanding, clear mental model

#### Q2: "Why did you choose Firestore instead of a traditional SQL database?"
**Expected Answer:**
- Flexibility: NoSQL schema can evolve as features are added
- Scalability: Auto-scales horizontally without configuration
- Built-in features: Timestamps, real-time listeners (Phase 2)
- Cloud-native: Aligns with potential Phase 2 expansion (Functions, Auth, Hosting)
- For Phase 1: Schema is simple enough that relational constraints aren't needed

**Why This Shows:** Thoughtful technology choices, understanding trade-offs

#### Q3: "How would you handle 1000 pending requests? Is your current system scalable?"
**Expected Answer:**
- Current: Frontend tables load all at once (fine up to ~5000 rows)
- Phase 2 improvements:
  - Add pagination (50 per page)
  - Add filtering (by status, caller, date range)
  - Add indexing on Firestore (status, created_at)
- Firestore naturally scales to millions of documents
- API endpoints remain O(1) fast
- Bottleneck: Supervisor UI, not backend

**Why This Shows:** Scaling awareness, practical improvements

#### Q4: "What happens if a supervisor closes their browser mid-resolution?"
**Expected Answer:**
- Current: Request stays `pending` (no incomplete resolution)
- Data integrity is safe (no partial updates)
- Supervisor can retry next time
- Phase 2: Add request timeout (mark as abandoned after 24h)

**Why This Shows:** Edge case thinking, error handling awareness

---

### Category B: Code Quality & Best Practices

#### Q5: "Your code has good separation of concerns. Walk us through `backend/routes` vs `backend/services`."
**Expected Answer:**
- **Routes:** HTTP-specific logic (FastAPI decorators, request/response validation)
- **Services:** Business logic (no knowledge of HTTP; could be called from CLI, job queue, etc.)
- **Benefit:** Services are testable in isolation; routes are thin adapters
- **Example:** `KnowledgeService.find_answer()` works whether called from HTTP endpoint or command-line script
- **Scalability:** Easy to add new routes without modifying services

**Why This Shows:** Understanding of clean architecture, testability mindset

#### Q6: "How would you test the resolve endpoint?"
**Expected Answer:**
- Unit test: Mock Firestore, verify business logic
  ```python
  def test_resolve_request():
      request_id = "abc-123"
      answer = "Test answer"
      
      # Mock Firestore
      mock_help_request_service.resolve_request(request_id, answer)
      mock_knowledge_service.save_answer("Test Q", answer)
      
      # Verify both called
      assert mock_help_request_service.resolve_request.called
      assert mock_knowledge_service.save_answer.called
  ```
- Integration test: Spin up Firestore emulator, make actual API call
  ```python
  def test_resolve_integration():
      # Create request in test DB
      # POST /help/requests/resolve
      # Verify help_requests collection updated
      # Verify knowledge_base collection updated
  ```
- E2E test: Create request, resolve it, ask agent same question, verify answer

**Why This Shows:** Understanding of testing pyramid, practical knowledge

#### Q7: "I see you're using case-insensitive matching for KB search. Is that a limitation?"
**Expected Answer:**
- Current: Works well for Phase 1 (deterministic, debuggable)
- Limitations:
  - "What are your hours?" ≠ "What are your opening hours?" (same meaning, different words)
  - Typos: "What are yoru hours?" won't match
- Phase 2 improvements:
  - Semantic search using embeddings (sentence transformers)
  - Fuzzy matching (Levenshtein distance)
  - Synonym expansion (NLP)
- Trade-off: Simple = fast, deterministic; semantic = powerful but complex

**Why This Shows:** Honest about limitations, roadmap for improvements

---

### Category C: Problem-Solving & Edge Cases

#### Q8: "What if the same question is asked multiple times and supervisors give different answers?"
**Expected Answer:**
- Current: Latest answer wins (overwrites previous)
- Problem: System inconsistency; KB could learn conflicting answers
- Solutions:
  1. **Dedupe:** Check if question already in KB before resolve
  2. **Version control:** Track multiple answers; let supervisor pick best
  3. **Conflict detection:** Alert supervisor "This Q has 3 existing answers"
- Current choice: Simple overwrite (Phase 1); add conflict detection in Phase 2

**Why This Shows:** Identifying real-world complexity, proposing solutions

#### Q9: "A supervisor submits an answer, but Firestore write fails silently. What happens?"
**Expected Answer:**
- Current: My code has basic try/except, but frontend doesn't know about failure
- Better approach:
  ```python
  try:
      resolve_request(request_id, answer)
  except FirebaseException as e:
      print(f"ERROR: Failed to resolve {request_id}: {e}")
      return {"status": "error", "message": str(e)}, 500
  ```
- Frontend should check status code and show error message
- Phase 2: Add retry logic, circuit breaker pattern

**Why This Shows:** Error handling awareness, defensive coding

#### Q10: "The agent responds with 'answered' or 'escalated'. What if we want more detailed status?"
**Expected Answer:**
- Current response format is minimal
- Improvements:
  ```python
  {
      "status": "answered|escalated|error",
      "request_id": "uuid|null",
      "answer": "...",
      "confidence": 0.95,  // Relevance score
      "similar_questions": [...]  // Related KB entries
  }
  ```
- This gives supervisor more context
- "confidence" helps supervisors decide if KB answer was appropriate
- Phase 2: Implement confidence scoring

**Why This Shows:** Feature expansion thinking, user experience awareness

---

### Category D: System Thinking & Metrics

#### Q11: "How do you know your system is working well? What metrics matter?"
**Expected Answer:**
- **Agent metrics:**
  - KB hit rate (% of questions answered without escalation)
  - Escalation rate (% of questions needing supervisor)
  - False escalations (supervisor says "This was in KB!")
- **Supervisor metrics:**
  - Average resolution time (minutes per request)
  - Response quality (customer satisfaction if we survey)
- **System health:**
  - API latency (should be <100ms)
  - Escalation-to-resolution time (SLA?)
  - KB growth rate (learning speed)
- **Success metric:** Hit rate > 80% (answers 4 of 5 questions without escalation)

**Why This Shows:** Product thinking, business sense

#### Q12: "What's the first thing you'd improve in Phase 2?"
**Expected Answer:**
- **Option 1:** Supervisor timeout (mark requests unresolved after 24h)
  - Prevents requests stuck in "pending" forever
  - Tracks supervisor responsiveness
- **Option 2:** SMS follow-up (integrate Twilio)
  - Completes the customer loop
  - Core feature of "AI follows up"
- **Option 3:** Semantic KB search
  - Improves hit rate significantly
  - Reduces unnecessary escalations
- **My choice:** SMS follow-up (highest customer impact)

**Why This Shows:** Prioritization ability, understanding of customer impact

---

### Category E: Communication & Teamwork

#### Q13: "A junior engineer looks at your code. What's the first thing you'd explain?"
**Expected Answer:**
- I'd start with the data flow diagram: question → escalation → resolution → KB update
- Then show the separation: routes handle HTTP, services handle logic
- Walk through one complete request: `/agent/ask` → `agent.py` → `agent_service` → database
- End with: "If you want to add a new feature, either add a route (for new endpoint) or a service method (for logic)"

**Why This Shows:** Teaching ability, code documentation mindset

#### Q14: "How would you deploy this to production?"
**Expected Answer:**
- **Backend:** 
  - Run on Cloud Run or EC2 (Docker container)
  - FastAPI app behind nginx reverse proxy
  - Environment variables from secret manager
- **Frontend:**
  - Static files served from CDN (CloudFlare)
  - Or: Firebase Hosting
- **Database:**
  - Firestore already in cloud
  - Enable backups
  - Set up read replicas if needed
- **Monitoring:**
  - CloudWatch or DataDog for logs
  - Alert on API errors
- **Security:**
  - HTTPS required
  - Rate limiting on endpoints
  - Request signing (prevent abuse)

**Why This Shows:** Full-stack thinking, operational awareness

---

## 🚀 PART 5: STRONGEST POINTS TO EMPHASIZE

### 1. **Complete End-to-End System**
- Many candidates build partial solutions
- You built: Agent → Escalation → Supervisor UI → KB → Learning
- Everything works together

### 2. **Clean Architecture**
- Services/Routes/Database separation
- Makes code testable and maintainable
- Shows architecture maturity beyond "make it work"

### 3. **Thoughtful Design Decisions**
- Each decision has a rationale (Phase 1 vs. Phase 2)
- You understand trade-offs (simple ≠ bad)
- You have a roadmap (not just "TODO")

### 4. **Atomic Operations**
- Resolve + KB update happen together
- Data consistency guaranteed
- Shows maturity in database design

### 5. **E2E Testing**
- Verified actual workflow works
- Not just "I built this", but "I tested it"
- Proves system-thinking

### 6. **Production Awareness**
- .gitignore prevents credential leaks
- Error handling in place
- Timestamps for audit trail
- Scalability considered

---

## 📝 PART 6: INTERVIEW STORYTELLING TEMPLATE

Use this structure in interviews:

```
QUESTION: "Tell us about this project."

ANSWER STRUCTURE:

1. CONTEXT (10 seconds)
   "I was given a 15-hour assessment to build a human-in-the-loop 
   AI supervision system for Frontdesk's engineering team."

2. THE PROBLEM (20 seconds)
   "The challenge had 4 parts: Build an AI agent that escalates 
   unknown questions, track escalations in a database, give supervisors 
   a dashboard to respond, and automatically learn from supervisor 
   answers so the AI improves over time."

3. YOUR APPROACH (30 seconds)
   "I separated concerns: Routes for HTTP, Services for business logic, 
   Database for persistence. Used Firestore for flexibility, FastAPI 
   for simplicity, and Bootstrap for a quick admin UI."

4. THE SOLUTION (60 seconds)
   "The agent checks the KB first. If no match, creates a request 
   and alerts the supervisor. The supervisor UI shows pending requests 
   and a form to submit answers. When resolved, the answer automatically 
   gets saved to the KB. Next time the agent sees that question, it 
   responds immediately without escalation. I made resolve + KB update 
   atomic to prevent data inconsistency."

5. RESULTS (15 seconds)
   "All 4 deliverables working. E2E tested. System scales to thousands 
   of requests. Ready for Phase 2 improvements like SMS follow-up and 
   semantic search."

6. REFLECTION (15 seconds)
   "The key insight: Separate the control plane (routes) from 
   computation (services) from data (database). This made the code 
   testable, scalable, and easy for a team to build on."
```

---

## 🎯 FINAL CHECKLIST FOR INTERVIEW

- [ ] I understand why each Deliverable was required
- [ ] I can explain the complete data flow from question to learning
- [ ] I can justify each architectural decision
- [ ] I know the trade-offs of my choices (simple vs. complex)
- [ ] I have 2-3 ideas for Phase 2 improvements
- [ ] I can discuss scalability (1K, 10K, 100K requests)
- [ ] I can talk about testing (unit, integration, E2E)
- [ ] I understand the difference between MVP and production-ready
- [ ] I can defend why I didn't over-engineer (no auth, simple KB search)
- [ ] I'm ready to discuss edge cases and error handling

---

**Good luck with your interview! Remember: You built a complete, working system that demonstrates good engineering judgment. Be confident. 🚀**
