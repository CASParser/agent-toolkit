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

## Error Handling Best Practices

```python
# Python example
response = requests.post(url, headers=headers, ...)
request_id = response.headers.get("X-Request-ID", "unknown")

if response.status_code == 200:
    data = response.json()
    # Process successful response
elif response.status_code == 400:
    error = response.json()
    print(f"Bad request: {error.get('msg')} (req: {request_id})")
elif response.status_code == 401:
    print("API key is missing or invalid")
elif response.status_code == 403:
    print("Quota exceeded — check credits or upgrade plan")
elif response.status_code == 500:
    print(f"Server error — contact support with req: {request_id}")
```

```javascript
// Node.js example
const response = await fetch(url, { method: "POST", headers, body });
const requestId = response.headers.get("x-request-id") || "unknown";

if (response.ok) {
  const data = await response.json();
  // Process successful response
} else {
  const error = await response.json();
  switch (response.status) {
    case 400: console.error(`Bad request: ${error.msg} (req: ${requestId})`); break;
    case 401: console.error("API key missing or invalid"); break;
    case 403: console.error("Quota exceeded"); break;
    case 500: console.error(`Server error — contact support: ${requestId}`); break;
  }
}
```

## Support

- **Email:** sameer@casparser.in
- **Always include** the `X-Request-ID` from the response header
