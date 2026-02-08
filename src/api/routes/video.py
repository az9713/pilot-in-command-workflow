"""
Video API endpoints.

Provides endpoints for lip-sync generation and video encoding.
"""

import logging
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException

from ...utils import VRAMManager
from ...video import EncodingConfig, FFmpegEncoder, LipSyncConfig, MuseTalkLipSync
from ..models import VideoEncodeRequest, VideoInfoResponse, VideoLipSyncRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/video", tags=["video"])

# Global components (injected by main app)
_config: Optional[dict] = None
_vram_manager: Optional[VRAMManager] = None
_encoder: Optional[FFmpegEncoder] = None


def set_components(
    config: dict, vram_manager: VRAMManager, encoder: FFmpegEncoder
) -> None:
    """Set global video components."""
    global _config, _vram_manager, _encoder
    _config = config
    _vram_manager = vram_manager
    _encoder = encoder


@router.post("/lipsync", status_code=201)
async def generate_lipsync(request: VideoLipSyncRequest):
    """
    Generate lip-synced video from image and audio.

    Creates a talking head video by animating the face in the image
    to match the audio. The image should contain a clear frontal face.

    Args:
        request: Lip-sync parameters

    Returns:
        Generated video information

    Raises:
        404: Input files not found
        500: Generation failed
    """
    if None in (_config, _vram_manager):
        raise HTTPException(status_code=500, detail="Video system not initialized")

    try:
        # Validate input paths
        avatar_image = Path(request.avatar_image_path)
        audio_file = Path(request.audio_file_path)

        if not avatar_image.exists():
            raise HTTPException(
                status_code=404, detail=f"Avatar image not found: {avatar_image}"
            )

        if not audio_file.exists():
            raise HTTPException(
                status_code=404, detail=f"Audio file not found: {audio_file}"
            )

        # Determine output path
        if request.output_filename:
            output_path = Path("storage") / "outputs" / request.output_filename
        else:
            output_path = (
                Path("storage") / "outputs" / f"lipsync_{int(time.time())}.mp4"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Generating lip-sync video: {avatar_image} + {audio_file}")

        # Initialize lip-sync engine
        lipsync_engine = MuseTalkLipSync(
            config=_config.get("video", {}).get("lipsync", {}),
            vram_manager=_vram_manager,
        )

        # Create lip-sync config
        lipsync_config = LipSyncConfig(quality=request.quality)
        if request.fps is not None:
            lipsync_config.fps = request.fps

        # Generate video
        result = lipsync_engine.generate(
            avatar_image=avatar_image,
            audio_file=audio_file,
            output_path=output_path,
            config=lipsync_config,
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        logger.info(
            f"Lip-sync video generated: {result.duration_seconds:.2f}s, "
            f"{result.frame_count} frames @ {result.fps}fps"
        )

        return {
            "success": True,
            "video_path": str(result.video_path),
            "duration_seconds": result.duration_seconds,
            "frame_count": result.frame_count,
            "fps": result.fps,
            "resolution": {"width": result.resolution[0], "height": result.resolution[1]},
            "processing_time_seconds": result.processing_time_seconds,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lip-sync generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/encode", status_code=201)
async def encode_video(request: VideoEncodeRequest):
    """
    Encode or transcode video file.

    Re-encodes video with specified quality settings. Useful for
    compression, format conversion, or quality adjustments.

    Args:
        request: Encoding parameters

    Returns:
        Encoded video information

    Raises:
        404: Input video not found
        500: Encoding failed
    """
    if _encoder is None:
        raise HTTPException(status_code=500, detail="Video encoder not initialized")

    try:
        # Validate input path
        input_video = Path(request.input_video_path)

        if not input_video.exists():
            raise HTTPException(
                status_code=404, detail=f"Input video not found: {input_video}"
            )

        # Determine output path
        if request.output_filename:
            output_path = Path("storage") / "outputs" / request.output_filename
        else:
            output_path = (
                Path("storage") / "outputs" / f"encoded_{int(time.time())}.mp4"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Encoding video: {input_video} -> {output_path}")

        # Create encoding config
        encoding_config = EncodingConfig(
            preset=request.preset,
            crf=request.crf,
        )

        # Encode video
        result = _encoder.encode(input_video, output_path, encoding_config)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        logger.info(
            f"Video encoded: {result.file_size_bytes / 1024 / 1024:.2f}MB "
            f"({result.processing_time_seconds:.2f}s processing)"
        )

        return {
            "success": True,
            "output_path": str(result.output_path),
            "file_size_bytes": result.file_size_bytes,
            "duration_seconds": result.duration_seconds,
            "processing_time_seconds": result.processing_time_seconds,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video encoding failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info", response_model=VideoInfoResponse)
async def get_video_info(video_path: str):
    """
    Get video file information.

    Shows video metadata including duration, resolution, codec, and FPS.

    Args:
        video_path: Path to video file

    Returns:
        Video metadata

    Raises:
        404: Video file not found
        500: Info extraction failed
    """
    if _encoder is None:
        raise HTTPException(status_code=500, detail="Video encoder not initialized")

    try:
        # Validate path
        video_file = Path(video_path)

        if not video_file.exists():
            raise HTTPException(
                status_code=404, detail=f"Video file not found: {video_file}"
            )

        logger.info(f"Getting video info: {video_file}")

        # Get video info
        info = _encoder.get_video_info(video_file)

        # Get file size
        file_size_mb = video_file.stat().st_size / 1024 / 1024

        return VideoInfoResponse(
            file_path=str(video_file),
            duration=info["duration"],
            width=info["width"],
            height=info["height"],
            fps=info["fps"],
            codec=info["codec"],
            file_size_mb=file_size_mb,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
