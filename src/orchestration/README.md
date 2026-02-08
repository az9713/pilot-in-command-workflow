# Orchestration Module

The orchestration module coordinates the full avatar video generation pipeline, managing job queues and sequential model execution.

## Components

### Pipeline Coordinator (`coordinator.py`)

Orchestrates the complete pipeline from text to video:

1. **Load Voice Profile** - Retrieves the voice profile for TTS
2. **Synthesize Speech** - Generates audio from text using TTS
3. **Validate Avatar** - Detects and validates face in avatar image
4. **Generate Lip-Sync** - Creates talking head video with lip-sync
5. **Encode Final Video** - Encodes output with specified quality
6. **Cleanup** - Removes intermediate files (optional)

**Usage:**

```python
from pathlib import Path
from src.orchestration import PipelineCoordinator, PipelineConfig
from src.utils import VRAMManager

# Initialize
config = load_config()
vram_manager = VRAMManager()
coordinator = PipelineCoordinator(
    config=config,
    vram_manager=vram_manager,
    storage_path=Path("storage"),
)

# Execute pipeline
result = coordinator.execute(
    text="Hello, world!",
    voice_profile_id="vp-abc12345",
    avatar_image=Path("avatar.png"),
    output_path=Path("output.mp4"),
    config=PipelineConfig(video_quality="high"),
)

if result.success:
    print(f"Video created: {result.output_path}")
    print(f"Duration: {result.duration_seconds:.2f}s")
else:
    print(f"Error: {result.error}")
```

**Configuration Options:**

```python
PipelineConfig(
    max_video_length_seconds=120,  # Maximum video duration
    output_format="mp4",            # Output format
    cleanup_intermediates=True,     # Remove temp files
    video_quality="high",           # Quality preset (high/medium/low)
    video_fps=None,                 # FPS override (None = use preset)
    encoding_preset="medium",       # FFmpeg preset
    encoding_crf=23,                # Quality (0-51, lower is better)
)
```

### Job Queue (`queue.py`)

File-based job queue for asynchronous pipeline execution.

**Features:**

- Persistent storage (JSON files)
- Job status tracking
- Progress updates
- CRUD operations
- Job statistics

**Usage:**

```python
from src.orchestration import JobQueue, JobType

# Initialize queue
queue = JobQueue(storage_path=Path("storage"))

# Submit job
job_id = queue.submit(
    job_type=JobType.FULL_PIPELINE,
    params={
        "text": "Hello!",
        "voice_profile_id": "vp-abc12345",
        "avatar_image_path": "avatar.png",
        "output_filename": "output.mp4",
    }
)

# Check status
job = queue.get(job_id)
print(f"Status: {job.status.value}")
print(f"Progress: {job.progress * 100:.1f}%")

# List jobs
jobs = queue.list_jobs(status=JobStatus.PENDING, limit=10)

# Cancel job
queue.cancel(job_id)
```

**Storage Structure:**

```
storage/jobs/
├── job-20240115120000-abc12345.json
├── job-20240115120100-def67890.json
└── ...
```

### Job Definitions (`jobs.py`)

Data structures for job management.

**Job Types:**

- `FULL_PIPELINE` - Complete text-to-video pipeline
- `VOICE_CLONE` - Voice cloning only
- `VOICE_SYNTHESIS` - TTS synthesis only
- `AVATAR_GENERATION` - Avatar image generation only
- `VIDEO_LIPSYNC` - Lip-sync video generation only
- `VIDEO_ENCODING` - Video encoding only

**Job Statuses:**

- `PENDING` - Queued, not started
- `RUNNING` - Currently executing
- `COMPLETED` - Finished successfully
- `FAILED` - Finished with error
- `CANCELLED` - Cancelled by user

**Job Structure:**

```python
Job(
    job_id="job-20240115120000-abc12345",
    status=JobStatus.RUNNING,
    job_type=JobType.FULL_PIPELINE,
    params={...},              # Input parameters
    created_at="2024-01-15T12:00:00Z",
    started_at="2024-01-15T12:00:05Z",
    completed_at=None,
    result=None,               # Output data (when completed)
    error=None,                # Error message (when failed)
    progress=0.45,             # 0.0 to 1.0
    stage="generate_lipsync",  # Current stage description
)
```

