# Architecture Guide

This document explains the internal architecture of the PIC Agentic Organizational System. It's intended for developers who want to understand how the system works at a deeper level.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [State Management](#state-management)
5. [Agent Architecture](#agent-architecture)
6. [Coordination Model](#coordination-model)
7. [Extension Points](#extension-points)
8. [Design Decisions](#design-decisions)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│                    (Claude Code CLI + Skills)                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          ORCHESTRATION LAYER                         │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │
│  │   Skills    │  │ Orchestrator│  │    Hooks    │                  │
│  │ (Commands)  │  │  (Coord.)   │  │  (Events)   │                  │
│  └─────────────┘  └─────────────┘  └─────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            AGENT LAYER                               │
│                                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Research │ │ Planning │ │  Design  │ │  Impl.   │ │ Testing  │  │
│  │   PIC    │ │   PIC    │ │   PIC    │ │   PIC    │ │   PIC    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                                      │
│                              ┌──────────┐                           │
│                              │  Review  │                           │
│                              │   PIC    │                           │
│                              └──────────┘                           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         PERSISTENCE LAYER                            │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │ config.json │  │ state.json  │  │     status-log.jsonl        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐ │
│  │ decisions/  │  │  handoffs/  │  │  integration-results/       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Interaction

```
User Input ──▶ Skill ──▶ State Update ──▶ Agent Spawn ──▶ Work ──▶ Handoff
     ▲                                                               │
     │                                                               │
     └────────────────────── Next Phase ◀────────────────────────────┘
```

---

## Core Components

### 1. Skills (User Commands)

**Location:** `.claude/skills/*/SKILL.md`

**Purpose:** Handle user commands and translate them into system actions.

**Structure:**
```
.claude/skills/
├── pic-start/SKILL.md      # Start new workflow
├── pic-status/SKILL.md     # Show status
├── pic-decide/SKILL.md     # Record decision
├── pic-handoff/SKILL.md    # Phase transition
├── pic-conflict/SKILL.md   # Escalate conflict
└── pic-integration/SKILL.md # Run integration test
```

**Skill Lifecycle:**
```
1. User types /command
2. Claude Code loads SKILL.md
3. Skill instructions execute
4. State is modified
5. Agents may be spawned
```

### 2. Agents (Workers)

**Location:** `.claude/agents/*.md`

**Purpose:** Perform the actual work for each phase.

**Agent Types:**
| Agent File | Claude Code Type | Role |
|------------|------------------|------|
| pic-research.md | Explore | Information gathering |
| pic-planning.md | planner | Strategy creation |
| pic-design.md | planner | Architecture design |
| pic-implementation.md | builder | Code writing |
| pic-testing.md | test-writer | Validation |
| pic-review.md | reviewer | Quality check |
| orchestrator.md | orchestrator | Coordination |

**Agent Lifecycle:**
```
1. Config lookup for taskAgentType
2. Instructions loaded from file
3. Task spawned with context
4. Agent performs work
5. Agent signals completion
6. Results captured
```

### 3. Hooks (Event Handlers)

**Location:** `.claude/hooks/*.sh`

**Purpose:** React to system events automatically.

**Available Hooks:**
| Hook | Trigger | Purpose |
|------|---------|---------|
| validate-pic-action.sh | Before Task | Log agent spawns |
| on-decision-made.sh | After Write/Edit | Log file changes |
| on-pic-handoff.sh | Agent completion | Log phase transitions |
| notify-status.sh | Notifications | Inject context |

**Hook Execution:**
```
Event Occurs ──▶ Hook Triggered ──▶ Script Runs ──▶ Logs Updated
```

### 4. Rules (Policies)

**Location:** `.claude/rules/*.md`

**Purpose:** Define coordination policies that agents follow.

**Rule Files:**
| File | Content |
|------|---------|
| pic-coordination.md | Phase boundaries, handoff rules |
| decision-protocols.md | How to make/document decisions |
| conflict-resolution.md | How to handle disagreements |

---

## Data Flow

### Workflow Start Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     /pic-start "Build X"                          │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                     pic-start/SKILL.md                            │
│                                                                   │
│  1. Read current state.json                                       │
│  2. Generate workflow ID (WF-timestamp)                           │
│  3. Update state.json with new workflow                           │
│  4. Log "workflow_started" event                                  │
│  5. Spawn Research PIC                                            │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                       Research PIC                                │
│                                                                   │
│  1. Read problem statement                                        │
│  2. Search codebase (Glob, Grep)                                  │
│  3. Analyze findings                                              │
│  4. Produce research summary                                      │
│  5. Signal completion                                             │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                     [Phase Transition]
                                │
                                ▼
                       [Next Phase...]
```

### Phase Transition Flow

```
┌─────────────────┐
│  Current PIC    │
│  Signals Done   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Hook:          │────▶│ status-log.jsonl │
│  on-pic-handoff │     │ (append event)   │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Update         │────▶│  state.json     │
│  State          │     │ (phase status)  │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Create         │────▶│  handoffs/      │
│  Handoff Doc    │     │  (record)       │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Spawn Next PIC │
└─────────────────┘
```

### Decision Recording Flow

```
┌─────────────────┐
│  /pic-decide    │
│  "Title"        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gather Info    │
│  from User      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Create Doc     │────▶│ decisions/      │
│  DEC-XXX.md     │     │ DEC-001.md      │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Update State   │────▶│ state.json      │
│  (add ref)      │     │ decisions: []   │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Hook:          │────▶│ status-log.jsonl│
│  on-decision    │     │ (append)        │
└─────────────────┘     └─────────────────┘
```

---

## State Management

### State File Structure

```json
{
  "initialized": boolean,     // System ready?
  "workflow": string | null,  // Workflow ID
  "currentPhase": string,     // Active phase name
  "currentPIC": string,       // Active agent name
  "problem": string,          // User's problem statement
  "startedAt": ISO-8601,      // Start timestamp
  "completedAt": ISO-8601,    // End timestamp (null if running)

  "phases": {
    "[phase-name]": {
      "status": "pending" | "in_progress" | "completed" | "blocked",
      "startedAt": ISO-8601 | null,
      "completedAt": ISO-8601 | null
    }
  },

  "decisions": [              // References to DEC-XXX docs
    {
      "id": "DEC-001",
      "title": "Choose database",
      "phase": "design",
      "timestamp": ISO-8601
    }
  ],

  "conflicts": [...],         // References to CON-XXX docs
  "handoffs": [...]           // Handoff summaries
}
```

### State Transitions

```
                    ┌─────────┐
                    │ pending │
                    └────┬────┘
                         │ start phase
                         ▼
               ┌─────────────────┐
               │  in_progress    │
               └────────┬────────┘
                        │
           ┌────────────┼────────────┐
           │            │            │
           ▼            ▼            ▼
    ┌───────────┐ ┌───────────┐ ┌─────────┐
    │ completed │ │  blocked  │ │ (error) │
    └───────────┘ └─────┬─────┘ └────┬────┘
                        │            │
                        ▼            ▼
                   unblocked     recovery
```

### Log Format (JSONL)

Each line is an independent JSON object:

```json
{"timestamp": "ISO-8601", "event": "event_name", ...additional fields}
```

**Common Events:**
| Event | Fields | Meaning |
|-------|--------|---------|
| workflow_started | workflow, problem | New workflow begun |
| phase_completed | phase, agent | Phase finished |
| phase_handoff | from, to, notes | Transition occurred |
| decision_recorded | decision, title | Decision documented |
| conflict_escalated | conflict, summary | Conflict raised |
| workflow_completed | workflow, result | Workflow finished |

---

## Agent Architecture

### Agent Composition

Each agent is composed of:

```
┌─────────────────────────────────────────────────┐
│                    AGENT                         │
├─────────────────────────────────────────────────┤
│  Task Agent Type        │  e.g., "Explore"      │
│  (from Claude Code)     │                       │
├─────────────────────────┼───────────────────────┤
│  Instructions           │  .claude/agents/*.md  │
│  (from file)            │                       │
├─────────────────────────┼───────────────────────┤
│  Context                │  Problem statement,   │
│  (from workflow)        │  previous findings    │
├─────────────────────────┼───────────────────────┤
│  Permissions            │  read-only, full,     │
│  (from config)          │  acceptEdits          │
└─────────────────────────┴───────────────────────┘
```

### Agent Type Mapping

```
PIC Role          →  Claude Code Agent  →  Capabilities
────────────────────────────────────────────────────────
Research          →  Explore            →  Search, read
Planning          →  planner            →  Plan, write
Design            →  planner            →  Design, write
Implementation    →  builder            →  Code, execute
Testing           →  test-writer        →  Test, execute
Review            →  reviewer           →  Review, read
Orchestrator      →  orchestrator       →  Coordinate
```

### Agent Communication

Agents do NOT communicate directly. All communication is through:

1. **State Files** - Shared state in `.pic/`
2. **Handoff Documents** - Explicit transition records
3. **Orchestrator** - Coordination through central agent

```
Agent A ──▶ State File ──▶ Agent B
            ▲
            │
       Orchestrator
```

---

## Coordination Model

### Hybrid Coordination

The system uses a hybrid of:

1. **Centralized Control** (Orchestrator)
   - Manages phase transitions
   - Resolves conflicts
   - Maintains workflow state

2. **Decentralized Ownership** (PICs)
   - Each phase has autonomous authority
   - PICs make domain decisions independently
   - No cross-phase interference

### Handoff Protocol

```
1. Current PIC signals completion
   └── "I'm done, here's what I found"

2. Orchestrator validates
   └── "Did you meet exit criteria?"

3. State updated
   └── Current phase → completed
   └── Next phase → in_progress

4. Handoff documented
   └── Create record in handoffs/

5. Next PIC spawned
   └── With context from previous phase
```

### Conflict Resolution Protocol

```
1. Conflict detected
   └── PICs have contradictory recommendations

2. Orchestrator gathers positions
   └── What does each PIC recommend?
   └── What evidence supports each?

3. Analysis
   └── Find common ground
   └── Identify core disagreement

4. Resolution attempt
   ├── Evidence clear? → Decide and document
   ├── Synthesis possible? → Combine approaches
   └── Ambiguous? → Escalate to user

5. Resolution documented
   └── Create record in conflicts/
   └── Update state
```

---

## Extension Points

### Adding New Phases

1. Create agent file: `.claude/agents/pic-[name].md`
2. Update config: `.pic/config.json` (add to order and definitions)
3. Update init script: `scripts/pic-init.sh` (add to state template)
4. Update docs: `CLAUDE.md`, `USER_GUIDE.md`

### Adding New Skills

1. Create directory: `.claude/skills/[name]/`
2. Create skill file: `SKILL.md` with front matter
3. Restart Claude Code (skills load on startup)

### Adding New Hooks

1. Create script: `.claude/hooks/[name].sh`
2. Make executable: `chmod +x`
3. Register in `.claude/settings.json`

### Adding New Rules

1. Create rule file: `.claude/rules/[name].md`
2. Reference in agent instructions as needed

---

## Design Decisions

### Why JSON for State?

| Alternative | Rejected Because |
|-------------|------------------|
| Database | Overkill, adds dependency |
| YAML | Less tooling support |
| XML | Verbose, harder to parse |
| **JSON** | **Simple, universal, human-readable** |

### Why JSONL for Logs?

| Alternative | Rejected Because |
|-------------|------------------|
| Single JSON array | Must rewrite entire file on append |
| Plain text | Hard to parse programmatically |
| Database | Overkill |
| **JSONL** | **Append-only, easy to parse, grep-friendly** |

### Why Markdown for Docs?

| Alternative | Rejected Because |
|-------------|------------------|
| Plain text | No formatting |
| HTML | Verbose |
| PDF | Not editable |
| **Markdown** | **Readable, formattable, version-control friendly** |

### Why Separate Agent Files?

| Alternative | Rejected Because |
|-------------|------------------|
| Inline in config | Hard to edit, no syntax highlighting |
| Single large file | Hard to navigate |
| **Separate files** | **Modular, easy to modify individually** |

### Why Explicit Handoffs?

| Alternative | Rejected Because |
|-------------|------------------|
| Automatic transitions | Hard to debug, less control |
| No transitions | Chaos, no clear ownership |
| **Explicit handoffs** | **Clear accountability, audit trail** |

---

## Summary

The PIC system is built on:

1. **Layered Architecture** - UI → Orchestration → Agents → Persistence
2. **State-Based Coordination** - All communication through shared state
3. **Modular Components** - Each part can be modified independently
4. **Explicit Contracts** - Clear interfaces between components
5. **Full Auditability** - Everything is logged and documented

This architecture enables:
- Easy extension (add phases, skills, hooks)
- Clear debugging (follow state changes)
- Reliable execution (explicit transitions)
- Complete traceability (audit logs)
