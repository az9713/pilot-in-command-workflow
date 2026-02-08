"""
Hardware detection module.

Detects GPU capabilities and determines appropriate hardware profiles
for model loading and VRAM management.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def detect_gpu() -> dict:
    """
    Detect GPU and return hardware information.

    Returns:
        dict with keys:
            - name (str): GPU model name
            - vram_total (int): Total VRAM in MB
            - vram_free (int): Free VRAM in MB
            - cuda_available (bool): Whether CUDA is available
            - device_id (int): CUDA device ID (or -1 if CPU)

    Note:
        Falls back to CPU if CUDA is unavailable or on detection error.
    """
    try:
        import torch

        if not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            return {
                "name": "CPU",
                "vram_total": 0,
                "vram_free": 0,
                "cuda_available": False,
                "device_id": -1,
            }

        device_id = 0  # Use first GPU
        gpu_props = torch.cuda.get_device_properties(device_id)

        # Get VRAM in MB
        vram_total_mb = gpu_props.total_memory // (1024 * 1024)
        vram_free_mb = (torch.cuda.mem_get_info(device_id)[0]) // (1024 * 1024)

        gpu_info = {
            "name": gpu_props.name,
            "vram_total": vram_total_mb,
            "vram_free": vram_free_mb,
            "cuda_available": True,
            "device_id": device_id,
        }

        logger.info(
            f"Detected GPU: {gpu_info['name']} "
            f"({gpu_info['vram_total']}MB total, {gpu_info['vram_free']}MB free)"
        )

        return gpu_info

    except ImportError:
        logger.error("PyTorch not installed, falling back to CPU")
        return {
            "name": "CPU",
            "vram_total": 0,
            "vram_free": 0,
            "cuda_available": False,
            "device_id": -1,
        }
    except Exception as e:
        logger.error(f"GPU detection failed: {e}, falling back to CPU")
        return {
            "name": "CPU",
            "vram_total": 0,
            "vram_free": 0,
            "cuda_available": False,
            "device_id": -1,
        }


def get_hardware_profile(vram_mb: Optional[int] = None) -> str:
    """
    Determine hardware profile based on available VRAM.

    Args:
        vram_mb: Total VRAM in MB. If None, auto-detects.

    Returns:
        Profile name: "rtx4090", "rtx3080", or "low_vram"

    Profile VRAM thresholds:
        - rtx4090: >= 20GB (high-end, can run multiple models)
        - rtx3080: >= 8GB (target spec, sequential loading)
        - low_vram: < 8GB (reduced quality/features)
    """
    if vram_mb is None:
        gpu_info = detect_gpu()
        vram_mb = gpu_info["vram_total"]

    # Profile thresholds
    if vram_mb >= 20 * 1024:  # 20GB+
        profile = "rtx4090"
    elif vram_mb >= 8 * 1024:  # 8GB+
        profile = "rtx3080"
    else:  # < 8GB
        profile = "low_vram"

    logger.info(f"Selected hardware profile: {profile} (VRAM: {vram_mb}MB)")
    return profile
