"""
Pytest configuration and shared fixtures.

Provides common fixtures for testing without requiring GPU hardware,
model weights, or external dependencies.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
import torch


# Configuration fixtures
@pytest.fixture
def sample_config():
    """Sample configuration dictionary."""
    return {
        "hardware_profile": "rtx3080",
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
    }


@pytest.fixture
def temp_storage(tmp_path):
    """Temporary storage directory for tests."""
    storage_dir = tmp_path / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)

    # Create subdirectories
    (storage_dir / "voices").mkdir()
    (storage_dir / "avatars").mkdir()
    (storage_dir / "videos").mkdir()
    (storage_dir / "jobs").mkdir()

    return storage_dir


# VRAM and GPU mocking fixtures
@pytest.fixture
def mock_torch_cuda(mocker):
    """Mock torch.cuda for testing without GPU."""
    mock_cuda = MagicMock()
    mock_cuda.is_available.return_value = False
    mocker.patch("torch.cuda", mock_cuda)
    return mock_cuda


@pytest.fixture
def mock_torch_cuda_available(mocker):
    """Mock torch.cuda with GPU available."""
    mock_cuda = MagicMock()
    mock_cuda.is_available.return_value = True

    # Mock device properties
    mock_props = MagicMock()
    mock_props.name = "NVIDIA GeForce RTX 3080"
    mock_props.total_memory = 10 * 1024 * 1024 * 1024  # 10GB
    mock_cuda.get_device_properties.return_value = mock_props

    # Mock memory info (free, total)
    mock_cuda.mem_get_info.return_value = (
        8 * 1024 * 1024 * 1024,  # 8GB free
        10 * 1024 * 1024 * 1024  # 10GB total
    )

    mocker.patch("torch.cuda", mock_cuda)
    return mock_cuda


@pytest.fixture
def mock_vram_manager(mocker):
    """Mock VRAM manager that doesn't require GPU."""
    from src.utils.vram import VRAMStatus

    mock_manager = MagicMock()
    mock_manager.device_id = 0
    mock_manager.get_status.return_value = VRAMStatus(
        total_mb=10240,
        used_mb=2048,
        free_mb=8192,
        utilization_percent=20.0,
        cuda_available=True,
    )
    mock_manager.can_load.return_value = True
    mock_manager.force_cleanup.return_value = None
    mock_manager.log_status.return_value = None

    return mock_manager


# Voice profile fixtures
@pytest.fixture
def mock_voice_profile(tmp_path):
    """Mock voice profile for testing."""
    from src.voice.interfaces import VoiceProfile

    profile_dir = tmp_path / "voices" / "vp-test1234"
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy files
    embedding_path = profile_dir / "embedding.pt"
    reference_path = profile_dir / "reference.wav"

    torch.save(torch.randn(512), embedding_path)
    reference_path.touch()

    return VoiceProfile(
        profile_id="vp-test1234",
        name="Test Voice",
        language="en",
        embedding_path=embedding_path,
        reference_audio_path=reference_path,
        created_at="2024-01-15T10:30:00Z",
        metadata={
            "profile_id": "vp-test1234",
            "name": "Test Voice",
            "language": "en",
            "created_at": "2024-01-15T10:30:00Z",
            "embedding_shape": [512],
        },
    )


@pytest.fixture
def mock_avatar_profile(tmp_path):
    """Mock avatar profile for testing."""
    from src.avatar.interfaces import AvatarProfile

    profile_dir = tmp_path / "avatars" / "ap-test5678"
    profile_dir.mkdir(parents=True, exist_ok=True)

    # Create dummy image
    image_path = profile_dir / "base_image.png"
    image_path.touch()

    return AvatarProfile(
        profile_id="ap-test5678",
        name="Test Avatar",
        base_image_path=image_path,
        aspect_ratio="16:9",
        face_region={"x": 100, "y": 50, "width": 300, "height": 400},
        created_at="2024-01-15T10:30:00Z",
        metadata={
            "profile_id": "ap-test5678",
            "name": "Test Avatar",
            "aspect_ratio": "16:9",
            "face_detected": True,
            "face_confidence": 0.95,
            "created_at": "2024-01-15T10:30:00Z",
        },
    )


# Audio/Video file fixtures
@pytest.fixture
def sample_audio_file(tmp_path):
    """Create a minimal valid audio file for testing."""
    import wave
    import struct

    audio_path = tmp_path / "test_audio.wav"

    # Create a simple 1-second mono WAV file
    sample_rate = 22050
    duration = 1.0
    num_samples = int(sample_rate * duration)

    with wave.open(str(audio_path), "w") as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate silence
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack("<h", 0))

    return audio_path


@pytest.fixture
def sample_image_file(tmp_path):
    """Create a minimal valid image file for testing."""
    from PIL import Image

    image_path = tmp_path / "test_image.png"

    # Create a simple 512x512 RGB image
    img = Image.new("RGB", (512, 512), color=(128, 128, 128))
    img.save(image_path)

    return image_path


@pytest.fixture
def sample_video_file(tmp_path):
    """Create a minimal video file path (mock, not real video)."""
    video_path = tmp_path / "test_video.mp4"
    video_path.touch()  # Just create empty file for path testing
    return video_path


# Job fixtures
@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "job_id": "job-20240115103000-abc12345",
        "status": "pending",
        "job_type": "full_pipeline",
        "params": {
            "text": "Hello, world!",
            "voice_profile_id": "vp-test1234",
            "avatar_image_path": "/path/to/avatar.png",
        },
        "created_at": "2024-01-15T10:30:00Z",
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
        "progress": 0.0,
        "stage": "Queued",
    }


# Config file fixtures
@pytest.fixture
def sample_config_file(tmp_path, sample_config):
    """Create a temporary YAML config file."""
    import yaml

    config_path = tmp_path / "config.yaml"

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(sample_config, f)

    return config_path


# Mock model fixtures
@pytest.fixture
def mock_xtts_model(mocker):
    """Mock XTTS model for voice cloning."""
    mock_model = MagicMock()
    mock_model.get_conditioning_latents.return_value = (
        torch.randn(1, 512),  # gpt_cond_latent
        torch.randn(1, 512),  # speaker_embedding
    )
    return mock_model


@pytest.fixture
def mock_tts_model(mocker):
    """Mock TTS model for synthesis."""
    mock_model = MagicMock()
    mock_model.tts.return_value = torch.randn(22050)  # 1 second audio
    return mock_model


@pytest.fixture
def mock_sdxl_pipeline(mocker):
    """Mock SDXL pipeline for avatar generation."""
    from PIL import Image

    mock_pipeline = MagicMock()
    mock_pipeline.return_value.images = [Image.new("RGB", (512, 512))]
    return mock_pipeline


@pytest.fixture
def mock_mediapipe_face_detection(mocker):
    """Mock MediaPipe face detection."""
    mock_detection = MagicMock()
    mock_detection.process.return_value.detections = [
        MagicMock(
            location_data=MagicMock(
                relative_bounding_box=MagicMock(
                    xmin=0.2,
                    ymin=0.1,
                    width=0.6,
                    height=0.8,
                )
            ),
            score=[0.95],
        )
    ]
    return mock_detection


@pytest.fixture
def mock_ffmpeg(mocker):
    """Mock FFmpeg subprocess calls."""
    mock_run = MagicMock()
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = ""
    mock_run.return_value.stderr = ""
    mocker.patch("subprocess.run", mock_run)
    return mock_run


# Pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (may be slower)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow (requires model loading)"
    )
    config.addinivalue_line(
        "markers", "gpu: mark test as requiring GPU"
    )
