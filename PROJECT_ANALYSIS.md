# NEUROCORE v0.4 - Full Project Analysis

## 🎯 Project Overview

**NEUROCORE** is a local personal AI assistant built in Python with multimodal capabilities. It features a sophisticated mode-based interaction system, voice I/O with multilingual support (Tamil/English/Tanglish), and persistent memory management—all running locally without cloud dependencies.

**Version:** 0.4  
**Status:** Active development  
**Primary Use:** Local AI companion with terminal, planning, and development assistance

---

## 📊 Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────┐
│               NEUROCORE v0.4                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  User Interface (CLI - Rich Terminal UI)         │  │
│  └──────────────────────────────────────────────────┘  │
│         ↑                    ↑                 ↑        │
│         │                    │                 │        │
│  ┌──────▼──┐    ┌───────────▼─┐    ┌─────────▼────┐  │
│  │  Voice  │    │  Orchestr.  │    │  Terminal    │  │
│  │  I/O    │    │  (Brain)    │    │  Execution   │  │
│  └─────────┘    └───────┬─────┘    └──────────────┘  │
│                         │                              │
│  ┌──────────┬───────────▼──────────┬─────────────┐   │
│  │ Ollama   │  Memory Database     │  Permissions│   │
│  │ Model    │  (SQLite + Retrieval)│  Manager    │   │
│  └──────────┴──────────────────────┴─────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 🗂️ Folder Structure & Files

### Core System (`core/`)

| File | Purpose | Key Classes |
|------|---------|------------|
| `__init__.py` | Package marker | — |
| `brain.py` | Simplified API wrapper | `NeuroCore` |
| `config.py` | Settings loader | `load_settings()` |
| `orchestrator.py` | Central controller | `Orchestrator` |
| `modes.py` | Mode definitions & manager | `Mode`, `ModeManager`, `MODES` dict |
| `model.py` | LLM integration | `OllamaModel` |
| `permissions.py` | Command safety | `PermissionManager` |

### Voice System (`voice/`)

| File | Purpose | Key Classes |
|------|---------|------------|
| `__init__.py` | Package marker | — |
| `speech.py` | Speech-to-text | `SpeechRecognizer` (Whisper) |
| `tts.py` | Text-to-speech | `TextToSpeech` (Piper Tamil) |
| `models/` | Pre-trained models | `ta_IN-rasa_female-medium.onnx` (Tamil Piper) |

### Memory System (`memory/`)

| File | Purpose | Key Classes |
|------|---------|------------|
| `__init__.py` | Package marker | — |
| `database.py` | Persistent storage | `MemoryDatabase` |
| `retrieval.py` | Semantic search | `retrieve()` function |

### Tools & Utilities (`tools/`)

| File | Purpose | Key Classes |
|------|---------|------------|
| `__init__.py` | Package marker | — |
| `terminal.py` | Safe command execution | `TerminalTool` |

### Configuration (`config/`)

| File | Purpose | Format |
|------|---------|--------|
| `settings.json` | Runtime configuration | JSON |

### Entry Point

| File | Purpose |
|------|---------|
| `main.py` | Primary app entry point (v0.4) |
| `main_v03_backup.py` | Previous version backup |

### Supporting Folders

- `agents/` - **Empty** (reserved for future agent plugins)
- `knowledge/` - **Empty** (reserved for knowledge base)
- `models/` - **Empty** (could store additional ML models)
- `workspace/` - Working directory for terminal commands
- `.venv/`, `.venv-1/` - Python virtual environments

---

## 🔧 Core Functionality

### 1. **Orchestrator (Brain)**

**File:** [core/orchestrator.py](core/orchestrator.py)

The `Orchestrator` class is the central hub. It:
- Loads configuration and initializes all subsystems
- Manages conversation history (last 10 messages)
- Routes messages based on current mode
- Integrates memory retrieval into prompts
- Executes terminal commands with permission checking
- Provides the `run(message, mode)` and `remember(content)` APIs

**Key Flow:**
```python
orchestrator.run("what's the weather?", mode="friend")
  → Retrieve relevant memories
  → Inject into system prompt
  → Chat with OllamaModel
  → Maintain history
  → Return response
```

### 2. **Mode System**

**File:** [core/modes.py](core/modes.py)

Five interaction modes with distinct system prompts:

