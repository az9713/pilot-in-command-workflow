"""
Job management API endpoints.

Provides endpoints for job submission, status checking, and cancellation.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...orchestration import JobQueue, JobStatus
from ..models import JobListResponse, JobResponse, JobStatsResponse, PipelineRequest, PipelineResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])

# Global job queue (injected by main app)
_job_queue: Optional[JobQueue] = None


def set_job_queue(queue: JobQueue) -> None:
    """Set the global job queue instance."""
    global _job_queue
    _job_queue = queue


@router.post("", response_model=PipelineResponse, status_code=202)
async def submit_job(request: PipelineRequest):
    """
    Submit a new pipeline job for async execution.

    Creates a job and queues it for processing. Returns immediately with
    job ID for status tracking.

    Args:
        request: Pipeline execution parameters

    Returns:
        Job ID and initial status

    Note:
        The job will be processed asynchronously. Use GET /jobs/{job_id}
        to check status and retrieve results.
    """
    if _job_queue is None:
        raise HTTPException(status_code=500, detail="Job queue not initialized")

    try:
        from ...orchestration import JobType

        # Create job parameters
        params = {
            "text": request.text,
            "voice_profile_id": request.voice_profile_id,
            "avatar_image_path": request.avatar_image_path,
            "output_filename": request.output_filename,
            "quality": request.quality,
            "fps": request.fps,
            "cleanup_intermediates": request.cleanup_intermediates,
        }

        # Submit job
        job_id = _job_queue.submit(JobType.FULL_PIPELINE, params)

        logger.info(f"Pipeline job submitted: {job_id}")

        return PipelineResponse(
            job_id=job_id,
            status="pending",
            output_url=None,
            message="Job queued for processing",
        )

    except Exception as e:
        logger.error(f"Failed to submit job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=JobListResponse)
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of jobs"),
):
    """
    List all jobs, optionally filtered by status.

    Args:
        status: Filter by job status (pending, running, completed, failed, cancelled)
        limit: Maximum number of jobs to return

    Returns:
        List of jobs matching criteria
    """
    if _job_queue is None:
        raise HTTPException(status_code=500, detail="Job queue not initialized")

    try:
        # Parse status filter
        status_filter = None
        if status is not None:
            try:
                status_filter = JobStatus(status)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid status: {status}. Valid values: "
                    f"{', '.join([s.value for s in JobStatus])}",
                )

        # Get jobs
        jobs = _job_queue.list_jobs(status=status_filter, limit=limit)

        # Convert to response models
        job_responses = [
            JobResponse(
                job_id=job.job_id,
                status=job.status.value,
                job_type=job.job_type.value,
                progress=job.progress,
                stage=job.stage,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                result=job.result,
                error=job.error,
            )
            for job in jobs
        ]

        return JobListResponse(
            jobs=job_responses,
            total=len(job_responses),
            status_filter=status,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=JobStatsResponse)
async def get_job_stats():
    """
    Get job queue statistics.

    Returns:
        Job counts by status
    """
    if _job_queue is None:
        raise HTTPException(status_code=500, detail="Job queue not initialized")

    try:
        stats = _job_queue.get_stats()
        return JobStatsResponse(**stats)

    except Exception as e:
        logger.error(f"Failed to get job stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    """
    Get status of a specific job.

    Args:
        job_id: Job ID to query

    Returns:
        Job status and details

    Raises:
        404: Job not found
    """
    if _job_queue is None:
        raise HTTPException(status_code=500, detail="Job queue not initialized")

    try:
        job = _job_queue.get(job_id)

        if job is None:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        return JobResponse(
            job_id=job.job_id,
            status=job.status.value,
            job_type=job.job_type.value,
            progress=job.progress,
            stage=job.stage,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            result=job.result,
            error=job.error,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{job_id}", status_code=204)
async def cancel_job(job_id: str):
    """
    Cancel a pending job.

    Args:
        job_id: Job ID to cancel

    Raises:
        404: Job not found
        400: Job cannot be cancelled (not pending)
    """
    if _job_queue is None:
        raise HTTPException(status_code=500, detail="Job queue not initialized")

    try:
        job = _job_queue.get(job_id)

        if job is None:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        if job.status != JobStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Job cannot be cancelled: status is {job.status.value}",
            )

        success = _job_queue.cancel(job_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to cancel job")

        logger.info(f"Job cancelled: {job_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {e}")
        raise HTTPException(status_code=500, detail=str(e))
