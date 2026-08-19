# 🎯 NEUROCORE Action Items - Priority Roadmap

**Last Updated:** 2026-08-17  
**Current Phase:** v0.5 (API Gateway Completion)  
**Timeline to v1.0:** 8-12 weeks

---

## 🚨 CRITICAL PATH (Do These First)

### This Week: API Streaming Implementation

#### [ ] 1. WebSocket Streaming (3-4 hours)
**Status:** Not started  
**Impact:** HIGH - Enables real-time chat UI  
**What to do:**
- Implement `/ws/chat` endpoint in `server/api/websocket.py`
- Token-by-token streaming from Ollama
- Client receives `{"token": "...", "cumulative": "..."}`
- Proper disconnection handling & error recovery

**Code template ready in PROJECT_AUDIT_2026.md**

**Acceptance criteria:**
- WebSocket connection accepts chat messages
- Tokens stream in real-time
- Frontend can display partial responses
- Clean disconnection without errors

---

#### [ ] 2. Ollama Model Streaming Support (2-3 hours)
**Status:** Not started  
**Impact:** HIGH - Enables fast perceived response time  
**What to do:**
- Add `stream_response()` method to `core/model.py`
- Use `stream=True` parameter in Ollama API call
- Yield tokens one at a time
- Handle edge cases (empty response, errors)

**Acceptance criteria:**
- `model.stream_response(messages)` yields tokens
- Works with all 5 modes
- Error handling for broken streams
- Integration test passes

---

#### [ ] 3. Tool Execution Endpoint (2-3 hours)
**Status:** Framework exists, needs integration  
**Impact:** HIGH - Enables terminal/build commands via API  
**What to do:**
- Implement `/tools/execute` in `server/api/routes/tools.py`
- Map tool types: "terminal", "git", "file"
- Route through orchestrator.terminal / git / filesystem
- Include permission checks
- Return output with exit code

**Acceptance criteria:**
- POST /tools/execute accepts tool requests
- Terminal commands execute with permission checks
- Responses include exit code + output
- API tests pass

---

#### [ ] 4. API Integration Tests (3-4 hours)
**Status:** Partial (unit tests exist, API tests minimal)  
**Impact:** MEDIUM - Catches integration bugs early  
**What to do:**
- Create `tests/test_api_integration.py`
- Test chat endpoint (sync)
- Test chat streaming (WebSocket)
- Test voice endpoint
- Test memory CRUD
- Test tool execution
- Test permission enforcement

**Acceptance criteria:**
- 15+ integration tests
- Coverage: happy path + error cases
- All tests pass
- CI/CD ready

---

### Next 2 Weeks: v0.5 Completion

#### [ ] 5. Voice Streaming Response (2-3 hours)
**Status:** Not started  
**Impact:** MEDIUM - Better UX for voice mode  
**What to do:**
- Stream TTS audio chunks over WebSocket
- Send `{"audio_chunk": base64_data, "progress": 0.5}`
- Client plays chunks as received
- No waiting for full response

**Acceptance criteria:**
- Audio starts playing before generation completes
- No buffering issues
- Smooth playback

---

#### [ ] 6. Memory Semantic Search Endpoint (1-2 hours)
**Status:** Partial (backend works, endpoint missing)  
**Impact:** LOW - Nice-to-have for now  
**What to do:**
- Add `/memory/search` endpoint
- Accept query string
- Return ranked results with similarity scores
- Expose existing semantic retrieval

**Acceptance criteria:**
- GET /memory/search?q="java" returns relevant memories
- Results ranked by similarity
- Timestamps included

---

#### [ ] 7. Enhanced Health Check (1 hour)
**Status:** Basic health check exists  
**Impact:** LOW - Useful for monitoring  
**What to do:**
- Check Ollama model availability (not just connection)
- Check database health
- Check voice model availability
- Return detailed status object

**Acceptance criteria:**
- GET /health returns:
  ```json
  {
    "status": "healthy",
    "ollama": {"available": true, "model": "qwen3:8b"},
    "database": {"available": true, "memories": 150},
    "voice": {"speech": "ready", "tts": "ready"}
  }
  ```

---

#### [ ] 8. API Documentation Updates (1-2 hours)
**Status:** Partial (FastAPI auto-docs exist)  
**Impact:** LOW - Developer convenience  
**What to do:**
- Document all endpoints in Swagger/ReDoc
- Add request/response examples
- Document WebSocket protocol
- Create postman collection

