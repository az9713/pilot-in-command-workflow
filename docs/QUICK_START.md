# Quick Start Guide

Welcome! This guide will get you using the PIC system in 5 minutes, then walk you through 10 hands-on examples.

---

## Prerequisites

Before starting, make sure you have:

1. **Claude Code installed** - The AI coding assistant from Anthropic
2. **A terminal/command line** - Windows PowerShell, Git Bash, macOS Terminal, or Linux terminal
3. **This project folder** - The folder containing this documentation

### How to Check if Claude Code is Installed

Open your terminal and type:
```bash
claude --version
```

If you see a version number, you're ready! If not, visit [Claude Code documentation](https://docs.anthropic.com/claude-code) to install it.

---

## Step 1: Open the Project

Open your terminal and navigate to the project folder:

```bash
# On Windows (PowerShell)
cd C:\Users\YourName\Downloads\nemotron_PIC_lambert

# On macOS/Linux
cd ~/Downloads/nemotron_PIC_lambert
```

**Verify you're in the right place:**
```bash
ls
```

You should see files like `CLAUDE.md`, `scripts/`, `.claude/`, and `.pic/`.

---

## Step 2: Initialize the System

Run the initialization script:

```bash
bash scripts/pic-init.sh
```

**What you should see:**
```
=== PIC System Initialization ===

Creating subdirectories...
Initializing state.json...
Initializing status-log.jsonl...
...
=== PIC System Ready ===

Use /pic-start [problem] to begin a new workflow.
```

**What this does:**
- Creates the `.pic/` folder for storing workflow state
- Sets up empty log files
- Prepares the system for your first workflow

---

## Step 3: Start Claude Code

Launch Claude Code in this folder:

```bash
claude
```

You'll see the Claude Code interface. This is where you'll type commands.

---

## Step 4: Your First Workflow

Type this command in Claude Code:

```
/pic-start Create a hello world script
```

**What happens next:**
1. The system initializes a new workflow
2. The Research PIC gathers information
3. Each phase runs in sequence
4. You get a working script at the end

---

## 10 Example Use Cases

These examples go from simple to more complex. Try them in order to build your skills.

---

### Example 1: Hello World Script

**Goal:** Create your first script using the PIC system.

**Command:**
```
/pic-start Create a bash script that prints "Hello, World!"
```

**What You'll Learn:**
- How the six phases work
- How agents hand off to each other
- Where output files are created

**Expected Output:**
- A file `scripts/hello-world.sh` that prints "Hello, World!"

---

### Example 2: Check Workflow Status

**Goal:** Learn to monitor progress during a workflow.

**Command (while a workflow is running):**
```
/pic-status
```

**What You'll See:**
```
## PIC Workflow Status

Workflow ID: WF-20260204-123456
Problem: Create a bash script...

Phase Progress:
| Phase          | Status      |
|----------------|-------------|
| Research       | ✓ Completed |
| Planning       | > In Progress |
| Design         | Pending     |
...
```

**What You'll Learn:**
- How to track which phase is active
- How to see what's been completed
- How to view recent activity

---

### Example 3: Calculator Script

**Goal:** Create something slightly more complex.

**Command:**
```
/pic-start Create a bash script that adds two numbers passed as arguments
```

**Expected Behavior:**
```bash
$ bash scripts/calculator.sh 5 3
8
```

**What You'll Learn:**
- How the system handles requirements with parameters
- How Planning breaks down the task
- How Implementation handles command-line arguments

---

### Example 4: File Counter Utility

**Goal:** Create a utility that counts files in a directory.

**Command:**
```
/pic-start Create a script that counts how many files are in a given directory
```

**Expected Behavior:**
```bash
$ bash scripts/count-files.sh /home/user/documents
42 files found
```

