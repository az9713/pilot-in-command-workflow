"""
Job definitions and state management.

Defines job types, status, and data structures for async pipeline execution.
"""

import secrets
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Job type classification."""

    FULL_PIPELINE = "full_pipeline"
    VOICE_CLONE = "voice_clone"
    VOICE_SYNTHESIS = "voice_synthesis"
    AVATAR_GENERATION = "avatar_generation"
    VIDEO_LIPSYNC = "video_lipsync"
    VIDEO_ENCODING = "video_encoding"


@dataclass
class Job:
    """
    Job execution state.

    Attributes:
        job_id: Unique job identifier (format: job-{timestamp}-{random})
        status: Current job status
        job_type: Type of job
        params: Job parameters (input files, config, etc.)
        created_at: ISO timestamp of job creation
        started_at: ISO timestamp of job start (if running/completed)
        completed_at: ISO timestamp of job completion (if completed/failed)
        result: Job result data (if completed)
        error: Error message (if failed)
        progress: Progress percentage (0.0-1.0)
        stage: Current processing stage description
    """

    job_id: str
    status: JobStatus
    job_type: JobType
    params: dict
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    progress: float = 0.0
    stage: str = "Queued"

    @staticmethod
    def generate_id() -> str:
        """
        Generate unique job ID.

        Returns:
            Job ID in format 'job-{timestamp}-{random_hex}'
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_hex = secrets.token_hex(4)  # 8 chars
        return f"job-{timestamp}-{random_hex}"

    @staticmethod
    def create(job_type: JobType, params: dict) -> "Job":
        """
        Create a new job.

        Args:
            job_type: Type of job to create
            params: Job parameters

        Returns:
            New Job instance in PENDING status
        """
        return Job(
            job_id=Job.generate_id(),
            status=JobStatus.PENDING,
            job_type=job_type,
            params=params,
            created_at=datetime.utcnow().isoformat() + "Z",
        )

    def start(self) -> None:
        """Mark job as running."""
        self.status = JobStatus.RUNNING
        self.started_at = datetime.utcnow().isoformat() + "Z"
        self.progress = 0.0
        self.stage = "Starting"

    def complete(self, result: dict) -> None:
        """
        Mark job as completed.

        Args:
            result: Job result data
        """
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.result = result
        self.progress = 1.0
        self.stage = "Completed"

    def fail(self, error: str) -> None:
        """
        Mark job as failed.

        Args:
            error: Error message
        """
        self.status = JobStatus.FAILED
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.error = error
        self.stage = "Failed"

    def cancel(self) -> None:
        """Mark job as cancelled."""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.utcnow().isoformat() + "Z"
        self.stage = "Cancelled"

    def update_progress(self, progress: float, stage: str) -> None:
        """
        Update job progress.

        Args:
            progress: Progress percentage (0.0-1.0)
            stage: Current processing stage description
        """
        self.progress = max(0.0, min(1.0, progress))  # Clamp to [0, 1]
        self.stage = stage

    def to_dict(self) -> dict:
        """
        Convert job to dictionary.

        Returns:
            Dictionary representation of job
        """
        data = asdict(self)
        # Convert enums to strings
        data["status"] = self.status.value
        data["job_type"] = self.job_type.value
        return data

    @staticmethod
    def from_dict(data: dict) -> "Job":
        """
        Create job from dictionary.

        Args:
            data: Dictionary with job data

        Returns:
            Job instance
        """
        # Convert string status/type back to enums
        data_copy = data.copy()
        data_copy["status"] = JobStatus(data["status"])
        data_copy["job_type"] = JobType(data["job_type"])
        return Job(**data_copy)
