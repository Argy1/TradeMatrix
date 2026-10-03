"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useSession } from "@/lib/api/account";
import { supabaseBrowser } from "@/lib/supabase/client";

export function AuthButtons() {
  const { session, ready } = useSession();
  const router = useRouter();

  if (!ready) return <div className="h-11 w-40" aria-hidden />;

  if (session)
    return (
      <div className="flex items-center gap-3 text-sm">
        <span className="hidden max-w-48 truncate text-fg-2 md:inline" title={session.user.email}>
          {session.user.email}
        </span>
        <button
          type="button"
          className="key px-4 py-2.5 font-semibold"
          onClick={async () => {
            await supabaseBrowser().auth.signOut();
            router.push("/");
            router.refresh();
          }}
        >
          Sign out
        </button>
      </div>
    );

  return (
    <div className="flex items-center gap-3 text-sm">
      <Link href="/login" className="key px-4 py-2.5 font-semibold text-fg">
        Sign in
      </Link>
      <Link href="/login?mode=signup" className="btn-primary hidden px-4 py-2.5 sm:inline-block">
        Create free account
      </Link>
    </div>
  );
}
