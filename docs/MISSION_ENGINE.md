# Mission Engine

The Mission Engine is the long-term differentiator for NEUROCORE. It turns isolated prompts into persistent, user-controlled goals.

```text
Mission
  -> Goals
  -> Tasks
  -> Agents
  -> Memory
  -> Knowledge
  -> Files
  -> Decisions
  -> Events
  -> Progress
```

## Planned mission loop

```text
Understand
  -> Plan
  -> Select capability
  -> Request approval
  -> Execute
  -> Verify
  -> Remember
  -> Report
```

Mission state is not implemented as a complete subsystem yet. The current task model and event bus are the foundation for it.

## Product principle

NEUROCORE should track why work exists, what is active, what is waiting, what changed, and what must happen next. It should not pretend to be conscious; mission state is operational state persisted for useful continuity.

