"""
Job queue management.

File-based job queue for async pipeline execution with status tracking.
"""

import json
import logging
from pathlib import Path
from typing import Optional

from .jobs import Job, JobStatus, JobType

logger = logging.getLogger(__name__)


class JobQueue:
    """
    File-based job queue for async processing.

    Stores jobs as individual JSON files in filesystem for persistence
    and easy inspection. Provides CRUD operations for job management.

    Storage structure:
        storage/jobs/{job_id}.json

    Each job file contains:
        - Job ID and type
        - Current status
        - Parameters
        - Progress tracking
        - Results/errors
    """

    def __init__(self, storage_path: Path):
        """
        Initialize job queue.

        Args:
            storage_path: Base storage directory
        """
        self.storage_path = Path(storage_path)
        self.jobs_dir = self.storage_path / "jobs"
        self.jobs_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Job queue storage: {self.jobs_dir}")

    def submit(self, job_type: JobType, params: dict) -> str:
        """
        Submit a new job to the queue.

        Args:
            job_type: Type of job to create
            params: Job parameters

        Returns:
            Job ID of submitted job
        """
        # Create new job
        job = Job.create(job_type, params)

        # Save to storage
        self._save_job(job)

        logger.info(f"Job submitted: {job.job_id} (type: {job_type.value})")
        return job.job_id

    def get(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.

        Args:
            job_id: Job ID to retrieve

        Returns:
            Job instance or None if not found
        """
        job_file = self.jobs_dir / f"{job_id}.json"

        if not job_file.exists():
            logger.warning(f"Job not found: {job_id}")
            return None

        try:
            with open(job_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            job = Job.from_dict(data)
            return job

        except Exception as e:
            logger.error(f"Failed to load job {job_id}: {e}")
            return None

    def list_jobs(
        self, status: Optional[JobStatus] = None, limit: Optional[int] = None
    ) -> list[Job]:
        """
        List jobs, optionally filtered by status.

        Args:
            status: Filter by job status (None for all)
            limit: Maximum number of jobs to return (None for all)

        Returns:
            List of Job instances, sorted by creation time (newest first)
        """
        jobs = []

        try:
            # Load all job files
            for job_file in self.jobs_dir.glob("*.json"):
                try:
                    with open(job_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    job = Job.from_dict(data)

                    # Apply status filter
                    if status is None or job.status == status:
                        jobs.append(job)

                except Exception as e:
                    logger.warning(f"Skipping invalid job file {job_file.name}: {e}")

            # Sort by creation time (newest first)
            jobs.sort(key=lambda j: j.created_at, reverse=True)

            # Apply limit
            if limit is not None:
                jobs = jobs[:limit]

        except Exception as e:
            logger.error(f"Failed to list jobs: {e}")

        return jobs

    def update(self, job: Job) -> bool:
        """
        Update job state.

        Args:
            job: Job instance with updated state

        Returns:
            True if updated successfully, False otherwise
        """
        try:
            self._save_job(job)
            logger.debug(f"Job updated: {job.job_id} (status: {job.status.value})")
            return True

        except Exception as e:
            logger.error(f"Failed to update job {job.job_id}: {e}")
            return False

    def cancel(self, job_id: str) -> bool:
        """
        Cancel a pending job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled successfully, False otherwise
        """
        job = self.get(job_id)

        if job is None:
            logger.warning(f"Cannot cancel: job not found: {job_id}")
            return False

        # Can only cancel pending jobs
        if job.status != JobStatus.PENDING:
            logger.warning(
                f"Cannot cancel job {job_id}: status is {job.status.value}, "
                "only PENDING jobs can be cancelled"
            )
            return False

        # Mark as cancelled
        job.cancel()
        self.update(job)

        logger.info(f"Job cancelled: {job_id}")
        return True

    def delete(self, job_id: str) -> bool:
        """
        Delete a job from queue.

        Args:
            job_id: Job ID to delete

        Returns:
            True if deleted successfully, False otherwise

        Note:
            This permanently removes the job record. Use cancel() for
            graceful cancellation of pending jobs.
        """
        job_file = self.jobs_dir / f"{job_id}.json"

        if not job_file.exists():
            logger.warning(f"Cannot delete: job not found: {job_id}")
            return False

        try:
            job_file.unlink()
            logger.info(f"Job deleted: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete job {job_id}: {e}")
            return False

    def cleanup_completed(self, keep_recent: int = 100) -> int:
        """
        Clean up old completed/failed jobs.

        Args:
            keep_recent: Number of recent jobs to keep (default: 100)

        Returns:
            Number of jobs deleted
        """
        try:
            # Get all completed/failed jobs
            completed = self.list_jobs(status=JobStatus.COMPLETED)
            failed = self.list_jobs(status=JobStatus.FAILED)
            finished = completed + failed

            # Sort by completion time (oldest first)
            finished.sort(key=lambda j: j.completed_at or j.created_at)

            # Delete old jobs beyond keep_recent limit
            to_delete = finished[:-keep_recent] if len(finished) > keep_recent else []

            deleted_count = 0
            for job in to_delete:
                if self.delete(job.job_id):
                    deleted_count += 1

            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} old jobs")

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup jobs: {e}")
            return 0

    def get_stats(self) -> dict:
        """
        Get job queue statistics.

        Returns:
            Dictionary with queue statistics:
                - total: Total number of jobs
                - pending: Number of pending jobs
                - running: Number of running jobs
                - completed: Number of completed jobs
                - failed: Number of failed jobs
                - cancelled: Number of cancelled jobs
        """
        all_jobs = self.list_jobs()

        stats = {
            "total": len(all_jobs),
            "pending": sum(1 for j in all_jobs if j.status == JobStatus.PENDING),
            "running": sum(1 for j in all_jobs if j.status == JobStatus.RUNNING),
            "completed": sum(1 for j in all_jobs if j.status == JobStatus.COMPLETED),
            "failed": sum(1 for j in all_jobs if j.status == JobStatus.FAILED),
            "cancelled": sum(1 for j in all_jobs if j.status == JobStatus.CANCELLED),
        }

        return stats

    def _save_job(self, job: Job) -> None:
        """
        Save job to storage.

        Args:
            job: Job instance to save

        Raises:
            IOError: If save fails
        """
        job_file = self.jobs_dir / f"{job.job_id}.json"

        try:
            with open(job_file, "w", encoding="utf-8") as f:
                json.dump(job.to_dict(), f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save job {job.job_id}: {e}")
            raise IOError(f"Job save failed: {e}") from e
