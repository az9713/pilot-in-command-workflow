"""
Tests for voice profile management.

Tests profile creation, loading, listing, and deletion.
"""

import json
from pathlib import Path

import pytest
import torch

from src.voice.profiles import VoiceProfileManager


class TestVoiceProfileManager:
    """Tests for VoiceProfileManager class."""

    def test_init_creates_directory(self, tmp_path):
        """Test that initialization creates storage directory."""
        storage_dir = tmp_path / "storage"

        manager = VoiceProfileManager(storage_dir)

        assert manager.storage_dir.exists()
        assert manager.storage_dir == storage_dir / "voices"

    def test_create_profile(self, tmp_path, sample_audio_file):
        """Test creating a new voice profile."""
        manager = VoiceProfileManager(tmp_path)

        embedding = torch.randn(512)
        name = "Test Voice"
        language = "en"

        profile = manager.create_profile(
            name=name,
            language=language,
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        # Verify profile attributes
        assert profile.profile_id.startswith("vp-")
        assert profile.name == name
        assert profile.language == language
        assert profile.embedding_path.exists()
        assert profile.reference_audio_path.exists()
        assert profile.created_at.endswith("Z")

        # Verify files were created
        profile_dir = manager.storage_dir / profile.profile_id
        assert profile_dir.exists()
        assert (profile_dir / "embedding.pt").exists()
        assert (profile_dir / "reference.wav").exists()
        assert (profile_dir / "metadata.json").exists()

        # Verify embedding saved correctly
        loaded_embedding = torch.load(profile.embedding_path)
        assert torch.allclose(loaded_embedding, embedding)

        # Verify metadata
        with open(profile_dir / "metadata.json", "r") as f:
            metadata = json.load(f)
        assert metadata["profile_id"] == profile.profile_id
        assert metadata["name"] == name
        assert metadata["language"] == language

    def test_create_profile_duplicate_name(self, tmp_path, sample_audio_file):
        """Test that creating profile with duplicate name fails."""
        manager = VoiceProfileManager(tmp_path)

        embedding = torch.randn(512)

        # Create first profile
        manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        # Try to create second profile with same name
        with pytest.raises(ValueError, match="already exists"):
            manager.create_profile(
                name="Test Voice",
                language="en",
                embedding=embedding,
                reference_audio=sample_audio_file,
            )

    def test_create_profile_cleanup_on_failure(self, tmp_path, sample_audio_file, mocker):
        """Test that profile directory is cleaned up on creation failure."""
        manager = VoiceProfileManager(tmp_path)

        embedding = torch.randn(512)

        # Mock torch.save to fail
        mocker.patch("torch.save", side_effect=RuntimeError("Save failed"))

        with pytest.raises(IOError, match="Profile creation failed"):
            manager.create_profile(
                name="Test Voice",
                language="en",
                embedding=embedding,
                reference_audio=sample_audio_file,
            )

        # Verify no profile directories left behind
        assert len(list(manager.storage_dir.iterdir())) == 0

    def test_load_profile(self, tmp_path, sample_audio_file):
        """Test loading an existing profile."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        embedding = torch.randn(512)
        created = manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        # Load profile
        loaded = manager.load_profile(created.profile_id)

        assert loaded.profile_id == created.profile_id
        assert loaded.name == created.name
        assert loaded.language == created.language
        assert loaded.embedding_path == created.embedding_path
        assert loaded.reference_audio_path == created.reference_audio_path

    def test_load_profile_not_found(self, tmp_path):
        """Test loading non-existent profile raises error."""
        manager = VoiceProfileManager(tmp_path)

        with pytest.raises(FileNotFoundError, match="Profile not found"):
            manager.load_profile("vp-nonexistent")

    def test_load_profile_corrupted_metadata(self, tmp_path, sample_audio_file):
        """Test loading profile with corrupted metadata."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        embedding = torch.randn(512)
        profile = manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        # Corrupt metadata file
        metadata_path = manager.storage_dir / profile.profile_id / "metadata.json"
        metadata_path.write_text("invalid json {{{")

        with pytest.raises(IOError, match="Profile loading failed"):
            manager.load_profile(profile.profile_id)

    def test_list_profiles_empty(self, tmp_path):
        """Test listing profiles when none exist."""
        manager = VoiceProfileManager(tmp_path)

        profiles = manager.list_profiles()

        assert profiles == []

    def test_list_profiles(self, tmp_path, sample_audio_file):
        """Test listing multiple profiles."""
        manager = VoiceProfileManager(tmp_path)

        # Create multiple profiles
        names = ["Voice A", "Voice B", "Voice C"]
        created_ids = []

        for name in names:
            profile = manager.create_profile(
                name=name,
                language="en",
                embedding=torch.randn(512),
                reference_audio=sample_audio_file,
            )
            created_ids.append(profile.profile_id)

        # List profiles
        profiles = manager.list_profiles()

        assert len(profiles) == 3

        # Verify all created profiles are in list
        listed_ids = [p.profile_id for p in profiles]
        for created_id in created_ids:
            assert created_id in listed_ids

    def test_list_profiles_skips_invalid(self, tmp_path, sample_audio_file):
        """Test that listing skips invalid profile directories."""
        manager = VoiceProfileManager(tmp_path)

        # Create valid profile
        manager.create_profile(
            name="Valid Voice",
            language="en",
            embedding=torch.randn(512),
            reference_audio=sample_audio_file,
        )

        # Create invalid profile directory (missing metadata)
        invalid_dir = manager.storage_dir / "vp-invalid"
        invalid_dir.mkdir()

        # List should skip invalid and return only valid
        profiles = manager.list_profiles()

        assert len(profiles) == 1
        assert profiles[0].name == "Valid Voice"

    def test_list_profiles_skips_files(self, tmp_path, sample_audio_file):
        """Test that listing skips files in storage directory."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=torch.randn(512),
            reference_audio=sample_audio_file,
        )

        # Create file in storage directory
        (manager.storage_dir / "some_file.txt").touch()

        # List should only return profiles, not files
        profiles = manager.list_profiles()

        assert len(profiles) == 1

    def test_delete_profile(self, tmp_path, sample_audio_file):
        """Test deleting a profile."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        profile = manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=torch.randn(512),
            reference_audio=sample_audio_file,
        )

        profile_dir = manager.storage_dir / profile.profile_id
        assert profile_dir.exists()

        # Delete profile
        result = manager.delete_profile(profile.profile_id)

        assert result is True
        assert not profile_dir.exists()

    def test_delete_profile_not_found(self, tmp_path):
        """Test deleting non-existent profile returns False."""
        manager = VoiceProfileManager(tmp_path)

        result = manager.delete_profile("vp-nonexistent")

        assert result is False

    def test_delete_profile_failure(self, tmp_path, sample_audio_file, mocker):
        """Test delete handles errors gracefully."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        profile = manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=torch.randn(512),
            reference_audio=sample_audio_file,
        )

        # Mock shutil.rmtree to fail
        mocker.patch("shutil.rmtree", side_effect=OSError("Permission denied"))

        with pytest.raises(IOError, match="Profile deletion failed"):
            manager.delete_profile(profile.profile_id)

    def test_generate_id_format(self, tmp_path):
        """Test that generated IDs have correct format."""
        manager = VoiceProfileManager(tmp_path)

        profile_id = manager._generate_id()

        # Should have format vp-{8 chars}
        assert profile_id.startswith("vp-")
        parts = profile_id.split("-")
        assert len(parts) == 2
        assert len(parts[1]) == 8
        assert all(c in "0123456789abcdef" for c in parts[1])

    def test_generate_id_uniqueness(self, tmp_path):
        """Test that generated IDs are unique."""
        manager = VoiceProfileManager(tmp_path)

        ids = [manager._generate_id() for _ in range(100)]

        # All IDs should be unique
        assert len(ids) == len(set(ids))

    def test_profile_metadata_includes_embedding_shape(self, tmp_path, sample_audio_file):
        """Test that metadata includes embedding shape."""
        manager = VoiceProfileManager(tmp_path)

        embedding = torch.randn(512)
        profile = manager.create_profile(
            name="Test Voice",
            language="en",
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        assert "embedding_shape" in profile.metadata
        assert profile.metadata["embedding_shape"] == [512]

    @pytest.mark.integration
    def test_full_profile_workflow(self, tmp_path, sample_audio_file):
        """Integration test for full profile workflow."""
        manager = VoiceProfileManager(tmp_path)

        # Create profile
        embedding = torch.randn(512)
        created = manager.create_profile(
            name="Integration Test Voice",
            language="en",
            embedding=embedding,
            reference_audio=sample_audio_file,
        )

        # Verify it appears in list
        profiles = manager.list_profiles()
        assert len(profiles) == 1
        assert profiles[0].profile_id == created.profile_id

        # Load profile
        loaded = manager.load_profile(created.profile_id)
        assert loaded.name == "Integration Test Voice"

        # Delete profile
        success = manager.delete_profile(created.profile_id)
        assert success

        # Verify it's gone
        profiles = manager.list_profiles()
        assert len(profiles) == 0
