"""
Utility modules for the avatar pipeline.

Includes VRAM management and other helper functions.
"""

from .vram import VRAMManager, VRAMStatus

__all__ = [
    "VRAMManager",
    "VRAMStatus",
]
