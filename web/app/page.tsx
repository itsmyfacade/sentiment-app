"use client";

import { useState } from "react";

/*
  Frontend page for the Sentiment App.
  - Uses a Next.js API route (/api/analyze) that proxies to the Flask backend.
  - Shows loading state, result, and simple error messages.
*/

type AnalyzeResponse = { label: string; score: number };
type ErrorResponse = { error?: string };

export default function Home() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setResult(null);

    // basic validation (require some text)
    const value = text.trim();
    if (!value) {
      setError("Please enter some text to analyze.");
      return;
    }

    try {
      setLoading(true);

      // call our Next.js proxy which forwards to Flask
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value }),
      });

      const data = (await res.json()) as AnalyzeResponse & ErrorResponse;

      if (!res.ok) {
        // backend might send {error: "..."} on bad requests
        setError(data?.error || "Request failed.");
        return;
      }

      // quick type check (should be label + score)
      if (typeof data.label !== "string" || typeof data.score !== "number") {
        setError("Unexpected response from API.");
        return;
      }

      setResult({ label: data.label, score: data.score });
    } catch {
      setError("Could not reach the API. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <h1>Sentiment Analysis</h1>
      <p>Enter some text and get a sentiment prediction from the API.</p>

      <form onSubmit={onSubmit} style={{ display: "grid", gap: 12 }}>
        <label>
          Text to analyze
          <textarea
            rows={6}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type or paste text here..."
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {/* error message (shows under the form) */}
      {error && <div className="error">{error}</div>}

      {/* result box (only shows after a successful call) */}
      {result && (
        <div className="result" aria-live="polite">
          {result.label} ({(result.score * 100).toFixed(1)}%)
        </div>
      )}
    </main>
  );
}