**What You'll Learn:**
- How Research investigates existing patterns
- How Design specifies the interface
- Error handling (what if directory doesn't exist?)

---

### Example 5: Recording a Decision

**Goal:** Learn to document important decisions formally.

**During any workflow, type:**
```
/pic-decide Choose scripting language
```

**You'll be prompted for:**
1. What decision was made
2. What alternatives were considered
3. Why this choice was made

**Result:**
- Creates `.pic/decisions/DEC-001.md`
- Documents the decision for future reference

**What You'll Learn:**
- How to create formal decision records
- Why documentation matters
- How to reference past decisions

---

### Example 6: Temperature Converter

**Goal:** Create a multi-function utility.

**Command:**
```
/pic-start Create a script that converts temperatures between Celsius and Fahrenheit
```

**Expected Behavior:**
```bash
$ bash scripts/temp-convert.sh 100 C
100°C = 212°F

$ bash scripts/temp-convert.sh 32 F
32°F = 0°C
```

**What You'll Learn:**
- How Design handles multiple use cases
- How Implementation structures code for clarity
- How Testing verifies multiple scenarios

---

### Example 7: Simple Text Formatter

**Goal:** Create a text processing utility.

**Command:**
```
/pic-start Create a script that converts text to uppercase
```

**Expected Behavior:**
```bash
$ echo "hello world" | bash scripts/uppercase.sh
HELLO WORLD
```

**What You'll Learn:**
- How to handle standard input (piped data)
- Unix philosophy of small, composable tools
- How Testing validates different input methods

---

### Example 8: Date Formatter

**Goal:** Create a utility with multiple output formats.

**Command:**
```
/pic-start Create a script that displays the current date in different formats (ISO, US, European)
```

**Expected Behavior:**
```bash
$ bash scripts/date-format.sh iso
2026-02-04

$ bash scripts/date-format.sh us
02/04/2026

$ bash scripts/date-format.sh eu
04/02/2026
```

**What You'll Learn:**
- How Planning identifies all required formats
- How Design creates a flexible interface
- How to handle invalid arguments gracefully

---

### Example 9: System Information Reporter

**Goal:** Create a more comprehensive utility.

**Command:**
```
/pic-start Create a script that displays system information including OS, memory, and disk space
```

**Expected Output:**
```
System Information Report
=========================
OS: Linux 5.15.0
Memory: 16GB total, 8GB used
Disk: 500GB total, 200GB free
```

**What You'll Learn:**
- How Research finds system-specific commands
- How Implementation handles cross-platform differences
- How Review checks for edge cases

---

### Example 10: Running an Integration Test

**Goal:** Learn to test multiple components together.

**Command (after creating several scripts):**
```
/pic-integration scripts/calculator.sh scripts/temp-convert.sh
```

**What This Does:**
1. Tests that both scripts work independently
2. Tests them together (if there are interactions)
3. Creates a report in `.pic/integration-results/`

**What You'll Learn:**
- The "Integration Over Ablation" principle
- How to verify components work together
- How to read integration test reports

---

## What's Next?

Congratulations! You've completed the Quick Start Guide. Here's what to explore next:

| If You Want To... | Read This |
|-------------------|-----------|
| Understand all commands in detail | [Reference Guide](REFERENCE.md) |
| Learn the full workflow process | [User Guide](USER_GUIDE.md) |
| Modify or extend the system | [Developer Guide](DEVELOPER_GUIDE.md) |
| Understand how it works inside | [Architecture Guide](ARCHITECTURE.md) |
| Fix problems | [Troubleshooting Guide](TROUBLESHOOTING.md) |

---

## Common Questions

### Q: How long does a workflow take?
**A:** Simple tasks (like hello world) take 1-2 minutes. Complex tasks may take longer depending on the scope.

### Q: Can I stop a workflow in the middle?
**A:** Yes. Just close Claude Code. Your progress is saved in `.pic/state.json`. You can resume later.

### Q: What if something goes wrong?
**A:** See the [Troubleshooting Guide](TROUBLESHOOTING.md). Most issues have simple solutions.

### Q: Can I skip phases?
**A:** By default, no. All six phases run in order. This ensures quality. Advanced users can configure this in `.pic/config.json`.

---

## Getting Help

If you're stuck:

1. Check `/pic-status` to see current state
2. Read the [Troubleshooting Guide](TROUBLESHOOTING.md)
3. Look at `.pic/status-log.jsonl` for activity history
4. Review `.pic/state.json` to see full workflow state
