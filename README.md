# Nemotron PIC + Avatar Pipeline

This repository contains **two projects** that tell a single story:

1. **PIC Agentic Organizational System** - A workflow framework that coordinates
   AI agents through structured phases, inspired by NVIDIA's Nemotron project
   management model.

2. **Avatar Lipsync Pipeline** - An AI video generation system built *using* the
   PIC framework. Takes text + reference audio and produces lip-synced talking
   head videos with cloned voices.

The PIC system was the builder. The avatar pipeline was the product. Both live
in this repo as a case study of agentic software development.

---

## The Story

### What Worked: PIC Built a Real Product

The PIC workflow took a vague problem statement ("build an open-source avatar
video pipeline") and systematically decomposed it across six phases:

```
Research ─── Found XTTS-v2, Coqui TTS, SDXL, MuseTalk as model stack
    │
Planning ── Created 7-week plan with 6 milestones and 41 tasks
    │
Design ──── Architected 4-layer system with sequential VRAM loading
    │
Implementation ── Built 6 modules, 3,400+ lines of production code
    │
Testing ─── 135 tests, all passing (after fixing 25 mock-pattern bugs)
    │
Review ──── Polish pass: 6 examples, 4 config profiles, install scripts
```

**The PIC system successfully produced**:
- A complete CLI (`avatar voice clone`, `avatar pipeline run`, etc.)
- A REST API with 17 endpoints
- Hardware-aware config for 3 GPU tiers (RTX 4090, 3080, low VRAM)
- Sequential model loading that fits 5 large models into 10GB VRAM
- Automated install scripts for Linux, macOS, Windows, and RunPod
- Comprehensive documentation and working examples

### What Failed: The Pipeline Never Ran End-to-End

Despite producing well-structured, well-tested code, the avatar pipeline
was never successfully run end-to-end to generate a video. The failures
were all at the **dependency and environment layer**, not in the application
code itself:

| Failure | Root Cause | Phase Where It Should Have Been Caught |
|---------|-----------|---------------------------------------|
| `pip install TTS` hangs for 10+ min | Coqui AI shut down in 2024; stale dependency pins | **Research** (library health check) |
| Python 3.12 incompatible | TTS uses `distutils`, removed in 3.12 | **Research** (compatibility check) |
| `torchaudio.info()` removed | PyTorch API breaking change in 2.1+ | **Design** (API stability audit) |
| `torchaudio.load()` needs `torchcodec` | Backend refactor, undocumented requirement | **Design** (API stability audit) |
| `No module named 'coqpit'` | Missing transitive dep (TTS installed with `--no-deps`) | **Testing** (smoke tests, not just mocked unit tests) |
| 25 test failures on RunPod | Tests used wrong mock patterns for local imports | **Testing** (run tests in target environment) |
| RunPod has Python 3.12 default | Environment assumption not validated | **Planning** (environment matrix) |

**Key insight**: Every failure traced back to a planning-phase gap. The code
was correct. The dependency assumptions were wrong. This is the most common
failure mode in ML/AI projects, and it's entirely preventable.

### What We Learned

The painful debugging sessions produced three durable artifacts:

1. **[LESSONS_LEARNED.md](docs/avatar-pipeline/LESSONS_LEARNED.md)** -
   8 categorized issues, root cause analysis, prevention strategies

2. **[`/dependency-risk-planner`](.claude/skills/dependency-risk-planner/SKILL.md)** -
   A Claude Code skill that runs a pre-flight dependency health audit
   during the planning phase, before any code is written

3. **[INSTALLATION_GUIDE.md](docs/avatar-pipeline/INSTALLATION_GUIDE.md)** -
   Every workaround documented, with the "why" not just the "what"

---

## Project Map

```
nemotron_PIC_lambert/
│
├── PIC WORKFLOW SYSTEM (the builder)
│   ├── CLAUDE.md                  # System overview + commands
│   ├── .claude/
│   │   ├── skills/                # /pic-start, /pic-status, /pic-decide, etc.
│   │   │   └── dependency-risk-planner/  # Lesson-learned skill
│   │   ├── agents/                # PIC agent configurations
│   │   ├── rules/                 # Coordination, decisions, conflicts
│   │   └── hooks/                 # Event handlers + audit logging
│   ├── .pic/                      # Runtime state
│   │   ├── state.json             # Current workflow
│   │   ├── handoffs/              # Phase transition records
│   │   ├── decisions/             # Formal decision documents
│   │   └── status-log.jsonl       # Activity log
│   ├── docs/
│   │   ├── QUICK_START.md         # PIC quick start
│   │   ├── USER_GUIDE.md          # PIC user guide
│   │   ├── DEVELOPER_GUIDE.md     # PIC dev guide
│   │   ├── ARCHITECTURE.md        # PIC architecture
│   │   └── TROUBLESHOOTING.md     # PIC troubleshooting
│   └── scripts/
│       └── pic-init.sh            # Initialize PIC system
│
├── AVATAR PIPELINE (the product)
│   ├── src/                       # Application code
│   │   ├── cli.py                 # CLI interface (Click)
│   │   ├── config/                # Hardware detection, settings
│   │   ├── voice/                 # XTTS-v2 cloning, Coqui TTS
│   │   ├── avatar/                # SDXL generation, MediaPipe
│   │   ├── video/                 # MuseTalk lip-sync, FFmpeg
│   │   ├── orchestration/         # Pipeline coordinator, job queue
│   │   ├── api/                   # FastAPI REST API
│   │   └── utils/                 # VRAM management
│   ├── tests/                     # 135 tests (all passing)
│   ├── examples/                  # 6 working example scripts
│   ├── config/                    # Hardware profile templates
│   ├── docs/avatar-pipeline/      # Avatar-specific docs
│   │   ├── README.md              # Avatar pipeline docs
│   │   ├── INSTALLATION_GUIDE.md  # Install guide (read this!)
│   │   ├── LESSONS_LEARNED.md     # Dependency hell postmortem
│   │   └── CHANGELOG.md           # Version history
│   ├── scripts/
│   │   ├── install.sh             # Linux/macOS installer
│   │   └── install.ps1            # Windows installer
│   ├── pyproject.toml             # Python packaging
│   └── requirements.txt           # Dependencies
│
└── SHARED CONTEXT
    └── .ignore/                   # Working files, transcripts, test assets
```

---

## Successes

### PIC System
- Took a vague problem and produced structured, documented output
- Clear handoff documents show the reasoning at each phase transition
- Decision records capture why choices were made (not just what)
- The sequential phase model prevented scope creep and kept focus
- Successfully coordinated research, design, and implementation

### Avatar Pipeline (Code Quality)
- Clean architecture: 4-layer separation, interface-based modules
- Smart VRAM management: sequential loading fits 5 models in 10GB
- Complete CLI and REST API with proper error handling
- 135 tests covering config, VRAM, CLI, API, voice, orchestration
- Multi-platform support: Linux, macOS, Windows, RunPod

### Documentation & Learning
- Every painful lesson was captured and distilled into reusable artifacts
- The `/dependency-risk-planner` skill prevents future projects from
  repeating the same mistakes
- Installation guides document the "why" behind every workaround

## Failures

### Dependency Management (Critical)
- **Coqui TTS dependency was a ticking time bomb** - the company shut down
  in 2024, but we chose it anyway without assessing maintainer viability
- **`--no-deps` workaround is fragile** - we're manually managing transitive
  dependencies that could break with any update
- **Python version ceiling** (`<3.12`) limits the project's future
- **torchaudio API instability** caused runtime failures that tests didn't catch

### Testing Gap
- **100% mocked tests gave false confidence** - all 135 tests passed even
  when actual dependencies were broken or missing
- **No smoke import tests** - would have caught `coqpit`, `soundfile`, and
  `torchaudio` issues immediately
- **No integration tests on target hardware** - tests were written and run
  on machines without GPU

### Environment Planning
- **RunPod environment not validated upfront** - Python 3.12 default
  incompatibility was discovered during deployment, not planning
- **No Docker image** - would have eliminated all environment variability
- **Jupyter Lab terminal workflow undocumented** - learned by trial and error

### End-to-End Execution
- **Pipeline never produced a video** - each dependency fix revealed the
  next dependency issue in a chain of failures
- **Model downloads untested** - ~12GB of models need to download on first
  run; this was never validated in a clean environment

---

## Bitter Lessons

1. **A library from a dead company is a liability, not an asset.**
   Coqui TTS was the best open-source voice cloning library. But "best"
   doesn't matter when the dependency tree is broken and nobody will fix it.
   Assess the *maintainer*, not just the *code*.

2. **Tests that mock everything test nothing.**
   Our 135 tests all passed. Our code didn't run. The tests proved our
   business logic was correct but said nothing about whether the software
   could actually execute. Smoke import tests cost 5 minutes to write and
   would have saved days.

3. **Dependency problems are planning problems, not debugging problems.**
   Every issue we hit (Python version ceiling, stale pins, removed APIs,
   missing transitive deps) was knowable before writing a single line of
   application code. The `/dependency-risk-planner` skill encodes this
   lesson: spend an hour auditing dependencies during planning, save days
   during testing.

4. **The gap between "code complete" and "working software" can be enormous.**
   We had 3,400+ lines of well-structured code, 135 passing tests, complete
   documentation, and zero working output. The last mile (real dependencies,
   real GPU, real model downloads) is where ML projects actually fail.

5. **Framework utility functions are ephemeral; C library wrappers are eternal.**
   `torchaudio.info()` was removed. `soundfile.info()` (wrapping `libsndfile`,
   a 20-year-old C library) works fine. When choosing between a framework
   convenience function and a stable C wrapper, choose the C wrapper.

6. **RunPod/cloud GPU environments are their own platform.**
   They have different default Python versions, pre-installed packages,
   filesystem layouts, and network constraints. Treat them as a deployment
   target that needs its own install script and validation, not as "just
   another Linux box."

---

## Quick Start

### PIC Workflow System

```bash
bash scripts/pic-init.sh        # Initialize
# Then in Claude Code:
/pic-start Build a login system  # Start a workflow
/pic-status                      # Check progress
```

### Avatar Pipeline

```bash
# See docs/avatar-pipeline/INSTALLATION_GUIDE.md for full instructions
# TL;DR (requires Python 3.10 or 3.11):
python3.11 -m venv venv --clear && source venv/bin/activate
pip install TTS==0.22.0 --no-deps   # Dead library workaround
pip install -e . --no-deps
pip install torch torchaudio soundfile numpy scipy librosa scikit-learn \
    einops unidecode num2words coqpit diffusers transformers accelerate \
    mediapipe opencv-python Pillow fastapi "uvicorn[standard]" click \
    pyyaml pydantic python-multipart
avatar status                        # Verify setup
```

### Dependency Risk Planning

```bash
# In Claude Code, before choosing dependencies for any new project:
/dependency-risk-planner torch TTS diffusers
```

---

## Acknowledgements

- The **PIC (Pilot in Command) workflow system** was inspired by the concept presented in
  [Why NVIDIA builds their own open models | Nemotron w/ Bryan Catanzaro](https://www.youtube.com/watch?v=Y3Vb6ecvfpU&t=19s)
- The **avatar lip-sync video pipeline** idea was inspired by
  [Claude Code Let's Build: The AI Video Oracle (Qwen3 TTS)](https://www.youtube.com/watch?v=Vbws3a_OmBM&t=46s)
- All code and documentation in this repository were generated by
  [Claude Code](https://claude.com/claude-code) powered by Claude Opus 4.5

---

## License

MIT - see [LICENSE](LICENSE)
