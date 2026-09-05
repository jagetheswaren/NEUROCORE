# NEUROCORE

NEUROCORE is a local-first personal AI operating agent with a full-screen Textual terminal UI, Ollama integration, controlled tools, memory, and API surfaces.

## Windows setup

### Prerequisites

- Python **3.11.x** (recommended; the pinned FastAPI/Pydantic/PyYAML stack has reliable wheels for 3.11)
- Ollama
- The configured model, normally `qwen3:8b`

Install and start the model:

```powershell
ollama pull qwen3:8b
```

### Install

Create the isolated environment with the installed Python 3.11 runtime:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Python 3.11 is recommended because Python 3.14 may require native compilation for some pinned dependencies when compatible wheels are unavailable.

### Run

Ensure Ollama is running, then launch the TUI:

```powershell
.venv\Scripts\python.exe main.py
```

The normal shorthand also works after activating the environment:

```powershell
.venv\Scripts\Activate.ps1
python main.py
```

Sound is disabled by default. The TUI supports `/sound on`, `/sound off`, and `/sound status`.

### V0.2 Command Deck preview

The V0.2 workspace is an opt-in Textual experience layered on top of the stable V0.1 HUD. It adds a persistent navigation rail, responsive context and inspector panels, Dashboard/Chat/Agents/Tasks/Voice screens, and explicit run-state presentation without exposing hidden reasoning or executing tools from model output.

To preview it, set this value in `config/settings.json`:

```json
"v02_ui_enabled": true
```

Then launch normally:

```powershell
.venv\Scripts\python.exe main.py
```

Set it back to `false` to return to the V0.1 HUD. The default remains `false` while the Command Deck is being expanded.

The first V0.2 core slice now provides one shared `AgentRegistry`, `EventBus`,
`Planner`, `TaskExecutor`, and `Verifier` through the orchestrator. The Agents
screen reads those real registry states; capabilities do not grant permissions,
and unconfigured providers are shown as `NOT CONFIGURED`. Voice, RAG, and
consequential tool execution remain intentionally outside this milestone.

### Diagnostics and tests

Run the environment diagnostic without starting the UI:

```powershell
.venv\Scripts\python.exe main.py --doctor
```

Run the complete test suite:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

### Troubleshooting

- **Ollama OFFLINE:** start Ollama and verify `ollama list`.
- **Model NOT DETECTED:** run `ollama pull qwen3:8b`, or update `config/settings.json`.
- **Dependency build errors on Python 3.14:** use the Python 3.11 `.venv` commands above; do not install into the global interpreter.
- **TUI unavailable:** verify `textual` is installed in the active `.venv`.
