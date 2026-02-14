# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is the **CAS Parser Agent Toolkit** — a collection of skills, templates, and documentation for AI coding agents to integrate Indian financial portfolio tracking into applications using the CAS Parser API.

This is NOT an application codebase — it's a reference toolkit containing templates and documentation.

## Key Files to Read First

- `AGENTS.md` — Core rules for CAS Parser integration (authentication, endpoints, patterns)
- `skills/casparser/SKILL.md` — Detailed CAS Parser concepts, Indian financial domain knowledge, and integration patterns

## Structure

- `skills/casparser/templates/` — Code snippets for Python, Node.js, React, and curl
- `skills/casparser/references/` — Detailed guides for complex flows (CDSL fetch, email import, SDK)

## MCP Server

A live MCP server is available at `https://cas-parser.stlmcp.com/mcp` that exposes all API endpoints as tools. See `AGENTS.md` for configuration instructions.

## When Working on CAS Parser Integrations

1. Read `AGENTS.md` for core integration rules and MCP server config
2. Read `skills/casparser/SKILL.md` for domain concepts and available templates
3. **For frontend/web apps:** Start with Portfolio Connect SDK (`@cas-parser/connect`) — see Pattern 1 in SKILL.md
4. **For backend/server-side:** Use `/v4/smart/parse` for CAS parsing (auto-detects type)
5. Use the sandbox API key `sandbox-with-json-responses` for development
6. Never expose API keys to the frontend — use access tokens (`at_` prefix)
