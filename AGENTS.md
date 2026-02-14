# CAS Parser Integration

This repository is the **CAS Parser Agent Toolkit** — a collection of templates, skills, and documentation for integrating financial portfolio tracking into applications using the [CAS Parser API](https://docs.casparser.in/).

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
- For frontend/SDK usage, generate short-lived **access tokens** (`at_` prefix) from your backend via `POST /v1/access-token`. Never expose raw API keys to the client.

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

### KFintech CAS Generator
- `POST /v4/kfintech/generate` triggers an **async email mailback** — the CAS PDF is sent to the investor's email, not returned in the response.
- This is not an instant operation. For instant CAS retrieval, use CDSL Fetch.

### Email Import (Gmail OAuth)
- This is a **multi-step OAuth flow**:
  1. `POST /v4/inbox/connect` → get `oauth_url`, redirect user to it.
  2. User authorizes → redirected back with `inbox_token`.
  3. `POST /v4/inbox/cas` with `x-inbox-token` header → list CAS files from inbox.
  4. Download URLs expire in 24 hours.
- Read-only access — the API cannot send emails.
- User can revoke via `POST /v4/inbox/disconnect`.

### Portfolio Connect SDK (Recommended for Frontend)
- **For web/frontend apps, start here.** The `@cas-parser/connect` npm package provides a drop-in modal widget.
- The widget handles file upload, password entry, Gmail inbox import, and CDSL OTP fetch — all in a single UI.
- Works with React, Next.js, or vanilla HTML/JS (via UMD bundle).
- Install: `npm install @cas-parser/connect`
- Always generate an `accessToken` (`at_` prefix) from your backend via `POST /v1/access-token`. Never expose raw API keys to the frontend.
- See [`references/portfolio-connect-sdk.md`](skills/casparser/references/portfolio-connect-sdk.md) for full integration guide.

### Response Format
- All CAS parse endpoints return a **unified response** regardless of CAS type (CDSL, NSDL, or CAMS/KFintech).
- Top-level keys: `meta`, `investor`, `summary`, `demat_accounts`, `mutual_funds`, `insurance`, `nps`.
- Use `summary.total_value` for portfolio value. Use `summary.accounts` for counts per category.

### Error Handling
- Success: `{"status": "success", ...}`
- Failure: `{"status": "failed", "msg": "..."}` or `{"status": "error", "msg": "..."}`
- Common errors: invalid PDF, wrong password, quota exceeded, invalid API key.
- All responses include an `X-Request-ID` header (`req_*` format) — use it for support requests.

### Credits & Billing
- Each API call consumes credits. Check quota with `POST /credits`.
- Different features cost different credits (e.g., parsing = 1 credit, CDSL fetch = 1.5 credits).
- Monitor usage with `POST /logs` and `POST /logs/summary`.

## Before Implementing

Always check [`skills/casparser/SKILL.md`](skills/casparser/SKILL.md) for existing templates and patterns before writing new CAS Parser integration code. The skill contains ready-to-use examples for:

- **Portfolio Connect SDK** — React, Next.js, vanilla HTML (recommended for frontend)
- Parsing CAS PDFs — Python, Node.js, curl (for backend/server-side)
- CDSL OTP fetch flow
- KFintech mailback generation
- Gmail inbox import
- Credits and usage monitoring

## MCP Server

A live MCP server is available that exposes all CAS Parser API endpoints as tools:

### CAS Parser MCP (`casparser`)

Provides direct API access for AI agents:
- Parsing CAS PDFs and contract notes
- Checking credits and usage
- Managing email import connections
- CDSL fetch operations

**Configuration for Claude Code** (`~/.claude.json`):
```json
{
  "mcpServers": {
    "casparser": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://cas-parser.stlmcp.com/mcp"]
    }
  }
}
```

**Configuration for Cursor:**
1. Open Cursor Settings (Cmd + Shift + J / Ctrl + Shift + J)
2. Navigate to General > MCP
3. Click + Add New MCP Server
4. Enter:
   - Name: `casparser`
   - Type: `command`
   - Command: `npx -y mcp-remote https://cas-parser.stlmcp.com/mcp`

**Configuration for Windsurf:**
1. Open Windsurf Settings
2. Navigate to Cascade > MCP
3. Click Add Server
4. Enter:
   - Name: `casparser`
   - Type: `command`
   - Command: `npx -y mcp-remote https://cas-parser.stlmcp.com/mcp`

**Important:** The MCP server connects to the live CAS Parser API. You still need to provide your API key when making requests through it.
