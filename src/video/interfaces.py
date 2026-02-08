"""
Video module interfaces.

Defines abstract base classes and data structures for lip-sync generation
and video encoding operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LipSyncConfig:
    """
    Configuration for lip-sync generation.

    Attributes:
        fps: Frames per second for output video
        face_det_batch_size: Batch size for face detection
        wav2lip_batch_size: Batch size for wav2lip processing
        quality: Quality preset ("high", "medium", "low")
    """

    fps: int = 25
    face_det_batch_size: int = 1
    wav2lip_batch_size: int = 1
    quality: str = "high"


@dataclass
class LipSyncResult:
    """
    Result of lip-sync video generation.

    Attributes:
        success: Whether generation succeeded
        video_path: Path to generated video file (if successful)
        duration_seconds: Duration of generated video
        frame_count: Number of frames in video
        fps: Frames per second of output video
        resolution: Video resolution as (width, height)
        error: Error message (if failed)
        processing_time_seconds: Time taken for generation
    """

    success: bool
    video_path: Optional[Path]
    duration_seconds: float
    frame_count: int
    fps: int
    resolution: tuple[int, int]
    error: Optional[str]
    processing_time_seconds: float


@dataclass
class EncodingConfig:
    """
    Configuration for video encoding.

    Attributes:
        codec: Video codec to use (default: libx264)
        preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
        crf: Constant Rate Factor for quality (0-51, lower is better)
        audio_codec: Audio codec to use (default: aac)
        audio_bitrate: Audio bitrate (default: 192k)
    """

    codec: str = "libx264"
    preset: str = "medium"
    crf: int = 23
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"


@dataclass
class EncodingResult:
    """
    Result of video encoding.

    Attributes:
        success: Whether encoding succeeded
        output_path: Path to encoded video file (if successful)
        file_size_bytes: Size of output file in bytes
        duration_seconds: Duration of output video
        error: Error message (if failed)
        processing_time_seconds: Time taken for encoding
    """

    success: bool
    output_path: Optional[Path]
    file_size_bytes: int
    duration_seconds: float
    error: Optional[str]
    processing_time_seconds: float


class LipSyncEngineInterface(ABC):
    """
    Abstract interface for lip-sync video generation.

    Implementations should use MuseTalk or compatible models to generate
    talking head videos from static avatar images and audio files.
    """

    @abstractmethod
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
            avatar_image: Path to avatar image (must contain clear frontal face)
            audio_file: Path to audio file (WAV/MP3)
            output_path: Where to save generated video (MP4)
            config: Optional lip-sync configuration

        Returns:
            LipSyncResult with success status and video info

        Note:
            Avatar image should have been validated for lip-sync compatibility
            using face detector. Audio duration determines video length.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> dict[str, list[str]]:
        """
        Get supported input/output formats.

        Returns:
            Dictionary with 'image', 'audio', and 'video' format lists
            Example: {
                'image': ['png', 'jpg', 'jpeg'],
                'audio': ['wav', 'mp3'],
                'video': ['mp4']
            }
        """
        pass


class VideoEncoderInterface(ABC):
    """
    Abstract interface for video encoding.

    Implementations should use FFmpeg or compatible tools to encode,
    transcode, and manipulate video files.
    """

    @abstractmethod
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
        pass

    @abstractmethod
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

        Note:
            Audio will be mixed/replaced with the video stream.
            If audio is longer than video, video loops. If shorter,
            silence is added.
        """
        pass

    @abstractmethod
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
            width: Target width in pixels
            height: Target height in pixels

        Returns:
            EncodingResult with success status and file info

        Note:
            Aspect ratio may be changed. Use -1 for auto-calculation
            to maintain aspect ratio (e.g., width=1920, height=-1).
        """
        pass
