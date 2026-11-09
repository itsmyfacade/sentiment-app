"use client";

import { useState } from "react";

type AnalyzeResponse = { label: string; score: number; inference_time_ms?: number };
type ErrorResponse = { error?: string };
const examples = [
  { label: "Positive example", text: "The new workflow is clear, fast, and genuinely helpful." },
  { label: "Negative example", text: "The update is confusing, unreliable, and difficult to use." },
];

function LegacyHome() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState("");

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setResult(null);
    const value = text.trim();
    if (!value) { setError("Enter text before running the analysis."); return; }
    try {
      setLoading(true);
      const response = await fetch("/api/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text: value }) });
      const data = (await response.json()) as AnalyzeResponse & ErrorResponse;
      if (!response.ok) { setError(data.error || "The analysis request could not be completed."); return; }
      if (typeof data.label !== "string" || typeof data.score !== "number") { setError("The service returned an unexpected response."); return; }
      setResult(data);
    } catch { setError("Could not reach the analysis service. Check that the backend is running."); }
    finally { setLoading(false); }
  }

  const score = result ? Math.max(0, Math.min(1, result.score)) : 0;
  const isPositive = result?.label.toUpperCase() === "POSITIVE";

  return (
    <main className="app-shell">
      <header className="topbar"><a className="brand" href="/" aria-label="Sentiment Analysis home"><span className="brand-mark" aria-hidden="true">SA</span><span>Sentiment Lab</span></a><span className="service-status"><span className="status-dot" /> Local inference workspace</span></header>
      <section className="hero" aria-labelledby="page-title"><p className="eyebrow">NLP / BINARY CLASSIFICATION</p><h1 id="page-title">Read the signal<br /><span>inside the words.</span></h1><p className="hero-copy">A focused sentiment workspace powered by DistilBERT. Test a sentence, inspect the model signal, and understand what the result does — and does not — mean.</p></section>
      <section className="workspace-grid" aria-label="Sentiment analysis workspace">
        <form className="analysis-card" onSubmit={onSubmit}>
          <div className="card-heading"><div><p className="eyebrow">01 / INPUT</p><h2>Analyze a statement</h2></div><span className="model-chip">SST-2</span></div>
          <label className="field-label" htmlFor="sentiment-text">Text to analyze</label>
          <textarea id="sentiment-text" rows={8} maxLength={5000} value={text} onChange={(event) => setText(event.target.value)} placeholder="Paste a review, message, or observation here..." aria-describedby="text-help text-count" />
          <div className="field-meta"><span id="text-help">Up to 5,000 characters</span><span id="text-count">{text.length.toLocaleString()} / 5,000</span></div>
          <div className="examples" aria-label="Example inputs"><span className="examples-label">Try an example</span>{examples.map((example) => <button className="example-button" type="button" key={example.label} onClick={() => { setText(example.text); setResult(null); setError(""); }}>{example.label}</button>)}</div>
          <button className="primary-button" type="submit" disabled={loading || !text.trim()}><span>{loading ? "Running inference" : "Analyze sentiment"}</span><span aria-hidden="true">{loading ? "…" : "→"}</span></button>
          <div className="form-status" aria-live="polite">{loading && <span className="loading-line"><span className="spinner" /> Loading the model or scoring your text…</span>}{error && <div className="error-message" role="alert"><strong>Request not completed</strong><span>{error}</span></div>}</div>
        </form>
        <aside className={`result-card ${result ? "has-result" : ""}`} aria-live="polite" aria-label="Analysis result">
          <div className="card-heading"><div><p className="eyebrow">02 / RESULT</p><h2>Model readout</h2></div><span className="result-index">{result ? "LIVE" : "WAITING"}</span></div>
          {result ? <div className="result-content"><p className="result-kicker">Predicted sentiment</p><p className={`result-label ${isPositive ? "positive" : "negative"}`}>{result.label}</p><p className="result-explanation">The model assigned this text to its {isPositive ? "positive" : "negative"} class.</p><div className="confidence-block"><div className="confidence-header"><span>Model score</span><strong>{(score * 100).toFixed(1)}%</strong></div><div className="confidence-track"><span className={isPositive ? "positive-fill" : "negative-fill"} style={{ width: `${score * 100}%` }} /></div><span className="confidence-note">Score from the returned model response; not a calibrated probability.</span></div>{typeof result.inference_time_ms === "number" && <div className="timing-row"><span>Inference time</span><strong>{result.inference_time_ms.toFixed(2)} ms</strong></div>}</div> : <div className="empty-result"><div className="empty-orbit" aria-hidden="true"><span /></div><h3>Your result will appear here</h3><p>Run an analysis to inspect the predicted class, returned score, and actual inference time.</p></div>}
        </aside>
      </section>
      <section className="model-note" aria-labelledby="model-note-title"><div className="note-icon" aria-hidden="true">i</div><div><h2 id="model-note-title">What this model can tell you</h2><p>Sentiment Lab uses <strong>distilbert-base-uncased-finetuned-sst-2-english</strong>, a binary classifier trained for positive and negative sentiment. It does not detect neutral sentiment, emotions, intent, or factual truth. Treat every output as a model signal to investigate, not a verdict.</p></div></section>
      <footer className="app-footer"><span>Built as a focused ML inference application</span><span>DistilBERT · Transformers · Flask · Next.js</span></footer>
    </main>
  );
}

export { default } from "./AnalysisWorkbench";
