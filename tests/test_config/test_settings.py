"""
Tests for configuration loading module.

Tests YAML loading, profile defaults, and configuration merging.
"""

import pytest
import yaml

from src.config.settings import DEFAULT_CONFIGS, _deep_merge, load_config


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_defaults_only(self, mocker):
        """Test loading config with defaults only (no config file)."""
        # Mock hardware profile detection
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        config = load_config(config_path=None)

        # Should return rtx3080 defaults
        assert config["hardware_profile"] == "rtx3080"
        assert config["voice"]["xtts"]["batch_size"] == 2
        assert config["avatar"]["sdxl"]["num_inference_steps"] == 40
        assert config["video"]["musetalk"]["fps"] == 25

    def test_load_config_with_valid_file(self, tmp_path, mocker):
        """Test loading config from valid YAML file."""
        # Mock hardware profile
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        # Create config file
        config_path = tmp_path / "config.yaml"
        user_config = {
            "voice": {
                "xtts": {
                    "batch_size": 4,  # Override default
                }
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(user_config, f)

        config = load_config(config_path=config_path)

        # Should merge user config with defaults
        assert config["voice"]["xtts"]["batch_size"] == 4  # User override
        assert config["voice"]["xtts"]["temperature"] == 0.7  # Default preserved
        assert config["hardware_profile"] == "rtx3080"

    def test_load_config_file_not_found(self, tmp_path, mocker):
        """Test loading config when file doesn't exist."""
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        config_path = tmp_path / "nonexistent.yaml"

        # Should fall back to defaults without error
        config = load_config(config_path=config_path)

        assert config["hardware_profile"] == "rtx3080"
        assert "voice" in config

    def test_load_config_empty_file(self, tmp_path, mocker):
        """Test loading config from empty YAML file."""
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")

        config = load_config(config_path=config_path)

        # Should use defaults
        assert config["hardware_profile"] == "rtx3080"
        assert "voice" in config

    def test_load_config_invalid_yaml(self, tmp_path, mocker):
        """Test loading config with invalid YAML syntax."""
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: syntax: bad")

        with pytest.raises(ValueError, match="Failed to parse config file"):
            load_config(config_path=config_path)

    def test_load_config_different_profiles(self, mocker):
        """Test loading config for different hardware profiles."""
        # Test rtx4090 profile
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx4090")
        config_4090 = load_config()
        assert config_4090["voice"]["xtts"]["batch_size"] == 4
        assert config_4090["avatar"]["sdxl"]["num_inference_steps"] == 50

        # Test rtx3080 profile
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")
        config_3080 = load_config()
        assert config_3080["voice"]["xtts"]["batch_size"] == 2
        assert config_3080["avatar"]["sdxl"]["num_inference_steps"] == 40

        # Test low_vram profile
        mocker.patch("src.config.settings.get_hardware_profile", return_value="low_vram")
        config_low = load_config()
        assert config_low["voice"]["xtts"]["batch_size"] == 1
        assert config_low["avatar"]["sdxl"]["num_inference_steps"] == 25

    def test_load_config_preserves_nested_defaults(self, tmp_path, mocker):
        """Test that config merging preserves nested default values."""
        mocker.patch("src.config.settings.get_hardware_profile", return_value="rtx3080")

        config_path = tmp_path / "config.yaml"
        user_config = {
            "avatar": {
                "sdxl": {
                    "num_inference_steps": 30,  # Only override this
                }
            }
        }

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(user_config, f)

        config = load_config(config_path=config_path)

        # User override applied
        assert config["avatar"]["sdxl"]["num_inference_steps"] == 30

        # Other defaults preserved
        assert config["avatar"]["sdxl"]["precision"] == "fp16"
        assert config["avatar"]["sdxl"]["guidance_scale"] == 7.5
        assert "voice" in config  # Other top-level keys preserved


class TestDeepMerge:
    """Tests for _deep_merge helper function."""

    def test_deep_merge_flat_dicts(self):
        """Test merging flat dictionaries."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = _deep_merge(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        base = {
            "level1": {
                "level2": {
                    "a": 1,
                    "b": 2,
                }
            }
        }
        override = {
            "level1": {
                "level2": {
                    "b": 3,
                    "c": 4,
                }
            }
        }

        result = _deep_merge(base, override)

        assert result["level1"]["level2"]["a"] == 1  # Preserved
        assert result["level1"]["level2"]["b"] == 3  # Overridden
        assert result["level1"]["level2"]["c"] == 4  # Added

    def test_deep_merge_different_types(self):
        """Test merging when value types differ."""
        base = {"a": {"nested": 1}}
        override = {"a": "string"}

        result = _deep_merge(base, override)

        # Override should replace entire value
        assert result["a"] == "string"

    def test_deep_merge_empty_override(self):
        """Test merging with empty override."""
        base = {"a": 1, "b": 2}
        override = {}

        result = _deep_merge(base, override)

        assert result == base

    def test_deep_merge_empty_base(self):
        """Test merging with empty base."""
        base = {}
        override = {"a": 1, "b": 2}

        result = _deep_merge(base, override)

        assert result == override

    def test_deep_merge_preserves_lists(self):
        """Test that lists are replaced, not merged."""
        base = {"items": [1, 2, 3]}
        override = {"items": [4, 5]}

        result = _deep_merge(base, override)

        # Lists should be replaced, not merged
        assert result["items"] == [4, 5]

    def test_deep_merge_complex_structure(self):
        """Test merging complex nested structure."""
        base = {
            "voice": {
                "xtts": {
                    "precision": "fp16",
                    "batch_size": 2,
                    "temperature": 0.7,
                },
                "tts": {
                    "precision": "fp16",
                },
            },
            "avatar": {
                "sdxl": {
                    "num_inference_steps": 40,
                }
            },
        }

        override = {
            "voice": {
                "xtts": {
                    "batch_size": 4,  # Override
                }
            },
            "video": {  # New top-level key
                "fps": 30,
            }
        }

        result = _deep_merge(base, override)

        # Overridden values
        assert result["voice"]["xtts"]["batch_size"] == 4

        # Preserved values
        assert result["voice"]["xtts"]["precision"] == "fp16"
        assert result["voice"]["xtts"]["temperature"] == 0.7
        assert result["voice"]["tts"]["precision"] == "fp16"
        assert result["avatar"]["sdxl"]["num_inference_steps"] == 40

        # New values
        assert result["video"]["fps"] == 30


class TestDefaultConfigs:
    """Tests for DEFAULT_CONFIGS structure."""

    def test_all_profiles_exist(self):
        """Test that all expected profiles are defined."""
        expected_profiles = ["rtx4090", "rtx3080", "low_vram"]

        for profile in expected_profiles:
            assert profile in DEFAULT_CONFIGS

    def test_all_profiles_have_required_sections(self):
        """Test that all profiles have required configuration sections."""
        required_sections = ["voice", "avatar", "video"]

        for profile, config in DEFAULT_CONFIGS.items():
            for section in required_sections:
                assert section in config, f"Profile {profile} missing {section}"

    def test_profile_voice_config_structure(self):
        """Test that voice config has required subsections."""
        for profile, config in DEFAULT_CONFIGS.items():
            assert "xtts" in config["voice"], f"Profile {profile} missing voice.xtts"
            assert "tts" in config["voice"], f"Profile {profile} missing voice.tts"

    def test_profile_avatar_config_structure(self):
        """Test that avatar config has required subsections."""
        for profile, config in DEFAULT_CONFIGS.items():
            assert "sdxl" in config["avatar"], f"Profile {profile} missing avatar.sdxl"

    def test_profile_video_config_structure(self):
        """Test that video config has required subsections."""
        for profile, config in DEFAULT_CONFIGS.items():
            assert "musetalk" in config["video"], f"Profile {profile} missing video.musetalk"
            assert "max_duration_seconds" in config["video"]

    def test_profile_batch_sizes_decrease(self):
        """Test that batch sizes decrease with lower VRAM profiles."""
        batch_sizes = {
            profile: config["voice"]["xtts"]["batch_size"]
            for profile, config in DEFAULT_CONFIGS.items()
        }

        # rtx4090 should have largest batch size
        assert batch_sizes["rtx4090"] >= batch_sizes["rtx3080"]
        assert batch_sizes["rtx3080"] >= batch_sizes["low_vram"]

    def test_profile_inference_steps_decrease(self):
        """Test that inference steps decrease with lower VRAM profiles."""
        steps = {
            profile: config["avatar"]["sdxl"]["num_inference_steps"]
            for profile, config in DEFAULT_CONFIGS.items()
        }

        # rtx4090 should have most inference steps
        assert steps["rtx4090"] >= steps["rtx3080"]
        assert steps["rtx3080"] >= steps["low_vram"]
