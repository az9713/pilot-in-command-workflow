"""
Pipeline coordinator for avatar video generation.

Orchestrates the full pipeline from text to video:
1. TTS synthesis
2. Avatar validation
3. Lip-sync generation
4. Final encoding
"""

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..avatar import MediaPipeFaceDetector
from ..utils import VRAMManager
from ..video import FFmpegEncoder, LipSyncConfig, MuseTalkLipSync
from ..voice import CoquiTTSSynthesizer, VoiceProfileManager

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """
    Pipeline execution configuration.

    Attributes:
        max_video_length_seconds: Maximum allowed video duration
        output_format: Video output format (default: mp4)
        cleanup_intermediates: Remove intermediate files after completion
        video_quality: Lip-sync quality preset (high, medium, low)
        video_fps: Video frame rate (None = use quality preset default)
        encoding_preset: FFmpeg encoding preset
        encoding_crf: FFmpeg CRF quality (0-51, lower is better)
    """

    max_video_length_seconds: int = 120
    output_format: str = "mp4"
    cleanup_intermediates: bool = True
    video_quality: str = "high"
    video_fps: Optional[int] = None
    encoding_preset: str = "medium"
    encoding_crf: int = 23


@dataclass
class PipelineResult:
    """
    Result of pipeline execution.

    Attributes:
        success: Whether pipeline completed successfully
        job_id: Job ID (if async execution)
        output_path: Path to final video file
        duration_seconds: Video duration in seconds
        stages_completed: List of completed stages
        error: Error message if failed
        processing_time_seconds: Total processing time
        intermediate_files: Paths to intermediate files (if not cleaned up)
    """

    success: bool
    job_id: Optional[str]
    output_path: Optional[Path]
    duration_seconds: float
    stages_completed: list[str]
    error: Optional[str]
    processing_time_seconds: float
    intermediate_files: Optional[dict] = None


