"""
Voice module interfaces.

Defines abstract base classes and data structures for voice cloning
and TTS synthesis operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VoiceProfile:
    """
    Voice profile metadata.

    Attributes:
        profile_id: Unique identifier (format: vp-{8 chars})
        name: Human-readable profile name
        language: Language code (e.g., 'en', 'es', 'fr')
        embedding_path: Path to stored speaker embedding (.pt file)
        reference_audio_path: Path to reference audio file
        created_at: ISO timestamp of creation
        metadata: Additional profile metadata
    """

    profile_id: str
    name: str
    language: str
    embedding_path: Path
    reference_audio_path: Path
    created_at: str
    metadata: dict


@dataclass
class CloneResult:
    """
    Result of voice cloning operation.

    Attributes:
        success: Whether cloning succeeded
        profile: Created voice profile (if successful)
        error: Error message (if failed)
        processing_time_seconds: Time taken for cloning
    """

    success: bool
    profile: Optional[VoiceProfile]
    error: Optional[str]
    processing_time_seconds: float


@dataclass
class SynthesisResult:
    """
    Result of TTS synthesis operation.

    Attributes:
        success: Whether synthesis succeeded
        audio_path: Path to generated audio file (if successful)
        duration_seconds: Duration of generated audio
        error: Error message (if failed)
        processing_time_seconds: Time taken for synthesis
    """

    success: bool
    audio_path: Optional[Path]
    duration_seconds: float
    error: Optional[str]
    processing_time_seconds: float


class VoiceClonerInterface(ABC):
    """
    Abstract interface for voice cloning.

    Implementations should use XTTS-v2 or compatible models to extract
    speaker embeddings from reference audio.
    """

    @abstractmethod
    def clone_voice(
        self, reference_audio: Path, profile_name: str, language: str = "en"
    ) -> CloneResult:
        """
        Clone a voice from reference audio.

        Args:
            reference_audio: Path to reference audio file (WAV/MP3)
            profile_name: Name for the voice profile
            language: Language code (default: 'en')

        Returns:
            CloneResult with success status and profile data

        Note:
            Reference audio should be at least 3 seconds, 6+ recommended.
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported language codes.

        Returns:
            List of ISO language codes (e.g., ['en', 'es', 'fr'])
        """
        pass


class TTSSynthesizerInterface(ABC):
    """
    Abstract interface for TTS synthesis.

    Implementations should use Coqui TTS or compatible models to generate
    speech from text using cloned voice profiles.
    """

    @abstractmethod
    def synthesize(
        self, text: str, voice_profile: VoiceProfile, output_path: Path
    ) -> SynthesisResult:
        """
        Synthesize speech from text using a voice profile.

        Args:
            text: Text to synthesize (max 5000 characters)
            voice_profile: Voice profile with speaker embedding
            output_path: Where to save generated audio (WAV)

        Returns:
            SynthesisResult with success status and audio info
        """
        pass

    @abstractmethod
    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate audio duration for given text.

        Args:
            text: Text to synthesize
            speed: Speech speed multiplier (1.0 = normal)

        Returns:
            Estimated duration in seconds
        """
        pass
