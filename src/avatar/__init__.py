"""
Avatar generation module.

Provides SDXL 1.5-based avatar image generation and MediaPipe face detection
for lip-sync preparation.
"""

from .detector import FaceDetectionResult, MediaPipeFaceDetector
from .generator import SDXLAvatarGenerator
from .interfaces import (
    AvatarGeneratorInterface,
    AvatarProfile,
    FaceDetectorInterface,
    GenerationResult,
)
from .profiles import AvatarProfileManager

__all__ = [
    # Interfaces
    "AvatarProfile",
    "GenerationResult",
    "FaceDetectionResult",
    "AvatarGeneratorInterface",
    "FaceDetectorInterface",
    # Implementations
    "SDXLAvatarGenerator",
    "MediaPipeFaceDetector",
    "AvatarProfileManager",
]
