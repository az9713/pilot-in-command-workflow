"""
Tests for Pydantic API models.

Tests request/response validation and serialization.
"""

import pytest
from pydantic import ValidationError

from src.api.models import (
    AvatarGenerateRequest,
    AvatarListResponse,
    AvatarProfileResponse,
    ErrorResponse,
    FaceDetectionResponse,
    HealthResponse,
    JobListResponse,
    JobResponse,
    JobStatsResponse,
    PipelineRequest,
    PipelineResponse,
    StatusResponse,
    VideoEncodeRequest,
    VideoInfoResponse,
    VideoLipSyncRequest,
    VoiceCloneRequest,
    VoiceListResponse,
    VoiceProfileResponse,
    VoiceSynthesizeRequest,
)


class TestPipelineModels:
    """Tests for pipeline-related models."""

    def test_pipeline_request_valid(self):
        """Test valid pipeline request."""
        request = PipelineRequest(
            text="Hello, world!",
            voice_profile_id="vp-abc123",
            avatar_image_path="/path/to/avatar.png",
            quality="high",
        )

        assert request.text == "Hello, world!"
        assert request.voice_profile_id == "vp-abc123"
        assert request.quality == "high"
        assert request.cleanup_intermediates is True  # Default

    def test_pipeline_request_text_validation(self):
        """Test text length validation."""
        # Empty text should fail
        with pytest.raises(ValidationError):
            PipelineRequest(
                text="",
                voice_profile_id="vp-abc123",
                avatar_image_path="/path/to/avatar.png",
            )

        # Text too long (>5000 chars) should fail
        with pytest.raises(ValidationError):
            PipelineRequest(
                text="x" * 5001,
                voice_profile_id="vp-abc123",
                avatar_image_path="/path/to/avatar.png",
            )

    def test_pipeline_response_valid(self):
        """Test valid pipeline response."""
        response = PipelineResponse(
            job_id="job-123",
            status="pending",
            message="Job queued",
        )

        assert response.job_id == "job-123"
        assert response.status == "pending"
        assert response.output_url is None


class TestJobModels:
    """Tests for job-related models."""

    def test_job_response_valid(self):
        """Test valid job response."""
        response = JobResponse(
            job_id="job-123",
            status="running",
            job_type="voice_synthesis",
            progress=0.5,
            stage="Processing",
            created_at="2024-01-15T10:30:00Z",
        )

        assert response.job_id == "job-123"
        assert response.progress == 0.5

    def test_job_response_progress_validation(self):
        """Test progress must be in [0, 1]."""
        # Progress < 0 should fail
        with pytest.raises(ValidationError):
            JobResponse(
                job_id="job-123",
                status="running",
                job_type="voice_synthesis",
                progress=-0.1,
                stage="Processing",
                created_at="2024-01-15T10:30:00Z",
            )

        # Progress > 1 should fail
        with pytest.raises(ValidationError):
            JobResponse(
                job_id="job-123",
                status="running",
                job_type="voice_synthesis",
                progress=1.1,
                stage="Processing",
                created_at="2024-01-15T10:30:00Z",
            )

    def test_job_list_response(self):
        """Test job list response."""
        jobs = [
            JobResponse(
                job_id=f"job-{i}",
                status="pending",
                job_type="voice_synthesis",
                progress=0.0,
                stage="Queued",
                created_at="2024-01-15T10:30:00Z",
            )
            for i in range(3)
        ]

        response = JobListResponse(
            jobs=jobs,
            total=3,
        )

        assert len(response.jobs) == 3
        assert response.total == 3

    def test_job_stats_response(self):
        """Test job statistics response."""
        stats = JobStatsResponse(
            total=10,
            pending=2,
            running=3,
            completed=4,
            failed=1,
            cancelled=0,
        )

        assert stats.total == 10
        assert stats.pending == 2
        assert stats.completed == 4


