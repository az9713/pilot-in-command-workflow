# Decision Protocols

These protocols govern how decisions are made and documented in the PIC workflow system.

## Decision Tiers

### Tier 1: Formal Decisions (DEC-XXX)

**When to use:**
- Major architectural choices
- Technology selections
- Significant trade-offs
- Decisions affecting multiple phases
- Irreversible or costly-to-reverse choices

**Requirements:**
- Full decision document in `.pic/decisions/`
- Minimum 2 alternatives considered
- Explicit rationale
- Evidence supporting the choice
- Documented consequences

**Format:** See `/pic-decide` skill

### Tier 2: Lightweight Decisions (Status Log)

**When to use:**
- Implementation choices within established patterns
- Minor trade-offs
- Decisions with obvious answers
- Reversible choices

**Requirements:**
- Entry in `.pic/status-log.jsonl`
- Brief rationale
- Can be promoted to Tier 1 if contested

**Format:**
```json
{"timestamp": "...", "event": "decision", "title": "...", "choice": "...", "rationale": "..."}
```

### Tier 3: Implicit Decisions

**When to use:**
- Following established patterns
- Standard practices
- Obvious choices

**Requirements:**
- No documentation needed
- Can be questioned and promoted to higher tier

## Decision Authority

### By Phase

| Phase | Can Decide | Must Escalate |
|-------|------------|---------------|
| Research | What to investigate | Scope changes |
| Planning | Strategy, milestones | Major constraints |
| Design | Architecture, interfaces | Technology choices |
| Implementation | Code structure | Design changes |
| Testing | Test approach | Blocking bugs |
| Review | Approval/rejection | Scope disputes |

### Escalation Triggers

A decision must be escalated when:

1. **Cross-phase impact**: Decision affects another PIC's domain
2. **Conflict**: Disagreement between PICs
3. **Uncertainty**: Insufficient evidence for confident choice
4. **Irreversibility**: High cost to change later
5. **Policy**: User has requested involvement

## Decision-Making Process

### Step 1: Identify the Decision

- What exactly needs to be decided?
- What tier does it fall into?
- Who has authority to decide?

### Step 2: Gather Information

- What evidence exists?
- What are the alternatives?
- What are the trade-offs?

### Step 3: Evaluate Options

Apply these criteria:

| Criterion | Question |
|-----------|----------|
| Feasibility | Can we actually do this? |
| Alignment | Does it fit the problem? |
| Risk | What could go wrong? |
| Reversibility | How hard to change later? |
| Evidence | What supports this choice? |

### Step 4: Make the Decision

- Choose based on evidence
- Document the rationale
- Note what you're trading off

### Step 5: Communicate

- Update relevant state
- Log the decision
- Inform affected parties

## Evidence Standards

Decisions should be supported by evidence:

### Strong Evidence

- Empirical data (tests, benchmarks)
- Documented requirements
- Prior art with proven success
- Multiple independent sources

### Moderate Evidence

- Expert opinion with rationale
- Single reliable source
- Analogous situations

### Weak Evidence

- Intuition (must be acknowledged)
- Single anecdote
- Untested assumptions

### Evidence Requirements by Tier

| Tier | Minimum Evidence |
|------|------------------|
| Formal | 2+ pieces of moderate or strong evidence |
| Lightweight | 1 piece of evidence or clear rationale |
| Implicit | Established pattern |

## Reversing Decisions

Decisions can be revisited when:

1. **New evidence** emerges that changes the calculus
2. **Implementation** reveals unforeseen issues
3. **Requirements** change
4. **Escalation** by another PIC

### Reversal Process

1. Document why reversal is needed
2. Reference the original decision
3. Follow the same decision process
4. Create new decision document (referencing the old)

## Anti-Patterns

### Avoid These

| Anti-Pattern | Better Approach |
|--------------|-----------------|
| Deciding without evidence | Gather evidence first |
| Deciding outside your domain | Escalate or defer |
| Undocumented decisions | Log at appropriate tier |
| Revisiting settled decisions without cause | Accept and move on |
| Analysis paralysis | Set decision deadline |
| Premature optimization | Decide what matters now |

## Templates

### Quick Decision Log Entry

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event": "decision",
  "title": "Use PostgreSQL for user data",
  "choice": "PostgreSQL",
  "alternatives": ["MySQL", "MongoDB"],
  "rationale": "Team expertise + ACID requirements"
}
```

### Full Decision Document

See `.pic/decisions/` for template (created by `/pic-decide`).
