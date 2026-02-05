---
name: pic-decide
description: Record a formal decision document with rationale and alternatives
args: "[decision title]"
---

# PIC Decision Recording

You are recording a formal decision for the PIC workflow. Follow this protocol exactly.

## Input

The user wants to record a decision titled: `$ARGS`

If no title was provided, ask the user what decision they want to document.

## Protocol

### Step 1: Verify Workflow State

Read `.pic/state.json` to verify a workflow is active.

**If no workflow:**
```
No active workflow. Use `/pic-start [problem]` first.
```
And stop.

### Step 2: Generate Decision ID

Read existing decisions in `.pic/decisions/` to determine the next ID.

Format: `DEC-[NNN]` where NNN is zero-padded (e.g., DEC-001, DEC-002)

### Step 3: Gather Decision Details

Ask the user for (if not already provided):

1. **Decision Title**: What is being decided
2. **Context**: Why this decision is needed
3. **Options Considered**: What alternatives were evaluated
4. **Decision**: What was chosen
5. **Rationale**: Why this option was selected
6. **Consequences**: What this decision enables or constrains
7. **Evidence**: Data or findings supporting this decision

### Step 4: Create Decision Document

Write to `.pic/decisions/DEC-[NNN].md`:

```markdown
# DEC-[NNN]: [Title]

**Date**: [ISO date]
**Workflow**: [workflow id]
**Phase**: [current phase]
**Status**: Accepted

## Context

[Why this decision is needed]

## Decision

[What was decided]

## Options Considered

### Option 1: [Name]
- **Pros**: [advantages]
- **Cons**: [disadvantages]

### Option 2: [Name]
- **Pros**: [advantages]
- **Cons**: [disadvantages]

[... more options as needed ...]

## Rationale

[Why this option was selected over others]

## Evidence

[Data, research findings, or other evidence supporting this decision]

## Consequences

### Enables
- [What this decision makes possible]

### Constrains
- [What this decision limits or prevents]

## Related Decisions

- [Links to related DEC-XXX documents, if any]
```

### Step 5: Update State

Add decision reference to `.pic/state.json` decisions array:

```json
{
  "id": "DEC-[NNN]",
  "title": "[title]",
  "phase": "[current phase]",
  "timestamp": "[ISO]"
}
```

### Step 6: Log Decision

Append to `.pic/status-log.jsonl`:

```json
{"timestamp": "[ISO]", "event": "decision_recorded", "decision": "DEC-[NNN]", "title": "[title]", "phase": "[phase]"}
```

### Step 7: Confirm to User

Display:

```
## Decision Recorded

**ID**: DEC-[NNN]
**Title**: [title]
**File**: .pic/decisions/DEC-[NNN].md

The decision has been formally documented. It can be referenced by other phases and will be included in the final review.
```

## Viewing Existing Decisions

If the user runs `/pic-decide` without arguments and there are existing decisions, offer to:
1. Create a new decision
2. List existing decisions
3. View a specific decision

## Decision Quality Standards

Per the config, decisions should include:
- Clear rationale (required)
- Alternatives considered (required)
- Supporting evidence (recommended)

If the user's input is missing required elements, prompt for them.

## Error Handling

- If decisions directory doesn't exist, create it
- If unable to write, report the error
- If state update fails, note the decision was created but state wasn't updated
