# NEUROCORE Architecture

NEUROCORE is a local-first personal AI operating layer. Its long-term architecture is:

```text
User
  -> Interface (Textual CLI / API)
  -> Orchestrator
  -> Planner
  -> Agent Registry
  -> Memory / Knowledge / LLM / Tools
  -> Permission and Approval Boundary
  -> Executor
  -> Verifier
  -> User-safe Result
```

## Implemented foundation

- `core/orchestrator.py` is the canonical orchestration boundary.
- `core/model.py` adapts Ollama and supports streaming.
- `memory/` provides SQLite-backed persistent memory.
- `knowledge/` provides document ingestion and retrieval.
- `server/` provides FastAPI, SSE, and WebSocket surfaces.
- `interface/tui.py` provides the stable V0.1 HUD.
- `interface/workspace.py` provides the opt-in V0.2 Command Deck.
- `agents/registry.py` and `core/events.py` provide the first shared Agent Core.

## Design rules

One NEUROCORE shares one LLM boundary, memory boundary, knowledge boundary, tool layer, security layer, event bus, and orchestrator. Specialized agents are capabilities of that system, not independent AI applications.

Model output never directly executes a process. Consequential work must pass through policy, approval where required, execution, and verification.

