# Glossary

This glossary defines all terms and concepts used in the PIC Agentic Organizational System. Terms are organized alphabetically.

---

## A

### Agent
A specialized AI worker that performs tasks. In this system, each PIC role is performed by an agent. Agents receive instructions and context, do their work, and produce output.

**Example:** The Research PIC agent searches the codebase and web to gather information.

### Agent Type
The specific Claude Code built-in agent used to perform work. Different agent types have different capabilities.

**Agent types used:**
- `Explore` - For searching and reading
- `planner` - For planning and design
- `builder` - For writing code
- `test-writer` - For writing tests
- `reviewer` - For reviewing work
- `orchestrator` - For coordination

### Architecture
The overall structure and design of a system, including how components connect and communicate.

---

## B

### Bash
A command-line shell and scripting language used on Unix/Linux/macOS systems. Windows users can use Git Bash.

**Example:**
```bash
#!/bin/bash
echo "Hello, World!"
```

---

## C

### Claude Code
An AI-powered coding assistant from Anthropic. This system runs inside Claude Code and uses its agent capabilities.

### Conflict
A disagreement between two or more PICs about how to proceed. Conflicts are resolved through a structured process.

**Types of conflicts:**
- Technical disagreements
- Scope disputes
- Priority conflicts
- Process disputes

### Config (Configuration)
Settings that control how the system behaves. Stored in `.pic/config.json`.

---

## D

### Decision
A formal choice made during a workflow. Decisions are documented to explain why certain approaches were chosen.

**Decision tiers:**
1. **Formal** (DEC-XXX.md) - Major decisions with full documentation
2. **Lightweight** (log entry) - Minor decisions with brief rationale
3. **Implicit** - Following established patterns, no documentation needed

### Delegation
When one agent assigns work to sub-agents. Only Implementation and Testing PICs can delegate.

---

## E

### Escalation
Raising an issue to a higher level for resolution. Conflicts that can't be resolved by the orchestrator are escalated to the user.

### Evidence
Data, facts, or observations that support a decision or recommendation.

**Types of evidence:**
- Code analysis results
- Documentation
- Test results
- Web research
- Expert opinion

### Exit Criteria
Conditions that must be met before a phase can be considered complete.

**Example:** Research phase exit criteria:
- Problem is clearly understood
- Evidence sources documented
- Knowledge gaps identified

---

## F

### Front Matter
Metadata at the start of a Markdown file, enclosed in `---`.

**Example:**
```markdown
---
name: pic-start
description: Initialize a workflow
---
```

---

## G

### Git
A version control system for tracking changes to files. Not required for this system but commonly used alongside it.

### Glob
A pattern-matching tool for finding files by name.

**Example:** `*.sh` matches all files ending in `.sh`

### Grep
A tool for searching file contents for patterns.

---

## H

### Handoff
The formal transition from one PIC to the next. Handoffs include a summary of completed work and context for the next phase.

**Handoff record includes:**
- What was done
- Key findings
- Open questions
- Notes for next phase

### Hook
A script that runs automatically when certain events occur.

**Available hooks:**
- `PreToolUse` - Before a tool runs
- `PostToolUse` - After a tool runs
- `SubagentStop` - When an agent finishes

---

## I

### Implementation
The phase where code is written based on the design specification.

### Integration Test
A test that verifies multiple components work correctly together.

**Example:** Testing that the login form correctly communicates with the authentication server.

### ISO 8601
A standard format for dates and times.

**Example:** `2026-02-04T22:17:58Z`

---

## J

### JSON (JavaScript Object Notation)
A text format for storing structured data.

**Example:**
```json
{
  "name": "value",
  "count": 42,
  "active": true
}
```

### JSONL (JSON Lines)
A format with one JSON object per line. Used for logs.

**Example:**
```
{"event": "start", "time": "10:00"}
{"event": "end", "time": "10:30"}
```

---

## L

### Log
A record of events that occurred. The system logs to `.pic/status-log.jsonl`.

---

## M

### Markdown
A simple text formatting language used for documentation.

