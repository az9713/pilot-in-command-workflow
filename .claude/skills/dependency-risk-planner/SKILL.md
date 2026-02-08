---
name: dependency-risk-planner
description: Pre-flight dependency risk assessment for the planning phase. Use BEFORE writing code when choosing libraries, designing architecture, or setting up a new project. Prevents dependency hell, version conflicts, and abandoned-library traps. Especially critical for ML/AI projects with heavy dependencies.
argument-hint: "[library-name or project-description]"
---

# Dependency Risk Planner

Run this assessment BEFORE writing code. Every hour spent here saves days of
debugging downstream. This skill exists because we learned the hard way: a
dead library (Coqui TTS), a removed API (`torchaudio.info()`), and invisible
transitive dependencies cost weeks of debugging that proper planning would
have prevented entirely.

## When to Use This Skill

- Evaluating a library before adding it to the project
- Starting a new project and choosing its dependency stack
- Planning architecture around ML models or external services
- Designing a deployment strategy for multiple environments
- Reviewing an existing dependency stack for risk

## Protocol

### Phase 1: Dependency Health Audit

For EACH candidate library, research and answer these questions. Do not skip
any. A single "red" answer can mean weeks of wasted work later.

#### 1.1 Maintainer Viability

| Question | How to Check | Red Flag |
|----------|-------------|----------|
| Is the maintainer an individual or a company? | GitHub org page, about page | Company (can shut down overnight) |
| Is the company/person financially stable? | News, Crunchbase, layoff trackers | Recent layoffs, no funding, pivoting |
| When was the last release? | PyPI/npm release dates | >6 months ago |
| When was the last commit to main? | GitHub commits tab | >3 months ago |
| Are issues being responded to? | GitHub issues, response time | Rising open count, no maintainer replies |
| Is there a clear successor if this dies? | README, community forks | No alternative exists |

**Action**: If any red flag fires, immediately research alternatives. Document
the risk and the fallback plan BEFORE proceeding.

**Real example**: Coqui AI shut down in 2024. Their TTS library was the best
open-source voice cloning solution. After shutdown: no releases, stale
dependency pins, no Python 3.12 support. The entire installation process
broke and required a `--no-deps` workaround with manually-managed transitive
dependencies. Had we assessed maintainer viability in the planning phase, we
would have either chosen an alternative or designed an abstraction layer from
day one.

#### 1.2 Dependency Tree Health

| Question | How to Check | Red Flag |
|----------|-------------|----------|
| Does it pin exact versions of transitive deps? | `pip show -v <pkg>`, setup.cfg/pyproject.toml | Exact pins (`==`) on transitive deps |
| Do its pins conflict with your other deps? | `pip install --dry-run` | Version conflicts |
| How many transitive deps does it pull in? | `pipdeptree -p <pkg>` | >20 transitive deps |
| Does it depend on C extensions that need compilation? | Install on clean env | Build failures on different platforms |
| Can you install it with `--no-deps` and provide deps yourself? | Try it | Import errors at runtime |

**Action**: Run `pip install <pkg> --dry-run` in a clean venv BEFORE committing
to the library. If it takes >2 minutes to resolve, that's a warning sign.

**Real example**: `pip install TTS` backtracks through 30+ dependency versions
for 10+ minutes and often fails entirely. The fix is `pip install TTS==0.22.0
--no-deps`, but this means you must manually discover and provide every
transitive dependency (numpy, scipy, soundfile, librosa, scikit-learn, einops,
unidecode, num2words, coqpit). Some of these only surface at runtime, not
at import time.

#### 1.3 Python/Runtime Compatibility

| Question | How to Check | Red Flag |
|----------|-------------|----------|
| What Python versions does it support? | pyproject.toml, setup.cfg, CI matrix | Missing latest Python version |
| Does it use deprecated stdlib modules? | Search for `distutils`, `imp`, `pipes` | Uses modules removed in Python 3.12+ |
| Does it work on your target OS? | CI matrix, issue tracker | Windows/macOS/Linux gaps |
| Does it work on your target hardware? | GPU/CPU tests, issue tracker | GPU-only with no CPU fallback |

**Action**: If the library caps Python version support, that cap becomes YOUR
project's cap. Document this constraint in `pyproject.toml` immediately:
```toml
requires-python = ">=3.10,<3.12"  # Capped by <library-name>
```

**Real example**: TTS 0.22.0 uses `distutils` (removed in Python 3.12, PEP 632).
This forced our entire project to cap at Python <3.12. Every developer and every
deployment environment must use Python 3.10 or 3.11. This constraint was
invisible until installation failed on Python 3.12.

#### 1.4 API Stability