class TestVoiceModels:
    """Tests for voice-related models."""

    def test_voice_clone_request_valid(self):
        """Test valid voice clone request."""
        request = VoiceCloneRequest(
            name="John Doe",
            language="en",
        )

        assert request.name == "John Doe"
        assert request.language == "en"

    def test_voice_clone_request_name_validation(self):
        """Test name length validation."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            VoiceCloneRequest(name="", language="en")

        # Name too long (>100 chars) should fail
        with pytest.raises(ValidationError):
            VoiceCloneRequest(name="x" * 101, language="en")

    def test_voice_synthesize_request_valid(self):
        """Test valid synthesize request."""
        request = VoiceSynthesizeRequest(
            text="Hello, world!",
            voice_profile_id="vp-abc123",
        )

        assert request.text == "Hello, world!"
        assert request.voice_profile_id == "vp-abc123"

    def test_voice_synthesize_request_text_validation(self):
        """Test text validation."""
        # Empty text should fail
        with pytest.raises(ValidationError):
            VoiceSynthesizeRequest(text="", voice_profile_id="vp-abc123")

        # Text too long should fail
        with pytest.raises(ValidationError):
            VoiceSynthesizeRequest(text="x" * 5001, voice_profile_id="vp-abc123")

    def test_voice_profile_response(self):
        """Test voice profile response."""
        response = VoiceProfileResponse(
            profile_id="vp-abc123",
            name="John Doe",
            language="en",
            created_at="2024-01-15T10:30:00Z",
        )

        assert response.profile_id == "vp-abc123"
        assert response.name == "John Doe"

    def test_voice_list_response(self):
        """Test voice profile list response."""
        profiles = [
            VoiceProfileResponse(
                profile_id=f"vp-{i}",
                name=f"Voice {i}",
                language="en",
                created_at="2024-01-15T10:30:00Z",
            )
            for i in range(3)
        ]

        response = VoiceListResponse(profiles=profiles, total=3)

        assert len(response.profiles) == 3
        assert response.total == 3


class TestAvatarModels:
    """Tests for avatar-related models."""

    def test_avatar_generate_request_valid(self):
        """Test valid avatar generation request."""
        request = AvatarGenerateRequest(
            prompt="Professional businessman in suit",
            aspect_ratio="16:9",
        )

        assert request.prompt == "Professional businessman in suit"
        assert request.aspect_ratio == "16:9"
        assert request.negative_prompt == ""  # Default

    def test_avatar_generate_request_prompt_validation(self):
        """Test prompt validation."""
        # Empty prompt should fail
        with pytest.raises(ValidationError):
            AvatarGenerateRequest(prompt="")

        # Prompt too long should fail
        with pytest.raises(ValidationError):
            AvatarGenerateRequest(prompt="x" * 501)

    def test_avatar_profile_response(self):
        """Test avatar profile response."""
        response = AvatarProfileResponse(
            profile_id="ap-abc123",
            name="Business Avatar",
            aspect_ratio="16:9",
            face_detected=True,
            face_confidence=0.95,
            created_at="2024-01-15T10:30:00Z",
        )

        assert response.profile_id == "ap-abc123"
        assert response.face_detected is True
        assert response.face_confidence == 0.95

    def test_face_detection_response_detected(self):
        """Test face detection response when face detected."""
        response = FaceDetectionResponse(
            detected=True,
            confidence=0.95,
            face_region={"x": 100, "y": 50, "width": 300, "height": 400},
            is_valid_for_lipsync=True,
            validation_message="Face detected successfully",
        )

        assert response.detected is True
        assert response.confidence == 0.95
        assert response.is_valid_for_lipsync is True

    def test_face_detection_response_not_detected(self):
        """Test face detection response when no face found."""
        response = FaceDetectionResponse(
            detected=False,
            confidence=0.0,
            is_valid_for_lipsync=False,
            validation_message="No face detected",
        )

        assert response.detected is False
        assert response.is_valid_for_lipsync is False


class TestVideoModels:
    """Tests for video-related models."""

    def test_video_lipsync_request_valid(self):
        """Test valid lip-sync request."""
        request = VideoLipSyncRequest(
            avatar_image_path="/path/to/avatar.png",
            audio_file_path="/path/to/audio.wav",
            quality="high",
        )

        assert request.avatar_image_path == "/path/to/avatar.png"
        assert request.audio_file_path == "/path/to/audio.wav"
        assert request.quality == "high"

    def test_video_encode_request_valid(self):
        """Test valid encode request."""
        request = VideoEncodeRequest(
            input_video_path="/path/to/input.mp4",
            preset="medium",
            crf=23,
        )

        assert request.input_video_path == "/path/to/input.mp4"
        assert request.preset == "medium"
        assert request.crf == 23

    def test_video_encode_request_crf_validation(self):
        """Test CRF value validation."""
        # CRF < 0 should fail
        with pytest.raises(ValidationError):
            VideoEncodeRequest(
                input_video_path="/path/to/input.mp4",
                crf=-1,
            )

        # CRF > 51 should fail
        with pytest.raises(ValidationError):
            VideoEncodeRequest(
                input_video_path="/path/to/input.mp4",
                crf=52,
            )

    def test_video_info_response(self):
        """Test video info response."""
        response = VideoInfoResponse(
            file_path="/path/to/video.mp4",
            duration=10.5,
            width=1920,
            height=1080,
            fps=30.0,
            codec="h264",
            file_size_mb=15.5,
        )

        assert response.duration == 10.5
        assert response.width == 1920
        assert response.fps == 30.0


class TestSystemModels:
    """Tests for system-related models."""

    def test_health_response_with_gpu(self):
        """Test health response with GPU available."""
        response = HealthResponse(
            status="healthy",
            version="0.1.0",
            gpu_available=True,
            gpu_name="NVIDIA GeForce RTX 3080",
            vram_total_mb=10240,
            vram_free_mb=8192,
        )

        assert response.status == "healthy"
        assert response.gpu_available is True
        assert response.gpu_name == "NVIDIA GeForce RTX 3080"

    def test_health_response_without_gpu(self):
        """Test health response without GPU."""
        response = HealthResponse(
            status="healthy",
            version="0.1.0",
            gpu_available=False,
        )

        assert response.status == "healthy"
        assert response.gpu_available is False
        assert response.gpu_name is None

    def test_status_response(self):
        """Test system status response."""
        response = StatusResponse(
            gpu={"name": "RTX 3080", "cuda_available": True},
            vram={"total_mb": 10240, "free_mb": 8192},
            hardware_profile="rtx3080",
            job_queue=JobStatsResponse(
                total=5, pending=1, running=2, completed=2, failed=0, cancelled=0
            ),
            storage_path="/path/to/storage",
        )

        assert response.hardware_profile == "rtx3080"
        assert response.job_queue.total == 5

    def test_error_response(self):
        """Test error response."""
        response = ErrorResponse(
            error="Invalid input",
            detail="Text must not be empty",
            status_code=400,
        )

        assert response.error == "Invalid input"
        assert response.detail == "Text must not be empty"
        assert response.status_code == 400


class TestModelSerialization:
    """Tests for model serialization."""

    def test_model_to_dict(self):
        """Test converting model to dictionary."""
        request = VoiceCloneRequest(name="Test Voice", language="en")

        data = request.model_dump()

        assert data["name"] == "Test Voice"
        assert data["language"] == "en"

    def test_model_to_json(self):
        """Test converting model to JSON."""
        request = VoiceCloneRequest(name="Test Voice", language="en")

        json_str = request.model_dump_json()

        assert '"name":"Test Voice"' in json_str or '"name": "Test Voice"' in json_str
        assert "language" in json_str

    def test_model_from_dict(self):
        """Test creating model from dictionary."""
        data = {"name": "Test Voice", "language": "en"}

        request = VoiceCloneRequest(**data)

        assert request.name == "Test Voice"
        assert request.language == "en"
