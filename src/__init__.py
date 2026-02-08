"""
Avatar Pipeline - Open-source AI avatar video generation system.

This package provides voice cloning, text-to-speech, avatar generation,
and lip-sync video creation capabilities optimized for 10GB VRAM GPUs.
"""

__version__ = "0.1.0"
__author__ = "Avatar Pipeline Contributors"
__license__ = "MIT"

# Export main modules
from . import api, avatar, config, orchestration, utils, video, voice

__all__ = [
    "config",
    "utils",
    "voice",
    "avatar",
    "video",
    "orchestration",
    "api",
]
