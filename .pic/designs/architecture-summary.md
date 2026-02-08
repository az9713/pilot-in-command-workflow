# Architecture Summary

**Workflow**: WF-20260205-010915
**Design PIC**: pic-design
**Created**: 2026-02-05T05:40:00Z

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE (CLI / REST API)              │
└─────────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                         │
│  Job Queue │ Pipeline Coordinator │ VRAM Manager │ Progress     │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ VOICE MODULE  │       │ AVATAR MODULE │       │ VIDEO MODULE  │
│ - XTTS-v2     │       │ - SDXL 1.5    │       │ - MuseTalk    │
│ - Coqui TTS   │       │ - MediaPipe   │       │ - FFmpeg      │
└───────────────┘       └───────────────┘       └───────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                             │
│  Voice Profiles │ Avatar Assets │ Job State │ Output Artifacts  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DEC-D1 | Sequential model loading | 10GB VRAM limit |
| DEC-D2 | Module isolation | Testability, future parallelization |
| DEC-D3 | File-based IPC | Simplicity, job resumption |
| DEC-D4 | Synchronous pipeline | VRAM constraints |

## Component Stack

| Component | Tool | VRAM | Interface |
|-----------|------|------|-----------|
| Voice Clone | XTTS-v2 | 4-6GB | VoiceClonerInterface |
| TTS | Coqui TTS | 2-4GB | TTSSynthesizerInterface |
| Avatar Gen | SDXL 1.5 | 6-8GB | AvatarGeneratorInterface |
| Lip-Sync | MuseTalk | 4-6GB | LipSyncEngineInterface |

## VRAM Management Timeline

```
Step 1: [████ XTTS-v2 (4-6GB) ████] → unload
Step 2:                             [████ Coqui TTS (2-4GB) ████] → unload
Step 3:                                                          [████ SDXL (6-8GB) ████] → unload
Step 4:                                                                                    [████ MuseTalk (4-6GB) ████]
```

## Project Structure

```
src/
├── voice/          # Voice cloning + TTS
├── avatar/         # Image generation + face detection
├── video/          # Lip-sync + encoding
├── orchestration/  # Pipeline coordination
├── api/            # REST API (FastAPI)
└── config/         # Configuration system
```

## Design Documents Created

1. **architecture.md** - Full system architecture
2. **interfaces.md** - Python API contracts
3. **data-models.md** - Storage schemas
4. **api-spec.md** - REST API specification
5. **config-schema.md** - Configuration system

## Implementation Priority

1. Project structure + config system (M1)
2. Voice module (XTTS-v2 + Coqui TTS) (M2)
3. Avatar module (SDXL 1.5) (M3)
4. Video module (MuseTalk) (M4)
5. Orchestration layer (M5)
6. REST API (M5)
