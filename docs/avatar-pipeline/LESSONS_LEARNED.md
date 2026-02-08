# Lessons Learned: Dependency Hell, Deprecated Modules & Version Conflicts

This document captures every painful lesson from building, installing, and running
the Avatar Pipeline. It exists so that **nobody has to repeat this debugging**.

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Issue Catalog](#issue-catalog)
   - [Coqui TTS Shutdown](#1-coqui-tts-shutdown-critical)
   - [torchaudio API Breakage](#2-torchaudio-api-breakage-high)
   - [Python Version Ceiling](#3-python-version-ceiling-critical)
   - [Virtual Environment Contamination](#4-virtual-environment-contamination-medium)
   - [Missing Transitive Dependencies](#5-missing-transitive-dependencies-high)
   - [Test Mocking vs Local Imports](#6-test-mocking-vs-local-imports-medium)
   - [Dataclass Field Drift](#7-dataclass-field-drift-in-tests-medium)
   - [RunPod Environment Mismatch](#8-runpod-environment-mismatch-medium)
3. [Root Cause Analysis](#root-cause-analysis)
4. [Prevention Strategies](#prevention-strategies)
5. [Decision Record: Why We Made These Choices](#decision-record)
6. [Future Risk Register](#future-risk-register)

---

## The Big Picture

This project depends on **four large ML models** from different organizations:

| Model | Provider | Status | Risk Level |
|-------|----------|--------|------------|
| XTTS-v2 (voice cloning) | Coqui AI | **Shut down (2024)** | Critical |
| Coqui TTS (synthesis) | Coqui AI | **Shut down (2024)** | Critical |
| Stable Diffusion XL | Stability AI | Active but pivoting | Medium |
| MuseTalk (lip-sync) | TMElyra Lab | Active, not on PyPI | Medium |

**Core problem**: When a dependency's maintainer disappears, the package becomes
a ticking time bomb. It still works today, but every upstream change (Python
releases, PyTorch updates, OS updates) creates new incompatibilities that nobody
will fix.

**Our approach**: Isolate the fragile dependency (`TTS==0.22.0`) with `--no-deps`,
pin what we can, and document everything we can't pin.

---

## Issue Catalog

### 1. Coqui TTS Shutdown (CRITICAL)

**What happened**: Coqui AI, the company behind the best open-source voice
cloning library (XTTS-v2), shut down in 2024. TTS 0.22.0 is the last release.

**Symptoms**:
- `pip install TTS` backtracks through 30+ dependency versions for 10+ minutes
- Often fails entirely with unresolvable version conflicts
- `pip install -e .` triggers the same backtracking via TTS in the dep tree
- Python 3.12+ installation fails outright (uses `distutils`, removed in 3.12)

**Root cause**: TTS 0.22.0 pins exact versions of dozens of transitive
dependencies (e.g., `numpy==1.22.0`, `scipy==1.9.3`). These pins conflict with
modern versions of PyTorch, transformers, and other libraries.

**Fix applied**:
```bash
# Install TTS without its dependency tree
pip install TTS==0.22.0 --no-deps

# Provide transitive dependencies ourselves (compatible versions)
pip install numpy scipy soundfile librosa scikit-learn einops unidecode num2words coqpit

# Install our project without re-triggering TTS resolution
pip install -e . --no-deps
```

**Files affected**:
- `pyproject.toml` (lines 40-43): Warning comment + `--no-deps` instructions
- `requirements.txt` (lines 1-24): Header with TL;DR install recipe
- `scripts/install.sh` (lines 112-134): Automated workaround
- `scripts/install.ps1` (lines 106-131): Windows equivalent
- `docs/avatar-pipeline/INSTALLATION_GUIDE.md`: Full explanation

**Lesson**: When depending on a library from a startup, have a migration plan.
Track the company's health (funding rounds, layoffs, open-source activity).
When signs of decline appear, start evaluating alternatives *before* the shutdown.

---

### 2. torchaudio API Breakage (HIGH)

**What happened**: `torchaudio.info()` was removed in newer torchaudio versions
(post-2.1). When we tried the alternative `torchaudio.load()`, it required a
new backend called `torchcodec` that isn't installed by default.

**Symptoms**:
```
AttributeError: module 'torchaudio' has no attribute 'info'
```
Then after attempting `torchaudio.load()`:
```
RuntimeError: TorchCodec is required for load_with_torchcodec
```

**Root cause**: PyTorch's audio library underwent a major backend refactor.
The old `sox`/`soundfile` backends were replaced with `torchcodec`. The
`torchaudio.info()` convenience function was removed without a direct
replacement in the new API.

**Fix applied**: Replaced all `torchaudio.info()` calls with `soundfile`:
```python
# Before (broken):
info = torchaudio.info(audio_path)
duration = info.num_frames / info.sample_rate

# After (stable):
import soundfile as sf
info = sf.info(str(audio_path))
return info.duration
```

**Files changed**:
- `src/voice/cloner.py` (`_get_audio_duration` method, ~line 277)
- `src/video/lipsync.py` (`_get_audio_duration` method, ~line 541)

**Why soundfile?**:
- `soundfile` wraps `libsndfile`, a C library that has been stable for 20+ years
- It provides `.duration` directly (no manual calculation)
- It's already a dependency (used by `librosa` and TTS itself)
- It doesn't depend on PyTorch's backend system

**Lesson**: Prefer libraries that wrap stable C libraries (`soundfile` wraps
`libsndfile`, `Pillow` wraps `libjpeg`/`libpng`) over framework-specific
utilities (`torchaudio.info`, `torchvision.io`). The framework utilities change
with every major version; the C wrappers have been stable for decades.

**Note**: We still use `torchaudio` for actual audio loading in the ML pipeline
(`_extract_audio_features`), where we need tensors on GPU. The `soundfile` fix
is only for metadata queries (duration, sample rate).

---

### 3. Python Version Ceiling (CRITICAL)

**What happened**: TTS 0.22.0 uses `distutils` and other features removed in
Python 3.12 (PEP 632). Installation fails on Python 3.12+.

**Symptoms**:
```
ModuleNotFoundError: No module named 'distutils'
```
Or various `SyntaxError`s from TTS internals.

**Fix applied**:
- `pyproject.toml`: `requires-python = ">=3.10,<3.12"`
- Install scripts auto-detect Python 3.10/3.11 and refuse 3.12+
- RunPod guide explicitly instructs creating a Python 3.11 venv

**Lesson**: Always test your project on the *newest* Python version before
depending on it. Pin `requires-python` upper bounds when you know a dependency
can't handle newer versions. This is controversial (some prefer no upper bound),
but a broken install is worse than a conservative pin.

**Future plan**: Replace Coqui TTS with an actively maintained alternative
(e.g., Bark, StyleTTS2, or a HuggingFace-hosted XTTS fork). This removes the
Python version ceiling.

---

### 4. Virtual Environment Contamination (MEDIUM)

**What happened**: On systems where the default Python is 3.12, running
`python3 -m venv venv` creates a venv that inherits the 3.12 interpreter.
Even if you then `pip install` Python 3.11 packages, the interpreter itself
is 3.12 and TTS fails.

**Symptoms**:
- `python --version` inside venv shows 3.12 despite expecting 3.11
- System packages leak into the venv
- TTS import fails with obscure errors

**Fix applied**:
```bash
# Always specify the exact Python version
python3.11 -m venv venv --clear

# The --clear flag removes any existing venv artifacts
# This prevents stale state from previous attempts
```

**Lesson**: Never use `python3 -m venv`. Always use the explicit version
(`python3.11 -m venv`). Always use `--clear`. Always verify after activation:
```bash
python --version  # Must show 3.11.x
```

---

### 5. Missing Transitive Dependencies (HIGH)

**What happened**: Because we install TTS with `--no-deps`, we must manually
provide every package that TTS imports at runtime. We discovered `coqpit` was
missing only when we ran the actual voice cloning code (tests mock everything,
so they don't trigger real imports).

**Symptoms**:
```
ModuleNotFoundError: No module named 'coqpit'
```

**Fix applied**: Added `coqpit` to all dependency lists (requirements.txt,
pyproject.toml, install.sh, install.ps1, INSTALLATION_GUIDE.md).

**Full list of TTS transitive deps we provide**:
```
numpy scipy soundfile librosa scikit-learn einops unidecode num2words coqpit
```

**How to find more missing deps**: Run the actual pipeline (not just tests).
Tests mock all external libraries, so they pass even with missing dependencies.
The runtime code path is the only reliable way to discover missing packages.

**Lesson**: When using `--no-deps`, you are taking on the responsibility of
dependency management yourself. You *will* miss packages. Plan for iterative
discovery: run real workloads, hit import errors, add the package, repeat.

**Prevention**: After installation, run a quick smoke test that exercises real
imports without needing GPU:
```python
python -c "
from TTS.api import TTS
from TTS.utils.manage import ModelManager
print('TTS imports OK')
"
```

---

### 6. Test Mocking vs Local Imports (MEDIUM)

**What happened**: 25 tests failed because of incorrect mock patching. The
source code uses *local imports* (`import torch` inside function bodies), but
the tests tried to mock torch as a *module-level attribute*:

```python
# Source code (src/utils/vram.py):
class VRAMManager:
    def __init__(self):
        import torch  # Local import inside method
        ...

# Test (BROKEN):
mocker.patch("src.utils.vram.torch", mock_torch)
# AttributeError: does not have the attribute 'torch'

# Test (FIXED):
mocker.patch.dict("sys.modules", {"torch": mock_torch})
```

**Why local imports?**: The codebase uses local imports so that the CLI and
config modules can load without GPU libraries installed. This is a valid
pattern for optional heavy dependencies.

**Fix applied**:
- All `mocker.patch("module.torch", ...)` → `mocker.patch.dict("sys.modules", {"torch": mock_torch})`
- For "no torch" tests: `mocker.patch.dict("sys.modules", {"torch": None})`
  (setting a module to `None` in `sys.modules` makes `import torch` raise `ImportError`)

**Files fixed**:
- `tests/test_utils/test_vram.py` (15 tests)
- `tests/test_config/test_hardware.py` (4 tests)
- `tests/test_cli.py` (6 tests)

**Lesson**: When code uses local/lazy imports, you must mock at the
`sys.modules` level, not the module attribute level. This is a common pitfall
with `pytest-mock`. Document the import pattern in a test README or conftest.

---

### 7. Dataclass Field Drift in Tests (MEDIUM)

**What happened**: Tests referenced wrong class names and were missing required
constructor arguments for dataclasses:

| Test Used | Actual Class | Issue |
|-----------|-------------|-------|
| `VoiceCloneResult` | `CloneResult` | Wrong name |
| `AvatarGenerationResult` | `GenerationResult` | Wrong name |
| `FaceDetectionResult(...)` | Same | Missing `landmarks`, `error` fields |
| `LipSyncResult(...)` | Same | Missing `error` field |
| `PipelineResult(...)` | Same | Missing `job_id`, `error` fields |

**Root cause**: The interface dataclasses were updated during implementation
(fields added, classes renamed), but the tests weren't updated to match.

**Fix applied**: Updated all test files to use correct names and provide all
required fields.

**Lesson**: Dataclasses without default values will fail loudly if you add a
new required field. This is actually a *feature* - it forces you to update all
call sites. But it means tests must be updated whenever the interface changes.

**Prevention**: Consider giving new fields default values (`error: Optional[str] = None`)
to avoid breaking existing code. Or use a conftest fixture that creates valid
instances, so there's only one place to update.

---

### 8. RunPod Environment Mismatch (MEDIUM)

**What happened**: RunPod pods ship with Python 3.12 as the system default and
PyTorch pre-installed at system level. This conflicts with our Python <3.12
requirement.

**Symptoms**:
- System Python is 3.12
- Pre-installed PyTorch is for Python 3.12
- TTS refuses to install

**Fix applied**:
```bash
# Install Python 3.11 alongside the system Python
apt install python3.11 python3.11-venv python3.11-dev

# Create isolated venv (NOT inside the project directory)
python3.11 -m venv /workspace/venv311 --clear

# Activate and install everything fresh
source /workspace/venv311/bin/activate
```

**Key RunPod tips**:
- Put the venv at `/workspace/venv311` (persists across pod restarts)
- Never rely on the system Python or pre-installed packages
- Re-activate on every reconnect: `source /workspace/venv311/bin/activate`
- First model download takes ~12GB; use a pod with 50GB+ disk

**Lesson**: Cloud GPU environments optimize for the latest Python and CUDA.
If your project needs an older Python, you must create a completely isolated
environment. Never assume the system packages are compatible.

---

## Root Cause Analysis

All eight issues share common root causes:

### 1. Dependency on Defunct Maintainers

**Pattern**: Project depends on library → Company shuts down → Library stops
receiving updates → Incompatibilities accumulate → Installation breaks.

**Affected**: Coqui TTS (issues 1, 3, 5)

**Signal to watch**: GitHub activity drops to zero, company blog goes silent,
employees leave. When you see these signs, start evaluating alternatives.

### 2. Implicit API Contracts

**Pattern**: Code uses an API → Library authors consider it internal/unstable
→ API changes without deprecation warnings → Code breaks silently.

**Affected**: `torchaudio.info()` removal (issue 2)

**Signal to watch**: Functions not in the library's "stable API" docs,
functions that don't appear in the official tutorials, functions marked
with `_` prefix or `# experimental` comments.

### 3. Testing with Mocks Hides Real Failures

**Pattern**: Tests mock everything → Tests pass → Real execution fails because
actual imports/dependencies are broken.

**Affected**: Missing `coqpit` (issue 5), torchaudio breakage (issue 2)

**Signal to watch**: 100% test pass rate with 0% integration testing. If every
external dependency is mocked, you're testing your mocks, not your code.

### 4. Environment Assumptions

**Pattern**: Code assumes specific Python version / OS / GPU → Deployed to
different environment → Breaks.

**Affected**: Python 3.12 on RunPod (issues 3, 4, 8)

**Signal to watch**: Hard-coded paths, unchecked `python3` vs `python3.11`,
reliance on pre-installed system packages.

---

## Prevention Strategies

### Strategy 1: Dependency Health Monitoring

**Before depending on a library, check:**
- [ ] Is the maintainer a company or individual? (Companies can shut down)
- [ ] When was the last release? (>6 months is a warning sign)
- [ ] How many open issues/PRs? (Rising count with no response = abandoned)
- [ ] Is there a clear successor if this library dies?
- [ ] Can we vendor (copy) the minimal code we need instead of depending on the whole library?

**Ongoing:**
- Set up a quarterly dependency review
- Track GitHub stars/activity trends
- Subscribe to library announcement channels

### Strategy 2: Integration Smoke Tests

Add a CI step that imports real libraries without mocking:

```python
# tests/test_smoke_imports.py
"""Smoke tests that verify real imports work (no mocking)."""

import pytest

def test_tts_imports():
    """Verify TTS and its transitive deps are importable."""
    from TTS.api import TTS
    from TTS.utils.manage import ModelManager

def test_torch_imports():
    """Verify PyTorch is importable."""
    import torch
    import torchaudio

def test_soundfile_imports():
    """Verify audio processing deps are importable."""
    import soundfile
    import librosa

def test_cv_imports():
    """Verify computer vision deps are importable."""
    import cv2
    from PIL import Image
    import mediapipe
```

These tests don't need GPU - they just verify that all packages are installed
and importable. Run them after every `pip install`.

### Strategy 3: Pin Aggressively, Update Deliberately

```toml
# pyproject.toml - Pin known-good versions
dependencies = [
    "TTS==0.22.0",           # DEAD - must pin forever
    "torch>=2.0,<3.0",       # Pin major version
    "torchaudio>=2.0,<3.0",  # Pin major version
    "soundfile>=0.12",       # Stable C wrapper, safe to float
]
```

**Rules:**
- Dead libraries: Pin exact version forever
- Active libraries with stable APIs: Pin major version
- Stable C wrappers: Float with minimum version
- Never leave a dependency unpinned (`numpy` alone is dangerous)

### Strategy 4: Wrapper Pattern for Fragile APIs

Wrap unstable APIs behind your own interface:

```python
# src/utils/audio.py
"""Audio utility functions that abstract over backend changes."""

def get_audio_duration(audio_path: Path) -> float:
    """Get audio duration in seconds. Uses soundfile (stable C wrapper)."""
    import soundfile as sf
    info = sf.info(str(audio_path))
    return info.duration

def load_audio_tensor(audio_path: Path, target_sr: int = 16000) -> torch.Tensor:
    """Load audio as a tensor. Handles resampling."""
    import torchaudio
    waveform, sr = torchaudio.load(audio_path)
    if sr != target_sr:
        waveform = torchaudio.transforms.Resample(sr, target_sr)(waveform)
    return waveform
```

When `torchaudio` breaks again, you fix one file instead of hunting through
the entire codebase.

### Strategy 5: Document the "Why" Not Just the "What"

Every workaround should explain why it exists:

```bash
# BAD: what (no context)
pip install TTS==0.22.0 --no-deps

# GOOD: why (future maintainers understand the constraint)
# Coqui AI shut down in 2024. TTS 0.22.0 is the last release.
# Its dependency pins conflict with modern PyTorch. --no-deps
# skips TTS's broken dependency tree; we provide the actual
# needed packages ourselves. See LESSONS_LEARNED.md #1.
pip install TTS==0.22.0 --no-deps
```

### Strategy 6: Test Matrix for Environment Variations

If you support multiple environments, test all of them:

| Environment | Python | PyTorch | GPU | Status |
|-------------|--------|---------|-----|--------|
| Local dev (Windows) | 3.11 | 2.x | Optional | Tested |
| Local dev (macOS) | 3.11 | 2.x | None | Untested |
| RunPod (Linux) | 3.11 venv | 2.x | RTX 3080+ | Tested |
| Docker | 3.11 | 2.x | NVIDIA runtime | Planned |

---

## Decision Record

### DEC-001: Use `--no-deps` for TTS

**Decision**: Install TTS with `--no-deps` and manually manage transitive dependencies.

**Alternatives considered**:
1. **Pin all TTS deps to exact versions**: Would work but creates conflicts with
   other libraries (especially PyTorch, numpy)
2. **Fork TTS and update deps**: Too much maintenance burden for our team size
3. **Replace TTS entirely**: Desirable long-term but no drop-in replacement exists
   today with equivalent quality
4. **Use Docker with frozen environment**: Would work but adds deployment complexity

**Why this choice**: Least invasive, works reliably, easy to understand and maintain.

### DEC-002: Use soundfile Instead of torchaudio for Audio Metadata

**Decision**: Use `soundfile.info()` for duration/metadata queries; keep
`torchaudio` only for tensor operations.

**Alternatives considered**:
1. **Install torchcodec backend**: Adds another dependency, may break again
2. **Pin torchaudio to older version**: Conflicts with PyTorch version
3. **Use librosa.get_duration()**: Works but slower (loads entire file)

**Why this choice**: `soundfile` wraps `libsndfile` (stable for 20+ years),
is already in our dep tree, and provides `.duration` directly.

### DEC-003: Cap Python at <3.12

**Decision**: Set `requires-python = ">=3.10,<3.12"` in pyproject.toml.

**Alternatives considered**:
1. **No upper bound**: Users on 3.12+ would get cryptic errors
2. **Support 3.12+ without TTS**: Would require removing voice cloning feature

**Why this choice**: Explicit is better than implicit. Users see the constraint
immediately rather than debugging for hours.

---

## Future Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PyTorch drops Python 3.11 support | Medium (2-3 years) | Critical | Monitor PyTorch release notes; accelerate TTS replacement |
| SDXL model removed from HuggingFace | Low | High | Cache model locally; evaluate SDXL alternatives |
| MuseTalk repo archived | Medium | High | Vendor critical code; evaluate SadTalker/Wav2Lip |
| `soundfile` breaks (unlikely) | Very Low | Medium | `libsndfile` has been stable 20+ years |
| RunPod drops Python 3.11 | Medium (1-2 years) | Medium | Use Docker image with pinned Python |
| New critical TTS transitive dep discovered | Medium | Low | Add to dep list, run smoke tests |

### Replacement Candidates for Coqui TTS

When the time comes to replace TTS, evaluate these:

| Library | Voice Cloning | Quality | Python 3.12+ | Active |
|---------|--------------|---------|--------------|--------|
| [Bark](https://github.com/suno-ai/bark) | Yes | Good | Yes | Yes |
| [StyleTTS2](https://github.com/yl4579/StyleTTS2) | Yes | Excellent | Yes | Yes |
| [WhisperSpeech](https://github.com/collabora/WhisperSpeech) | Limited | Good | Yes | Yes |
| [OpenVoice](https://github.com/myshell-ai/OpenVoice) | Yes | Good | Yes | Yes |
| XTTS (community fork) | Yes | Same | TBD | TBD |

---

## Appendix: Complete Dependency Conflict Map

```
TTS==0.22.0 (DEAD - Coqui AI shutdown 2024)
├── Requires: Python <3.12 (uses distutils, removed in 3.12)
├── Pins: numpy==1.22.0 (conflicts with PyTorch 2.x which needs numpy>=1.24)
├── Pins: scipy==1.9.3 (conflicts with scikit-learn>=1.3 which needs scipy>=1.5)
├── Pins: librosa==0.9.2 (conflicts with soundfile>=0.12)
├── Needs at runtime (not declared properly):
│   ├── coqpit (config dataclass library)
│   ├── unidecode (text normalization)
│   ├── num2words (number to text conversion)
│   └── einops (tensor operations)
└── Our workaround: --no-deps + manual dep list

torchaudio>=2.1 (API BREAKING CHANGE)
├── Removed: torchaudio.info() (metadata query)
├── Changed: torchaudio.load() backend (sox → torchcodec)
├── New requirement: torchcodec package (not auto-installed)
└── Our workaround: soundfile.info() for metadata, keep torchaudio for tensors
```

---

*Last updated: 2026-02-07*
*Authored through painful experience across 5+ debugging sessions.*
