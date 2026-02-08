# Avatar Pipeline Examples

This directory contains example scripts demonstrating how to use the Avatar Pipeline programmatically.

## Prerequisites

Make sure you have:
1. Installed the avatar-pipeline package: `pip install -e .`
2. A CUDA-compatible GPU with 8GB+ VRAM (or CPU for slower processing)
3. Models will be downloaded automatically on first run

## Examples Overview

### 01_voice_cloning.py
Clone a voice from reference audio and save the profile.

```bash
python examples/01_voice_cloning.py
```

**What it demonstrates:**
- Loading configuration
- Initializing VRAM manager
- Voice profile management
- XTTS-v2 voice cloning
- Error handling

### 02_text_to_speech.py
Generate speech from text using a cloned voice profile.

```bash
python examples/02_text_to_speech.py
```

**What it demonstrates:**
- Loading voice profiles
- Coqui TTS synthesis
- Audio output handling
- Processing time metrics

### 03_avatar_generation.py
Generate an avatar image from a text prompt using SDXL.

```bash
python examples/03_avatar_generation.py
```

**What it demonstrates:**
- SDXL avatar generation
- Face detection with MediaPipe
- Avatar profile management
- Image quality settings

### 04_lipsync_video.py
Create a lip-synced video from an image and audio file.

```bash
python examples/04_lipsync_video.py
```

**What it demonstrates:**
- MuseTalk lip-sync
- Video encoding with FFmpeg
- Quality presets
- Frame rate configuration

### 05_full_pipeline.py
Execute the complete pipeline from text to final video.

```bash
python examples/05_full_pipeline.py
```

**What it demonstrates:**
- Pipeline coordinator usage
- Sequential model loading
- End-to-end workflow
- Intermediate file management

### 06_api_client.py
Interact with the REST API server programmatically.

```bash
# First, start the server in another terminal:
avatar server start

# Then run the example:
python examples/06_api_client.py
```

**What it demonstrates:**
- API job submission
- Job status polling
- Error handling
- Result retrieval

## Modifying Examples

All examples are self-contained and can be easily modified:

1. **Change paths**: Update input/output file paths
2. **Adjust quality**: Modify quality presets and parameters
3. **Custom config**: Load your own config file
4. **Error handling**: Examples show proper error handling patterns

## Common Parameters

### Voice Module
- `audio_file`: Path to reference audio (3+ seconds, WAV/MP3)
- `name`: Human-readable voice profile name
- `language`: Language code (en, es, fr, de, etc.)
- `temperature`: Speech variation (0.1-1.0)

### Avatar Module
- `prompt`: Text description of desired avatar
- `aspect_ratio`: Image size ("16:9", "9:16", "1:1")
- `seed`: Random seed for reproducibility
- `negative_prompt`: Things to avoid in generation

### Video Module
- `avatar_image`: Path to image with visible face
- `audio_file`: Path to audio file for lip-sync
- `quality`: Video quality preset ("high", "medium", "low")
- `fps`: Frames per second (15-30)

### Pipeline
- `text`: Text to convert to speech
- `voice_profile_id`: Voice profile to use
- `avatar_image`: Avatar image for video
- `output_path`: Where to save final video
- `cleanup_intermediates`: Remove temp files (True/False)

## Troubleshooting

### Out of Memory
If you get CUDA OOM errors:
- Use fp16 precision in config
- Reduce batch sizes
- Close other GPU applications
- Try lower quality presets

### Model Downloads
Models download automatically to `~/.cache/huggingface/`. This can take time on first run:
- XTTS-v2: ~2GB
- SDXL: ~7GB
- MuseTalk: ~3GB

### File Not Found
Make sure to:
- Create necessary directories: `mkdir -p storage output`
- Use absolute paths or paths relative to project root
- Check file permissions

## Next Steps

After running examples:
1. Try modifying parameters to see effects
2. Use your own reference audio and images
3. Explore the CLI: `avatar --help`
4. Read the full documentation in `docs/`

## Need Help?

- Check the main [README.md](../README.md) for installation
- See [Troubleshooting](../README.md#troubleshooting) section
- Open an issue on GitHub
