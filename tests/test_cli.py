"""
Tests for CLI commands.

Tests Click commands for status, voice, avatar, video, and pipeline operations.
"""

import pytest
from click.testing import CliRunner

from src.cli import main


class TestStatusCommand:
    """Tests for 'status' command."""

    def test_status_command_no_cuda(self, mocker):
        """Test status command when CUDA is unavailable."""
        # Mock GPU detection to return CPU
        mocker.patch(
            "src.cli.detect_gpu",
            return_value={
                "name": "CPU",
                "cuda_available": False,
                "vram_total": 0,
                "vram_free": 0,
                "device_id": -1,
            },
        )
        mocker.patch("src.cli.get_hardware_profile", return_value="low_vram")
        mocker.patch("src.cli.load_config", return_value={"hardware_profile": "low_vram"})

        runner = CliRunner()
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "CPU" in result.output
        assert "CUDA Available: No" in result.output

    def test_status_command_with_cuda(self, mocker):
        """Test status command with CUDA available."""
        # Mock GPU detection to return GPU
        mocker.patch(
            "src.cli.detect_gpu",
            return_value={
                "name": "NVIDIA GeForce RTX 3080",
                "cuda_available": True,
                "vram_total": 10240,
                "vram_free": 8192,
                "device_id": 0,
            },
        )
        mocker.patch("src.cli.get_hardware_profile", return_value="rtx3080")
        mocker.patch("src.cli.load_config", return_value={"hardware_profile": "rtx3080"})

        # Mock VRAM manager
        from src.utils.vram import VRAMStatus

        mock_vram_manager = mocker.MagicMock()
        mock_vram_manager.get_status.return_value = VRAMStatus(
            total_mb=10240,
            used_mb=2048,
            free_mb=8192,
            utilization_percent=20.0,
            cuda_available=True,
        )
        mocker.patch("src.cli.VRAMManager", return_value=mock_vram_manager)

        runner = CliRunner()
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "RTX 3080" in result.output
        assert "CUDA Available: Yes" in result.output
        assert "10,240 MB" in result.output or "10240 MB" in result.output

    def test_status_command_verbose(self, mocker):
        """Test status command with --verbose flag."""
        mocker.patch(
            "src.cli.detect_gpu",
            return_value={
                "name": "CPU",
                "cuda_available": False,
                "vram_total": 0,
                "vram_free": 0,
                "device_id": -1,
            },
        )
        mocker.patch("src.cli.get_hardware_profile", return_value="low_vram")
        mocker.patch(
            "src.cli.load_config",
            return_value={
                "hardware_profile": "low_vram",
                "voice": {"xtts": {"batch_size": 1}},
            },
        )

        runner = CliRunner()
        result = runner.invoke(main, ["status", "--verbose"])

        assert result.exit_code == 0
        assert "Detailed Configuration" in result.output


class TestVoiceCommands:
    """Tests for voice subcommands."""

    def test_voice_clone_command(self, mocker, tmp_path, sample_audio_file):
        """Test voice clone command."""
        # Mock components
        mocker.patch("src.cli.load_config", return_value={})
        mocker.patch("src.cli.VRAMManager")

        # Mock cloner
        from src.voice.interfaces import CloneResult, VoiceProfile

        mock_profile = VoiceProfile(
            profile_id="vp-test123",
            name="Test Voice",
            language="en",
            embedding_path=tmp_path / "embedding.pt",
            reference_audio_path=tmp_path / "reference.wav",
            created_at="2024-01-15T10:30:00Z",
            metadata={},
        )

        mock_result = CloneResult(
            success=True,
            profile=mock_profile,
            error=None,
            processing_time_seconds=5.0,
        )

        mock_cloner = mocker.MagicMock()
        mock_cloner.clone_voice.return_value = mock_result
        mocker.patch("src.cli.XTTSVoiceCloner", return_value=mock_cloner)
        mocker.patch("src.cli.VoiceProfileManager")

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "voice",
                "clone",
                str(sample_audio_file),
                "--name",
                "Test Voice",
                "--storage",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Success!" in result.output
        assert "vp-test123" in result.output

    def test_voice_list_empty(self, mocker, tmp_path):
        """Test voice list command with no profiles."""
        mock_manager = mocker.MagicMock()
        mock_manager.list_profiles.return_value = []
        mocker.patch("src.cli.VoiceProfileManager", return_value=mock_manager)

        runner = CliRunner()
        result = runner.invoke(main, ["voice", "list", "--storage", str(tmp_path)])

        assert result.exit_code == 0
        assert "No voice profiles found" in result.output


