#!/bin/bash
# audit-tool-use.sh
# PostToolUse hook for ALL tools - logs tool usage to audit log
# This provides comprehensive tracking of every tool invocation during PIC workflows
#
# Windows/MINGW compatible - uses sed instead of grep -oP

TOOL_NAME="$1"
TOOL_INPUT="$2"
TOOL_OUTPUT="$3"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
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

# Only log if PIC system state file exists
if [ ! -f "$STATE_FILE" ]; then
    exit 0
fi

# Check if workflow is initialized
INITIALIZED=$(cat "$STATE_FILE" | json_get_bool "initialized")
[ -z "$INITIALIZED" ] && INITIALIZED="false"

if [ "$INITIALIZED" != "true" ]; then
    exit 0
fi

# Ensure audit log directory exists
AUDIT_DIR=$(dirname "$AUDIT_LOG")
mkdir -p "$AUDIT_DIR" 2>/dev/null

# Extract workflow and phase info from state
WORKFLOW=$(cat "$STATE_FILE" | json_get "workflow")
[ -z "$WORKFLOW" ] && WORKFLOW="none"

PHASE=$(cat "$STATE_FILE" | json_get "currentPhase")
[ -z "$PHASE" ] && PHASE="none"

# Truncate large inputs/outputs (keep first 2000 chars)
INPUT_PREVIEW=$(echo "$TOOL_INPUT" | head -c 2000 | tr '\n' ' ' | tr '"' "'" | tr '\\' '/')
OUTPUT_PREVIEW=$(echo "$TOOL_OUTPUT" | head -c 2000 | tr '\n' ' ' | tr '"' "'" | tr '\\' '/')

# Get lengths
INPUT_LENGTH=${#TOOL_INPUT}
OUTPUT_LENGTH=${#TOOL_OUTPUT}

# Generate audit entry ID (use milliseconds if available, else seconds)
if date +%s%N >/dev/null 2>&1; then
    AUDIT_ID="AUD-$(date +%s%N | cut -c1-13)"
else
    AUDIT_ID="AUD-$(date +%s)000"
fi

# Write audit entry (use printf to avoid issues with special characters)
printf '{"id":"%s","timestamp":"%s","workflow":"%s","phase":"%s","eventType":"tool_use","tool":"%s","inputPreview":"%s","outputPreview":"%s","inputLength":%d,"outputLength":%d}\n' \
    "$AUDIT_ID" \
    "$TIMESTAMP" \
    "$WORKFLOW" \
    "$PHASE" \
    "$TOOL_NAME" \
    "$INPUT_PREVIEW" \
    "$OUTPUT_PREVIEW" \
    "$INPUT_LENGTH" \
    "$OUTPUT_LENGTH" >> "$AUDIT_LOG"

exit 0
