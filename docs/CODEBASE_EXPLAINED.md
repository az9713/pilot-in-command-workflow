# Codebase Explained

This document provides a complete explanation of every file in the PIC system. By the end, you will understand exactly what each file does, how they connect, and when they are used.

---

## Table of Contents

1. [Overview: The Three Directories](#overview-the-three-directories)
2. [The scripts/ Directory](#the-scripts-directory)
3. [The .pic/ Directory](#the-pic-directory)
4. [The .claude/ Directory](#the-claude-directory)
5. [File Relationships](#file-relationships)
6. [Complete Workflow Walkthrough](#complete-workflow-walkthrough)
7. [File Quick Reference](#file-quick-reference)

---

## Overview: The Three Directories

The PIC system has three main directories:

```
project-root/
├── scripts/          ← Utility scripts (initialization, examples)
├── .pic/             ← Runtime state (created when system runs)
└── .claude/          ← Claude Code configuration (agents, skills, hooks)
```

### How They Relate

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER                                           │
│                      (types commands)                                    │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         .claude/                                         │
│              (defines HOW the system behaves)                            │
│                                                                          │
│   skills/ → What commands are available                                  │
│   agents/ → What each PIC does                                          │
│   hooks/  → What happens on events                                       │
│   rules/  → Policies to follow                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          .pic/                                           │
│              (stores WHAT is happening now)                              │
│                                                                          │
│   config.json → System settings                                          │
│   state.json  → Current workflow state                                   │
│   status-log.jsonl → History of events                                   │
│   decisions/, handoffs/, conflicts/ → Documents created                  │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         scripts/                                         │
│              (utilities to SET UP the system)                            │
│                                                                          │
│   pic-init.sh → Creates .pic/ directory                                  │
│   hello-world.sh → Example output                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## The scripts/ Directory

This directory contains utility scripts. Currently has 2 files.

### File: scripts/pic-init.sh

**Purpose:** Initialize or reset the PIC system.

**When Used:**
- First time setup
- When you want to reset everything
- After corrupted state

**Full Code with Explanation:**

```bash
#!/bin/bash
# pic-init.sh
# Initialize the PIC (Pilot in Command) agentic organizational system
# Run this script to set up or reset the .pic/ runtime state directory

set -e  # Exit immediately if any command fails

# ─────────────────────────────────────────────────────────────────────────
# SECTION 1: Determine directory paths
# ─────────────────────────────────────────────────────────────────────────

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Project root is one level up from scripts/
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# The .pic directory will be created here
PIC_DIR="$PROJECT_ROOT/.pic"

echo "=== PIC System Initialization ==="
echo ""

# ─────────────────────────────────────────────────────────────────────────
# SECTION 2: Check for existing state
# ─────────────────────────────────────────────────────────────────────────

if [ -d "$PIC_DIR" ]; then
    # .pic directory exists - check if there's an active workflow
    if [ -f "$PIC_DIR/state.json" ]; then
        # Extract the "initialized" value from state.json
        # grep -oP uses Perl regex to extract just the value
        INITIALIZED=$(cat "$PIC_DIR/state.json" | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")

        if [ "$INITIALIZED" = "true" ]; then
            # Warn user they'll lose their work
            echo "Warning: An active workflow exists."
            echo ""
            read -p "Do you want to reset and lose current state? (y/N) " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Initialization cancelled. Existing workflow preserved."
                exit 0
            fi
            echo "Resetting existing workflow..."
        fi
    fi
else
    echo "Creating .pic directory structure..."
    mkdir -p "$PIC_DIR"
fi

# ─────────────────────────────────────────────────────────────────────────
# SECTION 3: Create subdirectories
# ─────────────────────────────────────────────────────────────────────────

echo "Creating subdirectories..."
mkdir -p "$PIC_DIR/decisions"           # For DEC-XXX.md files
mkdir -p "$PIC_DIR/handoffs"            # For handoff records
mkdir -p "$PIC_DIR/conflicts"           # For CON-XXX.md files
mkdir -p "$PIC_DIR/integration-results" # For INT-XXX.md files

# ─────────────────────────────────────────────────────────────────────────
# SECTION 4: Create state.json (current workflow state)
# ─────────────────────────────────────────────────────────────────────────

echo "Initializing state.json..."

# The 'EOF' syntax is called a "heredoc" - it lets us write
# multi-line content directly in the script
cat > "$PIC_DIR/state.json" << 'EOF'
{
  "initialized": false,
  "workflow": null,
  "currentPhase": null,
  "currentPIC": null,
  "problem": null,
  "startedAt": null,
  "phases": {
    "research": { "status": "pending", "startedAt": null, "completedAt": null },
    "planning": { "status": "pending", "startedAt": null, "completedAt": null },
    "design": { "status": "pending", "startedAt": null, "completedAt": null },
    "implementation": { "status": "pending", "startedAt": null, "completedAt": null },
    "testing": { "status": "pending", "startedAt": null, "completedAt": null },
    "review": { "status": "pending", "startedAt": null, "completedAt": null }
  },
  "decisions": [],
  "conflicts": [],
  "handoffs": []
}
EOF

# ─────────────────────────────────────────────────────────────────────────
# SECTION 5: Create status-log.jsonl (event log)
# ─────────────────────────────────────────────────────────────────────────

echo "Initializing status-log.jsonl..."

# Get current time in ISO 8601 format (universal time)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create log with first entry
echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"system_initialized\", \"version\": \"1.0.0\"}" > "$PIC_DIR/status-log.jsonl"

# ─────────────────────────────────────────────────────────────────────────
# SECTION 6: Create config.json if it doesn't exist
# ─────────────────────────────────────────────────────────────────────────

if [ ! -f "$PIC_DIR/config.json" ]; then
    echo "Creating default config.json..."
    # [config.json content created here - see config.json section below]
else
    echo "Existing config.json preserved."
fi

# ─────────────────────────────────────────────────────────────────────────
# SECTION 7: Set permissions on hook scripts
# ─────────────────────────────────────────────────────────────────────────

echo "Setting hook permissions..."
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
if [ -d "$HOOKS_DIR" ]; then
    # Make all .sh files executable
    # 2>/dev/null suppresses errors if no files exist
    chmod +x "$HOOKS_DIR"/*.sh 2>/dev/null || true
fi

# ─────────────────────────────────────────────────────────────────────────
# SECTION 8: Verification and completion
# ─────────────────────────────────────────────────────────────────────────

echo ""
echo "=== Verification ==="
echo ""
echo "Directory structure:"
find "$PIC_DIR" -type d | sed 's/^/  /'  # List directories, indented

echo ""
echo "Files:"
find "$PIC_DIR" -type f | sed 's/^/  /'  # List files, indented

echo ""
echo "=== PIC System Ready ==="
echo ""
echo "Use /pic-start [problem] to begin a new workflow."
echo "Use /pic-status to check current status."
echo ""
```

**Key Concepts Explained:**

| Line | What It Does |
|------|--------------|
| `#!/bin/bash` | Tells the system to run this with bash |
| `set -e` | Stop immediately if any command fails |
| `$(...)` | Run command and capture output |
| `cat > file << 'EOF'` | Write everything until EOF to file |
| `grep -oP` | Extract matching text using Perl regex |
| `chmod +x` | Make file executable |
| `2>/dev/null` | Hide error messages |
| `|| true` | Don't fail even if previous command fails |

**Cross-References:**
- Creates: [.pic/state.json](#file-picstatejson)
- Creates: [.pic/status-log.jsonl](#file-picstatus-logjsonl)
- Creates: [.pic/config.json](#file-picconfigjson)
- Sets permissions on: [.claude/hooks/](#the-claudehooks-directory)

---

### File: scripts/hello-world.sh

**Purpose:** Example script created during the test workflow.

**When Used:** Created by Implementation PIC as a demo.

**Full Code:**

```bash
#!/bin/bash
# hello-world.sh
# Simple hello world demonstration script

set -e

echo "Hello, World!"
```

**This file demonstrates:**
- Standard script structure used in this project
- The output of a complete PIC workflow

---

## The .pic/ Directory

This directory stores all runtime state. It's created by `pic-init.sh` and modified during workflows.

### File: .pic/config.json

**Purpose:** System configuration - controls how the PIC system behaves.

**When Used:**
- Read at workflow start to get phase order
- Read during handoffs to get agent types
- Read by skills to check settings

**Full Code with Explanation:**

```json
{
  "version": "1.0.0",

  "pics": {
    "order": [
      "research",
      "planning",
      "design",
      "implementation",
      "testing",
      "review"
    ],
```

↑ **Phase Order:** Defines the sequence of phases. To change the order or add/remove phases, modify this array.

```json
    "definitions": {
      "research": {
        "name": "Research PIC",
        "taskAgentType": "Explore",
        "instructionsFile": ".claude/agents/pic-research.md",
        "description": "Information gathering and evidence collection",
        "permissions": "read-only",
        "canDelegate": false
      },
```

↑ **Phase Definition:** Each phase has:
- `name`: Display name
- `taskAgentType`: Which Claude Code agent to use (see [Agent Reference](REFERENCE.md#agent-reference))
- `instructionsFile`: Path to instructions (see [.claude/agents/](#the-claudeagents-directory))
- `permissions`: What the agent can do
- `canDelegate`: Whether it can spawn sub-agents

```json
      "planning": {
        "name": "Planning PIC",
        "taskAgentType": "planner",
        "instructionsFile": ".claude/agents/pic-planning.md",
        "description": "Strategic planning and roadmap creation",
        "permissions": "acceptEdits",
        "canDelegate": false
      },
      "design": {
        "name": "Design PIC",
        "taskAgentType": "planner",
        "instructionsFile": ".claude/agents/pic-design.md",
        "description": "Technical architecture and system design",
        "permissions": "acceptEdits",
        "canDelegate": false
      },
      "implementation": {
        "name": "Implementation PIC",
        "taskAgentType": "builder",
        "instructionsFile": ".claude/agents/pic-implementation.md",
        "description": "Code execution and feature building",
        "permissions": "full",
        "canDelegate": true
      },
      "testing": {
        "name": "Testing PIC",
        "taskAgentType": "test-writer",
        "instructionsFile": ".claude/agents/pic-testing.md",
        "description": "Validation and integration testing",
        "permissions": "full",
        "canDelegate": true
      },
      "review": {
        "name": "Review PIC",
        "taskAgentType": "reviewer",
        "instructionsFile": ".claude/agents/pic-review.md",
        "description": "Final approval and quality gate",
        "permissions": "read-only",
        "canDelegate": false
      }
    }
  },
```

↑ **All Six PICs Defined:** Note how permissions vary:
- Research and Review: `read-only` (cannot modify files)
- Planning and Design: `acceptEdits` (can write with approval)
- Implementation and Testing: `full` + `canDelegate: true` (full access, can spawn sub-agents)

```json
  "orchestrator": {
    "agent": "orchestrator",
    "maxParallelAgents": 3,
    "conflictResolutionTimeout": 300
  },
```

↑ **Orchestrator Settings:**
- `maxParallelAgents`: How many agents can run at once
- `conflictResolutionTimeout`: Seconds before escalating to user

```json
  "workflow": {
    "autoHandoff": false,
    "requireHandoffApproval": true,
    "minEvidenceForDecision": 2
  },
```

↑ **Workflow Settings:**
- `autoHandoff: false`: Don't auto-transition (require explicit handoff)
- `requireHandoffApproval: true`: Ask before phase transitions
- `minEvidenceForDecision: 2`: Need 2+ pieces of evidence for decisions

```json
  "logging": {
    "verbosity": "normal",
    "logStatusUpdates": true,
    "logHandoffs": true,
    "logDecisions": true
  },
```

↑ **Logging Settings:** Control what gets logged to status-log.jsonl

```json
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

↑ **Document Settings:** Prefixes for decision and integration docs

**Cross-References:**
- Created by: [scripts/pic-init.sh](#file-scriptspic-initsh)
- Read by: [.claude/skills/pic-start/SKILL.md](#file-claudeskillspic-startskillmd)
- Read by: [.claude/skills/pic-handoff/SKILL.md](#file-claudeskillspic-handoffskillmd)
- References: [.claude/agents/*.md](#the-claudeagents-directory)

---

### File: .pic/state.json

**Purpose:** Current workflow state - what's happening right now.

**When Used:**
- Read by `/pic-status` to show progress
- Updated by `/pic-start` when starting workflow
- Updated by `/pic-handoff` during phase transitions
- Updated by `/pic-decide` when recording decisions

**Full Code with Explanation:**

```json
{
  "initialized": true,
```
↑ `true` when a workflow is active, `false` when reset

```json
  "workflow": "WF-20260204-221758",
```
↑ Unique workflow ID. Format: `WF-YYYYMMDD-HHMMSS`

```json
  "currentPhase": "implementation",
  "currentPIC": "pic-implementation",
```
↑ Which phase is active and which agent is running

```json
  "problem": "Create a simple hello world CLI tool",
```
↑ The user's original problem statement

```json
  "startedAt": "2026-02-04T22:17:58Z",
  "completedAt": null,
```
↑ Timestamps. `completedAt` is null while workflow is running.

```json
  "phases": {
    "research": {
      "status": "completed",
      "startedAt": "2026-02-04T22:17:58Z",
      "completedAt": "2026-02-04T22:18:30Z"
    },
    "planning": {
      "status": "completed",
      "startedAt": "2026-02-04T22:18:30Z",
      "completedAt": "2026-02-04T22:19:00Z"
    },
    "design": {
      "status": "completed",
      "startedAt": "2026-02-04T22:19:00Z",
      "completedAt": "2026-02-04T22:19:05Z"
    },
    "implementation": {
      "status": "in_progress",
      "startedAt": "2026-02-04T22:19:05Z",
      "completedAt": null
    },
    "testing": {
      "status": "pending",
      "startedAt": null,
      "completedAt": null
    },
    "review": {
      "status": "pending",
      "startedAt": null,
      "completedAt": null
    }
  },
```

↑ **Phase Tracking:** Each phase has:
- `status`: `pending` | `in_progress` | `completed` | `blocked`
- `startedAt`: When it started (null if not started)
- `completedAt`: When it finished (null if not finished)

```json
  "decisions": [
    {
      "id": "DEC-001",
      "title": "Choose scripting language",
      "phase": "design",
      "timestamp": "2026-02-04T22:19:02Z"
    }
  ],
```
↑ **Decisions:** References to decision documents in `.pic/decisions/`

```json
  "conflicts": [],
```
↑ **Conflicts:** References to conflict documents in `.pic/conflicts/`

```json
  "handoffs": [
    {
      "from": "research",
      "to": "planning",
      "timestamp": "2026-02-04T22:18:30Z",
      "notes": "Research complete, ready for planning"
    }
  ]
}
```
↑ **Handoffs:** Record of phase transitions

**State Machine:**

```
┌─────────┐    start     ┌─────────────┐   complete   ┌───────────┐
│ pending │ ───────────▶ │ in_progress │ ───────────▶ │ completed │
└─────────┘              └─────────────┘              └───────────┘
                               │
                               │ blocked
                               ▼
                         ┌─────────┐
                         │ blocked │
                         └─────────┘
```

**Cross-References:**
- Created by: [scripts/pic-init.sh](#file-scriptspic-initsh)
- Updated by: [.claude/skills/pic-start/SKILL.md](#file-claudeskillspic-startskillmd)
- Read by: [.claude/skills/pic-status/SKILL.md](#file-claudeskillspic-statusskillmd)

---

### File: .pic/status-log.jsonl

**Purpose:** Append-only log of all events that occur.

**When Used:**
- Appended to whenever something happens
- Read by `/pic-status` to show recent activity
- Used for debugging and auditing

**Format:** Each line is a complete JSON object.

**Example Content:**

```json
{"timestamp": "2026-02-04T22:17:58Z", "event": "system_initialized", "version": "1.0.0"}
{"timestamp": "2026-02-04T22:17:58Z", "event": "workflow_started", "workflow": "WF-20260204-221758", "problem": "Create a simple hello world CLI tool"}
{"timestamp": "2026-02-04T22:18:30Z", "event": "phase_completed", "phase": "research", "agent": "pic-research"}
{"timestamp": "2026-02-04T22:18:30Z", "event": "phase_handoff", "from": "research", "to": "planning"}
{"timestamp": "2026-02-04T22:19:02Z", "event": "decision_recorded", "decision": "DEC-001", "title": "Choose scripting language"}
{"timestamp": "2026-02-04T22:21:00Z", "event": "workflow_completed", "workflow": "WF-20260204-221758", "result": "success"}
```

**Event Types:**

| Event | When It Occurs | Fields |
|-------|---------------|--------|
| `system_initialized` | After `pic-init.sh` runs | version |
| `workflow_started` | After `/pic-start` | workflow, problem |
| `phase_completed` | When a PIC finishes | phase, agent |
| `phase_handoff` | During phase transition | from, to, notes |
| `decision_recorded` | After `/pic-decide` | decision, title, phase |
| `decision_file_written` | When DEC-XXX.md created | decision, path |
| `conflict_escalated` | After `/pic-conflict` | conflict, summary |
| `integration_study` | After `/pic-integration` | id, components, result |
| `workflow_completed` | After Review approves | workflow, result |
| `task_spawn` | When agent spawned | agent |
| `pic_agent_completed` | When PIC finishes | agent, output_preview |

**Why JSONL?**
- Each line is independent (easy to append)
- Can read with `tail -5` for recent events
- Can search with `grep "phase_completed"`
- Won't corrupt entire file if write interrupted

**Cross-References:**
- Created by: [scripts/pic-init.sh](#file-scriptspic-initsh)
- Written by: [.claude/hooks/*.sh](#the-claudehooks-directory)
- Read by: [.claude/skills/pic-status/SKILL.md](#file-claudeskillspic-statusskillmd)

---

### Directory: .pic/decisions/

**Purpose:** Stores formal decision documents.

**When Used:** Created by `/pic-decide` command.

**File Naming:** `DEC-001.md`, `DEC-002.md`, etc.

**Example File (DEC-001.md):**

```markdown
# DEC-001: Choose scripting language

**Date**: 2026-02-04T22:19:02Z
**Workflow**: WF-20260204-221758
**Phase**: design
**Status**: Accepted

## Context

We need to decide which scripting language to use for the CLI tool.
The project already uses bash for existing scripts.

## Decision

Use Bash for the scripting language.

## Options Considered

### Option 1: Bash
- **Pros**: Already used in project, no dependencies, runs everywhere
- **Cons**: Limited features compared to Python

### Option 2: Python
- **Pros**: More powerful, better error handling
- **Cons**: Requires Python installed, new pattern for this project

### Option 3: Node.js
- **Pros**: Modern, good tooling
- **Cons**: Heavy dependency, overkill for simple scripts

## Rationale

Bash is the simplest choice that fits project conventions. The script
is simple enough that Bash's limitations don't apply.

## Evidence

1. Existing scripts (pic-init.sh) use Bash successfully
2. Target is simple "Hello World" - doesn't need advanced features
3. No additional dependencies required

## Consequences

### Enables
- Consistent with existing scripts
- No new dependencies to manage
- Simple deployment

### Constrains
- Can't use advanced language features
- Limited error handling options
```

**Cross-References:**
- Created by: [.claude/skills/pic-decide/SKILL.md](#file-claudeskillspic-decideskillmd)
- Referenced in: [.pic/state.json](#file-picstatejson) decisions array
- Logged in: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

### Directory: .pic/handoffs/

**Purpose:** Stores phase transition records.

**When Used:** Created during `/pic-handoff`.

**File Naming:** `WF-XXXXXXXX-XXXXXX-research-to-planning.md`

**Example File:**

```markdown
# Handoff: Research → Planning

**Workflow**: WF-20260204-221758
**Timestamp**: 2026-02-04T22:18:30Z
**From PIC**: pic-research
**To PIC**: pic-planning

## Phase Summary

### Completed Work
- Analyzed problem statement
- Searched existing codebase for patterns
- Identified project conventions

### Deliverables
- Research summary with key findings
- Evidence log with sources
- Recommendations for approach

### Handoff Notes
Research complete, ready for planning phase.

## Context for Next Phase

### Key Findings
- Project uses Bash scripts (see scripts/pic-init.sh)
- Scripts follow pattern: shebang, set -e, main logic
- Output should go in scripts/ directory

### Open Questions
- None identified

### Risks/Concerns
- None identified for this simple task

## Exit Criteria Verification

| Criterion | Status |
|-----------|--------|
| Problem understood | Met |
| Evidence collected | Met |
| Recommendations provided | Met |
```

**Cross-References:**
- Created by: [.claude/skills/pic-handoff/SKILL.md](#file-claudeskillspic-handoffskillmd)
- Referenced in: [.pic/state.json](#file-picstatejson) handoffs array

---

### Directory: .pic/conflicts/

**Purpose:** Stores conflict escalation records.

**When Used:** Created by `/pic-conflict`.

**File Naming:** `CON-001.md`, `CON-002.md`, etc.

**Example File:**

```markdown
# CON-001: Database Selection

**Date**: 2026-02-04T22:19:30Z
**Workflow**: WF-20260204-221758
**Phase**: design
**Status**: Resolved

## Summary

Design PIC recommends SQLite, Planning PIC recommends PostgreSQL.

## Conflicting Positions

### Position A: SQLite
**Advocate**: pic-design
**Position**: Use SQLite for the database
**Evidence**:
- No server setup required
- File-based, simple deployment
- Sufficient for current scale
**Rationale**: Simplicity and ease of deployment

### Position B: PostgreSQL
**Advocate**: pic-planning
**Position**: Use PostgreSQL for the database
**Evidence**:
- Team has PostgreSQL experience
- Better for future scaling
- More features available
**Rationale**: Future-proofing and team expertise

## Analysis

### Points of Agreement
- Both agree we need a relational database
- Both agree data integrity is important

### Core Disagreement
- Simplicity vs. future scalability

### Stakes
This affects deployment complexity and future scaling options.

## Resolution

**Decision**: SQLite
**Rationale**: User decided simplicity is more important for MVP
**Decided By**: User
**Date**: 2026-02-04T22:20:00Z
```

**Cross-References:**
- Created by: [.claude/skills/pic-conflict/SKILL.md](#file-claudeskillspic-conflictskillmd)
- Referenced in: [.pic/state.json](#file-picstatejson) conflicts array

---

### Directory: .pic/integration-results/

**Purpose:** Stores integration test results.

**When Used:** Created by `/pic-integration`.

**File Naming:** `INT-001.md`, `INT-002.md`, etc.

**Example File:**

```markdown
# INT-001: Script Integration Test

**Date**: 2026-02-04T22:25:00Z
**Workflow**: WF-20260204-221758
**Status**: Pass

## Overview

**Components Tested**:
- scripts/hello-world.sh
- scripts/pic-init.sh

**Duration**: 15 seconds
**Result**: All tests passed

## Test Plan

### Test 1: Scripts execute independently
- Run each script
- Verify exit code 0
- Verify expected output

### Test 2: Scripts don't interfere
- Run pic-init.sh
- Run hello-world.sh
- Verify state unchanged

## Results

### Test 1: Independent Execution
- **Status**: Pass
- **Observations**: Both scripts run successfully
- **Evidence**: Exit codes were 0

### Test 2: No Interference
- **Status**: Pass
- **Observations**: Scripts are independent
- **Evidence**: State file unchanged by hello-world.sh

## Issues Found

None.

## Integration Health

### Working Well
- Scripts follow consistent patterns
- No shared state conflicts
- Clean separation of concerns

### Needs Attention
- Nothing identified

### Recommendations
- Continue using same patterns for new scripts
```

**Cross-References:**
- Created by: [.claude/skills/pic-integration/SKILL.md](#file-claudeskillspic-integrationskillmd)

---

## The .claude/ Directory

This directory contains all Claude Code configuration - how the system behaves.

### File: .claude/settings.json

**Purpose:** Claude Code settings - permissions and hooks.

**When Used:**
- Read by Claude Code when starting
- Hooks execute during workflow

**Full Code with Explanation:**

```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)",
      "WebSearch(**)",
      "WebFetch(**)"
    ],
    "deny": []
  },
```

↑ **Default Permissions:** What tools are allowed by default. The `(**)` means any arguments.

```json
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Task",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-pic-action.sh \"$TOOL_INPUT\""
          }
        ]
      }
    ],
```

↑ **PreToolUse Hook:** Before the Task tool runs, execute `validate-pic-action.sh`. The `$TOOL_INPUT` variable contains the tool's input as JSON.

```json
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/on-decision-made.sh \"$TOOL_INPUT\" \"$TOOL_OUTPUT\""
          }
        ]
      }
    ]
  }
}
```

↑ **PostToolUse Hook:** After Write or Edit tools run, execute `on-decision-made.sh`. This detects when decision documents are created.

**Hook Execution Flow:**

```
User requests action
        │
        ▼
┌─────────────────┐
│ PreToolUse hook │ ← validate-pic-action.sh runs
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Tool runs     │ ← The actual Write/Edit/Task
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PostToolUse hook│ ← on-decision-made.sh runs
└─────────────────┘
```

**Cross-References:**
- References: [.claude/hooks/*.sh](#the-claudehooks-directory)

---

### The .claude/agents/ Directory

Contains instruction files for each PIC agent. These files tell agents what to do.

#### File: .claude/agents/orchestrator.md

**Purpose:** Instructions for the central coordinator.

**When Used:** When orchestrating workflow, resolving conflicts.

**Key Sections:**

```markdown
# Orchestrator Agent

You are the **Orchestrator** - the central coordinator for the PIC workflow.

## Role

You manage the flow between specialized PIC agents, resolve conflicts,
and ensure smooth phase transitions. You do NOT do the work yourself -
you delegate to the appropriate PIC.

## Responsibilities

1. **Workflow Initialization** - Set up new workflows
2. **Phase Transitions** - Validate handoffs and spawn next PIC
3. **Conflict Resolution** - Synthesize disagreements using evidence
4. **Progress Tracking** - Maintain workflow state and status logs
5. **Quality Gates** - Ensure each phase meets exit criteria
```

**Cross-References:**
- Referenced by: [.pic/config.json](#file-picconfigjson) orchestrator section

---

#### File: .claude/agents/pic-research.md

**Purpose:** Instructions for the Research PIC.

**When Used:** First phase of every workflow.

**Key Sections:**

```markdown
# Research PIC Agent

You are the **Research PIC** - the Pilot in Command for the research phase.

## Role

You own the research phase completely. Your job is to gather information,
collect evidence, and build the knowledge foundation.

## Tools Available

You have **read-only** access:
- `Read` - Read files in the codebase
- `Glob` - Find files by pattern
- `Grep` - Search file contents
- `WebSearch` - Search the web
- `WebFetch` - Fetch and analyze web content

You CANNOT use: `Write`, `Edit`, `Bash`, `Task`

## Deliverables

1. **Research Summary** - Key findings organized by topic
2. **Evidence Log** - Sources with reliability ratings
3. **Knowledge Gaps** - What couldn't be determined
4. **Recommendations** - Suggested directions
5. **Risk Factors** - Potential issues identified

## Handoff Criteria

Ready when:
1. Problem is clearly understood
2. Evidence sources documented
3. Knowledge gaps listed
4. Recommendations provided
```

**Why Read-Only?** Research should gather information, not modify the codebase. This prevents scope creep.

**Cross-References:**
- Referenced by: [.pic/config.json](#file-picconfigjson) `pics.definitions.research.instructionsFile`
- Uses agent type: `Explore`

---

#### File: .claude/agents/pic-planning.md

**Purpose:** Instructions for the Planning PIC.

**When Used:** Second phase, after Research.

**Key Sections:**

```markdown
# Planning PIC Agent

## Role

Create a strategic roadmap based on research findings.

## Tools Available

You have **edit** access:
- `Read`, `Write`, `Edit`, `Glob`, `Grep`

You CANNOT use: `Bash`, `Task`, `WebSearch`, `WebFetch`

## Deliverables

1. **Strategic Plan Document** - Approach and rationale
2. **Milestone Definitions** - What constitutes completion
3. **Task Breakdown** - Specific work items
4. **Risk Register** - Risks and mitigations
5. **Success Criteria** - Measurable outcomes
```

**Cross-References:**
- Uses agent type: `planner`

---

#### File: .claude/agents/pic-design.md

**Purpose:** Instructions for the Design PIC.

**When Used:** Third phase, after Planning.

**Key Sections:**

```markdown
# Design PIC Agent

## Role

Create technical architecture and define interfaces.

## Tools Available

Same as Planning: `Read`, `Write`, `Edit`, `Glob`, `Grep`

## Deliverables

1. **Architecture Document** - System structure
2. **Interface Specifications** - APIs, contracts
3. **Technical Decision Records** - Key decisions
4. **Implementation Guidelines** - Patterns, conventions
5. **Test Strategy** - How to verify the design
```

**Cross-References:**
- Uses agent type: `planner`

---

#### File: .claude/agents/pic-implementation.md

**Purpose:** Instructions for the Implementation PIC.

**When Used:** Fourth phase, after Design.

**Key Sections:**

```markdown
# Implementation PIC Agent

## Role

Write code and build features according to design specifications.

## Tools Available

You have **full** access:
- All tools including `Bash` and `Task`

## Sub-Agent Delegation

You CAN spawn sub-agents for:
- Parallel implementation of independent components
- Utility tasks like formatting

You CANNOT delegate:
- Work outside your domain
- Final verification (Testing handles this)
```

**Why Full Access?** Implementation needs to write code, run builds, and potentially spawn helpers.

**Cross-References:**
- Uses agent type: `builder`

---

#### File: .claude/agents/pic-testing.md

**Purpose:** Instructions for the Testing PIC.

**When Used:** Fifth phase, after Implementation.

**Key Sections:**

```markdown
# Testing PIC Agent

## Role

Validate implementation and run integration tests.

## Tools Available

Full access including `Bash` and `Task`.

## Test Categories

### Unit Tests
- Verify individual components
- Already provided by Implementation PIC

### Integration Tests
- Verify components work together
- Your primary focus

### Edge Cases
- Boundary conditions
- Invalid inputs
- Error scenarios
```

**Cross-References:**
- Uses agent type: `test-writer`

---

#### File: .claude/agents/pic-review.md

**Purpose:** Instructions for the Review PIC.

**When Used:** Final phase, after Testing.

**Key Sections:**

```markdown
# Review PIC Agent

You are the **quality gate** - verify all phases met their criteria.

## Tools Available

You have **read-only** access:
- `Read`, `Glob`, `Grep`

You CANNOT use: `Write`, `Edit`, `Bash`, `Task`

## Review Checklist

### Research Phase
- [ ] Problem clearly understood
- [ ] Evidence sources documented

### Planning Phase
- [ ] Approach justified
- [ ] Milestones defined

[... checklist continues for all phases ...]

## Decision

**APPROVED** when:
- All phases met exit criteria
- No critical issues remain
- Documentation adequate

**REVISIONS REQUIRED** when:
- Critical quality issues
- Significant gaps
- Documentation inadequate
```

**Why Read-Only?** Review should assess, not modify. Changes require going back to the appropriate phase.

**Cross-References:**
- Uses agent type: `reviewer`

---

### The .claude/skills/ Directory

Contains user-invocable commands. Each skill is in its own directory with a `SKILL.md` file.

#### File: .claude/skills/pic-start/SKILL.md

**Purpose:** Initialize a new workflow.

**When Used:** User types `/pic-start [problem]`

**Key Code Sections:**

```markdown
---
name: pic-start
description: Initialize a new PIC workflow with a problem statement
args: "[problem description]"
---
```

↑ **Front Matter:** Defines skill metadata. Claude Code reads this to register the command.

```markdown
## Protocol

### Step 1: Verify System State

Read `.pic/state.json` to check if a workflow is already in progress.

**If a workflow exists and is not complete:**
- Warn the user
- Ask if they want to: (a) resume, (b) abandon and start fresh
```

↑ **State Check:** Prevents accidentally overwriting an active workflow.

```markdown
### Step 2: Initialize State

Update `.pic/state.json` with:

{
  "initialized": true,
  "workflow": "WF-[timestamp]",
  "currentPhase": "research",
  "currentPIC": "pic-research",
  "problem": "[user's problem statement]",
  ...
}
```

↑ **State Update:** Creates the workflow.

```markdown
### Step 5: Spawn Research PIC

Read `.pic/config.json` to get the `taskAgentType` for research (should be `Explore`).

Use the Task tool with:
- subagent_type: `Explore`
- prompt: [Instructions from pic-research.md + problem statement]
```

↑ **Agent Spawning:** Starts the first PIC.

**Workflow Diagram:**

```
/pic-start "Build X"
        │
        ▼
┌───────────────┐
│ Read state    │ ← Check for existing workflow
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Update state  │ ← Set initialized=true, workflow=WF-XXX
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Log event     │ ← Append to status-log.jsonl
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Spawn Research│ ← Use Task tool with Explore agent
└───────────────┘
```

**Cross-References:**
- Reads: [.pic/state.json](#file-picstatejson)
- Reads: [.pic/config.json](#file-picconfigjson)
- Writes: [.pic/status-log.jsonl](#file-picstatus-logjsonl)
- Spawns: [.claude/agents/pic-research.md](#file-claudeagentspic-researchmd)

---

#### File: .claude/skills/pic-status/SKILL.md

**Purpose:** Display current workflow status.

**When Used:** User types `/pic-status`

**Key Code Sections:**

```markdown
### Step 1: Read Current State

Read `.pic/state.json` to get the current workflow state.

**If no workflow is initialized:**
Display: "No active workflow. Use /pic-start to begin."
```

```markdown
### Step 3: Display Status

Format and display:

## PIC Workflow Status

**Workflow ID**: [workflow id]
**Problem**: [problem statement]

### Phase Progress

| Phase          | Status       |
|----------------|--------------|
| Research       | [x] Completed |
| Planning       | [>] In Progress |
...
```

**This skill is read-only** - it only displays information.

**Cross-References:**
- Reads: [.pic/state.json](#file-picstatejson)
- Reads: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

#### File: .claude/skills/pic-decide/SKILL.md

**Purpose:** Record a formal decision document.

**When Used:** User types `/pic-decide [title]`

**Key Code Sections:**

```markdown
### Step 2: Generate Decision ID

Read existing decisions in `.pic/decisions/` to determine the next ID.

Format: `DEC-[NNN]` where NNN is zero-padded (e.g., DEC-001)
```

```markdown
### Step 4: Create Decision Document

Write to `.pic/decisions/DEC-[NNN].md`
```

```markdown
### Step 5: Update State

Add decision reference to `.pic/state.json` decisions array
```

**Cross-References:**
- Creates: [.pic/decisions/DEC-XXX.md](#directory-picdecisions)
- Updates: [.pic/state.json](#file-picstatejson)
- Writes: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

#### File: .claude/skills/pic-handoff/SKILL.md

**Purpose:** Execute phase transition.

**When Used:** User types `/pic-handoff [notes]`

**Key Code Sections:**

```markdown
### Step 4: Determine Next Phase

Look up the next phase in the configured order from config.json.
```

```markdown
### Step 5: Create Handoff Record

Write to `.pic/handoffs/[workflow]-[from]-to-[to].md`
```

```markdown
### Step 9: Spawn Next PIC

Read `.pic/config.json` to get the `taskAgentType` for the next phase.

| Phase | taskAgentType |
|-------|---------------|
| research | Explore |
| planning | planner |
| design | planner |
| implementation | builder |
| testing | test-writer |
| review | reviewer |
```

**Cross-References:**
- Reads: [.pic/config.json](#file-picconfigjson)
- Updates: [.pic/state.json](#file-picstatejson)
- Creates: [.pic/handoffs/](#directory-pichandoffs)
- Spawns: Next agent from [.claude/agents/](#the-claudeagents-directory)

---

#### File: .claude/skills/pic-conflict/SKILL.md

**Purpose:** Escalate a conflict for user decision.

**When Used:** User types `/pic-conflict [summary]`

**Key Code Sections:**

```markdown
### Step 4: Create Conflict Record

Write to `.pic/conflicts/CON-[NNN].md`
```

```markdown
### Step 7: Present to User

Display the conflict clearly and ask for decision:

Please indicate how you'd like to proceed:
1. Accept Position A
2. Accept Position B
3. Propose a different approach
```

**Cross-References:**
- Creates: [.pic/conflicts/CON-XXX.md](#directory-picconflicts)
- Updates: [.pic/state.json](#file-picstatejson)

---

#### File: .claude/skills/pic-integration/SKILL.md

**Purpose:** Run integration tests on multiple components.

**When Used:** User types `/pic-integration [components]`

**Key Code Sections:**

```markdown
### Step 5: Spawn Testing Agent

Use the Task tool with `subagent_type: "test-writer"`
```

```markdown
### Step 6: Record Results

Write to `.pic/integration-results/INT-[NNN].md`
```

**Cross-References:**
- Creates: [.pic/integration-results/INT-XXX.md](#directory-picintegration-results)
- Spawns: Testing agent

---

#### File: .claude/skills/pic-audit/SKILL.md

**Purpose:** View the comprehensive audit trail for the workflow.

**When Used:** User types `/pic-audit`

**Key Code Sections:**

```markdown
### Step 1: Read Audit Log

Read `.pic/audit-log.jsonl` and display formatted entries showing
agent executions, tool usage, and decision trail.
```

**Cross-References:**
- Reads: [.pic/audit-log.jsonl](#file-picaudit-logjsonl)
- Reads: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

#### File: .claude/skills/dependency-risk-planner/SKILL.md

**Purpose:** Pre-flight dependency risk assessment for the planning phase. Prevents dependency hell, version conflicts, and abandoned-library traps.

**When Used:** User types `/dependency-risk-planner [library-name or project-description]`

**Key Code Sections:**

```markdown
### Phase 1: Dependency Health Audit
- Maintainer viability check
- Dependency tree health
- Python/runtime compatibility
- API stability assessment

### Phase 2: Architecture Decisions
- Wrapper pattern for fragile APIs
- Import strategy for heavy dependencies
- Transitive dependency inventory
- Environment compatibility matrix

### Phase 3: Dependency Specification
- Pinning strategy per category
- Install script design checklist
- Documentation artifacts

### Phase 4: Test Planning
- Three test layers (smoke, unit, integration)
- Mock pattern documentation
- Dataclass/interface stability
```

**Cross-References:**
- Born from: [docs/avatar-pipeline/LESSONS_LEARNED.md](avatar-pipeline/LESSONS_LEARNED.md)
- Useful during: Planning phase of any PIC workflow

---

### The .claude/hooks/ Directory

Contains scripts that run automatically on events.

#### File: .claude/hooks/validate-pic-action.sh

**Purpose:** Log when agents are spawned.

**When Used:** Before any Task tool runs (PreToolUse).

**Full Code with Explanation:**

```bash
#!/bin/bash
# validate-pic-action.sh
# PreToolUse hook for Task tool - logs task spawns

TOOL_INPUT="$1"  # Receives the Task tool input as JSON
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Extract agent type from tool input using regex
# grep -oP uses Perl regex: find text after "subagent_type": "
AGENT_TYPE=$(echo "$TOOL_INPUT" | grep -oP '"subagent_type"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")

# Log the task spawn
if [ -f "$LOG_FILE" ]; then
    echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"task_spawn\", \"agent\": \"$AGENT_TYPE\"}" >> "$LOG_FILE"
fi

# Check if PIC system is initialized (optional warning)
if [ -f ".pic/state.json" ]; then
    INITIALIZED=$(cat .pic/state.json | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")

    if [ "$INITIALIZED" = "false" ]; then
        if [[ "$AGENT_TYPE" == pic-* ]]; then
            echo "Warning: PIC system not initialized." >&2
        fi
    fi
fi

# Always allow (exit 0 = success = allow the action)
exit 0
```

**Hook Execution Context:**

```
Task tool about to run
        │
        ▼
┌─────────────────────────┐
│ validate-pic-action.sh  │
│                         │
│ Input: $TOOL_INPUT      │
│ (JSON with agent info)  │
│                         │
│ Action: Log to jsonl    │
│                         │
│ Output: exit 0 (allow)  │
└────────────┬────────────┘
             │
             ▼
      Task tool runs
```

**Cross-References:**
- Registered in: [.claude/settings.json](#file-claudesettingsjson)
- Writes to: [.pic/status-log.jsonl](#file-picstatus-logjsonl)
- Reads: [.pic/state.json](#file-picstatejson)

---

#### File: .claude/hooks/on-decision-made.sh

**Purpose:** Detect and log when decision documents are created.

**When Used:** After any Write or Edit tool runs (PostToolUse).

**Full Code with Explanation:**

```bash
#!/bin/bash
# on-decision-made.sh
# PostToolUse hook for Write|Edit

TOOL_INPUT="$1"   # The tool's input (contains file path)
TOOL_OUTPUT="$2"  # The tool's output (what happened)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Extract file path from tool input
FILE_PATH=$(echo "$TOOL_INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' 2>/dev/null || echo "")

# Check if this is a decision document
if [[ "$FILE_PATH" == *".pic/decisions/DEC-"* ]]; then
    DECISION_ID=$(basename "$FILE_PATH" .md)  # Extract DEC-001 from path

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"decision_file_written\", \"decision\": \"$DECISION_ID\", \"path\": \"$FILE_PATH\"}" >> "$LOG_FILE"
    fi

    echo "Decision document created: $DECISION_ID"
fi

# Check for handoff documents
if [[ "$FILE_PATH" == *".pic/handoffs/"* ]]; then
    HANDOFF_FILE=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"handoff_file_written\", \"file\": \"$HANDOFF_FILE\"}" >> "$LOG_FILE"
    fi
fi

# Check for conflict documents
if [[ "$FILE_PATH" == *".pic/conflicts/CON-"* ]]; then
    CONFLICT_ID=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"conflict_file_written\", \"conflict\": \"$CONFLICT_ID\"}" >> "$LOG_FILE"
    fi
fi

# Check for integration results
if [[ "$FILE_PATH" == *".pic/integration-results/INT-"* ]]; then
    INT_ID=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"integration_result_written\", \"id\": \"$INT_ID\"}" >> "$LOG_FILE"
    fi
fi

exit 0
```

**Pattern Matching Explained:**

| Pattern | Matches |
|---------|---------|
| `*".pic/decisions/DEC-"*` | Any path containing `.pic/decisions/DEC-` |
| `basename "$FILE_PATH" .md` | Extracts filename without .md extension |

**Cross-References:**
- Registered in: [.claude/settings.json](#file-claudesettingsjson)
- Writes to: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

#### File: .claude/hooks/on-pic-handoff.sh

**Purpose:** Log when PIC agents complete.

**When Used:** When any agent stops (SubagentStop event).

**Full Code with Explanation:**

```bash
#!/bin/bash
# on-pic-handoff.sh
# SubagentStop hook for pic-* agents

AGENT_NAME="$1"   # Name of the agent that finished
AGENT_OUTPUT="$2" # Output from the agent
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Only process PIC agents
if [[ "$AGENT_NAME" != pic-* ]]; then
    exit 0
fi

# Log completion
if [ -f "$LOG_FILE" ]; then
    # Truncate output for logging (first 200 chars)
    OUTPUT_PREVIEW=$(echo "$AGENT_OUTPUT" | head -c 200 | tr '\n' ' ')
    echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"pic_agent_completed\", \"agent\": \"$AGENT_NAME\", \"output_preview\": \"$OUTPUT_PREVIEW\"}" >> "$LOG_FILE"
fi

# Map agent name to phase
case "$AGENT_NAME" in
    pic-research)     PHASE="research" ;;
    pic-planning)     PHASE="planning" ;;
    pic-design)       PHASE="design" ;;
    pic-implementation) PHASE="implementation" ;;
    pic-testing)      PHASE="testing" ;;
    pic-review)       PHASE="review" ;;
    *)                PHASE="unknown" ;;
