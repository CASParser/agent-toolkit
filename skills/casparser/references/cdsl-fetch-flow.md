# CDSL Fetch Flow (OTP-Based)

## Overview

CDSL Fetch allows users to download their CAS directly from CDSL's portal without having a PDF on hand. It's a 2-step OTP-based process.

## Flow Diagram

```
Your App                   CAS Parser API              CDSL Portal
┌────────┐                ┌──────────────┐            ┌──────────────┐
│ Step 1  │──request OTP─▶│ /cdsl/fetch   │──captcha──▶│ Solve        │
│         │               │              │──login────▶│ reCAPTCHA    │
│         │               │              │──trigger──▶│ Send OTP     │
│         │◀─session_id──│              │            │ to mobile    │
│         │               │              │            └──────────────┘
│ (wait)  │ User receives OTP on registered mobile (~15-20s)
│         │                                            
│ Step 2  │──verify OTP──▶│ /cdsl/fetch/  │──verify──▶│ Validate OTP │
│         │               │ {id}/verify   │──fetch───▶│ Download CAS │
│         │◀─file URLs───│              │◀─PDFs─────│ files        │
└────────┘                └──────────────┘            └──────────────┘
```

## Step 1: Request OTP

```
POST /v4/cdsl/fetch
x-api-key: your-api-key
Content-Type: application/json

{
  "pan": "ABCDE1234F",
  "bo_id": "1234567890123456",
  "dob": "1990-01-15"
}
```

**Parameters:**
- `pan` — PAN number (10 characters)
- `bo_id` — CDSL Beneficiary Owner ID (16 digits)
- `dob` — Date of birth (YYYY-MM-DD)

**Response:**
```json
{
  "status": "success",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "msg": "OTP sent to registered mobile"
}
```

**Timing:** This step takes ~15-20 seconds because the API:
1. Navigates to CDSL's portal
2. Solves reCAPTCHA automatically
3. Submits login credentials
4. Triggers OTP delivery

The OTP is sent to the **user's registered mobile number** (the one linked to their CDSL account).

## Step 2: Verify OTP and Get Files

```
POST /v4/cdsl/fetch/{session_id}/verify
x-api-key: your-api-key
Content-Type: application/json

{
  "otp": "123456",
  "num_periods": 6
}
```

**Parameters:**
- `otp` — The OTP received on mobile
- `num_periods` — Number of monthly CAS statements to fetch (default: 6)

**Response:**
```json
{
  "status": "success",
  "msg": "Fetched 6 CAS files",
  "files": [
    {
      "filename": "CDSL_CAS_1234567890123456_NOV2025.pdf",
      "url": "https://cdn.casparser.in/cdsl-cas/session-id/CDSL_CAS_1234567890123456_NOV2025.pdf"
    },
    {
      "filename": "CDSL_CAS_1234567890123456_OCT2025.pdf",
      "url": "https://cdn.casparser.in/cdsl-cas/session-id/CDSL_CAS_1234567890123456_OCT2025.pdf"
    }
  ]
}
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `"Invalid PAN or BO ID"` | Wrong credentials | Verify PAN/BO ID format |
| `"Session expired"` | OTP took too long | Restart from Step 1 |
| `"Invalid OTP"` | Wrong OTP entered | Retry with correct OTP (same session) |
| `"CAPTCHA failed"` | Captcha solving failed | Retry from Step 1 |

## UX Best Practices

1. **Show a loading indicator** during Step 1 (15-20s is a long wait)
2. **Explain the OTP** — tell users to check their registered mobile
3. **Set a timeout** — sessions expire after a few minutes
4. **Auto-parse** — after getting file URLs, immediately parse them with `/v4/smart/parse`

## Billing

CDSL Fetch costs **1.5 credits** per successful verify step.

## Related Templates

- [`templates/python-cdsl-fetch.py`](../templates/python-cdsl-fetch.py)
- [`templates/nodejs-cdsl-fetch.js`](../templates/nodejs-cdsl-fetch.js)
