# User Guide

This comprehensive guide covers everything you need to know to use the PIC Agentic Organizational System effectively.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Understanding the System](#understanding-the-system)
3. [Getting Started](#getting-started)
4. [The Six Phases Explained](#the-six-phases-explained)
5. [Using Commands](#using-commands)
6. [Working with Decisions](#working-with-decisions)
7. [Handling Conflicts](#handling-conflicts)
8. [Reading Status and Logs](#reading-status-and-logs)
9. [Configuration Options](#configuration-options)
10. [Best Practices](#best-practices)
11. [Advanced Usage](#advanced-usage)

---

## Introduction

### What Is This System For?

The PIC system helps you solve complex problems by breaking them into manageable phases. Instead of trying to do everything at once, specialized AI agents handle each phase:

- **Research Agent** gathers information
- **Planning Agent** creates a strategy
- **Design Agent** defines the technical approach
- **Implementation Agent** writes the code
- **Testing Agent** verifies it works
- **Review Agent** checks quality

### Why Use This Approach?

1. **Better Quality** - Each phase has a dedicated expert
2. **Clear Progress** - You always know what's happening
3. **Documented Decisions** - Everything is recorded
4. **Fewer Mistakes** - Systematic process catches errors early

### Who Is This For?

- Developers who want structured, high-quality output
- Teams who need documented decision trails
- Anyone learning software development best practices

---

## Understanding the System

### The Airplane Analogy

Imagine an airplane flight:

1. **Before Flight** (Research) - Check weather, plan route, verify fuel
2. **Taxi** (Planning) - Get clearances, set procedures
3. **Takeoff** (Design) - Configure systems, set course
4. **Cruise** (Implementation) - Execute the flight plan
5. **Approach** (Testing) - Verify systems, prepare for landing
6. **Landing** (Review) - Final checks, safe completion

At each phase, there's ONE pilot in command. They have full authority over their domain. When their phase is complete, they hand off to the next pilot.

### The Workflow Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   START ──► Research ──► Planning ──► Design ──►       │
│                                                         │
│              Implementation ──► Testing ──► Review ──► END
│                                                         │
└─────────────────────────────────────────────────────────┘
```

Each arrow represents a **handoff** - a formal transition from one agent to the next.

---

## Getting Started

### Step 1: Install Prerequisites

You need:
- **Claude Code** - Install from Anthropic
- **Bash shell** - Git Bash on Windows, or built-in on macOS/Linux

### Step 2: Open the Project Folder

```bash
cd /path/to/nemotron_PIC_lambert
```

### Step 3: Initialize (First Time Only)

```bash
bash scripts/pic-init.sh
```

This creates the `.pic/` directory with:
- `config.json` - System configuration
- `state.json` - Current workflow state
- `status-log.jsonl` - Activity log
- Empty folders for decisions, handoffs, conflicts

### Step 4: Launch Claude Code

```bash
claude
```

### Step 5: Start Your First Workflow

```
/pic-start Describe your problem here
```

---

## The Six Phases Explained

### Phase 1: Research

**Purpose:** Understand the problem and gather relevant information.

**What the Research Agent Does:**
1. Analyzes your problem statement
2. Searches existing code for patterns
3. Looks up relevant documentation
4. Identifies constraints and requirements

**What You'll See:**
```
Research Summary:
- Problem understood as: [interpretation]
- Key findings: [list of discoveries]
- Recommendations: [suggested approaches]
- Risks identified: [potential issues]
```

**Example Output:**
```markdown
## Research Summary

### Problem Understanding
User wants a script to convert temperatures.

### Key Findings
1. Existing project uses bash scripts
2. Similar scripts follow `scripts/[name].sh` pattern
3. Project uses `set -e` for error handling

### Recommendations
- Create `scripts/temp-convert.sh`
- Accept temperature and unit as arguments
- Support both C→F and F→C conversions
```

### Phase 2: Planning

**Purpose:** Create a strategic roadmap for solving the problem.

**What the Planning Agent Does:**
1. Reviews research findings
2. Breaks work into milestones
3. Defines success criteria
4. Identifies risks and mitigations

**What You'll See:**
```
Strategic Plan:
- Approach: [high-level strategy]
- Milestones: [list of checkpoints]
- Tasks: [specific work items]
- Risks: [what could go wrong]
```

### Phase 3: Design

**Purpose:** Define the technical architecture and interfaces.

**What the Design Agent Does:**
1. Reviews the plan
2. Designs system structure
3. Specifies interfaces (inputs/outputs)
4. Makes technical decisions

**What You'll See:**
```
Technical Design:
- Architecture: [system structure]
- Interfaces: [how components connect]
- Decisions: [technical choices made]
```

### Phase 4: Implementation

**Purpose:** Write the actual code.

**What the Implementation Agent Does:**
1. Follows the design specification
2. Writes clean, working code
3. Creates unit tests
4. Documents the code

**What You'll See:**
- New files created in your project
- Code that matches the design
- Basic tests

### Phase 5: Testing

**Purpose:** Verify everything works correctly.

**What the Testing Agent Does:**
1. Runs unit tests
2. Tests integration between components
3. Checks edge cases
4. Reports any bugs found

**What You'll See:**
```
Test Report:
- Tests run: [count]
- Tests passed: [count]
- Issues found: [list]
- Coverage: [percentage]
```

### Phase 6: Review

**Purpose:** Final quality check and approval.

**What the Review Agent Does:**
1. Verifies all phases completed properly
2. Checks code quality
3. Confirms requirements are met
4. Approves or requests revisions

**What You'll See:**
```
Review Report:
- Status: APPROVED / REVISIONS REQUIRED
- Checklist: [verification items]
- Issues: [if any]
```

---

## Using Commands

### Command: /pic-start

**Purpose:** Begin a new workflow.

**Syntax:**
```
/pic-start [problem description]
```

**Examples:**
```
/pic-start Create a file backup script
/pic-start Build a simple calculator
/pic-start Write a function to validate email addresses
```

**Tips:**
- Be specific about what you want
- Include key requirements
- Mention constraints if any

**Good Problem Statements:**
```
✓ Create a bash script that backs up a folder to a ZIP file
✓ Build a temperature converter that handles Celsius and Fahrenheit
✓ Write a Python function to validate email addresses using regex
```

**Poor Problem Statements:**
```
✗ Make something
✗ Fix the code
✗ Do the thing
```

### Command: /pic-status

**Purpose:** Show current workflow progress.

**Syntax:**
```
/pic-status
```

**Output Explained:**
```
## PIC Workflow Status

Workflow ID: WF-20260204-221758    ← Unique identifier
Problem: Create a calculator       ← Your original request

### Phase Progress

| Phase          | Status       | Started    | Completed  |
|----------------|--------------|------------|------------|
| Research       | [x] Completed | 10:30:00  | 10:30:45   |
| Planning       | [>] In Progress | 10:30:45 | -         |
| Design         | [ ] Pending  | -          | -          |
...

### Current Phase
Planning - Creating strategic roadmap

### Recent Activity
- 10:30:45 - Phase handoff: Research → Planning
- 10:30:30 - Research findings documented
```

### Command: /pic-decide

**Purpose:** Record a formal decision.

**Syntax:**
```
/pic-decide [decision title]
```

**When to Use:**
- Choosing between alternatives
- Making technical trade-offs
- Recording important choices

**What You'll Be Asked:**
1. What decision was made?
2. What alternatives were considered?
3. Why was this choice made?
4. What are the consequences?

**Example:**
```
/pic-decide Choose database type
```

Creates a document like:
```markdown
# DEC-001: Choose database type

## Decision
Use SQLite for the database.

## Alternatives Considered
1. PostgreSQL - More powerful but requires setup
2. SQLite - Simple, file-based, no server needed
3. MySQL - Good but overkill for this use case

## Rationale
SQLite is sufficient for our needs and requires
no additional infrastructure.
```

### Command: /pic-handoff

**Purpose:** Manually trigger transition to next phase.

**Syntax:**
```
/pic-handoff [optional notes]
```

**When to Use:**
- Usually happens automatically
- Use manually if workflow is stuck
- Add notes for next phase

**Example:**
```
/pic-handoff Ready for implementation, prioritize error handling
```

### Command: /pic-conflict

**Purpose:** Escalate a disagreement for human decision.

**Syntax:**
```
/pic-conflict [summary of conflict]
```

**When This Happens:**
- Two agents recommend different approaches
- Evidence doesn't clearly favor one option
- Trade-offs require human judgment

**Example Output:**
```
## Conflict Escalation

Position A: Use REST API
- Evidence: Industry standard, team familiarity

Position B: Use GraphQL
- Evidence: More efficient for complex queries

Please choose:
1. Accept Position A
2. Accept Position B
3. Provide alternative
```

### Command: /pic-integration

**Purpose:** Test components working together.

**Syntax:**
```
/pic-integration [component list]
```

**Example:**
```
/pic-integration scripts/validator.sh scripts/formatter.sh
```

**What It Does:**
1. Tests each component individually
2. Tests them together
3. Reports compatibility issues
4. Saves results to `.pic/integration-results/`

---

## Working with Decisions

### Decision Tiers

The system has three levels of decision documentation:

**Tier 1: Formal Decisions**
- Major choices affecting the project
- Stored in `.pic/decisions/DEC-XXX.md`
- Include full rationale and alternatives

**Tier 2: Lightweight Decisions**
- Minor choices during workflow
- Logged in `.pic/status-log.jsonl`
- Brief rationale only

**Tier 3: Implicit Decisions**
- Following established patterns
- No documentation needed
- Can be questioned later

### Viewing Past Decisions

```bash
# List all decisions
ls .pic/decisions/

# Read a specific decision
cat .pic/decisions/DEC-001.md
```

### Reversing Decisions

If a decision turns out to be wrong:

1. Create a new decision document
2. Reference the original decision
3. Explain why it's being reversed
4. Document the new choice

---

## Handling Conflicts

### What Is a Conflict?

A conflict occurs when:
- Different agents recommend contradictory approaches
- Evidence supports multiple options equally
- Trade-offs require value judgments

### The Resolution Process

1. **Orchestrator Gathers Positions**
   - Each agent states their recommendation
   - Evidence is collected for each option

2. **Analysis**
   - Common ground is identified
   - Key differences are clarified

3. **Resolution Attempt**
   - If one option clearly wins → proceed
   - If synthesis possible → combine approaches
   - If unclear → escalate to user

4. **Your Decision**
   - Review the options presented
   - Choose based on your priorities
   - Decision is documented and workflow continues

### Example Conflict

```
## Conflict: Database Choice

### Position A: SQLite
Advocate: Design PIC
Evidence: Simple, no setup, sufficient for current needs

### Position B: PostgreSQL
Advocate: Planning PIC
Evidence: Scalable, production-ready, team experience

### What's at Stake
This affects future scalability and development complexity.

Your choice: [1] SQLite  [2] PostgreSQL  [3] Other
```

---

## Reading Status and Logs

### The State File (.pic/state.json)

Contains current workflow state:

```json
{
  "initialized": true,
  "workflow": "WF-20260204-221758",
  "currentPhase": "implementation",
  "problem": "Create a calculator",
  "phases": {
    "research": {"status": "completed"},
    "planning": {"status": "completed"},
    "design": {"status": "completed"},
    "implementation": {"status": "in_progress"},
    "testing": {"status": "pending"},
    "review": {"status": "pending"}
  }
}
```

### The Activity Log (.pic/status-log.jsonl)

Append-only log of all events:

```json
{"timestamp": "2026-02-04T10:30:00Z", "event": "workflow_started", "workflow": "WF-123"}
{"timestamp": "2026-02-04T10:30:45Z", "event": "phase_completed", "phase": "research"}
{"timestamp": "2026-02-04T10:31:00Z", "event": "decision_recorded", "decision": "DEC-001"}
```

**Reading the log:**
```bash
# View all entries
cat .pic/status-log.jsonl

# View last 5 entries
tail -5 .pic/status-log.jsonl

# Search for specific events
grep "phase_completed" .pic/status-log.jsonl
```

---

## Configuration Options

### The Config File (.pic/config.json)

Key settings you can modify:

```json
{
  "workflow": {
    "autoHandoff": false,        // Auto-transition between phases?
    "requireHandoffApproval": true  // Ask before each transition?
  },
  "logging": {
    "verbosity": "normal"        // "quiet", "normal", or "verbose"
  }
}
```

### Changing Phase Order

Default order:
```json
"order": ["research", "planning", "design", "implementation", "testing", "review"]
```

You can modify this, but it's not recommended for beginners.

---

## Best Practices

### 1. Write Clear Problem Statements

**Do:**
```
Create a bash script that accepts a directory path
and outputs the total size of all files in that directory
```

**Don't:**
```
Make a size thing
```

### 2. Check Status Regularly

Use `/pic-status` to monitor progress. Don't just start a workflow and walk away.

### 3. Document Important Decisions

Use `/pic-decide` for choices that matter. Your future self will thank you.

### 4. Read the Logs When Things Go Wrong

The `.pic/status-log.jsonl` file tells you exactly what happened.

### 5. Let Phases Complete Naturally

Don't force handoffs unless necessary. Each phase has important work to do.

### 6. Be Specific About Requirements

The more detail you provide, the better the results.

---

## Advanced Usage

### Running Multiple Workflows

You can only have one active workflow at a time. To start a new one:

1. Complete or abandon the current workflow
2. Run `bash scripts/pic-init.sh` to reset
3. Start a new workflow with `/pic-start`

### Customizing Agents

Advanced users can modify agent behavior by editing files in `.claude/agents/`. See the [Developer Guide](DEVELOPER_GUIDE.md).

### Integrating with Other Tools

The PIC system outputs standard files:
- JSON for configuration and state
- Markdown for documentation
- Bash scripts for utilities

These can be used with any tools that understand these formats.

---

## Summary

1. **Initialize** the system with `bash scripts/pic-init.sh`
2. **Start** a workflow with `/pic-start [problem]`
3. **Monitor** progress with `/pic-status`
4. **Document** decisions with `/pic-decide [title]`
5. **Resolve** conflicts when asked
6. **Review** results when workflow completes

The system guides you through a proven process for high-quality software development. Trust the process, be specific about what you want, and document important decisions along the way.