| Mode | Color | Purpose | Prompt Focus |
|------|-------|---------|--------------|
| **friend** | magenta | Casual chat | Friendly, conversational, multilingual |
| **plan** | yellow | Analysis | Step-by-step planning, no execution |
| **terminal** | green | Safe commands | Help run `$ <command>` safely |
| **build** | blue | Development | Code writing & improvement |
| **voice** | cyan | Speech I/O | Spoken-friendly, short responses |

Each mode has custom system prompt instructions. Mode switching via `/mode` commands.

### 3. **Memory System**

**File:** [memory/database.py](memory/database.py) + [memory/retrieval.py](memory/retrieval.py)

**Database Schema:**
```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Retrieval Strategy:**
- Extracts 3+ letter words (Thai, English, Tamil)
- Scores memories by word overlap with message
- Returns top 3 matches for injection into prompt
- Supports Thai/English/Tamil via Unicode regex

**API:**
```python
memory.save(content, category="general")  # Save memory
memories = memory.get_all()                # Fetch all
relevant = retrieve(memories, message)     # Search top 3
```

### 4. **OllamaModel (LLM)**

**File:** [core/model.py](core/model.py)

Wraps Ollama API for local LLM inference.

**Configuration:**
- **Model:** `qwen3:8b` (default, configurable)
- **Base URL:** `http://127.0.0.1:11434` (local Ollama server)
- **Temperature:** 0.7 (configurable)
- **Max tokens:** 400
- **Thinking disabled** (no_think=True)

**API:**
```python
answer = model.chat("Hello", system="You are helpful")
answer = model.chat_messages(history, system="...")
```

### 5. **Voice System**

#### Speech Recognition ([voice/speech.py](voice/speech.py))
- **Model:** Faster-Whisper (small, int8 quantized)
- **Device:** CPU
- **Audio capture:** sounddevice, 16kHz mono
- **Silence detection:** 0.9s threshold @ 350 energy
- **Max duration:** 15 seconds

#### Text-to-Speech ([voice/tts.py](voice/tts.py))
- **Model:** Piper (ta_IN-rasa_female-medium)
- **Language:** Tamil only (currently)
- **Output:** WAV → winsound playback (Windows)
- **Detection:** Auto-detects Tamil content ratio

### 6. **Permission Manager**

**File:** [core/permissions.py](core/permissions.py)

Three-tier command approval:

```python
status = "auto"       # Auto-approved (git, dir, ls, pwd, echo)
status = "sensitive"  # Requires confirmation (del, rm, shutdown)
status = "ask"        # Ask user (everything else)
```

**Configured in [config/settings.json](config/settings.json):**
```json
{
  "auto_approve": ["python", "pip", "dir", "ls", "git status", ...],
  "sensitive": ["del", "rm", "rmdir", "format", "shutdown", ...]
}
```

### 7. **Terminal Execution**

**File:** [tools/terminal.py](tools/terminal.py)

Safe subprocess wrapper:
- Runs commands in `workspace/` directory
- 120-second timeout default
- Captures stdout + stderr
- Returns (exit_code, output)
- Handles timeout & exception errors

---

## ⚙️ Configuration

**File:** [config/settings.json](config/settings.json)

```json
{
    "model": "qwen3:8b",                    # Ollama model name
    "ollama_url": "http://127.0.0.1:11434", # Ollama API endpoint
    "temperature": 0.7,                      # LLM creativity (0-1)
    "workspace": "workspace",                # Terminal working directory
    "auto_approve": [...],                   # Safe commands (no prompt)
    "sensitive": [...]                       # Dangerous commands (confirm)
}
```

---

## 🎙️ User Interface (main.py)

**File:** [main.py](main.py)

**NeuroCoreApp Class:**
- Initializes all subsystems
- Displays rich terminal UI (banner, tables)
- Command dispatcher: `/friend`, `/plan`, `/terminal`, `/build`, `/voice`, `/mode`, `/remember`, `/memory`, `/clear`, `/help`
- Voice mode loop with bilingual stop commands (English + Tamil)

**Key Commands:**
```
/friend              - Switch to friend mode
/plan <request>      - Get a plan (no execution)
/terminal            - Terminal mode
/build               - Development mode
/voice               - Start voice conversation
/mode                - Show current mode
/remember <info>     - Save to long-term memory
/memory              - List all memories
/clear               - Clear conversation history
/help                - Show commands
exit                 - Quit
```

---

## 📦 Dependencies

