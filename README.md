# CAS Parser Agent Toolkit

A collection of skills, templates, and documentation for AI coding agents to integrate Indian financial portfolio tracking into applications using the [CAS Parser API](https://casparser.in/docs/).

## What is CAS Parser?

CAS Parser is an API platform that extracts structured data from Indian financial portfolio documents:
- **Portfolio Connect SDK** — drop-in UI widget for web apps (file upload, email inbox import, CDSL fetch — all in one modal)
- **REST API** — parse CAS PDFs from CDSL, NSDL, and CAMS/KFintech into structured JSON
- **Contract Notes** — parse broker trade documents from Zerodha, Groww, Upstox, ICICI

## What's in the Toolkit

| Component | What it does |
|-----------|-------------|
| **AGENTS.md** | Integration rules your AI agent follows automatically |
| **SKILL.md** | Domain knowledge (Indian financial concepts, API architecture, integration patterns) |
| **Templates** | 15 copy-paste-ready code snippets (Python, Node.js, React, HTML, curl) |
| **References** | 9 detailed guides + full OpenAPI spec for complex flows |
| **MCP Server** | 17 live API tools your agent can call directly (parse, fetch, import, credits) |

The agent instructions + domain knowledge + MCP tools work together so your AI coding agent can build CAS Parser integrations without you having to explain the API.

## Quick Start

### 1. Install the Skill

Using the [skills CLI](https://skills.sh):

```bash
npx skills add casparser/agent-toolkit
```

This installs templates and documentation into your project's `.skills/` directory.

If you prefer manual setup, copy the `skills/casparser/` directory into your project's `.skills/` or `skills/` folder.

### 2. Add Agent Instructions

Download `AGENTS.md` to your project root:

```bash
curl -O https://raw.githubusercontent.com/casparser/agent-toolkit/main/AGENTS.md
```

For Claude Code, also download `CLAUDE.md`:

```bash
curl -O https://raw.githubusercontent.com/casparser/agent-toolkit/main/CLAUDE.md
```

### 3. Add MCP Server

The official [`cas-parser-node-mcp`](https://www.npmjs.com/package/cas-parser-node-mcp) package exposes all API endpoints as tools, with **Code Mode** (agents write TypeScript SDK code in a sandbox) and a **doc search** tool.

#### Claude Code (CLI — recommended)

```sh
claude mcp add cas_parser_node_mcp -e CAS_PARSER_API_KEY=your-api-key -- npx -y cas-parser-node-mcp@latest
```

#### Claude Code (manual — `~/.claude.json`)

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

#### Cursor (`mcp.json` via Settings > Tools & MCP)

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

#### Windsurf

1. Open Windsurf Settings
2. Navigate to **Cascade > MCP**
3. Click **Add Server**
4. Enter:
   - **Name:** `cas_parser_node_mcp`
   - **Type:** `command`
   - **Command:** `npx -y cas-parser-node-mcp@latest`
   - **Env:** `CAS_PARSER_API_KEY=your-api-key`

#### VS Code

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

> Use `sandbox-with-json-responses` as the API key for testing.

### 4. Start Building

Ask your AI agent:

> "Review the CAS Parser skill and help me integrate portfolio parsing into my app"

Or try specific tasks:

> "Parse a CAS PDF using the CAS Parser API"
>
> "Add Portfolio Connect widget to my React app"
>
> "Set up CDSL fetch with OTP verification"

## Key Features

- **Portfolio Connect SDK** — Drop-in React/Vue/Angular/HTML widget for the full import flow (recommended for frontend)
- **Portfolio Links** — Branded no-code collection pages for advisors (`link.casparser.in/your-company`)
- **CAS Parsing** — Parse CDSL, NSDL, CAMS/KFintech PDFs into structured JSON via REST API
- **Contract Notes** — Parse broker trade documents from Zerodha, Groww, Upstox, ICICI
- **CDSL Fetch** — Download CAS directly from CDSL via OTP authentication
- **Email Import** — Import CAS files from Gmail, Outlook, or Zoho via OAuth
- **Inbound Email** — Create dedicated email addresses for CAS forwarding with webhook delivery
- **Unified Response** — Consistent JSON format across all 9 asset classes

## Project Structure

```
├── AGENTS.md                          # Core integration rules for agents
├── CLAUDE.md                          # Claude Code-specific guidance
├── README.md                          # This file
└── skills/casparser/
    ├── SKILL.md                       # CAS Parser concepts and patterns
    ├── templates/                     # Ready-to-use code snippets
    │   ├── react-portfolio-connect.tsx # React: Portfolio Connect widget ⭐
    │   ├── nextjs-portfolio-connect.tsx# Next.js: full page with widget
    │   ├── html-portfolio-connect.html# Vanilla HTML: embed widget
    │   ├── python-smart-parse.py      # Python: auto-detect & parse CAS
    │   ├── python-cdsl-fetch.py       # Python: CDSL OTP flow
    │   ├── python-email-import.py     # Python: Gmail inbox import
    │   ├── python-contract-note.py    # Python: parse contract notes
    │   ├── python-kfintech-generate.py# Python: KFintech mailback
    │   ├── python-inbound-email.py    # Python: inbound email forwarding
    │   ├── python-credits-check.py    # Python: quota & usage monitoring
    │   ├── nodejs-smart-parse.js      # Node.js: smart parse
    │   ├── nodejs-cdsl-fetch.js       # Node.js: CDSL OTP flow
    │   ├── nodejs-email-import.js     # Node.js: email import
    │   ├── nodejs-access-token.js     # Node.js: generate access tokens
    │   └── curl-examples.sh           # curl for every endpoint
    └── references/                    # Detailed guides
        ├── api-overview.md            # Auth, base URLs, headers, sandbox
        ├── cas-types.md               # CDSL vs NSDL vs CAMS/KFintech
        ├── unified-response.md        # Full response schema
        ├── portfolio-connect-sdk.md   # SDK integration guide
        ├── email-import-flow.md       # Email OAuth walkthrough (Gmail, Outlook, Zoho)
        ├── cdsl-fetch-flow.md         # CDSL 2-step OTP guide
        ├── contract-notes.md          # Contract note parsing
        ├── error-handling.md          # Error codes and debugging
        └── credits-billing.md         # Credits system and pricing
```

## Resources

- [CAS Parser Documentation](https://casparser.in/docs/) — Official docs
- [API Reference](https://casparser.in/docs/api-reference/introduction) — Interactive API reference
- [CAS Parser Web Portal](https://app.casparser.in) — Try it online
- [Portfolio Connect SDK](https://www.npmjs.com/package/@cas-parser/connect) — Frontend UI widget (npm)
- [Node.js / TypeScript SDK](https://www.npmjs.com/package/cas-parser-node) — Official TypeScript API client (npm)
- [Python SDK](https://github.com/CASParser/cas-parser-python) — Official Python API client (GitHub)
- [MCP Server](https://www.npmjs.com/package/cas-parser-node-mcp) — AI agent tools with Code Mode (npm)
- [LLM Context (llms.txt)](https://casparser.in/llms.txt) — Short LLM context file
- [LLM Context (full)](https://casparser.in/llms-full.txt) — Comprehensive LLM context with full API reference
- [Agents.md](https://agents.md/) — Standard for agent behaviors
- [Agent Skills Spec](https://agentskills.io/home) — Specification for agent skills

## About

The CAS Parser Agent Toolkit empowers AI coding agents to build financial portfolio tracking applications using the CAS Parser API — the leading platform for parsing Indian financial documents.