**Example:**
```markdown
# Heading
**Bold text**
- Bullet point
```

### Milestone
A significant checkpoint in a project plan.

---

## N

### NVIDIA Nemotron
A project management model from NVIDIA that inspired this system. Key principles include decentralized ownership and data-driven decisions.

---

## O

### Orchestrator
The central coordinator that manages workflow flow, phase transitions, and conflict resolution.

**Responsibilities:**
- Start workflows
- Validate handoffs
- Resolve conflicts
- Track state

---

## P

### Permission
Rules about what actions an agent can take.

**Permission levels:**
- `read-only` - Can only read, not modify
- `acceptEdits` - Can write with approval
- `full` - Full access to all tools

### Phase
One of six stages in a workflow. Phases run in sequence.

**Phases:**
1. Research
2. Planning
3. Design
4. Implementation
5. Testing
6. Review

### PIC (Pilot in Command)
An agent that owns a specific phase of the workflow. The term comes from aviation - there's always one pilot in command.

### Problem Statement
The user's description of what they want to accomplish. A good problem statement is specific and clear.

**Good:** "Create a bash script that backs up a folder to a ZIP file"
**Poor:** "Make a backup thing"

---

## R

### Research
The first phase where information is gathered about the problem.

### Review
The final phase where work is checked for quality before completion.

### Rule
A documented policy that governs how the system operates.

**Rule files:**
- `pic-coordination.md` - Phase boundaries
- `decision-protocols.md` - How to decide
- `conflict-resolution.md` - How to resolve conflicts

---

## S

### Shebang
The first line of a script that specifies what interpreter to use.

**Example:** `#!/bin/bash`

### Skill
A user command that can be invoked with a slash.

**Available skills:**
- `/pic-start` - Start workflow
- `/pic-status` - Show status
- `/pic-decide` - Record decision
- `/pic-handoff` - Transition phase
- `/pic-conflict` - Escalate conflict
- `/pic-integration` - Run integration test

### State
The current condition of the workflow. Stored in `.pic/state.json`.

**State includes:**
- Current phase
- Phase statuses
- Decisions made
- Conflicts

---

## T

### Task
A specific piece of work to be done. In Claude Code, the Task tool spawns agents to do work.

### Testing
The phase where code is verified to work correctly.

### Timestamp
A record of when something happened. Uses ISO 8601 format.

### Transition
Moving from one phase to another. See: Handoff.

---

## U

### Unit Test
A test that verifies a single component works correctly in isolation.

---

## V

### Validation
Checking that something meets requirements or criteria.

### Verbosity
How much detail is included in logs.

**Levels:**
- `quiet` - Minimal logging
- `normal` - Standard logging
- `verbose` - Detailed logging

---

## W

### Workflow
A complete execution of all phases from start to finish.

**Workflow lifecycle:**
1. Start (`/pic-start`)
2. Phases execute in sequence
3. Complete or abort

### Workflow ID
A unique identifier for a workflow.

**Format:** `WF-YYYYMMDD-HHMMSS`

**Example:** `WF-20260204-221758`

---

## Common Abbreviations

| Abbreviation | Meaning |
|--------------|---------|
| API | Application Programming Interface |
| CLI | Command Line Interface |
| DEC | Decision (document prefix) |
| CON | Conflict (document prefix) |
| INT | Integration test (document prefix) |
| JSON | JavaScript Object Notation |
| JSONL | JSON Lines |
| PIC | Pilot in Command |
| WF | Workflow |

---

## File Extensions

| Extension | Meaning |
|-----------|---------|
| `.json` | JSON data file |
| `.jsonl` | JSON Lines log file |
| `.md` | Markdown document |
| `.sh` | Bash shell script |

---

## Directory Names

| Directory | Purpose |
|-----------|---------|
| `.pic/` | Runtime state |
| `.claude/` | Claude Code configuration |
| `docs/` | Documentation |
| `scripts/` | Utility scripts |
| `agents/` | Agent instruction files |
| `skills/` | User command definitions |
| `hooks/` | Event handler scripts |
| `rules/` | Policy documents |