### Core Libraries
```
rich              - Terminal UI (tables, panels, styling)
requests          - HTTP client for Ollama API
sqlite3           - Built-in, memory database
json              - Built-in, configuration parsing
subprocess        - Built-in, terminal execution
pathlib           - Built-in, file paths
```

### Voice & Audio
```
faster_whisper    - Speech recognition (Whisper optimized)
piper-tts         - Tamil text-to-speech
sounddevice       - Audio capture
scipy             - WAV file I/O
numpy             - Numeric operations
winsound          - Windows audio playback
```

**Status:** ❌ **No requirements.txt exists** — dependencies are implicit in imports

---

## 🔍 Code Quality & Issues

### ✅ Strengths
1. **Clean architecture** - Separation of concerns (modes, memory, model, permissions)
2. **Multilingual support** - Tamil/English/Tanglish with Unicode regex
3. **Local-first** - No cloud, runs on CPU, privacy-focused
4. **Safety-first** - Permission system for terminal commands
5. **Persistent memory** - SQLite + semantic retrieval
6. **Voice I/O** - Full speech recognition + TTS

### ⚠️ Issues & Gaps

| Issue | Severity | File | Details |
|-------|----------|------|---------|
| No `requirements.txt` | High | `/` | Dependencies not documented |
| No error handling for missing Ollama | High | `core/model.py` | Fails silently if server unavailable |
| Voice model hardcoded to Tamil | Medium | `voice/tts.py` | No language selection for TTS |
| Unused folders | Low | `agents/`, `knowledge/`, `models/` | Empty placeholders |
| Backup files clutter | Low | `main_v03_backup.py`, `voice_backup/` | Version control inconsistency |
| No logging framework | Medium | Throughout | Print-based debugging only |
| Limited error recovery | Medium | `voice/speech.py` | No graceful handling of audio failures |
| Hardcoded timeouts | Low | `tools/terminal.py` | 120s fixed, not configurable |

---

## 🚀 Usage Flow

### Startup
```python
# main.py
app = NeuroCoreApp()
app.show_banner()
# Loop: read command → route → execute → return response
```

### Typical Conversation
```
> /friend
[friend mode] Tell me about Python

→ Orchestrator.run("Tell me about Python", "friend")
→ Retrieve related memories (if any)
→ Inject memories + friend prompt to OllamaModel
→ Return: "Python is a high-level programming language..."

> /remember Python is my favorite language for AI projects
→ MemoryDatabase.save("Python is my favorite...", "general")
→ "Memory saved successfully."

> /mode
→ "Current mode: friend (magenta)"

> /terminal
> $ ls workspace/
→ Check permissions → Run "ls workspace/" → Return files
```

---

## 📋 Project Statistics

| Metric | Count |
|--------|-------|
| Python files | 11 (main code + backups) |
| Folders | 9 (3 empty) |
| Lines of code | ~800 (main logic) |
| Modes | 5 |
| Languages supported | 3 (English, Tamil, Tanglish) |
| Database tables | 1 |
| External model APIs | 2 (Ollama, Whisper, Piper) |

---

## 🔮 Recommended Improvements

### Priority 1 (Critical)
- [ ] Create `requirements.txt` with pinned versions
- [ ] Add `requirements-voice.txt` for optional audio dependencies
- [ ] Add error handling for missing Ollama server (graceful fallback)
- [ ] Add logging framework (Python's `logging` module)

### Priority 2 (Important)
- [ ] Multi-language support for TTS (detect language, switch model)
- [ ] Configurable terminal timeout in `settings.json`
- [ ] Unit tests for core modules (orchestrator, retrieval, permissions)
- [ ] Add try-catch blocks for audio hardware failures

### Priority 3 (Nice-to-have)
- [ ] Remove backup files, use Git versioning properly
- [ ] Document agents, knowledge, models folders or remove
- [ ] Add CLI argument parsing (--mode, --model, --workspace)
- [ ] Dashboard for memory management (search, edit, delete)
- [ ] Support for additional LLM backends (OpenAI, local Mistral, etc.)

---

## 📝 Summary

**NEUROCORE v0.4** is a well-architected local AI assistant with thoughtful design:
- Clean mode-based interaction
- Persistent memory with semantic search
- Multilingual voice I/O
- Safe terminal execution with permissions
- Privacy-focused (local-first, no cloud)

**Main gaps:** Missing dependency documentation, weak error handling, and incomplete multilingual voice support. Overall, a solid foundation for a personal AI companion.

---

**Last Updated:** 2026-08-17  
**Analysis by:** GitHub Copilot
