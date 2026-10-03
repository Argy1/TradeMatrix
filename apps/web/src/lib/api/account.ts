"use client";

import type { Session } from "@supabase/supabase-js";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";

import { supabaseBrowser } from "@/lib/supabase/client";

import { api, unwrap } from "./client";

/** The current login session, kept in sync with sign-in / sign-out in any tab. */
export function useSession() {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const supabase = supabaseBrowser();
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setReady(true);
    });
    const { data } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => data.subscription.unsubscribe();
  }, []);
  return { session, ready };
}

const bearer = (session: Session) => ({ Authorization: `Bearer ${session.access_token}` });

export function useWatchlist(session: Session | null) {
  return useQuery({
    queryKey: ["watchlist", session?.user.id],
    queryFn: () => unwrap(api.GET("/v1/watchlist", { headers: bearer(session!) })),
    enabled: session !== null,
  });
}

export function useToggleWatchlist(session: Session | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ symbol, add }: { symbol: string; add: boolean }) => {
      const options = { params: { path: { symbol } }, headers: bearer(session!) };
      return unwrap(add ? api.PUT("/v1/watchlist/{symbol}", options) : api.DELETE("/v1/watchlist/{symbol}", options));
    },
    onSuccess: (data) => queryClient.setQueryData(["watchlist", session?.user.id], data),
  });
}
