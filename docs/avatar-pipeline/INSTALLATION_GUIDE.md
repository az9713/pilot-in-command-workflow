# Installation Guide

This guide covers every known installation pitfall. Read the warnings before
running any commands.

## Known Issues at a Glance

| Issue | Impact | Workaround |
|-------|--------|------------|
| Coqui TTS requires Python <3.12 | `pip install TTS` fails on Python 3.12+ | Use Python 3.10 or 3.11 |
| TTS has stale dependency pins | pip backtrack for 10+ min, often fails | Install TTS with `--no-deps` |
| Venv can inherit system packages | Wrong Python version leaks into venv | Always use `--clear` flag |
| RunPod default Python is 3.12 | TTS will not install | Create Python 3.11 venv |

---

## Option A: Automated Install (Recommended)

The install scripts handle all the workarounds automatically.

**Linux / macOS / RunPod:**
```bash
cd avatar-pipeline
bash scripts/install.sh
```

**Windows PowerShell:**
```powershell
cd avatar-pipeline
.\scripts\install.ps1
```

The scripts will:
1. Find Python 3.10 or 3.11 (refuse 3.12+)
2. Create a clean venv with `--clear`
3. Install TTS with the `--no-deps` workaround
4. Install all other dependencies
5. Run GPU and FFmpeg checks

---

## Option B: Manual Install (Step by Step)

### Step 1: Verify Python Version

**You MUST use Python 3.10 or 3.11.** Python 3.12+ will not work.

```bash
python3 --version
# Must show 3.10.x or 3.11.x
```

If you have 3.12+, install 3.11:
```bash
# Ubuntu/Debian
sudo apt install python3.11 python3.11-venv python3.11-dev

# macOS
brew install python@3.11

# Windows - download from python.org
```

### Step 2: Create Virtual Environment

**Always use the `--clear` flag** to avoid inheriting system packages:

```bash
python3.11 -m venv venv --clear
source venv/bin/activate    # Linux/macOS
# .\venv\Scripts\Activate.ps1  # Windows
```

After activating, verify:
```bash
python --version
# Must show 3.10.x or 3.11.x - NOT 3.12
```

**Gotcha:** If your system Python is 3.12 and you run `python3 -m venv venv`
without specifying `python3.11`, the venv may use Python 3.12.
Always use the explicit `python3.11` command.

### Step 3: Upgrade pip

```bash
pip install --upgrade pip wheel setuptools
```

### Step 4: Install TTS (with --no-deps workaround)

**Do NOT run `pip install TTS` directly.** It will backtrack for 10+ minutes
and likely fail because Coqui AI shut down in 2024 and their package has
stale, overly strict dependency pins.

Instead:

```bash
pip install TTS==0.22.0 --no-deps
```

This installs the TTS package without pulling in its broken dependency tree.

### Step 5: Install All Other Dependencies

```bash
# PyTorch (installs CUDA version automatically if GPU available)
pip install torch torchaudio

# ML libraries, computer vision, API, utilities, and TTS transitive deps
pip install \
    diffusers transformers accelerate \
    mediapipe opencv-python Pillow \
    fastapi "uvicorn[standard]" click \
    pyyaml pydantic python-multipart \
    numpy scipy soundfile librosa scikit-learn \
    einops unidecode num2words
```

### Step 6: Install the Project

```bash
pip install -e . --no-deps
```

**Note the `--no-deps`** - this prevents pip from trying to resolve TTS's
dependency tree again during the editable install.

### Step 7: Install Test Dependencies

```bash
pip install pytest pytest-mock pytest-asyncio pytest-cov httpx
```

### Step 8: Verify

```bash
# Check GPU detection
avatar status

# Run tests (all 135 should pass)
pytest tests/ -v
```

---

## RunPod Setup

RunPod pods typically come with Python 3.12 and PyTorch pre-installed.
Since TTS requires Python <3.12, you need a separate Python 3.11 venv.

### Step 1: Start a Pod

- Template: **RunPod Pytorch** (or any CUDA template)
- GPU: RTX 3080 or better (10GB+ VRAM)
- Disk: 50GB+ (for models)

### Step 2: Get the Code onto the Pod

**Option A: Git clone** (if repo is public)
```bash
cd /workspace
git clone <repo-url>
cd avatar-pipeline
```

**Option B: Upload via Jupyter Lab** (if repo is private)
1. On your local machine, zip the project:
   ```bash
   # Linux/macOS
   zip -r avatar-pipeline.zip avatar-pipeline/

   # Windows PowerShell
   Compress-Archive -Path avatar-pipeline -DestinationPath avatar-pipeline.zip
   ```
