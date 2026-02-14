/**
 * CAS Parser — Gmail Email Import (Node.js)
 *
 * Full OAuth flow to import CAS files from a user's Gmail inbox.
 *
 * Flow:
 *   1. Get OAuth URL → redirect user
 *   2. User authorizes → you receive inbox_token
 *   3. List CAS files from inbox
 *   4. Download and parse files
 *
 * Requirements:
 *   Node 18+ (built-in fetch) or npm install node-fetch
 */

const API_KEY = process.env.CASPARSER_API_KEY || "sandbox-with-json-responses";
const BASE_URL = "https://portfolio-parser.api.casparser.in";
const HEADERS = { "x-api-key": API_KEY, "Content-Type": "application/json" };

/**
 * Step 1: Get OAuth URL for Gmail connection.
 *
 * @param {string} redirectUri - Your callback URL
 * @param {string} [state] - CSRF protection token
 * @returns {Promise<string>} OAuth URL to redirect the user to
 */
async function connectInbox(redirectUri, state = "") {
  const payload = { redirect_uri: redirectUri };
  if (state) payload.state = state;

  const response = await fetch(`${BASE_URL}/v4/inbox/connect`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(payload),
  });

  const result = await response.json();
  if (result.status !== "success") {
    throw new Error(`Connect failed: ${result.msg || "Unknown error"}`);
  }

  return result.oauth_url;
}

/**
 * Check if an inbox connection is still valid.
 *
 * @param {string} inboxToken - Token from OAuth callback
 * @returns {Promise<object>} Status with connected, provider, email fields
 */
async function checkInboxStatus(inboxToken) {
  const response = await fetch(`${BASE_URL}/v4/inbox/status`, {
    method: "POST",
    headers: { ...HEADERS, "x-inbox-token": inboxToken },
  });
  return response.json();
}

/**
 * Step 3: List CAS files from the user's email inbox.
 *
 * @param {string} inboxToken - Token from OAuth callback
 * @param {object} [options] - Filter options
 * @param {string[]} [options.casTypes] - Filter: ["cdsl", "nsdl", "cams", "kfintech"]
 * @param {string} [options.startDate] - Start date (YYYY-MM-DD)
 * @param {string} [options.endDate] - End date (YYYY-MM-DD)
 * @returns {Promise<Array>} List of CAS file objects with download URLs (expire in 24h)
 */
async function listCasFiles(inboxToken, options = {}) {
  const payload = {};
  if (options.casTypes) payload.cas_types = options.casTypes;
  if (options.startDate) payload.start_date = options.startDate;
  if (options.endDate) payload.end_date = options.endDate;

  const response = await fetch(`${BASE_URL}/v4/inbox/cas`, {
    method: "POST",
    headers: { ...HEADERS, "x-inbox-token": inboxToken },
    body: Object.keys(payload).length > 0 ? JSON.stringify(payload) : undefined,
  });

  const result = await response.json();
  if (result.status !== "success") {
    if (result.requires_reconnect) {
      throw new Error("Email access revoked. User must reconnect.");
    }
    throw new Error(`List failed: ${result.msg || "Unknown error"}`);
  }

  return result.files || [];
}

/**
 * Revoke email access and invalidate the token.
 *
 * @param {string} inboxToken - Token to revoke
 */
async function disconnectInbox(inboxToken) {
  const response = await fetch(`${BASE_URL}/v4/inbox/disconnect`, {
    method: "POST",
    headers: { ...HEADERS, "x-inbox-token": inboxToken },
  });
  const result = await response.json();
  console.log(`Disconnected: ${result.msg || "Done"}`);
}

// Example usage
async function main() {
  // Step 1: Get OAuth URL
  const oauthUrl = await connectInbox("https://yourapp.com/oauth-callback", "csrf-token");
  console.log(`Redirect user to:\n${oauthUrl}\n`);

  // Step 2: After OAuth, you receive inbox_token in the callback query params
  const readline = require("readline");
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const inboxToken = await new Promise((resolve) => rl.question("Paste inbox_token: ", resolve));
  rl.close();

  // Step 3: List CAS files
  const files = await listCasFiles(inboxToken, {
    casTypes: ["cdsl", "nsdl"],
    startDate: "2025-01-01",
  });

  console.log(`\nFound ${files.length} CAS files:`);
  for (const f of files) {
    console.log(`  [${f.cas_type}] ${f.filename} — ${f.message_date}`);
    console.log(`    URL: ${f.url}`);
  }

  // Step 4: Parse files using /v4/smart/parse with pdf_url
  // (See nodejs-smart-parse.js for the parsing step)
}

main().catch(console.error);

module.exports = { connectInbox, checkInboxStatus, listCasFiles, disconnectInbox };
