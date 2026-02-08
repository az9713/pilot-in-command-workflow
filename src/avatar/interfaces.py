"""
Avatar module interfaces.

Defines abstract base classes and data structures for avatar generation
and face detection operations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class AvatarProfile:
    """
    Avatar profile metadata.

    Attributes:
        profile_id: Unique identifier (format: ap-{8 chars})
        name: Human-readable profile name
        base_image_path: Path to generated avatar image
        face_region: Face bounding box {x, y, width, height}
        aspect_ratio: Image aspect ratio ("16:9", "9:16", "1:1")
        created_at: ISO timestamp of creation
        metadata: Additional profile metadata
    """

    profile_id: str
    name: str
    base_image_path: Path
    face_region: dict
    aspect_ratio: str
    created_at: str
    metadata: dict


@dataclass
class GenerationResult:
    """
    Result of avatar generation operation.

    Attributes:
        success: Whether generation succeeded
        profile: Created avatar profile (if successful)
        error: Error message (if failed)
        processing_time_seconds: Time taken for generation
    """

    success: bool
    profile: Optional[AvatarProfile]
    error: Optional[str]
    processing_time_seconds: float


@dataclass
class FaceDetectionResult:
    """
    Result of face detection operation.

    Attributes:
        detected: Whether a face was detected
        face_region: Face bounding box {x, y, width, height} (if detected)
        landmarks: Key facial landmarks dictionary (if detected)
        confidence: Detection confidence score (0.0-1.0)
        error: Error message (if failed)
    """

    detected: bool
    face_region: Optional[dict]
    landmarks: Optional[dict]
    confidence: float
    error: Optional[str]


class AvatarGeneratorInterface(ABC):
    """
    Abstract interface for avatar image generation.

    Implementations should use SDXL 1.5 or compatible models to generate
    photorealistic portrait images suitable for lip-sync animation.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: Optional[int] = None,
        output_path: Optional[Path] = None,
    ) -> GenerationResult:
        """
        Generate avatar image from text prompt.

        Args:
            prompt: Text description of desired avatar
            negative_prompt: Things to avoid in generation (optional)
            aspect_ratio: Image aspect ratio ("16:9", "9:16", "1:1")
            seed: Random seed for reproducibility (optional)
            output_path: Where to save generated image (optional, auto-generated if None)

        Returns:
            GenerationResult with success status and profile data

        Note:
            Generated images should feature clear frontal faces suitable for lip-sync.
        """
        pass

    @abstractmethod
    def get_supported_aspect_ratios(self) -> list[str]:
        """
        Get list of supported aspect ratios.

        Returns:
            List of aspect ratio strings (e.g., ["16:9", "9:16", "1:1"])
        """
        pass


class FaceDetectorInterface(ABC):
    """
    Abstract interface for face detection.

    Implementations should use MediaPipe or compatible models to detect
    and validate faces for lip-sync compatibility.
    """

    @abstractmethod
    def detect(self, image_path: Path) -> FaceDetectionResult:
        """
        Detect face in image.

        Args:
            image_path: Path to image file

        Returns:
            FaceDetectionResult with detection status and face data
        """
        pass

    @abstractmethod
    def validate_for_lipsync(
        self, detection: FaceDetectionResult
    ) -> tuple[bool, str]:
        """
        Validate if detected face is suitable for lip-sync.

        Args:
            detection: FaceDetectionResult from detect()

        Returns:
            Tuple of (is_valid, reason_message)
            - is_valid: True if face is suitable for lip-sync
            - reason_message: Explanation (success message or failure reason)
        """
        pass
