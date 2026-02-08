# Avatar Pipeline Installation Script (Windows PowerShell)
# ====================================================================
# CRITICAL: Requires Python 3.10 or 3.11. Python 3.12+ will NOT work.
# Coqui TTS (a core dependency) does not support Python 3.12+.
# ====================================================================

$ErrorActionPreference = "Stop"

function Print-Header {
    param([string]$Message)
    Write-Host "`n===================================================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "===================================================================`n" -ForegroundColor Blue
}

function Print-Success { param([string]$Message); Write-Host "[OK] $Message" -ForegroundColor Green }
function Print-Warning { param([string]$Message); Write-Host "[WARNING] $Message" -ForegroundColor Yellow }
function Print-Error   { param([string]$Message); Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Print-Info    { param([string]$Message); Write-Host "[INFO] $Message" -ForegroundColor Cyan }

Print-Header "Avatar Pipeline - Installation Script (Windows)"

# -- Step 1: Find compatible Python (3.10 or 3.11) --------------------
Print-Info "Step 1/7: Checking Python version..."

$pythonCmd = $null
foreach ($candidate in @("python3.11", "python3.10", "python3", "python", "py -3.11", "py -3.10")) {
    try {
        $verOutput = & $candidate.Split()[0] ($candidate.Split() | Select-Object -Skip 1) --version 2>&1
        if ($verOutput -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            if ($major -eq 3 -and $minor -ge 10 -and $minor -lt 12) {
                $pythonCmd = $candidate
                $pythonVersion = "$($Matches[1]).$($Matches[2]).$($Matches[3])"
                break
            }
        }
    } catch { continue }
}

if (-not $pythonCmd) {
    Print-Error "No compatible Python found!"
    Write-Host ""
    Write-Host "  This project requires Python 3.10 or 3.11."
    Write-Host "  Python 3.12+ will NOT work (Coqui TTS dependency)."
    Write-Host ""
    Write-Host "  Download Python 3.11: https://www.python.org/downloads/release/python-3119/"
    Write-Host "  During install, check 'Add Python to PATH'"
    Write-Host ""
    exit 1
}

Print-Success "Using $pythonCmd ($pythonVersion)"

# -- Step 2: Check project directory -----------------------------------
Print-Info "Step 2/7: Checking project directory..."
if (-not (Test-Path "pyproject.toml")) {
    Print-Error "Not in project root directory (pyproject.toml not found)"
    Print-Info "Run this script from the avatar-pipeline directory"
    exit 1
}
Print-Success "Project directory OK"

# -- Step 3: Create virtual environment --------------------------------
Print-Info "Step 3/7: Creating virtual environment..."

$venvDir = "venv"
if (Test-Path $venvDir) {
    Print-Warning "Virtual environment already exists"
    $response = Read-Host "Remove and recreate? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Remove-Item -Recurse -Force $venvDir
    } else {
        Print-Info "Using existing virtual environment"
    }
}

if (-not (Test-Path $venvDir)) {
    & $pythonCmd.Split()[0] ($pythonCmd.Split() | Select-Object -Skip 1) -m venv $venvDir --clear
    Print-Success "Virtual environment created"
}

# Activate
& ".\$venvDir\Scripts\Activate.ps1"

# Verify venv Python version
$venvVer = python --version 2>&1
if ($venvVer -match "Python 3\.(\d+)") {
    $venvMinor = [int]$Matches[1]
    if ($venvMinor -ge 12) {
        Print-Error "Venv Python is 3.$venvMinor (3.12+). This will NOT work."
        Print-Info "Delete the venv and re-run: Remove-Item -Recurse venv; .\scripts\install.ps1"
        exit 1
    }
    Print-Success "Venv Python: $venvVer"
}

# -- Step 4: Install dependencies --------------------------------------
Print-Info "Step 4/7: Installing dependencies..."
Print-Warning "This may take 5-10 minutes on first install."

# Upgrade pip
python -m pip install --upgrade pip wheel setuptools | Out-Null

# -----------------------------------------------------------------------
# CRITICAL: Coqui TTS --no-deps workaround
#
# Coqui AI shut down in 2024. Their TTS package has stale, overly strict
# dependency pins that cause pip to backtrack through dozens of versions
# (10+ minutes) and often fail. The fix: install TTS with --no-deps,
# then install the actual needed dependencies ourselves.
# -----------------------------------------------------------------------
Print-Info "Installing Coqui TTS (with --no-deps workaround)..."
pip install TTS==0.22.0 --no-deps

Print-Info "Installing ML frameworks..."
pip install torch torchaudio

Print-Info "Installing remaining dependencies..."
pip install diffusers transformers accelerate mediapipe opencv-python Pillow fastapi "uvicorn[standard]" click pyyaml pydantic python-multipart numpy scipy soundfile librosa scikit-learn einops unidecode num2words coqpit

# Install project (--no-deps to skip TTS resolution)
Print-Info "Installing avatar-pipeline package..."
pip install -e . --no-deps

# Install test dependencies
Print-Info "Installing test dependencies..."
pip install pytest pytest-mock pytest-asyncio pytest-cov httpx

Print-Success "All dependencies installed"

# -- Step 5: Check CUDA -------------------------------------------------
Print-Info "Step 5/7: Checking GPU/CUDA availability..."
try {
    python -c "import torch; print('  GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None (CPU mode)'); print('  CUDA:', torch.version.cuda if torch.cuda.is_available() else 'N/A')"
} catch {
    Print-Warning "Could not check CUDA"
}

# -- Step 6: Check FFmpeg -----------------------------------------------
Print-Info "Step 6/7: Checking FFmpeg..."
try {
    $ffmpegVer = ffmpeg -version 2>&1 | Select-String "ffmpeg version" | ForEach-Object { $_.ToString().Split()[2] }
    Print-Success "FFmpeg $ffmpegVer found"
} catch {
    Print-Warning "FFmpeg not found (needed for video encoding)"
    Print-Info "  Install: choco install ffmpeg"
    Print-Info "  Or download: https://www.gyan.dev/ffmpeg/builds/"
}

# -- Step 7: Create directories -----------------------------------------
Print-Info "Step 7/7: Creating directories..."
@("storage\voices", "storage\avatars", "storage\jobs", "output") | ForEach-Object {
    New-Item -ItemType Directory -Path $_ -Force | Out-Null
}
Print-Success "Directories created"

# -- Summary -------------------------------------------------------------
Write-Host ""
Print-Header "Installation Complete!"
Write-Host ""
Write-Host "  Activate:  .\$venvDir\Scripts\Activate.ps1"
Write-Host "  Status:    avatar status"
Write-Host "  Tests:     pytest tests/ -v"
Write-Host "  Docs:      docs\avatar-pipeline\INSTALLATION_GUIDE.md"
Write-Host ""
Print-Warning "Models download automatically on first use (~12GB total):"
Write-Host "    XTTS-v2:   ~2GB (voice cloning)"
Write-Host "    SDXL:      ~7GB (avatar generation)"
Write-Host "    MuseTalk:  ~3GB (lip-sync)"
Write-Host ""
Print-Success "Setup complete!"