2. Open Jupyter Lab from RunPod dashboard (click "Connect" > "Jupyter Lab")
3. Upload the zip file to `/workspace`
4. In Jupyter terminal:
   ```bash
   cd /workspace
   unzip avatar-pipeline.zip
   ```

**Option C: SSH/SCP** (if SSH key is configured)
- SSH keys must be set in RunPod Settings **before** creating the pod
- If the pod was created before the key was added, restart the pod
- Connection: `ssh root@<IP> -p <PORT> -i ~/.ssh/id_ed25519`

### Step 3: Install Python 3.11

RunPod Ubuntu images usually have `python3.11` available or installable:

```bash
# Check if already available
python3.11 --version

# If not, install it
apt update && apt install -y python3.11 python3.11-venv python3.11-dev
```

### Step 4: Create Venv and Install

```bash
cd /workspace/avatar-pipeline

# Create Python 3.11 venv (NOT in project dir to avoid git noise)
python3.11 -m venv /workspace/venv311 --clear
source /workspace/venv311/bin/activate

# Verify
python --version  # Must show 3.11.x

# Run the install steps (Steps 3-7 from Manual Install above)
pip install --upgrade pip wheel setuptools
pip install TTS==0.22.0 --no-deps
pip install torch torchaudio
pip install \
    diffusers transformers accelerate \
    mediapipe opencv-python Pillow \
    fastapi "uvicorn[standard]" click \
    pyyaml pydantic python-multipart \
    numpy scipy soundfile librosa scikit-learn \
    einops unidecode num2words
pip install -e . --no-deps
pip install pytest pytest-mock pytest-asyncio pytest-cov httpx
```

### Step 5: Test

```bash
pytest tests/ -v
# Expected: 135 passed
```

### RunPod Tips

- **Venv location:** Put the venv at `/workspace/venv311` (not inside the project).
  The `/workspace` directory persists across pod restarts.
- **Activate on reconnect:** `source /workspace/venv311/bin/activate`
- **GPU check:** `nvidia-smi` to see GPU utilization
- **Pod costs:** Stop the pod when not in use (you only pay for disk when stopped)

---

## Troubleshooting

### "No module named TTS" after install

You probably ran `pip install -e .` without `--no-deps`, which triggered pip to
uninstall TTS during dependency resolution. Fix:

```bash
pip install TTS==0.22.0 --no-deps
pip install -e . --no-deps
```

### pip backtracking for 10+ minutes

You're installing TTS without `--no-deps`. Cancel with Ctrl+C and use:

```bash
pip install TTS==0.22.0 --no-deps
```

### "Python version 3.12 not supported"

TTS requires Python <3.12. Create a 3.11 venv:

```bash
python3.11 -m venv venv --clear
source venv/bin/activate
```

### Venv has wrong Python version

This happens when the venv inherits the system Python. Signs:
- `python --version` in the venv shows 3.12 even though you used `python3.11`
- Packages from the system appear in `pip list`

Fix: Recreate with `--clear`:

```bash
rm -rf venv
python3.11 -m venv venv --clear
source venv/bin/activate
```

### opencv-contrib-python build fails

This can happen when building from source on some platforms. It's safe to
ignore - we only need `opencv-python` (not `contrib`). If you see this error
during TTS install, it's another reason to use `--no-deps`.

### Tests fail with "does not have the attribute 'torch'"

This was a test bug (fixed in current version). The tests were trying to mock
`torch` as a module-level attribute, but the source code imports torch locally
inside functions. If you see this, make sure your test files are up to date.

### Tests fail with "cannot import name 'VoiceCloneResult'"

This was a test bug (fixed in current version). The actual class names are:
- `CloneResult` (not `VoiceCloneResult`) in `src/voice/interfaces.py`
- `GenerationResult` (not `AvatarGenerationResult`) in `src/avatar/interfaces.py`

Make sure your test files are up to date.

---

## Why Is Installation So Complicated?

**Coqui AI shut down in 2024.** Their TTS library was the best open-source
voice cloning solution, but after the company closed:

1. **No more releases** - TTS 0.22.0 is the last version
2. **Stale dependency pins** - The package pins exact versions of dozens of
   transitive dependencies, many of which conflict with modern Python
3. **No Python 3.12 support** - The code uses features removed in 3.12
4. **pip can't resolve** - The dependency tree is so tangled that pip
   backtracks through 30+ versions before giving up

The `--no-deps` workaround sidesteps all of this by installing TTS as a
standalone package and providing its runtime dependencies ourselves. This is
stable and tested.

**Future plan:** Replace Coqui TTS with an actively maintained alternative
(e.g., Bark, StyleTTS2, or a HuggingFace-hosted model). This is tracked
in the project roadmap.