## Pipeline Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     Pipeline Coordinator                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 1: Load Voice Profile      │
         │   • Validate profile exists         │
         │   • Load speaker embedding          │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 2: Synthesize Speech       │
         │   • Load TTS model                  │
         │   • Generate audio from text        │
         │   • Unload model + cleanup VRAM     │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 3: Validate Avatar         │
         │   • Detect face in image            │
         │   • Validate for lip-sync           │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 4: Generate Lip-Sync       │
         │   • Load lip-sync model             │
         │   • Generate talking head video     │
         │   • Unload model + cleanup VRAM     │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 5: Encode Final Video      │
         │   • Apply encoding settings         │
         │   • Compress/transcode video        │
         └────────────────────────────────────┘
                              │
                              ▼
         ┌────────────────────────────────────┐
         │   Stage 6: Cleanup (optional)      │
         │   • Delete intermediate files       │
         └────────────────────────────────────┘
                              │
                              ▼
                      ┌─────────────┐
                      │ Final Video │
                      └─────────────┘
```

## VRAM Management

The orchestration layer ensures sequential model loading to fit within VRAM constraints:

1. **One model at a time** - Only one heavy model loaded in VRAM
2. **Explicit cleanup** - Force VRAM cleanup between stages
3. **Status monitoring** - Log VRAM usage at each stage
4. **Error recovery** - Cleanup on failure

Example VRAM timeline:

```
Time   VRAM Usage              Model
────   ──────────────────────  ─────────────────
t0     512MB (baseline)        None
t1     3.5GB                   Coqui TTS loaded
t2     512MB                   TTS unloaded + cleanup
t3     5.6GB                   MuseTalk loaded
t4     512MB                   MuseTalk unloaded + cleanup
```

## Error Handling

The pipeline uses a staged error handling approach:

```python
result = coordinator.execute(...)

if not result.success:
    print(f"Failed after: {result.stages_completed}")
    # Output: ["load_profile", "synthesize_speech"]
    # Failed at stage 3 (validate_avatar)
```

**Cleanup on Error:**

- Intermediate files are cleaned up automatically
- VRAM is freed before raising errors
- Partial results are not saved

## Integration with API

The orchestration layer is used by the REST API for async job processing:

```python
# API endpoint submits job
job_id = job_queue.submit(JobType.FULL_PIPELINE, params)

# Background worker processes job
job = job_queue.get(job_id)
job.start()

coordinator = PipelineCoordinator(...)
result = coordinator.execute(...)

if result.success:
    job.complete(result)
else:
    job.fail(result.error)
```

## CLI Usage

The orchestration layer can be used via CLI:

```bash
# Full pipeline execution
avatar pipeline run "Hello, world!" \
  --voice vp-abc12345 \
  --avatar avatar.png \
  --output video.mp4 \
  --quality high

# Job queue management
avatar jobs list --status pending
avatar jobs status job-20240115-abc12345
```

## Performance Considerations

**Sequential Processing:**

- Trades parallelism for VRAM efficiency
- Total time = sum of stage times
- Suitable for RTX 3080 (10GB VRAM)

**Typical Processing Times (RTX 3080):**

| Stage | Duration (for 10s audio) |
|-------|-------------------------|
| Load profile | 0.1s |
| Synthesize speech | 20s (2x realtime) |
| Validate avatar | 0.5s |
| Generate lip-sync | 50s (5x realtime) |
| Encode video | 5s (0.5x realtime) |
| **Total** | **~76s** |

**Optimization Tips:**

1. **Batch processing** - Process multiple jobs sequentially
2. **Quality presets** - Use "medium" for faster processing
3. **Keep intermediates** - Skip cleanup for debugging
4. **Reduce FPS** - Lower frame rate = faster processing

## Testing

Run orchestration tests:

```bash
# Unit tests
pytest tests/test_orchestration.py

# Integration tests
pytest tests/test_pipeline_integration.py

# Example execution
python examples/pipeline_example.py
```

## Related Modules

- **config** - Configuration management
- **utils** - VRAM monitoring
- **voice** - Voice cloning and TTS
- **avatar** - Avatar generation and face detection
- **video** - Lip-sync and video encoding
- **api** - REST API endpoints
