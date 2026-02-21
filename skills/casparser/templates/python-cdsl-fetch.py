"""
CAS Parser — CDSL Fetch via OTP (Python)

Two-step flow to download CAS directly from CDSL:
  Step 1: Request OTP (sent to user's registered mobile)
  Step 2: Verify OTP and get download URLs

Requirements:
    pip install requests
"""

import os
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://api.casparser.in"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def request_otp(pan: str, bo_id: str, dob: str) -> str:
    """
    Step 1: Request OTP for CDSL CAS fetch.

    Args:
        pan: PAN number (e.g., "ABCDE1234F")
        bo_id: CDSL BO ID, 16 digits (e.g., "1234567890123456")
        dob: Date of birth, YYYY-MM-DD (e.g., "1990-01-15")

    Returns:
        session_id to use in Step 2

    Note: This takes ~15-20 seconds (captcha solving).
          OTP is sent to the user's registered mobile number.
    """
    response = requests.post(
        f"{BASE_URL}/v4/cdsl/fetch",
        headers=HEADERS,
        json={"pan": pan, "bo_id": bo_id, "dob": dob},
        timeout=30,
    )

    result = response.json()
    if result.get("status") != "success":
        raise Exception(f"OTP request failed: {result.get('msg', 'Unknown error')}")

    session_id = result["session_id"]
    print(f"OTP sent to registered mobile. Session: {session_id}")
    return session_id


def verify_otp(session_id: str, otp: str, num_periods: int = 6) -> list:
    """
    Step 2: Verify OTP and get CAS file download URLs.

    Args:
        session_id: From Step 1
        otp: OTP received on mobile (e.g., "123456")
        num_periods: Number of monthly statements to fetch (default 6)

    Returns:
        List of file dicts with 'filename' and 'url' keys
    """
    response = requests.post(
        f"{BASE_URL}/v4/cdsl/fetch/{session_id}/verify",
        headers=HEADERS,
        json={"otp": otp, "num_periods": num_periods},
        timeout=60,
    )

    result = response.json()
    if result.get("status") != "success":
        raise Exception(f"OTP verification failed: {result.get('msg', 'Unknown error')}")

    files = result.get("files", [])
    print(f"Fetched {len(files)} CAS files")
    return files


# Example usage:
if __name__ == "__main__":
    # Step 1: Request OTP
    session_id = request_otp(
        pan="ABCDE1234F",
        bo_id="1234567890123456",
        dob="1990-01-15",
    )

    # Step 2: Get OTP from user
    otp = input("Enter OTP received on mobile: ")

    # Step 3: Verify and download
    files = verify_otp(session_id, otp, num_periods=6)

    for f in files:
        print(f"  {f['filename']}: {f['url']}")
