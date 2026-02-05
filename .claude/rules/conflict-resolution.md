# Conflict Resolution Rules

These rules govern how conflicts between PICs are identified, analyzed, and resolved.

## What Constitutes a Conflict

A conflict exists when:

1. **Contradictory Positions**: Two PICs recommend mutually exclusive approaches
2. **Resource Contention**: Multiple demands on limited resources
3. **Scope Disputes**: Disagreement about ownership boundaries
4. **Evidence Disagreement**: Different interpretations of the same data
5. **Priority Conflicts**: Competing urgent needs

## Conflict Categories

### Category A: Technical Disagreements

Different views on how to solve a technical problem.

**Examples:**
- Design PIC wants microservices, Implementation PIC prefers monolith
- Testing PIC requires 90% coverage, Implementation PIC says 70% is sufficient

**Resolution Path:** Evidence-based evaluation → Orchestrator synthesis → User escalation

### Category B: Scope Disputes

Disagreement about who owns what or what's in/out of scope.

**Examples:**
- Research PIC investigating implementation details
- Implementation PIC making design decisions

**Resolution Path:** Refer to coordination rules → Orchestrator arbitration → User escalation

### Category C: Priority Conflicts

Competing demands that can't all be satisfied.

**Examples:**
- Speed vs. quality trade-offs
- Feature A vs. Feature B with limited time

**Resolution Path:** Stakeholder input → User decision

### Category D: Process Disputes

Disagreement about how work should proceed.

**Examples:**
- Skip testing for urgent fix?
- Revisit design after implementation started?

**Resolution Path:** Refer to protocols → Orchestrator decision → User escalation

## Resolution Process

### Step 1: Identify the Conflict

When a conflict is detected:

1. Document the conflicting positions
2. Identify the category
3. Note the stakes (what depends on resolution)
4. Assign conflict ID (CON-XXX)

### Step 2: Gather Positions

For each party in the conflict:

1. **Position**: What they recommend
2. **Evidence**: What supports their view
3. **Rationale**: Why they believe this is correct
4. **Stakes**: What they stand to lose if overruled

### Step 3: Orchestrator Analysis

The Orchestrator attempts resolution by:

1. **Finding Common Ground**: What do both sides agree on?
2. **Evaluating Evidence**: Which position has stronger support?
3. **Seeking Synthesis**: Can positions be combined?
4. **Assessing Consequences**: What happens with each choice?

### Step 4: Resolution Attempt

#### If Evidence Clearly Favors One Side

- Document the decision with rationale
- Note the override with respect
- Proceed with the winning position

#### If Synthesis Is Possible

- Create a hybrid approach
- Verify both parties can accept it
- Document the compromise

#### If Resolution Is Unclear

- Escalate to user via `/pic-conflict`
- Provide clear summary of positions
- Present options without bias

### Step 5: Document Resolution

Update the conflict record with:

- Decision made
- Rationale for decision
- Who decided
- Timestamp

Log the resolution in status-log.jsonl.

## Escalation to User

### When to Escalate

Escalate when:

1. Evidence doesn't clearly favor either position
2. Trade-offs require value judgments
3. Stakes are high and irreversible
4. Parties cannot accept Orchestrator's synthesis
5. Conflict category requires stakeholder input

### How to Escalate

Use the `/pic-conflict` skill to:

1. Present the conflict clearly
2. Summarize each position fairly
3. Show evidence for both sides
4. Offer concrete options
5. Await user decision

### After User Decision

1. Record the decision in conflict document
2. Communicate to affected PICs
3. Update workflow state
4. Continue with resolved direction

## Conflict Prevention

### Best Practices

1. **Clear Boundaries**: Respect domain ownership
2. **Early Alignment**: Discuss assumptions during handoffs
3. **Evidence First**: Gather data before forming positions
4. **Collaborative Mindset**: Seek understanding, not victory

### Warning Signs

Address these early to prevent conflicts:

| Warning Sign | Action |
|--------------|--------|
| Scope creep | Clarify boundaries |
| Undocumented assumptions | Make explicit |
| Missing handoff context | Request clarification |
| Rushed decisions | Slow down, gather evidence |

## Resolution Principles

### Fairness

- Hear all positions fully
- Evaluate evidence objectively
- Don't favor based on seniority or phase order

### Transparency

- Document the conflict and resolution
- Explain the rationale
- Acknowledge trade-offs

### Finality

- Once resolved, move forward
- Don't relitigate without new evidence
- Accept decisions with grace

### Learning

- Identify root causes
- Update processes if needed
- Prevent similar conflicts

## Anti-Patterns

### Avoid These

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Avoiding conflict | Issues fester | Address early |
| Power plays | Damages collaboration | Use evidence |
| Endless debate | Blocks progress | Set deadline, escalate |
| Grudges | Poisons future work | Accept and move on |
| Secret decisions | Erodes trust | Document openly |

## Conflict Record Template

See `.pic/conflicts/` for full template (created by `/pic-conflict`).

### Minimum Required Fields

```markdown
# CON-XXX: [Title]

**Status**: Open/Resolved
**Category**: [A/B/C/D]
**Parties**: [PICs involved]

## Positions
[Summary of each position]

## Resolution
[Decision and rationale]
```
