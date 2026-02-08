#!/bin/bash
# Avatar Pipeline Installation Script
# ====================================================================
# CRITICAL: Requires Python 3.10 or 3.11. Python 3.12+ will NOT work.
# Coqui TTS (a core dependency) does not support Python 3.12+.
# ====================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}===================================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================================================${NC}"
}

print_success() { echo -e "${GREEN}[OK] $1${NC}"; }
print_warning() { echo -e "${YELLOW}[WARNING] $1${NC}"; }
print_error()   { echo -e "${RED}[ERROR] $1${NC}"; }
print_info()    { echo -e "${BLUE}[INFO] $1${NC}"; }

print_header "Avatar Pipeline - Installation Script"

# ── Step 1: Find a compatible Python (3.10 or 3.11) ─────────────────
print_info "Step 1/7: Checking Python version..."

PYTHON_CMD=""
for candidate in python3.11 python3.10 python3 python; do
    if command -v "$candidate" &> /dev/null; then
        ver=$("$candidate" --version 2>&1 | awk '{print $2}')
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -eq 3 ] && [ "$minor" -ge 10 ] && [ "$minor" -lt 12 ]; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    print_error "No compatible Python found!"
    echo ""
    echo "  This project requires Python 3.10 or 3.11."
    echo "  Python 3.12+ will NOT work (Coqui TTS dependency)."
    echo ""
    echo "  Install Python 3.11:"
    echo "    Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "    macOS:         brew install python@3.11"
    echo "    RunPod:        apt install python3.11 python3.11-venv python3.11-dev"
    echo ""
    exit 1
fi

python_version=$("$PYTHON_CMD" --version 2>&1 | awk '{print $2}')
print_success "Using $PYTHON_CMD ($python_version)"

# ── Step 2: Check project directory ──────────────────────────────────
print_info "Step 2/7: Checking project directory..."
if [ ! -f "pyproject.toml" ]; then
    print_error "Not in project root directory (pyproject.toml not found)"
    print_info "Run this script from the avatar-pipeline directory"
    exit 1
fi
print_success "Project directory OK"

# ── Step 3: Create virtual environment ───────────────────────────────
print_info "Step 3/7: Creating virtual environment with $PYTHON_CMD..."

VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists"
    read -p "Remove and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$VENV_DIR"
    else
        print_info "Using existing virtual environment"
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON_CMD" -m venv "$VENV_DIR" --clear
    print_success "Virtual environment created"
fi

# Activate
source "$VENV_DIR/bin/activate"

# Verify the venv Python is correct
venv_ver=$(python --version 2>&1 | awk '{print $2}')
venv_minor=$(echo "$venv_ver" | cut -d. -f2)
if [ "$venv_minor" -ge 12 ]; then
    print_error "Venv Python is $venv_ver (3.12+). This will NOT work."
    print_info "Delete the venv and re-run: rm -rf $VENV_DIR && bash scripts/install.sh"
    exit 1
fi
print_success "Venv Python: $venv_ver"

# ── Step 4: Install dependencies ─────────────────────────────────────
print_info "Step 4/7: Installing dependencies..."
print_warning "This may take 5-10 minutes on first install."

# Upgrade pip
pip install --upgrade pip wheel setuptools > /dev/null 2>&1

# ────────────────────────────────────────────────────────────────────
# CRITICAL: Coqui TTS --no-deps workaround
#
# Coqui AI shut down in 2024. Their TTS package has stale, overly strict
# dependency pins that cause pip to backtrack through dozens of versions
# (10+ minutes) and often fail. The fix: install TTS with --no-deps,
# then install the actual needed dependencies ourselves.
# ────────────────────────────────────────────────────────────────────
print_info "Installing Coqui TTS (with --no-deps workaround)..."
pip install TTS==0.22.0 --no-deps 2>&1 | tail -1

print_info "Installing ML frameworks and dependencies..."
pip install torch torchaudio 2>&1 | tail -1

print_info "Installing remaining dependencies..."
pip install \
    diffusers transformers accelerate \
    mediapipe opencv-python Pillow \
    fastapi "uvicorn[standard]" click \
    pyyaml pydantic python-multipart \
    numpy scipy soundfile librosa scikit-learn \
    einops unidecode num2words \
    2>&1 | tail -1

# Install the project itself (also with --no-deps to avoid re-triggering TTS resolution)
print_info "Installing avatar-pipeline package..."
pip install -e . --no-deps 2>&1 | tail -1

# Install test dependencies
print_info "Installing test dependencies..."
pip install pytest pytest-mock pytest-asyncio pytest-cov httpx 2>&1 | tail -1

print_success "All dependencies installed"

# ── Step 5: Check CUDA ───────────────────────────────────────────────
print_info "Step 5/7: Checking GPU/CUDA availability..."
python -c "
import torch
if torch.cuda.is_available():
    name = torch.cuda.get_device_name(0)
    vram = torch.cuda.get_device_properties(0).total_memory // (1024**2)
    print(f'  GPU: {name} ({vram} MB VRAM)')
    print(f'  CUDA: {torch.version.cuda}')
else:
    print('  No CUDA GPU detected (CPU mode)')
" 2>/dev/null || print_warning "Could not check CUDA"

# ── Step 6: Check FFmpeg ─────────────────────────────────────────────
print_info "Step 6/7: Checking FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    ffmpeg_version=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    print_success "FFmpeg $ffmpeg_version found"
else
    print_warning "FFmpeg not found (needed for video encoding)"
    print_info "  Ubuntu/Debian: sudo apt install ffmpeg"
    print_info "  macOS: brew install ffmpeg"
fi

# ── Step 7: Create directories ───────────────────────────────────────
print_info "Step 7/7: Creating directories..."
mkdir -p storage/voices storage/avatars storage/jobs output
print_success "Directories created"

# ── Summary ──────────────────────────────────────────────────────────
echo ""
print_header "Installation Complete!"
echo ""
echo "  Activate:  source $VENV_DIR/bin/activate"
echo "  Status:    avatar status"
echo "  Tests:     pytest tests/ -v"
echo "  Docs:      docs/avatar-pipeline/INSTALLATION_GUIDE.md"
echo ""
print_warning "Models download automatically on first use (~12GB total):"
echo "    XTTS-v2:   ~2GB (voice cloning)"
echo "    SDXL:      ~7GB (avatar generation)"
echo "    MuseTalk:  ~3GB (lip-sync)"
echo ""
print_success "Setup complete!"
