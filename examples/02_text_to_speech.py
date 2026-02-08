"""
Example 02: Text-to-Speech Synthesis

Demonstrates how to generate speech from text using a cloned voice profile.

Requirements:
    - A cloned voice profile (run 01_voice_cloning.py first)
    - Or use an existing profile ID

Usage:
    python examples/02_text_to_speech.py
"""

from pathlib import Path

from src.config import load_config
from src.utils import VRAMManager
from src.voice import VoiceProfileManager, CoquiTTSSynthesizer


def main():
    """Synthesize speech from text."""
    print("=" * 70)
    print("Example 02: Text-to-Speech Synthesis")
    print("=" * 70)

    # Configuration
    text = "Hello! This is an example of text-to-speech synthesis using a cloned voice."
    voice_profile_name = "Example Voice"  # Replace with your profile name or ID
    output_path = Path("output/synthesized_speech.wav")
    storage_path = Path("storage")

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load configuration
    print("\n[1/5] Loading configuration...")
    config = load_config()
    print("Configuration loaded successfully")

    # Initialize components
    print("\n[2/5] Initializing text-to-speech system...")
    vram_manager = VRAMManager()
    profile_manager = VoiceProfileManager(storage_path)
    synthesizer = CoquiTTSSynthesizer(
        config=config.get("voice", {}).get("tts", {}),
        vram_manager=vram_manager,
    )
    print("Text-to-speech system initialized")

    # Load voice profile
    print("\n[3/5] Loading voice profile...")
    print(f"  Searching for: {voice_profile_name}")

    try:
        # First try to load as profile ID
        try:
            voice_profile = profile_manager.load_profile(voice_profile_name)
        except FileNotFoundError:
            # If not found, try finding by name
            profiles = profile_manager.list_profiles()
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

            voice_profile = matching[0]

        print(f"  Profile loaded: {voice_profile.name} ({voice_profile.profile_id})")
        print(f"  Language: {voice_profile.language}")

        # Synthesize speech
        print("\n[4/5] Synthesizing speech...")
        print(f"  Text: {text}")
        print(f"  Output: {output_path}")
        print("\nThis may take 20-40 seconds on first run (model download)...")

        result = synthesizer.synthesize(
            text=text,
            voice_profile=voice_profile,
            output_path=output_path,
        )

        # Display results
        print("\n[5/5] Speech synthesis complete!")
        print("=" * 70)

        if result.success:
            print("\nSuccess!")
            print(f"  Audio duration: {result.duration_seconds:.2f}s")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"  Speed: {result.duration_seconds / result.processing_time_seconds:.2f}x realtime")
            print(f"\nAudio saved to: {result.audio_path}")
            print("\nYou can:")
            print(f"  - Play the audio file")
            print(f"  - Use it for lip-sync: avatar video lipsync avatar.png {result.audio_path} --output video.mp4")
        else:
            print(f"\nError during synthesis: {result.error}")
            print("\nTroubleshooting:")
            print("  - Check voice profile is valid")
            print("  - Verify CUDA/GPU is available: avatar status")
            print("  - Ensure sufficient VRAM (3GB+ required)")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check:")
        print("  - Voice profile exists (run 01_voice_cloning.py)")
        print("  - GPU/CUDA availability")
        print("  - Available VRAM (3GB+ required)")

    print("=" * 70)


if __name__ == "__main__":
    main()
