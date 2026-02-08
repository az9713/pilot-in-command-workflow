"""
TTS synthesis using Coqui TTS.

Generates speech from text using cloned voice profiles.
Uses VRAM-aware loading and automatic cleanup.
"""

import logging
import time
from pathlib import Path

import torch
import torchaudio

from ..utils.vram import VRAMManager
from .interfaces import SynthesisResult, TTSSynthesizerInterface, VoiceProfile

logger = logging.getLogger(__name__)


class CoquiTTSSynthesizer(TTSSynthesizerInterface):
    """
    Coqui TTS synthesis implementation.

    Uses Coqui TTS with XTTS-v2 model to generate speech from text
    using cloned voice profiles. Manages VRAM loading and cleanup.
    """

    def __init__(self, config: dict, vram_manager: VRAMManager):
        """
        Initialize Coqui TTS synthesizer.

        Args:
            config: Configuration dict (voice.tts section)
            vram_manager: VRAM management instance
        """
        self.config = config
        self.vram_manager = vram_manager
        self._model = None
        self._device = None

        # Model settings
        self.vram_requirement_mb = 3072  # TTS requires ~3GB
        self.max_text_length = 5000
        self.default_sample_rate = 22050

        logger.info("Coqui TTS synthesizer initialized")

    def synthesize(
        self, text: str, voice_profile: VoiceProfile, output_path: Path
    ) -> SynthesisResult:
        """
        Synthesize speech from text using voice profile.

        Args:
            text: Text to synthesize
            voice_profile: Voice profile with speaker embedding
            output_path: Where to save generated audio

        Returns:
            SynthesisResult with success status and audio info
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            if len(text) > self.max_text_length:
                raise ValueError(
                    f"Text too long: {len(text)} characters "
                    f"(maximum {self.max_text_length})"
                )

            if not voice_profile.embedding_path.exists():
                raise FileNotFoundError(
                    f"Embedding not found: {voice_profile.embedding_path}"
                )

            # Check VRAM availability
            if not self.vram_manager.can_load(self.vram_requirement_mb):
                raise RuntimeError(
                    f"Insufficient VRAM: need {self.vram_requirement_mb}MB for TTS"
                )

            # Load model
            self._load_model()

            # Load speaker embedding
            embedding = torch.load(voice_profile.embedding_path)
            if embedding.device.type != "cpu":
                embedding = embedding.cpu()

            # Generate speech
            logger.info(
                f"Synthesizing speech with profile {voice_profile.profile_id} "
                f"({len(text)} chars)"
            )
            audio_waveform = self._generate_speech(
                text, embedding, voice_profile.language
            )

            # Save audio
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_audio(audio_waveform, output_path)

            # Calculate duration
            duration = len(audio_waveform) / self.default_sample_rate

            # Unload model and cleanup
            self._unload_model()

            processing_time = time.time() - start_time
            logger.info(
                f"Speech synthesis successful: {output_path.name} "
                f"({duration:.2f}s audio, {processing_time:.2f}s processing)"
            )

            return SynthesisResult(
                success=True,
                audio_path=output_path,
                duration_seconds=duration,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Speech synthesis failed: {e}")

            # Ensure cleanup on error
            self._unload_model()

            return SynthesisResult(
                success=False,
                audio_path=None,
                duration_seconds=0.0,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def estimate_duration(self, text: str, speed: float = 1.0) -> float:
        """
        Estimate audio duration for given text.

        Args:
            text: Text to synthesize
            speed: Speech speed multiplier (1.0 = normal)

        Returns:
            Estimated duration in seconds

        Note:
            Uses rough estimate of ~150 words per minute at normal speed.
        """
        # Count words
        words = len(text.split())

        # Estimate at 150 WPM (2.5 words per second)
        base_duration = words / 2.5

        # Adjust for speed
        duration = base_duration / speed

        return duration

    def _load_model(self) -> None:
        """Load TTS model into memory."""
        if self._model is not None:
            logger.debug("TTS model already loaded")
            return

        try:
            logger.info("Loading Coqui TTS model...")
            from TTS.api import TTS

            # Determine device
            if torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"
                logger.warning("CUDA not available, using CPU (will be slow)")

            # Load XTTS-v2 model (same as cloner)
            self._model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(
                self._device
            )

            logger.info(f"TTS model loaded on {self._device}")
            self.vram_manager.log_status()

        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def _unload_model(self) -> None:
        """Unload model and free VRAM."""
        if self._model is None:
            return

        try:
            logger.debug("Unloading TTS model...")

            # Delete model
            del self._model
            self._model = None
            self._device = None

            # Force cleanup
            self.vram_manager.force_cleanup()

        except Exception as e:
            logger.error(f"Error during model unload: {e}")

    def _generate_speech(
        self, text: str, speaker_embedding: torch.Tensor, language: str
    ) -> torch.Tensor:
        """
        Generate speech waveform from text.

        Args:
            text: Text to synthesize
            speaker_embedding: Speaker embedding tensor
            language: Language code

        Returns:
            Audio waveform tensor
        """
        if self._model is None:
            raise RuntimeError("Model not loaded")

        try:
            # Move embedding to correct device
            speaker_embedding = speaker_embedding.to(self._device)

            # Generate speech using XTTS with speaker embedding
            # XTTS tts_with_vc method takes text and speaker embedding
            outputs = self._model.synthesizer.tts_model.inference(
                text=text,
                language=language,
                gpt_cond_latent=speaker_embedding,
                speaker_embedding=speaker_embedding,
            )

            # Convert to tensor if needed
            if not isinstance(outputs, torch.Tensor):
                waveform = torch.tensor(outputs["wav"])
            else:
                waveform = outputs

            logger.debug(f"Generated waveform shape: {waveform.shape}")
            return waveform.cpu()

        except Exception as e:
            logger.error(f"Speech generation failed: {e}")
            raise RuntimeError(f"Failed to generate speech: {e}") from e

    def _save_audio(self, waveform: torch.Tensor, output_path: Path) -> None:
        """
        Save audio waveform to file.

        Args:
            waveform: Audio waveform tensor
            output_path: Output file path (WAV)
        """
        try:
            # Ensure waveform is 2D (channels, samples)
            if waveform.dim() == 1:
                waveform = waveform.unsqueeze(0)

            # Save as WAV
            torchaudio.save(
                output_path, waveform, self.default_sample_rate, encoding="PCM_S"
            )

            logger.debug(f"Saved audio to {output_path}")

        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise IOError(f"Audio save failed: {e}") from e
