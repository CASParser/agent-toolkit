"""
CAS Parser — Inbound Email (Python)

Create dedicated email addresses for investors to forward CAS statements to.
When a CAS email is forwarded, the API validates the sender, uploads attachments
to cloud storage, and POSTs the details to your webhook callback URL.

Lower-friction alternative to OAuth or manual file upload.

Requirements:
    pip install requests flask
"""

import os
import requests
from flask import Flask, request, jsonify

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://api.casparser.in"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


# --- Step 1: Create an Inbound Email Address ---


def create_inbound_email(
    callback_url: str,
    allowed_sources: list = None,
    reference: str = None,
    alias: str = None,
) -> dict:
    """
    Create a dedicated inbound email address for CAS forwarding.

    Args:
        callback_url: Your webhook URL to receive parsed CAS data
        allowed_sources: List of accepted CAS types (cdsl, nsdl, cams, kfintech)
        reference: Optional reference ID for tracking (e.g., user_id)
        alias: Optional friendly address prefix (e.g., "john-portfolio")

    Returns:
        Response dict with email address and inbound_email_id.
    """
    payload = {"callback_url": callback_url}
    if allowed_sources:
        payload["allowed_sources"] = allowed_sources
    if reference:
        payload["reference"] = reference
    if alias:
        payload["alias"] = alias

    response = requests.post(
        f"{BASE_URL}/v4/inbound-email",
        headers=HEADERS,
        json=payload,
        timeout=10,
    )

    result = response.json()
    if response.status_code not in (200, 201):
        raise Exception(f"Failed to create inbound email: {result.get('msg', 'Unknown error')}")

    print(f"Inbound email created: {result.get('email')}")
    print(f"ID: {result.get('inbound_email_id')}")
    return result


def list_inbound_emails() -> dict:
    """List all inbound email addresses."""
    response = requests.get(
        f"{BASE_URL}/v4/inbound-email",
        headers={"x-api-key": API_KEY},
        timeout=10,
    )
    return response.json()


def delete_inbound_email(inbound_email_id: str) -> dict:
    """Delete an inbound email address."""
    response = requests.delete(
        f"{BASE_URL}/v4/inbound-email/{inbound_email_id}",
        headers={"x-api-key": API_KEY},
        timeout=10,
    )
    return response.json()


# --- Step 2: Handle Webhook (Flask Example) ---

app = Flask(__name__)


@app.route("/webhooks/cas-email", methods=["POST"])
def handle_cas_email():
    """
    Webhook handler for inbound CAS emails.

    The API sends a POST to your callback_url with:
    - inbound_email_id: The ID of the inbound email address
    - forwarded_by: The investor's email address
    - reference: Your reference ID (if provided during creation)
    - files: List of CAS PDF attachments with download URLs
    - count: Number of files

    Only emails from verified CAS authorities are processed:
    - CDSL: eCAS@cdslstatement.com
    - NSDL: NSDL-CAS@nsdl.co.in
    - CAMS: donotreply@camsonline.com
    - KFintech: samfS@kfintech.com
    """
    data = request.json
    print(f"Received CAS from: {data.get('forwarded_by')}")
    print(f"Reference: {data.get('reference')}")
    print(f"Files: {data.get('count')}")

    for file_info in data.get("files", []):
        print(f"  Type: {file_info.get('cas_type')}")
        print(f"  Filename: {file_info.get('filename')}")
        print(f"  Sender: {file_info.get('sender_email')}")
        print(f"  URL: {file_info.get('url')}")
        print(f"  Expires in: {file_info.get('expires_in')}s")

        # Download the PDF and parse it, or use the URL directly
        # URLs expire in 48 hours (172800 seconds)

    return jsonify({"status": "received"}), 200


# --- Main ---


if __name__ == "__main__":
    # Create an inbound email
    result = create_inbound_email(
        callback_url="https://yourapp.com/webhooks/cas-email",
        allowed_sources=["cdsl", "nsdl", "cams", "kfintech"],
        reference="user_12345",
    )
    print(f"\nTell the investor to forward CAS to: {result.get('email')}")

    # List all inbound emails
    emails = list_inbound_emails()
    print(f"\nActive inbound emails: {len(emails.get('inbound_emails', []))}")

    # To run the webhook handler:
    # app.run(port=5000)
