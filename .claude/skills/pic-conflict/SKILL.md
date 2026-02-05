---
name: pic-conflict
description: Escalate a conflict between PICs to the user for resolution
args: "[conflict summary]"
---

# PIC Conflict Escalation

You are escalating a conflict to the user for resolution. Follow this protocol exactly.

## Input

Conflict summary: `$ARGS`

If no summary was provided, ask the user to describe the conflict.

## When to Use This Skill

This skill is used when:
1. Two or more PICs have conflicting recommendations
2. Evidence doesn't clearly favor one position
3. Synthesis of positions isn't possible
4. A decision requires human judgment

## Protocol

### Step 1: Verify Workflow State

Read `.pic/state.json` to verify a workflow is active.

**If no workflow:**
```
No active workflow. Conflicts can only be recorded within a workflow.
```
And stop.

### Step 2: Generate Conflict ID

Read existing conflicts in `.pic/conflicts/` to determine the next ID.

Format: `CON-[NNN]` where NNN is zero-padded (e.g., CON-001)

### Step 3: Gather Conflict Details

Collect or ask for:

1. **Parties**: Which PICs or positions are in conflict
2. **Summary**: Brief description of the disagreement
3. **Position A**: First position with supporting evidence
4. **Position B**: Second position with supporting evidence
5. **Stakes**: What depends on this decision
6. **Attempted Resolution**: What was tried before escalation

### Step 4: Create Conflict Record

Write to `.pic/conflicts/CON-[NNN].md`:

```markdown
# CON-[NNN]: [Brief Title]

**Date**: [ISO date]
**Workflow**: [workflow id]
**Phase**: [current phase]
**Status**: Open

## Summary

[Brief description of the conflict]

## Conflicting Positions

### Position A: [Name/Source]

**Advocate**: [Which PIC or entity]

**Position**: [What they recommend]

**Evidence**:
- [Supporting evidence 1]
- [Supporting evidence 2]

**Rationale**: [Why they believe this is correct]

### Position B: [Name/Source]

**Advocate**: [Which PIC or entity]

**Position**: [What they recommend]

**Evidence**:
- [Supporting evidence 1]
- [Supporting evidence 2]

**Rationale**: [Why they believe this is correct]

## Analysis

### Points of Agreement
- [What both sides agree on]

### Core Disagreement
[The fundamental issue causing conflict]

### Stakes
[What depends on this decision being made correctly]

## Attempted Resolution

[What was tried before escalation]

## Options for Resolution

### Option 1: Accept Position A
- **Impact**: [What happens if we choose this]
- **Risk**: [Potential downsides]

### Option 2: Accept Position B
- **Impact**: [What happens if we choose this]
- **Risk**: [Potential downsides]

### Option 3: Synthesis (if possible)
- **Approach**: [How to combine elements of both]
- **Trade-offs**: [What we give up]

## User Decision Required

Please review the positions above and indicate your decision:
- [ ] Accept Position A
- [ ] Accept Position B
- [ ] Accept Synthesis
- [ ] Provide alternative direction

---

## Resolution (to be filled after user decision)

**Decision**: [pending]
**Rationale**: [pending]
**Decided By**: [pending]
**Date**: [pending]
```

### Step 5: Update State

Add conflict reference to `.pic/state.json` conflicts array:

```json
{
  "id": "CON-[NNN]",
  "summary": "[summary]",
  "phase": "[current phase]",
  "status": "open",
  "timestamp": "[ISO]"
}
```

### Step 6: Log Conflict

Append to `.pic/status-log.jsonl`:

```json
{"timestamp": "[ISO]", "event": "conflict_escalated", "conflict": "CON-[NNN]", "summary": "[summary]"}
```

### Step 7: Present to User

Display the conflict clearly:

```
## Conflict Escalation

A conflict requires your input to proceed.

**ID**: CON-[NNN]
**Phase**: [current phase]

### The Disagreement
[Clear statement of what's in conflict]

### Position A: [Name]
[Summary of position with key evidence]

### Position B: [Name]
[Summary of position with key evidence]

### What's at Stake
[Why this decision matters]

---

Please indicate how you'd like to proceed:
1. Accept Position A
2. Accept Position B
3. Propose a different approach

Your decision will be recorded and the workflow will continue accordingly.
```

## Resolution Recording

When the user provides a decision:

1. Update the conflict record with the resolution
2. Update state to mark conflict as `resolved`
3. Log the resolution
4. Communicate the decision to relevant PICs
5. Continue the workflow

## Blocking Behavior

While a conflict is open and unresolved:
- The workflow should pause on decisions that depend on the conflict
- Other independent work can continue
- The conflict status should be shown in `/pic-status`

## Error Handling

- If conflicts directory doesn't exist, create it
- If unable to write, report the error
- Always present the conflict to the user even if logging fails
