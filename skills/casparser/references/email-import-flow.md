# Email Import Flow (Gmail OAuth)

## Overview

The Email Import feature lets users connect their Gmail inbox so your application can find and download CAS attachments automatically. This is a multi-step OAuth flow.

## Flow Diagram

```
Your App                   CAS Parser API              Google OAuth            User's Gmail
┌────────┐                ┌──────────────┐            ┌────────────┐          ┌───────────┐
│ Step 1  │──connect────▶│ /inbox/       │──redirect─▶│ Google     │          │           │
│         │               │ connect      │            │ consent    │          │           │
│         │               │              │◀─callback──│ screen     │          │           │
│         │◀─oauth_url───│              │            └────────────┘          │           │
│         │                              │                                    │           │
│ Step 2  │ User clicks oauth_url, authorizes, gets redirected back          │           │
│         │ with inbox_token in query params                                  │           │
│         │                                                                   │           │
│ Step 3  │──list cas───▶│ /inbox/cas    │──search──────────────────────────▶│ Find CAS  │
│         │◀─files[]─────│              │◀─attachments──────────────────────│ emails    │
│         │                                                                   │           │
│ Step 4  │ Download files using URLs, then parse with /v4/smart/parse       │           │
│         │                                                                   │           │
│ Step 5  │──disconnect─▶│ /inbox/       │──revoke token───────────────────▶│ Remove    │
│         │               │ disconnect   │                                    │ access    │
└────────┘                └──────────────┘                                    └───────────┘
```

## Step-by-Step

### Step 1: Initiate OAuth Connection

```
POST /v4/inbox/connect
x-api-key: your-api-key
Content-Type: application/json

{
  "redirect_uri": "https://yourapp.com/oauth-callback",
  "state": "random-csrf-token"
}
```

Response:
```json
{
  "status": "success",
  "oauth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
  "expires_in": 600
}
```

**Redirect the user** to `oauth_url`. The OAuth URL expires in ~10 minutes.

### Step 2: Handle OAuth Callback

After the user authorizes, Google redirects to your `redirect_uri` with query parameters:

**On success:**
```
https://yourapp.com/oauth-callback?inbox_token=encrypted_token_here&email=user@gmail.com&state=random-csrf-token
```

**On error:**
```
https://yourapp.com/oauth-callback?error=access_denied&state=random-csrf-token
```

**Store the `inbox_token` client-side** (localStorage, cookie, or state). You'll need it for all subsequent inbox API calls.

### Step 3: List CAS Files

```
POST /v4/inbox/cas
x-api-key: your-api-key
x-inbox-token: the-encrypted-token
Content-Type: application/json

{
  "cas_types": ["cdsl", "nsdl"],
  "start_date": "2025-01-01",
  "end_date": "2025-12-31"
}
```

Response:
```json
{
  "status": "success",
  "files": [
    {
      "message_id": "18d4a2b3c4d5e6f7",
      "filename": "cdsl_20250115_a1b2c3d4.pdf",
      "original_filename": "CDSL_CAS_Statement.pdf",
      "message_date": "2025-01-15",
      "cas_type": "cdsl",
      "size": 245000,
      "url": "https://cdn.casparser.in/email-cas/user123/cdsl_20250115_a1b2c3d4.pdf",
      "expires_in": 86400
    }
  ],
  "count": 1
}
```

**Important:** Download URLs expire in 24 hours.

### Step 4: Parse Downloaded Files

Use the download URL with the smart parse endpoint:

```
POST /v4/smart/parse
x-api-key: your-api-key
Content-Type: application/json

{
  "pdf_url": "https://cdn.casparser.in/email-cas/user123/cdsl_20250115_a1b2c3d4.pdf",
  "password": "user-pdf-password"
}
```

### Step 5: Check Status / Disconnect

Check if connection is still valid:
```
POST /v4/inbox/status
x-api-key: your-api-key
x-inbox-token: the-encrypted-token
```

Disconnect and revoke access:
```
POST /v4/inbox/disconnect
x-api-key: your-api-key
x-inbox-token: the-encrypted-token
```

## CAS Provider Email Addresses

The API searches for emails from these known senders:

| Provider | Sender Email |
|----------|-------------|
| CDSL | `eCAS@cdslstatement.com` |
| NSDL | `NSDL-CAS@nsdl.co.in` |
| CAMS | `donotreply@camsonline.com` |
| KFintech | `samfS@kfintech.com` |

## Filtering Options

| Parameter | Type | Description |
|-----------|------|-------------|
| `cas_types` | `string[]` | Filter by provider: `"cdsl"`, `"nsdl"`, `"cams"`, `"kfintech"` |
| `start_date` | `string` | Start date (YYYY-MM-DD). Default: 30 days ago |
| `end_date` | `string` | End date (YYYY-MM-DD). Default: today |

## Security Notes

- **Read-only access** — the API cannot send emails or modify the inbox
- Tokens are encrypted with a server-side secret
- Users can revoke access anytime via `/v4/inbox/disconnect`
- Users can also revoke via [Google Account settings](https://myaccount.google.com/permissions)

## Billing

Each call to `/v4/inbox/cas` costs **0.2 credits**, regardless of success or number of files found.

## Related Templates

- [`templates/python-email-import.py`](../templates/python-email-import.py)
- [`templates/nodejs-email-import.js`](../templates/nodejs-email-import.js)
