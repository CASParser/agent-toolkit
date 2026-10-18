"""
CAS Parser — CAS Generator (Python)

Triggers a CAS statement to be emailed to the investor via KFintech/CAMS mailback.
KFintech and CAMS have a mutual partnership for data sharing and consolidation,
so this retrieves mutual fund data from both RTAs.
This is an async operation — the PDF is sent to the investor's email, not returned.
By default, a Detailed CAS is generated (complete transaction history). The parsing
layer supports all statement types, but generation always requests the Detailed variant.

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
    cas_authority: str = "kfintech",
) -> dict:
    """
    Trigger CAS mailback via KFintech or CAMS.

    Args:
        email: Investor's email to receive the CAS
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        password: Password protecting the generated PDF. Must satisfy the chosen
            authority's policy — CAMS requires 6-20 chars with at least two digits,
            so a PAN works there; KFintech's policy is stricter.
        pan_no: PAN number (optional)
        cas_authority: Which RTA sends the mailback — "kfintech" (default) or
            "cams". This only picks the sender; both RTAs share folio data, so you
            get the same portfolio either way. Choose "cams" if you want to use the
            investor's PAN as the PDF password instead of storing a separate secret.

    Returns:
        Response dict with status and message.
        The CAS PDF will arrive in the investor's email within a few minutes.
    """
    payload = {
        "email": email,
        "from_date": from_date,
        "to_date": to_date,
        "password": password,
        "cas_authority": cas_authority,
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
