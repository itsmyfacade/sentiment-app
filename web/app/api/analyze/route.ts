import { NextResponse } from "next/server";

/*
  Simple proxy route.
  - Receives POST from the page.
  - Forwards to the Flask API /analyze.
  - Sends the Flask response back to the browser.
*/

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

export async function POST(req: Request) {
  try {
    const body = await req.text(); // pass body through as-is
    const r = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    // forward status + JSON back to the browser
    const text = await r.text();
    return new NextResponse(text, {
      status: r.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    // if Flask is down or not reachable
    return NextResponse.json({ error: "Proxy failed to reach backend" }, { status: 502 });
  }
}
