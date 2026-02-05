#!/bin/bash
# notify-status.sh
# Notification hook - injects PIC status context into notifications

NOTIFICATION_TYPE="$1"
NOTIFICATION_MESSAGE="$2"
STATE_FILE=".pic/state.json"

# Check if PIC system is active
if [ ! -f "$STATE_FILE" ]; then
    # No PIC system, pass through
    exit 0
fi

# Read current state
INITIALIZED=$(cat "$STATE_FILE" | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")

if [ "$INITIALIZED" = "false" ]; then
    exit 0
fi

# Extract current phase and workflow
CURRENT_PHASE=$(cat "$STATE_FILE" | grep -oP '"currentPhase"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")
WORKFLOW=$(cat "$STATE_FILE" | grep -oP '"workflow"\s*:\s*"\K[^"]+' 2>/dev/null || echo "unknown")

# Inject PIC context into status notifications
if [ "$NOTIFICATION_TYPE" = "status" ]; then
    echo "[PIC: $WORKFLOW | Phase: $CURRENT_PHASE] $NOTIFICATION_MESSAGE"
else
    # For other notification types, pass through
    echo "$NOTIFICATION_MESSAGE"
fi

exit 0
