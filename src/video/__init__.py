"""
Video generation module.

Provides lip-sync video generation and video encoding functionality.
"""

from .interfaces import (
    LipSyncConfig,
    LipSyncResult,
    EncodingConfig,
    EncodingResult,
    LipSyncEngineInterface,
    VideoEncoderInterface,
)
from .lipsync import MuseTalkLipSync
from .encoder import FFmpegEncoder

__all__ = [
    "LipSyncConfig",
    "LipSyncResult",
    "EncodingConfig",
    "EncodingResult",
    "LipSyncEngineInterface",
    "VideoEncoderInterface",
    "MuseTalkLipSync",
    "FFmpegEncoder",
]
