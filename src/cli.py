"""
CLI entry point for avatar pipeline.

Provides command-line interface for system status, configuration,
and pipeline execution.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .config import detect_gpu, get_hardware_profile, load_config
from .utils import VRAMManager
from .voice import (
    VoiceProfileManager,
    XTTSVoiceCloner,
    CoquiTTSSynthesizer,
)
from .avatar import (
    AvatarProfileManager,
    SDXLAvatarGenerator,
    MediaPipeFaceDetector,
)
from .video import (
    MuseTalkLipSync,
    FFmpegEncoder,
    LipSyncConfig,
)
from .orchestration import (
    PipelineCoordinator,
    PipelineConfig,
    JobQueue,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version="0.1.0", prog_name="avatar")
def main():
    """
    Avatar Pipeline - Open-source AI avatar video generation.

    Generate avatar videos with voice cloning, TTS, and lip-sync.
    Optimized for RTX 3080 (10GB VRAM).
    """
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed configuration",
)
def status(config: Path, verbose: bool):
    """
    Show system status (GPU, VRAM, configuration).

    Displays hardware information, VRAM usage, and active configuration
    profile. Use --verbose to see full config values.
    """
    try:
        click.echo("=" * 60)
        click.echo("Avatar Pipeline - System Status")
        click.echo("=" * 60)

        # GPU Detection
        click.echo("\n[GPU Information]")
        gpu_info = detect_gpu()

        if gpu_info["cuda_available"]:
            click.echo(f"  Device: {gpu_info['name']}")
            click.echo(f"  CUDA Available: Yes")
            click.echo(f"  Device ID: {gpu_info['device_id']}")
            click.echo(f"  Total VRAM: {gpu_info['vram_total']:,} MB")
            click.echo(f"  Free VRAM: {gpu_info['vram_free']:,} MB")

            # VRAM Status
            vram_manager = VRAMManager(device_id=gpu_info["device_id"])
            vram_status = vram_manager.get_status()
            click.echo(f"  VRAM Usage: {vram_status.utilization_percent:.1f}%")
        else:
            click.echo(f"  Device: {gpu_info['name']}")
            click.echo(f"  CUDA Available: No")
            click.echo(f"  Note: Running in CPU mode")

        # Hardware Profile
        click.echo("\n[Hardware Profile]")
        profile = get_hardware_profile()
        click.echo(f"  Profile: {profile}")

        profile_descriptions = {
            "rtx4090": "High-end (20GB+ VRAM) - Full quality, parallel models",
            "rtx3080": "Target spec (8-20GB VRAM) - Sequential loading",
            "low_vram": "Low VRAM (<8GB) - Reduced quality/features",
        }
        click.echo(f"  Description: {profile_descriptions.get(profile, 'Unknown')}")

        # Configuration
        click.echo("\n[Configuration]")
        try:
            cfg = load_config(config)
            click.echo(f"  Config Source: {'User file' if config else 'Defaults'}")
            if config:
                click.echo(f"  Config Path: {config}")
            click.echo(f"  Active Profile: {cfg.get('hardware_profile', 'unknown')}")

            if verbose:
                click.echo("\n[Detailed Configuration]")
                _print_config(cfg, indent=2)

        except Exception as e:
            click.echo(f"  Error loading config: {e}", err=True)

        # Model Compatibility
        click.echo("\n[Model Compatibility]")
        if gpu_info["cuda_available"]:
            vram_mb = gpu_info["vram_total"]

            # Estimated VRAM requirements
            models = {
                "XTTS-v2 (Voice Clone)": 4096,
                "Coqui TTS (Speech)": 3072,
                "SDXL 1.5 (Avatar)": 7168,
                "MuseTalk (Lip-Sync)": 5120,
            }

            for model_name, required_mb in models.items():
                can_run = vram_mb >= required_mb
                status_icon = "✓" if can_run else "✗"
                click.echo(f"  {status_icon} {model_name}: {required_mb}MB required")

            if vram_mb >= 8192:
                click.echo("\n  Note: Sequential model loading required")
        else:
            click.echo("  Running in CPU mode - models will use system RAM")

        click.echo("\n" + "=" * 60)

    except Exception as e:
        logger.error(f"Status command failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def _print_config(cfg: dict, indent: int = 0):
    """
    Pretty-print configuration dictionary.

    Args:
        cfg: Configuration dictionary
        indent: Current indentation level
    """
    prefix = " " * indent

    for key, value in cfg.items():
        if isinstance(value, dict):
            click.echo(f"{prefix}{key}:")
            _print_config(value, indent + 2)
        else:
            click.echo(f"{prefix}{key}: {value}")


@main.group()
def voice():
    """Voice cloning and synthesis commands."""
    pass


@voice.command()
@click.argument("audio_file", type=click.Path(exists=True, path_type=Path))
@click.option("--name", required=True, help="Name for the voice profile")
@click.option("--language", default="en", help="Language code (default: en)")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory for profiles",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def clone(audio_file: Path, name: str, language: str, storage: Path, config: Path):
    """
    Clone a voice from audio file.

    Creates a voice profile from reference audio that can be used
    for speech synthesis. Audio should be at least 3 seconds long,
    with 6+ seconds recommended.

    Example:
        avatar voice clone reference.wav --name "John Doe" --language en
    """
    try:
        click.echo(f"Cloning voice from: {audio_file}")
        click.echo(f"Profile name: {name}")
        click.echo(f"Language: {language}")

        # Load configuration
        cfg = load_config(config)

        # Initialize components
        vram_manager = VRAMManager()
        profile_manager = VoiceProfileManager(storage)
        cloner = XTTSVoiceCloner(
            config=cfg.get("voice", {}).get("xtts", {}),
            vram_manager=vram_manager,
            profile_manager=profile_manager,
        )

        # Clone voice
        result = cloner.clone_voice(audio_file, name, language)

        if result.success:
            click.echo(f"\nSuccess! Voice cloned in {result.processing_time_seconds:.2f}s")
            click.echo(f"Profile ID: {result.profile.profile_id}")
            click.echo(f"Storage: {result.profile.embedding_path.parent}")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Voice cloning failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@voice.command()
@click.argument("text")
@click.option("--profile", required=True, help="Voice profile ID or name")
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output audio file path")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory for profiles",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def speak(text: str, profile: str, output: Path, storage: Path, config: Path):
    """
    Synthesize speech with a cloned voice.

    Generates speech audio from text using a voice profile.
    Text length is limited to 5000 characters.

    Example:
        avatar voice speak "Hello, world!" --profile vp-abc12345 --output output.wav
    """
    try:
        click.echo(f"Synthesizing: {text[:50]}{'...' if len(text) > 50 else ''}")
        click.echo(f"Profile: {profile}")
        click.echo(f"Output: {output}")

        # Load configuration
        cfg = load_config(config)

        # Initialize components
        vram_manager = VRAMManager()
        profile_manager = VoiceProfileManager(storage)
        synthesizer = CoquiTTSSynthesizer(
            config=cfg.get("voice", {}).get("tts", {}),
            vram_manager=vram_manager,
        )

        # Load profile (try as ID first, then as name)
        try:
            voice_profile = profile_manager.load_profile(profile)
        except FileNotFoundError:
            # Try finding by name
            profiles = profile_manager.list_profiles()
            matching = [p for p in profiles if p.name == profile]
            if not matching:
                raise ValueError(f"Profile not found: {profile}")
            voice_profile = matching[0]
            click.echo(f"Using profile: {voice_profile.profile_id} ({voice_profile.name})")

        # Synthesize speech
        result = synthesizer.synthesize(text, voice_profile, output)

        if result.success:
            click.echo(
                f"\nSuccess! Generated {result.duration_seconds:.2f}s audio "
                f"in {result.processing_time_seconds:.2f}s"
            )
            click.echo(f"Saved to: {result.audio_path}")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@voice.command("list")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory for profiles",
)
def list_profiles(storage: Path):
    """
    List all voice profiles.

    Displays all available voice profiles with their IDs, names,
    and languages.
    """
    try:
        profile_manager = VoiceProfileManager(storage)
        profiles = profile_manager.list_profiles()

        if not profiles:
            click.echo("No voice profiles found.")
            click.echo(f"Storage directory: {storage / 'voices'}")
            return

        click.echo(f"\nFound {len(profiles)} voice profile(s):\n")
        click.echo("=" * 70)

        for profile in profiles:
            click.echo(f"Profile ID:   {profile.profile_id}")
            click.echo(f"Name:         {profile.name}")
            click.echo(f"Language:     {profile.language}")
            click.echo(f"Created:      {profile.created_at}")
            click.echo(f"Storage:      {profile.embedding_path.parent}")
            click.echo("-" * 70)

    except Exception as e:
        logger.error(f"Failed to list profiles: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def avatar():
    """Avatar generation and face detection commands."""
    pass


@avatar.command()
@click.argument("prompt")
@click.option("--output", type=click.Path(path_type=Path), help="Output image file path (optional)")
@click.option(
    "--aspect",
    default="16:9",
    type=click.Choice(["16:9", "9:16", "1:1"]),
    help="Image aspect ratio (default: 16:9)",
)
@click.option("--seed", type=int, help="Random seed for reproducibility")
@click.option(
    "--negative",
    default="",
    help="Negative prompt (things to avoid)",
)
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory for profiles",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def generate(
    prompt: str,
    output: Optional[Path],
    aspect: str,
    seed: Optional[int],
    negative: str,
    storage: Path,
    config: Path,
):
    """
    Generate avatar image from text prompt.

    Creates a photorealistic portrait image using SDXL 1.5.
    Automatically detects face and creates an avatar profile.

    Example:
        avatar avatar generate "professional businessman in suit" --aspect 16:9
    """
    try:
        click.echo(f"Generating avatar: {prompt}")
        click.echo(f"Aspect ratio: {aspect}")
        if seed is not None:
            click.echo(f"Seed: {seed}")

        # Load configuration
        cfg = load_config(config)

        # Initialize components
        vram_manager = VRAMManager()
        profile_manager = AvatarProfileManager(storage)
        generator = SDXLAvatarGenerator(
            config=cfg.get("avatar", {}).get("sdxl", {}),
            vram_manager=vram_manager,
            profile_manager=profile_manager,
        )

        # Generate avatar
        result = generator.generate(
            prompt=prompt,
            negative_prompt=negative,
            aspect_ratio=aspect,
            seed=seed,
            output_path=output,
        )

        if result.success:
            click.echo(
                f"\nSuccess! Avatar generated in {result.processing_time_seconds:.2f}s"
            )
            click.echo(f"Profile ID: {result.profile.profile_id}")
            click.echo(f"Image: {result.profile.base_image_path}")
            click.echo(f"Storage: {result.profile.base_image_path.parent}")

            # Show face detection info
            if result.profile.metadata.get("face_detected"):
                confidence = result.profile.metadata.get("face_confidence", 0)
                click.echo(f"Face detected: Yes (confidence: {confidence:.2f})")
            else:
                click.echo("Face detected: No (manual validation recommended)")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Avatar generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@avatar.command()
@click.argument("image", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed detection information",
)
def detect(image: Path, verbose: bool):
    """
    Detect and validate face in image.

    Detects faces using MediaPipe and validates suitability for lip-sync.
    Shows face region, landmarks, and validation results.

    Example:
        avatar avatar detect image.png --verbose
    """
    try:
        click.echo(f"Detecting face in: {image}")

        # Initialize detector
        detector = MediaPipeFaceDetector()

        # Detect face
        result = detector.detect(image)

        if result.error:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

        if not result.detected:
            click.echo("\nNo face detected in image.")
            sys.exit(1)

        # Show detection results
        click.echo("\n" + "=" * 60)
        click.echo("Face Detection Results")
        click.echo("=" * 60)
        click.echo(f"Detected: Yes")
        click.echo(f"Confidence: {result.confidence:.2f}")
        click.echo(f"\nFace Region:")
        click.echo(f"  X: {result.face_region['x']}")
        click.echo(f"  Y: {result.face_region['y']}")
        click.echo(f"  Width: {result.face_region['width']}")
        click.echo(f"  Height: {result.face_region['height']}")

        if verbose and result.landmarks:
            click.echo(f"\nKey Landmarks:")
            for name, coords in result.landmarks.items():
                click.echo(f"  {name}: ({coords['x']}, {coords['y']})")

        # Validate for lip-sync
        is_valid, message = detector.validate_for_lipsync(result)

        click.echo(f"\nLip-Sync Validation:")
        if is_valid:
            click.echo(f"  Status: Valid")
            click.echo(f"  Message: {message}")
        else:
            click.echo(f"  Status: Invalid")
            click.echo(f"  Reason: {message}")

        click.echo("=" * 60)

    except Exception as e:
        logger.error(f"Face detection failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@avatar.command("list")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory for profiles",
)
def list_avatar_profiles(storage: Path):
    """
    List all avatar profiles.

    Displays all available avatar profiles with their IDs, names,
    and generation details.
    """
    try:
        profile_manager = AvatarProfileManager(storage)
        profiles = profile_manager.list_profiles()

        if not profiles:
            click.echo("No avatar profiles found.")
            click.echo(f"Storage directory: {storage / 'avatars'}")
            return

        click.echo(f"\nFound {len(profiles)} avatar profile(s):\n")
        click.echo("=" * 70)

        for profile in profiles:
            click.echo(f"Profile ID:   {profile.profile_id}")
            click.echo(f"Name:         {profile.name}")
            click.echo(f"Aspect Ratio: {profile.aspect_ratio}")
            click.echo(f"Face Region:  {profile.face_region['width']}x{profile.face_region['height']}")
            click.echo(f"Created:      {profile.created_at}")
            click.echo(f"Image:        {profile.base_image_path}")

            # Show face detection status if available
            if "face_detected" in profile.metadata:
                face_detected = profile.metadata["face_detected"]
                if face_detected:
                    confidence = profile.metadata.get("face_confidence", 0)
                    click.echo(f"Face:         Detected (confidence: {confidence:.2f})")
                else:
                    click.echo(f"Face:         Not detected")

            click.echo("-" * 70)

    except Exception as e:
        logger.error(f"Failed to list profiles: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def video():
    """Video generation and encoding commands."""
    pass


@video.command()
@click.argument("image", type=click.Path(exists=True, path_type=Path))
@click.argument("audio", type=click.Path(exists=True, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output video file path")
@click.option(
    "--quality",
    default="high",
    type=click.Choice(["high", "medium", "low"]),
    help="Video quality preset (default: high)",
)
@click.option("--fps", type=int, help="Frames per second (overrides quality preset)")
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def lipsync(image: Path, audio: Path, output: Path, quality: str, fps: Optional[int], config: Path):
    """
    Generate lip-synced video from image and audio.

    Creates a talking head video by animating the face in the image
    to match the audio. The image should contain a clear frontal face.

    Example:
        avatar video lipsync avatar.png speech.wav --output video.mp4 --quality high
    """
    try:
        click.echo(f"Generating lip-sync video...")
        click.echo(f"  Image: {image}")
        click.echo(f"  Audio: {audio}")
        click.echo(f"  Output: {output}")
        click.echo(f"  Quality: {quality}")

        # Load configuration
        cfg = load_config(config)

        # Initialize components
        vram_manager = VRAMManager()
        lipsync_engine = MuseTalkLipSync(
            config=cfg.get("video", {}).get("lipsync", {}),
            vram_manager=vram_manager,
        )

        # Create lip-sync config
        lipsync_config = LipSyncConfig(quality=quality)
        if fps is not None:
            lipsync_config.fps = fps
            click.echo(f"  FPS: {fps}")

        # Generate video
        result = lipsync_engine.generate(
            avatar_image=image,
            audio_file=audio,
            output_path=output,
            config=lipsync_config,
        )

        if result.success:
            click.echo(
                f"\nSuccess! Generated {result.duration_seconds:.2f}s video "
                f"({result.frame_count} frames @ {result.fps}fps) "
                f"in {result.processing_time_seconds:.2f}s"
            )
            click.echo(f"Resolution: {result.resolution[0]}x{result.resolution[1]}")
            click.echo(f"Saved to: {result.video_path}")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Lip-sync generation failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@video.command()
@click.argument("input", type=click.Path(exists=True, path_type=Path))
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output video file path")
@click.option(
    "--quality",
    default="medium",
    type=click.Choice(["high", "medium", "low", "fast"]),
    help="Encoding quality preset (default: medium)",
)
@click.option("--crf", type=int, help="CRF quality value (0-51, lower is better)")
@click.option("--codec", default="libx264", help="Video codec (default: libx264)")
def encode(input: Path, output: Path, quality: str, crf: Optional[int], codec: str):
    """
    Encode or transcode video file.

    Re-encodes video with specified quality settings. Useful for
    compression, format conversion, or quality adjustments.

    Example:
        avatar video encode input.mp4 --output output.mp4 --quality high
    """
    try:
        click.echo(f"Encoding video: {input} -> {output}")
        click.echo(f"Quality preset: {quality}")
        click.echo(f"Codec: {codec}")

        # Initialize encoder
        encoder = FFmpegEncoder()

        # Map quality presets to FFmpeg settings
        preset_map = {
            "high": ("slow", 18),
            "medium": ("medium", 23),
            "low": ("fast", 28),
            "fast": ("veryfast", 23),
        }

        preset, default_crf = preset_map.get(quality, ("medium", 23))

        # Use provided CRF or default
        if crf is None:
            crf = default_crf

        click.echo(f"Settings: preset={preset}, crf={crf}")

        # Create encoding config
        from .video import EncodingConfig

        encoding_config = EncodingConfig(
            codec=codec,
            preset=preset,
            crf=crf,
        )

        # Encode video
        result = encoder.encode(input, output, encoding_config)

        if result.success:
            file_size_mb = result.file_size_bytes / 1024 / 1024
            click.echo(
                f"\nSuccess! Encoded {result.duration_seconds:.1f}s video "
                f"({file_size_mb:.2f}MB) in {result.processing_time_seconds:.2f}s"
            )
            click.echo(f"Saved to: {result.output_path}")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Video encoding failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@video.command()
@click.argument("video_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed information",
)
def info(video_file: Path, verbose: bool):
    """
    Display video file information.

    Shows video metadata including duration, resolution, codec, and FPS.

    Example:
        avatar video info video.mp4 --verbose
    """
    try:
        click.echo(f"Analyzing video: {video_file}")

        # Initialize encoder for info extraction
        encoder = FFmpegEncoder()

        # Get video info
        info_data = encoder.get_video_info(video_file)

        # Display info
        click.echo("\n" + "=" * 60)
        click.echo("Video Information")
        click.echo("=" * 60)
        click.echo(f"File:       {video_file}")
        click.echo(f"Duration:   {info_data['duration']:.2f} seconds")
        click.echo(f"Resolution: {info_data['width']}x{info_data['height']}")
        click.echo(f"FPS:        {info_data['fps']:.2f}")
        click.echo(f"Codec:      {info_data['codec']}")

        # Get file size
        file_size_mb = video_file.stat().st_size / 1024 / 1024
        click.echo(f"File Size:  {file_size_mb:.2f} MB")

        if verbose:
            # Calculate bitrate
            if info_data['duration'] > 0:
                bitrate_mbps = (file_size_mb * 8) / info_data['duration']
                click.echo(f"Bitrate:    {bitrate_mbps:.2f} Mbps (average)")

        click.echo("=" * 60)

    except Exception as e:
        logger.error(f"Failed to get video info: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def pipeline():
    """Full pipeline commands."""
    pass


@pipeline.command("run")
@click.argument("text")
@click.option("--voice", required=True, help="Voice profile ID or name")
@click.option("--avatar", required=True, type=click.Path(exists=True, path_type=Path), help="Avatar image path")
@click.option("--output", required=True, type=click.Path(path_type=Path), help="Output video file path")
@click.option(
    "--quality",
    default="high",
    type=click.Choice(["high", "medium", "low"]),
    help="Video quality preset (default: high)",
)
@click.option("--fps", type=int, help="Video frame rate (overrides quality preset)")
@click.option("--keep-temp", is_flag=True, help="Keep intermediate files")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def pipeline_run(
    text: str,
    voice: str,
    avatar: Path,
    output: Path,
    quality: str,
    fps: Optional[int],
    keep_temp: bool,
    storage: Path,
    config: Path,
):
    """
    Run full avatar video pipeline.

    Executes the complete pipeline from text to video:
    1. Text-to-speech synthesis
    2. Avatar face validation
    3. Lip-sync video generation
    4. Final encoding

    Example:
        avatar pipeline run "Hello, world!" --voice vp-abc12345 --avatar avatar.png --output video.mp4
    """
    try:
        click.echo("=" * 70)
        click.echo("Avatar Pipeline - Full Execution")
        click.echo("=" * 70)
        click.echo(f"\nText: {text[:100]}{'...' if len(text) > 100 else ''}")
        click.echo(f"Voice: {voice}")
        click.echo(f"Avatar: {avatar}")
        click.echo(f"Output: {output}")
        click.echo(f"Quality: {quality}")

        # Load configuration
        cfg = load_config(config)

        # Initialize components
        vram_manager = VRAMManager()
        voice_profile_manager = VoiceProfileManager(storage)
        coordinator = PipelineCoordinator(
            config=cfg,
            vram_manager=vram_manager,
            storage_path=storage,
        )

        # Load voice profile (try as ID first, then as name)
        try:
            voice_profile = voice_profile_manager.load_profile(voice)
            voice_profile_id = voice_profile.profile_id
        except FileNotFoundError:
            # Try finding by name
            profiles = voice_profile_manager.list_profiles()
            matching = [p for p in profiles if p.name == voice]
            if not matching:
                raise ValueError(f"Voice profile not found: {voice}")
            voice_profile_id = matching[0].profile_id
            click.echo(f"Using voice profile: {voice_profile_id} ({matching[0].name})")

        # Create pipeline config
        pipeline_config = PipelineConfig(
            video_quality=quality,
            video_fps=fps,
            cleanup_intermediates=not keep_temp,
        )

        # Execute pipeline
        result = coordinator.execute(
            text=text,
            voice_profile_id=voice_profile_id,
            avatar_image=avatar,
            output_path=output,
            config=pipeline_config,
        )

        if result.success:
            click.echo("\n" + "=" * 70)
            click.echo("Pipeline completed successfully!")
            click.echo("=" * 70)
            click.echo(f"\nOutput: {result.output_path}")
            click.echo(f"Duration: {result.duration_seconds:.2f}s")
            click.echo(f"Processing time: {result.processing_time_seconds:.2f}s")
            click.echo(f"Stages: {', '.join(result.stages_completed)}")

            if result.intermediate_files:
                click.echo("\nIntermediate files:")
                for category, path in result.intermediate_files.items():
                    click.echo(f"  {category}: {path}")
        else:
            click.echo(f"\nError: {result.error}", err=True)
            click.echo(f"Failed after stages: {', '.join(result.stages_completed)}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def server():
    """API server commands."""
    pass


@server.command("start")
@click.option("--host", default="0.0.0.0", help="Server host (default: 0.0.0.0)")
@click.option("--port", default=8000, type=int, help="Server port (default: 8000)")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to config YAML file",
)
def server_start(
    host: str, port: int, reload: bool, storage: Path, config: Path
):
    """
    Start REST API server.

    Starts the FastAPI server for remote access to the avatar pipeline.
    Provides HTTP endpoints for job submission, status checking, and
    component operations.

    Example:
        avatar server start --host 0.0.0.0 --port 8000
    """
    try:
        import uvicorn

        click.echo("=" * 70)
        click.echo("Avatar Pipeline - API Server")
        click.echo("=" * 70)
        click.echo(f"\nHost: {host}")
        click.echo(f"Port: {port}")
        click.echo(f"Storage: {storage}")
        if config:
            click.echo(f"Config: {config}")
        click.echo(f"Auto-reload: {'enabled' if reload else 'disabled'}")
        click.echo("\nStarting server...")
        click.echo("=" * 70)

        # Import and create app
        from .api.main import create_app

        app = create_app(config_path=config, storage_path=storage)

        # Run server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )

    except ImportError as e:
        logger.error(f"Failed to import server components: {e}")
        click.echo(
            "Error: Missing dependencies. Install with: pip install fastapi uvicorn",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Server failed: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.group()
def jobs():
    """Job queue commands."""
    pass


@jobs.command("list")
@click.option("--status", help="Filter by status")
@click.option("--limit", default=50, type=int, help="Maximum number of jobs to show")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory",
)
def list_jobs(status: Optional[str], limit: int, storage: Path):
    """
    List jobs in the queue.

    Shows all jobs with their status, type, and progress.

    Example:
        avatar jobs list --status pending --limit 20
    """
    try:
        # Initialize job queue
        job_queue = JobQueue(storage)

        # Parse status filter
        status_filter = None
        if status is not None:
            from .orchestration import JobStatus

            try:
                status_filter = JobStatus(status)
            except ValueError:
                valid_statuses = ", ".join([s.value for s in JobStatus])
                click.echo(
                    f"Error: Invalid status '{status}'. Valid: {valid_statuses}",
                    err=True,
                )
                sys.exit(1)

        # Get jobs
        jobs_list = job_queue.list_jobs(status=status_filter, limit=limit)

        if not jobs_list:
            click.echo("No jobs found.")
            return

        click.echo(f"\nFound {len(jobs_list)} job(s):\n")
        click.echo("=" * 100)

        for job in jobs_list:
            click.echo(f"Job ID:   {job.job_id}")
            click.echo(f"Type:     {job.job_type.value}")
            click.echo(f"Status:   {job.status.value}")
            click.echo(f"Progress: {job.progress * 100:.1f}%")
            click.echo(f"Stage:    {job.stage}")
            click.echo(f"Created:  {job.created_at}")

            if job.started_at:
                click.echo(f"Started:  {job.started_at}")

            if job.completed_at:
                click.echo(f"Completed: {job.completed_at}")

            if job.error:
                click.echo(f"Error:    {job.error}")

            if job.result:
                click.echo(f"Result:   {job.result}")

            click.echo("-" * 100)

    except Exception as e:
        logger.error(f"Failed to list jobs: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@jobs.command("status")
@click.argument("job_id")
@click.option(
    "--storage",
    type=click.Path(path_type=Path),
    default="storage",
    help="Storage directory",
)
def job_status(job_id: str, storage: Path):
    """
    Show status of a specific job.

    Example:
        avatar jobs status job-20240115-abc12345
    """
    try:
        # Initialize job queue
        job_queue = JobQueue(storage)

        # Get job
        job = job_queue.get(job_id)

        if job is None:
            click.echo(f"Error: Job not found: {job_id}", err=True)
            sys.exit(1)

        click.echo("\n" + "=" * 70)
        click.echo("Job Details")
        click.echo("=" * 70)
        click.echo(f"Job ID:   {job.job_id}")
        click.echo(f"Type:     {job.job_type.value}")
        click.echo(f"Status:   {job.status.value}")
        click.echo(f"Progress: {job.progress * 100:.1f}%")
        click.echo(f"Stage:    {job.stage}")
        click.echo(f"\nCreated:  {job.created_at}")

        if job.started_at:
            click.echo(f"Started:  {job.started_at}")

        if job.completed_at:
            click.echo(f"Completed: {job.completed_at}")

        click.echo(f"\nParameters:")
        for key, value in job.params.items():
            click.echo(f"  {key}: {value}")

        if job.result:
            click.echo(f"\nResult:")
            for key, value in job.result.items():
                click.echo(f"  {key}: {value}")

        if job.error:
            click.echo(f"\nError: {job.error}")

        click.echo("=" * 70)

    except Exception as e:
        logger.error(f"Failed to get job status: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
