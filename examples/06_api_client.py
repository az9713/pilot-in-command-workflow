"""
Example 06: REST API Client

Demonstrates how to interact with the Avatar Pipeline REST API.

Requirements:
    - API server running (start with: avatar server start)
    - requests library (pip install requests)

Usage:
    # Terminal 1: Start server
    avatar server start

    # Terminal 2: Run example
    python examples/06_api_client.py
"""

import time
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Error: requests library not found")
    print("Install with: pip install requests")
    exit(1)


class AvatarPipelineClient:
    """Simple client for Avatar Pipeline REST API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"

    def health_check(self) -> bool:
        """
        Check if API server is running.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def submit_pipeline_job(
        self,
        text: str,
        voice_profile_id: str,
        avatar_image_path: str,
        output_path: str,
        quality: str = "high",
    ) -> Optional[str]:
        """
        Submit a full pipeline job.

        Args:
            text: Text to convert to speech
            voice_profile_id: Voice profile ID to use
            avatar_image_path: Path to avatar image
            output_path: Where to save output video
            quality: Video quality ("high", "medium", "low")

        Returns:
            Job ID if successful, None otherwise
        """
        payload = {
            "text": text,
            "voice_profile_id": voice_profile_id,
            "avatar_image_path": avatar_image_path,
            "output_path": output_path,
            "config": {
                "video_quality": quality,
                "cleanup_intermediates": True,
            },
        }

        try:
            response = requests.post(
                f"{self.api_base}/jobs/pipeline",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            return response.json()["job_id"]
        except requests.RequestException as e:
            print(f"Error submitting job: {e}")
            return None

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get status of a job.

        Args:
            job_id: Job ID

        Returns:
            Job status dict if successful, None otherwise
        """
        try:
            response = requests.get(f"{self.api_base}/jobs/{job_id}", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error getting job status: {e}")
            return None

    def wait_for_job(
        self, job_id: str, poll_interval: float = 2.0, timeout: float = 600.0
    ) -> Optional[dict]:
        """
        Wait for job to complete.

        Args:
            job_id: Job ID
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait

        Returns:
            Final job status if completed, None if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_job_status(job_id)

            if not status:
                return None

            # Check if job is done
            if status["status"] in ["completed", "failed", "cancelled"]:
                return status

            # Show progress
            print(
                f"  Status: {status['status']} | "
                f"Progress: {status['progress'] * 100:.1f}% | "
                f"Stage: {status.get('stage', 'N/A')}"
            )

            time.sleep(poll_interval)

        print("Timeout waiting for job to complete")
        return None

    def list_jobs(self, status: Optional[str] = None, limit: int = 10) -> list:
        """
        List jobs.

        Args:
            status: Filter by status (optional)
            limit: Maximum number of jobs to return

        Returns:
            List of job dicts
        """
        params = {"limit": limit}
        if status:
            params["status"] = status

        try:
            response = requests.get(
                f"{self.api_base}/jobs", params=params, timeout=5
            )
            response.raise_for_status()
            return response.json()["jobs"]
        except requests.RequestException as e:
            print(f"Error listing jobs: {e}")
            return []


def main():
    """Demonstrate API client usage."""
    print("=" * 70)
    print("Example 06: REST API Client")
    print("=" * 70)

    # Initialize client
    client = AvatarPipelineClient()

    # Check server health
    print("\n[1/5] Checking API server...")
    if not client.health_check():
        print("Error: API server not responding")
        print("\nPlease start the server:")
        print("  avatar server start")
        print("\nThen run this example again.")
        return

    print("API server is running")

    # Submit a job
    print("\n[2/5] Submitting pipeline job...")
    job_id = client.submit_pipeline_job(
        text="Hello from the API! This is a test of the complete pipeline.",
        voice_profile_id="vp-example",  # Replace with your profile ID
        avatar_image_path="output/generated_avatar.png",  # Replace with your image
        output_path="output/api_test_video.mp4",
        quality="high",
    )

    if not job_id:
        print("Error: Failed to submit job")
        print("\nPlease check:")
        print("  - Voice profile exists")
        print("  - Avatar image exists")
        print("  - Server logs for errors")
        return

    print(f"Job submitted successfully: {job_id}")

    # Wait for completion
    print("\n[3/5] Waiting for job to complete...")
    print("(This may take several minutes)\n")

    final_status = client.wait_for_job(job_id, poll_interval=2.0, timeout=600.0)

    if not final_status:
        print("\nError: Job did not complete in time")
        return

    # Display results
    print("\n[4/5] Job complete!")
    print("=" * 70)

    if final_status["status"] == "completed":
        print("\nSuccess!")
        print(f"  Job ID: {job_id}")
        print(f"  Status: {final_status['status']}")
        print(f"  Progress: {final_status['progress'] * 100:.0f}%")

        if "result" in final_status:
            result = final_status["result"]
            print(f"\n  Results:")
            for key, value in result.items():
                print(f"    {key}: {value}")

    elif final_status["status"] == "failed":
        print("\nJob failed!")
        print(f"  Error: {final_status.get('error', 'Unknown error')}")

    else:
        print(f"\nJob ended with status: {final_status['status']}")

    # List recent jobs
    print("\n[5/5] Recent jobs:")
    jobs = client.list_jobs(limit=5)

    if jobs:
        print(f"Found {len(jobs)} job(s):\n")
        for job in jobs:
            print(f"  {job['job_id']}")
            print(f"    Type: {job['job_type']}")
            print(f"    Status: {job['status']}")
            print(f"    Progress: {job['progress'] * 100:.1f}%")
            print()
    else:
        print("  No jobs found")

    print("=" * 70)

    # Additional examples
    print("\nAdditional API endpoints:")
    print("  - Voice cloning: POST /api/v1/voice/clone")
    print("  - Text-to-speech: POST /api/v1/voice/synthesize")
    print("  - Avatar generation: POST /api/v1/avatar/generate")
    print("  - Lip-sync video: POST /api/v1/video/lipsync")
    print("  - API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