class TestAvatarCommands:
    """Tests for avatar subcommands."""

    def test_avatar_generate_command(self, mocker, tmp_path):
        """Test avatar generate command."""
        # Mock components
        mocker.patch("src.cli.load_config", return_value={})
        mocker.patch("src.cli.VRAMManager")

        # Mock generator
        from src.avatar.interfaces import GenerationResult, AvatarProfile

        mock_profile = AvatarProfile(
            profile_id="ap-test123",
            name="Test Avatar",
            base_image_path=tmp_path / "avatar.png",
            aspect_ratio="16:9",
            face_region={"x": 100, "y": 50, "width": 300, "height": 400},
            created_at="2024-01-15T10:30:00Z",
            metadata={"face_detected": True, "face_confidence": 0.95},
        )

        mock_result = GenerationResult(
            success=True,
            profile=mock_profile,
            error=None,
            processing_time_seconds=10.0,
        )

        mock_generator = mocker.MagicMock()
        mock_generator.generate.return_value = mock_result
        mocker.patch("src.cli.SDXLAvatarGenerator", return_value=mock_generator)
        mocker.patch("src.cli.AvatarProfileManager")

        runner = CliRunner()
        result = runner.invoke(
            main,
            ["avatar", "generate", "professional businessman", "--storage", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "Success!" in result.output
        assert "ap-test123" in result.output

    def test_avatar_detect_command(self, mocker, tmp_path, sample_image_file):
        """Test avatar detect command."""
        # Mock detector
        from src.avatar.interfaces import FaceDetectionResult

        mock_result = FaceDetectionResult(
            detected=True,
            face_region={"x": 100, "y": 50, "width": 300, "height": 400},
            landmarks={"nose": [150, 200], "left_eye": [130, 160], "right_eye": [170, 160]},
            confidence=0.95,
            error=None,
        )

        mock_detector = mocker.MagicMock()
        mock_detector.detect.return_value = mock_result
        mock_detector.validate_for_lipsync.return_value = (True, "Face is valid")
        mocker.patch("src.cli.MediaPipeFaceDetector", return_value=mock_detector)

        runner = CliRunner()
        result = runner.invoke(main, ["avatar", "detect", str(sample_image_file)])

        assert result.exit_code == 0
        assert "Detected: Yes" in result.output
        assert "0.95" in result.output


class TestVideoCommands:
    """Tests for video subcommands."""

    def test_video_lipsync_command(self, mocker, tmp_path, sample_image_file, sample_audio_file):
        """Test video lipsync command."""
        # Mock components
        mocker.patch("src.cli.load_config", return_value={})
        mocker.patch("src.cli.VRAMManager")

        # Mock lip-sync engine
        from src.video.interfaces import LipSyncResult

        output_path = tmp_path / "output.mp4"
        mock_result = LipSyncResult(
            success=True,
            video_path=output_path,
            duration_seconds=5.0,
            frame_count=150,
            fps=30,
            resolution=(1920, 1080),
            error=None,
            processing_time_seconds=15.0,
        )

        mock_lipsync = mocker.MagicMock()
        mock_lipsync.generate.return_value = mock_result
        mocker.patch("src.cli.MuseTalkLipSync", return_value=mock_lipsync)

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "video",
                "lipsync",
                str(sample_image_file),
                str(sample_audio_file),
                "--output",
                str(output_path),
            ],
        )

        assert result.exit_code == 0
        assert "Success!" in result.output

    def test_video_info_command(self, mocker, tmp_path, sample_video_file):
        """Test video info command."""
        # Mock encoder
        mock_encoder = mocker.MagicMock()
        mock_encoder.get_video_info.return_value = {
            "duration": 10.5,
            "width": 1920,
            "height": 1080,
            "fps": 30.0,
            "codec": "h264",
        }
        mocker.patch("src.cli.FFmpegEncoder", return_value=mock_encoder)

        runner = CliRunner()
        result = runner.invoke(main, ["video", "info", str(sample_video_file)])

        assert result.exit_code == 0
        assert "1920x1080" in result.output
        assert "30.00" in result.output


