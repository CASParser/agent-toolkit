# CAS Parser Agent Toolkit

A collection of skills, templates, and documentation for AI coding agents to integrate Indian financial portfolio tracking into applications using the [CAS Parser API](https://docs.casparser.in/).

## What is CAS Parser?

CAS Parser is an API platform that extracts structured data from Indian financial portfolio documents:
- **Portfolio Connect SDK** — drop-in UI widget for web apps (file upload, Gmail import, CDSL fetch — all in one modal)
- **REST API** — parse CAS PDFs from CDSL, NSDL, and CAMS/KFintech into structured JSON
- **Contract Notes** — parse broker trade documents from Zerodha, Groww, Upstox, ICICI

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

The CAS Parser MCP server exposes all API endpoints as tools for AI agents.

#### Claude Code (`~/.claude.json`)

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

#### Cursor

1. Open Cursor Settings (`Cmd + Shift + J` / `Ctrl + Shift + J`)
2. Navigate to **General > MCP**
3. Click **+ Add New MCP Server**
4. Enter:
   - **Name:** `casparser`
   - **Type:** `command`
   - **Command:** `npx -y mcp-remote https://cas-parser.stlmcp.com/mcp`

#### Windsurf

1. Open Windsurf Settings
2. Navigate to **Cascade > MCP**
3. Click **Add Server**
4. Enter:
   - **Name:** `casparser`
   - **Type:** `command`
   - **Command:** `npx -y mcp-remote https://cas-parser.stlmcp.com/mcp`

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

- **Portfolio Connect SDK** — Drop-in React/HTML widget for the full import flow (recommended for frontend)
- **CAS Parsing** — Parse CDSL, NSDL, CAMS/KFintech PDFs into structured JSON via REST API
- **Contract Notes** — Parse broker trade documents from Zerodha, Groww, Upstox, ICICI
- **CDSL Fetch** — Download CAS directly from CDSL via OTP authentication
- **Email Import** — Import CAS files from Gmail via OAuth
- **Unified Response** — Consistent JSON format regardless of CAS source

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
        ├── email-import-flow.md       # Gmail OAuth walkthrough
        ├── cdsl-fetch-flow.md         # CDSL 2-step OTP guide
        ├── contract-notes.md          # Contract note parsing
        ├── error-handling.md          # Error codes and debugging
        └── credits-billing.md         # Credits system and pricing
```

## Resources

- [CAS Parser Documentation](https://docs.casparser.in/) — Official docs
- [API Reference](https://docs.casparser.in/reference) — Interactive API reference
- [CAS Parser Web Portal](https://app.casparser.in) — Try it online
- [Portfolio Connect SDK](https://www.npmjs.com/package/@cas-parser/connect) — npm package
- [Agents.md](https://agents.md/) — Standard for agent behaviors
- [Agent Skills Spec](https://agentskills.io/home) — Specification for agent skills

## About

The CAS Parser Agent Toolkit empowers AI coding agents to build financial portfolio tracking applications using the CAS Parser API — the leading platform for parsing Indian financial documents.
