/**
 * CAS Parser — Portfolio Connect (Next.js Full Page)
 *
 * Complete Next.js page with:
 * - Backend API route for access token generation
 * - Frontend Portfolio Connect widget
 * - Result display
 *
 * Install:
 *   npm install @cas-parser/connect
 *
 * Files to create:
 *   1. app/api/casparser-token/route.ts  (or pages/api/casparser-token.ts)
 *   2. app/portfolio/page.tsx  (or pages/portfolio.tsx)
 */

// ============================================================
// FILE 1: app/api/casparser-token/route.ts (App Router)
// ============================================================
// This runs on your server — safe to use API key here.

/*
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

  if (!response.ok) {
    return NextResponse.json(
      { error: data.detail || "Failed to generate token" },
      { status: 500 }
    );
  }

  return NextResponse.json({
    access_token: data.access_token,
    expires_in: data.expires_in,
  });
}
*/

// ============================================================
// FILE 2: app/portfolio/page.tsx (App Router)
// ============================================================

"use client";

import React, { useState, useCallback } from "react";
import { PortfolioConnect } from "@cas-parser/connect";

interface PortfolioData {
  meta: { cas_type: string; statement_period: { from: string; to: string } };
  investor: { name: string; pan: string; email: string };
  summary: {
    total_value: number;
    accounts: Record<string, { count: number; total_value: number }>;
  };
  demat_accounts: any[];
  mutual_funds: any[];
}

export default function PortfolioPage() {
  const [accessToken, setAccessToken] = useState("");
  const [result, setResult] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const openWidget = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/casparser-token", { method: "POST" });
      const data = await res.json();

      if (!res.ok) throw new Error(data.error || "Token generation failed");

      setAccessToken(data.access_token);
      setIsOpen(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
      <h1>Portfolio Tracker</h1>
      <p>Import your CAS statement to view your complete portfolio.</p>

      <button
        onClick={openWidget}
        disabled={loading}
        style={{
          padding: "12px 24px",
          fontSize: 16,
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: 8,
          cursor: loading ? "wait" : "pointer",
        }}
      >
        {loading ? "Loading..." : "Import Portfolio Statement"}
      </button>

      {isOpen && accessToken && (
        <PortfolioConnect
          accessToken={accessToken}
          enableCdslFetch={true}
          enableInbox={true}
          onSuccess={(data: PortfolioData) => {
            setResult(data);
            setIsOpen(false);
          }}
          onError={(err: { message: string }) => {
            setError(err.message);
          }}
          onExit={() => setIsOpen(false)}
          onEvent={(event: { type: string }) => {
            console.log("Event:", event.type);
          }}
        />
      )}

      {error && (
        <div style={{ color: "red", marginTop: 16, padding: 12, background: "#fef2f2", borderRadius: 8 }}>
          {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 24 }}>
          <h2>Portfolio Summary</h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div style={{ padding: 16, background: "#f0f9ff", borderRadius: 8 }}>
              <strong>Investor</strong>
              <p>{result.investor.name}</p>
              <p>PAN: {result.investor.pan}</p>
            </div>
            <div style={{ padding: 16, background: "#f0fdf4", borderRadius: 8 }}>
              <strong>Total Value</strong>
              <p style={{ fontSize: 24, fontWeight: "bold" }}>
                Rs.{result.summary.total_value.toLocaleString()}
              </p>
            </div>
          </div>

          <h3 style={{ marginTop: 24 }}>Holdings</h3>
          {Object.entries(result.summary.accounts).map(([category, info]) =>
            info.count > 0 ? (
              <p key={category}>
                {category}: {info.count} accounts — Rs.{info.total_value.toLocaleString()}
              </p>
            ) : null
          )}
        </div>
      )}
    </div>
  );
}
