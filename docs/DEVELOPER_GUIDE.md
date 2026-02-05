# Developer Guide

This guide is for developers who want to understand, modify, or extend the PIC Agentic Organizational System. It assumes you have basic programming experience (C, C++, Java) but may be new to web technologies, JSON, bash scripting, or AI agents.

---

## Table of Contents

1. [Before You Start](#before-you-start)
2. [Technology Overview](#technology-overview)
3. [Project Structure](#project-structure)
4. [Understanding the Code](#understanding-the-code)
5. [How the System Works](#how-the-system-works)
6. [Making Changes](#making-changes)
7. [Adding a New PIC Agent](#adding-a-new-pic-agent)
8. [Creating New Skills](#creating-new-skills)
9. [Modifying Hooks](#modifying-hooks)
10. [Testing Your Changes](#testing-your-changes)
11. [Common Development Tasks](#common-development-tasks)
12. [Code Style Guidelines](#code-style-guidelines)
13. [Debugging](#debugging)

---

## Before You Start

### Required Knowledge

You should be comfortable with:
- Basic command line usage
- Reading and understanding code
- Text editors

### What You'll Learn

This guide will teach you:
- JSON file format
- Bash scripting basics
- Markdown syntax
- How Claude Code agents work

### Setting Up Your Development Environment

1. **Install a code editor**
   - Recommended: VS Code, Sublime Text, or Notepad++
   - Any text editor works

2. **Install Git Bash (Windows only)**
   - Download from https://git-scm.com/download/win
   - This provides a Unix-like terminal on Windows

3. **Verify Claude Code is installed**
   ```bash
   claude --version
   ```

---

## Technology Overview

### JSON (JavaScript Object Notation)

JSON is a text format for storing structured data. It's used throughout this project for configuration and state.

**Basic JSON Syntax:**
```json
{
  "name": "John",
  "age": 30,
  "active": true,
  "skills": ["coding", "design"],
  "address": {
    "city": "New York",
    "zip": "10001"
  }
}
```

**Key Rules:**
- Use double quotes `"` for strings (not single quotes)
- No trailing commas after the last item
- Boolean values are `true` or `false` (lowercase)
- Null values are `null`

**Common Mistakes:**
```json
// WRONG - single quotes
{'name': 'John'}

// WRONG - trailing comma
{"name": "John",}

// CORRECT
{"name": "John"}
```

### Bash Scripting

Bash is a command-line language for Unix systems. The scripts in this project use bash.

**Basic Bash Script:**
```bash
#!/bin/bash
# This is a comment
# The first line (shebang) tells the system to use bash

# Variables
NAME="World"
echo "Hello, $NAME!"

# Conditionals
if [ -f "file.txt" ]; then
    echo "File exists"
else
    echo "File not found"
fi

# Exit with success
exit 0
```

**Key Concepts:**
- `#!/bin/bash` - First line, tells system to use bash
- `#` - Comments (ignored by bash)
- `$VARIABLE` - Access variable value
- `set -e` - Exit immediately if any command fails
- `exit 0` - Exit successfully (0 = success)

### Markdown

Markdown is a text format for documentation. All `.md` files use Markdown.

**Basic Markdown:**
```markdown
# Heading 1
## Heading 2
### Heading 3

**Bold text**
*Italic text*

- Bullet point
- Another point

1. Numbered list
2. Second item

`inline code`

​```bash
code block
​```

[Link text](http://example.com)

| Column 1 | Column 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### JSONL (JSON Lines)

JSONL is JSON with one object per line. Used for logs.

**Example (.pic/status-log.jsonl):**
```
{"timestamp": "2026-02-04T10:00:00Z", "event": "start"}
{"timestamp": "2026-02-04T10:01:00Z", "event": "complete"}
```

Each line is a valid JSON object. Lines are independent.

---

## Project Structure

```
project-root/
├── CLAUDE.md                 # Main documentation (always read first)
├── docs/                     # All documentation files
│   ├── QUICK_START.md
│   ├── USER_GUIDE.md
│   ├── DEVELOPER_GUIDE.md    # ← You are reading this
│   ├── ARCHITECTURE.md
│   ├── TROUBLESHOOTING.md
│   ├── GLOSSARY.md
│   └── REFERENCE.md
│
├── scripts/                  # Utility scripts
│   ├── pic-init.sh          # System initialization
│   └── hello-world.sh       # Example output
│
├── .pic/                     # Runtime state (created by init)
│   ├── config.json          # System configuration
│   ├── state.json           # Current workflow state
│   ├── status-log.jsonl     # Activity log
│   ├── decisions/           # Decision documents (DEC-XXX.md)
│   ├── handoffs/            # Phase transition records
│   ├── conflicts/           # Conflict records (CON-XXX.md)
│   └── integration-results/ # Test results (INT-XXX.md)
│
└── .claude/                  # Claude Code configuration
    ├── settings.json        # Permissions and hooks
    ├── agents/              # Agent instruction files
    │   ├── orchestrator.md
    │   ├── pic-research.md
    │   ├── pic-planning.md
    │   ├── pic-design.md
    │   ├── pic-implementation.md
    │   ├── pic-testing.md
    │   └── pic-review.md
    ├── skills/              # User-invocable commands
    │   ├── pic-start/SKILL.md
    │   ├── pic-status/SKILL.md
    │   ├── pic-decide/SKILL.md
    │   ├── pic-handoff/SKILL.md
    │   ├── pic-conflict/SKILL.md
    │   └── pic-integration/SKILL.md
    ├── rules/               # Coordination rules
    │   ├── pic-coordination.md
    │   ├── decision-protocols.md
    │   └── conflict-resolution.md
    └── hooks/               # Event handlers
        ├── validate-pic-action.sh
        ├── on-decision-made.sh
        ├── on-pic-handoff.sh
        └── notify-status.sh
```

### What Each Directory Contains

| Directory | Purpose | When Modified |
|-----------|---------|---------------|
| `docs/` | Documentation | When updating docs |
| `scripts/` | Utility scripts | When adding tools |
| `.pic/` | Runtime data | Automatically during workflows |
| `.claude/agents/` | Agent instructions | When changing agent behavior |
| `.claude/skills/` | User commands | When adding commands |
| `.claude/rules/` | Coordination rules | When changing policies |
| `.claude/hooks/` | Event handlers | When adding automation |

---

## Understanding the Code

### The Configuration File (.pic/config.json)

This file controls system behavior:

```json
{
  "version": "1.0.0",              // Config format version

  "pics": {
    "order": [                     // Phase execution order
      "research",
      "planning",
      "design",
      "implementation",
      "testing",
      "review"
    ],
    "definitions": {
      "research": {
        "name": "Research PIC",           // Display name
        "taskAgentType": "Explore",       // Claude Code agent to use
        "instructionsFile": ".claude/agents/pic-research.md",
        "description": "Information gathering",
        "permissions": "read-only",       // What agent can do
        "canDelegate": false              // Can spawn sub-agents?
      }
      // ... other phases
    }
  },

  "orchestrator": {
    "agent": "orchestrator",
    "maxParallelAgents": 3,              // How many agents at once
    "conflictResolutionTimeout": 300      // Seconds before escalation
  },

  "workflow": {
    "autoHandoff": false,                 // Auto-transition phases?
    "requireHandoffApproval": true,       // Ask before transition?
    "minEvidenceForDecision": 2           // Evidence required
  },

  "logging": {
    "verbosity": "normal"                 // quiet/normal/verbose
  }
}
```

### The State File (.pic/state.json)

This file tracks current workflow state:

```json
{
  "initialized": true,                    // System ready?
  "workflow": "WF-20260204-221758",       // Current workflow ID
  "currentPhase": "implementation",        // Active phase
  "currentPIC": "pic-implementation",      // Active agent
  "problem": "Create a calculator",        // User's request
  "startedAt": "2026-02-04T22:17:58Z",    // When started
  "completedAt": null,                     // When finished (null if running)

  "phases": {
    "research": {
      "status": "completed",              // pending/in_progress/completed
      "startedAt": "2026-02-04T22:17:58Z",
      "completedAt": "2026-02-04T22:18:30Z"
    }
    // ... other phases
  },

  "decisions": [],                         // List of DEC-XXX references
  "conflicts": [],                         // List of CON-XXX references
  "handoffs": []                           // Handoff records
}
```

### Agent Instruction Files (.claude/agents/*.md)

Each agent has an instruction file that defines:
- Role and purpose
- Responsibilities
- Available tools
- Expected outputs
- Handoff criteria

**Example structure:**
```markdown
# Research PIC Agent

## Role
You are the Research PIC...

## Responsibilities
1. Problem analysis
2. Information gathering
...

## Tools Available
- Read, Glob, Grep (read-only)
- WebSearch, WebFetch

## Deliverables
1. Research summary
2. Evidence log
...

## Handoff Criteria
Ready when:
1. Problem is understood
2. Evidence collected
...
```

### Skill Files (.claude/skills/*/SKILL.md)

Skills are user commands. Each skill has a SKILL.md file:

```markdown
---
name: pic-start
description: Initialize a new PIC workflow
args: "[problem description]"
---

# PIC Workflow Initialization

[Instructions for the skill to follow]
```

The `---` section is called "front matter" and defines metadata.

---

## How the System Works

### Workflow Execution Flow

```
User types: /pic-start Create a calculator
                    ↓
1. Skill loads pic-start/SKILL.md
                    ↓
2. Skill updates .pic/state.json
                    ↓
3. Skill spawns Research PIC (using Explore agent)
                    ↓
4. Research PIC reads pic-research.md instructions
                    ↓
5. Research PIC does its work
                    ↓
6. Research PIC signals completion
                    ↓
7. Orchestrator validates and updates state
                    ↓
8. Next PIC spawns (Planning)
                    ↓
[Repeat for each phase]
                    ↓
9. Review PIC approves → Workflow complete
```

### Agent Spawning Mechanism

When a PIC needs to run:

1. **Config Lookup**: Read `.pic/config.json` to get `taskAgentType`
2. **Instructions Lookup**: Read the `instructionsFile`
3. **Task Spawn**: Use Claude Code's Task tool with:
   - `subagent_type`: The taskAgentType (e.g., "Explore")
   - `prompt`: Instructions from the file + context

**Code equivalent:**
```
Task(
  subagent_type = "Explore",
  prompt = [contents of pic-research.md] + [problem statement]
)
```

### State Transitions

The state machine for each phase:

```
pending → in_progress → completed
              ↓
          (on error)
              ↓
           blocked
```

### Hook Execution

Hooks run automatically on certain events:

| Event | Hook File | When It Runs |
|-------|-----------|--------------|
| Before Task | validate-pic-action.sh | Before spawning any agent |
| After Write/Edit | on-decision-made.sh | After file modifications |
| Agent Completes | on-pic-handoff.sh | When any PIC finishes |

---

## Making Changes

### General Process

1. **Understand** what you're changing
2. **Backup** important files
3. **Make** small, focused changes
4. **Test** after each change
5. **Document** what you changed

### Backup Before Changes

```bash
# Create a backup of .claude folder
cp -r .claude .claude.backup

# Create a backup of .pic folder
cp -r .pic .pic.backup
```

### Restore From Backup

```bash
# Restore if something goes wrong
rm -rf .claude
mv .claude.backup .claude
```

---

## Adding a New PIC Agent

### Step-by-Step Guide

Let's add a new "Security" PIC that runs after Implementation.

#### Step 1: Create the Agent Instruction File

Create `.claude/agents/pic-security.md`:

```markdown
# Security PIC Agent

You are the **Security PIC** - the Pilot in Command for security review.

## Role

You own the security review phase. Your job is to identify security vulnerabilities and ensure the code follows security best practices.

## Responsibilities

1. **Code Analysis** - Review code for security issues
2. **Vulnerability Detection** - Identify OWASP Top 10 vulnerabilities
3. **Best Practices** - Verify security best practices are followed
4. **Recommendations** - Suggest security improvements

## Tools Available

You have **read-only** access:
- `Read` - Read files in the codebase
- `Glob` - Find files by pattern
- `Grep` - Search file contents

## Deliverables

Your phase must produce:

1. **Security Report** - Summary of findings
2. **Vulnerability List** - Issues found with severity
3. **Recommendations** - How to fix issues

## Handoff Criteria

Ready when:
1. All code has been reviewed
2. Vulnerabilities are documented
3. Recommendations are provided
```

#### Step 2: Update Configuration

Edit `.pic/config.json`:

```json
{
  "pics": {
    "order": [
      "research",
      "planning",
      "design",
      "implementation",
      "security",        // ← Add here (after implementation)
      "testing",
      "review"
    ],
    "definitions": {
      // ... existing definitions ...

      "security": {                                    // ← Add this block
        "name": "Security PIC",
        "taskAgentType": "security-auditor",
        "instructionsFile": ".claude/agents/pic-security.md",
        "description": "Security vulnerability analysis",
        "permissions": "read-only",
        "canDelegate": false
      }
    }
  }
}
```

#### Step 3: Update the State Template

Edit `scripts/pic-init.sh` to include the new phase in the initial state:

Find the section that creates `state.json` and add:

```json
"phases": {
  "research": { "status": "pending", ... },
  "planning": { "status": "pending", ... },
  "design": { "status": "pending", ... },
  "implementation": { "status": "pending", ... },
  "security": { "status": "pending", "startedAt": null, "completedAt": null },  // ← Add
  "testing": { "status": "pending", ... },
  "review": { "status": "pending", ... }
}
```

#### Step 4: Test Your Changes

```bash
# Reinitialize
bash scripts/pic-init.sh

# Start a test workflow
claude
/pic-start Test security PIC integration
```

#### Step 5: Document Your Changes

Update `CLAUDE.md` to mention the new Security phase.

---

## Creating New Skills

### Step-by-Step Guide

Let's create a `/pic-reset` skill to reset the workflow.

#### Step 1: Create Skill Directory

```bash
mkdir -p .claude/skills/pic-reset
```

#### Step 2: Create SKILL.md

Create `.claude/skills/pic-reset/SKILL.md`:

```markdown
---
name: pic-reset
description: Reset the current workflow and start fresh
args: ""
---

# PIC Workflow Reset

You are resetting the PIC workflow. Follow this protocol exactly.

## Protocol

### Step 1: Check Current State

Read `.pic/state.json` to see if a workflow exists.

### Step 2: Confirm with User

Ask: "This will abandon the current workflow. Are you sure? (yes/no)"

If user says no, abort.

### Step 3: Archive Current State

If there's an active workflow:
1. Copy `.pic/state.json` to `.pic/archived/[workflow-id].json`
2. Log the abandonment

### Step 4: Reset State

Write a fresh state to `.pic/state.json`:

```json
{
  "initialized": false,
  "workflow": null,
  "currentPhase": null,
  ...
}
```

### Step 5: Confirm

Display: "Workflow reset complete. Use /pic-start to begin a new workflow."
```

#### Step 3: Test the Skill

After restarting Claude Code:
```
/pic-reset
```

---

## Modifying Hooks

### Understanding Hook Scripts

Hooks are bash scripts that run on events. They receive information via environment variables or arguments.

### Example: Adding Logging to a Hook

Edit `.claude/hooks/on-decision-made.sh`:

```bash
#!/bin/bash
# on-decision-made.sh

TOOL_INPUT="$1"
TOOL_OUTPUT="$2"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Extract file path
FILE_PATH=$(echo "$TOOL_INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' 2>/dev/null || echo "")

# Log all file writes (new addition)
echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"file_written\", \"path\": \"$FILE_PATH\"}" >> "$LOG_FILE"

# ... rest of the script
```

### Testing Hooks

After modifying a hook:

1. Make it executable:
   ```bash
   chmod +x .claude/hooks/on-decision-made.sh
   ```

2. Test manually:
   ```bash
   bash .claude/hooks/on-decision-made.sh '{"file_path": "/test/file.txt"}' ''
   ```

3. Check the log:
   ```bash
   tail -1 .pic/status-log.jsonl
   ```

---

## Testing Your Changes

### Manual Testing

1. **Reset the system**
   ```bash
   bash scripts/pic-init.sh
   ```

2. **Start a test workflow**
   ```bash
   claude
   /pic-start Test my changes with a simple hello world script
   ```

3. **Monitor progress**
   ```
   /pic-status
   ```

4. **Check logs**
   ```bash
   cat .pic/status-log.jsonl
   ```

### Verifying Config Changes

```bash
# Check JSON is valid
cat .pic/config.json | python -m json.tool

# If you don't have Python, just look for error messages
# when running /pic-start
```

### Verifying Agent Files

Make sure Markdown is well-formed:
- Headers use `#`, `##`, `###`
- Lists have proper indentation
- Code blocks are fenced with ```

---

## Common Development Tasks

### Task: Change the Phase Order

Edit `.pic/config.json`:
```json
"order": [
  "research",
  "design",      // ← Moved before planning
  "planning",
  "implementation",
  "testing",
  "review"
]
```

### Task: Make an Agent More/Less Restrictive

Edit the agent's instruction file in `.claude/agents/`.

For read-only:
```markdown
## Tools Available
You have **read-only** access:
- `Read`, `Glob`, `Grep`

You CANNOT use: `Write`, `Edit`, `Bash`
```

For full access:
```markdown
## Tools Available
You have **full** access to all tools.
```

### Task: Add More Logging

Edit `.claude/hooks/notify-status.sh` or create a new hook.

### Task: Change Decision Document Format

Edit `.claude/skills/pic-decide/SKILL.md` in the template section.

---

## Code Style Guidelines

### JSON Files

- Use 2-space indentation
- Keep keys in logical order
- Add comments sparingly (JSON doesn't support comments, but JSONC does)

### Bash Scripts

```bash
#!/bin/bash
# script-name.sh
# Brief description of what this script does

set -e  # Exit on error

# Constants in UPPER_CASE
LOG_FILE=".pic/status-log.jsonl"

# Variables in lower_case
current_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Functions
log_event() {
    local event="$1"
    echo "{\"timestamp\": \"$current_time\", \"event\": \"$event\"}" >> "$LOG_FILE"
}

# Main logic
log_event "script_started"

# Exit successfully
exit 0
```

### Markdown Files

- Use ATX headers (`#`, `##`) not underlines
- One blank line between sections
- Use fenced code blocks with language tags
- Tables should be aligned

---

## Debugging

### Problem: Skill Not Found

**Symptom:** `/pic-start` says "Unknown skill"

**Solution:**
1. Check skill directory exists: `ls .claude/skills/pic-start/`
2. Check SKILL.md exists: `cat .claude/skills/pic-start/SKILL.md`
3. Restart Claude Code (skills load on startup)

### Problem: Agent Fails to Spawn

**Symptom:** "Agent type 'xxx' not found"

**Solution:**
1. Check `taskAgentType` in config matches a valid type
2. Valid types: `Explore`, `planner`, `builder`, `reviewer`, `test-writer`, `security-auditor`, `refactorer`, `fixer`

### Problem: State File Corrupted

**Symptom:** JSON parse errors

**Solution:**
```bash
# Validate JSON
cat .pic/state.json | python -m json.tool

# If invalid, reset
bash scripts/pic-init.sh
```

### Problem: Hook Not Running

**Symptom:** Events not being logged

**Solution:**
1. Check hook is executable: `ls -la .claude/hooks/`
2. Make executable: `chmod +x .claude/hooks/*.sh`
3. Check hook syntax: `bash -n .claude/hooks/on-decision-made.sh`

### Reading Debug Information

```bash
# View recent activity
tail -20 .pic/status-log.jsonl

# View current state
cat .pic/state.json | python -m json.tool

# Check for errors in hooks
bash -x .claude/hooks/validate-pic-action.sh "test"
```

---

## Summary

1. **Understand the structure** - Know what each file and folder does
2. **Make small changes** - One thing at a time
3. **Test frequently** - After each change
4. **Backup first** - Before major modifications
5. **Document everything** - Update docs when you change behavior

When in doubt, read the existing code. The patterns are consistent throughout the project.
