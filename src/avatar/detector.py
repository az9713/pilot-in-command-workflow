"""
Face detection using MediaPipe.

Detects faces in images and validates them for lip-sync compatibility.
"""

import logging
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from .interfaces import FaceDetectionResult, FaceDetectorInterface

logger = logging.getLogger(__name__)


class MediaPipeFaceDetector(FaceDetectorInterface):
    """
    MediaPipe face detection implementation.

    Uses MediaPipe Face Detection and Face Mesh for robust face detection
    and landmark extraction suitable for lip-sync validation.
    """

    def __init__(self, min_detection_confidence: float = 0.5):
        """
        Initialize MediaPipe face detector.

        Args:
            min_detection_confidence: Minimum confidence for detection (0.0-1.0)
        """
        self.min_detection_confidence = min_detection_confidence
        self._face_detection = None
        self._face_mesh = None

        logger.info("MediaPipe face detector initialized")

    def detect(self, image_path: Path) -> FaceDetectionResult:
        """
        Detect face in image.

        Args:
            image_path: Path to image file

        Returns:
            FaceDetectionResult with detection status and face data
        """
        try:
            # Validate image exists
            if not image_path.exists():
                raise FileNotFoundError(f"Image not found: {image_path}")

            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            # Convert BGR to RGB (MediaPipe expects RGB)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape

            # Initialize MediaPipe Face Detection
            if self._face_detection is None:
                import mediapipe as mp

                self._face_detection = mp.solutions.face_detection.FaceDetection(
                    min_detection_confidence=self.min_detection_confidence
                )

            # Detect faces
            results = self._face_detection.process(image_rgb)

            if not results.detections:
                logger.info("No face detected")
                return FaceDetectionResult(
                    detected=False,
                    face_region=None,
                    landmarks=None,
                    confidence=0.0,
                    error=None,
                )

            # Use the first detected face (highest confidence)
            detection = results.detections[0]
            confidence = detection.score[0]

            # Extract bounding box
            bbox = detection.location_data.relative_bounding_box
            face_region = {
                "x": int(bbox.xmin * width),
                "y": int(bbox.ymin * height),
                "width": int(bbox.width * width),
                "height": int(bbox.height * height),
            }

            # Extract key landmarks (eyes, nose, mouth, ears)
            landmarks = {}
            keypoint_names = [
                "right_eye",
                "left_eye",
                "nose_tip",
                "mouth_center",
                "right_ear",
                "left_ear",
            ]

            for idx, keypoint in enumerate(detection.location_data.relative_keypoints):
                if idx < len(keypoint_names):
                    landmarks[keypoint_names[idx]] = {
                        "x": int(keypoint.x * width),
                        "y": int(keypoint.y * height),
                    }

            logger.info(
                f"Face detected: confidence {confidence:.2f}, "
                f"region {face_region['width']}x{face_region['height']}"
            )

            return FaceDetectionResult(
                detected=True,
                face_region=face_region,
                landmarks=landmarks,
                confidence=confidence,
                error=None,
            )

        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return FaceDetectionResult(
                detected=False,
                face_region=None,
                landmarks=None,
                confidence=0.0,
                error=str(e),
            )

    def validate_for_lipsync(
        self, detection: FaceDetectionResult
    ) -> tuple[bool, str]:
        """
        Validate if detected face is suitable for lip-sync.

        Args:
            detection: FaceDetectionResult from detect()

        Returns:
            Tuple of (is_valid, reason_message)
        """
        # Check if face was detected
        if not detection.detected:
            return False, "No face detected in image"

        # Check detection confidence
        if detection.confidence < self.min_detection_confidence:
            return (
                False,
                f"Detection confidence too low: {detection.confidence:.2f} "
                f"(minimum: {self.min_detection_confidence})",
            )

        # Check face size (should be at least 128x128 pixels)
        face_region = detection.face_region
        min_face_size = 128

        if (
            face_region["width"] < min_face_size
            or face_region["height"] < min_face_size
        ):
            return (
                False,
                f"Face too small: {face_region['width']}x{face_region['height']} "
                f"(minimum: {min_face_size}x{min_face_size})",
            )

        # Check aspect ratio (face should be roughly portrait oriented)
        aspect_ratio = face_region["width"] / face_region["height"]
        if aspect_ratio < 0.5 or aspect_ratio > 1.5:
            return (
                False,
                f"Unusual face aspect ratio: {aspect_ratio:.2f} "
                f"(expected: 0.5-1.5)",
            )

        # Check landmarks (both eyes and mouth should be detected)
        landmarks = detection.landmarks
        required_landmarks = ["right_eye", "left_eye", "mouth_center"]

        if not all(lm in landmarks for lm in required_landmarks):
            missing = [lm for lm in required_landmarks if lm not in landmarks]
            return (
                False,
                f"Missing key facial landmarks: {', '.join(missing)}",
            )

        # Check face orientation (eyes should be roughly horizontal)
        left_eye = landmarks["left_eye"]
        right_eye = landmarks["right_eye"]

        eye_dy = abs(left_eye["y"] - right_eye["y"])
        eye_dx = abs(left_eye["x"] - right_eye["x"])

        if eye_dx == 0:
            return False, "Cannot determine face orientation"

        eye_angle = abs(np.arctan(eye_dy / eye_dx) * 180 / np.pi)

        if eye_angle > 15:
            return (
                False,
                f"Face is tilted: {eye_angle:.1f}° (maximum: 15°)",
            )

        # All checks passed
        return (
            True,
            f"Face is suitable for lip-sync (confidence: {detection.confidence:.2f})",
        )

    def get_face_mesh(self, image_path: Path) -> Optional[dict]:
        """
        Get detailed face mesh with 468 landmarks.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with face mesh data or None if detection failed

        Note:
            This provides detailed mesh for advanced lip-sync applications.
        """
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Failed to load image: {image_path}")
                return None

            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape

            # Initialize MediaPipe Face Mesh
            if self._face_mesh is None:
                import mediapipe as mp

                self._face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    min_detection_confidence=self.min_detection_confidence,
                )

            # Process image
            results = self._face_mesh.process(image_rgb)

            if not results.multi_face_landmarks:
                logger.info("No face mesh detected")
                return None

            # Extract landmarks
            face_landmarks = results.multi_face_landmarks[0]
            landmarks = []

            for landmark in face_landmarks.landmark:
                landmarks.append(
                    {
                        "x": int(landmark.x * width),
                        "y": int(landmark.y * height),
                        "z": landmark.z,  # Depth information
                    }
                )

            logger.info(f"Extracted face mesh with {len(landmarks)} landmarks")

            return {
                "num_landmarks": len(landmarks),
                "landmarks": landmarks,
                "image_width": width,
                "image_height": height,
            }

        except Exception as e:
            logger.error(f"Face mesh extraction failed: {e}")
            return None

    def __del__(self):
        """Cleanup MediaPipe resources."""
        if self._face_detection is not None:
            self._face_detection.close()
        if self._face_mesh is not None:
            self._face_mesh.close()
