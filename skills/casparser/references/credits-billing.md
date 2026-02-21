# Credits & Billing

## Overview

CAS Parser uses a credit-based billing system. Each API call consumes credits based on the feature used. Credits reset at the start of each billing period.

## Credit Costs (Approximate)

Credit costs vary by plan. The table below shows typical costs:

| Feature | Typical Credits |
|---------|----------------|
| CAS Parse (smart, CDSL, NSDL, CAMS/KFintech) | ~1.0 |
| Contract Note Parse | ~1.0 |
| CDSL Fetch (OTP verify step) | ~1.5 |
| KFintech CAS Generator | ~2.0 |
| Email Import (list CAS files) | ~0.2 |

Check your actual credit costs via `POST /v1/credits` — the `enabled_features` field shows what's available on your plan. Only successful operations consume credits. Failed requests (invalid PDF, wrong password, etc.) do not consume credits.

## Checking Credits

```
POST https://api.casparser.in/v1/credits
x-api-key: your-api-key
```

**Note:** Must use your real API key, not an access token.

> Legacy path `/credits` is still supported for backward compatibility.

Response:
```json
{
  "used": 15.0,
  "remaining": 35.0,
  "limit": 50,
  "is_unlimited": false,
  "resets_at": "2026-02-15T00:00:00Z",
  "enabled_features": [
    "cams_kfintech_cas_parser",
    "cdsl_cas_parser",
    "nsdl_cas_parser",
    "contract_note_parser",
    "cdsl_otp_fetch",
    "email_import"
  ]
}
```

## Usage Logs

### Detailed Logs

```
POST https://api.casparser.in/v1/usage
x-api-key: your-api-key
Content-Type: application/json

{
  "start_time": "2026-01-01T00:00:00Z",
  "end_time": "2026-01-31T23:59:59Z",
  "limit": 100
}
```

Response:
```json
{
  "status": "success",
  "logs": [
    {
      "request_id": "req_2xYz7KpL8mN3Ab",
      "feature": "cdsl_cas_parser",
      "path": "/v4/cdsl/parse",
      "status_code": 200,
      "credits": 1.0,
      "timestamp": "2026-01-15T14:30:00Z"
    }
  ],
  "count": 25
}
```

### Usage Summary

```
POST https://api.casparser.in/v1/usage/summary
x-api-key: your-api-key
Content-Type: application/json

{
  "start_time": "2026-01-01T00:00:00Z"
}
```

Response:
```json
{
  "status": "success",
  "summary": {
    "total_credits": 45.5,
    "total_requests": 42,
    "by_feature": [
      { "feature": "cdsl_cas_parser", "credits": 15.0, "requests": 15 },
      { "feature": "nsdl_cas_parser", "credits": 10.0, "requests": 10 },
      { "feature": "cams_kfintech_cas_parser", "credits": 5.0, "requests": 5 },
      { "feature": "cdsl_otp_fetch", "credits": 9.0, "requests": 6 },
      { "feature": "email_import", "credits": 1.2, "requests": 6 }
    ]
  }
}
```

## Sandbox Mode

The sandbox key `sandbox-with-json-responses` does **not** consume credits. It returns realistic mock data for development and testing.

## Monitoring Best Practices

1. **Check credits on startup** — Verify you have credits before serving users
2. **Set up alerts** — Monitor `remaining` and alert when low
3. **Track by feature** — Use `/v1/usage/summary` to understand usage patterns
4. **Use request IDs** — Correlate logs with your application's request tracking

## Related Templates

- [`templates/python-credits-check.py`](../templates/python-credits-check.py)
- [`templates/curl-examples.sh`](../templates/curl-examples.sh) (sections 12-14)
