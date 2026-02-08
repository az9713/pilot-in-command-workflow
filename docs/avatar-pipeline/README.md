# Avatar Pipeline

Open-source AI avatar video generation pipeline with voice cloning, text-to-speech, avatar generation, and lip-sync capabilities. Optimized for consumer GPUs (RTX 3080 10GB).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10-3.11](https://img.shields.io/badge/python-3.10--3.11-blue.svg)](https://www.python.org/downloads/)

## Features

- **Voice Cloning**: Clone any voice from 3+ seconds of audio using XTTS-v2 (17 languages)
- **Text-to-Speech**: Generate natural-sounding speech with Coqui TTS
- **Avatar Generation**: Create photorealistic AI avatars with Stable Diffusion XL 1.5
- **Lip-Sync**: Animate avatar faces with MuseTalk for realistic talking videos
- **VRAM Optimized**: Sequential model loading for 10GB VRAM GPUs
- **REST API**: Remote access via FastAPI for job submission and monitoring
- **CLI Interface**: Complete command-line tools for all operations

## Quick Start

### Installation

> **Python 3.10 or 3.11 required.** Python 3.12+ will NOT work (Coqui TTS dependency).
> See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for detailed instructions and troubleshooting.

```bash
# Automated install (handles all workarounds):
cd avatar-pipeline
bash scripts/install.sh       # Linux/macOS/RunPod
# .\scripts\install.ps1       # Windows PowerShell

# --- OR manual install: ---
python3.11 -m venv venv --clear
source venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install TTS==0.22.0 --no-deps          # Must use --no-deps (see guide)
pip install -e . --no-deps
pip install torch torchaudio diffusers transformers accelerate mediapipe \
    opencv-python Pillow fastapi "uvicorn[standard]" click pyyaml pydantic \
    python-multipart numpy scipy soundfile librosa scikit-learn einops \
    unidecode num2words coqpit
```

### System Check

```bash
avatar status
```

This will show your GPU information, VRAM availability, hardware profile, and model compatibility.

### Example: Create Your First Video

```bash
# 1. Clone a voice
avatar voice clone reference.wav --name "My Voice"

# 2. Generate an avatar
avatar avatar generate "professional person, portrait" --aspect 16:9

# 3. Run the complete pipeline
avatar pipeline run "Hello! This is my first avatar video." \
  --voice "My Voice" \
  --avatar output/avatar.png \
  --output my_first_video.mp4 \
  --quality high
```

## Hardware Requirements

### Minimum Requirements
- **GPU**: NVIDIA GPU with 8GB+ VRAM
- **CUDA**: CUDA 11.8 or later
- **RAM**: 16GB system RAM
- **Python**: 3.10 or 3.11 only (NOT 3.12+)
- **Storage**: 20GB for models + output space

### Recommended Specs (Target)
- **GPU**: NVIDIA RTX 3080 (10GB VRAM)
- **CUDA**: CUDA 12.1
- **RAM**: 32GB system RAM
- **Storage**: SSD with 50GB+ free space

### Hardware Profiles

The system automatically detects your GPU and applies appropriate settings:

| Profile | VRAM | Description |
|---------|------|-------------|
| **rtx4090** | 20GB+ | High-end, full quality, parallel model loading |
| **rtx3080** | 8-20GB | Target spec, sequential model loading, fp16 precision |
| **low_vram** | <8GB | Reduced quality, CPU fallback for some operations |

See `config/pipeline.rtx3080.yaml` for target hardware configuration.

## Project Structure

```
avatar-pipeline/
├── src/                      # Source code
│   ├── config/              # Configuration and hardware detection
│   │   ├── hardware.py      # GPU detection and profiles
│   │   └── settings.py      # Config loading and defaults
│   ├── utils/               # Utilities
│   │   └── vram.py         # VRAM management for sequential loading
│   ├── voice/              # Voice cloning and TTS
│   │   ├── cloner.py       # XTTS-v2 voice cloning
│   │   ├── synthesizer.py  # Coqui TTS synthesis
│   │   └── profiles.py     # Voice profile management
│   ├── avatar/             # Avatar generation
│   │   ├── generator.py    # SDXL avatar generation
│   │   ├── detector.py     # MediaPipe face detection
│   │   └── profiles.py     # Avatar profile management
│   ├── video/              # Video generation
│   │   ├── lipsync.py      # MuseTalk lip-sync
│   │   └── encoder.py      # FFmpeg video encoding
│   ├── orchestration/      # Pipeline coordination
│   │   ├── coordinator.py  # Multi-stage pipeline executor
│   │   └── queue.py        # Job queue for API mode
│   ├── api/                # REST API
│   │   ├── main.py         # FastAPI application
│   │   └── routes/         # API endpoints
│   └── cli.py              # Command-line interface
├── config/                  # Configuration templates
│   ├── pipeline.yaml       # Default configuration
│   ├── pipeline.rtx4090.yaml   # High-end GPU settings
│   ├── pipeline.rtx3080.yaml   # Target spec settings
│   └── pipeline.low_vram.yaml  # Low VRAM settings
├── examples/                # Example scripts
│   ├── 01_voice_cloning.py
│   ├── 02_text_to_speech.py
│   ├── 03_avatar_generation.py
│   ├── 04_lipsync_video.py
│   ├── 05_full_pipeline.py
│   └── 06_api_client.py
├── docs/                    # Documentation
│   ├── INSTALLATION_GUIDE.md   # Step-by-step install (read this!)
│   └── LESSONS_LEARNED.md      # Dependency pitfalls & prevention
├── scripts/                 # Utility scripts
│   └── install.sh          # Installation helper
└── tests/                   # Test suite
```

## Architecture Overview

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                     CLI / REST API                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              Pipeline Coordinator                        │
│  (Sequential execution, VRAM management)                 │
└──┬──────────┬──────────┬───────────┬───────────────────┘
   │          │          │           │
   ▼          ▼          ▼           ▼
┌──────┐  ┌──────┐  ┌───────┐  ┌──────────┐
│Voice │  │Avatar│  │Lip-Sync│ │  Video   │
│Clone │  │ Gen  │  │        │ │ Encoder  │
│& TTS │  │      │  │        │ │          │
└──────┘  └──────┘  └───────┘  └──────────┘
   │          │          │           │
   ▼          ▼          ▼           ▼
┌─────────────────────────────────────────┐
│        VRAM Manager (Sequential)         │
│  Loads/unloads models to fit in VRAM     │
└─────────────────────────────────────────┘
```

### Pipeline Execution Flow

1. **Voice Synthesis**: Text → XTTS-v2/Coqui TTS → Audio file
2. **Avatar Validation**: Image → MediaPipe → Face detection/validation
3. **Lip-Sync**: Avatar + Audio → MuseTalk → Raw video frames
4. **Encoding**: Raw frames → FFmpeg → Final MP4 video

Each stage loads its model, executes, then unloads to free VRAM for the next stage.

## CLI Usage

### System Commands

```bash
# Check system status and GPU info
avatar status

# Show detailed configuration
avatar status --verbose --config config/custom.yaml
```

### Voice Commands

```bash
# Clone a voice from audio (3+ seconds, 6+ recommended)
avatar voice clone reference.wav --name "John Doe" --language en

# List all voice profiles
avatar voice list

# Generate speech from text
avatar voice speak "Hello, world!" --profile "John Doe" --output hello.wav
```

Supported languages: en, es, fr, de, it, pt, pl, tr, ru, nl, cs, ar, zh-cn, ja, hu, ko, hi

### Avatar Commands

```bash
# Generate avatar from text prompt
avatar avatar generate "professional woman, portrait, neutral expression" \
  --aspect 16:9 \
  --output avatar.png

# Detect and validate face in existing image
avatar avatar detect image.png --verbose

# List all avatar profiles
avatar avatar list
```

### Video Commands

```bash
# Create lip-synced video from image and audio
avatar video lipsync avatar.png speech.wav \
  --output video.mp4 \
  --quality high

# Re-encode video with different settings
avatar video encode input.mp4 --output output.mp4 \
  --quality medium \
  --codec libx264

# Show video information
avatar video info video.mp4 --verbose
```

### Pipeline Commands

```bash
# Run complete pipeline: text → speech → video
avatar pipeline run "Hello! This is a test." \
  --voice "My Voice" \
  --avatar avatar.png \
  --output final_video.mp4 \
  --quality high \
  --keep-temp

# Keep intermediate files for debugging
avatar pipeline run "Test message" \
  --voice vp-abc123 \
  --avatar avatar.png \
  --output test.mp4 \
  --keep-temp
```

### API Server

```bash
# Start REST API server
avatar server start --host 0.0.0.0 --port 8000

# Start with auto-reload for development
avatar server start --reload

# View API documentation (after starting server)
# Visit: http://localhost:8000/docs
```

### Job Management

```bash
# List all jobs
avatar jobs list

# Filter jobs by status
avatar jobs list --status running --limit 10

# Show specific job details
avatar jobs status job-20240115-abc12345
```

## API Usage

### Python Client Example

```python
import requests

# Submit pipeline job
response = requests.post("http://localhost:8000/api/v1/jobs/pipeline", json={
    "text": "Hello from the API!",
    "voice_profile_id": "vp-abc12345",
    "avatar_image_path": "avatar.png",
    "output_path": "output.mp4",
    "config": {
        "video_quality": "high"
    }
})

job_id = response.json()["job_id"]

# Poll for completion
while True:
    status = requests.get(f"http://localhost:8000/api/v1/jobs/{job_id}").json()
    if status["status"] in ["completed", "failed"]:
        break
    time.sleep(1)

print(f"Job {status['status']}: {status.get('result', status.get('error'))}")
```

See `examples/06_api_client.py` for complete examples.

## Configuration

Configuration files use YAML format. The system applies defaults based on detected hardware.

### Example Custom Configuration

```yaml
# config/custom.yaml
voice:
  xtts:
    precision: fp16  # fp16 or fp32
    batch_size: 2
    temperature: 0.7

avatar:
  sdxl:
    precision: fp16
    num_inference_steps: 40
    guidance_scale: 7.5

video:
  musetalk:
    precision: fp16
    fps: 25
  max_duration_seconds: 120

storage:
  voice_profiles: "data/voices"
  avatar_assets: "data/avatars"
  output: "output"
```

Load custom config with `--config` flag:

```bash
avatar status --config config/custom.yaml
```

## Troubleshooting

> **Installation problems?** See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for pip/TTS/Python issues.
> **Deeper understanding?** See [LESSONS_LEARNED.md](LESSONS_LEARNED.md) for root causes and prevention.

### Out of Memory Errors

**Problem**: CUDA out of memory during model loading.

**Solution**:
1. Use fp16 precision: Set `precision: fp16` in config
2. Reduce batch sizes: Lower `batch_size` values
3. Close other GPU applications
4. Use lower quality presets: `--quality medium` or `--quality low`

### Slow Performance

**Problem**: Video generation is very slow.

**Solution**:
1. Check GPU utilization: `nvidia-smi`
2. Ensure CUDA is properly installed: `avatar status`
3. Use quality presets: `--quality low` for faster processing
4. Reduce inference steps in config

### Voice Cloning Quality Issues

**Problem**: Cloned voice doesn't sound like reference.

**Solution**:
1. Use longer reference audio (6+ seconds recommended)
2. Ensure clean audio without background noise
3. Use consistent audio format (16kHz, mono recommended)
4. Try different temperature values (0.5-0.9)

### Lip-Sync Accuracy Issues

**Problem**: Lips don't match audio well.

**Solution**:
1. Use frontal face images with clear, visible mouth
2. Ensure good image quality and lighting
3. Validate face detection: `avatar avatar detect image.png`
4. Try higher FPS: `--fps 30`

### Model Download Issues

**Problem**: Models fail to download or load.

**Solution**:
1. Check internet connection
2. Manually download models:
   - XTTS-v2: https://huggingface.co/coqui/XTTS-v2
   - SDXL: https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
3. Place in Hugging Face cache: `~/.cache/huggingface/`

## Development

### Setup Development Environment

> **Important:** Follow the [Installation Guide](INSTALLATION_GUIDE.md) first.
> Do NOT run `pip install -e ".[dev]"` directly - it will trigger TTS
> dependency resolution and hang for 10+ minutes.

```bash
# Use the automated installer (recommended)
bash scripts/install.sh

# Then add dev tools
pip install black ruff mypy

# Run tests
pytest tests/ -v

# Format code
black src/
ruff check src/

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_voice.py

# Run with verbose output
pytest -v
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make changes with proper type hints and docstrings
4. Add tests for new functionality
5. Run tests and linting: `pytest && black . && ruff check .`
6. Commit changes: `git commit -m "Add feature: description"`
7. Push to fork: `git push origin feature/my-feature`
8. Create Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with amazing open-source projects:

- **[Coqui TTS](https://github.com/coqui-ai/TTS)** - Voice cloning and text-to-speech (XTTS-v2)
- **[Stable Diffusion XL](https://github.com/Stability-AI/generative-models)** - High-quality avatar image generation
- **[MuseTalk](https://github.com/TMElyralab/MuseTalk)** - Audio-driven facial animation and lip-sync
- **[MediaPipe](https://github.com/google/mediapipe)** - Real-time face detection and landmark tracking
- **[PyTorch](https://pytorch.org/)** - Deep learning framework
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework
- **[FFmpeg](https://ffmpeg.org/)** - Video encoding and processing

## Citation

If you use this project in your research or production, please cite:

```bibtex
@software{avatar_pipeline_2024,
  title = {Avatar Pipeline: Open-Source AI Avatar Video Generation},
  author = {Avatar Pipeline Contributors},
  year = {2024},
  url = {https://github.com/avatar-pipeline/avatar-pipeline}
}
```

## Support

- **Documentation**: See `docs/` directory
- **Issues**: [GitHub Issues](https://github.com/avatar-pipeline/avatar-pipeline/issues)
- **Discussions**: [GitHub Discussions](https://github.com/avatar-pipeline/avatar-pipeline/discussions)

## Roadmap

- [x] Voice cloning and synthesis (M1-M2)
- [x] Avatar generation and face detection (M3)
- [x] Lip-sync video generation (M4)
- [x] Pipeline orchestration (M5)
- [x] REST API and job queue (M5)
- [ ] Batch processing for multiple videos
- [ ] Real-time streaming mode
- [ ] Advanced facial expressions control
- [ ] Multi-language subtitle generation
- [ ] Cloud deployment templates (Docker, Kubernetes)
- [ ] Web UI frontend
- [ ] Video editing and post-processing tools

## FAQ

**Q: What GPU do I need?**
A: Minimum 8GB VRAM (e.g., RTX 3060 12GB, RTX 3070). Recommended: RTX 3080 10GB or better.

**Q: Can I run this on CPU only?**
A: Yes, but it will be very slow (10-100x slower). GPU is strongly recommended.

**Q: How long does it take to generate a video?**
A: On RTX 3080: ~30-60 seconds for a 10-second video, depending on quality settings.

**Q: Can I use my own trained voice model?**
A: Currently, the system uses XTTS-v2 for voice cloning. Custom model support is planned.

**Q: Is this safe for production use?**
A: The project is in alpha (v0.1.0). Expect bugs and API changes. Not recommended for production without thorough testing.

**Q: Can I generate videos in languages other than English?**
A: Yes! XTTS-v2 supports 17 languages. Lip-sync is language-agnostic.
