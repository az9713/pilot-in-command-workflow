# Avatar CLI Command Reference

Quick reference for avatar module CLI commands.

## Command: avatar generate

Generate avatar image from text prompt.

### Syntax

```bash
avatar avatar generate PROMPT [OPTIONS]
```

### Arguments

- `PROMPT` - Text description of desired avatar (required)

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--output` | PATH | Auto | Output image file path |
| `--aspect` | CHOICE | 16:9 | Aspect ratio: 16:9, 9:16, 1:1 |
| `--seed` | INT | Random | Random seed for reproducibility |
| `--negative` | TEXT | Default | Negative prompt (things to avoid) |
| `--storage` | PATH | storage | Storage directory for profiles |
| `--config`, `-c` | PATH | None | Path to config YAML file |

### Examples

**Basic generation:**
```bash
avatar avatar generate "professional businessman in suit"
```

**Landscape format with seed:**
```bash
avatar avatar generate "young woman, studio lighting" \
    --aspect 16:9 \
    --seed 42
```

**Portrait format for mobile:**
```bash
avatar avatar generate "elderly man with glasses" \
    --aspect 9:16 \
    --output portraits/grandfather.png
```

**Square format for social media:**
```bash
avatar avatar generate "teenage girl, casual style" \
    --aspect 1:1 \
    --seed 123
```

**With negative prompt:**
```bash
avatar avatar generate "professional portrait" \
    --negative "blurry, low quality, multiple people, sunglasses"
```

### Output

On success:
```
Generating avatar: professional businessman in suit
Aspect ratio: 16:9

Success! Avatar generated in 42.15s
Profile ID: ap-a1b2c3d4
Image: storage/avatars/ap-a1b2c3d4/avatar.png
Storage: storage/avatars/ap-a1b2c3d4
Face detected: Yes (confidence: 0.95)
```

On error:
```
Error: Insufficient VRAM: need 7168MB for SDXL
```

### Notes

- Generation time: 30-60 seconds on RTX 3080
- VRAM requirement: ~7GB (FP16)
- Automatic face detection included
- Profile created automatically on success

---

## Command: avatar detect

Detect and validate face in image.

### Syntax

```bash
avatar avatar detect IMAGE [OPTIONS]
```

### Arguments

- `IMAGE` - Path to image file (required)

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose`, `-v` | FLAG | False | Show detailed detection information |

### Examples

**Basic detection:**
```bash
avatar avatar detect image.png
```

**Detailed output:**
```bash
avatar avatar detect avatar.png --verbose
```

### Output

**Basic output:**
```
Detecting face in: image.png

============================================================
Face Detection Results
============================================================
Detected: Yes
Confidence: 0.95

Face Region:
  X: 234
  Y: 156
  Width: 512
  Height: 640

Lip-Sync Validation:
  Status: Valid
  Message: Face is suitable for lip-sync (confidence: 0.95)
============================================================
```

**Verbose output (adds):**
```
Key Landmarks:
  right_eye: (312, 245)
  left_eye: (456, 248)
  nose_tip: (384, 356)
  mouth_center: (384, 445)
  right_ear: (245, 289)
  left_ear: (523, 292)
```

**If invalid:**
```
Lip-Sync Validation:
  Status: Invalid
  Reason: Face is tilted: 18.5° (maximum: 15°)
```

### Exit Codes

- `0` - Success (face detected)
- `1` - Error or no face detected

---

## Command: avatar list

List all avatar profiles.

### Syntax

```bash
avatar avatar list [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--storage` | PATH | storage | Storage directory for profiles |

### Examples

**Default storage:**
```bash
avatar avatar list
```

**Custom storage:**
```bash
avatar avatar list --storage /path/to/storage
```

### Output

**With profiles:**
```
Found 3 avatar profile(s):

======================================================================
Profile ID:   ap-a1b2c3d4
Name:         professional businessman
Aspect Ratio: 16:9
Face Region:  512x640
Created:      2024-01-15T10:30:45Z
Image:        storage/avatars/ap-a1b2c3d4/avatar.png
Face:         Detected (confidence: 0.95)
----------------------------------------------------------------------
Profile ID:   ap-e5f6g7h8
Name:         young woman studio
Aspect Ratio: 9:16
Face Region:  448x672
Created:      2024-01-15T11:15:23Z
Image:        storage/avatars/ap-e5f6g7h8/avatar.png
Face:         Not detected
----------------------------------------------------------------------
Profile ID:   ap-i9j0k1l2
Name:         elderly man glasses
Aspect Ratio: 1:1
Face Region:  720x900
Created:      2024-01-15T12:00:01Z
Image:        storage/avatars/ap-i9j0k1l2/avatar.png
Face:         Detected (confidence: 0.88)
----------------------------------------------------------------------
```

**No profiles:**
```
No avatar profiles found.
Storage directory: storage/avatars
```

---

## Global Options

Available for all avatar commands:

| Option | Description |
|--------|-------------|
| `--help` | Show command help |
| `--version` | Show version information |

### Examples

```bash
avatar avatar generate --help
avatar avatar detect --help
avatar avatar list --help
```

---

## Aspect Ratios

