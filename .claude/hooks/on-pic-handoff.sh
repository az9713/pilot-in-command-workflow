#!/bin/bash
# on-pic-handoff.sh
# SubagentStop hook for pic-* agents - logs agent completion

AGENT_NAME="$1"
AGENT_OUTPUT="$2"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE=".pic/status-log.jsonl"
STATE_FILE=".pic/state.json"

# Only process PIC agents
if [[ "$AGENT_NAME" != pic-* ]]; then
    exit 0
fi

# Log the agent completion
if [ -f "$LOG_FILE" ]; then
    # Truncate output for logging (first 200 chars)
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

# Note: State updates are handled by the skill/orchestrator, not this hook
# This hook is for logging/notification purposes only

exit 0
