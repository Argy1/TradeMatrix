"use client";

import { createBrowserClient } from "@supabase/ssr";

// Only the public URL and the publishable key live in the browser; RLS protects the data
// (CLAUDE.md rule 4). The service-role key never comes near this app.
export function supabaseBrowser() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
