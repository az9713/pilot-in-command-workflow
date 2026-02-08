"""
Configuration loading and management.

Loads YAML configuration files with hardware profile-specific defaults.
"""

import logging
from pathlib import Path
from typing import Optional

import yaml

from .hardware import get_hardware_profile

logger = logging.getLogger(__name__)

# Default configuration values by hardware profile
DEFAULT_CONFIGS = {
    "rtx4090": {
        "voice": {
            "xtts": {
                "precision": "fp16",
                "batch_size": 4,
                "temperature": 0.7,
            },
            "tts": {
                "precision": "fp16",
                "vocoder_quality": "high",
            },
        },
        "avatar": {
            "sdxl": {
                "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "precision": "fp16",
                "num_inference_steps": 50,
                "guidance_scale": 7.5,
            },
        },
        "video": {
            "musetalk": {
                "precision": "fp16",
                "fps": 30,
            },
            "max_duration_seconds": 120,
        },
    },
    "rtx3080": {
        "voice": {
            "xtts": {
                "precision": "fp16",
                "batch_size": 2,
                "temperature": 0.7,
            },
            "tts": {
                "precision": "fp16",
                "vocoder_quality": "medium",
            },
        },
        "avatar": {
            "sdxl": {
                "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "precision": "fp16",
                "num_inference_steps": 40,
                "guidance_scale": 7.5,
            },
        },
        "video": {
            "musetalk": {
                "precision": "fp16",
                "fps": 25,
            },
            "max_duration_seconds": 120,
        },
    },
    "low_vram": {
        "voice": {
            "xtts": {
                "precision": "fp16",
                "batch_size": 1,
                "temperature": 0.7,
            },
            "tts": {
                "precision": "fp16",
                "vocoder_quality": "low",
            },
        },
        "avatar": {
            "sdxl": {
                "model_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "precision": "fp16",
                "num_inference_steps": 25,
                "guidance_scale": 7.0,
            },
        },
        "video": {
            "musetalk": {
                "precision": "fp16",
                "fps": 20,
            },
            "max_duration_seconds": 60,
        },
    },
}


def load_config(config_path: Optional[Path] = None) -> dict:
    """
    Load configuration from YAML file with hardware profile defaults.

    Args:
        config_path: Path to YAML config file. If None, uses defaults only.

    Returns:
        Configuration dictionary with merged defaults and user overrides.

    Behavior:
        1. Detects hardware profile (rtx4090/rtx3080/low_vram)
        2. Loads profile defaults
        3. If config_path provided, loads and merges user config
        4. User config values override defaults

    Example config structure:
        voice:
          xtts:
            precision: fp16
            batch_size: 2
        avatar:
          sdxl:
            num_inference_steps: 40
    """
    # Get hardware profile
    profile = get_hardware_profile()
    logger.info(f"Loading config for profile: {profile}")

    # Start with profile defaults
    config = DEFAULT_CONFIGS[profile].copy()

    # Add hardware profile to config
    config["hardware_profile"] = profile

    # Load user config if provided
    if config_path is not None:
        config_path = Path(config_path)

        if not config_path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return config

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)

            if user_config is None:
                logger.warning(f"Empty config file: {config_path}, using defaults")
                return config

            # Deep merge user config with defaults
            config = _deep_merge(config, user_config)
            logger.info(f"Loaded user config from: {config_path}")

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in {config_path}: {e}")
            raise ValueError(f"Failed to parse config file: {e}")
        except Exception as e:
            logger.error(f"Failed to load config from {config_path}: {e}")
            raise

    return config


def _deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge override dict into base dict.

    Args:
        base: Base dictionary with default values
        override: Dictionary with override values

    Returns:
        Merged dictionary (override values take precedence)
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dicts
            result[key] = _deep_merge(result[key], value)
        else:
            # Override value
            result[key] = value

    return result
