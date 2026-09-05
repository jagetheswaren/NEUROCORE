# Security Model

NEUROCORE follows a proposal-and-approval model:

```text
Agent
  -> Tool Proposal
  -> Security Policy
  -> Permission Check
  -> Approval when required
  -> Tool Execution
  -> Result
  -> Verification
```

## Rules

- Agent capabilities do not grant tool permissions.
- Model output cannot directly invoke a process.
- Blocked commands remain blocked.
- Read, write, execute, network, and system actions are classified by policy.
- Noninteractive API work must never wait for terminal input.
- Approvals must identify the proposed action, reason, risk, and result.
- Audit events must avoid secrets, credentials, and raw microphone data.
- Failed or cancelled work must not be reported as success.

The current `PermissionManager` and terminal boundary are preserved. A dedicated Approval Center is a future milestone.

## UI safety

The UI shows operational state, tool proposals, approvals, failures, and final results. It never displays hidden chain-of-thought.

