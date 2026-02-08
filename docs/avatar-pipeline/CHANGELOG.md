# Changelog

All notable changes to the Avatar Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-05

### Added - Milestone 1: Foundation Module

#### Project Structure
- Created `src/` directory with modular organization
- Set up Python package structure with proper `__init__.py` files
- Organized modules: `config/`, `utils/`

#### Configuration System
- **Hardware Detection** (`src/config/hardware.py`):
  - GPU detection with CUDA support
  - VRAM monitoring (total and free memory)
  - Hardware profile selection (rtx4090/rtx3080/low_vram)
  - Graceful fallback to CPU mode

- **Config Loader** (`src/config/settings.py`):
  - YAML configuration file support
  - Hardware profile-based defaults
  - Deep merge of user config with defaults
  - Three profiles with optimized settings for different VRAM capacities

#### VRAM Management
- **VRAM Manager** (`src/utils/vram.py`):
  - Real-time VRAM status monitoring
  - Pre-allocation checks with safety margins
  - Aggressive cleanup for sequential model loading
  - `VRAMStatus` dataclass for structured status info

#### CLI Interface
- **Command-line Tool** (`src/cli.py`):
  - `avatar status` command showing:
    - GPU information and VRAM usage
    - Hardware profile detection
    - Configuration status
    - Model compatibility checks
  - Verbose mode for detailed config display
  - Custom config file support

#### Project Configuration
- **pyproject.toml**: Modern Python packaging with:
  - Core dependencies (torch, TTS, diffusers, transformers)
  - Optional dev dependencies (pytest, black, ruff)
  - Entry point script: `avatar` command
  - Tool configurations (black, ruff, mypy, pytest)

- **requirements.txt**: Alternative dependency specification

- **config/pipeline.yaml**: Template configuration with:
  - Voice settings (XTTS-v2, Coqui TTS)
  - Avatar settings (SDXL)
  - Video settings (MuseTalk)
  - Storage paths
  - API configuration
  - Logging options

#### Documentation
- **README.md**: Project overview and quick start guide
- **.gitignore**: Comprehensive Python/ML project exclusions
- **CHANGELOG.md**: This file

### Technical Highlights
- 713 lines of Python code
- Full type hints and documentation
- Hardware-aware configuration system
- Optimized for RTX 3080 (10GB VRAM)
- Sequential model loading strategy
- Graceful degradation for low VRAM

### Verified Functionality
- [x] CLI runs successfully
- [x] Hardware detection works (tested in CPU mode)
- [x] Config loading and merging works
- [x] Status command displays all information
- [x] Verbose mode shows full config
- [x] Custom config file support works

## [0.1.1] - 2026-02-07

### Fixed - Runtime Dependency Issues
- Replaced `torchaudio.info()` with `soundfile.info()` in `cloner.py` and `lipsync.py`
  (torchaudio removed this API in 2.1+)
- Added `coqpit` to all dependency lists (missing TTS transitive dependency)
- Fixed 25 test failures: `mocker.patch()` → `mocker.patch.dict("sys.modules", ...)`
  for local-import mocking pattern
- Fixed wrong class names in tests: `VoiceCloneResult` → `CloneResult`,
  `AvatarGenerationResult` → `GenerationResult`
- Fixed missing dataclass fields in test constructors (`error`, `landmarks`, `job_id`)

### Added - Documentation & Tooling
- **LESSONS_LEARNED.md**: 8 categorized issues, root cause analysis, prevention strategies,
  decision records, future risk register, TTS replacement candidates
- **INSTALLATION_GUIDE.md**: Step-by-step install with RunPod setup, known issues table,
  troubleshooting for every encountered error
- **`/dependency-risk-planner` skill**: Claude Code skill for pre-flight dependency risk
  assessment during the planning phase (4-phase protocol, 360 lines)
- **Root README.md**: Project retrospective documenting successes, failures, and bitter lessons

### Changed
- `pyproject.toml`: Added `requires-python = ">=3.10,<3.12"`, pinned `TTS==0.22.0`,
  added all TTS transitive deps including `coqpit`
- `requirements.txt`: Rewritten with TL;DR install recipe and `--no-deps` explanation
- `scripts/install.sh`: Auto-detects Python 3.10/3.11, refuses 3.12+, `--clear` venv
- `scripts/install.ps1`: Same fixes for Windows PowerShell

### Status
- **135 tests passing** on both RunPod (RTX 5090) and Windows (no GPU)
- **End-to-end pipeline**: NOT yet completed (dependency chain still being resolved)
- **Voice cloning step**: Reached model loading phase before session ended

## [0.1.0] - 2026-02-05

### Added - Milestone 1: Foundation Module (M1)

(See below for original M1 details)

### Added - Milestone 2: Voice Module (M2)
- XTTS-v2 voice cloning (`src/voice/cloner.py`) with 17-language support
- Coqui TTS synthesis (`src/voice/synthesizer.py`)
- Voice profile management (`src/voice/profiles.py`) with file-based storage
- Audio validation: minimum 3 seconds, recommended 6+ seconds
- Auto-resample to 22050 Hz mono for XTTS compatibility

### Added - Milestone 3: Avatar Module (M3)
- SDXL 1.5 avatar generation (`src/avatar/generator.py`)
- MediaPipe face detection (`src/avatar/detector.py`) with landmark tracking
- Avatar profile management (`src/avatar/profiles.py`)
- Aspect ratio support (1:1, 16:9, 9:16)
- VRAM-aware model loading with FP16 support

### Added - Milestone 4: Video Module (M4)
- MuseTalk lip-sync engine (`src/video/lipsync.py`) with FFmpeg fallback
- FFmpeg video encoder (`src/video/encoder.py`)
- Quality presets (high/medium/low)
- Max video length: 120 seconds
- Mel spectrogram feature extraction for audio-driven animation

### Added - Milestone 5: Orchestration & API (M5)
- Pipeline coordinator (`src/orchestration/coordinator.py`): 6-stage sequential execution
- File-based job queue (`src/orchestration/queue.py`) with status tracking
- REST API (`src/api/main.py`): 17 endpoints via FastAPI
- CLI extensions: `avatar voice`, `avatar avatar`, `avatar video`, `avatar pipeline`, `avatar server`, `avatar jobs`
- 3,433 lines of orchestration code

### Added - Milestone 6: Polish (M6)
- 6 example scripts (`examples/01_voice_cloning.py` through `examples/06_api_client.py`)
- 4 hardware config templates (default, rtx4090, rtx3080, low_vram)
- Install scripts for Linux/macOS (`install.sh`) and Windows (`install.ps1`)
- CONTRIBUTING.md with development workflow
- README.md (524 lines) with complete usage guide
- 135 tests across 8 test files
