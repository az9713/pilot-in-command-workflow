# Reference Guide

This is the complete reference for all commands, files, configurations, and APIs in the PIC Agentic Organizational System.

---

## Table of Contents

1. [Commands Reference](#commands-reference)
2. [File Reference](#file-reference)
3. [Configuration Reference](#configuration-reference)
4. [State Reference](#state-reference)
5. [Agent Reference](#agent-reference)
6. [Hook Reference](#hook-reference)
7. [Event Reference](#event-reference)
8. [Error Reference](#error-reference)

---

## Commands Reference

### /pic-start

**Purpose:** Initialize a new PIC workflow.

**Syntax:**
```
/pic-start [problem description]
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| problem description | Yes | What you want to accomplish |

**Examples:**
```
/pic-start Create a hello world script
/pic-start Build a temperature converter with Celsius and Fahrenheit support
/pic-start Implement user authentication with login and logout
```

**Behavior:**
1. Checks if workflow already exists
2. Generates workflow ID (WF-YYYYMMDD-HHMMSS)
3. Creates initial state in `.pic/state.json`
4. Logs workflow start event
5. Spawns Research PIC

**State Changes:**
- `initialized` → `true`
- `workflow` → new workflow ID
- `currentPhase` → `"research"`
- `problem` → your description

**Errors:**
| Error | Cause | Solution |
|-------|-------|----------|
| "Active workflow exists" | Previous workflow not complete | Finish or reset current workflow |
| "State file not found" | System not initialized | Run `bash scripts/pic-init.sh` |

---

### /pic-status

**Purpose:** Display current workflow status.

**Syntax:**
```
/pic-status
```

**Parameters:** None

**Output Format:**
```
## PIC Workflow Status

Workflow ID: WF-XXXXXXXX-XXXXXX
Problem: [problem description]
Started: [timestamp]

### Phase Progress
| Phase          | Status       | Started    | Completed  |
|----------------|--------------|------------|------------|
| Research       | [status]     | [time]     | [time]     |
| Planning       | [status]     | [time]     | [time]     |
...

### Current Phase
[Phase Name] - [description]

### Recent Activity
[Last 5 events]

### Decisions Made
[Count] decisions recorded.

### Conflicts
[Count] conflicts. [Active conflicts noted]
```

**Status Indicators:**
| Symbol | Meaning |
|--------|---------|
| `[ ]` | Pending |
| `[>]` | In Progress |
| `[x]` | Completed |
| `[!]` | Blocked |

**Errors:**
| Error | Cause | Solution |
|-------|-------|----------|
| "No active workflow" | No workflow running | Start with `/pic-start` |

---

### /pic-decide

**Purpose:** Record a formal decision document.

**Syntax:**
```
/pic-decide [decision title]
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| decision title | Optional | Brief name for the decision |

**Interactive Prompts:**
If not all information is provided, you'll be asked for:
1. Decision title (if not given)
2. Context (why this decision is needed)
3. Options considered
4. Final decision
5. Rationale
6. Consequences
7. Evidence

**Output:**
Creates `.pic/decisions/DEC-XXX.md` with format:
```markdown
# DEC-XXX: [Title]

**Date**: [timestamp]
**Workflow**: [workflow ID]
**Phase**: [current phase]
**Status**: Accepted

## Context
[why needed]

## Decision
[what was decided]

## Options Considered
### Option 1: [name]
- Pros: [list]
- Cons: [list]
...

## Rationale
[why this choice]

## Evidence
[supporting data]

## Consequences
### Enables
- [what becomes possible]
### Constrains
- [what becomes limited]
```

**Numbering:**
- First decision: DEC-001
- Second: DEC-002
- Format: DEC-XXX (zero-padded to 3 digits)

---

### /pic-handoff

**Purpose:** Execute phase transition to next PIC.

**Syntax:**
```
/pic-handoff [notes]
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| notes | Optional | Context for next phase |

**Behavior:**
1. Validates current phase can transition
2. Creates handoff record in `.pic/handoffs/`
3. Updates state (current phase → completed, next → in_progress)
4. Logs handoff event
5. Spawns next PIC with context

**Handoff Record Format:**
```markdown
# Handoff: [From Phase] → [To Phase]

**Workflow**: [ID]
**Timestamp**: [time]
**From PIC**: [agent]
**To PIC**: [agent]

## Phase Summary
### Completed Work
[summary]

### Deliverables
[list]

### Handoff Notes
[user notes]

## Context for Next Phase
### Key Findings
[important info]

### Open Questions
[unresolved items]

### Risks/Concerns
[issues]
```

**Errors:**
| Error | Cause | Solution |
|-------|-------|----------|
| "No active workflow" | No workflow | Start one first |
| "Already at final phase" | Workflow complete | N/A |

---

### /pic-conflict

**Purpose:** Escalate a conflict to the user.

**Syntax:**
```
/pic-conflict [summary]
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| summary | Optional | Brief description of conflict |

**Interactive Prompts:**
1. Conflicting parties
2. Position A details
3. Position B details
4. Stakes
5. What was tried

**Output:**
Creates `.pic/conflicts/CON-XXX.md` with format:
```markdown
# CON-XXX: [Title]

**Date**: [timestamp]
**Status**: Open

## Summary
[description]

## Conflicting Positions

### Position A
**Advocate**: [PIC]
**Position**: [recommendation]
**Evidence**: [list]
**Rationale**: [why]

### Position B
...

## Analysis
### Points of Agreement
[common ground]

### Core Disagreement
[fundamental issue]

### Stakes
[what depends on this]

## Options for Resolution
[presented to user]

## Resolution (filled after user decides)
**Decision**: [pending]
**Rationale**: [pending]
```

---

### /pic-integration

**Purpose:** Run integration test on multiple components.

**Syntax:**
```
/pic-integration [components]
```

**Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| components | Optional | Space-separated list of files/components |

**Behavior:**
1. Identifies components to test
2. Creates test plan
3. Spawns Testing PIC
4. Executes tests
5. Records results in `.pic/integration-results/`

**Output:**
Creates `.pic/integration-results/INT-XXX.md`

---

## File Reference

### Project Structure

```
project-root/
├── CLAUDE.md                      # Main documentation entry point
├── docs/                          # All documentation
│   ├── QUICK_START.md            # Getting started guide
│   ├── USER_GUIDE.md             # Complete user manual
│   ├── DEVELOPER_GUIDE.md        # Developer documentation
│   ├── ARCHITECTURE.md           # System design
│   ├── TROUBLESHOOTING.md        # Problem solving
│   ├── GLOSSARY.md               # Term definitions
│   └── REFERENCE.md              # This file
├── scripts/                       # Utility scripts
│   ├── pic-init.sh               # System initialization
│   └── hello-world.sh            # Example output
├── .pic/                          # Runtime state
│   ├── config.json               # Configuration
│   ├── state.json                # Current state
│   ├── status-log.jsonl          # Event log
│   ├── decisions/                # Decision documents
│   │   └── DEC-XXX.md
│   ├── handoffs/                 # Handoff records
│   ├── conflicts/                # Conflict records
│   │   └── CON-XXX.md
│   └── integration-results/      # Test results
│       └── INT-XXX.md
└── .claude/                       # Claude Code config
    ├── settings.json             # Permissions/hooks
    ├── agents/                   # Agent instructions
    │   ├── orchestrator.md
    │   ├── pic-research.md
    │   ├── pic-planning.md
    │   ├── pic-design.md
    │   ├── pic-implementation.md
    │   ├── pic-testing.md
    │   └── pic-review.md
    ├── skills/                   # User commands
    │   ├── pic-start/SKILL.md
    │   ├── pic-status/SKILL.md
    │   ├── pic-decide/SKILL.md
    │   ├── pic-handoff/SKILL.md
    │   ├── pic-conflict/SKILL.md
    │   └── pic-integration/SKILL.md
    ├── rules/                    # Policies
    │   ├── pic-coordination.md
    │   ├── decision-protocols.md
    │   └── conflict-resolution.md
    └── hooks/                    # Event handlers
        ├── validate-pic-action.sh
        ├── on-decision-made.sh
        ├── on-pic-handoff.sh
        └── notify-status.sh
```

---

## Configuration Reference

### .pic/config.json

**Full Schema:**

```json
{
  "version": "1.0.0",

  "pics": {
    "order": ["research", "planning", "design", "implementation", "testing", "review"],

    "definitions": {
      "[phase-name]": {
        "name": "Display Name",
        "taskAgentType": "Claude Code agent type",
        "instructionsFile": "path/to/instructions.md",
        "description": "What this phase does",
        "permissions": "read-only | acceptEdits | full",
        "canDelegate": true | false
      }
    }
  },

  "orchestrator": {
    "agent": "orchestrator",
    "maxParallelAgents": 3,
    "conflictResolutionTimeout": 300
  },

  "workflow": {
    "autoHandoff": false,
    "requireHandoffApproval": true,
    "minEvidenceForDecision": 2
  },

  "logging": {
    "verbosity": "quiet | normal | verbose",
    "logStatusUpdates": true,
    "logHandoffs": true,
    "logDecisions": true
  },

  "decisions": {
    "numberingPrefix": "DEC",
    "requireRationale": true,
    "requireAlternatives": true
  },

  "integration": {
    "numberingPrefix": "INT",
    "requireTestPlan": true
  }
}
```

**Configuration Options:**

| Path | Type | Default | Description |
|------|------|---------|-------------|
| `version` | string | "1.0.0" | Config format version |
| `pics.order` | array | [6 phases] | Phase execution order |
| `pics.definitions.[x].taskAgentType` | string | varies | Claude Code agent to use |
| `pics.definitions.[x].permissions` | string | varies | Permission level |
| `pics.definitions.[x].canDelegate` | boolean | false | Can spawn sub-agents |
| `orchestrator.maxParallelAgents` | number | 3 | Max concurrent agents |
| `orchestrator.conflictResolutionTimeout` | number | 300 | Seconds before escalation |
| `workflow.autoHandoff` | boolean | false | Auto-transition phases |
| `workflow.requireHandoffApproval` | boolean | true | Confirm before transition |
| `workflow.minEvidenceForDecision` | number | 2 | Required evidence count |
| `logging.verbosity` | string | "normal" | Log detail level |

---

## State Reference

### .pic/state.json

**Full Schema:**

```json
{
  "initialized": boolean,
  "workflow": "WF-YYYYMMDD-HHMMSS" | null,
  "currentPhase": "phase-name" | null,
  "currentPIC": "pic-name" | null,
  "problem": "problem description" | null,
  "startedAt": "ISO-8601" | null,
  "completedAt": "ISO-8601" | null,

  "phases": {
    "[phase-name]": {
      "status": "pending | in_progress | completed | blocked",
      "startedAt": "ISO-8601" | null,
      "completedAt": "ISO-8601" | null
    }
  },

  "decisions": [
    {
      "id": "DEC-XXX",
      "title": "string",
      "phase": "phase-name",
      "timestamp": "ISO-8601"
    }
  ],

  "conflicts": [
    {
      "id": "CON-XXX",
      "summary": "string",
      "phase": "phase-name",
      "status": "open | resolved",
      "timestamp": "ISO-8601"
    }
  ],

  "handoffs": [
    {
      "from": "phase-name",
      "to": "phase-name",
      "timestamp": "ISO-8601",
      "notes": "string"
    }
  ]
}
```

**Phase Statuses:**

| Status | Meaning |
|--------|---------|
| `pending` | Not yet started |
| `in_progress` | Currently active |
| `completed` | Successfully finished |
| `blocked` | Waiting on something |

---

## Agent Reference

### Agent Types

| PIC | taskAgentType | Capabilities |
|-----|---------------|--------------|
| Research | `Explore` | Read, Glob, Grep, WebSearch, WebFetch |
| Planning | `planner` | Read, Write, Edit, Glob, Grep |
| Design | `planner` | Read, Write, Edit, Glob, Grep |
| Implementation | `builder` | All tools including Bash and Task |
| Testing | `test-writer` | All tools including Bash and Task |
| Review | `reviewer` | Read, Glob, Grep |
| Orchestrator | `orchestrator` | All tools |

### Agent File Format

```markdown
# [Agent Name]

## Role
[Description of what this agent does]

## Responsibilities
1. [Responsibility 1]
2. [Responsibility 2]
...

## Tools Available
- [Tool 1] - [what it does]
- [Tool 2] - [what it does]

## Deliverables
1. [What this agent produces]
...

## Handoff Criteria
Ready when:
1. [Condition 1]
2. [Condition 2]
...
```

---

## Hook Reference

### validate-pic-action.sh

**Trigger:** Before Task tool runs

**Input:** `$1` = Tool input JSON

**Purpose:** Log task spawns, validate PIC system

### on-decision-made.sh

**Trigger:** After Write or Edit tool

**Input:**
- `$1` = Tool input JSON
- `$2` = Tool output

**Purpose:** Detect and log decision/handoff/conflict documents

### on-pic-handoff.sh

**Trigger:** When agent completes

**Input:**
- `$1` = Agent name
- `$2` = Agent output

**Purpose:** Log phase completions

### notify-status.sh

**Trigger:** On notifications

**Input:**
- `$1` = Notification type
- `$2` = Notification message

**Purpose:** Inject PIC context into notifications

---

## Event Reference

### Log Events

All events in `.pic/status-log.jsonl`:

| Event | Fields | Meaning |
|-------|--------|---------|
| `system_initialized` | version | System set up |
| `workflow_started` | workflow, problem | New workflow begun |
| `phase_completed` | phase, agent | Phase finished |
| `phase_handoff` | from, to, notes | Transition occurred |
| `decision_recorded` | decision, title, phase | Decision made |
| `decision_file_written` | decision, path | Decision file created |
| `conflict_escalated` | conflict, summary | Conflict raised |
| `conflict_file_written` | conflict | Conflict file created |
| `integration_study` | id, components, result | Integration test run |
| `workflow_completed` | workflow, result | Workflow finished |
| `task_spawn` | agent | Agent spawned |
| `pic_agent_completed` | agent, output_preview | PIC finished |

### Event Format

```json
{
  "timestamp": "2026-02-04T22:17:58Z",
  "event": "event_name",
  "field1": "value1",
  "field2": "value2"
}
```

---

## Error Reference

### Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "No active workflow" | No workflow started | `/pic-start [problem]` |
| "Unknown skill" | Skill not loaded | Restart Claude Code |
| "Agent type not found" | Invalid taskAgentType | Fix config.json |
| "State file not found" | System not initialized | `bash scripts/pic-init.sh` |
| "Permission denied" | Script not executable | `chmod +x [script]` |
| "JSON parse error" | Invalid JSON syntax | Fix the JSON file |
| "Active workflow exists" | Previous workflow running | Finish or reset |
| "Phase already complete" | Can't modify completed phase | N/A |

### Error Categories

| Category | Typical Cause |
|----------|---------------|
| Initialization | System not set up properly |
| State | Corrupted or missing state files |
| Configuration | Invalid config.json |
| Permission | File permission issues |
| Agent | Invalid agent type or instructions |
| Workflow | Workflow in unexpected state |

---

## Quick Reference Card

### Commands
```
/pic-start [problem]    Start workflow
/pic-status             Show status
/pic-decide [title]     Record decision
/pic-handoff [notes]    Transition phase
/pic-conflict [summary] Escalate conflict
/pic-integration [...]  Run integration test
```

### Key Files
```
.pic/config.json        Configuration
.pic/state.json         Current state
.pic/status-log.jsonl   Event log
```

### Phase Order
```
Research → Planning → Design → Implementation → Testing → Review
```

### Agent Types
```
Explore, planner, builder, test-writer, reviewer, orchestrator
```

### Initialization
```bash
bash scripts/pic-init.sh
claude
/pic-start [problem]
```
