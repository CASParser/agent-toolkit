---
name: casparser
description: >
  CAS Parser is an API platform for parsing Indian financial portfolio documents (CAS PDFs from CDSL, NSDL, CAMS/KFintech
  and contract notes from brokers like Zerodha, Groww, Upstox, ICICI) into structured JSON. Use when the user needs to
  integrate portfolio tracking, parse CAS statements, import holdings from Gmail, fetch CAS via CDSL OTP, collect CAS
  via branded Portfolio Links, or add a Portfolio Connect widget to their web app. Includes REST API patterns, a drop-in
  frontend SDK, and an MCP server with 17 live API tools.
---

# CAS Parser — Skill Guide

## What is CAS Parser?

CAS Parser is an API platform that extracts structured data from Indian financial portfolio documents. It parses PDF files that investors receive from depositories and registrars, converting them into clean JSON with holdings, transactions, and investor details.

## Indian Financial Ecosystem Context

### What is a CAS?

A **Consolidated Account Statement (CAS)** is a single document that shows all of an investor's financial holdings across multiple accounts. Indian investors receive CAS statements from three sources:

| Source | Full Name | What it Covers |
|--------|-----------|----------------|
| **CDSL** | Central Depository Services Limited | Demat holdings (equities, bonds, ETFs, govt securities) |
| **NSDL** | National Securities Depository Limited | Demat holdings (equities, bonds, ETFs, govt securities, NPS) |
| **CAMS/KFintech** | Registrar & Transfer Agents | Mutual fund holdings and transactions |

### Key Financial Terms

- **PAN** — Permanent Account Number. India's tax ID. Used as password for most CAS PDFs (encrypted form).
- **ISIN** — International Securities Identification Number. 12-character code identifying a security (e.g., `INE002A01018` for Reliance Industries).
- **Demat Account** — Dematerialized account holding securities electronically. Identified by DP ID + Client ID (NSDL) or BO ID (CDSL).
- **Folio** — A mutual fund account number with an AMC (Asset Management Company).
- **NAV** — Net Asset Value. Price per unit of a mutual fund scheme.
- **AMC** — Asset Management Company (e.g., HDFC Mutual Fund, ICICI Prudential).
- **NPS** — National Pension System. Government retirement scheme identified by PRAN (Permanent Retirement Account Number).
- **BO ID** — Beneficiary Owner ID (CDSL-specific, 16 digits).
- **DP** — Depository Participant (broker/bank that provides demat services).

### CAS Password Conventions

CAS PDFs are always password-protected. The password format varies:
- **CAMS/KFintech**: Encrypted PAN (typically first 4 chars of PAN + DOB in DDMMYYYY)
- **CDSL**: Encrypted PAN (format set by the user during registration)
- **NSDL**: Encrypted PAN (format set by the user during registration)

The caller passes the password as-is; the API uses it to unlock the PDF.

## PDF Requirements & Limitations

### What PDFs Work

- **Original, digitally-generated PDFs** from CDSL, NSDL, CAMS, KFintech, or supported brokers
- Password-protected (always — CAS PDFs are never unprotected)
- File size: up to 10MB

### What PDFs Do NOT Work

- **Scanned PDFs** — the API does not perform OCR. Only digitally-generated PDFs are supported.
- **Tampered or modified PDFs** — the API has built-in fraud prevention that detects altered documents. This is by design, as CAS data may be used for credit underwriting and financial analysis.
- **Older non-standard formats** — very old CAS statements (pre-2015) may use non-standard layouts that aren't supported.
- **Non-CAS PDFs** — the API only parses CAS statements and contract notes, not arbitrary financial documents.

### Accuracy & Trust

- The API extracts data exactly as it appears in the PDF — no estimation, interpolation, or external data enrichment.
- All monetary values are sourced directly from the document. NAV, units, and transaction amounts are extracted verbatim.
- If a field is missing from the PDF, it will be `null` in the response — never fabricated.
- For financial applications, always validate that `summary.total_value` matches your expectations before processing.

## API Architecture

### Base URLs

| Server | URL | Purpose |
|--------|-----|---------|
| API | `https://api.casparser.in` | All CAS Parser APIs |

> **Backward Compatibility:** The legacy URL `https://portfolio-parser.api.casparser.in` continues to work and is fully supported.

