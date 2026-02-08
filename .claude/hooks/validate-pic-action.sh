#!/bin/bash
# validate-pic-action.sh
# PreToolUse hook for Task tool - logs task spawns, validates PIC actions,
# and captures full task input for audit trail
#
# Windows/MINGW compatible - uses sed instead of grep -oP

TOOL_INPUT="$1"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"
AUDIT_LOG=".pic/audit-log.jsonl"
STATE_FILE=".pic/state.json"

# Helper function to extract JSON string value (Windows compatible)
# Usage: json_get "key" <<< "$json_string"
json_get() {
    local key="$1"
    sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

# Helper function to extract JSON boolean value
json_get_bool() {
    local key="$1"
    sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*\(true\|false\).*/\1/p' | head -1
}

# Extract agent type from tool input if possible
AGENT_TYPE=$(echo "$TOOL_INPUT" | json_get "subagent_type")
[ -z "$AGENT_TYPE" ] && AGENT_TYPE="unknown"

# Log the task spawn to status log
if [ -f "$LOG_FILE" ]; then
    echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"task_spawn\", \"agent\": \"$AGENT_TYPE\"}" >> "$LOG_FILE"
fi

# Validation: Check if PIC system is initialized
if [ -f "$STATE_FILE" ]; then
    INITIALIZED=$(cat "$STATE_FILE" | json_get_bool "initialized")
    [ -z "$INITIALIZED" ] && INITIALIZED="false"

    if [ "$INITIALIZED" = "false" ]; then
        # Only warn for PIC-related agents
        if [[ "$AGENT_TYPE" == pic-* ]]; then
            echo "Warning: PIC system not initialized. Run /pic-start first." >&2
        fi
    fi
fi

# --- AUDIT LOGGING ---
# Only write to audit log if workflow is initialized
if [ -f "$STATE_FILE" ]; then
    INITIALIZED=$(cat "$STATE_FILE" | json_get_bool "initialized")
    [ -z "$INITIALIZED" ] && INITIALIZED="false"

    if [ "$INITIALIZED" = "true" ]; then
        # Ensure audit log directory exists
        AUDIT_DIR=$(dirname "$AUDIT_LOG")
        mkdir -p "$AUDIT_DIR" 2>/dev/null

        # Extract workflow and phase info
        WORKFLOW=$(cat "$STATE_FILE" | json_get "workflow")
        [ -z "$WORKFLOW" ] && WORKFLOW="none"

        PHASE=$(cat "$STATE_FILE" | json_get "currentPhase")
        [ -z "$PHASE" ] && PHASE="none"

        # Extract full prompt from tool input (up to 10000 chars)
        PROMPT=$(echo "$TOOL_INPUT" | json_get "prompt" | head -c 10000 | tr '\n' ' ' | tr '"' "'" | tr '\\' '/')

        # Extract description
        DESCRIPTION=$(echo "$TOOL_INPUT" | json_get "description")

        # Generate audit entry ID (use milliseconds if available, else seconds)
        if date +%s%N >/dev/null 2>&1; then
            AUDIT_ID="AUD-$(date +%s%N | cut -c1-13)"
        else
            AUDIT_ID="AUD-$(date +%s)000"
        fi

        # Store audit ID for correlation with completion hook
        TEMP_DIR="${TEMP:-/tmp}/pic-audit"
        mkdir -p "$TEMP_DIR" 2>/dev/null
        echo "$AUDIT_ID" > "$TEMP_DIR/audit-$$.id"

        # Get prompt length for metrics
        PROMPT_LENGTH=${#PROMPT}

        # Write comprehensive audit entry for agent_start
        printf '{"id":"%s","timestamp":"%s","workflow":"%s","phase":"%s","eventType":"agent_start","agent":"%s","description":"%s","input":{"promptPreview":"%s","promptLength":%d}}\n' \
            "$AUDIT_ID" \
            "$TIMESTAMP" \
            "$WORKFLOW" \
            "$PHASE" \
            "$AGENT_TYPE" \
            "$DESCRIPTION" \
            "$PROMPT" \
            "$PROMPT_LENGTH" >> "$AUDIT_LOG"

        # Also write to phase-specific audit file if it's a PIC agent
        if [[ "$AGENT_TYPE" == pic-* ]]; then
            PHASE_AUDIT_DIR=".pic/audit/$WORKFLOW"
            mkdir -p "$PHASE_AUDIT_DIR" 2>/dev/null

            # Store the full input for this phase
            PHASE_FILE="$PHASE_AUDIT_DIR/$PHASE-input.json"
            printf '{"agent":"%s","phase":"%s","startedAt":"%s","auditId":"%s","fullInput":%s}\n' \
                "$AGENT_TYPE" \
                "$PHASE" \
                "$TIMESTAMP" \
                "$AUDIT_ID" \
                "$TOOL_INPUT" > "$PHASE_FILE" 2>/dev/null || true
        fi
    fi
fi

# Always allow the action (hooks should log, not block in most cases)
exit 0
