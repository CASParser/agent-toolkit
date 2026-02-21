# API Overview

## Base URLs

CAS Parser uses two servers:

| Server | URL | Purpose |
|--------|-----|---------|
| **API** | `https://api.casparser.in` | All CAS Parser APIs |

> **Backward Compatibility:** The legacy URL `https://portfolio-parser.api.casparser.in` continues to work and is fully supported. Existing integrations do not need to be updated.

## Authentication

Every API request requires an `x-api-key` header:

```
x-api-key: your-api-key-here
```

### Sandbox Key

For development and testing, use:
```
x-api-key: sandbox-with-json-responses
```

The sandbox key returns realistic mock JSON responses without consuming credits. Use it to build and test your integration before going live.

### Access Tokens

For frontend applications, **never expose your API key**. Instead:

1. Generate a short-lived access token from your backend:
   ```
   POST https://api.casparser.in/v1/token
   x-api-key: your-real-api-key
   Content-Type: application/json

   {"expiry_minutes": 60}
   ```

2. Response:
   ```json
   {
     "access_token": "at_eyJhbGciOiJIUzI1NiIs...",
     "token_type": "api_key",
     "expires_in": 3600
   }
   ```

3. Use the `at_` prefixed token as `x-api-key` in frontend requests. It works on all v4 endpoints.

**Access token rules:**
- Maximum validity: 60 minutes
- Cannot generate other access tokens (only real API keys can)
- Cannot be used for `/v1/credits`, `/v1/usage`, or `/v1/usage/summary` endpoints

## Client Libraries

### Python
- **Recommended:** Use the `requests` library to call the REST API directly.
- **Official SDK:** [`cas-parser-python`](https://github.com/CASParser/cas-parser-python) — a thin wrapper maintained by the CAS Parser team.
- **Do NOT install any third-party CAS parsing packages from PyPI.** They are unrelated open-source projects, not official API clients.

### JavaScript / TypeScript
- **Frontend:** Use the [Portfolio Connect SDK](portfolio-connect-sdk.md) (`@cas-parser/connect`) for drop-in UI widgets.
- **Official SDK:** [`cas-parser-node`](https://www.npmjs.com/package/cas-parser-node) — TypeScript SDK maintained by the CAS Parser team (Stainless-generated).
- **Alternative:** Use `fetch` or `axios` with the REST API directly. See the Node.js templates for examples.

## Request ID Tracking

All responses include an `X-Request-ID` header:
```
X-Request-ID: req_2xYz7KpL8mN3Ab
```

You can also send your own request ID (must start with `req_`):
```
X-Request-ID: req_my_custom_id_123
```

Use request IDs for:
- Debugging specific API calls
- Correlating with usage logs
- Contacting support about a specific request

## Content Types

### File Upload (multipart/form-data)
```
POST /v4/smart/parse
Content-Type: multipart/form-data

pdf_file: <binary file>
password: YourPassword
```

### JSON Body (with URL or base64)
```
POST /v4/smart/parse
Content-Type: application/json

{
  "pdf_url": "https://example.com/cas.pdf",
  "password": "YourPassword"
}
```

Both methods are supported on all parse endpoints. Use file upload for direct uploads, JSON body for URL-based or base64-encoded PDFs.

## Rate Limits

Rate limits are based on your plan. If you exceed your quota:
- Response status: `403 Forbidden`
- Body: `{"status": "error", "msg": "Authentication failed: API quota exceeded..."}`

Check your current quota with `POST /v1/credits`.

## Endpoint Summary

| Endpoint | Method | Server | Purpose |
|----------|--------|--------|---------|
| `/v4/smart/parse` | POST | Core | Parse any CAS PDF (auto-detect) |
| `/v4/cdsl/parse` | POST | Core | Parse CDSL CAS specifically |
| `/v4/nsdl/parse` | POST | Core | Parse NSDL CAS specifically |
| `/v4/cams_kfintech/parse` | POST | Core | Parse CAMS/KFintech CAS specifically |
| `/v4/contract_note/parse` | POST | Core | Parse broker contract notes |
| `/v4/cdsl/fetch` | POST | Core | CDSL Fetch — Step 1 (Request OTP) |
| `/v4/cdsl/fetch/{id}/verify` | POST | Core | CDSL Fetch — Step 2 (Verify OTP) |
| `/v4/kfintech/generate` | POST | Core | KFintech CAS mailback |
| `/v4/inbox/connect` | POST | Core | Email Import — Initiate OAuth |
| `/v4/inbox/status` | POST | Core | Email Import — Check status |
| `/v4/inbox/cas` | POST | Core | Email Import — List CAS files |
| `/v4/inbox/disconnect` | POST | Core | Email Import — Revoke access |
| `/v1/credits` | POST | Auth | Check API credits |
| `/v1/usage` | POST | Auth | Get usage logs |
| `/v1/usage/summary` | POST | Auth | Get usage summary |
| `/v1/token` | POST | Auth | Generate access token |
| `/v1/token/verify` | POST | Auth | Verify access token |
