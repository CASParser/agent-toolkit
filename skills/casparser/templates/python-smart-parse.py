"""
CAS Parser — Smart Parse CAS PDF (Python)

Auto-detects CAS type (CDSL, NSDL, or CAMS/KFintech) and returns unified JSON.
This is the recommended endpoint for most use cases.

Usage:
    python python-smart-parse.py /path/to/cas.pdf "your-pdf-password"

Requirements:
    pip install requests
"""

import os
import sys
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://api.casparser.in"


def smart_parse_file(pdf_path: str, password: str) -> dict:
    """Parse a CAS PDF file using smart auto-detection."""
    with open(pdf_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/v4/smart/parse",
            headers={"x-api-key": API_KEY},
            files={"pdf_file": (os.path.basename(pdf_path), f, "application/pdf")},
            data={"password": password},
            timeout=60,
        )

    request_id = response.headers.get("X-Request-ID", "unknown")
    result = response.json()

    if response.status_code != 200:
        raise Exception(f"Parse failed (req: {request_id}): {result.get('msg', 'Unknown error')}")

    return result


def smart_parse_url(pdf_url: str, password: str) -> dict:
    """Parse a CAS PDF from a URL using smart auto-detection."""
    response = requests.post(
        f"{BASE_URL}/v4/smart/parse",
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        json={"pdf_url": pdf_url, "password": password},
        timeout=60,
    )

    request_id = response.headers.get("X-Request-ID", "unknown")
    result = response.json()

    if response.status_code != 200:
        raise Exception(f"Parse failed (req: {request_id}): {result.get('msg', 'Unknown error')}")

    return result


def print_portfolio_summary(data: dict):
    """Print a human-readable summary of the parsed portfolio."""
    investor = data.get("investor", {})
    summary = data.get("summary", {})
    meta = data.get("meta", {})

    print(f"\n{'='*50}")
    print(f"CAS Type: {meta.get('cas_type', 'Unknown')}")
    print(f"Investor: {investor.get('name', 'N/A')}")
    print(f"PAN: {investor.get('pan', 'N/A')}")
    print(f"Period: {meta.get('statement_period', {}).get('from', '?')} to {meta.get('statement_period', {}).get('to', '?')}")
    print(f"\nTotal Portfolio Value: ₹{summary.get('total_value', 0):,.2f}")

    accounts = summary.get("accounts", {})
    for category, info in accounts.items():
        if info.get("count", 0) > 0:
            print(f"  {category}: {info['count']} accounts, ₹{info.get('total_value', 0):,.2f}")

    # List demat holdings
    for account in data.get("demat_accounts", []):
        print(f"\nDemat: {account.get('dp_name', 'Unknown')} ({account.get('demat_type', '')})")
        for equity in account.get("holdings", {}).get("equities", []):
            print(f"  {equity.get('name', 'Unknown')}: {equity.get('units', 0)} units, ₹{equity.get('value', 0):,.2f}")

    # List mutual fund schemes
    for folio in data.get("mutual_funds", []):
        print(f"\nFolio: {folio.get('folio_number', 'Unknown')} ({folio.get('amc', '')})")
        for scheme in folio.get("schemes", []):
            print(f"  {scheme.get('name', 'Unknown')}: {scheme.get('units', 0)} units, ₹{scheme.get('value', 0):,.2f}")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python python-smart-parse.py <pdf_path_or_url> <password>")
        sys.exit(1)

    source = sys.argv[1]
    password = sys.argv[2]

    if source.startswith("http"):
        data = smart_parse_url(source, password)
    else:
        data = smart_parse_file(source, password)

    print_portfolio_summary(data)
