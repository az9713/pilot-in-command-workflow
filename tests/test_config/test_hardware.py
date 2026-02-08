"""
Tests for hardware detection module.

Tests GPU detection, VRAM querying, and hardware profile selection.
"""

import pytest

from src.config.hardware import detect_gpu, get_hardware_profile


class TestDetectGPU:
    """Tests for detect_gpu function."""

    def test_detect_gpu_no_cuda(self, mocker):
        """Test GPU detection when CUDA is unavailable."""
        # Mock torch.cuda.is_available to return False
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        result = detect_gpu()

        assert result["name"] == "CPU"
        assert result["vram_total"] == 0
        assert result["vram_free"] == 0
        assert result["cuda_available"] is False
        assert result["device_id"] == -1

    def test_detect_gpu_with_cuda(self, mocker):
        """Test GPU detection with CUDA available."""
        # Mock torch.cuda
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True

        # Mock device properties
        mock_props = mocker.MagicMock()
        mock_props.name = "NVIDIA GeForce RTX 3080"
        mock_props.total_memory = 10 * 1024 * 1024 * 1024  # 10GB
        mock_torch.cuda.get_device_properties.return_value = mock_props

        # Mock memory info (free, total)
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,  # 8GB free
            10 * 1024 * 1024 * 1024  # 10GB total (not used)
        )

        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        result = detect_gpu()

        assert result["name"] == "NVIDIA GeForce RTX 3080"
        assert result["vram_total"] == 10240  # 10GB in MB
        assert result["vram_free"] == 8192  # 8GB in MB
        assert result["cuda_available"] is True
        assert result["device_id"] == 0

    def test_detect_gpu_import_error(self, mocker):
        """Test GPU detection when PyTorch is not installed."""
        # Mock ImportError when importing torch
        mocker.patch.dict("sys.modules", {"torch": None})

        result = detect_gpu()

        assert result["name"] == "CPU"
        assert result["cuda_available"] is False

    def test_detect_gpu_exception_handling(self, mocker):
        """Test GPU detection handles unexpected errors."""
        # Mock torch.cuda to raise exception
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.side_effect = RuntimeError("CUDA error")
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        result = detect_gpu()

        assert result["name"] == "CPU"
        assert result["cuda_available"] is False


class TestGetHardwareProfile:
    """Tests for get_hardware_profile function."""

    def test_profile_rtx4090(self):
        """Test profile selection for 20GB+ VRAM (rtx4090)."""
        profile = get_hardware_profile(vram_mb=24576)  # 24GB
        assert profile == "rtx4090"

    def test_profile_rtx4090_exactly_20gb(self):
        """Test profile selection at exactly 20GB boundary."""
        profile = get_hardware_profile(vram_mb=20 * 1024)
        assert profile == "rtx4090"

    def test_profile_rtx3080(self):
        """Test profile selection for 8-20GB VRAM (rtx3080)."""
        profile = get_hardware_profile(vram_mb=10240)  # 10GB
        assert profile == "rtx3080"

    def test_profile_rtx3080_exactly_8gb(self):
        """Test profile selection at exactly 8GB boundary."""
        profile = get_hardware_profile(vram_mb=8 * 1024)
        assert profile == "rtx3080"

    def test_profile_low_vram(self):
        """Test profile selection for <8GB VRAM (low_vram)."""
        profile = get_hardware_profile(vram_mb=6144)  # 6GB
        assert profile == "low_vram"

    def test_profile_low_vram_4gb(self):
        """Test profile selection for 4GB VRAM."""
        profile = get_hardware_profile(vram_mb=4096)
        assert profile == "low_vram"

    def test_profile_zero_vram_cpu(self):
        """Test profile selection for CPU (0 VRAM)."""
        profile = get_hardware_profile(vram_mb=0)
        assert profile == "low_vram"

    def test_profile_auto_detect(self, mocker):
        """Test profile auto-detection when vram_mb is None."""
        # Mock detect_gpu to return specific VRAM
        mocker.patch(
            "src.config.hardware.detect_gpu",
            return_value={
                "vram_total": 10240,  # 10GB -> rtx3080
                "cuda_available": True,
            }
        )

        profile = get_hardware_profile(vram_mb=None)
        assert profile == "rtx3080"

    def test_profile_boundaries(self):
        """Test edge cases around profile boundaries."""
        # Just below 8GB -> low_vram
        assert get_hardware_profile(vram_mb=8191) == "low_vram"

        # Just below 20GB -> rtx3080
        assert get_hardware_profile(vram_mb=20479) == "rtx3080"

        # At 20GB -> rtx4090
        assert get_hardware_profile(vram_mb=20480) == "rtx4090"
