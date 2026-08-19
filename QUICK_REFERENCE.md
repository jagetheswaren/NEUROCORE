# NEUROCORE Quick Reference - Visual Overview

**Generated:** 2026-08-17

---

## 🏗️ Current Architecture (v0.5 In-Progress)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACES                               │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│   CLI        │   FastAPI    │   React Web  │   Tauri      │   Flutter   │
│   ✅         │   🔄         │   ⏳         │   ⏳         │   ⏳        │
│ main.py      │ /api/routes  │ apps/web/    │ apps/desktop │ apps/mobile │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────┘
                              │
                         ┌────▼────┐
                         │REST/WS  │
                         │ :8000   │
                         └────┬────┘
                              │
     ┌────────────────────────┼────────────────────────┐
     │                        │                        │
 ┌───▼────┐          ┌────────▼────────┐      ┌───────▼────┐
 │ CHAT   │          │  ORCHESTRATOR   │      │  VOICE     │
 │ENDPOINT│          │                 │      │ ENDPOINTS  │
 └────────┘          └────────┬────────┘      └────────────┘
                              │
     ┌────────────────────────┼────────────────────────┐
     │                        │                        │
 ┌───▼────────┐      ┌────────▼────────┐      ┌───────▼────────┐
 │  MODE      │      │  MODEL ROUTER   │      │   PERMISSION   │
 │ MANAGER    │      │                 │      │    ENGINE      │
 │            │      │ Fast/Reason/    │      │                │
 │ Friend     │      │ Coding          │      │ SAFE/ASK/      │
 │ Plan       │      │                 │      │ SENSITIVE/     │
 │ Terminal   │      └────────┬────────┘      │ BLOCKED        │
 │ Build      │               │               └────────────────┘
 │ Voice      │               │
 └────────────┘               │
                              │
                    ┌─────────▼──────────┐
                    │   OLLAMA MODEL     │
                    │  (qwen3:8b local)  │
                    └────────────────────┘
                              │
     ┌────────────────────────┼────────────────────────┐
     │                        │                        │
 ┌───▼────┐         ┌─────────▼──────────┐     ┌───────▼────┐
 │MEMORY  │         │  VOICE I/O        │     │  TERMINAL  │
 │        │         │                   │     │   TOOLS    │
 │SQLite  │         │ Whisper (ASR)    │     │            │
 │Database│         │ Piper (TTS)      │     │ Safe Exec  │
 │        │         │ Tamil/English     │     │ Permission │
 └────────┘         └───────────────────┘     └────────────┘
```

---

## ✅ What's Implemented (v0.4 Complete)

### Core Brain (100%)
```
✅ Orchestrator          - Central routing & history management
✅ Mode System           - 5 modes with distinct prompts
✅ Model Integration     - Ollama API + error handling
✅ Model Router          - Intent-based tier selection
✅ Permission Engine     - 4-tier security classification
✅ Memory Database       - SQLite CRUD + semantic search
✅ Voice I/O             - Whisper ASR + Piper TTS
✅ Terminal Execution    - Subprocess wrapper + permission checks
✅ Logging               - Structured logging throughout
✅ Error Handling        - Custom exceptions + recovery
✅ Testing              - 62+ tests with comprehensive fixtures
```

### API Gateway (80%)
```
✅ FastAPI Framework     - Server bootstrap, middleware
✅ CORS Middleware       - Allow web/desktop clients
✅ Dependency Injection  - Orchestrator, ModelRouter
✅ Pydantic Validation   - Request/response models
✅ Chat Endpoint         - POST /chat (sync)
✅ Voice Endpoint        - POST /voice/speak
✅ Memory Endpoints      - Basic CRUD
✅ Modes Endpoint        - List, switch
✅ Tools Endpoint        - Framework exists
✅ Health Check          - Ollama/TTS/Speech status
🔄 WebSocket Chat       - Framework exists, streaming TODO
🔄 Streaming Response    - Need token-by-token implementation
```

---

## 🔄 What's In Progress (v0.5)

### Must Implement This Week
```
1. WebSocket Streaming (3-4 hours)
   - /ws/chat endpoint
   - Token-by-token response
   - Real-time client updates

2. Model Streaming (2-3 hours)
   - core/model.py: stream_response()
   - Ollama stream=True integration
   - Error handling

3. Tool Execution (2-3 hours)
   - /tools/execute endpoint
   - Terminal/Git/File routing
   - Permission integration

4. API Tests (3-4 hours)
   - Integration test suite
   - WebSocket tests
   - Error scenarios
