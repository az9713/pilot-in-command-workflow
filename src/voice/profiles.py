"""
Voice profile management.

Handles CRUD operations for voice profiles, including storage of
speaker embeddings and reference audio.
"""

import json
import logging
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional

import torch

from .interfaces import VoiceProfile

logger = logging.getLogger(__name__)


class VoiceProfileManager:
    """
    Manages voice profile storage and retrieval.

    Stores voice profiles in filesystem with structure:
        storage/voices/{profile_id}/
        ├── reference.wav
        ├── embedding.pt
        └── metadata.json
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize profile manager.

        Args:
            storage_dir: Base directory for voice storage
        """
        self.storage_dir = Path(storage_dir) / "voices"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Voice profile storage: {self.storage_dir}")

    def create_profile(
        self,
        name: str,
        language: str,
        embedding: torch.Tensor,
        reference_audio: Path,
    ) -> VoiceProfile:
        """
        Create a new voice profile.

        Args:
            name: Profile name
            language: Language code
            embedding: Speaker embedding tensor
            reference_audio: Path to reference audio file

        Returns:
            Created VoiceProfile object

        Raises:
            ValueError: If profile name already exists
            IOError: If storage operations fail
        """
        # Check for duplicate names
        existing = self.list_profiles()
        if any(p.name == name for p in existing):
            raise ValueError(f"Profile with name '{name}' already exists")

        # Generate unique ID
        profile_id = self._generate_id()
        profile_dir = self.storage_dir / profile_id
        profile_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Save embedding
            embedding_path = profile_dir / "embedding.pt"
            torch.save(embedding, embedding_path)
            logger.debug(f"Saved embedding to {embedding_path}")

            # Copy reference audio
            reference_path = profile_dir / "reference.wav"
            import shutil

            shutil.copy2(reference_audio, reference_path)
            logger.debug(f"Copied reference audio to {reference_path}")

            # Create metadata
            created_at = datetime.utcnow().isoformat() + "Z"
            metadata = {
                "profile_id": profile_id,
                "name": name,
                "language": language,
                "created_at": created_at,
                "embedding_shape": list(embedding.shape),
                "reference_audio": str(reference_audio),
            }

            metadata_path = profile_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Created voice profile: {profile_id} ({name})")

            return VoiceProfile(
                profile_id=profile_id,
                name=name,
                language=language,
                embedding_path=embedding_path,
                reference_audio_path=reference_path,
                created_at=created_at,
                metadata=metadata,
            )

        except Exception as e:
            # Cleanup on failure
            if profile_dir.exists():
                import shutil

                shutil.rmtree(profile_dir)
            logger.error(f"Failed to create profile: {e}")
            raise IOError(f"Profile creation failed: {e}") from e

    def load_profile(self, profile_id: str) -> VoiceProfile:
        """
        Load a voice profile by ID.

        Args:
            profile_id: Profile ID to load

        Returns:
            VoiceProfile object

        Raises:
            FileNotFoundError: If profile doesn't exist
            IOError: If loading fails
        """
        profile_dir = self.storage_dir / profile_id

        if not profile_dir.exists():
            raise FileNotFoundError(f"Profile not found: {profile_id}")

        try:
            # Load metadata
            metadata_path = profile_dir / "metadata.json"
            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            # Build profile object
            profile = VoiceProfile(
                profile_id=metadata["profile_id"],
                name=metadata["name"],
                language=metadata["language"],
                embedding_path=profile_dir / "embedding.pt",
                reference_audio_path=profile_dir / "reference.wav",
                created_at=metadata["created_at"],
                metadata=metadata,
            )

            logger.debug(f"Loaded profile: {profile_id}")
            return profile

        except Exception as e:
            logger.error(f"Failed to load profile {profile_id}: {e}")
            raise IOError(f"Profile loading failed: {e}") from e

    def list_profiles(self) -> list[VoiceProfile]:
        """
        List all voice profiles.

        Returns:
            List of VoiceProfile objects
        """
        profiles = []

        try:
            for profile_dir in self.storage_dir.iterdir():
                if not profile_dir.is_dir():
                    continue

                try:
                    profile = self.load_profile(profile_dir.name)
                    profiles.append(profile)
                except Exception as e:
                    logger.warning(f"Skipping invalid profile {profile_dir.name}: {e}")

        except Exception as e:
            logger.error(f"Failed to list profiles: {e}")

        return profiles

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete a voice profile.

        Args:
            profile_id: Profile ID to delete

        Returns:
            True if deleted, False if not found
        """
        profile_dir = self.storage_dir / profile_id

        if not profile_dir.exists():
            return False

        try:
            import shutil

            shutil.rmtree(profile_dir)
            logger.info(f"Deleted profile: {profile_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete profile {profile_id}: {e}")
            raise IOError(f"Profile deletion failed: {e}") from e

    def _generate_id(self) -> str:
        """
        Generate unique profile ID.

        Returns:
            Profile ID in format 'vp-{8 chars}'
        """
        # Generate 8 random hex characters
        random_hex = secrets.token_hex(4)  # 4 bytes = 8 hex chars
        return f"vp-{random_hex}"
