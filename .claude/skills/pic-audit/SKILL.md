---
name: pic-audit
description: View detailed audit log for workflow - shows agent executions, tool usage, and decision trail
args: "[workflow-id] [phase]"
---

# PIC Audit Viewer

<pic-audit>

Display comprehensive audit trail for a workflow, including agent executions, tool usage, and complete decision-making history.

## Usage

- `/pic-audit` - Show audit summary for current workflow
- `/pic-audit WF-XXX` - Show audit for specific workflow
- `/pic-audit WF-XXX research` - Show detailed audit for specific phase

## Implementation

When this skill is invoked:

1. **Check if audit log exists**:
   ```bash
   # Read the audit log
   cat .pic/audit-log.jsonl
   ```

2. **Get current workflow** (if no workflow specified):
   ```bash
   # Get workflow ID from state
   cat .pic/state.json | grep -oP '"workflow"\s*:\s*"\K[^"]+'
   ```

3. **Display audit summary**:
   - Count events by type (agent_start, agent_complete, tool_use, decision, handoff, conflict, error)
   - Show timeline of agent executions with timestamps
   - Display tool usage statistics
   - List decision points

4. **For detailed phase view**:
   ```bash
   # Read phase-specific audit files
   cat .pic/audit/WF-XXX/[phase]-input.json
   cat .pic/audit/WF-XXX/[phase]-full.json
   ```

## Output Format

### Summary View

```
=== Audit Summary for WF-XXX ===
Started: 2024-01-15T10:00:00Z
Duration: 45 minutes

Event Counts:
  agent_start:    6
  agent_complete: 6
  tool_use:       47
  decision:       3
  handoff:        5

Agent Timeline:
  [10:00:00] pic-research started
  [10:05:30] pic-research completed (5m 30s)
  [10:05:32] pic-planning started
  ...

Tool Usage:
  Read:       23 calls
  Glob:       8 calls
  Grep:       12 calls
  Write:      4 calls

Decisions Made:
  DEC-001: Use PostgreSQL for database
  DEC-002: Implement REST API pattern
  DEC-003: Use JWT for authentication
```

### Detailed Phase View

```
=== Audit Detail: WF-XXX / research ===

Started: 2024-01-15T10:00:00Z
Completed: 2024-01-15T10:05:30Z
Duration: 5m 30s

Input (prompt):
  [Full prompt text...]

Output (2500 chars):
  [Full agent output...]

Tools Used:
  1. Glob("**/*.py") -> 15 files found
  2. Read("src/main.py") -> 120 lines
  3. Grep("def handler") -> 3 matches
  ...
```

## Audit Log Event Types

| Event Type | Description | Key Data |
|------------|-------------|----------|
| `agent_start` | Before Task runs | Full prompt, context |
| `agent_complete` | After agent finishes | Full output, duration |
| `tool_use` | After any tool | Tool name, I/O preview |
| `decision` | After /pic-decide | Decision content |
| `handoff` | During phase transition | From/to, notes |
| `conflict` | On conflict escalation | Positions, evidence |
| `error` | On failures | Error details |

## File Locations

- **Audit log**: `.pic/audit-log.jsonl` - Append-only log of all events
- **Phase transcripts**: `.pic/audit/WF-XXX/[phase]-full.json` - Complete output per phase
- **Phase inputs**: `.pic/audit/WF-XXX/[phase]-input.json` - Full input per phase

## Configuration

Audit settings in `.pic/config.json`:

```json
{
  "audit": {
    "enabled": true,
    "captureFullOutput": true,
    "maxOutputLength": 50000,
    "captureToolUsage": true,
    "retentionDays": 30
  }
}
```

</pic-audit>
