/**
 * CAS Parser — Portfolio Connect Widget (React)
 *
 * Drop-in React component that handles the full user flow:
 * - File upload with password entry
 * - Gmail inbox import
 * - CDSL fetch via OTP
 *
 * Install:
 *   npm install @cas-parser/connect
 *
 * IMPORTANT: Generate an access token from your backend.
 * Never expose your API key to the frontend.
 */

import React, { useState, useCallback } from "react";
import { PortfolioConnect } from "@cas-parser/connect";

interface PortfolioData {
  meta: { cas_type: string };
  investor: { name: string; pan: string };
  summary: { total_value: number };
  demat_accounts: any[];
  mutual_funds: any[];
}

export default function CASParserWidget() {
  const [accessToken, setAccessToken] = useState<string>("");
  const [result, setResult] = useState<PortfolioData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  // Fetch access token from your backend before opening the widget
  const handleOpen = useCallback(async () => {
    try {
      const res = await fetch("/api/casparser-token", { method: "POST" });
      const data = await res.json();
      setAccessToken(data.access_token);
      setIsOpen(true);
    } catch (err) {
      setError("Failed to get access token");
    }
  }, []);

  const handleSuccess = useCallback((data: PortfolioData) => {
    setResult(data);
    setIsOpen(false);
    console.log("Portfolio parsed:", data.summary.total_value);
  }, []);

  const handleError = useCallback((err: { message: string }) => {
    setError(err.message);
    console.error("Parse error:", err);
  }, []);

  const handleEvent = useCallback((event: { type: string; data?: any }) => {
    console.log("Widget event:", event.type, event.data);
  }, []);

  return (
    <div>
      <button onClick={handleOpen}>
        Import Portfolio
      </button>

      {isOpen && accessToken && (
        <PortfolioConnect
          accessToken={accessToken}
          onSuccess={handleSuccess}
          onError={handleError}
          onEvent={handleEvent}
          onExit={() => setIsOpen(false)}
          // Optional: pre-fill user's phone for CDSL fetch
          // phone="9876543210"
          // Optional: enable specific features
          // enableCdslFetch={true}
          // enableInbox={true}
        />
      )}

      {error && (
        <div style={{ color: "red", marginTop: 16 }}>
          Error: {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Portfolio Summary</h3>
          <p>Investor: {result.investor.name}</p>
          <p>CAS Type: {result.meta.cas_type}</p>
          <p>Total Value: Rs.{result.summary.total_value.toLocaleString()}</p>
          <p>Demat Accounts: {result.demat_accounts.length}</p>
          <p>Mutual Fund Folios: {result.mutual_funds.length}</p>
        </div>
      )}
    </div>
  );
}
