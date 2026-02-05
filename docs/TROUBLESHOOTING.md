# Troubleshooting Guide

This guide helps you solve common problems with the PIC Agentic Organizational System. Problems are organized by symptom so you can quickly find solutions.

---

## Table of Contents

1. [Quick Diagnosis](#quick-diagnosis)
2. [Installation Problems](#installation-problems)
3. [Initialization Problems](#initialization-problems)
4. [Workflow Problems](#workflow-problems)
5. [Skill Problems](#skill-problems)
6. [Agent Problems](#agent-problems)
7. [State Problems](#state-problems)
8. [Performance Problems](#performance-problems)
9. [Recovery Procedures](#recovery-procedures)

---

## Quick Diagnosis

### Diagnostic Commands

Run these commands to gather information about your system:

```bash
# Check if Claude Code is available
claude --version

# Check if .pic directory exists
ls -la .pic/

# View current state
cat .pic/state.json

# View recent activity
tail -10 .pic/status-log.jsonl

# Check for syntax errors in config
cat .pic/config.json | python -m json.tool

# List available skills
ls .claude/skills/

# Check hook permissions
ls -la .claude/hooks/
```

### Quick Fixes

| Symptom | Quick Fix |
|---------|-----------|
| "No active workflow" | Run `/pic-start [problem]` |
| "Unknown skill" | Restart Claude Code |
| "State file corrupted" | Run `bash scripts/pic-init.sh` |
| "Permission denied" | Run `chmod +x .claude/hooks/*.sh` |
| "Agent not found" | Check `taskAgentType` in config |

---

## Installation Problems

### Problem: Claude Code Not Found

**Symptom:**
```
bash: claude: command not found
```

**Cause:** Claude Code is not installed or not in your PATH.

**Solution:**
1. Install Claude Code from Anthropic
2. Verify installation:
   ```bash
   which claude
   ```
3. If installed but not found, add to PATH:
   ```bash
   export PATH=$PATH:/path/to/claude
   ```

### Problem: Bash Not Available (Windows)

**Symptom:**
```
'bash' is not recognized as an internal or external command
```

**Cause:** Windows doesn't have bash by default.

**Solution:**
1. Install Git for Windows from https://git-scm.com
2. Use Git Bash instead of Command Prompt or PowerShell
3. Or use Windows Subsystem for Linux (WSL)

### Problem: Scripts Won't Run

**Symptom:**
```
Permission denied
```

**Cause:** Scripts don't have execute permission.

**Solution:**
```bash
chmod +x scripts/*.sh
chmod +x .claude/hooks/*.sh
```

---

## Initialization Problems

### Problem: pic-init.sh Fails

**Symptom:**
```
bash: scripts/pic-init.sh: No such file or directory
```

**Cause:** You're not in the project directory.

**Solution:**
```bash
cd /path/to/nemotron_PIC_lambert
ls scripts/  # Verify pic-init.sh exists
bash scripts/pic-init.sh
```

### Problem: .pic Directory Already Exists Warning

**Symptom:**
```
Warning: An active workflow exists.
Do you want to reset and lose current state? (y/N)
```

**Cause:** There's an existing workflow.

**Solution:**
- Type `y` to reset and start fresh
- Type `n` to keep existing workflow
- Use `/pic-status` in Claude Code to see current state

### Problem: Config File Invalid

**Symptom:**
```
json: cannot unmarshal...
```
or
```
Expecting property name...
```

**Cause:** JSON syntax error in config.json.

**Solution:**
1. Validate the JSON:
   ```bash
   cat .pic/config.json | python -m json.tool
   ```
2. Look for common errors:
   - Missing commas
   - Trailing commas
   - Single quotes instead of double quotes
   - Missing closing braces

3. Fix the error or restore from backup:
   ```bash
   # If you have a backup
   cp .pic/config.json.backup .pic/config.json

   # Or reinitialize
   bash scripts/pic-init.sh
   ```

---

## Workflow Problems

### Problem: Workflow Won't Start

**Symptom:**
```
Cannot start workflow: [error message]
```

**Possible Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Another workflow active | Run `/pic-status` to check, then finish or reset |
| State file missing | Run `bash scripts/pic-init.sh` |
| Config file invalid | Check JSON syntax |

### Problem: Workflow Stuck

**Symptom:** No progress for a long time.

**Diagnosis:**
```
/pic-status
```

**Solutions by Status:**

| Status | Solution |
|--------|----------|
| `in_progress` | Agent is still working - wait or check logs |
| `blocked` | Something is blocking - check conflicts |
| `pending` | Handoff didn't happen - try `/pic-handoff` |

### Problem: Phase Doesn't Transition

**Symptom:** Phase says "in_progress" but nothing is happening.

**Solution:**
1. Check if agent completed:
   ```bash
   tail -20 .pic/status-log.jsonl | grep "completed"
   ```

2. Manually trigger handoff:
   ```
   /pic-handoff Phase completed, moving to next
   ```

3. If still stuck, check state file:
   ```bash
   cat .pic/state.json
   ```

### Problem: Workflow Completed But Files Missing

**Symptom:** Workflow finished but expected output isn't there.

**Cause:** Implementation phase may have failed silently.

**Solution:**
1. Check what was created:
   ```bash
   git status  # If using git
   find . -mmin -60 -type f  # Files modified in last hour
   ```

2. Check logs for errors:
   ```bash
   grep -i "error\|fail" .pic/status-log.jsonl
   ```

3. Look at the implementation phase output in the workflow state.

---

## Skill Problems

### Problem: Skill Not Recognized

**Symptom:**
```
Unknown skill: pic-start
```

**Causes & Solutions:**

1. **Skill files missing**
   ```bash
   ls .claude/skills/pic-start/SKILL.md
   ```
   If missing, recreate from documentation or backup.

2. **Claude Code needs restart**
   - Exit Claude Code
   - Restart it: `claude`
   - Skills are loaded on startup

3. **Wrong directory**
   - Make sure you're in the project root
   - Skills are relative to current directory

### Problem: Skill Runs But Does Nothing

**Symptom:** No error, but also no effect.

**Diagnosis:**
1. Check if state was updated:
   ```bash
   cat .pic/state.json
   ```

2. Check logs:
   ```bash
   tail -5 .pic/status-log.jsonl
   ```

**Common Causes:**
- Skill conditions not met (e.g., no active workflow for /pic-status)
- Skill encountered silent error

### Problem: Skill Shows Error

**Symptom:**
```
Error: [specific error message]
```

**Solutions by Error:**

| Error | Solution |
|-------|----------|
| "No active workflow" | Start one with `/pic-start` |
| "State file not found" | Run `bash scripts/pic-init.sh` |
| "Permission denied" | Check file permissions |
| "JSON parse error" | Fix state.json syntax |

---

## Agent Problems

### Problem: Agent Type Not Found

**Symptom:**
```
Agent type 'pic-research' not found
```

**Cause:** Config uses custom agent names instead of Claude Code built-in types.

**Solution:**
1. Check config.json for correct `taskAgentType`:
   ```bash
   grep taskAgentType .pic/config.json
   ```

2. Valid types are:
   - `Explore`
   - `planner`
   - `builder`
   - `reviewer`
   - `test-writer`
   - `security-auditor`
   - `refactorer`
   - `fixer`
   - `orchestrator`

3. Fix the config to use valid types.

### Problem: Agent Produces Wrong Output

**Symptom:** Agent runs but output doesn't match expectations.

**Cause:** Instructions may be unclear or context missing.

**Solution:**
1. Review agent instructions:
   ```bash
   cat .claude/agents/pic-[phase].md
   ```

2. Check what context was provided in the handoff.

3. Clarify instructions if needed.

### Problem: Agent Runs Forever

**Symptom:** Agent never completes.

**Solution:**
1. Wait a reasonable time (complex tasks take longer).

2. Check if there's output in progress:
   ```bash
   tail -f .pic/status-log.jsonl
   ```

3. If truly stuck, cancel and restart:
   - Exit Claude Code (Ctrl+C)
   - Restart and try again

---

## State Problems

### Problem: State File Corrupted

**Symptom:**
```
Unexpected token in JSON
SyntaxError: JSON.parse
```

**Solution:**
1. Try to validate and see the error:
   ```bash
   cat .pic/state.json | python -m json.tool
   ```

2. If error is minor, fix it manually.

3. If severely corrupted, reinitialize:
   ```bash
   bash scripts/pic-init.sh
   ```

### Problem: State Shows Wrong Phase

**Symptom:** `/pic-status` shows wrong current phase.

**Solution:**
1. Manually fix state.json:
   ```bash
   # Edit .pic/state.json
   # Change "currentPhase" to correct value
   ```

2. Or reinitialize and start over.

### Problem: Log File Too Large

**Symptom:** `.pic/status-log.jsonl` is very large.

**Solution:**
1. Archive old logs:
   ```bash
   mv .pic/status-log.jsonl .pic/status-log.jsonl.old
   touch .pic/status-log.jsonl
   ```

2. Or truncate (lose history):
   ```bash
   echo "" > .pic/status-log.jsonl
   ```

### Problem: Decisions Not Showing

**Symptom:** Made decisions but they're not listed.

**Solution:**
1. Check decisions directory:
   ```bash
   ls .pic/decisions/
   ```

2. Check state file for references:
   ```bash
   grep -A5 '"decisions"' .pic/state.json
   ```

3. Decision may have been created but not linked to state.

---

## Performance Problems

### Problem: Workflow Is Very Slow

**Symptom:** Each phase takes a long time.

**Possible Causes:**

1. **Complex problem** - Normal for difficult tasks
2. **Large codebase** - Research phase searches everything
3. **Network issues** - Web searches may be slow

**Solutions:**
- Break problem into smaller parts
- Be more specific in problem statement
- Ensure stable internet connection

### Problem: Claude Code Is Unresponsive

**Symptom:** No response to commands.

**Solution:**
1. Wait a moment - it may be processing.

2. Check if a long-running task is in progress.

3. Exit and restart:
   ```bash
   # Press Ctrl+C
   claude
   ```

---

## Recovery Procedures

### Complete Reset

If nothing else works, reset everything:

```bash
# Backup first (optional)
cp -r .pic .pic.backup
cp -r .claude .claude.backup

# Reinitialize
bash scripts/pic-init.sh

# Restart Claude Code
claude
```

### Restore From Backup

If you have a backup:

```bash
# Restore .pic folder
rm -rf .pic
cp -r .pic.backup .pic

# Restore .claude folder
rm -rf .claude
cp -r .claude.backup .claude
```

### Manual State Repair

If state.json is damaged but recoverable:

1. Open `.pic/state.json` in a text editor

2. Look for the structure:
   ```json
   {
     "initialized": true,
     "workflow": "WF-...",
     "currentPhase": "...",
     ...
   }
   ```

3. Fix any JSON syntax errors:
   - Add missing commas
   - Fix quote marks
   - Add missing braces

4. Validate:
   ```bash
   cat .pic/state.json | python -m json.tool
   ```

### Emergency Workflow Abort

If you need to stop everything immediately:

1. Exit Claude Code (Ctrl+C)

2. Reset state:
   ```bash
   bash scripts/pic-init.sh
   ```
   (Type `y` to confirm reset)

3. Restart and try again.

---

## Getting More Help

If you've tried everything and still have problems:

1. **Document the issue:**
   - What you were trying to do
   - What happened
   - Error messages (exact text)
   - What you've already tried

2. **Gather diagnostic information:**
   ```bash
   cat .pic/state.json
   tail -50 .pic/status-log.jsonl
   claude --version
   ```

3. **Check documentation:**
   - [User Guide](USER_GUIDE.md)
   - [Developer Guide](DEVELOPER_GUIDE.md)
   - [Architecture](ARCHITECTURE.md)

4. **Review this guide** for similar problems.

---

## Summary of Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Skill not found | Restart Claude Code |
| State corrupted | `bash scripts/pic-init.sh` |
| Permission denied | `chmod +x .claude/hooks/*.sh` |
| Workflow stuck | `/pic-handoff` or restart |
| Agent not found | Fix `taskAgentType` in config |
| Nothing works | Complete reset (see above) |
