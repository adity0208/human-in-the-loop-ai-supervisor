# VISUAL FLOWCHART GUIDE

## 🔄 System Data Flow

```
                              ┌─────────────────────────┐
                              │   CUSTOMER CALLER       │
                              │  (Asks Question)        │
                              └────────────┬────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │  API: GET /agent/ask          │
                           │  Parameters:                  │
                           │  • caller_id                  │
                           │  • question                   │
                           └───────────────┬───────────────┘
                                           │
                                           ▼
                           ┌───────────────────────────────┐
                           │  Agent Route (agent.py)       │
                           │                               │
                           │  1. Receive question          │
                           │  2. Call KnowledgeService     │
                           │  3. find_answer()             │
                           └───────────────┬───────────────┘
                                           │
                       ┌───────────────────┴──────────────────┐
                       │                                      │
           ┌───────────▼────────────┐          ┌─────────────▼────────────┐
           │ KB HAS ANSWER          │          │ KB NO ANSWER             │
           │ (String Match Found)   │          │ (Unknown Question)       │
           └───────────┬────────────┘          └─────────────┬────────────┘
                       │                                      │
                       ▼                                      ▼
           ┌───────────────────┐                 ┌──────────────────────────┐
           │ Return Immediate  │                 │ Escalate to Supervisor   │
           │ {                 │                 │                          │
           │  "status":        │                 │ 1. Create help_request   │
           │  "answered",      │                 │ 2. Assign request_id     │
           │  "answer": "..."  │                 │ 3. Set status: pending   │
           │ }                 │                 │ 4. Log supervisor alert  │
           │                   │                 │ 5. Return escalation     │
           │ ✓ DONE            │                 │    {                     │
           │   NO ESCALATION   │                 │     "status": "escaped", │
           └───────────────────┘                 │     "request_id": "..."  │
                       │                         │    }                     │
                       │                         │                          │
                       │              ┌──────────▼──────────┐              │
                       │              │ Alert Supervisor   │              │
                       │              │ "[SUPERVISOR]       │              │
                       │              │  Need help..."     │              │
                       │              └────────────────────┘              │
                       │                                     │            │
                       │                                     ▼            │
                       │                    ┌─────────────────────────┐   │
                       │                    │  SUPERVISOR DASHBOARD   │   │
                       │                    │  (frontend/pending.html)│   │
                       │                    │                        │   │
                       │                    │  Shows pending request  │   │
                       │                    │  with question & caller │   │
                       │                    └────────────┬────────────┘   │
                       │                                 │                │
                       │                                 ▼                │
                       │                    ┌─────────────────────────┐   │
                       │                    │ Supervisor Clicks       │   │
                       │                    │ "RESOLVE" Button        │   │
                       │                    └────────────┬────────────┘   │
                       │                                 │                │
                       │                                 ▼                │
                       │                    ┌─────────────────────────┐   │
                       │                    │ frontend/resolve.html   │   │
                       │                    │ Shows original Q         │   │
                       │                    │ [Text area for answer]  │   │
                       │                    │ [Submit button]         │   │
                       │                    └────────────┬────────────┘   │
                       │                                 │                │
                       │                                 ▼                │
                       │                    ┌─────────────────────────┐   │
                       │                    │ Supervisor submits      │   │
                       │                    │ POST /help/requests/    │   │
                       │                    │ resolve                 │   │
                       │                    │ ?request_id=abc123      │   │
                       │                    │ &answer="text..."       │   │
                       │                    └────────────┬────────────┘   │
                       │                                 │                │
                       │                                 ▼                │
                       │                    ┌─────────────────────────┐   │
                       │                    │ ATOMIC OPERATION        │   │
                       │                    │ (All or Nothing)        │   │
                       │                    │                        │   │
                       │                    │ STEP 1: Mark resolved   │   │
                       │                    │ STEP 2: Fetch question  │   │
                       │                    │ STEP 3: Save to KB ◄────┼───┘
                       │                    │ STEP 4: Log follow-up   │
                       │                    └────────────┬────────────┘
                       │                                 │
                       │                                 ▼
                       │                    ┌─────────────────────────┐
                       │                    │ KB Updated              │
                       │                    │                        │
                       │                    │ knowledge_base {       │
                       │                    │  question: "What...",  │
                       │                    │  answer: "text..."     │
                       │                    │ }                      │
                       │                    │                        │
                       │                    │ ✓ SYSTEM LEARNED!      │
                       │                    └────────────┬────────────┘
                       │                                 │
                       └─────────────────────┬───────────┘
                                             │
                                             ▼
                                ┌────────────────────────┐
                                │ NEXT IDENTICAL QUESTION│
                                │ Same question asked    │
                                │ by different caller    │
                                │                        │
                                │ GET /agent/ask         │
                                │ ?question="What..."    │
                                │                        │
                                │ ✓ KB MATCH FOUND       │
                                │ ✓ IMMEDIATE ANSWER     │
                                │ ✓ NO ESCALATION        │
                                │ ✓ SYSTEM IMPROVED!     │
                                └────────────────────────┘
```

