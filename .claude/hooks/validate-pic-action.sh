#!/bin/bash
# validate-pic-action.sh
# PreToolUse hook for Task tool - logs task spawns and validates PIC actions

TOOL_INPUT="$1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Extract agent type from tool input if possible
AGENT_TYPE=$(echo "$TOOL_INPUT" | grep -oP '"subagent_type"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")

# Log the task spawn
if [ -f "$LOG_FILE" ]; then
    echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"task_spawn\", \"agent\": \"$AGENT_TYPE\"}" >> "$LOG_FILE"
fi

# Validation: Check if PIC system is initialized
if [ -f ".pic/state.json" ]; then
    INITIALIZED=$(cat .pic/state.json | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")

    if [ "$INITIALIZED" = "false" ]; then
        # Only warn for PIC-related agents
        if [[ "$AGENT_TYPE" == pic-* ]]; then
            echo "Warning: PIC system not initialized. Run /pic-start first." >&2
        fi
    fi
fi

# Always allow the action (hooks should log, not block in most cases)
exit 0
