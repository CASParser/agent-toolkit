"""
CAS Parser — Gmail Email Import (Python)

Full OAuth flow to import CAS files from a user's Gmail inbox.

Flow:
  1. Get OAuth URL → redirect user
  2. User authorizes → you receive inbox_token
  3. List CAS files from inbox
  4. Download and parse files

Requirements:
    pip install requests
"""

import os
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://portfolio-parser.api.casparser.in"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def connect_inbox(redirect_uri: str, state: str = "") -> str:
    """
    Step 1: Get OAuth URL for Gmail connection.

    Args:
        redirect_uri: Your callback URL (e.g., "https://yourapp.com/oauth-callback")
        state: CSRF protection token (optional but recommended)

    Returns:
        OAuth URL to redirect the user to
    """
    payload = {"redirect_uri": redirect_uri}
    if state:
        payload["state"] = state

    response = requests.post(
        f"{BASE_URL}/v4/inbox/connect",
        headers=HEADERS,
        json=payload,
        timeout=10,
    )

    result = response.json()
    if result.get("status") != "success":
        raise Exception(f"Connect failed: {result.get('msg', 'Unknown error')}")

    oauth_url = result["oauth_url"]
    print(f"Redirect user to: {oauth_url}")
    return oauth_url


def check_inbox_status(inbox_token: str) -> dict:
    """Check if an inbox connection is still valid."""
    response = requests.post(
        f"{BASE_URL}/v4/inbox/status",
        headers={**HEADERS, "x-inbox-token": inbox_token},
        timeout=10,
    )
    return response.json()


def list_cas_files(
    inbox_token: str,
    cas_types: list = None,
    start_date: str = None,
    end_date: str = None,
) -> list:
    """
    Step 3: List CAS files from the user's email inbox.

    Args:
        inbox_token: Token received after OAuth callback
        cas_types: Filter by provider(s) — ["cdsl", "nsdl", "cams", "kfintech"]
        start_date: Start date filter (YYYY-MM-DD)
        end_date: End date filter (YYYY-MM-DD)

    Returns:
        List of CAS file dicts with download URLs (expire in 24h)
    """
    payload = {}
    if cas_types:
        payload["cas_types"] = cas_types
    if start_date:
        payload["start_date"] = start_date
    if end_date:
        payload["end_date"] = end_date

    response = requests.post(
        f"{BASE_URL}/v4/inbox/cas",
        headers={**HEADERS, "x-inbox-token": inbox_token},
        json=payload if payload else None,
        timeout=30,
    )

    result = response.json()
    if result.get("status") != "success":
        # Check if reconnection is needed
        if result.get("requires_reconnect"):
            raise Exception("Email access revoked. User must reconnect.")
        raise Exception(f"List failed: {result.get('msg', 'Unknown error')}")

    files = result.get("files", [])
    print(f"Found {result.get('count', len(files))} CAS files")
    return files


def disconnect_inbox(inbox_token: str):
    """Revoke email access and invalidate the token."""
    response = requests.post(
        f"{BASE_URL}/v4/inbox/disconnect",
        headers={**HEADERS, "x-inbox-token": inbox_token},
        timeout=10,
    )
    result = response.json()
    print(f"Disconnected: {result.get('msg', 'Done')}")


# Example usage:
if __name__ == "__main__":
    # Step 1: Get OAuth URL
    oauth_url = connect_inbox(
        redirect_uri="https://yourapp.com/oauth-callback",
        state="random-csrf-token",
    )
    print(f"\nRedirect user to:\n{oauth_url}\n")

    # Step 2: After user authorizes, you receive inbox_token in the callback
    inbox_token = input("Paste the inbox_token from callback: ")

    # Step 3: List CAS files (optionally filter by type/date)
    files = list_cas_files(
        inbox_token,
        cas_types=["cdsl", "nsdl"],  # Optional filter
        start_date="2025-01-01",
    )

    for f in files:
        print(f"  [{f.get('cas_type', '?')}] {f.get('filename', 'unknown')} — {f.get('message_date', '?')}")
        print(f"    URL: {f.get('url', 'N/A')} (expires in {f.get('expires_in', 0) // 3600}h)")

    # Step 4: Parse the downloaded files using /v4/smart/parse with pdf_url
    # (See python-smart-parse.py for the parsing step)
