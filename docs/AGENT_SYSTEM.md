# Agent System

## Common contract

Agents share:

- `id`
- `name`
- `description`
- `capabilities`
- `state`
- `context`
- `configuration`
- `execute()`
- `cancel()`
- `reset()`

The contract is implemented by `agents.base.BaseAgent`.

## Lifecycle

```text
IDLE -> READY -> THINKING -> PLANNING -> EXECUTING
      -> WAITING_APPROVAL -> VERIFYING -> COMPLETED
      -> FAILED / CANCELLED
```

States describe user-visible execution status only. Hidden chain-of-thought is not exposed.

## Registry

`AgentRegistry` supports registration, removal, lookup, capability search, and status reporting. The initial registry includes:

- General
- Coding
- Research
- Project
- Knowledge
- Document
- Tools
- Voice

Only configured agents are shown as ready. Capabilities are declarations and never grant permissions.

## Shared execution

The orchestrator owns one registry, planner, executor, verifier, and event bus. Agents do not create alternate model, memory, or security implementations.

