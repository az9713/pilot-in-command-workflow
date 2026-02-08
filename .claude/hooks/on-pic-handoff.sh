#!/bin/bash
# on-pic-handoff.sh
# SubagentStop hook for pic-* agents - logs agent completion and captures full output
# for comprehensive audit trail
#
# Windows/MINGW compatible - uses sed instead of grep -oP

AGENT_NAME="$1"
AGENT_OUTPUT="$2"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"
AUDIT_LOG=".pic/audit-log.jsonl"
STATE_FILE=".pic/state.json"

# Helper function to extract JSON string value (Windows compatible)
json_get() {
    local key="$1"
    sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1
}

# Helper function to extract JSON boolean value
json_get_bool() {
    local key="$1"
    sed -n 's/.*"'"$key"'"[[:space:]]*:[[:space:]]*\(true\|false\).*/\1/p' | head -1
}

# Only process PIC agents
if [[ "$AGENT_NAME" != pic-* ]]; then
    exit 0
fi

# Log the agent completion to status log (with preview)
if [ -f "$LOG_FILE" ]; then
    # Truncate output for status logging (first 200 chars)
    OUTPUT_PREVIEW=$(echo "$AGENT_OUTPUT" | head -c 200 | tr '\n' ' ')
    echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"pic_agent_completed\", \"agent\": \"$AGENT_NAME\", \"output_preview\": \"$OUTPUT_PREVIEW\"}" >> "$LOG_FILE"
fi

# Map agent name to phase
case "$AGENT_NAME" in
    pic-research)
        PHASE="research"
        ;;
    pic-planning)
        PHASE="planning"
        ;;
    pic-design)
        PHASE="design"
        ;;
    pic-implementation)
        PHASE="implementation"
        ;;
    pic-testing)
        PHASE="testing"
        ;;
    pic-review)
        PHASE="review"
        ;;
    *)
        PHASE="unknown"
        ;;
esac

echo "PIC agent completed: $AGENT_NAME (phase: $PHASE)"

# --- AUDIT LOGGING ---
# Only write to audit log if workflow is initialized
if [ -f "$STATE_FILE" ]; then
    INITIALIZED=$(cat "$STATE_FILE" | json_get_bool "initialized")
    [ -z "$INITIALIZED" ] && INITIALIZED="false"

    if [ "$INITIALIZED" = "true" ]; then
        # Ensure audit log directory exists
        AUDIT_DIR=$(dirname "$AUDIT_LOG")
        mkdir -p "$AUDIT_DIR" 2>/dev/null

        # Extract workflow info
        WORKFLOW=$(cat "$STATE_FILE" | json_get "workflow")
        [ -z "$WORKFLOW" ] && WORKFLOW="none"

        # Generate audit entry ID (use milliseconds if available, else seconds)
        if date +%s%N >/dev/null 2>&1; then
            AUDIT_ID="AUD-$(date +%s%N | cut -c1-13)"
        else
            AUDIT_ID="AUD-$(date +%s)000"
        fi

        # Get output length
        OUTPUT_LENGTH=${#AGENT_OUTPUT}

        # Create phase-specific audit directory
        PHASE_AUDIT_DIR=".pic/audit/$WORKFLOW"
        mkdir -p "$PHASE_AUDIT_DIR" 2>/dev/null

        # Write full output to phase-specific file (up to 50KB)
        PHASE_OUTPUT_FILE="$PHASE_AUDIT_DIR/$PHASE-full.json"
        FULL_OUTPUT=$(echo "$AGENT_OUTPUT" | head -c 50000)

        # Escape special characters for JSON
        ESCAPED_OUTPUT=$(echo "$FULL_OUTPUT" | tr '\n' ' ' | tr '"' "'" | tr '\\' '/' | tr '\t' ' ')

        # Write comprehensive phase output file
        printf '{"agent":"%s","phase":"%s","completedAt":"%s","auditId":"%s","outputLength":%d,"output":"%s"}\n' \
            "$AGENT_NAME" \
            "$PHASE" \
            "$TIMESTAMP" \
            "$AUDIT_ID" \
            "$OUTPUT_LENGTH" \
            "$ESCAPED_OUTPUT" > "$PHASE_OUTPUT_FILE" 2>/dev/null || true

        # Truncate for audit log entry (2000 chars)
        OUTPUT_PREVIEW_LONG=$(echo "$AGENT_OUTPUT" | head -c 2000 | tr '\n' ' ' | tr '"' "'" | tr '\\' '/')

        # Write audit log entry for agent_complete
        printf '{"id":"%s","timestamp":"%s","workflow":"%s","phase":"%s","eventType":"agent_complete","agent":"%s","outputLength":%d,"outputPreview":"%s","auditFile":"%s"}\n' \
            "$AUDIT_ID" \
            "$TIMESTAMP" \
            "$WORKFLOW" \
            "$PHASE" \
            "$AGENT_NAME" \
            "$OUTPUT_LENGTH" \
            "$OUTPUT_PREVIEW_LONG" \
            "$PHASE_OUTPUT_FILE" >> "$AUDIT_LOG"

        echo "Audit record created: $AUDIT_ID -> $PHASE_OUTPUT_FILE"
    fi
fi

# Note: State updates are handled by the skill/orchestrator, not this hook
# This hook is for logging/notification purposes only

exit 0
