import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8001";

// POST /api/analyze  -> forwards to Flask /analyze
export async function POST(req: Request) {
  try {
    const body = await req.text(); // pass JSON through unchanged
    const r = await fetch(`${API_URL}/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    const text = await r.text(); // forward the body + status
    return new NextResponse(text, {
      status: r.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch {
    return NextResponse.json(
      { error: "Proxy failed to reach backend" },
      { status: 502 }
    );
  }
}