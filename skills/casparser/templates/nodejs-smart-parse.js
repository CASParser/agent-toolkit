/**
 * CAS Parser — Smart Parse CAS PDF (Node.js)
 *
 * Auto-detects CAS type (CDSL, NSDL, or CAMS/KFintech) and returns unified JSON.
 * This is the recommended endpoint for most use cases.
 *
 * Usage:
 *   node nodejs-smart-parse.js /path/to/cas.pdf "your-pdf-password"
 *
 * Requirements:
 *   npm install node-fetch form-data
 *   (or use built-in fetch in Node 18+)
 */

const fs = require("fs");
const path = require("path");
const FormData = require("form-data");

const API_KEY = process.env.CASPARSER_API_KEY || "sandbox-with-json-responses";
const BASE_URL = "https://portfolio-parser.api.casparser.in";

/**
 * Parse a CAS PDF file using smart auto-detection.
 * @param {string} pdfPath - Path to the PDF file
 * @param {string} password - PDF password
 * @returns {Promise<object>} Parsed portfolio data
 */
async function smartParseFile(pdfPath, password) {
  const form = new FormData();
  form.append("pdf_file", fs.createReadStream(pdfPath), {
    filename: path.basename(pdfPath),
    contentType: "application/pdf",
  });
  form.append("password", password);

  const response = await fetch(`${BASE_URL}/v4/smart/parse`, {
    method: "POST",
    headers: {
      "x-api-key": API_KEY,
      ...form.getHeaders(),
    },
    body: form,
  });

  const requestId = response.headers.get("x-request-id") || "unknown";
  const result = await response.json();

  if (!response.ok) {
    throw new Error(`Parse failed (req: ${requestId}): ${result.msg || "Unknown error"}`);
  }

  return result;
}

/**
 * Parse a CAS PDF from a URL using smart auto-detection.
 * @param {string} pdfUrl - URL to the PDF file
 * @param {string} password - PDF password
 * @returns {Promise<object>} Parsed portfolio data
 */
async function smartParseUrl(pdfUrl, password) {
  const response = await fetch(`${BASE_URL}/v4/smart/parse`, {
    method: "POST",
    headers: {
      "x-api-key": API_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ pdf_url: pdfUrl, password }),
  });

  const requestId = response.headers.get("x-request-id") || "unknown";
  const result = await response.json();

  if (!response.ok) {
    throw new Error(`Parse failed (req: ${requestId}): ${result.msg || "Unknown error"}`);
  }

  return result;
}

/**
 * Print a human-readable portfolio summary.
 */
function printSummary(data) {
  const { meta = {}, investor = {}, summary = {} } = data;

  console.log("\n" + "=".repeat(50));
  console.log(`CAS Type: ${meta.cas_type || "Unknown"}`);
  console.log(`Investor: ${investor.name || "N/A"}`);
  console.log(`PAN: ${investor.pan || "N/A"}`);
  console.log(`Period: ${meta.statement_period?.from || "?"} to ${meta.statement_period?.to || "?"}`);
  console.log(`\nTotal Portfolio Value: Rs.${(summary.total_value || 0).toLocaleString()}`);

  const accounts = summary.accounts || {};
  for (const [category, info] of Object.entries(accounts)) {
    if (info?.count > 0) {
      console.log(`  ${category}: ${info.count} accounts, Rs.${(info.total_value || 0).toLocaleString()}`);
    }
  }

  for (const account of data.demat_accounts || []) {
    console.log(`\nDemat: ${account.dp_name || "Unknown"} (${account.demat_type || ""})`);
    for (const equity of account.holdings?.equities || []) {
      console.log(`  ${equity.name || "Unknown"}: ${equity.units || 0} units, Rs.${(equity.value || 0).toLocaleString()}`);
    }
  }

  for (const folio of data.mutual_funds || []) {
    console.log(`\nFolio: ${folio.folio_number || "Unknown"} (${folio.amc || ""})`);
    for (const scheme of folio.schemes || []) {
      console.log(`  ${scheme.name || "Unknown"}: ${scheme.units || 0} units, Rs.${(scheme.value || 0).toLocaleString()}`);
    }
  }

  console.log("=".repeat(50) + "\n");
}

// CLI usage
async function main() {
  const [source, password] = process.argv.slice(2);
  if (!source || !password) {
    console.log("Usage: node nodejs-smart-parse.js <pdf_path_or_url> <password>");
    process.exit(1);
  }

  const data = source.startsWith("http")
    ? await smartParseUrl(source, password)
    : await smartParseFile(source, password);

  printSummary(data);
}

main().catch(console.error);

module.exports = { smartParseFile, smartParseUrl };