```

---

## ⏳ What's Not Started (v0.6+)

### Web Interface (v0.6)
```
React + Vite + TypeScript
├── Chat component (streaming)
├── Mode selector
├── Memory viewer
├── Settings panel
└── Real-time status
```

### Desktop (v0.7)
```
Tauri wrapper
├── React + Tauri integration
├── System tray
├── Keyboard shortcuts
└── Windows/macOS/Linux installers
```

### Mobile (v0.9)
```
Flutter
├── Android build
├── iOS build
├── LAN discovery
└── Offline mode
```

### Knowledge/RAG (v0.8)
```
├── PDF/DOCX parser
├── Document chunking
├── Vector embeddings
├── Semantic search
└── /knowledge endpoints
```

### Build Agent (v0.8)
```
├── Planner agent
├── Coder agent
├── Reviewer agent
└── Multi-step execution
```

---

## 📊 Implementation Status Dashboard

### By Component Type

| Category | Count | ✅ | 🔄 | ⏳ |
|----------|-------|----|----|-----|
| **Core** | 6 | 6 | 0 | 0 |
| **Memory** | 4 | 4 | 0 | 0 |
| **Voice** | 2 | 2 | 0 | 0 |
| **API Endpoints** | 8 | 5 | 2 | 1 |
| **Real-time** | 3 | 0 | 1 | 2 |
| **Frontend** | 5 | 0 | 0 | 5 |
| **Tools** | 4 | 1 | 1 | 2 |
| **Testing** | 1 | 1 | 0 | 0 |
| **Documentation** | 3 | 3 | 0 | 0 |
| **TOTAL** | 36 | 22 | 4 | 10 |

**Completion:** 61% (22/36 core components done)

---

## 🎯 Phases & Timeline

### Current Phase: v0.5 API Completion

```
WEEK 1-2: Streaming Implementation
├─ WebSocket /ws/chat
├─ Ollama streaming
├─ Tool execution
└─ Integration tests

EXPECTED: Production-ready API by end of week 2
```

### Next Phases (If On Schedule)

```
v0.6: Web (Weeks 3-5)
  └─ React interface online

v0.7: Desktop (Weeks 6-8)
  └─ Tauri packaged

v0.8: Knowledge + Build (Weeks 9-12)
  └─ RAG + Agents

v0.9: Mobile (Weeks 10-13)
  └─ Flutter app

v1.0: Paper (Weeks 11-14)
  └─ Research publication
```

**Total Time:** 8-12 weeks (if full-time)

---

## 🔐 Security Model Overview

### Command Classification

```
┌─────────────────────────────────────────┐
│   User: "$ git status"                  │
└──────────────────┬──────────────────────┘
                   │
       ┌───────────▼───────────┐
       │  Permission Engine    │
       └───────────┬───────────┘
                   │
        ┌──────────┴──────────┬──────────┐
        │                     │          │
    SAFE (auto)          ASK (user)   BLOCKED
   "git status"       "pip install"   "shutdown"
        │                     │          │
    Execute              Show prompt    Refuse
```

### 4-Tier System

```
1. SAFE: Auto-execute (read-only, verified safe)
2. ASK: User confirmation (moderate risk)
3. SENSITIVE: Rare approval (high risk)
4. BLOCKED: Always refuse (destructive/dangerous)
```

**Configuration:** `config/settings.json`

---

## 📊 Data Flow Diagram - Chat Request

```
User Request
   "Explain inheritance"
        │
        ▼
┌─────────────────────────────────────┐
│ API Gateway: POST /chat             │
│ {message, mode}                     │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Orchestrator.run(message, mode)     │
│ 1. Get mode context                 │
│ 2. Retrieve memories (top-k)        │
│ 3. Determine model tier             │
│ 4. Build context                    │
│ 5. Call model                       │
│ 6. Store in history                 │
│ 7. Return response                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ OllamaModel.chat_messages()         │
│ - Prepare messages list             │
│ - Set system prompt                 │
│ - Call Ollama API                   │
│ - Handle errors                     │
│ - Return response                   │
└────────────┬────────────────────────┘
             │
             ▼
        Response
        "Inheritance is..."
```

---

## 🧠 Model Routing Strategy

### Intent Detection → Tier Selection

```
Message
   │
   ▼
┌─────────────────────────────────────┐
│ Analyze intent                      │
│ - Length analysis                   │
│ - Keyword detection                 │
│ - Complexity scoring                │
└────────────┬────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
  FAST   REASONING  CODING
 "Hi"   "Design    "Build
 "OK"   algo"      Python"
        "Explain"   "Fix bug"

