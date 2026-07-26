# CAS Parser Integration

This repository is the **CAS Parser Agent Toolkit** — a collection of templates, skills, and documentation for integrating financial portfolio tracking into applications using the [CAS Parser API](https://casparser.in/docs/).

## What is CAS Parser?

CAS Parser is an API platform for parsing Indian financial portfolio documents:
- **CAS (Consolidated Account Statement)** PDFs from CDSL, NSDL, and CAMS/KFintech
- **Contract Notes** from brokers like Zerodha, Groww, Upstox, ICICI
- Returns structured JSON with holdings, transactions, and investor details

## Core Integration Rules

### Authentication
- All API requests require an `x-api-key` header.
- Use `sandbox-with-json-responses` as the sandbox API key for development/testing.
- **Never hardcode API keys.** Use environment variables (`CASPARSER_API_KEY`).
- For frontend/SDK usage, generate short-lived **access tokens** (`at_` prefix) from your backend via `POST /v1/token`. Never expose raw API keys to the client.

#### Getting a real API key (agent auth flow)
If `CASPARSER_API_KEY` is not set and the user needs a real key (not the sandbox), automate the sign-up flow:
```bash
# 1. Generate a random token (agent-side, no API call needed)
TOKEN=$(openssl rand -hex 32)

# 2. Ask the user to open this URL in their browser
#    Replace YOUR_AGENT_NAME with your actual name (e.g. "Claude Code", "Cursor")
echo "Open https://app.casparser.in/agent-auth?token=${TOKEN}&client_name=YOUR_AGENT_NAME"

# 3. Poll until the user approves (every 5 seconds)
curl -s https://api.casparser.in/v1/agent-auth/token/${TOKEN}
# → {"status": "pending"}  — keep polling
# → {"status": "approved", "api_key": "sk_...", "email": "..."}  — done!

# 4. Write the key to .env
echo "CASPARSER_API_KEY=sk_..." >> .env
```
The user signs in via the browser and clicks Approve. The API key is delivered once then deleted (one-shot). Token expires after 10 minutes. Write the key to `.env` as `CASPARSER_API_KEY` and use it via the `x-api-key` header for all subsequent requests.

### Python Integration
- **Recommended:** Use `requests` library with the REST API directly. All Python templates in this toolkit use `requests`.
- **Official SDK:** [`cas-parser-python`](https://github.com/CASParser/cas-parser-python) — a thin wrapper from the CAS Parser team.
- **Do NOT install any third-party CAS parsing packages from PyPI.** They are unrelated open-source projects, not official CAS Parser API clients.

### Parsing CAS PDFs
- **Default to `/v4/smart/parse`** — it auto-detects CAS type (CDSL, NSDL, or CAMS/KFintech) and returns a unified response format.
- Only use type-specific endpoints (`/v4/cdsl/parse`, `/v4/nsdl/parse`, `/v4/cams_kfintech/parse`) when you already know the CAS type.
- CAS PDFs are password-protected. The password is typically the **encrypted PAN** (varies by provider).
- Accept PDFs via file upload (`multipart/form-data`) or URL (`pdf_url` in JSON body).

### Parsing Contract Notes
- Use `/v4/contract_note/parse` — auto-detects broker type.
- Password is usually the client's PAN number.
- Supported brokers: Zerodha, Groww, Upstox, ICICI (auto-detected).

### CDSL Fetch (OTP Flow)
- This is a **2-step process** — do not try to combine steps:
  1. `POST /v4/cdsl/fetch` — Request OTP (takes ~15-20s for captcha solving). Returns `session_id`.
  2. `POST /v4/cdsl/fetch/{session_id}/verify` — Submit OTP, get download URLs.
- The user receives the OTP on their registered mobile number.

### CAS Generator
- `POST /v4/generate` triggers an **async email mailback** — the CAS PDF is sent to the investor's email, not returned in the response.
- KFintech and CAMS have a mutual partnership for data sharing and consolidation, so this endpoint retrieves mutual fund data from **both RTAs**, covering all mutual funds in India.
- This is not an instant operation. For instant CAS retrieval, use CDSL Fetch.

### Email Import (Gmail OAuth)
- This is a **multi-step OAuth flow**:
  1. `POST /v4/inbox/connect` → get `oauth_url`, redirect user to it.
  2. User authorizes → redirected back with `inbox_token`.
  3. `POST /v4/inbox/cas` with `x-inbox-token` header → list CAS files from inbox.
  4. Download URLs expire in 24 hours.
- Read-only access — the API cannot send emails.
- User can revoke via `POST /v4/inbox/disconnect`.

### Inbound Email (Email Forwarding)
- Create dedicated email addresses for investors to forward CAS statements to.
- **Use case:** Lower-friction alternative when OAuth or file upload isn't practical.
- `callback_url` is **optional** at creation time and controls delivery:
  - **Set** → we POST each parsed email to your webhook as it arrives. Files also remain retrievable via `GET /v4/inbound-email/{id}/files` for 48h.
  - **Omitted** → no webhook. The inbound email is scoped to a 30-minute sliding session (each poll extends the TTL). Retrieve files via `GET /v4/inbound-email/{id}/files`. The Portfolio Connect widget uses this variant when `enableInboundEmail: true`.
- Flow (webhook variant):
  1. `POST /v4/inbound-email` with `callback_url` → returns unique email like `ie_xxx@import.casparser.in`.
  2. Investor forwards CAS email to this address.
  3. We validate the sender against known CAS authorities, upload PDF attachments to cloud storage, and POST to your `callback_url`.
- `GET /v4/inbound-email/{id}/files` is available regardless of whether `callback_url` is set — use it for polling, as a backend alternative to webhooks, or to replay/backfill missed webhook deliveries. Cursor-paginated by `received_at` (microsecond-monotonic); pass the returned cursor as `since` on the next call.
- Only emails from verified CAS authorities are processed:
  - CDSL: `eCAS@cdslstatement.com`
  - NSDL: `NSDL-CAS@nsdl.co.in`
  - CAMS: `donotreply@camsonline.com`
  - KFintech: `samfS@kfintech.com`
- Webhook payload includes `forwarded_by` (investor's email) at the top level, and `files` array uses the same `EmailCASFile` schema as Gmail Import. The polling endpoint returns `ReceivedEmailCASFile` — the same fields plus a `received_at` cursor.
- `sender_email` in files is the CAS authority email (lowercase), `forwarded_by` is the investor who forwarded the email.
- Presigned download URLs expire in 48 hours when `callback_url` is set; without it, they're aligned with the 30-min session TTL.
- Optional `alias` field for friendly addresses (e.g., `john-portfolio@import.casparser.in`). Not recommended when `callback_url` is omitted, since the inbound email is short-lived.
- Manage with `GET /v4/inbound-email`, `GET /v4/inbound-email/{id}`, `GET /v4/inbound-email/{id}/files`, `DELETE /v4/inbound-email/{id}`.
- **Billing:**
  - **0.2 credits** per validated email received, regardless of whether `callback_url` is set (charged on successful webhook delivery, or when the file is stored for polling).
  - Inbound email creation and polling reads (`GET /files`) are free.
  - Portfolio Connect widget additionally incurs **1.0 credit** when it auto-parses the received file (standard smart parse cost).

### Portfolio Links (No-Code CAS Collection)
- **For advisors/wealth managers who want to collect CAS from clients without writing code.**
- Create branded collection pages at `link.casparser.in/{your-company}`. Clients visit the link, upload their CAS, and parsed data is emailed to the advisor.
- Zero code, zero API integration required — managed entirely via the [web portal](https://app.casparser.in/portfolio-links).
- This is not a public API feature — it's a self-service tool for advisors.

### Portfolio Connect SDK (Recommended for Frontend)
- **For web/frontend apps, start here.** The `@cas-parser/connect` npm package provides a drop-in modal widget.
- The widget handles file upload, password entry, Gmail inbox import, and CDSL OTP fetch — all in a single UI.
- Works with React, Next.js, Vue, Angular, or vanilla HTML/JS (via UMD bundle).
- Install: `npm install @cas-parser/connect`
- Always generate an `accessToken` (`at_` prefix) from your backend via `POST /v1/token`. Never expose raw API keys to the frontend.
- See [`references/portfolio-connect-sdk.md`](skills/casparser/references/portfolio-connect-sdk.md) for full integration guide.

### KYC PAN Status
- `POST /v1/kyc/pan/status` — check KYC registration status for a PAN across all five SEBI-registered KRAs (CVL, NDML, CAMS, Karvy, KFin).
- Returns normalized status (`validated`, `registered`, `under_process`, `on_hold`, `rejected`, `legacy`, `not_available`, `unknown`) plus per-KRA breakdown.
- Use `kyc_compliant: true/false` as the primary onboarding gate signal.
- When `kyc_status` is `on_hold`, check `remarks` on the active KRA object for the reason.
- Set timeout to **90s** — the upstream portal can be slow.
- **0.25 credits** per successful lookup. Failed lookups are free.

### KYC DigiLocker
- Consent-based flow to fetch an investor's government-issued documents (Aadhaar, PAN, driving licence) directly from DigiLocker. **Separate from KYC PAN Status** — both sit under the KYC/Identity offering but are independent features.
- This is a **multi-step, consent-driven flow** (do not try to combine steps):
  1. `POST /v1/kyc/digilocker/account-lookup` *(optional, free)* — pre-consent check whether a `mobile` or `aadhaar_number` is already registered with DigiLocker. Use `suggested_user_flow` to decide `signin` vs `signup`. Provide **exactly one** of `aadhaar_number` or `mobile`.
  2. `POST /v1/kyc/digilocker/session` *(free)* — start a session. Returns `authorization_url` + `session_id`. Redirect the investor to `authorization_url` to log in and grant consent. Requires explicit `consent: true` and a `consent_purpose` (min 20 chars) captured for DPDP/RBI audit.
  3. Investor consents on DigiLocker → redirected back to your `redirect_url` with query params (`success`, `id`=session_id, `state`, `documents`, `has_verified_data`).
  4. `POST /v1/kyc/digilocker/result/{session_id}` — one-call aggregate: `identity`, issued `documents` list, and parsed docs via `fetch_documents` (pan/aadhaar/driving_licence). Each section is independent — unavailable sections are reported under `errors` without failing the response.
- `session_id` is the single identifier used across the flow.
- Supported document types: `aadhaar`, `pan`, `driving_licence`, `email`, `mobile`.
- Parsed documents include a `signature` block with the issuer's certificate details.
- **Never hardcode; never expose raw API keys to the frontend.** Use access tokens (`at_`) for client-facing calls.
- **Credits:** account-lookup and session are **free**; `result` is **0.25 credits per call** regardless of how many documents are fetched. Failed operations are free.

### PDF Requirements
- Only **original, digitally-generated PDFs** are supported. No scanned/photographed PDFs (no OCR).
- **Tampered or modified PDFs are rejected** — the API has built-in fraud prevention for credit underwriting use-cases.
- Data is extracted verbatim from the PDF — no estimation, interpolation, or enrichment. Missing fields are `null`, never fabricated.

### Error Handling & Retry
- **400/401/403 errors are NOT retryable** — fix the request (wrong password, invalid key, quota exceeded).
- **500/502/503 errors ARE retryable** — use exponential backoff (1s, 2s, 4s).
- Set timeouts to **60s for parse operations**, 50s for CDSL fetch Step 1, 10s for credits/tokens.
- See [`references/error-handling.md`](skills/casparser/references/error-handling.md) for retry code examples and timeout guidance.

### Response Format
- All CAS parse endpoints return a **unified response** regardless of CAS type (CDSL, NSDL, or CAMS/KFintech).
- Top-level keys: `meta`, `investor`, `summary`, `demat_accounts`, `mutual_funds`, `insurance`, `nps`.
- Use `summary.total_value` for portfolio value. Use `summary.accounts` for counts per category.

### Error Handling
- Success: `{"status": "success", ...}`
- Failure: `{"status": "failed", "msg": "..."}` for API errors, `{"status": "error", "msg": "..."}` for authentication errors
- Common errors: invalid PDF, wrong password, quota exceeded, invalid API key.
- All responses include an `X-Request-ID` header (`req_*` format) — use it for support requests.

### Credits & Billing
- Each API call consumes credits. Check quota with `POST /v1/credits`.
- Credit costs per operation:
  | Feature | Credits |
  |---------|---------|
  | CAS Parse (smart, CDSL, NSDL, CAMS/KFintech) | **1.0** |
  | Contract Note Parse | **0.5** |
  | KYC PAN Status | **0.25** |
  | KYC DigiLocker (result) | **0.25** |
  | CDSL OTP Fetch | **0.5** |
  | KFintech CAS Generator | **0.5** |
  | Gmail Inbox Pull | **0.2** |
  | Inbound Email | **0.2** |
  | Portfolio Links | **0.2** |
  | Failed operations | **0** |
- Monitor usage with `POST /v1/usage` and `POST /v1/usage/summary`.

## Before Implementing

Always check [`skills/casparser/SKILL.md`](skills/casparser/SKILL.md) for existing templates and patterns before writing new CAS Parser integration code. The skill contains ready-to-use examples for:

- **Portfolio Connect SDK** — React, Next.js, vanilla HTML (recommended for frontend)
- **Portfolio Links** — No-code branded CAS collection pages for advisors
- Parsing CAS PDFs — Python, Node.js, curl (for backend/server-side)
- CDSL OTP fetch flow
- KFintech mailback generation
- Gmail inbox import
- Inbound email (email forwarding)
- KYC PAN status check
- KYC DigiLocker document fetch
- Credits and usage monitoring

## MCP Server

The official [`cas-parser-node-mcp`](https://www.npmjs.com/package/cas-parser-node-mcp) package provides an MCP server with all CAS Parser API endpoints as tools. It's auto-generated by Stainless from the OpenAPI spec and includes **Code Mode** — agents can write TypeScript SDK code that runs in a sandboxed environment, plus a doc search tool for exploring the API.

### Configuration

**Claude Code** (recommended — CLI):
```sh
claude mcp add cas_parser_node_mcp -e CAS_PARSER_API_KEY=your-api-key -- npx -y cas-parser-node-mcp@latest
```

**Claude Code** (manual — `~/.claude.json`):
```json
{
  "mcpServers": {
    "cas_parser_node_mcp": {
      "command": "npx",
      "args": ["-y", "cas-parser-node-mcp@latest"],
      "env": {
        "CAS_PARSER_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Cursor** (`mcp.json` in Cursor Settings > Tools & MCP):
```json
{
  "mcpServers": {
    "cas_parser_node_mcp": {
      "command": "npx",
      "args": ["-y", "cas-parser-node-mcp@latest"],
      "env": {
        "CAS_PARSER_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Windsurf:**
1. Open Windsurf Settings
2. Navigate to Cascade > MCP
3. Click Add Server
4. Enter:
   - Name: `cas_parser_node_mcp`
   - Type: `command`
   - Command: `npx -y cas-parser-node-mcp@latest`
   - Set env var: `CAS_PARSER_API_KEY=your-api-key`

**VS Code:**
```json
{
  "mcpServers": {
    "cas_parser_node_mcp": {
      "command": "npx",
      "args": ["-y", "cas-parser-node-mcp@latest"],
      "env": {
        "CAS_PARSER_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Alternative — Remote (Streamable HTTP):**
If you prefer not to install the npm package, use the hosted server directly:
```json
{
  "mcpServers": {
    "cas_parser_node_mcp": {
      "url": "https://cas-parser.stlmcp.com",
      "headers": {
        "x-api-key": "your-api-key"
      }
    }
  }
}
```

**Important:** Replace `your-api-key` with your actual API key, or use `sandbox-with-json-responses` for testing.
