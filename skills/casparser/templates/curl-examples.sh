#!/bin/bash
#
# CAS Parser — curl Examples for All Endpoints
#
# Replace YOUR_API_KEY with your actual API key,
# or use the sandbox key for testing: sandbox-with-json-responses
#

API_KEY="${CASPARSER_API_KEY:-sandbox-with-json-responses}"
API_URL="https://api.casparser.in"

# ============================================================
# 1. Smart Parse CAS PDF (auto-detect type) — FILE UPLOAD
# ============================================================
curl -X POST "$API_URL/v4/smart/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/cas.pdf" \
  -F "password=YourPdfPassword"

# ============================================================
# 2. Smart Parse CAS PDF — URL INPUT
# ============================================================
curl -X POST "$API_URL/v4/smart/parse" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pdf_url": "https://example.com/cas.pdf",
    "password": "YourPdfPassword"
  }'

# ============================================================
# 3. Parse specific CAS type (CDSL / NSDL / CAMS_KFintech)
# ============================================================
# CDSL
curl -X POST "$API_URL/v4/cdsl/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/cdsl_cas.pdf" \
  -F "password=YourPdfPassword"

# NSDL
curl -X POST "$API_URL/v4/nsdl/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/nsdl_cas.pdf" \
  -F "password=YourPdfPassword"

# CAMS/KFintech
curl -X POST "$API_URL/v4/cams_kfintech/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/cams_cas.pdf" \
  -F "password=YourPdfPassword"

# ============================================================
# 4. Parse Contract Note
# ============================================================
curl -X POST "$API_URL/v4/contract_note/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/contract_note.pdf" \
  -F "password=ABCDE1234F"

# With explicit broker type
curl -X POST "$API_URL/v4/contract_note/parse" \
  -H "x-api-key: $API_KEY" \
  -F "pdf_file=@/path/to/contract_note.pdf" \
  -F "password=ABCDE1234F" \
  -F "broker_type=zerodha"

# ============================================================
# 5. CDSL Fetch — Step 1: Request OTP
# ============================================================
curl -X POST "$API_URL/v4/cdsl/fetch" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "pan": "ABCDE1234F",
    "bo_id": "1234567890123456",
    "dob": "1990-01-15"
  }'
# Response: {"status": "success", "session_id": "...", "msg": "OTP sent to registered mobile"}

# ============================================================
# 6. CDSL Fetch — Step 2: Verify OTP
# ============================================================
curl -X POST "$API_URL/v4/cdsl/fetch/SESSION_ID_HERE/verify" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "otp": "123456",
    "num_periods": 6
  }'

# ============================================================
# 7. KFintech CAS Generator (email mailback)
# ============================================================
curl -X POST "$API_URL/v4/kfintech/generate" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "investor@example.com",
    "from_date": "2025-01-01",
    "to_date": "2025-12-31",
    "password": "YourPdfPassword",
    "pan_no": "ABCDE1234F"
  }'

# ============================================================
# 8. Email Import — Connect Gmail (get OAuth URL)
# ============================================================
curl -X POST "$API_URL/v4/inbox/connect" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "redirect_uri": "https://yourapp.com/oauth-callback",
    "state": "csrf-token"
  }'

# ============================================================
# 9. Email Import — Check Connection Status
# ============================================================
curl -X POST "$API_URL/v4/inbox/status" \
  -H "x-api-key: $API_KEY" \
  -H "x-inbox-token: INBOX_TOKEN_HERE"

# ============================================================
# 10. Email Import — List CAS Files from Inbox
# ============================================================
curl -X POST "$API_URL/v4/inbox/cas" \
  -H "x-api-key: $API_KEY" \
  -H "x-inbox-token: INBOX_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "cas_types": ["cdsl", "nsdl"],
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'

# ============================================================
# 11. Email Import — Disconnect
# ============================================================
curl -X POST "$API_URL/v4/inbox/disconnect" \
  -H "x-api-key: $API_KEY" \
  -H "x-inbox-token: INBOX_TOKEN_HERE"

# ============================================================
# 12. Check Credits
# ============================================================
curl -X POST "$API_URL/v1/credits" \
  -H "x-api-key: $API_KEY"

# ============================================================
# 13. Get Usage Logs
# ============================================================
curl -X POST "$API_URL/v1/usage" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-01-01T00:00:00Z",
    "limit": 50
  }'

# ============================================================
# 14. Get Usage Summary
# ============================================================
curl -X POST "$API_URL/v1/usage/summary" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2025-01-01T00:00:00Z"
  }'

# ============================================================
# 15. Generate Access Token (for frontend/SDK)
# ============================================================
curl -X POST "$API_URL/v1/token" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "expiry_minutes": 60
  }'

# ============================================================
# 16. Verify Access Token
# ============================================================
curl -X POST "$API_URL/v1/token/verify" \
  -H "x-api-key: at_YOUR_ACCESS_TOKEN_HERE"