| Question | How to Check | Red Flag |
|----------|-------------|----------|
| Is the API you need in the stable/public API docs? | Official docs, not just tutorials | Function only in examples, not API reference |
| Has this API changed in the last 2 major versions? | CHANGELOG, migration guides | Breaking changes without deprecation warnings |
| Are there open issues about the API you plan to use? | GitHub issues search | "Breaking change", "removed", "deprecated" |
| Does the library distinguish stable vs experimental APIs? | Docs, module naming | No stability guarantees anywhere |

**Action**: Only depend on APIs that appear in the library's official stable
API documentation. Utility functions, convenience wrappers, and "info" helpers
are the first to be removed.

**Real example**: `torchaudio.info()` was a convenience function for getting
audio metadata. It was removed in torchaudio 2.1+ without a direct replacement.
The successor `torchaudio.load()` changed its backend to require `torchcodec`,
which isn't auto-installed. The fix: use `soundfile.info()` instead (wraps
`libsndfile`, a C library stable for 20+ years). The lesson: framework utility
functions change with every major version; C library wrappers are stable for
decades.

### Phase 2: Architecture Decisions

Based on the audit results, make these architecture decisions BEFORE writing code.

#### 2.1 Wrapper Pattern for Fragile APIs

For every dependency that scored any red flags in Phase 1, create an
abstraction layer:

```
YOUR CODE ---> Your Wrapper Module ---> Fragile Library
```

**Design rule**: Your application code NEVER imports the fragile library
directly. All access goes through your wrapper. When the library breaks,
you fix ONE file.

Example structure:
```
src/utils/
  audio.py        # Wraps soundfile + torchaudio
  image.py        # Wraps Pillow + torchvision
  model_loader.py # Wraps library-specific model loading
```

Each wrapper function should:
- Have a clear docstring explaining WHY it wraps (not just WHAT)
- Note which underlying library it uses and why
- Be the ONLY place that library is imported

**Real example**: We used `torchaudio.info()` directly in two files
(`cloner.py` and `lipsync.py`). When torchaudio removed it, we had to find
and fix both call sites. A single `get_audio_duration()` wrapper would have
meant fixing one function.

#### 2.2 Import Strategy for Optional Heavy Dependencies

For libraries that are heavy (GPU frameworks, ML models), use LOCAL imports
inside functions, not module-level imports:

```python
# GOOD: Module loads without GPU libraries installed
def generate_speech(text):
    import torch  # Local import - only needed when this function runs
    from TTS.api import TTS
    ...

# BAD: Module fails to import if torch isn't installed
import torch  # Module-level - breaks CLI, config, tests
```

**Why this matters for testing**: If you use module-level imports,
`mocker.patch("mymodule.torch")` works. But if you use local imports
(which you should), you must mock at the `sys.modules` level:
```python
mocker.patch.dict("sys.modules", {"torch": mock_torch})
```

Document your import strategy in a project convention so every developer
and every test follows the same pattern.

#### 2.3 Transitive Dependency Inventory

If you plan to use `--no-deps` for any library (because its dependency tree
is broken), you MUST build a complete inventory of what it actually imports
at runtime.

**Method**:
1. Install the library with `--no-deps`
2. Run a comprehensive smoke test that exercises every code path you use
3. Record every `ModuleNotFoundError`
4. Add each missing package to your explicit dependency list
5. Repeat until no more import errors

**Do NOT rely on the library's `setup.cfg` or `pyproject.toml`** for this
list. Dead libraries often have wrong or incomplete dependency declarations.
Runtime testing is the only reliable method.

**Create a smoke test file** that verifies all transitive deps are importable:
```python
# tests/test_smoke_imports.py
"""Import smoke tests - no mocking, no GPU needed."""

def test_tts_deps():
    """Verify all TTS transitive dependencies are installed."""
    import coqpit
    import einops
    import librosa
    import num2words
    import numpy
    import scipy
    import soundfile
    import unidecode

def test_ml_framework():
    import torch
    import torchaudio
```

#### 2.4 Environment Compatibility Matrix

Plan your supported environments BEFORE writing code. Each environment
variation is a potential failure point.

| Dimension | Options | Document In |
|-----------|---------|-------------|
| Python version | 3.10, 3.11 (NOT 3.12+) | `pyproject.toml` requires-python |
| OS | Linux, macOS, Windows | CI matrix, install scripts |
| GPU | NVIDIA (CUDA), CPU-only | Config profiles, fallback code |
| Deployment | Local, RunPod, Docker | Install guide, Dockerfiles |
| venv tool | venv, conda | Install scripts |

**For each supported environment, plan**:
- An install script or Dockerfile
- A verification command (`avatar status`, `pytest --smoke`)
- Known gotchas documented in the install guide