esac

echo "PIC agent completed: $AGENT_NAME (phase: $PHASE)"

exit 0
```

**Cross-References:**
- Writes to: [.pic/status-log.jsonl](#file-picstatus-logjsonl)

---

#### File: .claude/hooks/notify-status.sh

**Purpose:** Inject PIC context into notifications.

**When Used:** On system notifications.

**Full Code with Explanation:**

```bash
#!/bin/bash
# notify-status.sh
# Notification hook - injects PIC context

NOTIFICATION_TYPE="$1"
NOTIFICATION_MESSAGE="$2"
STATE_FILE=".pic/state.json"

# Check if PIC system is active
if [ ! -f "$STATE_FILE" ]; then
    exit 0  # No PIC system, pass through
fi

# Read state
INITIALIZED=$(cat "$STATE_FILE" | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")

if [ "$INITIALIZED" = "false" ]; then
    exit 0
fi

# Extract current info
CURRENT_PHASE=$(cat "$STATE_FILE" | grep -oP '"currentPhase"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")
WORKFLOW=$(cat "$STATE_FILE" | grep -oP '"workflow"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")

# Add context to status notifications
if [ "$NOTIFICATION_TYPE" = "status" ]; then
    echo "[PIC: $WORKFLOW | Phase: $CURRENT_PHASE] $NOTIFICATION_MESSAGE"
else
    echo "$NOTIFICATION_MESSAGE"
fi

exit 0
```

**Cross-References:**
- Reads: [.pic/state.json](#file-picstatejson)

---

#### File: .claude/hooks/audit-tool-use.sh

**Purpose:** Log every tool invocation to the audit trail.

**When Used:** Before and after tool use (PreToolUse/PostToolUse).

**What It Does:**
Records every tool invocation with input/output to `.pic/audit-log.jsonl`, creating a comprehensive audit trail of all actions taken during a workflow.

**Cross-References:**
- Registered in: [.claude/settings.json](#file-claudesettingsjson)
- Writes to: `.pic/audit-log.jsonl`

---

### The .claude/rules/ Directory

Contains policy documents that agents reference.

#### File: .claude/rules/pic-coordination.md

**Purpose:** Defines how PICs coordinate.

**Key Sections:**

```markdown
## Core Principles

### 1. Decentralized Ownership
Each PIC owns their domain completely.

### 2. Clear Boundaries
| PIC | Can Do | Cannot Do |
|-----|--------|-----------|
| Research | Read, search | Write, execute |
| Implementation | Everything | Approve final |
| Review | Read, assess | Write, execute |

### 3. Sequential Phases
Phases proceed in order unless configured otherwise.
```

**Cross-References:**
- Referenced by: All agents in [.claude/agents/](#the-claudeagents-directory)

---

#### File: .claude/rules/decision-protocols.md

**Purpose:** Defines how decisions are made and documented.

**Key Sections:**

```markdown
## Decision Tiers

### Tier 1: Formal (DEC-XXX.md)
- Major choices
- Full rationale required
- Alternatives documented

### Tier 2: Lightweight (status log)
- Minor choices
- Brief rationale

### Tier 3: Implicit
- Following patterns
- No documentation needed
```

**Cross-References:**
- Referenced by: [.claude/skills/pic-decide/SKILL.md](#file-claudeskillspic-decideskillmd)

---

#### File: .claude/rules/conflict-resolution.md

**Purpose:** Defines how conflicts are resolved.

**Key Sections:**

```markdown
## Resolution Process

1. **Gather Positions** - What does each PIC recommend?
2. **Evaluate Evidence** - Which has stronger support?
3. **Synthesize if Possible** - Can we combine approaches?
4. **Decide if Clear** - If evidence favors one, proceed
5. **Escalate if Ambiguous** - Ask user via /pic-conflict
```

**Cross-References:**
- Referenced by: [.claude/agents/orchestrator.md](#file-claudeagentsorchestratormd)
- Referenced by: [.claude/skills/pic-conflict/SKILL.md](#file-claudeskillspic-conflictskillmd)

---

## File Relationships

### Relationship Diagram

```
                        ┌──────────────────┐
                        │ scripts/         │
                        │ pic-init.sh      │
                        └────────┬─────────┘
                                 │ creates
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                          .pic/                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ config.json │  │ state.json  │  │   status-log.jsonl      │ │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘ │
│         │                │                       │              │
│         │ defines        │ tracks                │ logs         │
│         │ phases         │ progress              │ events       │
│         ▼                ▼                       ▲              │
│  ┌─────────────────────────────────────────────┐ │              │
│  │           Runtime Documents                  │ │              │
│  │  decisions/  handoffs/  conflicts/  int*/   │─┘              │
│  └─────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────┘
                                 ▲
                                 │ read/write
                                 │
┌─────────────────────────────────────────────────────────────────┐
│                         .claude/                                 │
│                                                                  │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ settings.json│    │  agents/    │     │  skills/    │       │
│  │             │     │             │     │             │       │
│  │ hooks config│     │ instructions│     │ commands    │       │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘       │
│         │                   │                   │               │
│         │ triggers          │ guides            │ triggers      │
│         ▼                   ▼                   ▼               │
│  ┌─────────────┐     ┌─────────────┐                           │
│  │   hooks/    │     │   rules/    │                           │
│  │             │     │             │                           │
│  │ event       │     │ policies    │                           │
│  │ handlers    │     │             │                           │
│  └─────────────┘     └─────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### Who Reads/Writes What

| File | Read By | Written By |
|------|---------|------------|
| config.json | Skills, agents | pic-init.sh (once) |
| state.json | All skills | pic-start, pic-handoff, pic-decide |
| status-log.jsonl | pic-status | All hooks, all skills |
| decisions/*.md | pic-status, pic-review | pic-decide |
| handoffs/*.md | Next phase agent | pic-handoff |
| conflicts/*.md | User, orchestrator | pic-conflict |
| agents/*.md | Task spawning | Developer (manual) |
| skills/*.md | Claude Code | Developer (manual) |
| hooks/*.sh | settings.json | Developer (manual) |
| rules/*.md | Agents | Developer (manual) |

---

## Complete Workflow Walkthrough

Let's trace a complete workflow from start to finish.

### Step 1: User Runs /pic-start

```
User types: /pic-start Create a hello world script
```

**Files Involved:**

1. `.claude/skills/pic-start/SKILL.md` - Loaded and executed
2. `.pic/state.json` - Read (check for existing), then written (create workflow)
3. `.pic/config.json` - Read (get research agent type)
4. `.pic/status-log.jsonl` - Appended (workflow_started event)
5. `.claude/agents/pic-research.md` - Read (get instructions)

**State After:**
```json
{
  "initialized": true,
  "workflow": "WF-20260204-221758",
  "currentPhase": "research",
  "currentPIC": "pic-research"
}
```

### Step 2: Research PIC Runs

**Files Involved:**

1. `.claude/agents/pic-research.md` - Instructions followed
2. Project files - Read/searched for patterns
3. `.claude/hooks/validate-pic-action.sh` - Runs before any Task
4. `.pic/status-log.jsonl` - Hook appends task_spawn event

**Output:** Research summary with findings

### Step 3: Research Completes, Handoff to Planning

**Files Involved:**

1. `.claude/hooks/on-pic-handoff.sh` - Runs when Research PIC stops
2. `.pic/status-log.jsonl` - Appended (pic_agent_completed)
3. `.claude/skills/pic-handoff/SKILL.md` - Executed
4. `.pic/state.json` - Updated (research→completed, planning→in_progress)
5. `.pic/handoffs/` - Handoff record created
6. `.pic/config.json` - Read (get planning agent type)
7. `.claude/agents/pic-planning.md` - Read for next agent

### Step 4-6: Planning, Design, Implementation

Each follows the same pattern:
1. Agent runs following its instructions
2. Hooks log events
3. State updated on completion
4. Handoff record created
5. Next agent spawned

### Step 7: Testing PIC Runs

**Additional Files:**

1. `.claude/agents/pic-testing.md` - Test instructions
2. May create `.pic/integration-results/INT-001.md` if integration tests run

### Step 8: Review PIC Runs

**Files Involved:**

1. `.claude/agents/pic-review.md` - Review checklist
2. All previous phase outputs - Read for verification
3. `.pic/decisions/*.md` - Checked for documentation

### Step 9: Workflow Completes

**Files Updated:**

1. `.pic/state.json`:
   ```json
   {
     "currentPhase": "complete",
     "currentPIC": null,
     "completedAt": "2026-02-04T22:21:00Z"
   }
   ```

2. `.pic/status-log.jsonl`:
   ```json
   {"event": "workflow_completed", "result": "success"}
   ```

---

## File Quick Reference

### By Purpose

| Purpose | Files |
|---------|-------|
| Initialize system | `scripts/pic-init.sh` |
| Configure system | `.pic/config.json` |
| Track progress | `.pic/state.json` |
| Log events | `.pic/status-log.jsonl` |
| Document decisions | `.pic/decisions/*.md` |
| Record transitions | `.pic/handoffs/*.md` |
| Handle conflicts | `.pic/conflicts/*.md` |
| Define commands | `.claude/skills/*/SKILL.md` |
| Instruct agents | `.claude/agents/*.md` |
| Handle events | `.claude/hooks/*.sh` |
| Define policies | `.claude/rules/*.md` |
| Configure Claude | `.claude/settings.json` |

### By When Used

| When | Files |
|------|-------|
| First setup | `scripts/pic-init.sh` |
| Starting workflow | `pic-start/SKILL.md`, `state.json`, `config.json` |
| Planning dependencies | `dependency-risk-planner/SKILL.md` |
| During phases | `agents/*.md`, `hooks/*.sh`, `status-log.jsonl`, `audit-log.jsonl` |
| Making decisions | `pic-decide/SKILL.md`, `decisions/*.md` |
| Transitioning | `pic-handoff/SKILL.md`, `handoffs/*.md` |
| Checking status | `pic-status/SKILL.md`, `state.json` |
| Viewing audit trail | `pic-audit/SKILL.md`, `audit-log.jsonl` |
| Resolving conflicts | `pic-conflict/SKILL.md`, `conflicts/*.md` |
| Completing | `state.json`, `status-log.jsonl` |

### File Counts

| Directory | File Count | Purpose |
|-----------|------------|---------|
| `scripts/` | 2 | Utilities |
| `.pic/` | 4 files + 4 dirs | Runtime state |
| `.claude/agents/` | 7 | Agent instructions |
| `.claude/skills/` | 8 | User commands |
| `.claude/hooks/` | 5 | Event handlers |
| `.claude/rules/` | 3 | Policies |
| `.claude/` root | 1 | Settings |
| **Total** | **30 files** | |

---

## Summary

The PIC system is organized into three directories:

1. **scripts/** - Setup utilities (run once)
2. **.pic/** - Runtime state (changes during workflows)
3. **.claude/** - Behavior configuration (defines how system works)

**Key Relationships:**
- `config.json` defines what agents exist
- `state.json` tracks current progress
- `status-log.jsonl` records all events
- `settings.json` connects hooks to events
- Skills read config and update state
- Hooks log events to the log
- Agents follow instructions from agents/ files

**To understand any file:**
1. Check its purpose in this document
2. Look at what files it reads/writes
3. Trace when it's used in a workflow

With this knowledge, you can understand, modify, and extend any part of the system.
