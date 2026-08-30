"""
CAS Parser — Registry Verification (Python)

Verify a financial intermediary's registration against SEBI's and AMFI's
official registers before onboarding them:
  - /v1/verify/sebi  — any SEBI intermediary (RIA, Research Analyst, PMS,
                       stock broker, mutual fund, AIF, ...). Category is
                       auto-detected from the registration number, or pass a
                       `type` (and to search by name).
  - /v1/verify/mfd   — an AMFI Mutual Fund Distributor by ARN, additionally
                       screened against AMFI's suspended / terminated /
                       terminated-EUIN lists.

`verified` is the boolean to gate onboarding on. A "not found" is a successful
200 with `verified: false`.

Usage:
    python python-verify.py sebi INA000000888
    python python-verify.py sebi INP000000670 portfolio-manager   # explicit type
    python python-verify.py sebi name "Motilal Oswal" portfolio-manager
    python python-verify.py mfd 89762

Requirements:
    pip install requests
"""

import os
import sys
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://api.casparser.in"


def _post(path: str, body: dict) -> dict:
    response = requests.post(
        f"{BASE_URL}{path}",
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
        json=body,
        timeout=30,
    )
    request_id = response.headers.get("X-Request-ID", "unknown")
    result = response.json()
    # A "not found" is a successful 200 (verified: false) — only real errors raise.
    if response.status_code != 200:
        raise Exception(f"Verification failed (req: {request_id}): {result.get('msg', 'Unknown error')}")
    return result


def verify_sebi(registration_number: str = None, name: str = None, type: str = None) -> dict:
    """Verify a SEBI-registered intermediary.

    Pass `registration_number` (category auto-detected) or `name` + `type`.
    `type` also overrides detection and is required for fund/FPI numbers.
    """
    body = {}
    if registration_number:
        body["registration_number"] = registration_number
    if name:
        body["name"] = name
    if type:
        body["type"] = type
    return _post("/v1/verify/sebi", body)


def verify_mfd(arn: str) -> dict:
    """Verify an AMFI Mutual Fund Distributor by ARN (with adverse-list screening)."""
    return _post("/v1/verify/mfd", {"arn": arn})


def print_verification(data: dict):
    """Print a human-readable summary of a verification result."""
    verified = data.get("verified")
    print(f"\n{'✓ VERIFIED' if verified else '✗ NOT VERIFIED'}")
    print(f"  Authority:  {data.get('authority')}")
    print(f"  Category:   {data.get('category_label')}")
    if data.get("name"):
        print(f"  Name:       {data['name']}")
    reg = data.get("registration_number") or data.get("arn")
    if reg:
        print(f"  Reg. no.:   {reg}")
    print(f"  Status:     {data.get('registration_status')}")
    if data.get("valid_from") or data.get("valid_till"):
        print(f"  Valid:      {data.get('valid_from')} -> {data.get('valid_till') or 'Perpetual'}")
    if data.get("kyd_compliant") is not None:
        print(f"  KYD:        {'compliant' if data['kyd_compliant'] else 'not compliant'}")
    if data.get("negative_list"):
        nl = data["negative_list"]
        print(f"  ADVERSE:    on AMFI '{nl['type']}' list (since {nl['since']})")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__)
        sys.exit(1)

    mode = args[0]
    if mode == "sebi":
        if args[1] == "name":
            # sebi name "<name>" <type>
            if len(args) < 4:
                print("Usage: python python-verify.py sebi name \"<name>\" <type>")
                sys.exit(1)
            data = verify_sebi(name=args[2], type=args[3])
        else:
            # sebi <registration_number> [type]
            data = verify_sebi(registration_number=args[1], type=args[2] if len(args) > 2 else None)
    elif mode == "mfd":
        data = verify_mfd(args[1])
    else:
        print("First argument must be 'sebi' or 'mfd'")
        sys.exit(1)

    print_verification(data)

    # `verified` is the gate: gate onboarding on it.
    sys.exit(0 if data.get("verified") else 2)
