"""
Configuration management module.

Handles hardware detection, YAML config loading, and profile selection.
"""

from .hardware import detect_gpu, get_hardware_profile
from .settings import load_config

__all__ = [
    "detect_gpu",
    "get_hardware_profile",
    "load_config",
]
