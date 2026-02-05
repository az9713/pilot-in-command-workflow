---
name: pic-status
description: Display current PIC workflow status and progress
args: ""
---

# PIC Status Display

You are displaying the current status of the PIC workflow. Follow this protocol exactly.

## Protocol

### Step 1: Read Current State

Read `.pic/state.json` to get the current workflow state.

**If no workflow is initialized:**
Display:
```
## No Active Workflow

No PIC workflow is currently active. Use `/pic-start [problem]` to begin a new workflow.
```
And stop.

### Step 2: Read Recent Activity

Read the last 10 lines of `.pic/status-log.jsonl` to get recent activity.

### Step 3: Display Status

Format and display the status:

```
## PIC Workflow Status

**Workflow ID**: [workflow id]
**Problem**: [problem statement]
**Started**: [timestamp]

### Phase Progress

| Phase | Status | Started | Completed |
|-------|--------|---------|-----------|
| Research | [status emoji] [status] | [time or -] | [time or -] |
| Planning | [status emoji] [status] | [time or -] | [time or -] |
| Design | [status emoji] [status] | [time or -] | [time or -] |
| Implementation | [status emoji] [status] | [time or -] | [time or -] |
| Testing | [status emoji] [status] | [time or -] | [time or -] |
| Review | [status emoji] [status] | [time or -] | [time or -] |

### Current Phase
**[Phase Name]** - [PIC agent name]

[Brief description of what this phase does]

### Recent Activity
[Last 5 events from status log, formatted nicely]

### Decisions Made
[Count] decisions recorded. Use `/pic-decide` to view or add decisions.

### Conflicts
[Count] conflicts recorded. [If any active, note them]
```

## Status Indicators

Use these indicators for phase status:

| Status | Display |
|--------|---------|
| pending | `[ ]` Pending |
| in_progress | `[>]` In Progress |
| completed | `[x]` Completed |
| blocked | `[!]` Blocked |
| skipped | `[-]` Skipped |

## Phase Descriptions

| Phase | Description |
|-------|-------------|
| research | Gathering information and evidence |
| planning | Creating strategic roadmap and milestones |
| design | Defining technical architecture and interfaces |
| implementation | Writing code and building features |
| testing | Validating and integration testing |
| review | Final quality review and approval |

## Additional Information

If there are active decisions or conflicts, mention them prominently.

If the workflow is complete, display a completion summary instead.

## Read-Only

This skill only reads and displays information. It does not modify any state.

## Error Handling

- If state file is corrupted, report the issue
- If log file is missing, note that no activity has been logged
- If config is invalid, suggest running `/pic-start` to reinitialize
