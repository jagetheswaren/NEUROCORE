# NEUROCORE

[![Tests](https://img.shields.io/badge/tests-97%20passed-42f58d)](https://github.com/jagetheswaren/NEUROCORE/actions)
[![Python](https://img.shields.io/badge/python-3.11%2B-3776ab)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black)](https://ollama.com/)
[![Status](https://img.shields.io/badge/status-V0.2%20foundation-00d9ff)](https://github.com/jagetheswaren/NEUROCORE/pulls)

> A local-first personal AI operating layer built around controlled missions, shared agent capabilities, persistent context, tools, voice, and verification.

NEUROCORE is designed to do more than answer questions. It runs on the user's own machine, uses a local LLM through Ollama, maintains context, and can eventually interact with files, projects, knowledge, and tools when explicitly allowed.

The core principle is:

> **The AI can understand, plan, and propose. The user remains in control of consequential actions.**

## GitHub

- Repository: [jagetheswaren/NEUROCORE](https://github.com/jagetheswaren/NEUROCORE)
- Current development PR: [#1 — V0.2 Agent Core Foundation and Command Deck](https://github.com/jagetheswaren/NEUROCORE/pull/1)
- Stable V0.1 tag: [`NEUROCORE-V0.1-STABLE`](https://github.com/jagetheswaren/NEUROCORE/releases/tag/NEUROCORE-V0.1-STABLE)
- Documentation index: [`docs/`](./docs)

## Current status

| Milestone | Status | Details |
| --- | --- | --- |
| V0.1 Stable Foundation | **Complete** | Full-screen Textual HUD, Rich CLI fallback, Ollama, streaming, Markdown, commands, sound controls, diagnostics, API compatibility, and stable test baseline |
| V0.2 Command Deck UI | **Complete as opt-in preview** | Responsive workspace with Dashboard, Chat, Agents, Tasks, Voice, Projects, Memory, and Settings screens |
| V0.2 Agent Core Foundation | **Implemented** | Shared agent contract, registry, task model, event bus, planner, executor, verifier, and orchestrator integration |
| V0.2 Voice/STT/TTS | Planned | Optional provider contract is planned; full voice implementation is not enabled by default |
| V0.2 RAG and knowledge graph | Planned | Existing knowledge components remain available, but agent-level orchestration is not yet enabled |
| Unrestricted computer automation | **Not planned for the current milestone** | Tools must remain policy-controlled and approval-gated |

The stable V0.1 restore point is tagged:

```text
NEUROCORE-V0.1-STABLE
```

The current Agent Core work is developed on the `jagetheswaren-neurocore-v01` branch and is tracked in the open pull request:

https://github.com/jagetheswaren/NEUROCORE/pull/1

## Architecture

```text
                         NEUROCORE
                             |
                    Orchestrator / Core
                             |
        +--------------------+--------------------+
        |                    |                    |
   Agent Registry         Event Bus          LLM Adapter
        |                    |                    |
   Agent contracts      Tasks / logs       Ollama qwen3:8b
        |                    |
   Planner -> Executor -> Verifier
        |
   Memory / Knowledge / Permission boundary
```

### V0.1 runtime

- `main.py` is the application entry point.
- `core/orchestrator.py` remains the canonical orchestration boundary.
- `core/model.py` provides the Ollama adapter and streaming model calls.
- `memory/` provides SQLite-backed persistent memory.
- `knowledge/` provides document ingestion and retrieval.
- `server/` provides FastAPI and streaming API surfaces.
- `interface/tui.py` provides the stable full-screen HUD.
- `interface/panels.py` provides Rich rendering for the fallback CLI.
- `interface/sounds.py` provides optional Windows UI tones, disabled by default.

### V0.2 Agent Core

The V0.2 foundation adds shared runtime services without replacing the V0.1 chat path:

- `agents/base.py` — `BaseAgent` and user-facing `AgentState` lifecycle.
- `agents/registry.py` — extensible registration, lookup, capability search, and truthful status reporting.
- `core/tasks.py` — shared `Task`, `TaskStep`, and `TaskStatus` objects.
- `core/events.py` — thread-safe in-process event bus with bounded history.
- `core/planner.py` — creates task objects and emits task events; it does not execute actions.
- `core/executor.py` — executes a planned agent boundary and records failure/cancellation state.
- `core/verifier.py` — explicit verification hook that does not trust an agent success claim alone.
- `core/orchestrator.py` — owns the shared registry, planner, executor, verifier, and event bus.
- `interface/workspace.py` — opt-in V0.2 Command Deck.

Capabilities describe what an agent can support; they do **not** grant permission to use tools. Tool execution must continue through the existing permission and security boundaries.

## User interface

### Stable V0.1 HUD

The default UI is the proven three-zone Textual terminal HUD:

- left navigation and system sections;
- central conversation and streaming response area;
- right-side Ollama/model/security status panel;
- command input with Markdown-compatible response rendering;
- compact layout behavior for narrow terminals;
- command palette, settings modal, sound controls, and clean terminal restoration.

Supported command aliases include:

```text
/help       /status       /model
/clear      /settings    /sound on
/sound off  /sound status /exit
```

### V0.2 Command Deck preview

The Command Deck is a separate opt-in workspace, not a replacement for the stable HUD. It provides:

- persistent navigation rail;
- context header with model and connection state;
- main screen canvas;
- activity and safety inspector;
- Dashboard, Chat, Agents, Tasks, Voice, Projects, Memory, and Settings screens;
- keyboard navigation with `Ctrl+1` through `Ctrl+5`;
- narrow-terminal collapse of the rail and inspector;
- truthful `NOT CONFIGURED` states for unavailable agents/providers;
- visible routing, streaming, verified, and failed states;
- no hidden chain-of-thought display.

Enable it in `config/settings.json`:

```json
"v02_ui_enabled": true
```

Disable it to return to the V0.1 HUD:

```json
"v02_ui_enabled": false
```

The default is `false`.

## Windows setup

### Prerequisites

- Windows 10 or newer
- Python **3.11.x** (recommended)
- Ollama
- `qwen3:8b`
- PowerShell

Python 3.11 is recommended because the pinned FastAPI, Pydantic, PyYAML, and Textual dependency set has reliable wheels for this runtime. Python 3.14 can require native compilation for packages that do not yet provide compatible wheels.

Install Ollama and pull the configured model:

```powershell
ollama pull qwen3:8b
```

Confirm Ollama is running:

```powershell
ollama list
```

### Install the isolated environment

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Voice dependencies are optional and are listed separately:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-voice.txt
```

Do not install optional voice packages just to run text chat or the Textual UI.

## Running NEUROCORE

With the virtual environment activated:

```powershell
.venv\Scripts\Activate.ps1
python main.py
```

Without activating it:

```powershell
.venv\Scripts\python.exe main.py
```

The normal launch command is:

```text
python main.py
```

after `.venv` has been activated.

Sound is disabled by default. It can be changed from the UI with `/sound on`, `/sound off`, and `/sound status`; missing sound support must never prevent text mode from starting.

## Diagnostics and testing

Run the environment diagnostic:

```powershell
.venv\Scripts\python.exe main.py --doctor
```

The diagnostic reports real values for:

- Python version;
- dependency imports;
- Textual availability;
- Ollama connectivity;
- configured model detection;
- sound configuration.

Run the complete test suite:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

Current verified baseline:

```text
97 passed
3 existing deprecation warnings
```

The warnings come from the current Starlette/FastAPI test lifecycle APIs and do not cause test failures.

Compile the application modules:

```powershell
.venv\Scripts\python.exe -m compileall -q core agents interface main.py
```

## Security and safety model

NEUROCORE uses a controlled action model:

```text
Agent
  -> proposal
  -> permission policy
  -> approval when required
  -> tool execution
  -> result
  -> verification
```

Important rules:

- agent capabilities are declarations, not grants;
- model output must not directly execute a process;
- blocked commands remain blocked;
- writes, execution, network, and system actions require the existing policy boundary;
- the planner creates plans but does not execute consequential actions;
- the verifier is separate from the agent that produced the result;
- unavailable agents and providers are displayed as unavailable rather than falsely marked ready;
- hidden chain-of-thought is never rendered in the UI.

## Repository layout

```text
NEUROCORE/
├── agents/              Agent contracts, registry, and existing adapters
├── assets/sounds/       Bundled optional UI tones
├── config/              Runtime and model-router configuration
├── core/                Model, orchestrator, events, tasks, planning, execution
├── interface/           Rich panels, stable HUD, Command Deck, design tokens
├── knowledge/           Document ingestion and retrieval
├── memory/              SQLite memory and retrieval
├── server/              FastAPI routes, SSE, and WebSocket surfaces
├── security/            Security-related project components
├── tests/               Unit, API, streaming, UI, and Agent Core tests
├── requirements.txt     Core runtime dependencies
├── requirements-dev.txt Development and test dependencies
└── requirements-voice.txt Optional voice dependencies
```

## Roadmap

### Completed

1. V0.1 stable terminal foundation.
2. Ollama and `qwen3:8b` integration.
3. Streaming responses and Markdown rendering.
4. Responsive Textual HUD and Rich fallback CLI.
5. Sound architecture disabled by default.
6. Python 3.11 environment stabilization and doctor command.
7. Opt-in Command Deck workspace.
8. Shared Agent Core foundation.

### Next

1. Connect real task/event data to Dashboard and Tasks views.
2. Add bounded multi-agent coordination around the shared registry.
3. Add a formal approval center backed by the permission boundary.
4. Add model-tier routing that controls actual execution.
5. Define the provider-neutral Voice Agent contract.
6. Integrate agent-level memory and knowledge context.
7. Add verification, cancellation, timeout, and audit hardening.

Full implementation planning is maintained in the project workspace plan artifact.

## Known limitations

- V0.2 agents other than the configured general/coding adapters are registry entries and report `NOT CONFIGURED`.
- The Command Deck is opt-in and currently a workspace preview.
- Full STT/TTS and Language Lab workflows are not part of this milestone.
- Advanced RAG orchestration and knowledge graph behavior are not yet implemented.
- Model routing configuration exists, but broad request-scoped multi-model execution is a later milestone.
- Existing FastAPI/Starlette deprecation warnings remain.

## License and project intent

NEUROCORE is an experimental local-first engineering project. It prioritizes transparent local execution, explicit user control, truthful capability reporting, and incremental architecture over pretending that unfinished capabilities are complete.