**Real example**: RunPod pods ship with Python 3.12 as the system default.
We didn't plan for this, so the first RunPod deployment failed. The fix
(creating a Python 3.11 venv at `/workspace/venv311`) should have been in
the deployment plan from day one.

### Phase 3: Dependency Specification

Write these artifacts BEFORE writing application code.

#### 3.1 Pinning Strategy

Decide your pinning strategy per dependency category:

| Category | Strategy | Example |
|----------|----------|---------|
| Dead library (no maintainer) | Pin exact version forever | `TTS==0.22.0` |
| Active library, stable API | Pin major version | `torch>=2.0,<3.0` |
| Stable C wrapper | Float with minimum | `soundfile>=0.12` |
| Transitive dep (manual) | Float with minimum | `numpy>=1.24` |
| Dev/test tool | Float with minimum | `pytest>=7.4` |

**Never leave a dependency completely unpinned** (bare `numpy` is dangerous).

#### 3.2 Install Script Design

Write your install script BEFORE your application code. The install script
is the first thing a new developer runs. If it fails, they never get to
your code.

**Install script checklist**:
- [ ] Detects and validates Python version (refuses incompatible versions)
- [ ] Creates venv with `--clear` flag (prevents contamination)
- [ ] Verifies venv Python version after activation (catches inheritance bugs)
- [ ] Handles broken dependency trees (`--no-deps` workarounds)
- [ ] Installs project with `--no-deps` if needed
- [ ] Checks for system dependencies (FFmpeg, CUDA, etc.)
- [ ] Creates required directories
- [ ] Runs a quick verification (smoke test, not full test suite)
- [ ] Prints clear summary with next steps

**Every workaround in the script must have a comment explaining WHY**:
```bash
# Coqui AI shut down in 2024. Their TTS package has stale dependency
# pins that cause pip to backtrack for 10+ minutes. --no-deps skips
# the broken dependency tree. See docs/LESSONS_LEARNED.md.
pip install TTS==0.22.0 --no-deps
```

#### 3.3 Documentation Artifacts

Create these documents BEFORE writing application code:

1. **INSTALLATION_GUIDE.md**: Step-by-step with known gotchas
2. **Known Issues table**: At the top of the install guide, not buried at the bottom
3. **requirements.txt header**: TL;DR install recipe + warnings
4. **LESSONS_LEARNED.md**: Living document, updated as new issues surface

### Phase 4: Test Planning for Dependencies

Plan your test strategy to catch dependency issues that unit tests with
mocking will miss.

#### 4.1 Three Test Layers

| Layer | What It Tests | Mocking? | When to Run |
|-------|--------------|----------|-------------|
| Smoke imports | All packages importable | None | After every `pip install` |
| Unit tests | Business logic | Full mocking | Every commit |
| Integration tests | Real library calls | Minimal | Before release, on CI with GPU |

**The critical gap**: Unit tests with full mocking pass even when
dependencies are completely broken. The smoke import tests fill this gap
without needing GPU or models.

#### 4.2 Mock Pattern Documentation

If your codebase uses local imports (which it should for heavy deps),
document the correct mock pattern so every test author uses it:

```python
# CORRECT: Mock at sys.modules level for local imports
mocker.patch.dict("sys.modules", {"torch": mock_torch})

# WRONG: Fails with AttributeError when import is inside a function
mocker.patch("src.mymodule.torch", mock_torch)

# CORRECT: Simulate "library not installed"
mocker.patch.dict("sys.modules", {"torch": None})

# WRONG: Doesn't trigger ImportError for local imports
mocker.patch("src.mymodule.torch", side_effect=ImportError)
```

#### 4.3 Dataclass/Interface Stability

If your interfaces use dataclasses, plan for field additions:

```python
# Fragile: Adding a new required field breaks all existing call sites
@dataclass
class Result:
    success: bool
    data: dict
    error: str        # Adding this breaks every Result() call

# Resilient: New fields have defaults, existing code keeps working
@dataclass
class Result:
    success: bool
    data: dict
    error: Optional[str] = None  # Safe to add later
```

**Rule**: Every field that might be added later should have a default value.
Required fields should only be things that are truly required from day one.

## Output

After completing this assessment, produce:

1. **Risk Summary Table**: Each dependency with health score (green/yellow/red)
2. **Architecture Decisions**: Wrapper modules needed, import strategy, pinning strategy
3. **Action Items**: Ordered list of what to create before writing application code
4. **Dependency Specification Files**: requirements.txt, pyproject.toml with pins and comments

## Additional Resources

For detailed case studies of every issue this skill prevents, see:
- [LESSONS_LEARNED.md](../../../docs/avatar-pipeline/LESSONS_LEARNED.md)
- [INSTALLATION_GUIDE.md](../../../docs/avatar-pipeline/INSTALLATION_GUIDE.md)
