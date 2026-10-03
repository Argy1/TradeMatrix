"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { supabaseBrowser } from "@/lib/supabase/client";

type Mode = "signin" | "signup";

export function LoginForm({ mode, error }: { mode: Mode; error?: string }) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(
    error === "confirm" ? "That confirmation link is invalid or expired. Please sign in or sign up again." : null,
  );
  const [sent, setSent] = useState(false);
  const signup = mode === "signup";

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage(null);
    const supabase = supabaseBrowser();
    if (signup) {
      const { data, error: failure } = await supabase.auth.signUp({
        email,
        password,
        // The confirmation email brings the person back to /auth/callback on this site.
        options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
      });
      setBusy(false);
      if (failure) return setMessage(failure.message);
      if (data.session) {
        router.push("/watchlist");
        router.refresh();
        return;
      }
      setSent(true);
      return;
    }
    const { error: failure } = await supabase.auth.signInWithPassword({ email, password });
    setBusy(false);
    if (failure) return setMessage(failure.message);
    router.push("/watchlist");
    router.refresh();
  }

  if (sent)
    return (
      <div role="status" className="glass space-y-2 p-6">
        <h2 className="font-display text-xl font-semibold">Check your inbox</h2>
        <p className="text-fg-2">
          We sent a confirmation link to <strong>{email}</strong>. Open it to finish creating your
          account.
        </p>
      </div>
    );

  return (
    <form onSubmit={submit} className="glass space-y-5 p-6" noValidate={false}>
      <div className="space-y-2">
        <label htmlFor="email" className="block text-sm font-semibold">
          Email
        </label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-fg placeholder:text-muted"
        />
      </div>
      <div className="space-y-2">
        <label htmlFor="password" className="block text-sm font-semibold">
          Password
        </label>
        <input
          id="password"
          type="password"
          required
          minLength={8}
          autoComplete={signup ? "new-password" : "current-password"}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-describedby="password-hint"
          className="w-full rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-fg"
        />
        <p id="password-hint" className="text-xs text-muted">
          At least 8 characters.
        </p>
      </div>
      {message && (
        <p role="alert" className="text-sm text-down-fg">
          {message}
        </p>
      )}
      <button type="submit" disabled={busy} className="btn-primary w-full px-4 py-3 disabled:opacity-60">
        {busy ? "Please wait…" : signup ? "Create free account" : "Sign in"}
      </button>
      <p className="text-center text-sm text-fg-2">
        {signup ? (
          <>
            Already have an account? <Link href="/login" className="text-cyan underline-offset-4 hover:underline">Sign in</Link>
          </>
        ) : (
          <>
            New here? <Link href="/login?mode=signup" className="text-cyan underline-offset-4 hover:underline">Create a free account</Link>
          </>
        )}
      </p>
    </form>
  );
}