---

## 📊 Database Schema Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│ FIRESTORE (Cloud Database)                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐ │
│  │ COLLECTION: help_requests    │  │ COLLECTION: knowledge_base
│  │                              │  │                          │ │
│  │ DOC 1:                       │  │ DOC 1:                   │ │
│  │ request_id: "abc-123"        │  │ question: "What hours?"  │ │
│  │ caller_id: "john"            │  │ answer: "9am-6pm"        │ │
│  │ question: "What hours?"      │  │ created_at: 14:35        │ │
│  │ status: "resolved"           │  │ updated_at: 14:35        │ │
│  │ supervisor_answer: "9am..."  │  │                          │ │
│  │ created_at: 14:28            │  │ DOC 2:                   │ │
│  │ resolved_at: 14:35           │  │ question: "Feedback?"    │ │
│  │                              │  │ answer: "email us"       │ │
│  │ DOC 2:                       │  │ created_at: 14:40        │ │
│  │ request_id: "def-456"        │  │ updated_at: 14:40        │ │
│  │ caller_id: "jane"            │  │                          │ │
│  │ question: "What feedback?"   │  │ DOC 3:                   │ │
│  │ status: "pending"            │  │ question: "Hours?"       │ │
│  │ supervisor_answer: null      │  │ answer: "Check website"  │ │
│  │ created_at: 14:40            │  │ created_at: 14:45        │ │
│  │ resolved_at: null            │  │ updated_at: 14:45        │ │
│  │                              │  │                          │ │
│  └──────────────────────────────┘  └──────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ Backend Layer Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1: HTTP ROUTES (FastAPI)                                   │
│ ┌────────────────┬────────────────┬────────────────────────────┐ │
│ │  agent.py      │ help_requests  │ knowledge_base.py          │ │
│ │ GET /agent/ask │ .py            │ GET /kb/all                │ │
│ │                │ GET /pending   │                            │ │
│ │                │ GET /history   │                            │ │
│ │                │ POST /resolve  │                            │ │
│ └────┬───────────┴────┬───────────┴─────────────────┬──────────┘ │
│      │                │                             │             │
│      └────────────────┼─────────────────────────────┘             │
│                       │ Calls                                      │
│                       ▼                                            │
│ ┌──────────────────────────────────────────────────────────────┐  │
│ │ LAYER 2: BUSINESS LOGIC (Services)                          │  │
│ │ ┌────────────────────────┬──────────────────────────────┐   │  │
│ │ │ help_request_service   │ knowledge_service            │   │  │
│ │ │                        │                              │   │  │
│ │ │ • create()             │ • find_answer()              │   │  │
│ │ │ • resolve()            │ • save_answer()              │   │  │
│ │ │ • get()                │ • get_all()                  │   │  │
│ │ │ • get_pending()        │                              │   │  │
│ │ │ • get_history()        │                              │   │  │
│ │ │                        │                              │   │  │
│ │ │ (No HTTP details here) │ (Reusable, testable)        │   │  │
│ │ └────────────┬───────────┴─────────────┬───────────────┘   │  │
│ │              │                         │                    │  │
│ │              └─────────────┬───────────┘                    │  │
│ │                            │ Calls                          │  │
│ │                            ▼                                │  │
│ │              ┌──────────────────────────┐                  │  │
│ │              │ LAYER 3: DATA (Database)│                  │  │
│ │              │ firestore.py             │                  │  │
│ │              │                          │                  │  │
│ │              │ help_requests collection │                  │  │
│ │              │ knowledge_base collection│                  │  │
│ │              │                          │                  │  │
│ │              │ (Firestore operations)   │                  │  │
│ │              └──────────────────────────┘                  │  │
│ │                                                            │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🌐 Frontend Page Navigation

```
                    ┌─────────────────┐
                    │  index.html     │
                    │  (Dashboard)    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐        ┌──────────┐      ┌──────────┐
    │pending   │        │history   │      │ kb.html  │
    │.html     │        │.html     │      │(Learned  │
    │(Pending) │        │(All)     │      │ Q&A)     │
    │          │        │          │      │          │
    │ [List]   │        │ [Table]  │      │ [Table]  │
    │ [Resolve]├───┐    │          │      │          │
    └──────────┘   │    └──────────┘      └──────────┘
                   │
                   ▼
            ┌─────────────────┐
            │ resolve.html    │
            │ (Answer Form)   │
            │                 │
            │ [Question]      │
            │ [Text Area]     │
            │ [Submit]───┐    │
            └─────────────────┘
                        │
                        ▼
                ┌───────────────┐
                │ POST /resolve │
                └───────┬───────┘
                        │
                        ▼
                  ┌──────────────┐
                  │ KB Updated   │
                  │ Redirect to  │
                  │ pending.html │
                  └──────────────┘
```

