"""
Avatar API endpoints.

Provides endpoints for avatar generation, face detection, and profile management.
"""

import logging
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from ...avatar import AvatarProfileManager, MediaPipeFaceDetector, SDXLAvatarGenerator
from ...utils import VRAMManager
from ..models import AvatarGenerateRequest, AvatarListResponse, AvatarProfileResponse, FaceDetectionResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/avatar", tags=["avatar"])

# Global components (injected by main app)
_config: Optional[dict] = None
_vram_manager: Optional[VRAMManager] = None
_profile_manager: Optional[AvatarProfileManager] = None
_face_detector: Optional[MediaPipeFaceDetector] = None


def set_components(
    config: dict,
    vram_manager: VRAMManager,
    profile_manager: AvatarProfileManager,
    face_detector: MediaPipeFaceDetector,
) -> None:
    """Set global avatar components."""
    global _config, _vram_manager, _profile_manager, _face_detector
    _config = config
    _vram_manager = vram_manager
    _profile_manager = profile_manager
    _face_detector = face_detector


@router.get("/profiles", response_model=AvatarListResponse)
async def list_avatar_profiles():
    """
    List all avatar profiles.

    Returns:
        List of available avatar profiles
    """
    if _profile_manager is None:
        raise HTTPException(status_code=500, detail="Avatar system not initialized")

    try:
        profiles = _profile_manager.list_profiles()

        profile_responses = [
            AvatarProfileResponse(
                profile_id=p.profile_id,
                name=p.name,
                aspect_ratio=p.aspect_ratio,
                face_detected=p.metadata.get("face_detected", False),
                face_confidence=p.metadata.get("face_confidence"),
                created_at=p.created_at,
                image_url=None,  # Could add file serving
            )
            for p in profiles
        ]

        return AvatarListResponse(
            profiles=profile_responses,
            total=len(profile_responses),
        )

    except Exception as e:
        logger.error(f"Failed to list avatar profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=AvatarProfileResponse, status_code=201)
async def generate_avatar(request: AvatarGenerateRequest):
    """
    Generate avatar image from text prompt.

    Creates a photorealistic portrait image using SDXL 1.5.
    Automatically detects face and creates an avatar profile.

    Args:
        request: Generation parameters

    Returns:
        Created avatar profile

    Raises:
        400: Invalid input
        500: Generation failed
    """
    if None in (_config, _vram_manager, _profile_manager):
        raise HTTPException(status_code=500, detail="Avatar system not initialized")

    try:
        # Determine output path
        if request.output_filename:
            output_path = Path("storage") / "outputs" / request.output_filename
        else:
            output_path = None  # Auto-generate

        logger.info(f"Generating avatar: {request.prompt}")

        # Initialize generator
        generator = SDXLAvatarGenerator(
            config=_config.get("avatar", {}).get("sdxl", {}),
            vram_manager=_vram_manager,
            profile_manager=_profile_manager,
        )

        # Generate avatar
        result = generator.generate(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            aspect_ratio=request.aspect_ratio,
            seed=request.seed,
            output_path=output_path,
        )

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        logger.info(f"Avatar generated: {result.profile.profile_id}")

        return AvatarProfileResponse(
            profile_id=result.profile.profile_id,
            name=result.profile.name,
            aspect_ratio=result.profile.aspect_ratio,
            face_detected=result.profile.metadata.get("face_detected", False),
            face_confidence=result.profile.metadata.get("face_confidence"),
            created_at=result.profile.created_at,
            image_url=None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect", response_model=FaceDetectionResponse)
async def detect_face(
    image: UploadFile = File(..., description="Image file to analyze"),
):
    """
    Detect and validate face in uploaded image.

    Detects faces using MediaPipe and validates suitability for lip-sync.
    Returns face region, landmarks, and validation results.

    Args:
        image: Image file upload

    Returns:
        Face detection results

    Raises:
        400: Invalid input
        500: Detection failed
    """
    if _face_detector is None:
        raise HTTPException(status_code=500, detail="Face detector not initialized")

    try:
        # Validate file
        if not image.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Save to temporary file
        import tempfile

        suffix = Path(image.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await image.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        logger.info(f"Detecting face in: {image.filename}")

        try:
            # Detect face
            detection = _face_detector.detect(tmp_path)

            # Validate for lip-sync if detected
            is_valid = False
            validation_message = "No face detected"

            if detection.detected:
                is_valid, validation_message = _face_detector.validate_for_lipsync(
                    detection
                )

            return FaceDetectionResponse(
                detected=detection.detected,
                confidence=detection.confidence,
                face_region=detection.face_region,
                landmarks=detection.landmarks,
                is_valid_for_lipsync=is_valid,
                validation_message=validation_message,
                error=detection.error,
            )

        finally:
            # Cleanup temp file
            if tmp_path.exists():
                tmp_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
