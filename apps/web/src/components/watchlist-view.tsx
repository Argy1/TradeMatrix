"use client";

import { Star, StarOff } from "lucide-react";
import Link from "next/link";

import { useSession, useToggleWatchlist, useWatchlist } from "@/lib/api/account";
import { TIMEFRAMES } from "@/lib/api/client";
import { useMarkets } from "@/lib/api/hooks";
import { formatChange, formatPrice, formatProbability } from "@/lib/format";
import { asDirection, shownProbability } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon } from "./direction";
import { ErrorState, Skeleton } from "./states";

/** Star button on the coin page: add or remove this coin from the watchlist. */
export function WatchToggle({ symbol }: { symbol: string }) {
  const { session, ready } = useSession();
  const list = useWatchlist(session);
  const toggle = useToggleWatchlist(session);
  if (!ready) return null;
  if (!session)
    return (
      <Link href="/login" className="key inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold">
        <Star aria-hidden size={16} /> Sign in to watch
      </Link>
    );
  const watching = list.data?.symbols.includes(symbol) ?? false;
  return (
    <button
      type="button"
      aria-pressed={watching}
      disabled={toggle.isPending || list.isPending}
      onClick={() => toggle.mutate({ symbol, add: !watching })}
      className="key inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold"
    >
      {watching ? <StarOff aria-hidden size={16} /> : <Star aria-hidden size={16} />}
      {watching ? "Remove from watchlist" : "Add to watchlist"}
    </button>
  );
}

export function WatchlistView() {
  const { session, ready } = useSession();
  const list = useWatchlist(session);
  const toggle = useToggleWatchlist(session);
  const markets = useMarkets();

  if (!ready) return <Skeleton className="h-64" />;
  if (!session)
    return (
      <div className="glass space-y-4 p-6">
        <p className="text-fg-2">Sign in to keep a list of the coins you follow. Signals stay public either way.</p>
        <Link href="/login" className="btn-primary inline-block px-5 py-3">Sign in</Link>
      </div>
    );
  if (list.isError) return <ErrorState message="Could not load your watchlist." onRetry={() => list.refetch()} />;
  if (list.isPending || markets.isPending) return <Skeleton className="h-64" />;

  const watched = new Set(list.data.symbols);
  const rows = markets.data ?? [];
  const mine = rows.filter((row) => watched.has(row.symbol));
  const others = rows.filter((row) => !watched.has(row.symbol));

  return (
    <div className="space-y-8">
      {mine.length === 0 ? (
        <div className="glass space-y-2 p-6">
          <p className="font-semibold">Your watchlist is empty.</p>
          <p className="text-fg-2">Add a coin below to see its signals here at a glance.</p>
        </div>
      ) : (
        <ul className="space-y-3">
          {mine.map((row) => (
            <li key={row.symbol} className="glass flex flex-wrap items-center gap-4 p-4 sm:p-5">
              <Link href={`/markets/${row.symbol}?tf=1h`} className="w-32">
                <p className="font-display text-lg font-bold">{row.symbol}</p>
                <p className="text-sm text-muted">{row.name}</p>
              </Link>
              <div className="w-36 font-mono">
                <p>{row.last_price ? formatPrice(row.last_price) : "n/a"}</p>
                <p className="text-sm text-muted">{formatChange(row.change_24h_pct)} 24h</p>
              </div>
              <div className="flex flex-1 flex-wrap gap-2">
                {TIMEFRAMES.map((tf) => {
                  const chip = row.signals[tf];
                  if (!chip) return null;
                  const direction = asDirection(chip.label);
                  return (
                    <span key={tf} className={`tile flex items-center gap-1.5 px-3 py-2 text-xs font-semibold ${DIRECTION_TEXT[direction]}`}>
                      <span className="font-mono text-muted">{tf}</span>
                      <DirectionIcon direction={direction} size={14} />
                      {direction === "neutral" ? "Neutral" : direction === "up" ? "Up" : "Down"}
                      <span className="font-mono">{formatProbability(shownProbability(direction, chip.p_up))}</span>
                    </span>
                  );
                })}
              </div>
              <button
                type="button"
                onClick={() => toggle.mutate({ symbol: row.symbol, add: false })}
                disabled={toggle.isPending}
                className="key px-3 py-2 text-sm"
                aria-label={`Remove ${row.name} from watchlist`}
              >
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
      {others.length > 0 && (
        <section aria-labelledby="add" className="space-y-3">
          <h2 id="add" className="font-display text-lg font-semibold">Add a coin</h2>
          <div className="flex flex-wrap gap-2">
            {others.map((row) => (
              <button
                key={row.symbol}
                type="button"
                onClick={() => toggle.mutate({ symbol: row.symbol, add: true })}
                disabled={toggle.isPending}
                className="key flex items-center gap-2 px-4 py-2 text-sm font-semibold"
              >
                <Star aria-hidden size={14} /> {row.symbol}
              </button>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
