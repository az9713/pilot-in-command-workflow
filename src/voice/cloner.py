"""
Voice cloning using XTTS-v2.

Extracts speaker embeddings from reference audio for voice cloning.
Uses VRAM-aware loading and automatic cleanup.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import torch
import torchaudio

from ..utils.vram import VRAMManager
from .interfaces import CloneResult, VoiceClonerInterface
from .profiles import VoiceProfileManager

logger = logging.getLogger(__name__)

# XTTS-v2 supported languages (17 total)
XTTS_LANGUAGES = [
    "en",  # English
    "es",  # Spanish
    "fr",  # French
    "de",  # German
    "it",  # Italian
    "pt",  # Portuguese
    "pl",  # Polish
    "tr",  # Turkish
    "ru",  # Russian
    "nl",  # Dutch
    "cs",  # Czech
    "ar",  # Arabic
    "zh-cn",  # Chinese (Simplified)
    "ja",  # Japanese
    "hu",  # Hungarian
    "ko",  # Korean
    "hi",  # Hindi
]


class XTTSVoiceCloner(VoiceClonerInterface):
    """
    XTTS-v2 voice cloning implementation.

    Uses Coqui XTTS-v2 model to extract speaker embeddings from
    reference audio. Manages VRAM loading and cleanup automatically.
    """

    def __init__(
        self,
        config: dict,
        vram_manager: VRAMManager,
        profile_manager: VoiceProfileManager,
    ):
        """
        Initialize XTTS voice cloner.

        Args:
            config: Configuration dict (voice.xtts section)
            vram_manager: VRAM management instance
            profile_manager: Voice profile manager
        """
        self.config = config
        self.vram_manager = vram_manager
        self.profile_manager = profile_manager
        self._model = None
        self._device = None

        # Model settings
        self.vram_requirement_mb = 4096  # XTTS-v2 requires ~4GB
        self.min_audio_seconds = 3.0
        self.recommended_audio_seconds = 6.0

        logger.info("XTTS voice cloner initialized")

    def clone_voice(
        self, reference_audio: Path, profile_name: str, language: str = "en"
    ) -> CloneResult:
        """
        Clone a voice from reference audio.

        Args:
            reference_audio: Path to reference audio file
            profile_name: Name for the voice profile
            language: Language code (default: 'en')

        Returns:
            CloneResult with success status and profile
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not reference_audio.exists():
                raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

            if language not in XTTS_LANGUAGES:
                raise ValueError(
                    f"Unsupported language: {language}. "
                    f"Supported: {', '.join(XTTS_LANGUAGES)}"
                )

            # Validate audio duration
            duration = self._get_audio_duration(reference_audio)
            if duration < self.min_audio_seconds:
                raise ValueError(
                    f"Audio too short: {duration:.1f}s "
                    f"(minimum {self.min_audio_seconds}s, "
                    f"recommended {self.recommended_audio_seconds}s)"
                )

            if duration < self.recommended_audio_seconds:
                logger.warning(
                    f"Audio duration {duration:.1f}s is below recommended "
                    f"{self.recommended_audio_seconds}s"
                )

            # Check VRAM availability
            if not self.vram_manager.can_load(self.vram_requirement_mb):
                raise RuntimeError(
                    f"Insufficient VRAM: need {self.vram_requirement_mb}MB for XTTS-v2"
                )

            # Load model
            self._load_model()

            # Extract speaker embedding
            logger.info(f"Extracting speaker embedding from {reference_audio}")
            embedding = self._extract_embedding(reference_audio)

            # Unload model and cleanup
            self._unload_model()

            # Create profile
            profile = self.profile_manager.create_profile(
                name=profile_name,
                language=language,
                embedding=embedding,
                reference_audio=reference_audio,
            )

            processing_time = time.time() - start_time
            logger.info(
                f"Voice cloning successful: {profile.profile_id} "
                f"({processing_time:.2f}s)"
            )

            return CloneResult(
                success=True,
                profile=profile,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Voice cloning failed: {e}")

            # Ensure cleanup on error
            self._unload_model()

            return CloneResult(
                success=False,
                profile=None,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def get_supported_languages(self) -> list[str]:
        """Get list of supported language codes."""
        return XTTS_LANGUAGES.copy()

    def _load_model(self) -> None:
        """Load XTTS-v2 model into memory."""
        if self._model is not None:
            logger.debug("XTTS model already loaded")
            return

        try:
            logger.info("Loading XTTS-v2 model...")
            from TTS.api import TTS

            # Determine device
            if torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"
                logger.warning("CUDA not available, using CPU (will be slow)")

            # Load XTTS-v2 model
            self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(
                self._device
            )

            logger.info(f"XTTS-v2 model loaded on {self._device}")
            self.vram_manager.log_status()

        except Exception as e:
            logger.error(f"Failed to load XTTS model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def _unload_model(self) -> None:
        """Unload model and free VRAM."""
        if self._model is None:
            return

        try:
            logger.debug("Unloading XTTS model...")

            # Delete model
            del self._model
            self._model = None
            self._device = None

            # Force cleanup
            self.vram_manager.force_cleanup()

        except Exception as e:
            logger.error(f"Error during model unload: {e}")

    def _extract_embedding(self, audio_path: Path) -> torch.Tensor:
        """
        Extract speaker embedding from audio.

        Args:
            audio_path: Path to audio file

        Returns:
            Speaker embedding tensor
        """
        if self._model is None:
            raise RuntimeError("Model not loaded")

        try:
            # XTTS-v2 requires audio in specific format
            # Load and resample to 22050 Hz if needed
            waveform, sample_rate = torchaudio.load(audio_path)

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Resample to 22050 Hz (XTTS requirement)
            if sample_rate != 22050:
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sample_rate, new_freq=22050
                )
                waveform = resampler(waveform)

            # Extract embedding using XTTS encoder
            # Note: XTTS uses the synthesizer's internal speaker encoder
            embedding = self._model.synthesizer.tts_model.speaker_manager.encoder.forward(
                waveform.to(self._device), l2_norm=True
            )

            logger.debug(f"Extracted embedding shape: {embedding.shape}")
            return embedding.cpu()

        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            raise RuntimeError(f"Failed to extract embedding: {e}") from e

    def _get_audio_duration(self, audio_path: Path) -> float:
        """
        Get audio duration in seconds.

        Args:
            audio_path: Path to audio file

        Returns:
            Duration in seconds
        """
        try:
            import soundfile as sf
            info = sf.info(str(audio_path))
            return info.duration

        except Exception as e:
            logger.error(f"Failed to get audio duration: {e}")
            raise RuntimeError(f"Audio validation failed: {e}") from e
