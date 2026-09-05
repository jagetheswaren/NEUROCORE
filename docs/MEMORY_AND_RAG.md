# Memory and Knowledge

NEUROCORE separates personal memory from external knowledge.

## Memory

`memory/` stores durable user context in SQLite. Memory is appropriate for preferences, facts, decisions, and conversation-related context.

The current retrieval path is lightweight lexical retrieval. Agents should consume a future provider interface rather than opening SQLite directly.

## Knowledge and RAG

`knowledge/` ingests documents and text, stores chunks, and provides search/context formatting. Knowledge is appropriate for project documents, reference material, and source files.

Agent-level RAG orchestration is planned. It must reuse the existing knowledge boundary and must not create duplicate vector or storage implementations.

## Planned context contract

```text
Agent
  -> Context Provider
     -> memory recall
     -> knowledge search
     -> bounded prompt context
```

Context must be size-limited, relevant, and free of secrets that are not required for the task.

