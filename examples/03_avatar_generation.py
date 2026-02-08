"""
Example 03: Avatar Generation

Demonstrates how to generate an avatar image from a text prompt using SDXL.

Requirements:
    - GPU with 8GB+ VRAM (SDXL requires ~7GB)
    - Or CPU mode (very slow)

Usage:
    python examples/03_avatar_generation.py
"""

from pathlib import Path

from src.config import load_config
from src.utils import VRAMManager
from src.avatar import AvatarProfileManager, SDXLAvatarGenerator, MediaPipeFaceDetector


def main():
    """Generate an avatar image from a text prompt."""
    print("=" * 70)
    print("Example 03: Avatar Generation with SDXL")
    print("=" * 70)

    # Configuration
    prompt = "professional person, portrait, neutral expression, looking at camera, high quality"
    negative_prompt = "cartoon, anime, drawing, low quality, blurry, deformed"
    aspect_ratio = "16:9"
    seed = None  # Set to integer for reproducible results
    output_path = Path("output/generated_avatar.png")
    storage_path = Path("storage")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    print("\n[1/5] Loading configuration...")
    config = load_config()
    print("Configuration loaded successfully")

    # Initialize components
    print("\n[2/5] Initializing avatar generation system...")
    vram_manager = VRAMManager()
    profile_manager = AvatarProfileManager(storage_path)
    generator = SDXLAvatarGenerator(
        config=config.get("avatar", {}).get("sdxl", {}),
        vram_manager=vram_manager,
        profile_manager=profile_manager,
    )
    print("Avatar generation system initialized")

    # Generate avatar
    print("\n[3/5] Generating avatar...")
    print(f"  Prompt: {prompt}")
    print(f"  Aspect ratio: {aspect_ratio}")
    if seed is not None:
        print(f"  Seed: {seed}")
    print("\nThis may take 2-5 minutes on first run (model download ~7GB)...")
    print("Generation typically takes 30-90 seconds depending on GPU...")

    try:
        result = generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            aspect_ratio=aspect_ratio,
            seed=seed,
            output_path=output_path,
        )

        # Display results
        print("\n[4/5] Avatar generation complete!")

        if result.success:
            print("\nSuccess!")
            print(f"  Profile ID: {result.profile.profile_id}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Image saved to: {result.profile.base_image_path}")

            # Face detection results
            print("\n[5/5] Face detection results:")
            if result.profile.metadata.get("face_detected"):
                confidence = result.profile.metadata.get("face_confidence", 0)
                print(f"  Face detected: Yes")
                print(f"  Confidence: {confidence:.2f}")
                print(f"  Face region: {result.profile.face_region['width']}x{result.profile.face_region['height']}")

                # Check if suitable for lip-sync
                detector = MediaPipeFaceDetector()
                detection_result = detector.detect(result.profile.base_image_path)
                is_valid, message = detector.validate_for_lipsync(detection_result)

                print(f"\n  Lip-sync validation:")
                if is_valid:
                    print(f"    Status: Valid for lip-sync")
                    print(f"    Message: {message}")
                else:
                    print(f"    Status: Not ideal for lip-sync")
                    print(f"    Reason: {message}")
                    print(f"    Suggestion: Try regenerating with different prompt/seed")
            else:
                print(f"  Face detected: No")
                print(f"  Note: You may need to regenerate with a clearer face")
                print(f"  Tip: Try adding 'frontal view, looking at camera' to prompt")

            print("\nYou can now:")
            print(f"  - View the image: {result.profile.base_image_path}")
            print(f"  - Use for video: avatar video lipsync {result.profile.base_image_path} audio.wav --output video.mp4")
            print(f"  - Validate face: avatar avatar detect {result.profile.base_image_path} --verbose")

        else:
            print(f"\nError during generation: {result.error}")
            print("\nTroubleshooting:")
            print("  - Check VRAM availability (7GB+ required): avatar status")
            print("  - Try closing other GPU applications")
            print("  - Consider using CPU mode (very slow)")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check:")
        print("  - GPU/CUDA availability")
        print("  - Available VRAM (7GB+ required for SDXL)")
        print("  - Disk space for model downloads (~7GB)")

    print("=" * 70)


if __name__ == "__main__":
    main()
