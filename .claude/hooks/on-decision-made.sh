#!/bin/bash
# on-decision-made.sh
# PostToolUse hook for Write|Edit - detects and logs decision document creation

TOOL_INPUT="$1"
TOOL_OUTPUT="$2"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"

# Extract file path from tool input
FILE_PATH=$(echo "$TOOL_INPUT" | grep -oP '"file_path"\s*:\s*"\K[^"]+' 2>/dev/null || echo "")

# Check if this is a decision document
if [[ "$FILE_PATH" == *".pic/decisions/DEC-"* ]]; then
    # Extract decision ID from path
    DECISION_ID=$(basename "$FILE_PATH" .md)

    # Log the decision creation
    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"decision_file_written\", \"decision\": \"$DECISION_ID\", \"path\": \"$FILE_PATH\"}" >> "$LOG_FILE"
    fi

    echo "Decision document created: $DECISION_ID"
fi

# Check if this is a handoff document
if [[ "$FILE_PATH" == *".pic/handoffs/"* ]]; then
    HANDOFF_FILE=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"handoff_file_written\", \"file\": \"$HANDOFF_FILE\"}" >> "$LOG_FILE"
    fi

    echo "Handoff document created: $HANDOFF_FILE"
fi

# Check if this is a conflict document
if [[ "$FILE_PATH" == *".pic/conflicts/CON-"* ]]; then
    CONFLICT_ID=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"conflict_file_written\", \"conflict\": \"$CONFLICT_ID\"}" >> "$LOG_FILE"
    fi

    echo "Conflict document created: $CONFLICT_ID"
fi

# Check if this is an integration result
if [[ "$FILE_PATH" == *".pic/integration-results/INT-"* ]]; then
    INT_ID=$(basename "$FILE_PATH" .md)

    if [ -f "$LOG_FILE" ]; then
        echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"integration_result_written\", \"id\": \"$INT_ID\"}" >> "$LOG_FILE"
    fi

    echo "Integration result created: $INT_ID"
fi

exit 0
