"""
Example 01: Voice Cloning

Demonstrates how to clone a voice from reference audio using XTTS-v2.

Requirements:
    - Reference audio file (3+ seconds, 6+ recommended)
    - WAV or MP3 format
    - Clean audio without background noise

Usage:
    python examples/01_voice_cloning.py
"""

from pathlib import Path

from src.config import load_config
from src.utils import VRAMManager
from src.voice import VoiceProfileManager, XTTSVoiceCloner


def main():
    """Clone a voice from reference audio."""
    print("=" * 70)
    print("Example 01: Voice Cloning with XTTS-v2")
    print("=" * 70)

    # Configuration
    reference_audio = Path("examples/reference_audio.wav")  # Replace with your audio
    voice_name = "Example Voice"
    language = "en"  # Change to your language
    storage_path = Path("storage")

    # Check if reference audio exists
    if not reference_audio.exists():
        print(f"\nError: Reference audio not found: {reference_audio}")
        print("\nPlease provide a reference audio file (3+ seconds).")
        print("Supported formats: WAV, MP3, FLAC, OGG")
        print("\nExample:")
        print(f"  Place your audio at: {reference_audio}")
        print("  Or modify the 'reference_audio' variable in this script")
        return

    # Load configuration
    print("\n[1/4] Loading configuration...")
    config = load_config()
    print("Configuration loaded successfully")

    # Initialize components
    print("\n[2/4] Initializing voice cloning system...")
    vram_manager = VRAMManager()
    profile_manager = VoiceProfileManager(storage_path)
    cloner = XTTSVoiceCloner(
        config=config.get("voice", {}).get("xtts", {}),
        vram_manager=vram_manager,
        profile_manager=profile_manager,
    )
    print("Voice cloning system initialized")

    # Clone voice
    print("\n[3/4] Cloning voice from audio...")
    print(f"  Audio file: {reference_audio}")
    print(f"  Voice name: {voice_name}")
    print(f"  Language: {language}")
    print("\nThis may take 30-60 seconds on first run (model download)...")

    try:
        result = cloner.clone_voice(
            audio_path=reference_audio,
            voice_name=voice_name,
            language=language,
        )

        # Display results
        print("\n[4/4] Voice cloning complete!")
        print("=" * 70)

        if result.success:
            print("\nSuccess!")
            print(f"  Profile ID: {result.profile.profile_id}")
            print(f"  Name: {result.profile.name}")
            print(f"  Language: {result.profile.language}")
            print(f"  Processing time: {result.processing_time_seconds:.2f}s")
            print(f"\nProfile saved to: {result.profile.embedding_path}")
            print("\nYou can now use this profile for speech synthesis:")
            print(f'  avatar voice speak "Hello!" --profile "{result.profile.profile_id}" --output output.wav')
            print(f'  Or: avatar voice speak "Hello!" --profile "{voice_name}" --output output.wav')
        else:
            print(f"\nError during voice cloning: {result.error}")
            print("\nTroubleshooting:")
            print("  - Ensure audio is at least 3 seconds long")
            print("  - Check audio format (WAV recommended)")
            print("  - Verify CUDA/GPU is available: avatar status")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("\nPlease check:")
        print("  - GPU/CUDA availability")
        print("  - Available VRAM (4GB+ required)")
        print("  - Audio file format and quality")

    print("=" * 70)


if __name__ == "__main__":
    main()
