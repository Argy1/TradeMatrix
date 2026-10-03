import { NextResponse } from "next/server";

import { supabaseServer } from "@/lib/supabase/server";

/**
 * The confirmation email links here with a one-time `code`. We swap it for a session cookie
 * (PKCE flow) and send the person on. Only same-site paths are allowed as `next`.
 */
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");
  const next = url.searchParams.get("next") ?? "/watchlist";
  const safeNext = next.startsWith("/") && !next.startsWith("//") ? next : "/watchlist";

  if (code) {
    const supabase = await supabaseServer();
    const { error } = await supabase.auth.exchangeCodeForSession(code);
    if (!error) return NextResponse.redirect(new URL(safeNext, url.origin));
  }
  return NextResponse.redirect(new URL("/login?error=confirm", url.origin));
}
