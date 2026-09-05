# Development Guide

## Environment

Use Python 3.11 and the project virtual environment:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

Keep optional voice dependencies separate.

## Development rules

1. Preserve the V0.1 default path.
2. Add new behavior behind explicit configuration until verified.
3. Reuse existing model, memory, knowledge, tool, and permission boundaries.
4. Never duplicate the Ollama client inside an agent.
5. Do not expose hidden chain-of-thought.
6. Do not claim unavailable capabilities are ready.
7. Add tests with every new contract.
8. Prefer deterministic fakes in unit tests; use live Ollama only for explicit integration checks.
9. Keep consequential actions approval-gated.
10. Document implemented versus planned behavior.

## Useful commands

```powershell
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe main.py --doctor
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m compileall -q core agents interface main.py
```

## Release checkpoints

Before publishing a milestone, verify tests, compilation, diagnostics, Ollama/model status, clean terminal exit, and a clean Git worktree. Keep a restore tag for stable milestones.

