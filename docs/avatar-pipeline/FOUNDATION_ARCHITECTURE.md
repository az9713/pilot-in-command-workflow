# Foundation Module Architecture

**Milestone**: M1 - Foundation
**Status**: Complete
**Implementation Date**: 2026-02-05

## Overview

The foundation module provides the core infrastructure for the Avatar Pipeline, including hardware detection, configuration management, and VRAM optimization for sequential model loading.

## Module Structure

```
src/
├── __init__.py                 # Package initialization
├── cli.py                      # CLI entry point (182 lines)
├── config/
│   ├── __init__.py            # Config module exports
│   ├── hardware.py            # GPU detection (114 lines)
│   └── settings.py            # Config loader (171 lines)
└── utils/
    ├── __init__.py            # Utils module exports
    └── vram.py                # VRAM manager (236 lines)
```

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                       CLI (cli.py)                          │
│  • status command                                           │
│  • Help system                                              │
│  • Version info                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Configuration System (config/)                  │
│                                                              │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  hardware.py     │        │  settings.py     │          │
│  │                  │        │                  │          │
│  │  • detect_gpu()  │───────▶│  • load_config() │          │
│  │  • get_profile() │        │  • deep_merge()  │          │
│  └──────────────────┘        └──────────────────┘          │
│                                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              VRAM Management (utils/)                        │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │  VRAMManager                             │              │
│  │                                          │              │
│  │  • get_status() → VRAMStatus            │              │
│  │  • can_load(required_mb) → bool         │              │
│  │  • force_cleanup()                      │              │
│  │  • log_status()                         │              │
│  └──────────────────────────────────────────┘              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Startup Sequence

```
1. User runs: avatar status
   │
   ▼
2. CLI initializes
   │
   ▼
3. hardware.detect_gpu() called
   │  └─→ Checks torch.cuda.is_available()
   │  └─→ Gets VRAM info
   │  └─→ Returns GPU dict
   │
   ▼
4. hardware.get_hardware_profile() called
   │  └─→ Evaluates VRAM capacity
   │  └─→ Returns profile name
   │
   ▼
5. settings.load_config() called
   │  └─→ Loads profile defaults
   │  └─→ Loads user YAML (if provided)
   │  └─→ Merges configs
   │  └─→ Returns final config dict
   │
   ▼
6. VRAMManager.get_status() called
   │  └─→ Queries current VRAM usage
   │  └─→ Returns VRAMStatus object
   │
   ▼
7. CLI displays all information
```

## Hardware Profile Selection

```
VRAM Capacity Decision Tree:

Total VRAM
    │
    ├─ >= 20GB ──→ rtx4090 profile
    │              • High quality
    │              • Batch size: 4
    │              • Steps: 50
    │
    ├─ >= 8GB  ──→ rtx3080 profile (TARGET)
    │              • Medium quality
    │              • Batch size: 2
    │              • Steps: 40
    │
    └─ < 8GB   ──→ low_vram profile
                   • Reduced quality
                   • Batch size: 1
                   • Steps: 25
```

## Configuration Cascade

```
Configuration Priority (highest to lowest):

1. User YAML file
   └─→ config/pipeline.yaml (explicit overrides)

2. Profile Defaults
   └─→ DEFAULT_CONFIGS[profile] in settings.py

3. Fallback Behavior
   └─→ CPU mode if CUDA unavailable
```

## VRAM Manager Usage Pattern

```python
# Typical usage in model loading code:

from src.utils import VRAMManager

# Initialize
vram = VRAMManager()

# Check before loading
if vram.can_load(required_mb=4096, safety_margin_mb=512):
    model = load_model()

    # Use model
    output = model.process(input_data)

    # Cleanup after unload
    del model
    vram.force_cleanup()
else:
    raise RuntimeError("Insufficient VRAM")
```

## Key Design Decisions

### DEC-I1: Hardware Profile System
**Decision**: Auto-detect GPU and select profile based on VRAM
**Rationale**: Simplifies user experience, prevents OOM errors
**Trade-off**: Less flexibility vs. ease of use

### DEC-I2: Deep Config Merging
**Decision**: Recursively merge user config with profile defaults
**Rationale**: Allows partial overrides while maintaining sensible defaults
**Trade-off**: More complex logic vs. user convenience

### DEC-I3: Aggressive VRAM Cleanup
**Decision**: Force GC + cache clear between model loads
**Rationale**: Ensures maximum VRAM available for next model
**Trade-off**: Slight performance overhead vs. reliability

### DEC-I4: Safety Margin in can_load()
**Decision**: Default 512MB safety margin when checking VRAM
**Rationale**: Prevents edge case OOM during model loading
**Trade-off**: Slightly conservative vs. preventing crashes

## Error Handling Strategy

### Hardware Detection
- **CUDA unavailable**: Log warning, return CPU mode
- **PyTorch missing**: Log error, return CPU mode
- **Detection error**: Log error, fallback to CPU mode

### Config Loading
- **File not found**: Log warning, use defaults
- **Invalid YAML**: Raise ValueError with details
- **Empty file**: Log warning, use defaults

### VRAM Management
- **Status query fails**: Return zero values
- **Cleanup fails**: Log error, continue
- **CPU mode**: Return True for can_load() (no constraint)

## Testing Strategy

### Unit Tests (Future)
- `test_hardware.py`: GPU detection, profile selection
- `test_settings.py`: Config loading, merging
- `test_vram.py`: Status, can_load, cleanup

### Integration Tests (Future)
- `test_cli.py`: Command execution, output format
- `test_config_cascade.py`: Profile + user config merging

### Manual Verification (Completed)
- [x] CLI status command works
- [x] Config loading works
- [x] Verbose mode displays full config
- [x] Hardware detection in CPU mode
- [x] Custom config file support

## Dependencies

### Direct Dependencies
- `torch>=2.0`: GPU detection and VRAM monitoring
- `click>=8.1.0`: CLI framework
- `pyyaml>=6.0`: Config file parsing

### Standard Library
- `logging`: Structured logging
- `pathlib`: Path handling
- `dataclasses`: VRAMStatus structure
- `gc`: Garbage collection

## File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| `cli.py` | 182 | CLI commands and display |
| `hardware.py` | 114 | GPU detection |
| `settings.py` | 171 | Config loading |
| `vram.py` | 236 | VRAM management |
| **Total** | **713** | Foundation module |

## Next Steps (Milestone 2: Voice Module)

The foundation is ready. Next implementation phase will add:

1. `src/voice/cloner.py` - XTTS-v2 integration
2. `src/voice/synthesizer.py` - Coqui TTS integration
3. `src/voice/profiles.py` - Voice profile CRUD

These will use:
- `VRAMManager` to check capacity before loading models
- `load_config()` to get voice-specific settings
- Hardware profile to set precision and batch sizes
