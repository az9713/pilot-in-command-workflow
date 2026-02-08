# Handoff: Research → Planning

**Workflow**: WF-20260205-010915
**Timestamp**: 2026-02-05T05:25:00Z
**From PIC**: pic-research (Explore)
**To PIC**: pic-planning (planner)

## Phase Summary

### Completed Work
Comprehensive research on open-source alternatives to the ElevenLabs AI avatar video pipeline. Evaluated tools across all five pipeline components with hardware requirements, quality assessments, and licensing analysis.

### Deliverables
- Complete research findings with tool recommendations
- Hardware requirements matrix (6-24GB VRAM options)
- Licensing analysis (all MIT/Apache compatible)
- Integration architecture overview
- Risk assessment and knowledge gaps

### Handoff Notes
Research complete. Found viable open-source alternatives: XTTS-v2/OpenVoice for voice cloning, Coqui TTS for speech synthesis, SDXL/Flux for avatar images, MuseTalk/Wav2Lip for lip-sync. Recommended hardware: RTX 3080 (10GB). Processing time: 30-50 min per 60-sec video. All MIT/Apache licensed.

## Context for Next Phase

### Key Findings

| Component | Primary Choice | Alternative | VRAM |
|-----------|---------------|-------------|------|
| Voice Cloning | XTTS-v2 | OpenVoice | 4-8GB |
| TTS | Coqui TTS | Qwen3-TTS | 4-6GB |
| Image Gen | SDXL 1.5 | Flux | 8-24GB |
| Lip-sync | MuseTalk | Wav2Lip | 4-8GB |

**Recommended Pipeline:**
```
Voice Sample → XTTS Clone → TTS → Audio
                                    ↓
Reference Photo → SDXL → Avatar → MuseTalk → Video
```

### Open Questions
1. Should we target MVP (RTX 3080) or Premium (RTX 4090) hardware tier?
2. ComfyUI workflow vs custom Python orchestration?
3. Real-time voice changer priority vs batch processing only?
4. Target video length limits (60s like Creatify Aurora?)

### Risks/Concerns
- 30-50 min processing per 60-sec video (not real-time)
- Quality variance 5-15% vs commercial solutions
- Complex multi-model orchestration required
- Wav2Lip low native resolution (needs upscaling)

## Exit Criteria Verification

| Criterion | Status |
|-----------|--------|
| Problem clearly understood | Met |
| Relevant prior art identified | Met |
| Key constraints documented | Met |
| Evidence quality sufficient | Met |
| Knowledge gaps listed | Met |
