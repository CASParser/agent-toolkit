"""
CAS Parser — KFintech CAS Generator (Python)

Triggers a CAS statement to be emailed to the investor via KFintech mailback.
This is an async operation — the PDF is sent to the investor's email, not returned.

For instant CAS retrieval, use CDSL Fetch instead (see python-cdsl-fetch.py).

Requirements:
    pip install requests
"""

import os
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://api.casparser.in"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def generate_kfintech_cas(
    email: str,
    from_date: str,
    to_date: str,
    password: str,
    pan_no: str = None,
) -> dict:
    """
    Trigger KFintech CAS mailback.

    Args:
        email: Investor's email to receive the CAS
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        password: Password for the generated PDF
        pan_no: PAN number (optional)

    Returns:
        Response dict with status and message.
        The CAS PDF will arrive in the investor's email within a few minutes.
    """
    payload = {
        "email": email,
        "from_date": from_date,
        "to_date": to_date,
        "password": password,
    }
    if pan_no:
        payload["pan_no"] = pan_no

    response = requests.post(
        f"{BASE_URL}/v4/generate",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )

    result = response.json()
    if result.get("status") != "success":
        raise Exception(f"Generation failed: {result.get('msg', 'Unknown error')}")

    print(f"CAS request submitted. Check {email} shortly.")
    return result


if __name__ == "__main__":
    result = generate_kfintech_cas(
        email="investor@example.com",
        from_date="2025-01-01",
        to_date="2025-12-31",
        password="YourPdfPassword123",
        pan_no="ABCDE1234F",
    )
    print(f"Status: {result.get('status')}")
    print(f"Message: {result.get('msg')}")
