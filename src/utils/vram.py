"""
VRAM management utilities.

Provides VRAM monitoring, cleanup, and allocation tracking for sequential
model loading within memory constraints.
"""

import gc
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class VRAMStatus:
    """
    VRAM status information.

    Attributes:
        total_mb: Total VRAM capacity in MB
        used_mb: Currently used VRAM in MB
        free_mb: Currently free VRAM in MB
        utilization_percent: VRAM usage as percentage
        cuda_available: Whether CUDA is available
    """

    total_mb: int
    used_mb: int
    free_mb: int
    utilization_percent: float
    cuda_available: bool

    def __str__(self) -> str:
        if not self.cuda_available:
            return "VRAM: N/A (CPU mode)"
        return (
            f"VRAM: {self.used_mb}/{self.total_mb}MB "
            f"({self.utilization_percent:.1f}% used, {self.free_mb}MB free)"
        )


class VRAMManager:
    """
    VRAM monitoring and management.

    Provides methods to check VRAM status, verify allocation feasibility,
    and force cleanup for sequential model loading.

    Usage:
        manager = VRAMManager()
        status = manager.get_status()
        if manager.can_load(4096):  # Check if 4GB available
            # Load model
            pass
        manager.force_cleanup()  # Aggressive cleanup after unload
    """

    def __init__(self, device_id: int = 0):
        """
        Initialize VRAM manager.

        Args:
            device_id: CUDA device ID (default: 0)
        """
        self.device_id = device_id
        self._torch = None
        self._cuda_available = False

        # Try to import torch
        try:
            import torch

            self._torch = torch
            self._cuda_available = torch.cuda.is_available()

            if self._cuda_available:
                logger.info(f"VRAM manager initialized for device {device_id}")
            else:
                logger.warning("CUDA not available, VRAM management disabled")

        except ImportError:
            logger.warning("PyTorch not installed, VRAM management disabled")

    def get_status(self) -> VRAMStatus:
        """
        Get current VRAM status.

        Returns:
            VRAMStatus object with current memory info

        Note:
            Returns zero values if CUDA is unavailable.
        """
        if not self._cuda_available or self._torch is None:
            return VRAMStatus(
                total_mb=0,
                used_mb=0,
                free_mb=0,
                utilization_percent=0.0,
                cuda_available=False,
            )

        try:
            # Get memory info in bytes
            mem_free, mem_total = self._torch.cuda.mem_get_info(self.device_id)

            # Convert to MB
            total_mb = mem_total // (1024 * 1024)
            free_mb = mem_free // (1024 * 1024)
            used_mb = total_mb - free_mb
            utilization = (used_mb / total_mb * 100) if total_mb > 0 else 0.0

            return VRAMStatus(
                total_mb=total_mb,
                used_mb=used_mb,
                free_mb=free_mb,
                utilization_percent=utilization,
                cuda_available=True,
            )

        except Exception as e:
            logger.error(f"Failed to get VRAM status: {e}")
            return VRAMStatus(
                total_mb=0,
                used_mb=0,
                free_mb=0,
                utilization_percent=0.0,
                cuda_available=False,
            )

    def can_load(self, required_mb: int, safety_margin_mb: int = 512) -> bool:
        """
        Check if sufficient VRAM is available for model loading.

        Args:
            required_mb: Required VRAM in MB
            safety_margin_mb: Additional safety margin in MB (default: 512)

        Returns:
            True if sufficient VRAM available, False otherwise

        Note:
            Always returns True if CUDA is unavailable (CPU mode).
        """
        if not self._cuda_available:
            # In CPU mode, always return True (no VRAM constraint)
            return True

        status = self.get_status()
        available_mb = status.free_mb - safety_margin_mb

        can_allocate = available_mb >= required_mb

        if not can_allocate:
            logger.warning(
                f"Insufficient VRAM: need {required_mb}MB, "
                f"have {available_mb}MB (after {safety_margin_mb}MB margin)"
            )
        else:
            logger.debug(
                f"VRAM check passed: need {required_mb}MB, "
                f"have {available_mb}MB available"
            )

        return can_allocate

    def force_cleanup(self) -> None:
        """
        Force aggressive VRAM cleanup.

        Performs garbage collection and clears CUDA cache to free
        maximum VRAM between model loads.

        Call this after unloading models to ensure VRAM is freed.
        """
        if not self._cuda_available or self._torch is None:
            return

        try:
            # Log status before cleanup
            status_before = self.get_status()
            logger.debug(f"VRAM before cleanup: {status_before}")

            # Run Python garbage collector
            gc.collect()

            # Clear PyTorch CUDA cache
            self._torch.cuda.empty_cache()

            # Synchronize to ensure cleanup completes
            self._torch.cuda.synchronize(self.device_id)

            # Log status after cleanup
            status_after = self.get_status()
            freed_mb = status_after.free_mb - status_before.free_mb

            logger.info(
                f"VRAM cleanup freed {freed_mb}MB "
                f"({status_after.free_mb}MB now available)"
            )

        except Exception as e:
            logger.error(f"VRAM cleanup failed: {e}")

    def log_status(self) -> None:
        """
        Log current VRAM status at INFO level.

        Convenience method for debugging and monitoring.
        """
        status = self.get_status()
        logger.info(str(status))
