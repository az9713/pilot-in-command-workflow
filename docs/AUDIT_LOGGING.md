# Audit Logging System

The PIC system includes comprehensive audit logging that captures every step of the workflow, providing complete traceability and debugging capabilities.

## Overview

The audit system captures:
- Which agents run and when
- Complete inputs and outputs to each agent
- All tool usage (Read, Write, Glob, Grep, Bash, WebSearch, WebFetch)
- Full decision-making audit trail
- Phase transitions and handoffs
- Timing metrics

## File Structure

```
.pic/
├── audit-log.jsonl       # Append-only log of all events
├── audit/                # Per-workflow detailed transcripts
│   └── WF-XXX/
│       ├── research-input.json   # Full input to research phase
│       ├── research-full.json    # Full output from research phase
│       ├── planning-input.json
│       ├── planning-full.json
│       └── ...
└── config.json           # Contains audit configuration
```

## Audit Log Format

The audit log (`.pic/audit-log.jsonl`) contains JSONL entries with the following structure:

### Agent Start Event

```json
{
  "id": "AUD-1707123456789",
  "timestamp": "2024-01-15T10:00:00Z",
  "workflow": "WF-001",
  "phase": "research",
  "eventType": "agent_start",
  "agent": "pic-research",
  "description": "Research phase for user login system",
  "input": {
    "promptPreview": "Research the codebase to understand...",
    "promptLength": 2500
  }
}
```

### Agent Complete Event

```json
{
  "id": "AUD-1707123756789",
  "timestamp": "2024-01-15T10:05:00Z",
  "workflow": "WF-001",
  "phase": "research",
  "eventType": "agent_complete",
  "agent": "pic-research",
  "outputLength": 4500,
  "outputPreview": "Research findings: The codebase uses...",
  "auditFile": ".pic/audit/WF-001/research-full.json"
}
```

### Tool Use Event

```json
{
  "id": "AUD-1707123556789",
  "timestamp": "2024-01-15T10:02:30Z",
  "workflow": "WF-001",
  "phase": "research",
  "eventType": "tool_use",
  "tool": "Glob",
  "inputPreview": "{\"pattern\": \"**/*.py\"}",
  "outputPreview": "src/main.py\nsrc/utils.py\n...",
  "inputLength": 25,
  "outputLength": 450
}
```

## Event Types

| Event Type | Description | When Logged |
|------------|-------------|-------------|
| `audit_initialized` | System startup | When pic-init.sh runs |
| `agent_start` | Agent begins | Before Task tool runs |
| `agent_complete` | Agent finishes | After agent returns |
| `tool_use` | Tool invocation | After any tool completes |
| `decision` | Formal decision | After /pic-decide |
| `handoff` | Phase transition | During /pic-handoff |
| `conflict` | Conflict escalation | During /pic-conflict |
| `error` | Failure occurred | On any error |

## Phase Transcript Files

### Input File (`[phase]-input.json`)

Contains the full input given to the agent:

```json
{
  "agent": "pic-research",
  "phase": "research",
  "startedAt": "2024-01-15T10:00:00Z",
  "auditId": "AUD-1707123456789",
  "fullInput": {
    "subagent_type": "Explore",
    "prompt": "Full prompt text here...",
    "description": "Research phase"
  }
}
```

### Output File (`[phase]-full.json`)

Contains the full output from the agent:

```json
{
  "agent": "pic-research",
  "phase": "research",
  "completedAt": "2024-01-15T10:05:00Z",
  "auditId": "AUD-1707123756789",
  "outputLength": 4500,
  "output": "Full agent output here..."
}
```

## Configuration

Configure audit logging in `.pic/config.json`:

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

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | true | Enable/disable audit logging |
| `captureFullOutput` | boolean | true | Capture complete agent outputs |
| `maxOutputLength` | number | 50000 | Maximum characters to capture |
| `captureToolUsage` | boolean | true | Log individual tool calls |
| `retentionDays` | number | 30 | Days to retain audit logs |

## Viewing Audit Logs

### Using the `/pic-audit` Skill

```bash
# View summary for current workflow
/pic-audit

# View specific workflow
/pic-audit WF-001

# View specific phase in detail
/pic-audit WF-001 research
```

### Manual Inspection

```bash
# View audit log entries
cat .pic/audit-log.jsonl | jq .

# Filter by event type
cat .pic/audit-log.jsonl | jq 'select(.eventType == "agent_start")'

# View phase output
cat .pic/audit/WF-001/research-full.json | jq .
```

## Hook Implementation

The audit system uses Claude Code hooks to capture events:

### PreToolUse Hook (Task)

`.claude/hooks/validate-pic-action.sh` captures:
- Full task prompt
- Agent type
- Workflow and phase context

### PostToolUse Hooks

`.claude/hooks/audit-tool-use.sh` captures:
- Tool name
- Input preview (2000 chars)
- Output preview (2000 chars)
- Full lengths

`.claude/hooks/on-pic-handoff.sh` captures:
- Complete agent output (50KB max)
- Duration metrics
- Writes to phase-specific files

## Use Cases

### Debugging Failed Workflows

1. Find the error event: `cat .pic/audit-log.jsonl | jq 'select(.eventType == "error")'`
2. Check the agent's full output in `.pic/audit/WF-XXX/[phase]-full.json`
3. Review tool calls leading up to the error

### Understanding Agent Decisions

1. View agent_start to see the prompt given
2. View tool_use events to see what information was gathered
3. View agent_complete to see the conclusion

### Reviewing Tool Usage Patterns

1. Filter audit log for tool_use events
2. Count by tool type
3. Analyze input/output patterns

### Compliance and Traceability

1. All decisions have documented rationale
2. Complete input/output capture for audit trails
3. Timestamps for all events

## Best Practices

1. **Regular cleanup**: Remove old audit directories to manage disk space
2. **Sensitive data**: Be aware that outputs may contain sensitive information
3. **Large outputs**: Adjust `maxOutputLength` based on your needs
4. **Retention policy**: Set appropriate `retentionDays` for compliance

## Troubleshooting

### Audit log not being created

1. Check that `.pic/audit-log.jsonl` exists
2. Verify workflow is initialized (`initialized: true` in state.json)
3. Check hook permissions: `chmod +x .claude/hooks/*.sh`

### Missing tool use events

1. Verify hooks are registered in `.claude/settings.json`
2. Check that audit is enabled in config.json
3. Verify state.json shows active workflow

### Large audit files

1. Adjust `maxOutputLength` in config
2. Implement retention cleanup
3. Consider archiving old workflows
