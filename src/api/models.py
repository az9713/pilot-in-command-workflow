"""
Pydantic models for API request/response validation.

Defines request and response schemas for all API endpoints.
"""

from typing import Optional

from pydantic import BaseModel, Field


# Pipeline models
class PipelineRequest(BaseModel):
    """Request model for full pipeline execution."""

    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=5000)
    voice_profile_id: str = Field(..., description="Voice profile ID")
    avatar_image_path: str = Field(..., description="Path to avatar image")
    output_filename: Optional[str] = Field(None, description="Output filename (optional)")
    quality: str = Field("high", description="Video quality preset")
    fps: Optional[int] = Field(None, description="Video frame rate (optional)")
    cleanup_intermediates: bool = Field(True, description="Remove intermediate files")


class PipelineResponse(BaseModel):
    """Response model for pipeline execution."""

    job_id: str = Field(..., description="Job ID for async tracking")
    status: str = Field(..., description="Job status")
    output_url: Optional[str] = Field(None, description="URL to output file")
    message: str = Field(..., description="Status message")


# Job models
class JobResponse(BaseModel):
    """Response model for job status."""

    job_id: str
    status: str
    job_type: str
    progress: float = Field(..., ge=0.0, le=1.0)
    stage: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None


class JobListResponse(BaseModel):
    """Response model for job listing."""

    jobs: list[JobResponse]
    total: int
    status_filter: Optional[str] = None


class JobStatsResponse(BaseModel):
    """Response model for job statistics."""

    total: int
    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int


# Voice models
class VoiceCloneRequest(BaseModel):
    """Request model for voice cloning."""

    name: str = Field(..., description="Profile name", min_length=1, max_length=100)
    language: str = Field("en", description="Language code")


class VoiceSynthesizeRequest(BaseModel):
    """Request model for speech synthesis."""

    text: str = Field(..., description="Text to synthesize", min_length=1, max_length=5000)
    voice_profile_id: str = Field(..., description="Voice profile ID")
    output_filename: Optional[str] = Field(None, description="Output filename (optional)")


class VoiceProfileResponse(BaseModel):
    """Response model for voice profile."""

    profile_id: str
    name: str
    language: str
    created_at: str
    reference_audio_url: Optional[str] = None


class VoiceListResponse(BaseModel):
    """Response model for voice profile listing."""

    profiles: list[VoiceProfileResponse]
    total: int


# Avatar models
class AvatarGenerateRequest(BaseModel):
    """Request model for avatar generation."""

    prompt: str = Field(..., description="Generation prompt", min_length=1, max_length=500)
    negative_prompt: str = Field("", description="Negative prompt")
    aspect_ratio: str = Field("16:9", description="Image aspect ratio")
    seed: Optional[int] = Field(None, description="Random seed")
    output_filename: Optional[str] = Field(None, description="Output filename (optional)")


class AvatarProfileResponse(BaseModel):
    """Response model for avatar profile."""

    profile_id: str
    name: str
    aspect_ratio: str
    face_detected: bool
    face_confidence: Optional[float] = None
    created_at: str
    image_url: Optional[str] = None


class AvatarListResponse(BaseModel):
    """Response model for avatar profile listing."""

    profiles: list[AvatarProfileResponse]
    total: int


class FaceDetectionResponse(BaseModel):
    """Response model for face detection."""

    detected: bool
    confidence: float
    face_region: Optional[dict] = None
    landmarks: Optional[dict] = None
    is_valid_for_lipsync: bool
    validation_message: str
    error: Optional[str] = None


# Video models
class VideoLipSyncRequest(BaseModel):
    """Request model for lip-sync generation."""

    avatar_image_path: str = Field(..., description="Path to avatar image")
    audio_file_path: str = Field(..., description="Path to audio file")
    output_filename: Optional[str] = Field(None, description="Output filename (optional)")
    quality: str = Field("high", description="Video quality preset")
    fps: Optional[int] = Field(None, description="Video frame rate (optional)")


class VideoEncodeRequest(BaseModel):
    """Request model for video encoding."""

    input_video_path: str = Field(..., description="Path to input video")
    output_filename: Optional[str] = Field(None, description="Output filename (optional)")
    preset: str = Field("medium", description="Encoding preset")
    crf: int = Field(23, description="CRF quality value", ge=0, le=51)


class VideoInfoResponse(BaseModel):
    """Response model for video information."""

    file_path: str
    duration: float
    width: int
    height: int
    fps: float
    codec: str
    file_size_mb: float


# System models
class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str
    gpu_available: bool
    gpu_name: Optional[str] = None
    vram_total_mb: Optional[int] = None
    vram_free_mb: Optional[int] = None


class StatusResponse(BaseModel):
    """Response model for system status."""

    gpu: dict
    vram: dict
    hardware_profile: str
    job_queue: JobStatsResponse
    storage_path: str


# Error models
class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str
    detail: Optional[str] = None
    status_code: int
