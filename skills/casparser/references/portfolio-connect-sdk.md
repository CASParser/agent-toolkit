# Portfolio Connect SDK

## Overview

Portfolio Connect is an embeddable UI widget (`@cas-parser/connect` npm package) that handles the full CAS import flow in a single modal:

- **File Upload** — Drag-and-drop or browse for CAS PDFs with password entry
- **Gmail Import** — OAuth-based inbox scanning for CAS attachments
- **CDSL Fetch** — OTP-based direct download from CDSL portal

## Installation

```bash
npm install @cas-parser/connect
```

## Architecture

```
Your Backend                    Your Frontend                  CAS Parser API
┌──────────┐                   ┌──────────────┐               ┌──────────────┐
│ Generate  │──access_token──▶│ Portfolio     │──parse req──▶│ /v4/smart/   │
│ access    │                  │ Connect       │               │ parse        │
│ token     │                  │ Widget        │◀──result────│              │
└──────────┘                   └──────────────┘               └──────────────┘
POST /v1/token                  Modal UI overlay               Returns unified JSON
(uses real API key)             (uses access token)
```

**Key security model:** Your backend holds the real API key. It generates a short-lived access token (`at_` prefix, max 60 min) that gets passed to the frontend widget.

## Quick Start (React)

```tsx
import { PortfolioConnect } from "@cas-parser/connect";

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [token, setToken] = useState("");

  const openWidget = async () => {
    // Generate token from your backend
    const res = await fetch("/api/casparser-token", { method: "POST" });
    const { access_token } = await res.json();
    setToken(access_token);
    setIsOpen(true);
  };

  return (
    <>
      <button onClick={openWidget}>Import Portfolio</button>
      {isOpen && token && (
        <PortfolioConnect
          accessToken={token}
          enableCdslFetch={true}
          enableInbox={true}
          onSuccess={(data) => {
            console.log("Parsed:", data.summary.total_value);
            setIsOpen(false);
          }}
          onError={(err) => console.error(err.message)}
          onExit={() => setIsOpen(false)}
          onEvent={(event) => console.log(event.type)}
        />
      )}
    </>
  );
}
```

## Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `accessToken` | `string` | Yes | Access token (`at_` prefix) from your backend |
| `onSuccess` | `(data) => void` | Yes | Called with parsed portfolio data |
| `onError` | `(error) => void` | No | Called on parsing errors |
| `onExit` | `() => void` | No | Called when user closes the widget |
| `onEvent` | `(event) => void` | No | Called on widget lifecycle events |
| `enableCdslFetch` | `boolean` | No | Enable CDSL OTP fetch option |
| `enableInbox` | `boolean` | No | Enable Gmail inbox import option |
| `enableGenerator` | `boolean` | No | Enable KFintech mailback option |
| `phone` | `string` | No | Pre-fill phone number for CDSL fetch |

## Backend: Access Token Endpoint

### Express.js

```js
app.post("/api/casparser-token", async (req, res) => {
  const response = await fetch("https://api.casparser.in/v1/token", {
    method: "POST",
    headers: {
      "x-api-key": process.env.CASPARSER_API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ expiry_minutes: 60 }),
  });

  const data = await response.json();
  res.json({ access_token: data.access_token, expires_in: data.expires_in });
});
```

### Next.js (App Router)

```ts
// app/api/casparser-token/route.ts
import { NextResponse } from "next/server";

export async function POST() {
  const response = await fetch("https://api.casparser.in/v1/token", {
    method: "POST",
    headers: {
      "x-api-key": process.env.CASPARSER_API_KEY!,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ expiry_minutes: 60 }),
  });

  const data = await response.json();
  return NextResponse.json({
    access_token: data.access_token,
    expires_in: data.expires_in,
  });
}
```

### Python (Flask)

```python
@app.route("/api/casparser-token", methods=["POST"])
def casparser_token():
    response = requests.post(
        "https://api.casparser.in/v1/token",
        headers={"x-api-key": os.environ["CASPARSER_API_KEY"], "Content-Type": "application/json"},
        json={"expiry_minutes": 60},
    )
    data = response.json()
    return jsonify(access_token=data["access_token"], expires_in=data["expires_in"])
```

## Vanilla HTML/JS

For non-React apps, use the UMD bundle:

```html
<script src="https://unpkg.com/@cas-parser/connect@latest/dist/index.umd.js"></script>
<script>
  CASParserConnect.open({
    accessToken: "at_...",
    enableCdslFetch: true,
    enableInbox: true,
    onSuccess: function(data) { console.log(data); },
    onError: function(err) { console.error(err); },
    onExit: function() { console.log("closed"); },
  });
</script>
```

## Widget Events

The `onEvent` callback receives events during the widget lifecycle:

| Event Type | Description |
|------------|-------------|
| `OPENED` | Widget opened |
| `TYPE_CHANGED` | User selected CAS type (CDSL/NSDL/MF) |
| `FILE_SELECTED` | User selected a file |
| `FILE_REMOVED` | User removed a file |
| `UPLOAD_STARTED` | Upload/parse began |
| `UPLOAD_PROGRESS` | Upload progress update |
| `PARSE_COMPLETE` | Parsing finished successfully |
| `ERROR` | An error occurred |
| `CLOSED` | Widget closed |

## Related Templates

- [`templates/react-portfolio-connect.tsx`](../templates/react-portfolio-connect.tsx) — React component
- [`templates/nextjs-portfolio-connect.tsx`](../templates/nextjs-portfolio-connect.tsx) — Next.js full page
- [`templates/html-portfolio-connect.html`](../templates/html-portfolio-connect.html) — Vanilla HTML
- [`templates/nodejs-access-token.js`](../templates/nodejs-access-token.js) — Access token generation
