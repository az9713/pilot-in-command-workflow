"""
Avatar profile management.

Handles CRUD operations for avatar profiles, including storage of
generated images and face detection metadata.
"""

import json
import logging
import secrets
from datetime import datetime
from pathlib import Path
from typing import Optional

from .interfaces import AvatarProfile

logger = logging.getLogger(__name__)


class AvatarProfileManager:
    """
    Manages avatar profile storage and retrieval.

    Stores avatar profiles in filesystem with structure:
        storage/avatars/{profile_id}/
        ├── avatar.png
        └── metadata.json
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize profile manager.

        Args:
            storage_dir: Base directory for avatar storage
        """
        self.storage_dir = Path(storage_dir) / "avatars"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Avatar profile storage: {self.storage_dir}")

    def create_profile(
        self,
        name: str,
        image_path: Path,
        face_region: dict,
        aspect_ratio: str,
        generation_metadata: Optional[dict] = None,
    ) -> AvatarProfile:
        """
        Create a new avatar profile.

        Args:
            name: Profile name
            image_path: Path to generated avatar image
            face_region: Face bounding box {x, y, width, height}
            aspect_ratio: Image aspect ratio
            generation_metadata: Additional metadata from generation

        Returns:
            Created AvatarProfile object

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
            # Copy image to profile directory
            avatar_path = profile_dir / "avatar.png"
            import shutil

            shutil.copy2(image_path, avatar_path)
            logger.debug(f"Copied avatar image to {avatar_path}")

            # Create metadata
            created_at = datetime.utcnow().isoformat() + "Z"
            metadata = {
                "profile_id": profile_id,
                "name": name,
                "aspect_ratio": aspect_ratio,
                "face_region": face_region,
                "created_at": created_at,
                "source_image": str(image_path),
            }

            # Add generation metadata if provided
            if generation_metadata:
                metadata["generation"] = generation_metadata

            metadata_path = profile_dir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"Created avatar profile: {profile_id} ({name})")

            return AvatarProfile(
                profile_id=profile_id,
                name=name,
                base_image_path=avatar_path,
                face_region=face_region,
                aspect_ratio=aspect_ratio,
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

    def load_profile(self, profile_id: str) -> AvatarProfile:
        """
        Load an avatar profile by ID.

        Args:
            profile_id: Profile ID to load

        Returns:
            AvatarProfile object

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
            profile = AvatarProfile(
                profile_id=metadata["profile_id"],
                name=metadata["name"],
                base_image_path=profile_dir / "avatar.png",
                face_region=metadata["face_region"],
                aspect_ratio=metadata["aspect_ratio"],
                created_at=metadata["created_at"],
                metadata=metadata,
            )

            logger.debug(f"Loaded profile: {profile_id}")
            return profile

        except Exception as e:
            logger.error(f"Failed to load profile {profile_id}: {e}")
            raise IOError(f"Profile loading failed: {e}") from e

    def list_profiles(self) -> list[AvatarProfile]:
        """
        List all avatar profiles.

        Returns:
            List of AvatarProfile objects
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
        Delete an avatar profile.

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
            Profile ID in format 'ap-{8 chars}'
        """
        # Generate 8 random hex characters
        random_hex = secrets.token_hex(4)  # 4 bytes = 8 hex chars
        return f"ap-{random_hex}"
