# Avatar Module

Avatar image generation using SDXL 1.5 and face detection using MediaPipe.

## Overview

The avatar module provides two main capabilities:

1. **Avatar Generation**: Generates photorealistic portrait images using Stable Diffusion XL
2. **Face Detection**: Detects and validates faces for lip-sync compatibility using MediaPipe

## Components

### Interfaces (`interfaces.py`)

Defines abstract base classes and data structures:

- `AvatarProfile`: Avatar profile metadata
- `GenerationResult`: Result of avatar generation
- `FaceDetectionResult`: Result of face detection
- `AvatarGeneratorInterface`: Interface for avatar generation
- `FaceDetectorInterface`: Interface for face detection

### Generator (`generator.py`)

`SDXLAvatarGenerator`: SDXL 1.5-based avatar generation.

**Features:**
- Multiple aspect ratios (16:9, 9:16, 1:1)
- FP16 precision for memory efficiency
- VRAM-aware model loading
- Automatic face detection
- Reproducible generation via seeds

**Usage:**

```python
from src.avatar import SDXLAvatarGenerator, AvatarProfileManager
from src.utils import VRAMManager
from src.config import load_config

# Initialize
config = load_config()
vram_manager = VRAMManager()
profile_manager = AvatarProfileManager(Path("storage"))
generator = SDXLAvatarGenerator(
    config=config["avatar"]["sdxl"],
    vram_manager=vram_manager,
    profile_manager=profile_manager,
)

# Generate avatar
result = generator.generate(
    prompt="professional businessman in suit, studio lighting",
    aspect_ratio="16:9",
    seed=42,
)

if result.success:
    print(f"Profile: {result.profile.profile_id}")
    print(f"Image: {result.profile.base_image_path}")
```

### Detector (`detector.py`)

`MediaPipeFaceDetector`: MediaPipe-based face detection and validation.

**Features:**
- Robust face detection
- Key landmark extraction (eyes, nose, mouth)
- Lip-sync suitability validation
- Optional detailed face mesh (468 landmarks)

**Usage:**

```python
from src.avatar import MediaPipeFaceDetector
from pathlib import Path

# Initialize
detector = MediaPipeFaceDetector()

# Detect face
result = detector.detect(Path("avatar.png"))

if result.detected:
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Region: {result.face_region}")

    # Validate for lip-sync
    is_valid, message = detector.validate_for_lipsync(result)
    print(f"Valid for lip-sync: {is_valid}")
    print(f"Message: {message}")
```

### Profile Manager (`profiles.py`)

`AvatarProfileManager`: Avatar profile storage and retrieval.

**Storage Structure:**
```
storage/avatars/{profile_id}/
├── avatar.png       # Generated avatar image
└── metadata.json    # Profile metadata
```

## CLI Commands

### Generate Avatar

```bash
avatar avatar generate "professional businessman in suit" \
    --aspect 16:9 \
    --seed 42 \
    --output avatar.png
```

Options:
- `--aspect`: Aspect ratio (16:9, 9:16, 1:1)
- `--seed`: Random seed for reproducibility
- `--output`: Output image path (optional)
- `--negative`: Negative prompt (things to avoid)
- `--storage`: Storage directory (default: storage)
- `--config`: Config file path

### Detect Face

```bash
avatar avatar detect avatar.png --verbose
```

Options:
- `--verbose`, `-v`: Show detailed detection information

### List Avatar Profiles

```bash
avatar avatar list --storage storage
```

## Configuration

Configuration is in `config.yaml` or uses hardware-specific defaults:

```yaml
avatar:
  sdxl:
    model_id: stabilityai/stable-diffusion-xl-base-1.0
    precision: fp16
    num_inference_steps: 40  # Higher = better quality, slower
    guidance_scale: 7.5      # Higher = more prompt adherence
```

## VRAM Requirements

| Model | VRAM (FP16) | Notes |
|-------|-------------|-------|
| SDXL Base | ~7 GB | Main generation model |
| MediaPipe | ~50 MB | Face detection (CPU/GPU) |

## Aspect Ratios

| Ratio | Resolution | Use Case |
|-------|------------|----------|
| 16:9 | 1344x768 | Landscape, YouTube horizontal |
| 9:16 | 768x1344 | Portrait, TikTok/Shorts |
| 1:1 | 1024x1024 | Square, Instagram |

## Tips for Better Results

### Prompts

**Good:**
- "professional businessman in suit, studio lighting, 8k, detailed face"
- "young woman with long hair, natural lighting, photorealistic"
- "elderly man with glasses, warm lighting, detailed portrait"

**Avoid:**
- Vague descriptions ("a person")
- Multiple people ("two friends")
- Complex poses (stick to frontal portraits)

### Negative Prompts

Default negative prompt avoids common issues, but you can customize:

```bash
avatar avatar generate "portrait" \
    --negative "blurry, low quality, multiple people, profile view"
```

### Face Detection

For best lip-sync compatibility:
- Use frontal faces (not profile/side view)
- Ensure good lighting
- Avoid extreme angles (<15° tilt)
- Minimum face size: 128x128 pixels

## Error Handling

All operations return result objects with success status:

```python
result = generator.generate(...)

if result.success:
    profile = result.profile
    # Use profile
else:
    error = result.error
    # Handle error
    print(f"Generation failed: {error}")
```

## Integration with Pipeline

Avatar module integrates with other pipeline components:

1. **Generate avatar** → Avatar Module
2. **Synthesize speech** → Voice Module
3. **Generate lip-sync video** → Video Module (MuseTalk)

Example full pipeline:

```python
# 1. Generate avatar
avatar_result = generator.generate("professional woman")
avatar_profile = avatar_result.profile

# 2. Synthesize speech
speech_result = synthesizer.synthesize("Hello", voice_profile)

# 3. Generate lip-sync video (future)
# video_result = lipsync.generate(avatar_profile, speech_result.audio_path)
```

## Development

### Adding New Generators

Implement `AvatarGeneratorInterface`:

```python
class CustomGenerator(AvatarGeneratorInterface):
    def generate(self, prompt, ...) -> GenerationResult:
        # Your implementation
        pass

    def get_supported_aspect_ratios(self) -> list[str]:
        return ["16:9", "1:1"]
```

### Adding New Detectors

Implement `FaceDetectorInterface`:

```python
class CustomDetector(FaceDetectorInterface):
    def detect(self, image_path) -> FaceDetectionResult:
        # Your implementation
        pass

    def validate_for_lipsync(self, detection) -> tuple[bool, str]:
        # Your validation logic
        pass
```

## Testing

```bash
# Run avatar module tests
pytest tests/test_avatar.py -v

# With coverage
pytest tests/test_avatar.py --cov=src.avatar
```

## Troubleshooting

### Out of VRAM

Reduce inference steps in config:

```yaml
avatar:
  sdxl:
    num_inference_steps: 25  # Reduce from 40
```

### Slow Generation (CPU)

SDXL is very slow on CPU. GPU strongly recommended.

### Face Not Detected

- Try different prompts emphasizing frontal view
- Ensure prompt includes "looking at camera", "frontal view"
- Check generated image quality

### Invalid for Lip-Sync

Common reasons:
- Face too small: Regenerate with closer crop
- Face tilted: Use "straight pose, frontal view" in prompt
- Multiple faces: Add "single person" to prompt
- Profile view: Add "looking at camera, frontal view"

## License

MIT License - see LICENSE file for details.