Result: Use appropriate model tier
```

**Configuration:** `config/models.yaml`

---

## 📝 File Organization at a Glance

```
NEUROCORE/
├── server/              # 🔄 API Gateway (v0.5 in-progress)
│   ├── app.py           # ✅ FastAPI bootstrap
│   └── api/
│       ├── routes/      # ✅ REST endpoints
│       ├── websocket.py # 🔄 WebSocket framework
│       └── dependencies.py # ✅ Dependency injection
│
├── core/                # ✅ Brain (100% complete)
│   ├── orchestrator.py  # ✅ Central router
│   ├── model.py         # ✅ Ollama integration
│   ├── model_router.py  # ✅ Model tier routing
│   ├── modes.py         # ✅ 5 mode definitions
│   ├── permissions.py   # ✅ Security engine
│   └── config.py        # ✅ Settings manager
│
├── memory/              # ✅ Persistence layer
│   ├── database.py      # ✅ SQLite CRUD
│   ├── retrieval.py     # ✅ Semantic search
│   ├── embeddings.py    # ✅ Embedding model
│   └── vector_db.py     # ✅ FAISS ready
│
├── voice/               # ✅ Multimodal I/O
│   ├── speech.py        # ✅ Whisper ASR
│   ├── tts.py           # ✅ Piper TTS
│   └── models/          # ✅ Tamil models
│
├── tools/               # 🔄 Execution layer
│   ├── terminal.py      # ✅ Subprocess wrapper
│   ├── filesystem.py    # 🔄 File ops
│   └── git.py           # 🔄 Git wrapper
│
├── apps/                # ⏳ Interfaces (not started)
│   ├── cli/             # ✅ CLI working
│   ├── web/             # ⏳ React scaffold
│   ├── desktop/         # ⏳ Tauri scaffold
│   └── mobile/          # ⏳ Flutter scaffold
│
├── tests/               # ✅ Test suite
│   ├── conftest.py      # ✅ Pytest fixtures
│   ├── test_*.py        # ✅ 62+ tests
│   └── README.md        # ✅ Test guide
│
├── config/              # ✅ Configuration
│   ├── settings.json    # ✅ Main settings
│   └── models.yaml      # ✅ Model routing
│
├── main.py              # ✅ CLI entry point
├── requirements.txt     # ✅ Core deps
├── requirements-voice.txt # ✅ Voice deps
├── requirements-dev.txt # ✅ Dev deps
└── logs/                # ✅ Log output

Legend:
✅ Fully implemented & tested
🔄 In progress or partial
⏳ Not started
```

---

## 🚀 How to Get Started

### 1. Install & Run (5 minutes)
```bash
# Install
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start Ollama
ollama serve

# Run server
python -m uvicorn server.app:app --reload

# Check API
curl http://localhost:8000/health
```

### 2. Test & Validate (2 minutes)
```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest tests/ --cov=. --cov-report=html
```

### 3. Read Documentation (15 minutes)
```
1. This file (you are here)
2. PROJECT_AUDIT_2026.md (detailed analysis)
3. ACTIONS_PRIORITY_ROADMAP.md (what to do next)
4. API Docs: http://localhost:8000/docs
5. Code: core/orchestrator.py (heart of system)
```

### 4. Contribute to v0.5 (3-4 hours minimum)
```
Recommended first task: WebSocket streaming
See ACTIONS_PRIORITY_ROADMAP.md item #1
```

---

## 📚 Key Insights

### What Makes This Different
1. **One Brain, Many Faces** - Not separate AIs, unified core
2. **Permission-Driven Security** - Explicit approval model
3. **Local-First** - No cloud dependencies required
4. **Multimodal Native** - Text + Voice integrated
5. **Researche-Grade** - Designed for academic publication

### Why It Works
- Clear separation of concerns (Core vs Interfaces)
- API contract enforced across all clients
- Permission engine prevents abuse
- Memory system provides context
- Model routing provides performance

### Next Bottleneck
- **WebSocket streaming** (currently missing)
- Once this is done, Web/Desktop become much easier
- Mobile needs same API contract

---

## 💬 Summary

**NEUROCORE v0.4 is complete and production-ready.** The core brain, memory, voice, and permissions systems are fully implemented with 62+ tests.

**v0.5 (API Gateway) is 80% done.** The missing 20% is streaming support, which is the critical path to supporting real-time Web/Desktop/Mobile interfaces.

**Your architecture is correct.** It matches the vision document exactly. Follow the roadmap: complete API (2 weeks) → Web (2-3 weeks) → Desktop (2-3 weeks) → RAG (3-4 weeks) → Mobile (3-4 weeks) → Paper (2-3 weeks).

**Get involved:** Start with WebSocket streaming. Allocate 3-4 focused hours. Code template provided. High impact on development velocity.

---

**Created:** 2026-08-17  
**For:** NEUROCORE Project Team
