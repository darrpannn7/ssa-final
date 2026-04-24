import { NextResponse } from "next/server";

export async function POST(req: Request) {
  let formData: FormData;

  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json(
      { error: "Invalid form data" },
      { status: 400 }
    );
  }

  try {
    const base = process.env.BACKEND_URL;

    if (!base) {
      return NextResponse.json(
        { error: "Missing BACKEND_URL" },
        { status: 500 }
      );
    }

    const res = await fetch(`${base}/ai/chat`, {
      method: "POST",
      body: formData,
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
