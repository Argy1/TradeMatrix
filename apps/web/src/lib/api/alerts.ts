"use client";

import type { Session } from "@supabase/supabase-js";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { AlertInput } from "@/lib/alerts";

import { api, unwrap } from "./client";

// Every call carries the user's own access token. The API checks it and only ever returns or
// changes that user's rules and notifications.
const bearer = (session: Session) => ({ Authorization: `Bearer ${session.access_token}` });

export function useAlerts(session: Session | null) {
  return useQuery({
    queryKey: ["alerts", session?.user.id],
    queryFn: () => unwrap(api.GET("/v1/alerts", { headers: bearer(session!) })),
    enabled: session !== null,
  });
}

export function useCreateAlert(session: Session | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AlertInput) =>
      unwrap(api.POST("/v1/alerts", { body, headers: bearer(session!) })),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts", session?.user.id] }),
  });
}

export function useUpdateAlert(session: Session | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, active }: { id: string; active: boolean }) =>
      unwrap(
        api.PATCH("/v1/alerts/{alert_id}", {
          params: { path: { alert_id: id } },
          body: { active },
          headers: bearer(session!),
        }),
      ),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts", session?.user.id] }),
  });
}

export function useDeleteAlert(session: Session | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      unwrap(
        api.DELETE("/v1/alerts/{alert_id}", {
          params: { path: { alert_id: id } },
          headers: bearer(session!),
        }),
      ),
    // The API answers with the remaining rules, so the list updates without a second request.
    onSuccess: (data) => queryClient.setQueryData(["alerts", session?.user.id], data),
  });
}

/** In-app notifications. Signal alerts arrive once per candle, so a minute is fresh enough. */
export function useNotifications(session: Session | null) {
  return useQuery({
    queryKey: ["notifications", session?.user.id],
    queryFn: () =>
      unwrap(
        api.GET("/v1/notifications", {
          params: { query: { limit: 30 } },
          headers: bearer(session!),
        }),
      ),
    enabled: session !== null,
    refetchInterval: 60_000,
  });
}

export function useMarkRead(session: Session | null) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) =>
      unwrap(
        api.POST("/v1/notifications/{notification_id}/read", {
          params: { path: { notification_id: id } },
          headers: bearer(session!),
        }),
      ),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["notifications", session?.user.id] }),
  });
}
