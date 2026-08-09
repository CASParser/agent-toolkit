# CAS Parser Documentation

Official documentation for CAS Parser — the portfolio import API for Indian fintech.

## Quick Facts

- **Platform**: [Mintlify](https://mintlify.com)
- **API Spec**: OpenAPI 3.1 (auto-generates endpoint docs)
- **Audience**: Developers, AI agents, fintech platforms

## Structure

```
docs/
├── index.mdx                    # Homepage
├── quickstart.mdx               # Overview
├── quickstart/                  # Language-specific guides
│   ├── python.mdx
│   ├── nodejs.mdx
│   └── curl.mdx
├── learn/                       # Deep-dive topics
│   ├── authentication.mdx       # API keys & access tokens
│   ├── response-schema.mdx      # Complete field reference
│   └── error-handling.mdx       # Retry logic & best practices
├── resources/                   # Reference
│   ├── sandbox.mdx
│   ├── security.mdx
│   └── support.mdx
├── api-reference/               # API docs (auto-generated)
│   ├── introduction.mdx
│   └── openapi.yaml             # Auto-generates all endpoints
├── sdk/                         # Portfolio Connect SDK (separate tab)
│   ├── portfolio-connect.mdx
│   └── configuration.mdx
├── guides/                      # Product guides (Knowledge Base tab)
│   ├── parsing.mdx              # CAS PDF parsing
│   ├── contract-notes.mdx       # Broker contract notes
│   ├── cas-generator.mdx        # KFintech email request
│   ├── gmail-inbox.mdx          # OAuth inbox import
│   ├── cdsl-fetch.mdx           # OTP-based fetch
│   └── mcp-server.mdx           # AI agent MCP integration
├── knowledge-base/              # FAQ & use cases (Knowledge Base tab)
│   ├── faq.mdx
│   └── use-cases.mdx
├── release-notes.mdx            # Changelog (separate tab)
├── docs.json                    # Mintlify config
└── logo/, images/               # Assets
```

## Navigation Structure

**5 Tabs:**
1. **Documentation** — Getting Started, Quickstart, Learn, Resources
2. **API Reference** — Auto-generated from OpenAPI (all endpoints)
3. **Portfolio Connect SDK** — Frontend widget documentation
4. **Knowledge Base** — Product guides, FAQ, use cases
5. **Release Notes** — Changelog and updates

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /v4/smart/parse` | Auto-detect and parse any CAS |
| `POST /v4/generate` | Request CAS via email (KFintech + CAMS) |
| `POST /v4/cdsl/fetch` | CDSL OTP flow (Step 1) |
| `POST /v4/inbox/connect` | Email OAuth (Gmail, Outlook, Zoho) |
| `POST /v1/token` | Generate access token |

## Local Development

```bash
cd docs
npx mintlify dev
```

## Style Guide

- **Voice**: Active, second person ("you")
- **Sentences**: One idea per sentence
- **Headings**: Sentence case
- **Code**: Backticks for paths, commands, variables
- **Diagrams**: Mermaid flowcharts and sequence diagrams
- **Examples**: Always include Python, Node.js, cURL

## OpenAPI Integration

API reference pages are **auto-generated** from `/api-reference/openapi.yaml`. To update endpoint docs:

1. Edit the OpenAPI spec at `/api-reference/openapi.yaml`
2. Mintlify rebuilds endpoint pages automatically
3. No separate MDX files needed per endpoint

## Writing for AI Agents

This documentation is optimized for AI agent discovery:

- Clear, scannable structure
- Code examples in every guide
- Explicit error handling patterns
- ASCII diagrams for visual flows
- Consistent terminology across pages
