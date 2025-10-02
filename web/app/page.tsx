"use client";

import { useState } from "react";

/*
  Simple sentiment form.
  - Sends text to /api/analyze (Next.js API route).
  - Shows loading, result, or an error message.
*/

type AnalyzeResponse = { label: string; score: number };
type ErrorResponse = { error?: string };

export default function Home() {
  // form state
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  // UI feedback
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    // reset messages each submit
    setError("");
    setResult(null);

    // basic check: must have text
    const value = text.trim();
    if (!value) {
      setError("Please enter some text to analyze.");
      return;
    }

    try {
      setLoading(true);

      // call Next.js API route which forwards to Flask
      const res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: value }),
      });

      const data = (await res.json()) as AnalyzeResponse & ErrorResponse;

      if (!res.ok) {
        setError(data?.error || "Request failed.");
        return;
      }

      // quick safety check for expected shape
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

  // disable button while loading or if the box is empty
  const isDisabled = loading || !text.trim();

  // choose a class based on the label (for color)
  const resultClass =
    result?.label?.toUpperCase() === "POSITIVE" ? "result positive" : "result negative";

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

        <button type="submit" disabled={isDisabled}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {/* show error under the form */}
      {error && <div className="error">{error}</div>}

      {/* show result when we have it */}
      {result && (
        <div className={resultClass} aria-live="polite">
          {result.label} ({(result.score * 100).toFixed(1)}%)
        </div>
      )}
    </main>
  );
}