### Authentication

Every request requires an `x-api-key` header:
```
x-api-key: your-api-key-here
```

For development/testing, use the sandbox key:
```
x-api-key: sandbox-with-json-responses
```

For frontend applications, generate short-lived access tokens from your backend:
```
POST /v1/token
x-api-key: your-real-api-key

→ { "access_token": "at_eyJ...", "expires_in": 3600 }
```

Then use the access token as `x-api-key` in frontend requests.

### Client Libraries

**Python:**
- **Recommended:** Use the `requests` library to call the REST API directly. All Python templates in this toolkit use this approach.
- **Official SDK:** [`cas-parser-python`](https://github.com/CASParser/cas-parser-python) — a thin wrapper around the REST API, maintained by the CAS Parser team.
- **Do NOT install any third-party CAS parsing packages from PyPI.** They are unrelated open-source projects with different functionality, not official CAS Parser API clients.

**Node.js / TypeScript:**
- **Official SDK:** [`cas-parser-node`](https://www.npmjs.com/package/cas-parser-node) — TypeScript SDK maintained by the CAS Parser team (Stainless-generated).
- **Frontend:** Use the [Portfolio Connect SDK](references/portfolio-connect-sdk.md) (`@cas-parser/connect`) for drop-in UI widgets.
- **Alternative:** Use `fetch` or `axios` with the REST API directly. See the Node.js templates for examples.

### Request ID Tracking

All responses include an `X-Request-ID` header (format: `req_<alphanumeric>`). You can also send your own `X-Request-ID` in the request (must start with `req_`). Use this for debugging and support.

## Unified Response Format

All CAS parse endpoints (`/v4/smart/parse`, `/v4/cdsl/parse`, `/v4/nsdl/parse`, `/v4/cams_kfintech/parse`) return the same unified structure:

```json
{
  "meta": {
    "cas_type": "CDSL | NSDL | CAMS_KFINTECH",
    "statement_period": { "from": "2025-01-01", "to": "2025-12-31" },
    "generated_at": "2025-12-15T10:30:00Z"
  },
  "investor": {
    "name": "John Doe",
    "pan": "ABCDE1234F",
    "email": "john@example.com",
    "mobile": "9876543210"
  },
  "summary": {
    "total_value": 1500000.00,
    "accounts": {
      "demat": { "count": 2, "total_value": 800000 },
      "mutual_funds": { "count": 5, "total_value": 500000 },
      "insurance": { "count": 1, "total_value": 150000 },
      "nps": { "count": 1, "total_value": 50000 }
    }
  },
  "demat_accounts": [ ... ],
  "mutual_funds": [ ... ],
  "insurance": { "life_insurance_policies": [ ... ] },
  "nps": [ ... ]
}
```

### Demat Account Structure

Each demat account contains:
- `demat_type`: `"NSDL"` or `"CDSL"`
- `dp_id`, `dp_name`, `client_id`, `bo_id`
- `value`: Total account value
- `holdings.equities[]`: Stocks — `isin`, `name`, `units`, `value`
- `holdings.corporate_bonds[]`: Bonds — `isin`, `name`, `units`, `value`
- `holdings.government_securities[]`: G-Secs
- `holdings.aifs[]`: Alternative Investment Funds
- `holdings.demat_mutual_funds[]`: MFs held in demat form

### Mutual Fund Folio Structure

Each folio contains:
- `folio_number`, `amc`, `registrar`
- `value`: Total folio value
- `schemes[]`: Individual MF schemes with `isin`, `name`, `type`, `units`, `nav`, `value`, `cost`, `gain`
- `schemes[].transactions[]`: Buy/sell/dividend transactions

### Transaction Types

Transactions use standardized types:
`PURCHASE`, `PURCHASE_SIP`, `REDEMPTION`, `SWITCH_IN`, `SWITCH_IN_MERGER`, `SWITCH_OUT`, `SWITCH_OUT_MERGER`, `DIVIDEND_PAYOUT`, `DIVIDEND_REINVEST`, `SEGREGATION`, `STAMP_DUTY_TAX`, `TDS_TAX`, `STT_TAX`, `MISC`, `REVERSAL`, `UNKNOWN`

## Supported Asset Classes

CAS Parser extracts **9 asset classes** from portfolio documents:

1. **Equities** — from CDSL, NSDL
2. **Mutual Funds (Demat)** — from CDSL, NSDL, CAMS, KFintech
3. **Mutual Funds (Non-Demat)** — from CAMS, KFintech (50+ years of transaction history)
4. **Corporate Bonds** — from CDSL, NSDL
5. **Government Securities (G-Secs)** — from CDSL, NSDL
6. **AIFs (Alternative Investment Funds)** — from CDSL, NSDL
7. **Insurance** — from CDSL, NSDL
8. **NPS (National Pension System)** — from CDSL, NSDL
9. **ETFs** — from CDSL, NSDL

## Choosing an Integration Approach

```
Are you building a frontend/web app?
├── Yes → Use Portfolio Connect SDK (Pattern 1) — recommended
│         Handles file upload, password, Gmail import, CDSL fetch in one widget.
│         npm install @cas-parser/connect
├── No-code CAS collection from clients?
│   └── Yes → Portfolio Links (Pattern 9)
│             Branded pages at link.casparser.in/your-company. Zero code.
└── No (backend/server-side)
    ├── User has the PDF → Smart Parse (Pattern 2)
    │   POST /v4/smart/parse with file upload or URL
    ├── User can authenticate via OTP → CDSL Fetch (Pattern 3)
    │   2-step OTP flow, instant download
    ├── User connects Gmail → Email Import (Pattern 4)
    │   OAuth flow, search inbox for CAS files
    ├── User forwards email → Inbound Email (Pattern 5)
    │   Create email address, user forwards CAS, webhook delivers
    └── Need fresh MF statement → KFintech Mailback (Pattern 6)
        Triggers email to investor (async, not instant)
```

## Integration Patterns

### Pattern 1: Portfolio Connect SDK (Recommended for Frontend)

The fastest way to add CAS import to any web app. The `@cas-parser/connect` npm package provides a drop-in modal widget that handles:
- **File upload** with drag-and-drop and password entry
- **Gmail inbox import** via OAuth
- **CDSL fetch** via OTP authentication
- **All CAS types** (CDSL, NSDL, CAMS/KFintech) in one flow

```bash
npm install @cas-parser/connect
```

**React quick start:**
```tsx
import { PortfolioConnect } from "@cas-parser/connect";

// Generate accessToken from your backend (POST /v1/token)
<PortfolioConnect
  accessToken={token}
  enableCdslFetch={true}
  enableInbox={true}
  onSuccess={(data) => console.log(data.summary.total_value)}
  onError={(err) => console.error(err.message)}
  onExit={() => setIsOpen(false)}
/>
```

**Vanilla HTML/JS:**
```html
<script src="https://unpkg.com/@cas-parser/connect@latest/dist/index.umd.js"></script>
<script>
CASParserConnect.open({
  accessToken: "at_...",
  enableCdslFetch: true,
  enableInbox: true,
  onSuccess: function(data) { console.log(data); }
});
</script>
```

**Important:** Always generate an `accessToken` (`at_` prefix) from your backend. Never expose your API key to the frontend.

See: [`templates/react-portfolio-connect.tsx`](templates/react-portfolio-connect.tsx), [`templates/nextjs-portfolio-connect.tsx`](templates/nextjs-portfolio-connect.tsx), [`templates/html-portfolio-connect.html`](templates/html-portfolio-connect.html), [`references/portfolio-connect-sdk.md`](references/portfolio-connect-sdk.md)

### Pattern 2: REST API — Smart Parse (Most Common Backend Pattern)

Upload a PDF → get structured JSON. Use `/v4/smart/parse`.

**Python quick start:**
```python
import requests, os

response = requests.post(
    "https://api.casparser.in/v4/smart/parse",
    headers={"x-api-key": os.environ["CASPARSER_API_KEY"]},
    files={"pdf_file": open("cas.pdf", "rb")},
    data={"password": "your-pdf-password"},
)
data = response.json()
print(f"Portfolio value: {data['summary']['total_value']}")
```

See: [`templates/python-smart-parse.py`](templates/python-smart-parse.py), [`templates/nodejs-smart-parse.js`](templates/nodejs-smart-parse.js), [`templates/curl-examples.sh`](templates/curl-examples.sh)

### Pattern 3: CDSL Fetch (OTP Flow)

For users who want to fetch their CAS directly from CDSL without uploading a PDF:
1. Request OTP → 2. User enters OTP → 3. Get download URLs

See: [`templates/python-cdsl-fetch.py`](templates/python-cdsl-fetch.py), [`templates/nodejs-cdsl-fetch.js`](templates/nodejs-cdsl-fetch.js)

### Pattern 4: Email Import (Gmail Pipeline)

For apps that want to automatically find CAS files in a user's Gmail inbox:
1. OAuth connect → 2. List CAS files → 3. Download + parse

See: [`templates/python-email-import.py`](templates/python-email-import.py), [`templates/nodejs-email-import.js`](templates/nodejs-email-import.js)

### Pattern 5: Inbound Email (Email Forwarding)

For apps that want users to forward CAS emails instead of uploading files or connecting Gmail.

`callback_url` is optional:
- **Set it** → we POST each parsed email to your webhook as it arrives.
- **Omit it** → retrieve files via `GET /v4/inbound-email/{id}/files`. The Portfolio Connect widget uses this variant when `enableInboundEmail: true` is set — no backend needed.

Flow: 1. Create inbound email → 2. User forwards CAS → 3. Receive files (via webhook or polling)

```python
import requests, os

# Step 1: Create inbound email (with callback_url → webhook delivery)
response = requests.post(
    "https://api.casparser.in/v4/inbound-email",
    headers={"x-api-key": os.environ["CASPARSER_API_KEY"]},
    json={
        "callback_url": "https://yourapp.com/webhooks/cas-email",
        "allowed_sources": ["cdsl", "nsdl", "cams", "kfintech"],
        "reference": "user_12345",
    }
)
data = response.json()
print(f"Forward CAS to: {data['email']}")
# ie_a1b2c3d4e5f6@import.casparser.in

# Step 2: Handle webhook (in your Flask/Express server)
# POST to your callback_url with:
# {
#   "inbound_email_id": "ie_a1b2c3d4e5f6",
#   "forwarded_by": "investor@gmail.com",  # Investor's email
#   "reference": "user_12345",
#   "files": [{ "message_id": "att_xyz", "filename": "cdsl_20250222_att_xyz.pdf",
#               "cas_type": "cdsl", "sender_email": "ecas@cdslstatement.com",  # CAS authority
#               "url": "https://...", "expires_in": 172800 }],
#   "count": 1
# }

# Retrieve files from any inbound email (works regardless of callback_url)
# GET /v4/inbound-email/{id}/files?since=<cursor>
#   → returns { files: [...], cursor: "<ISO timestamp>" }
# Pass the returned cursor as `since` on the next poll. Use for SDK polling,
# backend polling as an alternative to webhooks, or replay/backfill.
```

### Pattern 6: KFintech Mailback

Trigger a CAS to be emailed to the investor. Good for getting fresh mutual fund statements:

See: [`templates/python-kfintech-generate.py`](templates/python-kfintech-generate.py)

### Pattern 7: Contract Note Parsing

Parse broker contract notes for trade details and charges:

See: [`templates/python-contract-note.py`](templates/python-contract-note.py)

### Pattern 8: Credits & Usage Monitoring

Check remaining quota and track API usage:

See: [`templates/python-credits-check.py`](templates/python-credits-check.py)

### Pattern 9: Portfolio Links (No-Code CAS Collection)

For advisors and wealth managers who want to collect CAS from clients without writing any code:

1. Go to [app.casparser.in/portfolio-links](https://app.casparser.in/portfolio-links)
2. Create a branded collection page — choose a slug, company name, and notification email
3. Share the link (`link.casparser.in/{your-slug}`) with clients — they upload their CAS PDFs
4. Parsed data is emailed to the advisor's notification email

This is not a public API — it's a self-service tool managed entirely via the [web portal](https://app.casparser.in/portfolio-links).

## MCP Server

The official [`cas-parser-node-mcp`](https://www.npmjs.com/package/cas-parser-node-mcp) package exposes all CAS Parser API endpoints as tools for AI agents. It's auto-generated by Stainless from the OpenAPI spec.

Install: `npx -y cas-parser-node-mcp@latest` (requires `CAS_PARSER_API_KEY` env var). Use `sandbox-with-json-responses` for testing.

The MCP server includes **Code Mode** — agents can write TypeScript SDK code that runs in a sandboxed environment — and a **doc search tool** for exploring the API. See `AGENTS.md` for full configuration instructions for Claude Code, Cursor, Windsurf, and VS Code.

### Available MCP Tools

The MCP server is auto-generated from the OpenAPI spec. Each tool maps to an API endpoint:

| Tool (operationId) | Endpoint | Description | Key Parameters |
|--------------------|----------|-------------|----------------|
| `smartParse` | `POST /v4/smart/parse` | Parse any CAS PDF (auto-detect type) | `pdf_file` or `pdf_url`, `password` |
| `nsdlParse` | `POST /v4/nsdl/parse` | Parse NSDL CAS specifically | `pdf_file` or `pdf_url`, `password` |
| `cdslParse` | `POST /v4/cdsl/parse` | Parse CDSL CAS specifically | `pdf_file` or `pdf_url`, `password` |
| `camsKfintechParse` | `POST /v4/cams_kfintech/parse` | Parse CAMS/KFintech CAS specifically | `pdf_file` or `pdf_url`, `password` |
| `parseContractNote` | `POST /v4/contract_note/parse` | Parse broker contract notes | `pdf_file` or `pdf_url`, `password` |
| `cdslFetchRequestOTP` | `POST /v4/cdsl/fetch` | CDSL fetch Step 1 — request OTP | `pan`, `bo_id`, `dob` |
| `cdslFetchVerifyOTP` | `POST /v4/cdsl/fetch/{session_id}/verify` | CDSL fetch Step 2 — verify OTP | `session_id`, `otp`, `num_periods` |
| `generateCas` | `POST /v4/generate` | Trigger CAS mailback (KFintech + CAMS) | `email`, `from_date`, `to_date`, `password` |
| `inboxConnect` | `POST /v4/inbox/connect` | Start Gmail OAuth flow | `redirect_uri`, `state` |
| `inboxStatus` | `GET /v4/inbox/status` | Check inbox connection status | `x-inbox-token` header |
| `inboxCasList` | `GET /v4/inbox/cas` | List CAS files from inbox | `x-inbox-token` header, optional filters |
| `inboxDisconnect` | `POST /v4/inbox/disconnect` | Revoke Gmail access | `x-inbox-token` header |
| `checkCredits` | `POST /v1/credits` | Check remaining API quota | — |
| `getUsageLogs` | `POST /v1/usage` | Get detailed usage logs | optional `start_time`, `end_time`, `limit` |
| `getUsageSummary` | `POST /v1/usage/summary` | Get aggregated usage stats | optional `start_time`, `end_time` |
| `generateAccessToken` | `POST /v1/token` | Generate frontend token | optional `expiry_minutes` |
| `verifyAccessToken` | `POST /v1/token/verify` | Verify token validity | — |

### MCP Usage Notes

- All tools require `x-api-key` — pass the sandbox key `sandbox-with-json-responses` for testing
- Parse tools accept either a file upload or a `pdf_url` — not both
- The CDSL fetch flow requires **two sequential tool calls** (request OTP → verify OTP)
- Email import requires **multiple sequential calls** (connect → OAuth redirect → list → disconnect)
- The MCP server does not expose prompts or resources — only tools

## References

For detailed guides on specific topics:

- [`references/api-overview.md`](references/api-overview.md) — Authentication, base URLs, headers, sandbox
- [`references/cas-types.md`](references/cas-types.md) — CDSL vs NSDL vs CAMS/KFintech explained
- [`references/unified-response.md`](references/unified-response.md) — Full unified response schema
- [`references/portfolio-connect-sdk.md`](references/portfolio-connect-sdk.md) — Portfolio Connect SDK guide
- [`references/email-import-flow.md`](references/email-import-flow.md) — Gmail OAuth flow walkthrough
- [`references/cdsl-fetch-flow.md`](references/cdsl-fetch-flow.md) — CDSL 2-step OTP guide
- [`references/contract-notes.md`](references/contract-notes.md) — Contract note parsing & brokers
- [`references/error-handling.md`](references/error-handling.md) — Error codes and debugging
- [`references/credits-billing.md`](references/credits-billing.md) — Credits system, pricing, and subscription plans
