# Configuration Templates

This directory contains configuration templates for different hardware profiles and use cases.

## Available Templates

### pipeline.yaml (Default)
Balanced configuration that auto-detects hardware and applies appropriate defaults.
- Use this for most cases
- System automatically adjusts based on GPU

### pipeline.rtx4090.yaml (High-End)
Optimized for RTX 4090 and similar high-end GPUs (20GB+ VRAM).
- Full fp32 precision for maximum quality
- Parallel model loading
- Higher inference steps
- Larger batch sizes

### pipeline.rtx3080.yaml (Target Spec)
Optimized for RTX 3080 10GB (project target hardware).
- fp16 precision for VRAM efficiency
- Sequential model loading
- Balanced quality/performance
- Default for 8-20GB VRAM GPUs

### pipeline.low_vram.yaml (Low VRAM)
For GPUs with less than 8GB VRAM.
- Aggressive fp16 precision
- Reduced inference steps
- Smaller batch sizes
- CPU fallback for some operations

## Using Custom Configuration

### Command Line
```bash
# Use specific config file
avatar status --config config/pipeline.rtx3080.yaml

# Apply to any command
avatar voice clone audio.wav --name "Voice" --config config/custom.yaml
avatar pipeline run "Text" --voice "Voice" --avatar img.png --output video.mp4 \
  --config config/pipeline.rtx4090.yaml
```

### Python API
```python
from src.config import load_config

# Load specific config
config = load_config("config/pipeline.rtx3080.yaml")

# Use in components
from src.voice import XTTSVoiceCloner
cloner = XTTSVoiceCloner(config=config["voice"]["xtts"])
```

## Configuration Options

### Voice Settings

```yaml
voice:
  xtts:
    precision: fp16          # fp16 or fp32
    batch_size: 2            # Higher = faster but more VRAM
    temperature: 0.7         # 0.1-1.0, higher = more variation

  tts:
    precision: fp16          # fp16 or fp32
    vocoder_quality: medium  # low, medium, high
```

**Precision Impact:**
- fp32: Better quality, 2x VRAM usage
- fp16: Good quality, 2x less VRAM

**Temperature:**
- 0.5: More consistent, robotic
- 0.7: Balanced (recommended)
- 0.9: More variation, natural

### Avatar Settings

```yaml
avatar:
  sdxl:
    precision: fp16              # fp16 or fp32
    num_inference_steps: 40      # 20-50, higher = better quality
    guidance_scale: 7.5          # 5-15, higher = follows prompt more
```

**Inference Steps:**
- 20: Fast, lower quality
- 40: Balanced (recommended)
- 50: Slow, best quality

**Guidance Scale:**
- 5.0: More creative/varied
- 7.5: Balanced (recommended)
- 12.0: Strict prompt adherence

### Video Settings

```yaml
video:
  musetalk:
    precision: fp16          # fp16 or fp32
    fps: 25                  # 15-30 fps

  max_duration_seconds: 120  # Maximum video length
```

**FPS Recommendations:**
- 15: Fast generation, acceptable quality
- 25: Balanced (recommended)
- 30: Smooth, slower generation

### Storage Paths

```yaml
storage:
  voice_profiles: "data/voice_profiles"    # Voice embeddings
  avatar_assets: "data/avatar_assets"      # Avatar images
  job_state: "data/jobs"                   # Job queue state
  output: "output"                         # Default output directory
```

All paths are relative to project root or can be absolute.

### API Settings

```yaml
api:
  host: "0.0.0.0"              # Server bind address
  port: 8000                    # Server port
  workers: 1                    # Number of worker processes

  cors:
    allow_origins: ["*"]        # CORS allowed origins
    allow_methods: ["*"]        # Allowed HTTP methods
    allow_headers: ["*"]        # Allowed headers
```

**Production Notes:**
- Use specific CORS origins in production
- Consider reverse proxy (nginx) for SSL
- Set workers based on CPU cores

### Logging

```yaml
logging:
  level: "INFO"                 # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## Creating Custom Configurations

### Start from Template
```bash
# Copy a template
cp config/pipeline.rtx3080.yaml config/my_config.yaml

# Edit for your needs
nano config/my_config.yaml

# Test it
avatar status --config config/my_config.yaml
```

### Override Specific Values
You don't need to specify all values. The system merges your config with defaults:

```yaml
# config/fast_generation.yaml
# Only override what you need
avatar:
  sdxl:
    num_inference_steps: 20    # Faster generation

video:
  musetalk:
    fps: 15                    # Faster video
```

### Environment-Specific Configs
```bash
# Development
config/dev.yaml
  - Debug logging
  - Keep intermediate files
  - Fast generation for testing

# Production
config/prod.yaml
  - Info logging
  - Clean intermediates
  - High quality
  - Optimized settings
```

## Hardware-Specific Tips

### RTX 4090 / 4080 (20GB+)
```yaml
voice:
  xtts:
    precision: fp32        # Can afford full precision
    batch_size: 4          # Larger batches

avatar:
  sdxl:
    precision: fp32        # Maximum quality
    num_inference_steps: 50

video:
  musetalk:
    precision: fp32
    fps: 30
```

### RTX 3080 / 3090 (10-12GB)
Use `pipeline.rtx3080.yaml` as-is or:
```yaml
voice:
  xtts:
    precision: fp16        # Required for VRAM
    batch_size: 2

avatar:
  sdxl:
    precision: fp16
    num_inference_steps: 40

video:
  musetalk:
    precision: fp16
    fps: 25
```

### RTX 3060 / 3070 (8GB)
```yaml
voice:
  xtts:
    precision: fp16
    batch_size: 1          # Reduce batch size

avatar:
  sdxl:
    precision: fp16
    num_inference_steps: 30  # Fewer steps

video:
  musetalk:
    precision: fp16
    fps: 20
```

### Low VRAM (<8GB)
Use `pipeline.low_vram.yaml` or consider:
- Closing other GPU applications
- Using CPU mode (very slow)
- Upgrading GPU

## Validation

Test your configuration:

```bash
# Check if config loads
avatar status --config config/my_config.yaml --verbose

# Try a quick test
avatar voice speak "Test" --profile test --output test.wav \
  --config config/my_config.yaml
```

## Troubleshooting

### Out of Memory Errors
1. Use fp16 precision everywhere
2. Reduce batch_size to 1
3. Lower num_inference_steps
4. Reduce fps

### Slow Performance
1. Check precision isn't fp32 unnecessarily
2. Increase batch_size if VRAM allows
3. Reduce num_inference_steps
4. Lower fps

### Quality Issues
1. Increase num_inference_steps
2. Use fp32 if VRAM allows
3. Adjust temperature for voice
4. Increase fps for video

## Reference

For complete option reference, see:
- Default values: `src/config/settings.py`
- Hardware detection: `src/config/hardware.py`
- Main documentation: `README.md`
