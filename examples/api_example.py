"""
Example: API server usage.

Demonstrates starting the FastAPI server and making requests.
"""

import time

import requests


def test_api():
    """Test API endpoints."""
    base_url = "http://localhost:8000"

    print("=" * 70)
    print("Avatar Pipeline - API Test")
    print("=" * 70)

    # Test health check
    print("\n[1] Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test system status
    print("\n[2] Testing status endpoint...")
    response = requests.get(f"{base_url}/status")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

    # Test job submission
    print("\n[3] Submitting pipeline job...")
    job_data = {
        "text": "Hello, this is a test!",
        "voice_profile_id": "vp-example",
        "avatar_image_path": "examples/avatar.png",
        "quality": "high",
    }
    response = requests.post(f"{base_url}/jobs", json=job_data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")

    if response.status_code == 202:
        job_id = result["job_id"]

        # Check job status
        print(f"\n[4] Checking job status: {job_id}...")
        time.sleep(1)  # Wait a moment
        response = requests.get(f"{base_url}/jobs/{job_id}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

    # List all jobs
    print("\n[5] Listing all jobs...")
    response = requests.get(f"{base_url}/jobs")
    print(f"Status: {response.status_code}")
    jobs = response.json()
    print(f"Total jobs: {jobs['total']}")

    print("\n" + "=" * 70)
    print("API test complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Start server first with: avatar server start
    # Then run this script
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API server.")
        print("Start server with: avatar server start")
