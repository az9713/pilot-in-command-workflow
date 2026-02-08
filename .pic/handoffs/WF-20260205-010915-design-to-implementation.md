# Handoff: Design → Implementation

**Workflow**: WF-20260205-010915
**Timestamp**: 2026-02-05T05:50:00Z
**From PIC**: pic-design (planner)
**To PIC**: pic-implementation (builder)

## Phase Summary

### Completed Work
Created comprehensive technical architecture with interfaces, data models, API spec, and configuration schema for the AI avatar video pipeline.

### Deliverables
- System architecture (4-layer design)
- Python interface specifications (ABCs)
- Data model schemas (JSON)
- REST API specification
- Hardware-aware configuration system

### Key Architectural Decisions
1. Sequential model loading (one at a time for 10GB VRAM)
2. Module isolation (separate packages)
3. File-based IPC (enables job resumption)
4. Synchronous pipeline execution

## Implementation Priorities

### Phase 1: Foundation (Start Here)
```
src/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py      # Configuration loader
│   └── hardware.py      # GPU detection
└── utils/
    ├── __init__.py
    └── vram.py          # VRAM manager
```

### Phase 2: Voice Module
```
src/voice/
├── __init__.py
├── cloner.py            # XTTS-v2 integration
├── synthesizer.py       # Coqui TTS integration
└── profiles.py          # Voice profile CRUD
```

### Phase 3: Avatar Module
```
src/avatar/
├── __init__.py
├── generator.py         # SDXL 1.5 integration
└── detector.py          # Face detection (MediaPipe)
```

### Phase 4: Video Module
```
src/video/
├── __init__.py
├── lipsync.py           # MuseTalk integration
└── encoder.py           # FFmpeg wrapper
```

### Phase 5: Orchestration + API
```
src/
├── orchestration/
│   ├── __init__.py
│   ├── coordinator.py   # Pipeline coordinator
│   └── queue.py         # Job queue
└── api/
    ├── __init__.py
    └── main.py          # FastAPI app
```

## Component Specifications

### Voice Module Interface
```python
class VoiceClonerInterface(ABC):
    def clone_voice(self, audio: Path, name: str, lang: str) -> CloneResult
    def load_profile(self, profile_id: str) -> VoiceProfile
    def list_profiles(self) -> list[VoiceProfile]

class TTSSynthesizerInterface(ABC):
    def synthesize(self, text: str, profile: VoiceProfile, output: Path) -> SynthesisResult
```

### Hardware Requirements
- Target: RTX 3080 (10GB VRAM)
- Sequential model loading required
- FP16 for all models
- Aggressive VRAM cleanup between stages

## First Implementation Task

**Start with**: Project structure + configuration system

1. Create `pyproject.toml` with dependencies
2. Implement hardware detection (`src/config/hardware.py`)
3. Implement config loader (`src/config/settings.py`)
4. Implement VRAM manager (`src/utils/vram.py`)
5. Add basic CLI entry point

### Key Dependencies
```toml
[project]
dependencies = [
    "torch>=2.0",
    "torchaudio",
    "TTS",                    # Coqui TTS
    "diffusers",              # SDXL
    "transformers",
    "mediapipe",              # Face detection
    "fastapi",
    "uvicorn",
    "pyyaml",
    "click",                  # CLI
]
```

## Constraints
- All code MIT/Apache licensed
- Must run on 10GB VRAM
- 120 second max video length
- Batch processing only (no real-time)
