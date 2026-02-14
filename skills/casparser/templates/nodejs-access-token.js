/**
 * CAS Parser — Generate Access Token (Node.js)
 *
 * Generate short-lived access tokens from your backend for frontend/SDK usage.
 * Access tokens (at_ prefix) are drop-in replacements for API keys on all v4 endpoints.
 *
 * IMPORTANT: This runs on your backend. Never expose your API key to the frontend.
 *
 * Requirements:
 *   Node 18+ (built-in fetch) or npm install node-fetch
 */

const API_KEY = process.env.CASPARSER_API_KEY; // Must be a real API key, not an access token
const AUTH_BASE_URL = "https://client-apis.casparser.in";

if (!API_KEY) {
  throw new Error("CASPARSER_API_KEY environment variable is required");
}

/**
 * Generate a short-lived access token for frontend use.
 *
 * @param {number} [expiryMinutes=60] - Token validity in minutes (max 60)
 * @returns {Promise<{accessToken: string, expiresIn: number}>}
 */
async function generateAccessToken(expiryMinutes = 60) {
  const response = await fetch(`${AUTH_BASE_URL}/v1/access-token`, {
    method: "POST",
    headers: {
      "x-api-key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ expiry_minutes: expiryMinutes }),
  });

  const result = await response.json();

  if (!response.ok) {
    throw new Error(`Token generation failed: ${result.detail || result.msg || "Unknown error"}`);
  }

  return {
    accessToken: result.access_token,
    expiresIn: result.expires_in,
  };
}

/**
 * Verify if an access token is still valid.
 *
 * @param {string} token - The access token to verify
 * @returns {Promise<{valid: boolean, maskedApiKey?: string, error?: string}>}
 */
async function verifyToken(token) {
  const response = await fetch(`${AUTH_BASE_URL}/v1/verify-token`, {
    method: "POST",
    headers: {
      "x-api-key": token,
      "Content-Type": "application/json",
    },
  });

  return response.json();
}

// Express.js example endpoint
// app.post("/api/casparser-token", async (req, res) => {
//   try {
//     const { accessToken, expiresIn } = await generateAccessToken(60);
//     res.json({ access_token: accessToken, expires_in: expiresIn });
//   } catch (error) {
//     res.status(500).json({ error: error.message });
//   }
// });

// CLI usage
async function main() {
  const { accessToken, expiresIn } = await generateAccessToken(60);
  console.log(`Access Token: ${accessToken}`);
  console.log(`Expires In: ${expiresIn} seconds`);

  const verification = await verifyToken(accessToken);
  console.log(`Valid: ${verification.valid}`);
}

main().catch(console.error);

module.exports = { generateAccessToken, verifyToken };