class TestPipelineCommands:
    """Tests for pipeline commands."""

    def test_pipeline_run_command(self, mocker, tmp_path, sample_image_file, mock_voice_profile):
        """Test pipeline run command."""
        # Mock components
        mocker.patch("src.cli.load_config", return_value={})
        mocker.patch("src.cli.VRAMManager")

        # Mock voice profile manager
        mock_profile_manager = mocker.MagicMock()
        mock_profile_manager.load_profile.return_value = mock_voice_profile
        mocker.patch("src.cli.VoiceProfileManager", return_value=mock_profile_manager)

        # Mock coordinator
        from src.orchestration.coordinator import PipelineResult

        output_path = tmp_path / "output.mp4"
        mock_result = PipelineResult(
            success=True,
            job_id=None,
            output_path=output_path,
            duration_seconds=10.0,
            stages_completed=["synthesis", "lipsync", "encoding"],
            error=None,
            processing_time_seconds=30.0,
            intermediate_files={},
        )

        mock_coordinator = mocker.MagicMock()
        mock_coordinator.execute.return_value = mock_result
        mocker.patch("src.cli.PipelineCoordinator", return_value=mock_coordinator)

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "pipeline",
                "run",
                "Hello, world!",
                "--voice",
                "vp-test1234",
                "--avatar",
                str(sample_image_file),
                "--output",
                str(output_path),
                "--storage",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Pipeline completed successfully" in result.output


class TestJobCommands:
    """Tests for job queue commands."""

    def test_jobs_list_empty(self, mocker, tmp_path):
        """Test jobs list command with no jobs."""
        mock_queue = mocker.MagicMock()
        mock_queue.list_jobs.return_value = []
        mocker.patch("src.cli.JobQueue", return_value=mock_queue)

        runner = CliRunner()
        result = runner.invoke(main, ["jobs", "list", "--storage", str(tmp_path)])

        assert result.exit_code == 0
        assert "No jobs found" in result.output

    def test_jobs_status_not_found(self, mocker, tmp_path):
        """Test jobs status command for non-existent job."""
        mock_queue = mocker.MagicMock()
        mock_queue.get.return_value = None
        mocker.patch("src.cli.JobQueue", return_value=mock_queue)

        runner = CliRunner()
        result = runner.invoke(
            main, ["jobs", "status", "job-nonexistent", "--storage", str(tmp_path)]
        )

        assert result.exit_code == 1
        assert "Job not found" in result.output


class TestServerCommands:
    """Tests for server commands."""

    def test_server_start_import_error(self, mocker):
        """Test server start with missing dependencies."""
        # Mock import error
        mocker.patch.dict("sys.modules", {"uvicorn": None})

        runner = CliRunner()
        result = runner.invoke(main, ["server", "start"])

        assert result.exit_code == 1
        assert "Missing dependencies" in result.output or "import" in result.output.lower()


class TestCommandHelp:
    """Tests for command help text."""

    def test_main_help(self):
        """Test main command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Avatar Pipeline" in result.output
        assert "status" in result.output
        assert "voice" in result.output
        assert "avatar" in result.output

    def test_voice_help(self):
        """Test voice subcommand help."""
        runner = CliRunner()
        result = runner.invoke(main, ["voice", "--help"])

        assert result.exit_code == 0
        assert "clone" in result.output
        assert "speak" in result.output
        assert "list" in result.output

    def test_avatar_help(self):
        """Test avatar subcommand help."""
        runner = CliRunner()
        result = runner.invoke(main, ["avatar", "--help"])

        assert result.exit_code == 0
        assert "generate" in result.output
        assert "detect" in result.output

    def test_video_help(self):
        """Test video subcommand help."""
        runner = CliRunner()
        result = runner.invoke(main, ["video", "--help"])

        assert result.exit_code == 0
        assert "lipsync" in result.output
        assert "encode" in result.output
        assert "info" in result.output
