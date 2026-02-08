"""
Tests for VRAM management module.

Tests VRAM monitoring, allocation checking, and cleanup operations.
"""

import pytest

from src.utils.vram import VRAMManager, VRAMStatus


class TestVRAMStatus:
    """Tests for VRAMStatus dataclass."""

    def test_vram_status_creation(self):
        """Test creating VRAMStatus object."""
        status = VRAMStatus(
            total_mb=10240,
            used_mb=2048,
            free_mb=8192,
            utilization_percent=20.0,
            cuda_available=True,
        )

        assert status.total_mb == 10240
        assert status.used_mb == 2048
        assert status.free_mb == 8192
        assert status.utilization_percent == 20.0
        assert status.cuda_available is True

    def test_vram_status_str_with_cuda(self):
        """Test string representation with CUDA available."""
        status = VRAMStatus(
            total_mb=10240,
            used_mb=2048,
            free_mb=8192,
            utilization_percent=20.0,
            cuda_available=True,
        )

        result = str(status)

        assert "2048/10240MB" in result
        assert "20.0% used" in result
        assert "8192MB free" in result

    def test_vram_status_str_without_cuda(self):
        """Test string representation without CUDA."""
        status = VRAMStatus(
            total_mb=0,
            used_mb=0,
            free_mb=0,
            utilization_percent=0.0,
            cuda_available=False,
        )

        result = str(status)

        assert "N/A (CPU mode)" in result


class TestVRAMManager:
    """Tests for VRAMManager class."""

    def test_init_with_cuda(self, mocker):
        """Test VRAMManager initialization with CUDA available."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        assert manager.device_id == 0
        assert manager._cuda_available is True
        assert manager._torch is not None

    def test_init_without_cuda(self, mocker):
        """Test VRAMManager initialization without CUDA."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        assert manager.device_id == 0
        assert manager._cuda_available is False

    def test_init_no_torch(self, mocker):
        """Test VRAMManager initialization when PyTorch not installed."""
        mocker.patch.dict("sys.modules", {"torch": None})

        manager = VRAMManager(device_id=0)

        assert manager._cuda_available is False
        assert manager._torch is None

    def test_get_status_with_cuda(self, mocker):
        """Test getting VRAM status with CUDA available."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,  # 8GB free
            10 * 1024 * 1024 * 1024  # 10GB total
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)
        status = manager.get_status()

        assert status.total_mb == 10240
        assert status.free_mb == 8192
        assert status.used_mb == 2048
        assert status.utilization_percent == pytest.approx(20.0, rel=0.1)
        assert status.cuda_available is True

    def test_get_status_without_cuda(self, mocker):
        """Test getting VRAM status without CUDA."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)
        status = manager.get_status()

        assert status.total_mb == 0
        assert status.free_mb == 0
        assert status.used_mb == 0
        assert status.utilization_percent == 0.0
        assert status.cuda_available is False

    def test_get_status_exception_handling(self, mocker):
        """Test VRAM status handles exceptions gracefully."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.side_effect = RuntimeError("CUDA error")
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)
        status = manager.get_status()

        # Should return zero values on error
        assert status.total_mb == 0
        assert status.cuda_available is False

    def test_can_load_with_sufficient_vram(self, mocker):
        """Test can_load returns True when sufficient VRAM available."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,  # 8GB free
            10 * 1024 * 1024 * 1024  # 10GB total
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Request 4GB, have 8GB free - should succeed
        can_load = manager.can_load(required_mb=4096)

        assert can_load is True

    def test_can_load_with_insufficient_vram(self, mocker):
        """Test can_load returns False when insufficient VRAM available."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            2 * 1024 * 1024 * 1024,  # 2GB free
            10 * 1024 * 1024 * 1024  # 10GB total
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Request 4GB, only have 2GB free - should fail
        can_load = manager.can_load(required_mb=4096)

        assert can_load is False

    def test_can_load_with_safety_margin(self, mocker):
        """Test can_load considers safety margin."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            5 * 1024 * 1024 * 1024,  # 5GB free
            10 * 1024 * 1024 * 1024  # 10GB total
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Request 4GB with 1GB margin, have 5GB free - should succeed
        can_load = manager.can_load(required_mb=4096, safety_margin_mb=1024)
        assert can_load is True

        # Request 4GB with 2GB margin, have 5GB free - should fail
        can_load = manager.can_load(required_mb=4096, safety_margin_mb=2048)
        assert can_load is False

    def test_can_load_without_cuda_always_true(self, mocker):
        """Test can_load always returns True in CPU mode."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Should always return True in CPU mode
        can_load = manager.can_load(required_mb=999999)

        assert can_load is True

    def test_force_cleanup_with_cuda(self, mocker):
        """Test force_cleanup performs cleanup operations."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True

        # Mock mem_get_info to show cleanup effect
        call_count = [0]

        def mock_mem_info(device_id):
            call_count[0] += 1
            if call_count[0] == 1:  # Before cleanup
                return (6 * 1024 * 1024 * 1024, 10 * 1024 * 1024 * 1024)
            else:  # After cleanup
                return (8 * 1024 * 1024 * 1024, 10 * 1024 * 1024 * 1024)

        mock_torch.cuda.mem_get_info.side_effect = mock_mem_info
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        # Mock gc.collect
        mock_gc = mocker.patch("src.utils.vram.gc")

        manager = VRAMManager(device_id=0)
        manager.force_cleanup()

        # Verify cleanup operations called
        mock_gc.collect.assert_called_once()
        mock_torch.cuda.empty_cache.assert_called_once()
        mock_torch.cuda.synchronize.assert_called_once_with(0)

    def test_force_cleanup_without_cuda(self, mocker):
        """Test force_cleanup is no-op without CUDA."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)
        manager.force_cleanup()  # Should not raise error

        # Cleanup functions should not be called
        mock_torch.cuda.empty_cache.assert_not_called()

    def test_force_cleanup_exception_handling(self, mocker):
        """Test force_cleanup handles exceptions gracefully."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.empty_cache.side_effect = RuntimeError("CUDA error")
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,
            10 * 1024 * 1024 * 1024
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Should not raise exception
        manager.force_cleanup()

    def test_log_status(self, mocker):
        """Test log_status logs current VRAM status."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,
            10 * 1024 * 1024 * 1024
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager = VRAMManager(device_id=0)

        # Should not raise exception
        manager.log_status()

    def test_different_device_ids(self, mocker):
        """Test VRAMManager with different device IDs."""
        mock_torch = mocker.MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.mem_get_info.return_value = (
            8 * 1024 * 1024 * 1024,
            10 * 1024 * 1024 * 1024
        )
        mocker.patch.dict("sys.modules", {"torch": mock_torch})

        manager0 = VRAMManager(device_id=0)
        manager1 = VRAMManager(device_id=1)

        assert manager0.device_id == 0
        assert manager1.device_id == 1

        # Cleanup should use correct device ID
        manager1.force_cleanup()
        mock_torch.cuda.synchronize.assert_called_with(1)
