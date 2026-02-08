"""
Example: Full pipeline execution.

Demonstrates running the complete avatar video pipeline from text to video.
"""

from pathlib import Path

from src.config import load_config
from src.orchestration import PipelineConfig, PipelineCoordinator
from src.utils import VRAMManager


def main():
    """Run example pipeline execution."""
    # Configuration
    text = "Hello! This is a test of the avatar video pipeline."
    voice_profile_id = "vp-example"  # Replace with actual profile ID
    avatar_image = Path("examples/avatar.png")  # Replace with actual image
    output_path = Path("outputs/example_video.mp4")

    # Load config
    config = load_config()

    # Initialize components
    vram_manager = VRAMManager()
    storage_path = Path("storage")

    # Create pipeline coordinator
    coordinator = PipelineCoordinator(
        config=config,
        vram_manager=vram_manager,
        storage_path=storage_path,
    )

    # Create pipeline config
    pipeline_config = PipelineConfig(
        video_quality="high",
        cleanup_intermediates=True,
    )

    print("=" * 70)
    print("Avatar Pipeline - Example Execution")
    print("=" * 70)
    print(f"\nText: {text}")
    print(f"Voice: {voice_profile_id}")
    print(f"Avatar: {avatar_image}")
    print(f"Output: {output_path}")
    print("\nStarting pipeline...\n")

    # Execute pipeline
    result = coordinator.execute(
        text=text,
        voice_profile_id=voice_profile_id,
        avatar_image=avatar_image,
        output_path=output_path,
        config=pipeline_config,
    )

    # Display results
    print("\n" + "=" * 70)
    if result.success:
        print("Pipeline completed successfully!")
        print(f"\nOutput: {result.output_path}")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"Stages: {', '.join(result.stages_completed)}")
    else:
        print("Pipeline failed!")
        print(f"\nError: {result.error}")
        print(f"Completed stages: {', '.join(result.stages_completed)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