class PipelineCoordinator:
    """
    Orchestrates the full avatar video generation pipeline.

    Coordinates sequential model loading and execution:
    1. Text-to-speech synthesis
    2. Avatar face validation
    3. Lip-sync video generation
    4. Final video encoding

    Manages VRAM efficiently by loading models sequentially and
    cleaning up between stages.
    """

    def __init__(
        self,
        config: dict,
        vram_manager: VRAMManager,
        storage_path: Path,
    ):
        """
        Initialize pipeline coordinator.

        Args:
            config: Configuration dictionary
            vram_manager: VRAM management instance
            storage_path: Base storage path for profiles and temp files
        """
        self.config = config
        self.vram_manager = vram_manager
        self.storage_path = Path(storage_path)

        # Create temp directory for intermediate files
        self.temp_dir = self.storage_path / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # Initialize component managers (lightweight, no models loaded)
        self.voice_profile_manager = VoiceProfileManager(storage_path)
        self.face_detector = MediaPipeFaceDetector()

        logger.info("Pipeline coordinator initialized")

    def execute(
        self,
        text: str,
        voice_profile_id: str,
        avatar_image: Path,
        output_path: Path,
        config: Optional[PipelineConfig] = None,
    ) -> PipelineResult:
        """
        Execute the full avatar video pipeline.

        Args:
            text: Text to synthesize
            voice_profile_id: Voice profile ID for TTS
            avatar_image: Path to avatar image
            output_path: Where to save final video
            config: Optional pipeline configuration

        Returns:
            PipelineResult with execution status and output info

        Pipeline stages:
            1. Load voice profile
            2. Synthesize speech (TTS)
            3. Validate avatar face
            4. Generate lip-sync video
            5. Encode final output
            6. Cleanup intermediates
        """
        start_time = time.time()
        stages_completed = []
        intermediate_files = {}

        # Use default config if none provided
        if config is None:
            config = PipelineConfig()

        try:
            logger.info("=" * 60)
            logger.info("Starting avatar video pipeline")
            logger.info(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
            logger.info(f"Voice profile: {voice_profile_id}")
            logger.info(f"Avatar image: {avatar_image}")
            logger.info(f"Output: {output_path}")
            logger.info("=" * 60)

            # Stage 1: Load voice profile
            logger.info("\n[Stage 1/5] Loading voice profile...")
            voice_profile = self.voice_profile_manager.load_profile(voice_profile_id)
            logger.info(f"Loaded profile: {voice_profile.name} ({voice_profile.language})")
            stages_completed.append("load_profile")

            # Stage 2: Synthesize speech
            logger.info("\n[Stage 2/5] Synthesizing speech...")
            audio_path = self.temp_dir / f"speech_{int(time.time())}.wav"

            synthesizer = CoquiTTSSynthesizer(
                config=self.config.get("voice", {}).get("tts", {}),
                vram_manager=self.vram_manager,
            )

            synthesis_result = synthesizer.synthesize(text, voice_profile, audio_path)

            if not synthesis_result.success:
                raise RuntimeError(f"Speech synthesis failed: {synthesis_result.error}")

            logger.info(
                f"Speech synthesized: {synthesis_result.duration_seconds:.2f}s "
                f"({synthesis_result.processing_time_seconds:.2f}s processing)"
            )
            intermediate_files["audio"] = synthesis_result.audio_path
            stages_completed.append("synthesize_speech")

            # Check video duration limit
            if synthesis_result.duration_seconds > config.max_video_length_seconds:
                raise ValueError(
                    f"Audio too long: {synthesis_result.duration_seconds:.1f}s "
                    f"(maximum: {config.max_video_length_seconds}s)"
                )

            # Stage 3: Validate avatar face
            logger.info("\n[Stage 3/5] Validating avatar face...")

            if not avatar_image.exists():
                raise FileNotFoundError(f"Avatar image not found: {avatar_image}")

            detection = self.face_detector.detect(avatar_image)

            if not detection.detected:
                raise ValueError("No face detected in avatar image")

            is_valid, message = self.face_detector.validate_for_lipsync(detection)

            if not is_valid:
                raise ValueError(f"Avatar face validation failed: {message}")

            logger.info(f"Avatar validated: {message}")
            stages_completed.append("validate_avatar")

            # Stage 4: Generate lip-sync video
            logger.info("\n[Stage 4/5] Generating lip-sync video...")
            lipsync_path = self.temp_dir / f"lipsync_{int(time.time())}.mp4"

            lipsync_engine = MuseTalkLipSync(
                config=self.config.get("video", {}).get("lipsync", {}),
                vram_manager=self.vram_manager,
            )

            # Create lip-sync config
            lipsync_config = LipSyncConfig(quality=config.video_quality)
            if config.video_fps is not None:
                lipsync_config.fps = config.video_fps

            lipsync_result = lipsync_engine.generate(
                avatar_image=avatar_image,
                audio_file=synthesis_result.audio_path,
                output_path=lipsync_path,
                config=lipsync_config,
            )

            if not lipsync_result.success:
                raise RuntimeError(f"Lip-sync generation failed: {lipsync_result.error}")

            logger.info(
                f"Lip-sync video generated: {lipsync_result.duration_seconds:.2f}s, "
                f"{lipsync_result.frame_count} frames @ {lipsync_result.fps}fps "
                f"({lipsync_result.processing_time_seconds:.2f}s processing)"
            )
            intermediate_files["lipsync"] = lipsync_result.video_path
            stages_completed.append("generate_lipsync")

            # Stage 5: Encode final output
            logger.info("\n[Stage 5/5] Encoding final video...")
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            encoder = FFmpegEncoder()

            # Import encoding config
            from ..video import EncodingConfig

            encoding_config = EncodingConfig(
                preset=config.encoding_preset,
                crf=config.encoding_crf,
            )

            encoding_result = encoder.encode(
                input_video=lipsync_result.video_path,
                output_path=output_path,
                config=encoding_config,
            )

            if not encoding_result.success:
                raise RuntimeError(f"Video encoding failed: {encoding_result.error}")

            logger.info(
                f"Final video encoded: {encoding_result.file_size_bytes / 1024 / 1024:.2f}MB "
                f"({encoding_result.processing_time_seconds:.2f}s processing)"
            )
            stages_completed.append("encode_video")

            # Stage 6: Cleanup intermediate files
            if config.cleanup_intermediates:
                logger.info("\n[Stage 6/6] Cleaning up intermediate files...")
                self._cleanup_files(intermediate_files)
                intermediate_files = None
            else:
                logger.info("\n[Stage 6/6] Keeping intermediate files")

            # Calculate total processing time
            processing_time = time.time() - start_time

            logger.info("\n" + "=" * 60)
            logger.info("Pipeline completed successfully!")
            logger.info(f"Output: {output_path}")
            logger.info(f"Duration: {encoding_result.duration_seconds:.2f}s")
            logger.info(f"Processing time: {processing_time:.2f}s")
            logger.info("=" * 60)

            return PipelineResult(
                success=True,
                job_id=None,
                output_path=output_path,
                duration_seconds=encoding_result.duration_seconds,
                stages_completed=stages_completed,
                error=None,
                processing_time_seconds=processing_time,
                intermediate_files=intermediate_files,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Pipeline failed at stage {len(stages_completed) + 1}: {e}")

            # Cleanup on error
            if intermediate_files and config.cleanup_intermediates:
                self._cleanup_files(intermediate_files)

            return PipelineResult(
                success=False,
                job_id=None,
                output_path=None,
                duration_seconds=0.0,
                stages_completed=stages_completed,
                error=str(e),
                processing_time_seconds=processing_time,
                intermediate_files=None,
            )

    def estimate_duration(self, text: str, voice_profile_id: str) -> dict:
        """
        Estimate pipeline execution time.

        Args:
            text: Text to synthesize
            voice_profile_id: Voice profile ID

        Returns:
            Dictionary with duration estimates:
                - audio_duration: Estimated audio duration in seconds
                - processing_time: Estimated total processing time in seconds
                - stages: Per-stage time estimates

        Note:
            These are rough estimates based on typical hardware performance.
            Actual times may vary significantly.
        """
        try:
            # Load voice profile
            voice_profile = self.voice_profile_manager.load_profile(voice_profile_id)

            # Estimate audio duration
            synthesizer = CoquiTTSSynthesizer(
                config=self.config.get("voice", {}).get("tts", {}),
                vram_manager=self.vram_manager,
            )
            audio_duration = synthesizer.estimate_duration(text)

            # Estimate processing times (rough approximations)
            # These vary significantly based on hardware
            estimates = {
                "audio_duration": audio_duration,
                "stages": {
                    "load_profile": 0.1,
                    "synthesize_speech": max(5.0, audio_duration * 2),  # ~2x realtime
                    "validate_avatar": 0.5,
                    "generate_lipsync": max(10.0, audio_duration * 5),  # ~5x realtime
                    "encode_video": max(2.0, audio_duration * 0.5),  # ~0.5x realtime
                },
            }

            # Calculate total
            estimates["processing_time"] = sum(estimates["stages"].values())

            logger.info(
                f"Estimated pipeline duration: {audio_duration:.1f}s audio, "
                f"{estimates['processing_time']:.1f}s processing"
            )

            return estimates

        except Exception as e:
            logger.error(f"Duration estimation failed: {e}")
            return {
                "audio_duration": 0.0,
                "processing_time": 0.0,
                "stages": {},
                "error": str(e),
            }

    def _cleanup_files(self, files: dict) -> None:
        """
        Clean up intermediate files.

        Args:
            files: Dictionary of file category -> path
        """
        cleaned_count = 0

        for category, file_path in files.items():
            if file_path and Path(file_path).exists():
                try:
                    Path(file_path).unlink()
                    logger.debug(f"Deleted {category} file: {file_path}")
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete {category} file {file_path}: {e}")

        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} intermediate file(s)")
