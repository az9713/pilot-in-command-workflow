"""
Video encoding using FFmpeg.

Provides video encoding, audio mixing, and video manipulation using FFmpeg.
"""

import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

from .interfaces import EncodingConfig, EncodingResult, VideoEncoderInterface

logger = logging.getLogger(__name__)


class FFmpegEncoder(VideoEncoderInterface):
    """
    FFmpeg video encoder implementation.

    Uses FFmpeg to encode, transcode, and manipulate video files.
    Requires FFmpeg to be installed and available in system PATH.
    """

    def __init__(self):
        """Initialize FFmpeg encoder."""
        self._ffmpeg_available = self._check_ffmpeg()

        if not self._ffmpeg_available:
            logger.warning(
                "FFmpeg not found in PATH. Video encoding will not work. "
                "Install FFmpeg: https://ffmpeg.org/download.html"
            )
        else:
            logger.info("FFmpeg encoder initialized")

    def encode(
        self,
        input_video: Path,
        output_path: Path,
        config: Optional[EncodingConfig] = None,
    ) -> EncodingResult:
        """
        Encode or transcode video file.

        Args:
            input_video: Path to input video file
            output_path: Where to save encoded video
            config: Optional encoding configuration

        Returns:
            EncodingResult with success status and file info
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not input_video.exists():
                raise FileNotFoundError(f"Input video not found: {input_video}")

            if not self._ffmpeg_available:
                raise RuntimeError("FFmpeg not available")

            # Use default config if none provided
            if config is None:
                config = EncodingConfig()

            logger.info(f"Encoding video: {input_video} -> {output_path}")
            logger.info(
                f"Config: codec={config.codec}, preset={config.preset}, crf={config.crf}"
            )

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg command
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", str(input_video),  # Input file
                "-c:v", config.codec,  # Video codec
                "-preset", config.preset,  # Encoding preset
                "-crf", str(config.crf),  # Quality setting
                "-c:a", config.audio_codec,  # Audio codec
                "-b:a", config.audio_bitrate,  # Audio bitrate
                "-pix_fmt", "yuv420p",  # Pixel format for compatibility
                str(output_path),
            ]

            logger.debug(f"FFmpeg command: {' '.join(cmd)}")

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg encoding failed: {result.stderr}")

            # Get output file info
            file_size = output_path.stat().st_size
            duration = self._get_video_duration(output_path)

            processing_time = time.time() - start_time
            logger.info(
                f"Encoding complete: {file_size / 1024 / 1024:.2f}MB, "
                f"{duration:.1f}s, took {processing_time:.2f}s"
            )

            return EncodingResult(
                success=True,
                output_path=output_path,
                file_size_bytes=file_size,
                duration_seconds=duration,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Video encoding failed: {e}")

            return EncodingResult(
                success=False,
                output_path=None,
                file_size_bytes=0,
                duration_seconds=0.0,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def add_audio(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
    ) -> EncodingResult:
        """
        Add or replace audio track in video.

        Args:
            video_path: Path to input video file
            audio_path: Path to audio file to add
            output_path: Where to save output video

        Returns:
            EncodingResult with success status and file info
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not video_path.exists():
                raise FileNotFoundError(f"Video not found: {video_path}")

            if not audio_path.exists():
                raise FileNotFoundError(f"Audio not found: {audio_path}")

            if not self._ffmpeg_available:
                raise RuntimeError("FFmpeg not available")

            logger.info(f"Adding audio: {audio_path} -> {video_path}")

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg command (replace audio, use shortest duration)
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", str(video_path),  # Input video
                "-i", str(audio_path),  # Input audio
                "-c:v", "copy",  # Copy video stream (no re-encoding)
                "-c:a", "aac",  # Audio codec
                "-b:a", "192k",  # Audio bitrate
                "-map", "0:v:0",  # Use video from first input
                "-map", "1:a:0",  # Use audio from second input
                "-shortest",  # Match shortest stream duration
                str(output_path),
            ]

            logger.debug(f"FFmpeg command: {' '.join(cmd)}")

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg audio mixing failed: {result.stderr}")

            # Get output file info
            file_size = output_path.stat().st_size
            duration = self._get_video_duration(output_path)

            processing_time = time.time() - start_time
            logger.info(
                f"Audio added: {file_size / 1024 / 1024:.2f}MB, "
                f"{duration:.1f}s, took {processing_time:.2f}s"
            )

            return EncodingResult(
                success=True,
                output_path=output_path,
                file_size_bytes=file_size,
                duration_seconds=duration,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Audio mixing failed: {e}")

            return EncodingResult(
                success=False,
                output_path=None,
                file_size_bytes=0,
                duration_seconds=0.0,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def resize(
        self,
        input_video: Path,
        output_path: Path,
        width: int,
        height: int,
    ) -> EncodingResult:
        """
        Resize video to specified dimensions.

        Args:
            input_video: Path to input video file
            output_path: Where to save resized video
            width: Target width in pixels (use -1 for auto)
            height: Target height in pixels (use -1 for auto)

        Returns:
            EncodingResult with success status and file info
        """
        start_time = time.time()

        try:
            # Validate inputs
            if not input_video.exists():
                raise FileNotFoundError(f"Input video not found: {input_video}")

            if not self._ffmpeg_available:
                raise RuntimeError("FFmpeg not available")

            if width <= 0 and height <= 0:
                raise ValueError("At least one dimension must be positive")

            logger.info(f"Resizing video: {input_video} -> {width}x{height}")

            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build FFmpeg command with scale filter
            # -1 in either dimension maintains aspect ratio
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output
                "-i", str(input_video),  # Input file
                "-vf", f"scale={width}:{height}",  # Scale filter
                "-c:a", "copy",  # Copy audio stream
                str(output_path),
            ]

            logger.debug(f"FFmpeg command: {' '.join(cmd)}")

            # Run FFmpeg
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg resize failed: {result.stderr}")

            # Get output file info
            file_size = output_path.stat().st_size
            duration = self._get_video_duration(output_path)

            processing_time = time.time() - start_time
            logger.info(
                f"Resize complete: {file_size / 1024 / 1024:.2f}MB, "
                f"{duration:.1f}s, took {processing_time:.2f}s"
            )

            return EncodingResult(
                success=True,
                output_path=output_path,
                file_size_bytes=file_size,
                duration_seconds=duration,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Video resize failed: {e}")

            return EncodingResult(
                success=False,
                output_path=None,
                file_size_bytes=0,
                duration_seconds=0.0,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def get_video_info(self, video_path: Path) -> dict:
        """
        Get video metadata.

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata (duration, resolution, fps, codec)

        Raises:
            RuntimeError: If FFmpeg probe fails
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")

        if not self._ffmpeg_available:
            raise RuntimeError("FFmpeg not available")

        try:
            # Use ffprobe to get video info
            cmd = [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries",
                "stream=width,height,r_frame_rate,codec_name,duration",
                "-of", "csv=p=0",
                str(video_path),
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                raise RuntimeError(f"ffprobe failed: {result.stderr}")

            # Parse output (format: width,height,fps,codec,duration)
            parts = result.stdout.strip().split(",")

            if len(parts) >= 4:
                width = int(parts[0])
                height = int(parts[1])

                # Parse fps (format: "num/den")
                fps_parts = parts[2].split("/")
                fps = int(fps_parts[0]) / int(fps_parts[1]) if len(fps_parts) == 2 else 0

                codec = parts[3]
                duration = float(parts[4]) if len(parts) >= 5 else 0.0

                return {
                    "width": width,
                    "height": height,
                    "fps": fps,
                    "codec": codec,
                    "duration": duration,
                    "resolution": (width, height),
                }

            raise RuntimeError("Failed to parse ffprobe output")

        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            raise RuntimeError(f"Video info extraction failed: {e}") from e

    def _check_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is available in system PATH.

        Returns:
            True if FFmpeg is available, False otherwise
        """
        try:
            # Check for ffmpeg
            if shutil.which("ffmpeg") is None:
                logger.warning("ffmpeg not found in PATH")
                return False

            # Check for ffprobe
            if shutil.which("ffprobe") is None:
                logger.warning("ffprobe not found in PATH")
                return False

            # Test FFmpeg version
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                logger.warning("ffmpeg test command failed")
                return False

            logger.debug(f"FFmpeg version: {result.stdout.split()[2]}")
            return True

        except Exception as e:
            logger.warning(f"FFmpeg check failed: {e}")
            return False

    def _get_video_duration(self, video_path: Path) -> float:
        """
        Get video duration in seconds.

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds
        """
        try:
            info = self.get_video_info(video_path)
            return info.get("duration", 0.0)

        except Exception:
            # Fallback: return 0 if unable to get duration
            logger.warning(f"Unable to get duration for {video_path}")
            return 0.0
