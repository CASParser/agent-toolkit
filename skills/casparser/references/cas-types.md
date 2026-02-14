# CAS Types — CDSL vs NSDL vs CAMS/KFintech

## Overview

Indian investors receive Consolidated Account Statements (CAS) from three different sources. Each covers different types of financial holdings.

## CDSL (Central Depository Services Limited)

**What it covers:** Demat account holdings
- Equities (stocks)
- Corporate bonds
- Government securities (G-Secs)
- Alternative Investment Funds (AIFs)
- Mutual funds held in demat form
- ETFs

**How investors get it:**
- Monthly email from `eCAS@cdslstatement.com`
- On-demand via CDSL portal (automated via CDSL Fetch API)

**Password format:** Encrypted PAN (format set during registration)

**Unique identifiers:**
- **BO ID** (Beneficiary Owner ID): 16-digit number
- **DP ID** + **Client ID**: Together identify a demat account

**API endpoints:**
- Parse: `POST /v4/cdsl/parse` or `POST /v4/smart/parse`
- Fetch: `POST /v4/cdsl/fetch` → `POST /v4/cdsl/fetch/{session_id}/verify`

## NSDL (National Securities Depository Limited)

**What it covers:** Demat account holdings + NPS
- Equities (stocks)
- Corporate bonds
- Government securities
- Mutual funds held in demat form
- ETFs
- **NPS (National Pension System)** — unique to NSDL

**How investors get it:**
- Monthly email from `NSDL-CAS@nsdl.co.in`

**Password format:** Encrypted PAN (format set during registration)

**Unique identifiers:**
- **DP ID** + **Client ID**: Identify a demat account
- **PRAN** (Permanent Retirement Account Number): For NPS accounts

**API endpoints:**
- Parse: `POST /v4/nsdl/parse` or `POST /v4/smart/parse`

## CAMS/KFintech (Mutual Fund Registrars)

**What it covers:** Mutual fund holdings only
- All mutual fund schemes across all AMCs
- Transaction history (purchases, redemptions, SIPs, switches, dividends)
- Folio-level details with cost basis and gains

**How investors get it:**
- Monthly email from `donotreply@camsonline.com` (CAMS) or `samfS@kfintech.com` (KFintech)
- On-demand via KFintech mailback (automated via KFintech Generate API)

**Password format:** Typically first 4 chars of PAN + DOB in DDMMYYYY format

**Unique identifiers:**
- **Folio Number**: Unique per AMC per investor
- **ISIN**: Identifies specific mutual fund schemes

**API endpoints:**
- Parse: `POST /v4/cams_kfintech/parse` or `POST /v4/smart/parse`
- Generate: `POST /v4/kfintech/generate`

## Which Endpoint to Use?

```
Do you know the CAS type?
├── Yes → Use the specific endpoint (/v4/cdsl/parse, /v4/nsdl/parse, /v4/cams_kfintech/parse)
└── No  → Use /v4/smart/parse (recommended — auto-detects and returns unified format)
```

**Always prefer `/v4/smart/parse`** unless you have a specific reason to use a type-specific endpoint (e.g., you're building a CDSL-only integration).

## Unified Response

Regardless of which endpoint you use, the response format is identical. All CAS types are transformed into a unified schema with:

- `meta.cas_type` — Tells you which type was detected (`"CDSL"`, `"NSDL"`, or `"CAMS_KFINTECH"`)
- `demat_accounts[]` — Populated for CDSL and NSDL
- `mutual_funds[]` — Populated for all types (demat MFs for CDSL/NSDL, folio MFs for CAMS/KFintech)
- `insurance` — Populated for NSDL
- `nps[]` — Populated for NSDL only

See [unified-response.md](unified-response.md) for the full schema.
