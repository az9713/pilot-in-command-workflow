"""
Voice API endpoints.

Provides endpoints for voice cloning, synthesis, and profile management.
"""

import logging
import tempfile
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ...utils import VRAMManager
from ...voice import CoquiTTSSynthesizer, VoiceProfileManager, XTTSVoiceCloner
from ..models import VoiceListResponse, VoiceProfileResponse, VoiceSynthesizeRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Global components (injected by main app)
_config: Optional[dict] = None
_vram_manager: Optional[VRAMManager] = None
_profile_manager: Optional[VoiceProfileManager] = None


def set_components(
    config: dict, vram_manager: VRAMManager, profile_manager: VoiceProfileManager
) -> None:
    """Set global voice components."""
    global _config, _vram_manager, _profile_manager
    _config = config
    _vram_manager = vram_manager
    _profile_manager = profile_manager


@router.get("/profiles", response_model=VoiceListResponse)
async def list_voice_profiles():
    """
    List all voice profiles.

    Returns:
        List of available voice profiles
    """
    if _profile_manager is None:
        raise HTTPException(status_code=500, detail="Voice system not initialized")

    try:
        profiles = _profile_manager.list_profiles()

        profile_responses = [
            VoiceProfileResponse(
                profile_id=p.profile_id,
                name=p.name,
                language=p.language,
                created_at=p.created_at,
                reference_audio_url=None,  # Could add file serving
            )
            for p in profiles
        ]

        return VoiceListResponse(
            profiles=profile_responses,
            total=len(profile_responses),
        )

    except Exception as e:
        logger.error(f"Failed to list voice profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clone", response_model=VoiceProfileResponse, status_code=201)
async def clone_voice(
    audio_file: UploadFile = File(..., description="Reference audio file (WAV/MP3)"),
    name: str = Form(..., description="Profile name"),
    language: str = Form("en", description="Language code"),
):
    """
    Clone a voice from uploaded audio file.

    Creates a new voice profile from reference audio that can be used
    for speech synthesis. Audio should be at least 3 seconds long,
    with 6+ seconds recommended.

    Args:
        audio_file: Reference audio file upload
        name: Name for the voice profile
        language: Language code (default: en)

    Returns:
        Created voice profile

    Raises:
        400: Invalid input
        500: Cloning failed
    """
    if None in (_config, _vram_manager, _profile_manager):
        raise HTTPException(status_code=500, detail="Voice system not initialized")

    try:
        # Validate audio file
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")

        # Save uploaded file to temporary location
        suffix = Path(audio_file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await audio_file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)

        logger.info(f"Voice cloning: {audio_file.filename} -> {name}")

        try:
            # Initialize cloner
            cloner = XTTSVoiceCloner(
                config=_config.get("voice", {}).get("xtts", {}),
                vram_manager=_vram_manager,
                profile_manager=_profile_manager,
            )

            # Clone voice
            result = cloner.clone_voice(tmp_path, name, language)

            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)

            logger.info(f"Voice cloned successfully: {result.profile.profile_id}")

            return VoiceProfileResponse(
                profile_id=result.profile.profile_id,
                name=result.profile.name,
                language=result.profile.language,
                created_at=result.profile.created_at,
                reference_audio_url=None,
            )

        finally:
            # Cleanup temp file
            if tmp_path.exists():
                tmp_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice cloning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize", status_code=201)
async def synthesize_speech(request: VoiceSynthesizeRequest):
    """
    Synthesize speech from text using a voice profile.

    Generates speech audio from text using a cloned voice profile.
    Returns the path to the generated audio file.

    Args:
        request: Synthesis parameters

    Returns:
        Path to generated audio file

    Raises:
        404: Voice profile not found
        500: Synthesis failed
    """
    if None in (_config, _vram_manager, _profile_manager):
        raise HTTPException(status_code=500, detail="Voice system not initialized")

    try:
        # Load voice profile
        try:
            voice_profile = _profile_manager.load_profile(request.voice_profile_id)
        except FileNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"Voice profile not found: {request.voice_profile_id}",
            )

        # Determine output path
        if request.output_filename:
            output_path = Path("storage") / "outputs" / request.output_filename
        else:
            output_path = Path("storage") / "outputs" / f"speech_{int(time.time())}.wav"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Synthesizing speech with profile {voice_profile.profile_id}")

        # Initialize synthesizer
        synthesizer = CoquiTTSSynthesizer(
            config=_config.get("voice", {}).get("tts", {}),
            vram_manager=_vram_manager,
        )

        # Synthesize speech
        result = synthesizer.synthesize(request.text, voice_profile, output_path)

        if not result.success:
            raise HTTPException(status_code=500, detail=result.error)

        logger.info(
            f"Speech synthesized: {result.duration_seconds:.2f}s "
            f"({result.processing_time_seconds:.2f}s processing)"
        )

        return {
            "success": True,
            "audio_path": str(result.audio_path),
            "duration_seconds": result.duration_seconds,
            "processing_time_seconds": result.processing_time_seconds,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Speech synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
