/**
 * CAS Parser — CDSL Fetch via OTP (Node.js)
 *
 * Two-step flow to download CAS directly from CDSL:
 *   Step 1: Request OTP (sent to user's registered mobile)
 *   Step 2: Verify OTP and get download URLs
 *
 * Requirements:
 *   Node 18+ (built-in fetch) or npm install node-fetch
 */

const API_KEY = process.env.CASPARSER_API_KEY || "sandbox-with-json-responses";
const BASE_URL = "https://api.casparser.in";
const HEADERS = { "x-api-key": API_KEY, "Content-Type": "application/json" };

/**
 * Step 1: Request OTP for CDSL CAS fetch.
 *
 * @param {string} pan - PAN number (e.g., "ABCDE1234F")
 * @param {string} boId - CDSL BO ID, 16 digits
 * @param {string} dob - Date of birth, YYYY-MM-DD
 * @returns {Promise<string>} session_id for Step 2
 *
 * Note: Takes ~15-20 seconds (captcha solving).
 */
async function requestOtp(pan, boId, dob) {
  const response = await fetch(`${BASE_URL}/v4/cdsl/fetch`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ pan, bo_id: boId, dob }),
  });

  const result = await response.json();
  if (result.status !== "success") {
    throw new Error(`OTP request failed: ${result.msg || "Unknown error"}`);
  }

  console.log(`OTP sent to registered mobile. Session: ${result.session_id}`);
  return result.session_id;
}

/**
 * Step 2: Verify OTP and get CAS file download URLs.
 *
 * @param {string} sessionId - From Step 1
 * @param {string} otp - OTP received on mobile
 * @param {number} numPeriods - Monthly statements to fetch (default 6)
 * @returns {Promise<Array>} List of {filename, url} objects
 */
async function verifyOtp(sessionId, otp, numPeriods = 6) {
  const response = await fetch(`${BASE_URL}/v4/cdsl/fetch/${sessionId}/verify`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ otp, num_periods: numPeriods }),
  });

  const result = await response.json();
  if (result.status !== "success") {
    throw new Error(`OTP verification failed: ${result.msg || "Unknown error"}`);
  }

  const files = result.files || [];
  console.log(`Fetched ${files.length} CAS files`);
  return files;
}

// Example usage
async function main() {
  // Step 1: Request OTP
  const sessionId = await requestOtp("ABCDE1234F", "1234567890123456", "1990-01-15");

  // Step 2: Get OTP from user (in a real app, show a UI input)
  const readline = require("readline");
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const otp = await new Promise((resolve) => rl.question("Enter OTP: ", resolve));
  rl.close();

  // Step 3: Verify and get files
  const files = await verifyOtp(sessionId, otp, 6);
  for (const f of files) {
    console.log(`  ${f.filename}: ${f.url}`);
  }
}

main().catch(console.error);

module.exports = { requestOtp, verifyOtp };
