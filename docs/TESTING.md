# Testing

## Current baseline

The current branch has 97 passing tests. Existing Starlette/FastAPI deprecation warnings are non-failing warnings.

## Test layers

- Core model and Ollama behavior.
- Orchestrator modes, history, memory, and terminal policy.
- SQLite memory and knowledge retrieval.
- FastAPI, SSE, and WebSocket surfaces.
- Textual HUD, Command Deck, responsive layout, panels, settings, and sound.
- Agent contract, registry, capability status, task lifecycle, event bus, executor, and verifier.

## Commands

```powershell
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe main.py --doctor
.venv\Scripts\python.exe -m compileall -q core agents interface main.py
```

## Future coverage

Future milestones must add deterministic tests for bounded multi-agent coordination, approval workflows, cancellation, timeout, audit events, provider-unavailable voice states, and agent-level memory/knowledge context.

No test should require a microphone, Piper, Whisper, a real shell, or a running Ollama server unless it is explicitly marked as an integration test.

