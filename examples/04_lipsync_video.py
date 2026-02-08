"""
Example 04: Lip-Sync Video Generation

Demonstrates how to create a lip-synced video from an image and audio file.

Requirements:
    - Avatar image with visible face
    - Audio file (WAV/MP3)
    - GPU with 8GB+ VRAM (MuseTalk requires ~5GB)
    - FFmpeg installed

Usage:
    python examples/04_lipsync_video.py
"""

from pathlib import Path

from src.config import load_config
from src.utils import VRAMManager
from src.video import MuseTalkLipSync, FFmpegEncoder, LipSyncConfig


def main():
    """Generate a lip-synced video."""
    print("=" * 70)
    print("Example 04: Lip-Sync Video Generation with MuseTalk")
    print("=" * 70)

    # Configuration
    avatar_image = Path("output/generated_avatar.png")  # Replace with your image
    audio_file = Path("output/synthesized_speech.wav")  # Replace with your audio
    output_video = Path("output/lipsync_video.mp4")
    quality = "high"  # Options: "high", "medium", "low"

    # Check if inputs exist
    if not avatar_image.exists():
        print(f"\nError: Avatar image not found: {avatar_image}")
        print("\nPlease provide an avatar image or run 03_avatar_generation.py")
        return

    if not audio_file.exists():
        print(f"\nError: Audio file not found: {audio_file}")
        print("\nPlease provide an audio file or run 02_text_to_speech.py")
        return

    # Ensure output directory exists
    output_video.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    print("\n[1/4] Loading configuration...")
    config = load_config()
    print("Configuration loaded successfully")

    # Initialize components
    print("\n[2/4] Initializing lip-sync system...")
    vram_manager = VRAMManager()
    lipsync_engine = MuseTalkLipSync(
        config=config.get("video", {}).get("musetalk", {}),
        vram_manager=vram_manager,
    )
    print("Lip-sync system initialized")

    # Create lip-sync config
    lipsync_config = LipSyncConfig(quality=quality)

    # Generate video
    print("\n[3/4] Generating lip-synced video...")
    print(f"  Avatar image: {avatar_image}")
    print(f"  Audio file: {audio_file}")
    print(f"  Output: {output_video}")
    print(f"  Quality: {quality}")
    print(f"  FPS: {lipsync_config.fps}")
    print("\nThis may take 2-5 minutes on first run (model download ~3GB)...")
    print("Generation typically takes 1-3 minutes depending on audio length and GPU...")

    try:
        result = lipsync_engine.generate(
            avatar_image=avatar_image,
            audio_file=audio_file,
            output_path=output_video,
            config=lipsync_config,
        )

        # Display results
        print("\n[4/4] Lip-sync video complete!")
        print("=" * 70)

        if result.success:
            print("\nSuccess!")
            print(f"  Video duration: {result.duration_seconds:.2f}s")
            print(f"  Frame count: {result.frame_count}")
            print(f"  FPS: {result.fps}")
            print(f"  Resolution: {result.resolution[0]}x{result.resolution[1]}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Speed: {result.duration_seconds / result.processing_time_seconds:.2f}x realtime")

            # Get file size
            file_size_mb = result.video_path.stat().st_size / 1024 / 1024
            print(f"  File size: {file_size_mb:.2f} MB")

            print(f"\nVideo saved to: {result.video_path}")

            print("\nYou can now:")
            print(f"  - Play the video file")
            print(f"  - Check video info: avatar video info {result.video_path}")
            print(f"  - Re-encode: avatar video encode {result.video_path} --output output.mp4 --quality medium")

            # Tips for quality
            print("\nQuality tips:")
            print("  - For faster generation: --quality low (15 fps)")
            print("  - For better quality: --quality high (25 fps)")
            print("  - For custom FPS: --fps 30")

        else:
            print(f"\nError during video generation: {result.error}")
            print("\nTroubleshooting:")
            print("  - Check face is visible and frontal in image")
            print("  - Verify CUDA/GPU is available: avatar status")
            print("  - Ensure sufficient VRAM (5GB+ required)")
            print("  - Verify FFmpeg is installed: ffmpeg -version")
            print("  - Try lower quality: --quality low")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check:")
        print("  - GPU/CUDA availability")
        print("  - Available VRAM (5GB+ required for MuseTalk)")
        print("  - FFmpeg installation")
        print("  - Image contains visible face")
        print("  - Audio file is valid")

    print("=" * 70)


if __name__ == "__main__":
    main()
