"""
Voice module - Voice cloning and TTS synthesis.

Provides XTTS-v2 voice cloning and Coqui TTS integration with
VRAM-aware sequential model loading.
"""

from .interfaces import (
    CloneResult,
    SynthesisResult,
    TTSSynthesizerInterface,
    VoiceClonerInterface,
    VoiceProfile,
)
from .cloner import XTTSVoiceCloner
from .synthesizer import CoquiTTSSynthesizer
from .profiles import VoiceProfileManager

__all__ = [
    # Interfaces
    "VoiceProfile",
    "CloneResult",
    "SynthesisResult",
    "VoiceClonerInterface",
    "TTSSynthesizerInterface",
    # Implementations
    "XTTSVoiceCloner",
    "CoquiTTSSynthesizer",
    "VoiceProfileManager",
]
