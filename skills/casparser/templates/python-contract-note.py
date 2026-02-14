"""
CAS Parser — Parse Contract Note PDF (Python)

Parses broker contract notes from Zerodha, Groww, Upstox, ICICI, and others.
Auto-detects broker type from the PDF content.

Usage:
    python python-contract-note.py /path/to/contract_note.pdf "PAN_NUMBER"

Requirements:
    pip install requests
"""

import os
import sys
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
BASE_URL = "https://portfolio-parser.api.casparser.in"


def parse_contract_note(pdf_path: str, password: str, broker_type: str = None) -> dict:
    """
    Parse a contract note PDF.

    Args:
        pdf_path: Path to the contract note PDF
        password: PDF password (usually client's PAN number)
        broker_type: Optional override — "zerodha", "groww", "upstox", "icici"
                     If not provided, auto-detected from PDF content.

    Returns:
        Parsed contract note data with trades, charges, and client info
    """
    data = {"password": password}
    if broker_type:
        data["broker_type"] = broker_type

    with open(pdf_path, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/v4/contract_note/parse",
            headers={"x-api-key": API_KEY},
            files={"pdf_file": (os.path.basename(pdf_path), f, "application/pdf")},
            data=data,
            timeout=60,
        )

    request_id = response.headers.get("X-Request-ID", "unknown")
    result = response.json()

    if result.get("status") != "success":
        raise Exception(f"Parse failed (req: {request_id}): {result.get('msg', 'Unknown error')}")

    return result.get("data", {})


def print_contract_note_summary(data: dict):
    """Print a human-readable summary of the parsed contract note."""
    info = data.get("contract_note_info", {})
    broker = data.get("broker_info", {})
    client = data.get("client_info", {})
    charges = data.get("charges_summary", {})

    print(f"\n{'='*50}")
    print(f"Broker: {broker.get('name', 'Unknown')} ({broker.get('broker_type', '?')})")
    print(f"Client: {client.get('name', 'N/A')} (PAN: {client.get('pan', 'N/A')})")
    print(f"Trade Date: {info.get('trade_date', 'N/A')}")
    print(f"Settlement: {info.get('settlement_date', 'N/A')}")

    equities = data.get("equity_transactions", [])
    if equities:
        print(f"\nEquity Transactions ({len(equities)} securities):")
        for tx in equities:
            name = tx.get("security_name", "Unknown")
            buy_qty = tx.get("buy_quantity", 0)
            sell_qty = tx.get("sell_quantity", 0)
            net = tx.get("net_obligation", 0)
            side = f"BUY {buy_qty}" if buy_qty else f"SELL {sell_qty}"
            print(f"  {name}: {side}, Net: Rs.{net:,.2f}")

    trades = data.get("detailed_trades", [])
    if trades:
        print(f"\nDetailed Trades: {len(trades)} individual trades")

    if charges:
        print(f"\nNet Amount: Rs.{charges.get('net_amount_receivable_payable', 0):,.2f}")

    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python python-contract-note.py <pdf_path> <password> [broker_type]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    password = sys.argv[2]
    broker = sys.argv[3] if len(sys.argv) > 3 else None

    data = parse_contract_note(pdf_path, password, broker)
    print_contract_note_summary(data)
