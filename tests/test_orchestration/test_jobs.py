"""
Tests for job dataclasses and state management.

Tests job creation, state transitions, and serialization.
"""

from datetime import datetime

import pytest

from src.orchestration.jobs import Job, JobStatus, JobType


class TestJobStatus:
    """Tests for JobStatus enum."""

    def test_all_statuses_defined(self):
        """Test that all expected statuses are defined."""
        expected = ["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]

        for status_name in expected:
            assert hasattr(JobStatus, status_name)

    def test_status_values(self):
        """Test enum values match expected strings."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"


class TestJobType:
    """Tests for JobType enum."""

    def test_all_types_defined(self):
        """Test that all expected job types are defined."""
        expected = [
            "FULL_PIPELINE",
            "VOICE_CLONE",
            "VOICE_SYNTHESIS",
            "AVATAR_GENERATION",
            "VIDEO_LIPSYNC",
            "VIDEO_ENCODING",
        ]

        for type_name in expected:
            assert hasattr(JobType, type_name)

    def test_type_values(self):
        """Test enum values match expected strings."""
        assert JobType.FULL_PIPELINE.value == "full_pipeline"
        assert JobType.VOICE_CLONE.value == "voice_clone"
        assert JobType.VOICE_SYNTHESIS.value == "voice_synthesis"
        assert JobType.AVATAR_GENERATION.value == "avatar_generation"
        assert JobType.VIDEO_LIPSYNC.value == "video_lipsync"
        assert JobType.VIDEO_ENCODING.value == "video_encoding"


class TestJob:
    """Tests for Job dataclass."""

    def test_generate_id(self):
        """Test job ID generation."""
        job_id = Job.generate_id()

        # Should have format job-{timestamp}-{random}
        assert job_id.startswith("job-")
        parts = job_id.split("-")
        assert len(parts) == 3

        # Timestamp part should be 14 digits (YYYYMMDDHHmmss)
        assert len(parts[1]) == 14
        assert parts[1].isdigit()

        # Random part should be 8 hex characters
        assert len(parts[2]) == 8
        assert all(c in "0123456789abcdef" for c in parts[2])

    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [Job.generate_id() for _ in range(100)]

        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_create_job(self):
        """Test creating a new job."""
        params = {"text": "Hello", "voice_profile_id": "vp-123"}

        job = Job.create(JobType.VOICE_SYNTHESIS, params)

        assert job.job_id.startswith("job-")
        assert job.status == JobStatus.PENDING
        assert job.job_type == JobType.VOICE_SYNTHESIS
        assert job.params == params
        assert job.created_at.endswith("Z")
        assert job.started_at is None
        assert job.completed_at is None
        assert job.result is None
        assert job.error is None
        assert job.progress == 0.0
        assert job.stage == "Queued"

    def test_start_job(self):
        """Test starting a job."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})

        assert job.status == JobStatus.PENDING

        job.start()

        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None
        assert job.started_at.endswith("Z")
        assert job.progress == 0.0
        assert job.stage == "Starting"

    def test_complete_job(self):
        """Test completing a job."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})
        job.start()

        result_data = {"output_path": "/path/to/output.wav"}
        job.complete(result_data)

        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.completed_at.endswith("Z")
        assert job.result == result_data
        assert job.progress == 1.0
        assert job.stage == "Completed"
        assert job.error is None

    def test_fail_job(self):
        """Test failing a job."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})
        job.start()

        error_msg = "Model loading failed"
        job.fail(error_msg)

        assert job.status == JobStatus.FAILED
        assert job.completed_at is not None
        assert job.error == error_msg
        assert job.stage == "Failed"
        assert job.result is None

    def test_cancel_job(self):
        """Test cancelling a job."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})

        job.cancel()

        assert job.status == JobStatus.CANCELLED
        assert job.completed_at is not None
        assert job.stage == "Cancelled"

    def test_update_progress(self):
        """Test updating job progress."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})
        job.start()

        job.update_progress(0.5, "Processing audio")

        assert job.progress == 0.5
        assert job.stage == "Processing audio"

    def test_update_progress_clamping(self):
        """Test that progress is clamped to [0, 1]."""
        job = Job.create(JobType.VOICE_SYNTHESIS, {})

        # Test below 0
        job.update_progress(-0.5, "Test")
        assert job.progress == 0.0

        # Test above 1
        job.update_progress(1.5, "Test")
        assert job.progress == 1.0

    def test_to_dict(self):
        """Test converting job to dictionary."""
        params = {"text": "Hello", "voice_profile_id": "vp-123"}
        job = Job.create(JobType.VOICE_SYNTHESIS, params)

        job_dict = job.to_dict()

        assert job_dict["job_id"] == job.job_id
        assert job_dict["status"] == "pending"  # Enum converted to string
        assert job_dict["job_type"] == "voice_synthesis"  # Enum converted to string
        assert job_dict["params"] == params
        assert job_dict["created_at"] == job.created_at
        assert job_dict["progress"] == 0.0

    def test_from_dict(self):
        """Test creating job from dictionary."""
        job_data = {
            "job_id": "job-20240115103000-abc12345",
            "status": "running",
            "job_type": "voice_synthesis",
            "params": {"text": "Hello"},
            "created_at": "2024-01-15T10:30:00Z",
            "started_at": "2024-01-15T10:30:05Z",
            "completed_at": None,
            "result": None,
            "error": None,
            "progress": 0.3,
            "stage": "Processing",
        }

        job = Job.from_dict(job_data)

        assert job.job_id == "job-20240115103000-abc12345"
        assert job.status == JobStatus.RUNNING
        assert job.job_type == JobType.VOICE_SYNTHESIS
        assert job.params == {"text": "Hello"}
        assert job.progress == 0.3
        assert job.stage == "Processing"

    def test_serialization_roundtrip(self):
        """Test that job can be serialized and deserialized."""
        original = Job.create(JobType.FULL_PIPELINE, {"text": "Test"})
        original.start()
        original.update_progress(0.5, "Halfway")

        # Convert to dict and back
        job_dict = original.to_dict()
        restored = Job.from_dict(job_dict)

        assert restored.job_id == original.job_id
        assert restored.status == original.status
        assert restored.job_type == original.job_type
        assert restored.params == original.params
        assert restored.progress == original.progress
        assert restored.stage == original.stage

    def test_job_lifecycle(self):
        """Test full job lifecycle."""
        # Create job
        job = Job.create(JobType.VOICE_CLONE, {"audio_path": "/path/to/audio.wav"})
        assert job.status == JobStatus.PENDING

        # Start job
        job.start()
        assert job.status == JobStatus.RUNNING
        assert job.started_at is not None

        # Update progress
        job.update_progress(0.25, "Loading model")
        assert job.progress == 0.25

        job.update_progress(0.5, "Processing audio")
        assert job.progress == 0.5

        job.update_progress(0.75, "Generating embedding")
        assert job.progress == 0.75

        # Complete job
        result = {"profile_id": "vp-new123"}
        job.complete(result)

        assert job.status == JobStatus.COMPLETED
        assert job.completed_at is not None
        assert job.result == result
        assert job.progress == 1.0

    def test_job_failure_after_partial_progress(self):
        """Test job failure after some progress."""
        job = Job.create(JobType.AVATAR_GENERATION, {"prompt": "Portrait"})
        job.start()

        # Make some progress
        job.update_progress(0.6, "Generating image")

        # Then fail
        job.fail("CUDA out of memory")

        assert job.status == JobStatus.FAILED
        assert job.error == "CUDA out of memory"
        assert job.progress == 0.6  # Progress preserved

    def test_job_with_all_fields(self):
        """Test job with all fields populated."""
        job = Job(
            job_id="job-20240115103000-abc12345",
            status=JobStatus.COMPLETED,
            job_type=JobType.VIDEO_LIPSYNC,
            params={"image": "avatar.png", "audio": "speech.wav"},
            created_at="2024-01-15T10:30:00Z",
            started_at="2024-01-15T10:30:05Z",
            completed_at="2024-01-15T10:35:00Z",
            result={"video_path": "/path/to/output.mp4", "duration": 10.5},
            error=None,
            progress=1.0,
            stage="Completed",
        )

        # Verify all fields
        assert job.job_id == "job-20240115103000-abc12345"
        assert job.status == JobStatus.COMPLETED
        assert job.job_type == JobType.VIDEO_LIPSYNC
        assert "image" in job.params
        assert job.result["duration"] == 10.5
        assert job.progress == 1.0
