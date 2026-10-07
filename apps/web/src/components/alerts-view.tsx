"use client";

import type { Session } from "@supabase/supabase-js";
import { Bell, BellOff, Check, Trash2 } from "lucide-react";
import Link from "next/link";
import { type FormEvent, useState } from "react";

import {
  type Alert,
  type AlertType,
  type AppNotification,
  TYPE_OPTIONS,
  cooldownWords,
  isSignalType,
  parseThreshold,
  ruleSentence,
} from "@/lib/alerts";
import { useSession } from "@/lib/api/account";
import {
  useAlerts,
  useCreateAlert,
  useDeleteAlert,
  useMarkRead,
  useNotifications,
  useUpdateAlert,
} from "@/lib/api/alerts";
import { ApiError, TIMEFRAMES, type Timeframe } from "@/lib/api/client";
import { useMarkets } from "@/lib/api/hooks";
import { DISCLAIMER_SHORT } from "@/lib/copy";
import { formatAgo, formatDateTime } from "@/lib/format";

import { ErrorState, Skeleton } from "./states";

const FIELD = "w-full rounded-xl border border-white/15 bg-white/5 px-4 py-3 text-fg";
const COOLDOWNS = [15, 60, 240, 1440];

function errorText(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback;
}

function NewAlertForm({ session, full }: { session: Session; full: boolean }) {
  const markets = useMarkets();
  const create = useCreateAlert(session);
  const [symbol, setSymbol] = useState("BTC");
  const [type, setType] = useState<AlertType>("signal_change");
  const [tf, setTf] = useState<Timeframe>("1h");
  const [typed, setTyped] = useState("");
  const [cooldown, setCooldown] = useState(60);
  const [problem, setProblem] = useState<string | null>(null);

  const signal = isSignalType(type);
  const needsLevel = type !== "signal_change";

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const { threshold, error } = parseThreshold(type, typed);
    if (error) return setProblem(error);
    setProblem(null);
    create.mutate(
      {
        symbol,
        type,
        timeframe: signal ? tf : null,
        threshold,
        cooldown_minutes: cooldown,
      },
      { onSuccess: () => setTyped("") },
    );
  };

  return (
    <form onSubmit={submit} className="glass space-y-5 p-6">
      <h2 className="font-display text-lg font-semibold">New alert</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label htmlFor="alert-coin" className="block text-sm font-semibold">
            Coin
          </label>
          <select
            id="alert-coin"
            value={symbol}
            onChange={(event) => setSymbol(event.target.value)}
            className={FIELD}
          >
            {(markets.data ?? [{ symbol: "BTC", name: "Bitcoin" }]).map((row) => (
              <option key={row.symbol} value={row.symbol} className="bg-ink">
                {row.name} ({row.symbol})
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-2">
          <label htmlFor="alert-type" className="block text-sm font-semibold">
            Tell me when
          </label>
          <select
            id="alert-type"
            value={type}
            onChange={(event) => {
              setType(event.target.value as AlertType);
              setTyped("");
              setProblem(null);
            }}
            className={FIELD}
          >
            {TYPE_OPTIONS.map((option) => (
              <option key={option.type} value={option.type} className="bg-ink">
                {option.label}
              </option>
            ))}
          </select>
        </div>
        {signal && (
          <div className="space-y-2">
            <label htmlFor="alert-tf" className="block text-sm font-semibold">
              Candle size
            </label>
            <select
              id="alert-tf"
              value={tf}
              onChange={(event) => setTf(event.target.value as Timeframe)}
              className={FIELD}
            >
              {TIMEFRAMES.map((option) => (
                <option key={option} value={option} className="bg-ink">
                  {option}
                </option>
              ))}
            </select>
          </div>
        )}
        {needsLevel && (
          <div className="space-y-2">
            <label htmlFor="alert-level" className="block text-sm font-semibold">
              {signal ? "Chance of Up (%)" : "Price in USDT"}
            </label>
            <input
              id="alert-level"
              inputMode="decimal"
              required
              value={typed}
              onChange={(event) => setTyped(event.target.value)}
              placeholder={signal ? "60" : "85000"}
              aria-describedby="alert-level-hint"
              className={`${FIELD} font-mono placeholder:text-muted`}
            />
            <p id="alert-level-hint" className="text-xs text-muted">
              {signal
                ? "A number from 1 to 99. The chance of Down is 100 minus this."
                : "You are notified when the price moves across this level, not while it stays beyond it."}
            </p>
          </div>
        )}
        <div className="space-y-2">
          <label htmlFor="alert-cooldown" className="block text-sm font-semibold">
            At most once every
          </label>
          <select
            id="alert-cooldown"
            value={cooldown}
            onChange={(event) => setCooldown(Number(event.target.value))}
            className={FIELD}
          >
            {COOLDOWNS.map((minutes) => (
              <option key={minutes} value={minutes} className="bg-ink">
                {cooldownWords(minutes)}
              </option>
            ))}
          </select>
        </div>
      </div>
      {(problem || create.isError) && (
        <p role="alert" className="text-sm text-down-fg">
          {problem ?? errorText(create.error, "Could not save the alert. Please try again.")}
        </p>
      )}
      {create.isSuccess && !problem && (
        <p role="status" className="text-sm text-up">
          Alert saved.
        </p>
      )}
      <button
        type="submit"
        disabled={create.isPending || full}
        className="btn-primary min-h-11 px-5 py-3 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {create.isPending ? "Saving…" : "Save alert"}
      </button>
      {full && (
        <p className="text-sm text-neutral">
          You have reached the maximum number of alerts. Delete one to add another.
        </p>
      )}
    </form>
  );
}

function AlertRow({ alert, session }: { alert: Alert; session: Session }) {
  const update = useUpdateAlert(session);
  const remove = useDeleteAlert(session);
  const busy = update.isPending || remove.isPending;
  return (
    <li className="glass flex flex-wrap items-center gap-4 p-4 sm:p-5">
      <div className="min-w-0 flex-1 basis-64">
        <p className="font-semibold text-fg">{ruleSentence(alert)}</p>
        <p className="mt-1 text-sm text-muted">
          {alert.active ? "Active" : "Paused"} · at most once every{" "}
          {cooldownWords(alert.cooldown_minutes)} ·{" "}
          {alert.last_triggered_at
            ? `last fired ${formatDateTime(alert.last_triggered_at)}`
            : "has not fired yet"}
        </p>
        {(update.isError || remove.isError) && (
          <p role="alert" className="mt-1 text-sm text-down-fg">
            Could not change this alert. Please try again.
          </p>
        )}
      </div>
      <button
        type="button"
        disabled={busy}
        aria-pressed={!alert.active}
        onClick={() => update.mutate({ id: alert.id, active: !alert.active })}
        className="key inline-flex min-h-11 items-center gap-2 px-4 text-sm font-semibold"
      >
        {alert.active ? <BellOff aria-hidden size={16} /> : <Bell aria-hidden size={16} />}
        {alert.active ? "Pause" : "Resume"}
      </button>
      <button
        type="button"
        disabled={busy}
        onClick={() => remove.mutate(alert.id)}
        aria-label={`Delete alert: ${ruleSentence(alert)}`}
        className="key inline-flex min-h-11 items-center gap-2 px-4 text-sm font-semibold"
      >
        <Trash2 aria-hidden size={16} /> Delete
      </button>
    </li>
  );
}

function NotificationRow({ item, session }: { item: AppNotification; session: Session }) {
  const markRead = useMarkRead(session);
  const unread = item.read_at === null;
  return (
    <li className="flex flex-wrap items-start gap-x-4 gap-y-2 border-t border-white/10 py-4 first:border-t-0 first:pt-0">
      <div className="min-w-0 flex-1 basis-64">
        <p className="font-semibold text-fg">
          {unread && (
            <span className="mr-2 rounded-full bg-cyan/15 px-2 py-0.5 text-xs font-bold text-cyan">
              New
            </span>
          )}
          {item.title}
        </p>
        <p className="mt-1 text-sm text-fg-2">{item.body}</p>
        <p className="mt-1 text-xs text-muted">
          <time dateTime={item.created_at} title={formatDateTime(item.created_at)}>
            {formatAgo(item.created_at)}
          </time>
        </p>
      </div>
      {unread && (
        <button
          type="button"
          disabled={markRead.isPending}
          onClick={() => markRead.mutate(item.id)}
          className="key inline-flex min-h-11 items-center gap-2 px-4 text-sm font-semibold"
        >
          <Check aria-hidden size={16} /> Mark as read
        </button>
      )}
    </li>
  );
}

export function AlertsView() {
  const { session, ready } = useSession();
  const alerts = useAlerts(session);
  const notifications = useNotifications(session);

  if (!ready) return <Skeleton className="h-64" />;
  if (!session)
    return (
      <div className="glass space-y-4 p-6">
        <p className="text-fg-2">
          Sign in to get a notification when a signal changes or a price crosses a level you
          choose. Signals stay public either way.
        </p>
        <Link href="/login" className="btn-primary inline-block px-5 py-3">
          Sign in
        </Link>
      </div>
    );

  const items = alerts.data?.items ?? [];
  const max = alerts.data?.max_alerts ?? 20;
  return (
    <div className="space-y-8">
      <section aria-labelledby="notifications" className="glass space-y-4 p-6">
        <h2 id="notifications" className="font-display text-lg font-semibold">
          Notifications
          {notifications.data && notifications.data.unread > 0 && (
            <span className="ml-2 text-sm font-normal text-cyan">
              {notifications.data.unread} new
            </span>
          )}
        </h2>
        {notifications.isPending ? (
          <Skeleton className="h-24" />
        ) : notifications.isError ? (
          <ErrorState
            message="Could not load your notifications."
            onRetry={() => notifications.refetch()}
          />
        ) : notifications.data.items.length === 0 ? (
          <p className="text-sm text-fg-2">
            Nothing yet. When one of your alerts fires, it shows up here.
          </p>
        ) : (
          <ul>
            {notifications.data.items.map((item) => (
              <NotificationRow key={item.id} item={item} session={session} />
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="rules" className="space-y-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h2 id="rules" className="font-display text-lg font-semibold">
            Your alerts
          </h2>
          {alerts.data && (
            <p className="text-sm text-muted">
              {items.length} of {max} used
            </p>
          )}
        </div>
        {alerts.isPending ? (
          <Skeleton className="h-24" />
        ) : alerts.isError ? (
          <ErrorState message="Could not load your alerts." onRetry={() => alerts.refetch()} />
        ) : items.length === 0 ? (
          <p className="glass p-6 text-fg-2">You have no alerts yet. Create the first one below.</p>
        ) : (
          <ul className="space-y-3">
            {items.map((alert) => (
              <AlertRow key={alert.id} alert={alert} session={session} />
            ))}
          </ul>
        )}
      </section>

      <NewAlertForm session={session} full={items.length >= max} />

      <p className="text-sm leading-relaxed text-muted">
        Signal alerts are checked each time a candle closes. Price alerts are checked once a
        minute. Notifications appear on this page; phone notifications come with the mobile app.{" "}
        {DISCLAIMER_SHORT}
      </p>
    </div>
  );
}

/** The button under the signal card: one tap creates "tell me when this signal changes". */
export function SignalAlertButton({ symbol, tf }: { symbol: string; tf: Timeframe }) {
  const { session, ready } = useSession();
  const alerts = useAlerts(session);
  const create = useCreateAlert(session);
  const base = "btn-primary flex min-h-12 w-full items-center justify-center gap-2 px-4 py-3";

  if (ready && !session)
    return (
      <div>
        <Link href="/login" className={base}>
          <Bell aria-hidden size={18} /> Sign in to get alerts
        </Link>
        <p className="mt-2 text-center text-xs text-muted">
          Free. You are told when this signal changes.
        </p>
      </div>
    );

  const existing = alerts.data?.items.find(
    (alert) => alert.type === "signal_change" && alert.symbol === symbol && alert.timeframe === tf,
  );
  if (existing)
    return (
      <div>
        <Link href="/alerts" className="key flex min-h-12 w-full items-center justify-center gap-2 px-4 py-3 font-semibold">
          <Check aria-hidden size={18} /> Alert is set. Manage alerts
        </Link>
        <p className="mt-2 text-center text-xs text-muted">
          {existing.active
            ? `You are told when the ${symbol} ${tf} signal changes.`
            : "This alert is paused."}
        </p>
      </div>
    );

  return (
    <div>
      <button
        type="button"
        disabled={!ready || alerts.isPending || create.isPending}
        onClick={() =>
          create.mutate({ symbol, type: "signal_change", timeframe: tf, cooldown_minutes: 60 })
        }
        className={`${base} disabled:cursor-not-allowed disabled:opacity-60`}
      >
        <Bell aria-hidden size={18} />
        {create.isPending ? "Saving…" : "Alert me when this signal changes"}
      </button>
      {create.isError ? (
        <p role="alert" className="mt-2 text-center text-xs text-down-fg">
          {errorText(create.error, "Could not save the alert. Please try again.")}
        </p>
      ) : (
        <p className="mt-2 text-center text-xs text-muted">
          You get a notification on the Alerts page. {DISCLAIMER_SHORT}
        </p>
      )}
    </div>
  );
}

/** Unread count next to "Alerts" in the header (only when signed in and there is something). */
export function UnreadBadge() {
  const { session } = useSession();
  const notifications = useNotifications(session);
  const unread = notifications.data?.unread ?? 0;
  if (!session || unread === 0) return null;
  return (
    <span className="ml-1.5 rounded-full bg-cyan/20 px-2 py-0.5 text-xs font-bold text-cyan">
      {unread > 99 ? "99+" : unread}
      <span className="sr-only"> unread notifications</span>
    </span>
  );
}
