# Error Handling

## Response Patterns

### Success
```json
{
  "status": "success",
  ...
}
```
HTTP Status: `200`

### Parse Failure
```json
{
  "status": "failed",
  "msg": "Invalid PDF file or password."
}
```
HTTP Status: `400`

### Authentication Error
```json
{
  "status": "error",
  "msg": "Authentication failed: API key is missing. Please provide a valid API key in the x-api-key header."
}
```
HTTP Status: `401`

### Quota Exceeded
```json
{
  "status": "error",
  "msg": "Authentication failed: API quota exceeded or invalid API key. Please check your API key or quota limits."
}
```
HTTP Status: `403`

### Server Error
```json
{
  "status": "failed",
  "msg": "Internal server error"
}
```
HTTP Status: `500`

## Common Errors and Solutions

### Authentication

| Error | Cause | Fix |
|-------|-------|-----|
| `API key is missing` | No `x-api-key` header | Add `x-api-key` header to request |
| `API quota exceeded or invalid API key` | Invalid key or out of credits | Verify API key, check credits via `POST /credits` |
| `Access tokens cannot be used for credits API` | Using `at_` token for admin endpoints | Use your real API key for `/credits`, `/logs`, `/logs/summary` |
| `Cannot create access token from access token` | Trying to nest token generation | Use your real API key to generate access tokens |

### PDF Parsing

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid PDF file or password` | Wrong password or corrupted file | Verify password format (see CAS password conventions) |
| `Unable to detect CAS type` | PDF is not a recognized CAS format | Use type-specific endpoint instead of smart parse |
| `File too large` | PDF exceeds size limit | Ensure file is under 10MB |
| `No PDF file provided` | Missing `pdf_file` and `pdf_url` | Provide either `pdf_file` or `pdf_url` |

### CDSL Fetch

| Error | Cause | Fix |
|-------|-------|-----|
| `Invalid PAN or BO ID` | Wrong CDSL credentials | Verify PAN (10 chars) and BO ID (16 digits) |
| `CAPTCHA failed` | reCAPTCHA solving failed | Retry the request |
| `Session expired` | Too long between Steps 1 and 2 | Start a new session from Step 1 |
| `Invalid OTP` | Wrong OTP entered | Ask user to re-enter, or restart session |
| `Session not found` | Invalid session_id | Check session_id from Step 1 |

### Email Import

| Error | Cause | Fix |
|-------|-------|-----|
| `Email access revoked. Please reconnect.` | User revoked Gmail access | Redirect user to OAuth flow again |
| `Invalid redirect_uri` | Malformed callback URL | Use full URL with http/https scheme |
| `Token expired` | inbox_token is no longer valid | Re-initiate OAuth flow |

## Request ID for Debugging

Every response includes an `X-Request-ID` header:
```
X-Request-ID: req_2xYz7KpL8mN3Ab
```

When contacting support, always include:
1. The `X-Request-ID` value
2. The endpoint called
3. The HTTP status code received
4. The error message from the response body

## PDF Validation Errors

The API has built-in fraud prevention. These are **not retryable**:

| Error | Meaning |
|-------|----------|
| `Invalid PDF file or password` | PDF is corrupted, tampered, or wrong password |
| `Unable to detect CAS type` | Not a recognized CAS format (could be scanned or non-CAS PDF) |
| `File too large` | Exceeds 10MB limit |

**Important:** The API only works with **original, digitally-generated PDFs**. It does not support:
- Scanned/photographed PDFs (no OCR)
- Tampered or modified PDFs (fraud prevention detects alterations)
- Non-CAS documents

## Retry Logic

### What to Retry

| Status | Retry? | Strategy |
|--------|--------|----------|
| `200` | No | Success |
| `400` | **No** | Bad input — fix the request (wrong password, invalid PDF, missing params) |
| `401` | **No** | Invalid API key — fix authentication |
| `403` | **No** | Quota exceeded — check credits or upgrade plan |
| `500` | **Yes** | Server error — retry with exponential backoff |
| `502/503` | **Yes** | Temporary — retry with exponential backoff |
| Timeout | **Yes** | Retry, but increase timeout (parse operations can take 10-30s) |

### Python: Retry with Exponential Backoff

```python
import time
import requests

