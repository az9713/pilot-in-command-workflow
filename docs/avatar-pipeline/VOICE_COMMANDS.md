# Voice Commands Quick Reference

## Overview

The voice module provides three commands for voice cloning and text-to-speech synthesis.

## Commands

### 1. Clone Voice

Create a voice profile from reference audio.

```bash
avatar voice clone <audio_file> --name <name> [options]
```

**Required Arguments**:
- `audio_file` - Path to WAV/MP3 audio file (3+ seconds)

**Required Options**:
- `--name <name>` - Name for the voice profile

**Optional Options**:
- `--language <code>` - Language code (default: en)
- `--storage <dir>` - Storage directory (default: storage)
- `--config <file>` - Config file path

**Example**:
```bash
avatar voice clone reference.wav --name "John Doe"
avatar voice clone voice.mp3 --name "Jane" --language es
```

**Output**:
```
Cloning voice from: reference.wav
Profile name: John Doe
Language: en

Success! Voice cloned in 8.3s
Profile ID: vp-a1b2c3d4
Storage: storage/voices/vp-a1b2c3d4
```

---

### 2. Synthesize Speech

Generate speech audio from text using a cloned voice.

```bash
avatar voice speak <text> --profile <id> --output <file> [options]
```

**Required Arguments**:
- `text` - Text to synthesize (max 5000 characters)

**Required Options**:
- `--profile <id>` - Voice profile ID or name
- `--output <file>` - Output WAV file path

**Optional Options**:
- `--storage <dir>` - Storage directory (default: storage)
- `--config <file>` - Config file path

**Example**:
```bash
avatar voice speak "Hello, world!" --profile vp-a1b2c3d4 --output hello.wav
avatar voice speak "Hola" --profile "John Doe" --output hola.wav
```

**Output**:
```
Synthesizing: Hello, world!
Profile: vp-a1b2c3d4
Output: hello.wav

Success! Generated 2.3s audio in 3.1s
Saved to: hello.wav
```

---

### 3. List Profiles

Display all available voice profiles.

```bash
avatar voice list [options]
```

**Optional Options**:
- `--storage <dir>` - Storage directory (default: storage)

**Example**:
```bash
avatar voice list
```

**Output**:
```
Found 2 voice profile(s):

======================================================================
Profile ID:   vp-a1b2c3d4
Name:         John Doe
Language:     en
Created:      2026-02-05T10:30:00Z
Storage:      storage/voices/vp-a1b2c3d4
----------------------------------------------------------------------
Profile ID:   vp-e5f6g7h8
Name:         Jane
Language:     es
Created:      2026-02-05T11:15:00Z
Storage:      storage/voices/vp-e5f6g7h8
----------------------------------------------------------------------
```

---

## Supported Languages

The voice module supports 17 languages via XTTS-v2:

| Code | Language |
|------|----------|
| en | English |
| es | Spanish |
| fr | French |
| de | German |
| it | Italian |
| pt | Portuguese |
| pl | Polish |
| tr | Turkish |
| ru | Russian |
| nl | Dutch |
| cs | Czech |
| ar | Arabic |
| zh-cn | Chinese (Simplified) |
| ja | Japanese |
| hu | Hungarian |
| ko | Korean |
| hi | Hindi |

---

## Tips

### Voice Cloning

1. **Audio Quality**: Use clear, noise-free audio
2. **Duration**: 6+ seconds recommended (3s minimum)
3. **Content**: Natural speech with varied intonation
4. **Format**: WAV preferred, but MP3 supported

### Speech Synthesis

1. **Text Length**: Keep under 5000 characters
2. **Long Text**: Split into multiple chunks
3. **Profile Lookup**: Can use either ID or name
4. **Output Format**: Always WAV (22050 Hz, mono)

### Storage Management

1. **Location**: Default is `storage/voices/`
2. **Cleanup**: Manually delete profile directories to free space
3. **Backup**: Copy entire `storage/voices/` directory
4. **Sharing**: Share profile directory (includes embedding + audio)

---

## Workflow Examples

### Basic Workflow

```bash
# 1. Clone a voice
avatar voice clone my_voice.wav --name "My Voice"
# Note the profile ID: vp-abc12345

# 2. Generate speech
avatar voice speak "Hello!" --profile vp-abc12345 --output hello.wav

# 3. Play the result (platform-specific)
# Windows: start hello.wav
# macOS: afplay hello.wav
# Linux: aplay hello.wav
```

### Batch Processing

Clone multiple voices:
```bash
for file in voices/*.wav; do
  name=$(basename "$file" .wav)
  avatar voice clone "$file" --name "$name"
done
```

Generate script audio:
```bash
# Assuming script.txt has one line per utterance
i=0
while IFS= read -r line; do
  avatar voice speak "$line" --profile vp-xxx --output "line_$i.wav"
  ((i++))
done < script.txt
```

### Multi-language Support

```bash
# Clone Spanish voice
avatar voice clone spanish.wav --name "Spanish Voice" --language es

# Generate Spanish speech
avatar voice speak "Hola, mundo!" --profile "Spanish Voice" --output hola.wav
```

---

## Error Messages

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Reference audio not found" | File path incorrect | Check file path |
| "Audio too short: X.Xs" | Audio < 3 seconds | Use longer audio |
| "Unsupported language: X" | Invalid language code | Use supported code |
| "Insufficient VRAM" | Not enough GPU memory | Close other programs |
| "Text too long: X characters" | Text > 5000 chars | Split text into chunks |
| "Profile not found: X" | Invalid profile ID/name | Check `avatar voice list` |

---

## Advanced Usage

### Custom Storage Location

```bash
# Use custom directory
avatar voice clone audio.wav --name "Test" --storage /path/to/storage

# Must use same storage for all commands
avatar voice list --storage /path/to/storage
avatar voice speak "Hi" --profile "Test" --output out.wav --storage /path/to/storage
```

### Custom Configuration

Create `config.yaml`:
```yaml
voice:
  xtts:
    precision: fp16
    batch_size: 2
    temperature: 0.7
  tts:
    precision: fp16
    vocoder_quality: high
```

Use it:
```bash
avatar voice clone audio.wav --name "Test" --config config.yaml
avatar voice speak "Test" --profile "Test" --output out.wav --config config.yaml
```

---

## Performance

### Expected Processing Times (RTX 3080)

| Operation | Input Size | Time |
|-----------|-----------|------|
| Voice cloning | 6s audio | ~8s |
| Speech synthesis | 100 chars | ~3s |
| Speech synthesis | 1000 chars | ~5s |

### VRAM Requirements

| Operation | VRAM Needed |
|-----------|-------------|
| Voice cloning | ~4 GB |
| Speech synthesis | ~3 GB |

**Note**: Models load sequentially. Only one operation at a time.

---

## Troubleshooting

### Command Not Found

```bash
# Install package
pip install -e .

# Or run directly
python -m src.cli voice --help
```

### Module Import Errors

```bash
# Install dependencies
pip install torch torchaudio TTS click pyyaml
```

### CUDA/VRAM Issues

```bash
# Check GPU status
avatar status

# Use CPU mode (slower but works)
# No special flag needed - auto-detected
```

### Audio Format Issues

```bash
# Convert to WAV first (using ffmpeg)
ffmpeg -i input.mp3 -ar 22050 -ac 1 output.wav
avatar voice clone output.wav --name "Test"
```

---

## Getting Help

```bash
# General help
avatar voice --help

# Command-specific help
avatar voice clone --help
avatar voice speak --help
avatar voice list --help

# System status
avatar status
```
