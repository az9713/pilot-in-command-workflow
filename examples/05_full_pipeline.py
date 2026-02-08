"""
Example 05: Full Pipeline Execution

Demonstrates running the complete pipeline from text to final video.

Requirements:
    - A cloned voice profile
    - Avatar image with visible face
    - GPU with 10GB+ VRAM (or sequential loading on 8GB)

Usage:
    python examples/05_full_pipeline.py
"""

from pathlib import Path

from src.config import load_config
from src.orchestration import PipelineConfig, PipelineCoordinator
from src.utils import VRAMManager
from src.voice import VoiceProfileManager


def main():
    """Execute the full avatar video pipeline."""
    print("=" * 70)
    print("Example 05: Full Pipeline Execution")
    print("=" * 70)

    # Configuration
    text = "Hello! This is a demonstration of the complete avatar video pipeline. It combines voice cloning, text-to-speech synthesis, and lip-sync video generation."
    voice_profile_name = "Example Voice"  # Replace with your voice profile
    avatar_image = Path("output/generated_avatar.png")  # Replace with your avatar
    output_video = Path("output/full_pipeline_video.mp4")
    storage_path = Path("storage")

    # Pipeline settings
    video_quality = "high"  # Options: "high", "medium", "low"
    keep_intermediates = True  # Keep temp files for debugging

    # Check inputs
    if not avatar_image.exists():
        print(f"\nError: Avatar image not found: {avatar_image}")
        print("\nPlease:")
        print("  1. Run 03_avatar_generation.py to create an avatar")
        print("  2. Or provide your own avatar image path")
        return

    # Ensure output directory exists
    output_video.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    print("\n[1/7] Loading configuration...")
    config = load_config()
    print("Configuration loaded successfully")

    # Initialize components
    print("\n[2/7] Initializing pipeline...")
    vram_manager = VRAMManager()
    voice_profile_manager = VoiceProfileManager(storage_path)
    coordinator = PipelineCoordinator(
        config=config,
        vram_manager=vram_manager,
        storage_path=storage_path,
    )
    print("Pipeline initialized")

    # Load voice profile
    print("\n[3/7] Loading voice profile...")
    try:
        # Try loading as ID first
        try:
            voice_profile = voice_profile_manager.load_profile(voice_profile_name)
            voice_profile_id = voice_profile.profile_id
        except FileNotFoundError:
            # Try finding by name
            profiles = voice_profile_manager.list_profiles()
            matching = [p for p in profiles if p.name == voice_profile_name]

            if not matching:
                print(f"\nError: Voice profile not found: {voice_profile_name}")
                print("\nAvailable profiles:")
                if profiles:
                    for p in profiles:
                        print(f"  - {p.name} (ID: {p.profile_id})")
                else:
                    print("  No profiles found. Run 01_voice_cloning.py first.")
                return

            voice_profile_id = matching[0].profile_id
            print(f"  Using profile: {matching[0].name} ({voice_profile_id})")

    except Exception as e:
        print(f"\nError loading voice profile: {e}")
        return

    # Create pipeline config
    pipeline_config = PipelineConfig(
        video_quality=video_quality,
        cleanup_intermediates=not keep_intermediates,
    )

    # Execute pipeline
    print("\n[4/7] Executing pipeline...")
    print(f"  Text: {text[:100]}{'...' if len(text) > 100 else ''}")
    print(f"  Voice: {voice_profile_id}")
    print(f"  Avatar: {avatar_image}")
    print(f"  Output: {output_video}")
    print(f"  Quality: {video_quality}")
    print(f"  Keep intermediates: {keep_intermediates}")
    print("\nPipeline stages:")
    print("  1. Text-to-speech synthesis")
    print("  2. Avatar face validation")
    print("  3. Lip-sync video generation")
    print("  4. Final video encoding")
    print("\nThis will take 2-5 minutes depending on text length and GPU...")

    try:
        result = coordinator.execute(
            text=text,
            voice_profile_id=voice_profile_id,
            avatar_image=avatar_image,
            output_path=output_video,
            config=pipeline_config,
        )

        # Display results
        print("\n[5/7] Pipeline execution complete!")
        print("=" * 70)

        if result.success:
            print("\nSuccess!")
            print(f"  Video duration: {result.duration_seconds:.2f}s")
            print(f"  Total processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Speed: {result.duration_seconds / result.processing_time_seconds:.2f}x realtime")
            print(f"\n  Stages completed: {', '.join(result.stages_completed)}")

            # Show intermediate files if kept
            if result.intermediate_files:
                print("\n[6/7] Intermediate files:")
                for category, path in result.intermediate_files.items():
                    print(f"  {category}: {path}")
            else:
                print("\n[6/7] Intermediate files cleaned up")

            # File info
            file_size_mb = result.output_path.stat().st_size / 1024 / 1024
            print(f"\n[7/7] Final output:")
            print(f"  Path: {result.output_path}")
            print(f"  Size: {file_size_mb:.2f} MB")

            print("\nYou can now:")
            print(f"  - Play the video file")
            print(f"  - Check details: avatar video info {result.output_path}")
            print(f"  - Share or upload the video")

            # Performance tips
            print("\nPerformance tips:")
            print("  - For faster generation: --quality low")
            print("  - For better quality: --quality high")
            print("  - Keep intermediates for debugging: --keep-temp")

        else:
            print(f"\nError: {result.error}")
            print(f"Failed after stages: {', '.join(result.stages_completed)}")
            print("\nTroubleshooting:")
            print("  - Check error message above")
            print("  - Verify all inputs are valid")
            print("  - Check VRAM: avatar status")
            print("  - Try lower quality: --quality low")

            if result.intermediate_files:
                print("\nIntermediate files (for debugging):")
                for category, path in result.intermediate_files.items():
                    print(f"  {category}: {path}")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check:")
        print("  - Voice profile exists and is valid")
        print("  - Avatar image has visible face")
        print("  - GPU/CUDA availability")
        print("  - Available VRAM (8GB+ required)")
        print("  - FFmpeg is installed")

    print("=" * 70)


if __name__ == "__main__":
    main()
