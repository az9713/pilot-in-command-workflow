---
name: pic-handoff
description: Execute a phase transition from current PIC to next PIC
args: "[handoff notes]"
---

# PIC Phase Handoff

You are executing a phase transition in the PIC workflow. Follow this protocol exactly.

## Input

Handoff notes provided: `$ARGS`

## Protocol

### Step 1: Verify Workflow State

Read `.pic/state.json` to get current workflow state.

**If no workflow:**
```
No active workflow. Use `/pic-start [problem]` first.
```
And stop.

**If workflow is complete:**
```
Workflow [id] is already complete. All phases have finished.
```
And stop.

### Step 2: Read Configuration

Read `.pic/config.json` to get:
- Phase order
- Handoff requirements

### Step 3: Validate Current Phase

Determine the current phase and PIC. Validate that:
- The current phase is marked as `in_progress`
- Handoff is being requested appropriately

### Step 4: Determine Next Phase

Look up the next phase in the configured order.

**If current phase is 'review' (final phase):**
- This is workflow completion, not a handoff
- Mark workflow as complete
- Skip to completion protocol below

### Step 5: Create Handoff Record

Write to `.pic/handoffs/[workflow]-[from]-to-[to].md`:

```markdown
# Handoff: [From Phase] → [To Phase]

**Workflow**: [workflow id]
**Timestamp**: [ISO timestamp]
**From PIC**: [from agent]
**To PIC**: [to agent]

## Phase Summary

### Completed Work
[Summary of what the outgoing PIC accomplished]

### Deliverables
- [List of artifacts produced]

### Handoff Notes
[User-provided notes: $ARGS]

## Context for Next Phase

### Key Findings
[Important information for the next PIC]

### Open Questions
[Unresolved items the next PIC should address]

### Risks/Concerns
[Issues to be aware of]

## Exit Criteria Verification

| Criterion | Status |
|-----------|--------|
| [Expected deliverable] | [Met/Not Met] |
```

### Step 6: Update State

Update `.pic/state.json`:

1. Mark current phase as `completed` with timestamp
2. Mark next phase as `in_progress` with timestamp
3. Update `currentPhase` and `currentPIC`
4. Add handoff to `handoffs` array

### Step 7: Log Handoff

Append to `.pic/status-log.jsonl`:

```json
{"timestamp": "[ISO]", "event": "phase_handoff", "from": "[from phase]", "to": "[to phase]", "notes": "[notes]"}
```

### Step 8: Display Handoff Summary

```
## Phase Transition Complete

**From**: [From Phase] ([from PIC])
**To**: [To Phase] ([to PIC])

### [From Phase] Summary
[Brief summary of completed work]

### [To Phase] Objectives
[What the next PIC should focus on]

### Handoff Record
Saved to: .pic/handoffs/[filename]

The [To Phase] PIC is now active.
```

### Step 9: Spawn Next PIC

Read `.pic/config.json` to get the `taskAgentType` for the next phase.
Read the corresponding instructions file from `.claude/agents/pic-[phase].md`.

Use the Task tool with:
- **subagent_type**: The `taskAgentType` from config (e.g., `planner`, `builder`, `reviewer`)
- **prompt**: Include PIC instructions + context from:
  - The problem statement
  - Relevant deliverables from completed phases
  - Handoff notes
  - Any decisions made

### Agent Type Mapping (from config)

| Phase | taskAgentType |
|-------|---------------|
| research | Explore |
| planning | planner |
| design | planner |
| implementation | builder |
| testing | test-writer |
| review | reviewer |

## Workflow Completion Protocol

If transitioning from Review (final phase):

1. Update state to mark workflow complete
2. Create completion summary
3. Display:

```
## Workflow Complete

**Workflow ID**: [id]
**Problem**: [problem]
**Duration**: [time from start to finish]

### Phase Summary
| Phase | Duration | Decisions |
|-------|----------|-----------|
| [phase] | [duration] | [count] |
...

### Deliverables
[List of all artifacts produced]

### Final Status
All phases completed successfully.

Use `/pic-start` to begin a new workflow.
```

## Validation

Before executing handoff:
- Verify current PIC has signaled readiness
- Check that required deliverables exist
- If `requireHandoffApproval` is true in config, ask user to confirm

## Error Handling

- If state update fails, report error and don't spawn next PIC
- If next phase doesn't exist in config, report configuration error
- If handoff file can't be written, log to status-log instead
