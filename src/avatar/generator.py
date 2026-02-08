"""
Avatar generation using SDXL 1.5.

Generates photorealistic portrait images using Stable Diffusion XL.
Uses VRAM-aware loading and automatic cleanup.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import torch
from PIL import Image

from ..utils.vram import VRAMManager
from .interfaces import AvatarGeneratorInterface, GenerationResult
from .profiles import AvatarProfileManager

logger = logging.getLogger(__name__)

# Supported aspect ratios and their dimensions for SDXL
ASPECT_RATIOS = {
    "16:9": (1344, 768),  # Landscape
    "9:16": (768, 1344),  # Portrait
    "1:1": (1024, 1024),  # Square
}

# Default negative prompt to avoid common issues
DEFAULT_NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, deformed, ugly, bad anatomy, "
    "disfigured, poorly drawn face, mutation, extra limbs, "
    "low resolution, watermark, text, multiple people"
)


class SDXLAvatarGenerator(AvatarGeneratorInterface):
    """
    SDXL 1.5 avatar generation implementation.

    Uses Stable Diffusion XL to generate photorealistic portrait images.
    Manages VRAM loading and cleanup automatically.
    """

    def __init__(
        self,
        config: dict,
        vram_manager: VRAMManager,
        profile_manager: AvatarProfileManager,
    ):
        """
        Initialize SDXL avatar generator.

        Args:
            config: Configuration dict (avatar.sdxl section)
            vram_manager: VRAM management instance
            profile_manager: Avatar profile manager
        """
        self.config = config
        self.vram_manager = vram_manager
        self.profile_manager = profile_manager
        self._pipeline = None
        self._device = None

        # Model settings
        self.vram_requirement_mb = 7168  # SDXL requires ~7GB for FP16
        self.model_id = config.get("model_id", "stabilityai/stable-diffusion-xl-base-1.0")
        self.num_inference_steps = config.get("num_inference_steps", 30)
        self.guidance_scale = config.get("guidance_scale", 7.5)

        logger.info("SDXL avatar generator initialized")

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        seed: Optional[int] = None,
        output_path: Optional[Path] = None,
    ) -> GenerationResult:
        """
        Generate avatar image from text prompt.

        Args:
            prompt: Text description of desired avatar
            negative_prompt: Things to avoid (optional, uses defaults if empty)
            aspect_ratio: Image aspect ratio ("16:9", "9:16", "1:1")
            seed: Random seed for reproducibility (optional)
            output_path: Where to save image (optional, auto-generated if None)

        Returns:
            GenerationResult with success status and profile
        """
        start_time = time.time()

        try:
            # Validate aspect ratio
            if aspect_ratio not in ASPECT_RATIOS:
                raise ValueError(
                    f"Unsupported aspect ratio: {aspect_ratio}. "
                    f"Supported: {', '.join(ASPECT_RATIOS.keys())}"
                )

            width, height = ASPECT_RATIOS[aspect_ratio]

            # Enhance prompt for portrait generation
            enhanced_prompt = self._enhance_prompt(prompt)

            # Use default negative prompt if none provided
            if not negative_prompt:
                negative_prompt = DEFAULT_NEGATIVE_PROMPT

            # Check VRAM availability
            if not self.vram_manager.can_load(self.vram_requirement_mb):
                raise RuntimeError(
                    f"Insufficient VRAM: need {self.vram_requirement_mb}MB for SDXL"
                )

            # Load model
            self._load_model()

            # Generate image
            logger.info(f"Generating avatar: {prompt[:50]}...")
            logger.info(f"Resolution: {width}x{height} ({aspect_ratio})")

            # Set random seed if provided
            generator = None
            if seed is not None:
                generator = torch.Generator(device=self._device).manual_seed(seed)
                logger.info(f"Using seed: {seed}")

            # Generate with pipeline
            result = self._pipeline(
                prompt=enhanced_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=self.num_inference_steps,
                guidance_scale=self.guidance_scale,
                generator=generator,
            )

            image = result.images[0]

            # Unload model and cleanup
            self._unload_model()

            # Save image
            if output_path is None:
                # Auto-generate output path in temp storage
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path(f"temp_avatar_{timestamp}.png")

            output_path.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path)
            logger.info(f"Saved avatar to {output_path}")

            # Detect face in generated image
            from .detector import MediaPipeFaceDetector

            detector = MediaPipeFaceDetector()
            detection = detector.detect(output_path)

            if not detection.detected:
                logger.warning("No face detected in generated image")
                face_region = {"x": 0, "y": 0, "width": width, "height": height}
            else:
                face_region = detection.face_region
                logger.info(
                    f"Face detected: confidence {detection.confidence:.2f}"
                )

            # Create profile (extract name from prompt)
            profile_name = self._extract_name_from_prompt(prompt)

            generation_metadata = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "seed": seed,
                "width": width,
                "height": height,
                "steps": self.num_inference_steps,
                "guidance_scale": self.guidance_scale,
                "face_detected": detection.detected,
                "face_confidence": detection.confidence,
            }

            profile = self.profile_manager.create_profile(
                name=profile_name,
                image_path=output_path,
                face_region=face_region,
                aspect_ratio=aspect_ratio,
                generation_metadata=generation_metadata,
            )

            processing_time = time.time() - start_time
            logger.info(
                f"Avatar generation successful: {profile.profile_id} "
                f"({processing_time:.2f}s)"
            )

            return GenerationResult(
                success=True,
                profile=profile,
                error=None,
                processing_time_seconds=processing_time,
            )

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Avatar generation failed: {e}")

            # Ensure cleanup on error
            self._unload_model()

            return GenerationResult(
                success=False,
                profile=None,
                error=str(e),
                processing_time_seconds=processing_time,
            )

    def get_supported_aspect_ratios(self) -> list[str]:
        """Get list of supported aspect ratios."""
        return list(ASPECT_RATIOS.keys())

    def _load_model(self) -> None:
        """Load SDXL pipeline into memory."""
        if self._pipeline is not None:
            logger.debug("SDXL pipeline already loaded")
            return

        try:
            logger.info("Loading SDXL pipeline...")
            from diffusers import StableDiffusionXLPipeline

            # Determine device
            if torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"
                logger.warning("CUDA not available, using CPU (will be very slow)")

            # Load pipeline with FP16 for memory efficiency
            if self._device == "cuda":
                self._pipeline = StableDiffusionXLPipeline.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16,
                    variant="fp16",
                    use_safetensors=True,
                )
            else:
                self._pipeline = StableDiffusionXLPipeline.from_pretrained(
                    self.model_id,
                    use_safetensors=True,
                )

            self._pipeline = self._pipeline.to(self._device)

            # Enable memory optimizations
            if self._device == "cuda":
                # Enable attention slicing to reduce VRAM usage
                self._pipeline.enable_attention_slicing()
                logger.debug("Enabled attention slicing")

            logger.info(f"SDXL pipeline loaded on {self._device}")
            self.vram_manager.log_status()

        except Exception as e:
            logger.error(f"Failed to load SDXL pipeline: {e}")
            raise RuntimeError(f"Model loading failed: {e}") from e

    def _unload_model(self) -> None:
        """Unload model and free VRAM."""
        if self._pipeline is None:
            return

        try:
            logger.debug("Unloading SDXL pipeline...")

            # Delete pipeline
            del self._pipeline
            self._pipeline = None
            self._device = None

            # Force cleanup
            self.vram_manager.force_cleanup()

        except Exception as e:
            logger.error(f"Error during model unload: {e}")

    def _enhance_prompt(self, prompt: str) -> str:
        """
        Enhance prompt for better portrait generation.

        Args:
            prompt: Original prompt

        Returns:
            Enhanced prompt with quality modifiers
        """
        # Add quality and style modifiers if not present
        quality_keywords = [
            "professional",
            "high quality",
            "detailed",
            "portrait",
        ]

        # Check if prompt already has quality keywords
        prompt_lower = prompt.lower()
        has_quality = any(kw in prompt_lower for kw in quality_keywords)

        if not has_quality:
            # Add professional portrait modifiers
            enhanced = f"professional portrait, {prompt}, high quality, detailed face, studio lighting, 8k"
        else:
            enhanced = prompt

        return enhanced

    def _extract_name_from_prompt(self, prompt: str) -> str:
        """
        Extract a profile name from the prompt.

        Args:
            prompt: Generation prompt

        Returns:
            Extracted name (first 2-3 words or timestamp)
        """
        # Take first few words as name, max 30 chars
        words = prompt.split()[:3]
        name = " ".join(words)

        if len(name) > 30:
            name = name[:30]

        # If name is empty or very short, use timestamp
        if len(name) < 3:
            from datetime import datetime

            name = f"Avatar_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return name
