# Handoff: Planning → Design

**Workflow**: WF-20260205-010915
**Timestamp**: 2026-02-05T05:35:00Z
**From PIC**: pic-planning (planner)
**To PIC**: pic-design (planner)

## Phase Summary

### Completed Work
Created comprehensive 7-week strategic plan with milestones, task breakdown, risk register, and success criteria for the open-source ElevenLabs alternative.

### Deliverables
- Strategic plan with 4 key decisions documented
- 6 milestones with success criteria
- 41 tasks broken down by phase (8 design, 21 impl, 12 test)
- Risk register with 10 identified risks and mitigations
- Success criteria with measurable targets

### Strategic Decisions Made
1. **Hardware Target**: RTX 3080 (10GB) - best cost/capability balance
2. **Integration**: Python orchestration with ComfyUI bridge for SDXL
3. **Scope**: Batch processing first, real-time voice changer deferred
4. **Video Length**: 120 seconds maximum

## Context for Design Phase

### Architecture Scope
Design PIC must define:
1. System architecture and component boundaries
2. Interface specifications for voice, avatar, lip-sync modules
3. Data models for voice profiles, jobs, pipeline state
4. REST API contracts
5. Configuration schema for hardware-aware model selection

### Component Stack
| Component | Primary Tool | VRAM Budget |
|-----------|-------------|-------------|
| Voice Clone | XTTS-v2 | 4-6GB |
| TTS | Coqui TTS | 2-4GB |
| Image Gen | SDXL 1.5 | 6-8GB |
| Lip-sync | MuseTalk | 4-6GB |

### Design Tasks (from Plan)
| ID | Task | Priority |
|----|------|----------|
| D1 | System architecture and component boundaries | P0 |
| D2 | Voice pipeline interfaces | P0 |
| D3 | Avatar generation interfaces | P0 |
| D4 | Lip-sync pipeline interfaces | P0 |
| D5 | Orchestration layer and job queue schema | P0 |
| D6 | REST API endpoints | P1 |
| D7 | Configuration schema | P0 |
| D8 | ComfyUI bridge interface | P2 |

### Key Constraints
- Must run on 10GB VRAM (sequential model loading)
- Batch processing only (30-50 min per 60s video acceptable)
- Support 16:9 and 9:16 aspect ratios
- All MIT/Apache licensed components

### Open Questions for User
1. Real-time voice changer: MVP or Phase 2?
2. Web UI required, or CLI + API sufficient?
3. Cloud deployment guides needed?
4. Priority languages for testing?

## Exit Criteria Verification

| Criterion | Status |
|-----------|--------|
| Approach documented with rationale | Met |
| Milestones defined with success criteria | Met |
| Tasks broken down and assigned | Met |
| Risks identified with mitigations | Met |
| Design PIC has clear direction | Met |