**Acceptance criteria:**
- All endpoints documented at `/docs`
- Examples for each endpoint
- Postman collection works

---

## 🎯 MEDIUM-TERM (After API Completion)

### v0.6 - Web Interface (Weeks 3-5)

#### [ ] 9. React + Vite Setup
- Create React app with Vite
- Install dependencies
- Set up build process
- Configure for localhost + LAN access

#### [ ] 10. Chat Component
- Message display with formatting
- Streaming response support
- User/AI message differentiation
- Timestamps

#### [ ] 11. Mode Selector
- Toggle between 5 modes
- Show current mode
- Keyboard shortcuts

#### [ ] 12. Memory Viewer
- List all memories
- Search functionality
- Delete memory button
- Semantic search results

#### [ ] 13. Settings Panel
- Model selection
- Temperature slider
- Timeout configuration
- Log level selection

#### [ ] 14. Real-time Status
- Connection status
- Model loading indicator
- Voice input indicator
- Ollama health

---

### v0.7 - Desktop Application (Weeks 6-8)

#### [ ] 15. Tauri Integration
- Wrap React with Tauri
- System tray icon
- Window management

#### [ ] 16. System Shortcuts
- Ctrl+Shift+N for new chat
- Ctrl+Shift+V for voice
- Ctrl+/ for help

#### [ ] 17. File Integration
- Drag-and-drop files
- System file browser
- Workspace explorer

#### [ ] 18. Packaging
- Windows: .exe installer
- macOS: .dmg installer
- Linux: .AppImage / .deb

---

## 📚 LONG-TERM (Weeks 9-12)

### v0.8 - Knowledge + Build Agent

#### [ ] 19. PDF Parser
- Extract text from PDFs
- Document chunking
- Metadata preservation

#### [ ] 20. Vector Embeddings
- Embedding model
- FAISS integration
- Similarity search

#### [ ] 21. Build Agent
- Planner agent
- Coder agent
- Reviewer agent

### v0.9 - Mobile + Benchmarks

#### [ ] 22. Flutter App
- Android & iOS
- LAN discovery
- Offline mode

#### [ ] 23. Benchmark Suite
- Latency measurements
- Memory profiling
- Voice accuracy (WER)
- Permission accuracy

### v1.0 - Publication

#### [ ] 24. Research Paper
- Write paper
- Run final benchmarks
- Create performance charts
- Prepare for submission

#### [ ] 25. Open Source Release
- GitHub repository
- README + documentation
- License selection
- Community guidelines

---

## 📊 COMPLETION TRACKING

### v0.5 Completion Checklist

```
API Gateway Streaming:
  [_] WebSocket /ws/chat endpoint
  [_] Ollama streaming support
  [_] Tool execution endpoint
  [_] Integration tests
  [_] Voice streaming response
  [_] Memory search endpoint
  [_] Enhanced health check
  [_] API documentation

Total: 8 items | Target Completion: 2 weeks
```

### Estimated Hours per Phase

| Phase | v0.5 | v0.6 | v0.7 | v0.8 | v0.9 | v1.0 | Total |
|-------|------|------|------|------|------|------|-------|
| Hours | 25 | 35 | 25 | 45 | 45 | 35 | 210 |
| Weeks | 2 | 2-3 | 2-3 | 3-4 | 3-4 | 2-3 | 8-12 |

---

## 🔗 Resources

- **Full Audit:** `PROJECT_AUDIT_2026.md`
- **Architecture:** Check `server/app.py` + diagram in README
- **Test Framework:** `tests/conftest.py` (9 fixtures ready)
- **Code Examples:** All in PROJECT_AUDIT_2026.md sections 5.2, 5.3, 5.4
- **API Docs:** Run server and visit http://localhost:8000/docs

---

## ⚡ Quick Start for Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Start Ollama (separate terminal)
ollama serve

# Start FastAPI server
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --reload

# Run tests
pytest tests/ -v

# Check API docs
# Visit http://127.0.0.1:8000/docs
```

---

**Next step:** Start with item #1 (WebSocket Streaming). Allocate 3-4 focused hours. Code template provided in PROJECT_AUDIT_2026.md section 5.2.
