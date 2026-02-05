---
name: pic-start
description: Initialize a new PIC (Pilot in Command) workflow with a problem statement
args: "[problem description]"
---

# PIC Workflow Initialization

You are initializing a new PIC agentic workflow. Follow this protocol exactly.

## Input

The user has provided a problem statement: `$ARGS`

If no problem was provided, ask the user to describe the problem they want to solve.

## Initialization Protocol

### Step 1: Verify System State

Read `.pic/state.json` to check if a workflow is already in progress.

**If a workflow exists and is not complete:**
- Warn the user that an active workflow exists
- Ask if they want to: (a) resume the existing workflow, (b) abandon it and start fresh
- If abandoning, archive the current state before proceeding

**If no active workflow or user confirms fresh start:**
- Continue to Step 2

### Step 2: Initialize State

Update `.pic/state.json` with:

```json
{
  "initialized": true,
  "workflow": "WF-[timestamp]",
  "currentPhase": "research",
  "currentPIC": "pic-research",
  "problem": "[user's problem statement]",
  "startedAt": "[ISO timestamp]",
  "phases": {
    "research": { "status": "in_progress", "startedAt": "[ISO timestamp]", "completedAt": null },
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
```

### Step 3: Log Initialization

Append to `.pic/status-log.jsonl`:

```json
{"timestamp": "[ISO]", "event": "workflow_started", "workflow": "WF-[id]", "problem": "[problem]"}
```

### Step 4: Confirm to User

Display:

```
## PIC Workflow Initialized

**Workflow ID**: WF-[id]
**Problem**: [problem statement]
**Current Phase**: Research
**Current PIC**: pic-research

The Research PIC will now gather information and evidence related to your problem.

### Workflow Phases
1. **Research** ← Current
2. Planning
3. Design
4. Implementation
5. Testing
6. Review

Use `/pic-status` to check progress at any time.
```

### Step 5: Spawn Research PIC

Read `.pic/config.json` to get the `taskAgentType` for the research phase (should be `Explore`).

Read `.claude/agents/pic-research.md` to get the PIC instructions.

Use the Task tool with:

**subagent_type:** `Explore` (from config.pics.definitions.research.taskAgentType)

**Prompt:**
```
You are the Research PIC for workflow [WF-id].

[Include key instructions from .claude/agents/pic-research.md]

## Problem Statement
[user's problem]

## Your Mission
Gather information, collect evidence, and build the knowledge foundation for this problem.

When complete, provide your research summary and signal readiness for handoff to the Planning PIC.
```

## Error Handling

- If `.pic/` directory doesn't exist, run `./scripts/pic-init.sh` first
- If config is invalid, report the issue and suggest running init
- If unable to write state, report the error to the user

## Important

- Always read current state before modifying
- Generate unique workflow IDs using timestamp
- Log all state changes
- The Orchestrator manages the full workflow - this skill just initializes it
