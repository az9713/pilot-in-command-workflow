# PIC Coordination Rules

These rules govern how PICs (Pilots in Command) coordinate within the agentic workflow system.

## Core Principles

### 1. Decentralized Ownership

Each PIC owns their domain completely:

- **Research PIC** owns information gathering
- **Planning PIC** owns strategic roadmap
- **Design PIC** owns technical architecture
- **Implementation PIC** owns code execution
- **Testing PIC** owns validation
- **Review PIC** owns quality approval

No PIC may override another PIC's domain decisions without going through the conflict resolution process.

### 2. Clear Boundaries

PICs operate within strict boundaries:

| PIC | Can Do | Cannot Do |
|-----|--------|-----------|
| Research | Read, search, gather | Write, edit, execute |
| Planning | Read, write plans | Execute code, test |
| Design | Read, write specs | Execute code, test |
| Implementation | Read, write, execute | Test beyond unit, approve |
| Testing | Read, write tests, execute | Implement features, approve |
| Review | Read, assess | Write, edit, execute |

### 3. Sequential Phases

Phases proceed in order unless explicitly configured otherwise:

```
Research → Planning → Design → Implementation → Testing → Review
```

Phase skipping requires:
1. Explicit configuration in `.pic/config.json`
2. Documented rationale
3. Acknowledgment of risks

## Coordination Protocols

### Phase Transitions

1. Current PIC signals completion
2. Orchestrator validates exit criteria
3. Handoff record is created
4. State is updated
5. Next PIC is spawned with context

### Parallel Work

Within a phase, the owning PIC may delegate sub-tasks:

- **Allowed**: Parallel implementation of independent components
- **Allowed**: Parallel testing of different scenarios
- **Not Allowed**: Parallel work across phase boundaries
- **Not Allowed**: Circumventing the phase sequence

### Information Flow

Information flows forward through handoffs:

```
Research findings → Planning → Design → Implementation → Testing → Review
```

Backward information flow requires explicit escalation:

```
If Testing finds design flaw → Escalate to Orchestrator → May revisit Design
```

## Communication Rules

### Between PICs

PICs do not communicate directly. All coordination goes through:

1. **Handoff documents** (`.pic/handoffs/`)
2. **Decision documents** (`.pic/decisions/`)
3. **State file** (`.pic/state.json`)
4. **Orchestrator** (for conflict resolution)

### With Orchestrator

PICs communicate with the Orchestrator by:

1. Signaling phase completion
2. Escalating conflicts
3. Requesting clarification on scope

### With User

PICs do not communicate directly with users. User interaction goes through:

1. **Skills** (user-invocable commands)
2. **Orchestrator** (conflict escalation)
3. **Status displays** (`/pic-status`)

## Accountability

### Ownership Records

Every artifact must have clear ownership:

- Decision documents note the deciding PIC
- Code changes are attributed to Implementation PIC
- Test results are attributed to Testing PIC

### Audit Trail

All significant actions are logged:

- `.pic/status-log.jsonl` for activity
- `.pic/decisions/` for decisions
- `.pic/handoffs/` for transitions
- `.pic/conflicts/` for escalations

## Violation Handling

If a PIC violates these rules:

1. **Minor violation**: Log warning, continue
2. **Major violation**: Pause workflow, alert Orchestrator
3. **Critical violation**: Halt workflow, escalate to user

Examples:

- **Minor**: Planning PIC reads implementation code (allowed but unusual)
- **Major**: Implementation PIC modifies design docs
- **Critical**: Testing PIC deploys to production
