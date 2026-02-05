#!/bin/bash
# pic-init.sh
# Initialize the PIC (Pilot in Command) agentic organizational system
# Run this script to set up or reset the .pic/ runtime state directory

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PIC_DIR="$PROJECT_ROOT/.pic"

echo "=== PIC System Initialization ==="
echo ""

# Check if .pic directory exists
if [ -d "$PIC_DIR" ]; then
    # Check if there's an active workflow
    if [ -f "$PIC_DIR/state.json" ]; then
        INITIALIZED=$(cat "$PIC_DIR/state.json" | grep -oP '"initialized"\s*:\s*\K(true|false)' 2>/dev/null || echo "false")
        if [ "$INITIALIZED" = "true" ]; then
            echo "Warning: An active workflow exists."
            echo ""
            read -p "Do you want to reset and lose current state? (y/N) " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "Initialization cancelled. Existing workflow preserved."
                exit 0
            fi
            echo "Resetting existing workflow..."
        fi
    fi
else
    echo "Creating .pic directory structure..."
    mkdir -p "$PIC_DIR"
fi

# Create subdirectories
echo "Creating subdirectories..."
mkdir -p "$PIC_DIR/decisions"
mkdir -p "$PIC_DIR/handoffs"
mkdir -p "$PIC_DIR/conflicts"
mkdir -p "$PIC_DIR/integration-results"

# Initialize or reset state.json
echo "Initializing state.json..."
cat > "$PIC_DIR/state.json" << 'EOF'
{
  "initialized": false,
  "workflow": null,
  "currentPhase": null,
  "currentPIC": null,
  "problem": null,
  "startedAt": null,
  "phases": {
    "research": { "status": "pending", "startedAt": null, "completedAt": null },
    "planning": { "status": "pending", "startedAt": null, "completedAt": null },
    "design": { "status": "pending", "startedAt": null, "completedAt": null },
    "implementation": { "status": "pending", "startedAt": null, "completedAt": null },
    "testing": { "status": "pending", "startedAt": null, "completedAt": null },
    "review": { "status": "pending", "startedAt": null, "completedAt": null }
  },
  "decisions": [],
  "conflicts": [],
  "handoffs": []
}
EOF

# Initialize or reset status-log.jsonl
echo "Initializing status-log.jsonl..."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
echo "{\"timestamp\": \"$TIMESTAMP\", \"event\": \"system_initialized\", \"version\": \"1.0.0\"}" > "$PIC_DIR/status-log.jsonl"

# Check if config.json exists, create default if not
if [ ! -f "$PIC_DIR/config.json" ]; then
    echo "Creating default config.json..."
    cat > "$PIC_DIR/config.json" << 'EOF'
{
  "version": "1.0.0",
  "pics": {
    "order": [
      "research",
      "planning",
      "design",
      "implementation",
      "testing",
      "review"
    ],
    "definitions": {
      "research": {
        "name": "Research PIC",
        "agent": "pic-research",
        "description": "Information gathering and evidence collection",
        "permissions": "read-only",
        "canDelegate": false
      },
      "planning": {
        "name": "Planning PIC",
        "agent": "pic-planning",
        "description": "Strategic planning and roadmap creation",
        "permissions": "acceptEdits",
        "canDelegate": false
      },
      "design": {
        "name": "Design PIC",
        "agent": "pic-design",
        "description": "Technical architecture and system design",
        "permissions": "acceptEdits",
        "canDelegate": false
      },
      "implementation": {
        "name": "Implementation PIC",
        "agent": "pic-implementation",
        "description": "Code execution and feature building",
        "permissions": "full",
        "canDelegate": true
      },
      "testing": {
        "name": "Testing PIC",
        "agent": "pic-testing",
        "description": "Validation and integration testing",
        "permissions": "full",
        "canDelegate": true
      },
      "review": {
        "name": "Review PIC",
        "agent": "pic-review",
        "description": "Final approval and quality gate",
        "permissions": "read-only",
        "canDelegate": false
      }
    }
  },
  "orchestrator": {
    "agent": "orchestrator",
    "maxParallelAgents": 3,
    "conflictResolutionTimeout": 300
  },
  "workflow": {
    "autoHandoff": false,
    "requireHandoffApproval": true,
    "minEvidenceForDecision": 2
  },
  "logging": {
    "verbosity": "normal",
    "logStatusUpdates": true,
    "logHandoffs": true,
    "logDecisions": true
  },
  "decisions": {
    "numberingPrefix": "DEC",
    "requireRationale": true,
    "requireAlternatives": true
  },
  "integration": {
    "numberingPrefix": "INT",
    "requireTestPlan": true
  }
}
EOF
else
    echo "Existing config.json preserved."
fi

# Make hook scripts executable
echo "Setting hook permissions..."
HOOKS_DIR="$PROJECT_ROOT/.claude/hooks"
if [ -d "$HOOKS_DIR" ]; then
    chmod +x "$HOOKS_DIR"/*.sh 2>/dev/null || true
fi

# Verify structure
echo ""
echo "=== Verification ==="
echo ""
echo "Directory structure:"
find "$PIC_DIR" -type d | sed 's/^/  /'

echo ""
echo "Files:"
find "$PIC_DIR" -type f | sed 's/^/  /'

echo ""
echo "=== PIC System Ready ==="
echo ""
echo "Use /pic-start [problem] to begin a new workflow."
echo "Use /pic-status to check current status."
echo ""