def call_with_retry(method, url, max_retries=3, **kwargs):
    """Call API with retry for server errors only."""
    kwargs.setdefault("timeout", 60)
    
    for attempt in range(max_retries + 1):
        try:
            response = requests.request(method, url, **kwargs)
            request_id = response.headers.get("X-Request-ID", "unknown")
            
            if response.status_code == 200:
                return response.json()
            
            # Don't retry client errors
            if response.status_code in (400, 401, 403):
                error = response.json()
                raise Exception(f"[{response.status_code}] {error.get('msg')} (req: {request_id})")
            
            # Retry server errors
            if response.status_code >= 500 and attempt < max_retries:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(f"Server error (req: {request_id}), retrying in {wait}s...")
                time.sleep(wait)
                continue
            
            # Final attempt failed
            raise Exception(f"[{response.status_code}] Server error after {max_retries} retries (req: {request_id})")
            
        except requests.exceptions.Timeout:
            if attempt < max_retries:
                wait = 2 ** attempt
                print(f"Timeout, retrying in {wait}s...")
                time.sleep(wait)
                continue
            raise Exception(f"Request timed out after {max_retries} retries")
```

### Node.js: Retry with Exponential Backoff

```javascript
async function callWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 60000);
      
      const response = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeout);
      
      const requestId = response.headers.get("x-request-id") || "unknown";
      
      if (response.ok) return await response.json();
      
      const error = await response.json();
      
      // Don't retry client errors
      if ([400, 401, 403].includes(response.status)) {
        throw new Error(`[${response.status}] ${error.msg} (req: ${requestId})`);
      }
      
      // Retry server errors
      if (response.status >= 500 && attempt < maxRetries) {
        const wait = Math.pow(2, attempt) * 1000;
        console.log(`Server error (req: ${requestId}), retrying in ${wait}ms...`);
        await new Promise(r => setTimeout(r, wait));
        continue;
      }
      
      throw new Error(`[${response.status}] Server error after ${maxRetries} retries (req: ${requestId})`);
    } catch (err) {
      if (err.name === "AbortError" && attempt < maxRetries) {
        const wait = Math.pow(2, attempt) * 1000;
        console.log(`Timeout, retrying in ${wait}ms...`);
        await new Promise(r => setTimeout(r, wait));
        continue;
      }
      throw err;
    }
  }
}
```

## Timeout Guidance

| Operation | Recommended Timeout | Why |
|-----------|--------------------|----- |
| CAS Parse (file upload) | **60s** | Large PDFs with many folios take time |
| CAS Parse (URL) | **60s** | API downloads + parses the PDF |
| Contract Note Parse | **60s** | Similar to CAS parse |
| CDSL Fetch Step 1 | **30s** | Includes ~15-20s for captcha solving |
| CDSL Fetch Step 2 | **60s** | Downloads multiple CAS files from CDSL |
| KFintech Generate | **30s** | Submits request (PDF arrives via email) |
| Email Import (list) | **30s** | Searches Gmail for CAS emails |
| Credits / Logs | **10s** | Simple lookups |
| Access Token | **10s** | Simple generation |

## Error Handling Best Practices

### Simple (No Retry)

```python
# Python — minimal error handling
response = requests.post(url, headers=headers, ..., timeout=60)
request_id = response.headers.get("X-Request-ID", "unknown")

if response.status_code == 200:
    data = response.json()
elif response.status_code == 400:
    error = response.json()
    print(f"Bad request: {error.get('msg')} (req: {request_id})")
elif response.status_code == 401:
    print("API key is missing or invalid")
elif response.status_code == 403:
    print("Quota exceeded — check credits or upgrade plan")
elif response.status_code >= 500:
    print(f"Server error — retry or contact support with req: {request_id}")
```

```javascript
// Node.js — minimal error handling
const response = await fetch(url, { method: "POST", headers, body });
const requestId = response.headers.get("x-request-id") || "unknown";

if (response.ok) {
  const data = await response.json();
} else {
  const error = await response.json();
  switch (response.status) {
    case 400: console.error(`Bad request: ${error.msg} (req: ${requestId})`); break;
    case 401: console.error("API key missing or invalid"); break;
    case 403: console.error("Quota exceeded"); break;
    default:  console.error(`Server error — retry or contact support: ${requestId}`); break;
  }
}
```

## Support

- **Email:** sameer@casparser.in
- **Always include** the `X-Request-ID` from the response header