---

## 🔄 Request Lifecycle Diagram

```
TIME                EVENT                    STATUS           LOCATION
────────────────────────────────────────────────────────────────────
14:28:00           Customer asks             
                   "What hours?"             
                        │
                        ▼
                   Agent checks KB          
                   (No match)               
                        │
                        ▼
14:28:01           Create help_request       PENDING          DB
                   request_id: abc-123       
                        │
                        ▼
                   Alert supervisor         
                   "[SUPERVISOR ALERT]"      
                        │
                        ▼
14:28:30           Supervisor sees          PENDING          UI
                   in pending list          
                        │
                        ▼
14:30:00           Supervisor clicks        
                   "Resolve"                
                        │
                        ▼
14:30:05           Supervisor enters        
                   answer in form           
                        │
                        ▼
14:30:10           Supervisor clicks        RESOLVING        API
                   "Submit"                 
                        │
                        ▼
14:30:11           ATOMIC OPERATIONS:
                   1. Mark resolved         RESOLVED         DB
                   2. Fetch question       
                   3. Save to KB           LEARNED          DB
                   4. Log follow-up        
                        │
                        ▼
14:30:12           Return success          
                   Redirect to pending      
                        │
                        ▼
14:30:15           Request no longer       RESOLVED         UI
                   in pending list         
                        │
                        ▼
14:40:00           Different customer      
                   asks "What hours?"      
                        │
                        ▼
                   Agent checks KB         
                   MATCH FOUND!            
                        │
                        ▼
14:40:01           Return answer           
                   "9am-6pm"               
                   (No escalation!)        
                        │
                        ▼
                   ✓ SYSTEM IMPROVED       
                   ✓ WITHOUT CODE CHANGE   
```

---

## 💾 Data Consistency Guarantee (Atomic Operation)

```
SCENARIO: Supervisor submits answer to resolve.html

WITHOUT Atomicity (WRONG):
┌─────────────────────────┐
│ Step 1: Mark resolved   │
│ ✓ SUCCESS               │
└─────────────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Step 2: Save to KB      │
│ ✗ FAILS (network error) │
└─────────────────────────┘

Result: INCONSISTENT STATE!
- Request marked resolved ✓
- But KB not updated ✗
- Next identical question: No answer in KB!
- Supervisor thinks they saved the answer, but system didn't learn

WITH Atomicity (CORRECT):
┌────────────────────────────┐
│ BEGIN TRANSACTION          │
├────────────────────────────┤
│ Step 1: Mark resolved      │
│ Step 2: Save to KB         │
│ (Both operations)          │
├────────────────────────────┤
│ Step 3: COMMIT or ROLLBACK │
│ (Both succeed or fail)     │
└────────────────────────────┘

Scenario A: Both succeed
  ✓ Request resolved
  ✓ KB updated
  ✓ System learned
  → Return HTTP 200 OK

Scenario B: Either fails
  ✗ Entire transaction rolls back
  → Request stays "pending"
  → KB unchanged
  → Supervisor can retry
  → Return HTTP 500 Error

Result: ALWAYS CONSISTENT!
- Either both operations succeed
- Or both fail and system reverts
- No halfway state possible
```

---

## 📈 Scalability Growth Path

```
CURRENT (Phase 1)
┌─────────────────────────┐
│ 1K - 10K requests/day   │
│ ✓ String KB search      │
│ ✓ All items load in UI  │
│ ✓ Single supervisor     │
│ ✓ Simple alerts         │
└─────────────────────────┘
         │
         ▼
   (Add features)
         │
         ▼
PHASE 2
┌─────────────────────────┐
│ 10K - 100K requests/day │
│ ✓ Add pagination to UI  │
│ ✓ Supervisor auth       │
│ ✓ SMS follow-up         │
│ ✓ Request timeout       │
│ ✓ Semantic KB search    │
└─────────────────────────┘
         │
         ▼
   (Scale infrastructure)
         │
         ▼
PHASE 3
┌─────────────────────────┐
│ 100K - 1M requests/day  │
│ ✓ Vector DB for KB      │
│ ✓ Multi-supervisor pool │
│ ✓ Load balancing        │
│ ✓ Advanced monitoring   │
│ ✓ Real LLM integration  │
└─────────────────────────┘
```

---

**You built this. You understand it. You can explain it. 🚀**
