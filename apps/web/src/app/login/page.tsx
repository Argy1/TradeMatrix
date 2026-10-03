import type { Metadata } from "next";

import { LoginForm } from "@/components/login-form";

export const metadata: Metadata = { title: "Sign in" };

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const { mode, error } = await searchParams;
  const signup = mode === "signup";
  return (
    <div className="mx-auto max-w-md space-y-6 pt-8">
      <div>
        <h1 className="font-display text-3xl font-bold">{signup ? "Create a free account" : "Sign in"}</h1>
        <p className="mt-2 text-fg-2">
          An account lets you keep a watchlist. Signals and the track record are public.
        </p>
      </div>
      <LoginForm mode={signup ? "signup" : "signin"} error={typeof error === "string" ? error : undefined} />
    </div>
  );
}
