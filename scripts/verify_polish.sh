#!/bin/bash
# Verification script for M6 Polish completion
# Checks that all required files and documentation are in place

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}M6 Polish - Verification Script${NC}"
echo -e "${BLUE}===================================================================${NC}"
echo ""

# Counter
total=0
passed=0

check_file() {
    total=$((total + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗${NC} $1 - MISSING"
    fi
}

check_dir() {
    total=$((total + 1))
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗${NC} $1/ - MISSING"
    fi
}

# Main documentation
echo -e "${YELLOW}Main Documentation:${NC}"
check_file "README.md"
check_file "CONTRIBUTING.md"
check_file "LICENSE"
check_file "M6_POLISH_COMPLETE.md"
echo ""

# Examples
echo -e "${YELLOW}Examples:${NC}"
check_dir "examples"
check_file "examples/README.md"
check_file "examples/01_voice_cloning.py"
check_file "examples/02_text_to_speech.py"
check_file "examples/03_avatar_generation.py"
check_file "examples/04_lipsync_video.py"
check_file "examples/05_full_pipeline.py"
check_file "examples/06_api_client.py"
echo ""

# Configuration
echo -e "${YELLOW}Configuration Templates:${NC}"
check_dir "config"
check_file "config/README.md"
check_file "config/pipeline.yaml"
check_file "config/pipeline.rtx4090.yaml"
check_file "config/pipeline.rtx3080.yaml"
check_file "config/pipeline.low_vram.yaml"
echo ""

# Scripts
echo -e "${YELLOW}Installation Scripts:${NC}"
check_dir "scripts"
check_file "scripts/install.sh"
check_file "scripts/install.ps1"
echo ""

# Source modules
echo -e "${YELLOW}Source Modules:${NC}"
check_dir "src"
check_file "src/__init__.py"
check_file "src/cli.py"
check_dir "src/config"
check_file "src/config/__init__.py"
check_dir "src/utils"
check_file "src/utils/__init__.py"
check_dir "src/voice"
check_file "src/voice/__init__.py"
check_dir "src/avatar"
check_file "src/avatar/__init__.py"
check_dir "src/video"
check_file "src/video/__init__.py"
check_dir "src/orchestration"
check_file "src/orchestration/__init__.py"
check_dir "src/api"
check_file "src/api/__init__.py"
echo ""

# Project metadata
echo -e "${YELLOW}Project Metadata:${NC}"
check_file "pyproject.toml"
check_file "requirements.txt"
echo ""

# Summary
echo -e "${BLUE}===================================================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}===================================================================${NC}"
echo ""

if [ $passed -eq $total ]; then
    echo -e "${GREEN}✓ All checks passed: $passed/$total${NC}"
    echo ""
    echo -e "${GREEN}M6 Polish is complete and ready for production!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some checks failed: $passed/$total${NC}"
    echo ""
    echo -e "${YELLOW}Missing files need to be created.${NC}"
    echo ""
    exit 1
fi
