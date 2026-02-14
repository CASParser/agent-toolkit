"""
CAS Parser — Check Credits & Usage (Python)

Monitor your API quota, usage logs, and feature-level analytics.

Requirements:
    pip install requests
"""

import os
import requests

API_KEY = os.environ.get("CASPARSER_API_KEY", "sandbox-with-json-responses")
AUTH_BASE_URL = "https://client-apis.casparser.in"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}


def check_credits() -> dict:
    """Check remaining API credits and enabled features."""
    response = requests.post(
        f"{AUTH_BASE_URL}/credits",
        headers=HEADERS,
        timeout=10,
    )
    result = response.json()

    print(f"Credits Used: {result.get('used', 0)}")
    print(f"Credits Remaining: {result.get('remaining', 'unlimited')}")
    print(f"Credit Limit: {result.get('limit', 'N/A')}")
    print(f"Resets At: {result.get('resets_at', 'N/A')}")
    print(f"Enabled Features: {', '.join(result.get('enabled_features', []))}")

    return result


def get_usage_logs(start_time: str = None, end_time: str = None, limit: int = 50) -> list:
    """
    Get detailed API usage logs.

    Args:
        start_time: ISO 8601 datetime (defaults to 30 days ago)
        end_time: ISO 8601 datetime (defaults to now)
        limit: Max logs to return (1-500, default 100)

    Returns:
        List of log entries with request_id, feature, status_code, credits, timestamp
    """
    payload = {"limit": limit}
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    response = requests.post(
        f"{AUTH_BASE_URL}/logs",
        headers=HEADERS,
        json=payload,
        timeout=10,
    )

    result = response.json()
    logs = result.get("logs", [])

    for log in logs[:10]:  # Print first 10
        print(f"  [{log.get('timestamp', '?')}] {log.get('feature', '?')} "
              f"→ {log.get('status_code', '?')} ({log.get('credits', 0)} credits) "
              f"req: {log.get('request_id', '?')}")

    return logs


def get_usage_summary(start_time: str = None, end_time: str = None) -> dict:
    """
    Get aggregated usage statistics grouped by feature.

    Returns:
        Summary dict with total_credits, total_requests, and by_feature breakdown
    """
    payload = {}
    if start_time:
        payload["start_time"] = start_time
    if end_time:
        payload["end_time"] = end_time

    response = requests.post(
        f"{AUTH_BASE_URL}/logs/summary",
        headers=HEADERS,
        json=payload if payload else None,
        timeout=10,
    )

    result = response.json()
    summary = result.get("summary", {})

    print("\nUsage Summary:")
    print(f"  Total Credits: {summary.get('total_credits', 0)}")
    print(f"  Total Requests: {summary.get('total_requests', 0)}")

    for feature in summary.get("by_feature", []):
        print(f"  {feature.get('feature', '?')}: "
              f"{feature.get('requests', 0)} requests, "
              f"{feature.get('credits', 0)} credits")

    return summary


if __name__ == "__main__":
    print("=== Credits ===")
    check_credits()

    print("\n=== Recent Logs ===")
    get_usage_logs(limit=10)

    print("\n=== Summary ===")
    get_usage_summary()
