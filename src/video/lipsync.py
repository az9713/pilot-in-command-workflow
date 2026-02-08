"""
Lip-sync video generation using MuseTalk.

Generates talking head videos from static avatar images and audio files.
Uses VRAM-aware loading and automatic cleanup.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import torch
import torchaudio
from PIL import Image

from ..utils.vram import VRAMManager
from .interfaces import LipSyncConfig, LipSyncEngineInterface, LipSyncResult

logger = logging.getLogger(__name__)

# Quality presets for lip-sync generation
QUALITY_PRESETS = {
    "high": {"fps": 25, "face_det_batch": 1, "wav2lip_batch": 1},
    "medium": {"fps": 25, "face_det_batch": 2, "wav2lip_batch": 2},
    "low": {"fps": 25, "face_det_batch": 4, "wav2lip_batch": 4},
}


class MuseTalkLipSync(LipSyncEngineInterface):
    """
    MuseTalk lip-sync implementation.

    Uses MuseTalk model to generate lip-synced talking head videos.
    Falls back to simple image-to-video conversion if MuseTalk is unavailable.

    Note:
        MuseTalk is not a standard pip package. Install manually from:
        https://github.com/TMElyralab/MuseTalk

        If MuseTalk is not available, this implementation will create
        a fallback video using the static avatar image with audio overlay.
    """

    def __init__(self, config: dict, vram_manager: VRAMManager):
        """
        Initialize MuseTalk lip-sync engine.

        Args:
            config: Configuration dict (video.lipsync section)
            vram_manager: VRAM management instance
        """
        self.config = config
        self.vram_manager = vram_manager
        self._model = None
        self._device = None
        self._musetalk_available = False

        # Model settings
        self.vram_requirement_mb = 5120  # MuseTalk requires ~5GB
        self.max_video_seconds = 120.0  # Maximum video length

        # Check MuseTalk availability
        try:
            import musetalk  # noqa: F401

            self._musetalk_available = True
            logger.info("MuseTalk library detected")
        except ImportError:
            logger.warning(
                "MuseTalk library not found. Using fallback mode. "
                "Install from: https://github.com/TMElyralab/MuseTalk"
            )

        logger.info(
            f"MuseTalk lip-sync initialized (fallback mode: {not self._musetalk_available})"
        )

    def generate(
        self,
        avatar_image: Path,
        audio_file: Path,
        output_path: Path,
        config: Optional[LipSyncConfig] = None,
    ) -> LipSyncResult:
        """
        Generate lip-synced video from avatar image and audio.

        Args:
            avatar_image: Path to avatar image
            audio_file: Path to audio file
            output_path: Where to save video
            config: Optional lip-sync configuration

        Returns:
            LipSyncResult with success status and video info
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not avatar_image.exists():
                raise FileNotFoundError(f"Avatar image not found: {avatar_image}")

            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_file}")

            # Get audio duration
            audio_duration = self._get_audio_duration(audio_file)

            if audio_duration > self.max_video_seconds:
                raise ValueError(
                    f"Audio too long: {audio_duration:.1f}s "
                    f"(maximum {self.max_video_seconds}s)"
                )

            # Use default config if none provided
            if config is None:
                config = LipSyncConfig()

            # Apply quality preset
            if config.quality in QUALITY_PRESETS:
                preset = QUALITY_PRESETS[config.quality]
                config.fps = preset["fps"]
                config.face_det_batch_size = preset["face_det_batch"]
                config.wav2lip_batch_size = preset["wav2lip_batch"]

            logger.info(f"Generating lip-sync video: {avatar_image} + {audio_file}")
            logger.info(
                f"Config: {config.fps}fps, quality={config.quality}, duration={audio_duration:.1f}s"
            )

            # Choose generation method
            if self._musetalk_available:
                result = self._generate_with_musetalk(
                    avatar_image, audio_file, output_path, config, audio_duration
                )
            else:
                result = self._generate_fallback(
                    avatar_image, audio_file, output_path, config, audio_duration
                )

            processing_time = time.time() - start_time
            logger.info(f"Lip-sync generation complete ({processing_time:.2f}s)")

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Lip-sync generation failed: {e}")

            # Ensure cleanup on error
            self._unload_model()

            return LipSyncResult(
                success=False,
                video_path=None,
                duration_seconds=0.0,
                frame_count=0,
                fps=0,
                resolution=(0, 0),
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def get_supported_formats(self) -> dict[str, list[str]]:
        """Get supported input/output formats."""
        return {
            "image": ["png", "jpg", "jpeg"],
            "audio": ["wav", "mp3", "flac"],
            "video": ["mp4"],
        }

    def _generate_with_musetalk(
        self,
        avatar_image: Path,
        audio_file: Path,
        output_path: Path,
        config: LipSyncConfig,
        audio_duration: float,
    ) -> LipSyncResult:
        """
        Generate video using MuseTalk model.

        Args:
            avatar_image: Path to avatar image
            audio_file: Path to audio file
            output_path: Where to save video
            config: Lip-sync configuration
            audio_duration: Duration of audio in seconds

        Returns:
            LipSyncResult with generation results
        """
        # Check VRAM availability
        if not self.vram_manager.can_load(self.vram_requirement_mb):
            raise RuntimeError(
                f"Insufficient VRAM: need {self.vram_requirement_mb}MB for MuseTalk"
            )

        # Load model
        self._load_model()

        try:
            # Preprocess avatar image
            avatar_tensor = self._preprocess_avatar(avatar_image)

            # Extract audio features
            audio_features = self._extract_audio_features(audio_file)

            # Generate video frames
            logger.info("Generating lip-sync frames...")
            frames = self._model.generate_frames(
                avatar=avatar_tensor,
                audio_features=audio_features,
                fps=config.fps,
                batch_size=config.wav2lip_batch_size,
            )

            # Get video metadata
            frame_count = len(frames)
            height, width = frames[0].shape[:2]

            # Save video
            self._save_video(
                frames, audio_file, output_path, fps=config.fps
            )

            # Unload model and cleanup
            self._unload_model()

            processing_time = time.time()

            return LipSyncResult(
                success=True,
                video_path=output_path,
                duration_seconds=audio_duration,
                frame_count=frame_count,
                fps=config.fps,
                resolution=(width, height),
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            logger.error(f"MuseTalk generation failed: {e}")
            self._unload_model()
            raise

    def _generate_fallback(
        self,
        avatar_image: Path,
        audio_file: Path,
        output_path: Path,
        config: LipSyncConfig,
        audio_duration: float,
    ) -> LipSyncResult:
        """
        Generate video using fallback method (static image + audio).

        Args:
            avatar_image: Path to avatar image
            audio_file: Path to audio file
            output_path: Where to save video
            config: Lip-sync configuration
            audio_duration: Duration of audio in seconds

        Returns:
            LipSyncResult with generation results
        """
        logger.info("Using fallback mode: static image with audio overlay")

        try:
            # Import FFmpeg encoder for video creation
            from .encoder import FFmpegEncoder

            encoder = FFmpegEncoder()

            # Load avatar image to get dimensions
            image = Image.open(avatar_image)
            width, height = image.size

            # Calculate frame count
            frame_count = int(audio_duration * config.fps)

            # Create video from static image using FFmpeg
            output_path.parent.mkdir(parents=True, exist_ok=True)

            import subprocess

            # Use FFmpeg to create video from static image with audio
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-loop", "1",  # Loop the image
                "-i", str(avatar_image),  # Input image
                "-i", str(audio_file),  # Input audio
                "-c:v", "libx264",  # Video codec
                "-tune", "stillimage",  # Optimize for static image
                "-c:a", "aac",  # Audio codec
                "-b:a", "192k",  # Audio bitrate
                "-pix_fmt", "yuv420p",  # Pixel format for compatibility
                "-shortest",  # Match video length to audio
                "-r", str(config.fps),  # Frame rate
                str(output_path),
            ]

            logger.debug(f"FFmpeg command: {' '.join(cmd)}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f"FFmpeg failed: {result.stderr}"
                )

            logger.info(f"Fallback video created: {output_path}")

            processing_time = time.time()

            return LipSyncResult(
                success=True,
                video_path=output_path,
                duration_seconds=audio_duration,
                frame_count=frame_count,
                fps=config.fps,
                resolution=(width, height),
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            raise

    def _load_model(self) -> None:
        """Load MuseTalk model into memory."""
        if self._model is not None:
            logger.debug("MuseTalk model already loaded")
            return

        if not self._musetalk_available:
            raise RuntimeError("MuseTalk not available, cannot load model")

        try:
            logger.info("Loading MuseTalk model...")
            import musetalk

            # Determine device
            if torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"
                logger.warning("CUDA not available, using CPU (will be very slow)")

            # Load MuseTalk model
            self._model = musetalk.MuseTalkModel(device=self._device)

            logger.info(f"MuseTalk model loaded on {self._device}")
            self.vram_manager.log_status()

        except Exception as e:
            logger.error(f"Failed to load MuseTalk model: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def _unload_model(self) -> None:
        """Unload model and free VRAM."""
        if self._model is None:
            return

        try:
            logger.debug("Unloading MuseTalk model...")

            # Delete model
            del self._model
            self._model = None
            self._device = None

            # Force cleanup
            self.vram_manager.force_cleanup()

        except Exception as e:
            logger.error(f"Error during model unload: {e}")

    def _preprocess_avatar(self, image_path: Path) -> torch.Tensor:
        """
        Preprocess avatar image for MuseTalk.

        Args:
            image_path: Path to avatar image

        Returns:
            Preprocessed image tensor
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")

            # Convert to tensor and normalize (MuseTalk expects [0, 1] range)
            import torchvision.transforms as transforms

            transform = transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]
                    ),
                ]
            )

            tensor = transform(image).unsqueeze(0)  # Add batch dimension

            if self._device:
                tensor = tensor.to(self._device)

            logger.debug(f"Preprocessed avatar: shape={tensor.shape}")
            return tensor

        except Exception as e:
            logger.error(f"Avatar preprocessing failed: {e}")
            raise RuntimeError(f"Failed to preprocess avatar: {e}") from e

    def _extract_audio_features(self, audio_path: Path) -> torch.Tensor:
        """
        Extract audio features for MuseTalk.

        Args:
            audio_path: Path to audio file

        Returns:
            Audio feature tensor (mel spectrogram)
        """
        try:
            # Load audio
            waveform, sample_rate = torchaudio.load(audio_path)

            # Convert to mono if stereo
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)

            # Resample to 16kHz (MuseTalk requirement)
            if sample_rate != 16000:
                resampler = torchaudio.transforms.Resample(
                    orig_freq=sample_rate, new_freq=16000
                )
                waveform = resampler(waveform)

            # Extract mel spectrogram
            mel_transform = torchaudio.transforms.MelSpectrogram(
                sample_rate=16000,
                n_fft=1024,
                hop_length=256,
                n_mels=80,
            )

            mel_spec = mel_transform(waveform)

            if self._device:
                mel_spec = mel_spec.to(self._device)

            logger.debug(f"Extracted audio features: shape={mel_spec.shape}")
            return mel_spec

        except Exception as e:
            logger.error(f"Audio feature extraction failed: {e}")
            raise RuntimeError(f"Failed to extract audio features: {e}") from e

    def _save_video(
        self, frames: list, audio_path: Path, output_path: Path, fps: int
    ) -> None:
        """
        Save generated frames as video with audio.

        Args:
            frames: List of video frames (numpy arrays)
            audio_path: Path to audio file to add
            output_path: Where to save video
            fps: Frames per second
        """
        try:
            import cv2
            import numpy as np

            # Get frame dimensions
            height, width = frames[0].shape[:2]

            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            temp_video = output_path.with_suffix(".temp.mp4")

            writer = cv2.VideoWriter(
                str(temp_video), fourcc, fps, (width, height)
            )

            # Write frames
            for frame in frames:
                # Convert RGB to BGR for OpenCV
                if isinstance(frame, torch.Tensor):
                    frame = frame.cpu().numpy()

                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                writer.write(frame_bgr)

            writer.release()

            # Add audio using FFmpeg
            from .encoder import FFmpegEncoder

            encoder = FFmpegEncoder()
            result = encoder.add_audio(temp_video, audio_path, output_path)

            # Clean up temp file
            if temp_video.exists():
                temp_video.unlink()

            if not result.success:
                raise RuntimeError(f"Failed to add audio: {result.error}")

            logger.debug(f"Saved video: {output_path}")

        except Exception as e:
            logger.error(f"Video saving failed: {e}")
            raise RuntimeError(f"Failed to save video: {e}") from e

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
