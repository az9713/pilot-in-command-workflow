"""
FastAPI application for avatar pipeline.

Provides REST API for pipeline execution, job management, and component operations.
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ..avatar import AvatarProfileManager, MediaPipeFaceDetector
from ..config import detect_gpu, get_hardware_profile, load_config
from ..orchestration import JobQueue, PipelineCoordinator
from ..utils import VRAMManager
from ..video import FFmpegEncoder
from ..voice import VoiceProfileManager
from .models import HealthResponse, StatusResponse
from .routes import avatar, jobs, voice, video

logger = logging.getLogger(__name__)

# API version
VERSION = "0.1.0"

# Global state
_app_state: Optional[dict] = None


def create_app(
    config_path: Optional[Path] = None,
    storage_path: Path = Path("storage"),
) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        config_path: Path to config YAML file (optional)
        storage_path: Base storage directory

    Returns:
        Configured FastAPI application
    """
    global _app_state

    # Create app
    app = FastAPI(
        title="Avatar Pipeline API",
        description="REST API for AI avatar video generation with voice cloning and lip-sync",
        version=VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize application state
    try:
        logger.info("Initializing Avatar Pipeline API...")

        # Load configuration
        config = load_config(config_path)
        logger.info(f"Configuration loaded (profile: {config.get('hardware_profile')})")

        # Initialize VRAM manager
        gpu_info = detect_gpu()
        vram_manager = VRAMManager(device_id=gpu_info.get("device_id", 0))

        # Initialize profile managers
        voice_profile_manager = VoiceProfileManager(storage_path)
        avatar_profile_manager = AvatarProfileManager(storage_path)

        # Initialize face detector
        face_detector = MediaPipeFaceDetector()

        # Initialize video encoder
        video_encoder = FFmpegEncoder()

        # Initialize job queue
        job_queue = JobQueue(storage_path)

        # Initialize pipeline coordinator
        pipeline_coordinator = PipelineCoordinator(
            config=config,
            vram_manager=vram_manager,
            storage_path=storage_path,
        )

        # Store global state
        _app_state = {
            "config": config,
            "storage_path": storage_path,
            "vram_manager": vram_manager,
            "voice_profile_manager": voice_profile_manager,
            "avatar_profile_manager": avatar_profile_manager,
            "face_detector": face_detector,
            "video_encoder": video_encoder,
            "job_queue": job_queue,
            "pipeline_coordinator": pipeline_coordinator,
            "gpu_info": gpu_info,
        }

        # Inject dependencies into route modules
        jobs.set_job_queue(job_queue)
        voice.set_components(config, vram_manager, voice_profile_manager)
        avatar.set_components(
            config, vram_manager, avatar_profile_manager, face_detector
        )
        video.set_components(config, vram_manager, video_encoder)

        logger.info("API initialization complete")

    except Exception as e:
        logger.error(f"API initialization failed: {e}", exc_info=True)
        raise

    # Register routes
    app.include_router(jobs.router)
    app.include_router(voice.router)
    app.include_router(avatar.router)
    app.include_router(video.router)

    # Health check endpoint
    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health_check():
        """
        Health check endpoint.

        Returns:
            System health status
        """
        if _app_state is None:
            raise HTTPException(status_code=503, detail="Service not initialized")

        gpu_info = _app_state["gpu_info"]
        vram_manager = _app_state["vram_manager"]
        vram_status = vram_manager.get_status()

        return HealthResponse(
            status="healthy",
            version=VERSION,
            gpu_available=gpu_info["cuda_available"],
            gpu_name=gpu_info.get("name"),
            vram_total_mb=vram_status.total_mb if vram_status.cuda_available else None,
            vram_free_mb=vram_status.free_mb if vram_status.cuda_available else None,
        )

    # System status endpoint
    @app.get("/status", response_model=StatusResponse, tags=["system"])
    async def get_status():
        """
        Get system status.

        Returns:
            Detailed system status including GPU, VRAM, and job queue
        """
        if _app_state is None:
            raise HTTPException(status_code=503, detail="Service not initialized")

        gpu_info = _app_state["gpu_info"]
        vram_manager = _app_state["vram_manager"]
        job_queue = _app_state["job_queue"]
        config = _app_state["config"]
        storage_path = _app_state["storage_path"]

        vram_status = vram_manager.get_status()
        job_stats = job_queue.get_stats()

        return StatusResponse(
            gpu={
                "name": gpu_info.get("name", "Unknown"),
                "cuda_available": gpu_info["cuda_available"],
                "device_id": gpu_info.get("device_id", 0),
            },
            vram={
                "total_mb": vram_status.total_mb,
                "used_mb": vram_status.used_mb,
                "free_mb": vram_status.free_mb,
                "utilization_percent": vram_status.utilization_percent,
            },
            hardware_profile=config.get("hardware_profile", "unknown"),
            job_queue=job_stats,
            storage_path=str(storage_path),
        )

    # Root endpoint
    @app.get("/", tags=["system"])
    async def root():
        """
        API root endpoint.

        Returns:
            API information and documentation links
        """
        return {
            "name": "Avatar Pipeline API",
            "version": VERSION,
            "documentation": "/docs",
            "health": "/health",
            "status": "/status",
        }

    return app


# Default app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
