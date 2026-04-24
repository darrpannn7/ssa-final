import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const base = process.env.BACKEND_URL;

    if (!base) {
      return NextResponse.json(
        { error: "Missing BACKEND_URL" },
        { status: 500 }
      );
    }

    const body = await req.json();

    const res = await fetch(`${base}/ai/flare-predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const detail = await res.text();
      return NextResponse.json(
        { error: `Backend error: ${detail}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);

  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