| Ratio | Resolution | Use Case |
|-------|------------|----------|
| 16:9 | 1344×768 | Landscape, YouTube horizontal |
| 9:16 | 768×1344 | Portrait, TikTok/Instagram Reels |
| 1:1 | 1024×1024 | Square, Instagram feed |

---

## Prompt Tips

### Good Prompts

- **Specific**: "professional businessman in navy suit, white shirt"
- **Quality modifiers**: "studio lighting, 8k, detailed face"
- **Style**: "photorealistic portrait, natural skin texture"
- **Age/gender**: "middle-aged woman", "young man"

### Avoid

- **Vague**: "a person", "someone"
- **Multiple people**: "two friends", "group photo"
- **Complex poses**: "jumping", "dancing"
- **Side views**: "profile view" (use "frontal view, looking at camera")

### Default Enhancement

The system automatically adds quality modifiers:
```
User prompt: "businessman in suit"
Actual prompt: "professional portrait, businessman in suit, high quality, detailed face, studio lighting, 8k"
```

---

## Negative Prompts

Default negative prompt (used if none specified):
```
blurry, low quality, distorted, deformed, ugly, bad anatomy,
disfigured, poorly drawn face, mutation, extra limbs,
low resolution, watermark, text, multiple people
```

Custom negative prompts replace the default:
```bash
avatar avatar generate "portrait" \
    --negative "glasses, hat, profile view, tilted head"
```

---

## Error Messages

### Common Errors

**Insufficient VRAM:**
```
Error: Insufficient VRAM: need 7168MB for SDXL
```
Solution: Close other applications or reduce `num_inference_steps` in config

**No face detected:**
```
Face detected: No (manual validation recommended)
```
Solution: Regenerate with "frontal view, looking at camera" in prompt

**Invalid for lip-sync:**
```
Reason: Face too small: 64x80 (minimum: 128x128)
```
Solution: Regenerate or use higher resolution

**Model download:**
```
Downloading: 100%|████████████| 6.94G/6.94G [05:23<00:00, 21.4MB/s]
```
Note: First run downloads ~7GB SDXL model

---

## Configuration

Override defaults in `config.yaml`:

```yaml
avatar:
  sdxl:
    model_id: stabilityai/stable-diffusion-xl-base-1.0
    precision: fp16
    num_inference_steps: 40  # Higher = better quality, slower
    guidance_scale: 7.5      # Higher = more prompt adherence
```

Performance vs Quality:

| Profile | Steps | Time (RTX 3080) | Quality |
|---------|-------|-----------------|---------|
| Low | 25 | ~30s | Good |
| Medium | 40 | ~45s | Better |
| High | 50 | ~60s | Best |

---

## Storage Structure

```
storage/avatars/
├── ap-a1b2c3d4/
│   ├── avatar.png       # Generated image
│   └── metadata.json    # Profile metadata
├── ap-e5f6g7h8/
│   ├── avatar.png
│   └── metadata.json
└── ...
```

### Metadata Format

```json
{
  "profile_id": "ap-a1b2c3d4",
  "name": "professional businessman",
  "aspect_ratio": "16:9",
  "face_region": {"x": 234, "y": 156, "width": 512, "height": 640},
  "created_at": "2024-01-15T10:30:45Z",
  "source_image": "temp_avatar_20240115_103045.png",
  "generation": {
    "prompt": "professional portrait, businessman in suit, ...",
    "negative_prompt": "blurry, low quality, ...",
    "seed": 42,
    "width": 1344,
    "height": 768,
    "steps": 40,
    "guidance_scale": 7.5,
    "face_detected": true,
    "face_confidence": 0.95
  }
}
```

---

## Integration with Pipeline

### Step 1: Generate Avatar

```bash
avatar avatar generate "professional woman, business attire" \
    --aspect 16:9 \
    --seed 42 \
    --output avatar.png
```

Output: Profile ID `ap-a1b2c3d4`

### Step 2: Verify Face

```bash
avatar avatar detect storage/avatars/ap-a1b2c3d4/avatar.png -v
```

Confirms: Valid for lip-sync

### Step 3: Use in Video Pipeline

```bash
# Clone voice
avatar voice clone audio.wav --name "Professional"
# Output: Profile ID vp-x1y2z3w4

# Generate video (future)
avatar video generate \
    --avatar ap-a1b2c3d4 \
    --voice vp-x1y2z3w4 \
    --text "Welcome to our presentation"
```

---

## Performance Notes

### RTX 3080 (10GB VRAM)

- Generation: 30-60s depending on steps
- Face detection: <1s
- Memory: ~7GB VRAM + 2GB overhead

### RTX 4090 (24GB VRAM)

- Generation: 20-40s (same steps, faster GPU)
- Can run higher steps (50-75) for better quality

### Low VRAM (8GB)

- Reduce `num_inference_steps` to 25
- May need to close other applications
- Generation: 25-45s

### CPU Mode

- Not recommended (extremely slow)
- Generation: 10-30 minutes
- Face detection: Still fast (~1s)

---

## See Also

- [Avatar Module README](../src/avatar/README.md) - Detailed module documentation
- [User Guide](USER_GUIDE.md) - Complete pipeline guide
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
