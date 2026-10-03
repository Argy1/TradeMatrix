"use client";

import Link from "next/link";

import { TIMEFRAMES } from "@/lib/api/client";
import { useMarkets, usePerformance } from "@/lib/api/hooks";
import { formatChange, formatPrice, formatProbability } from "@/lib/format";
import { asDirection, shownProbability } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon } from "./direction";
import { ErrorState, Skeleton } from "./states";

export function MarketList() {
  const markets = useMarkets();
  if (markets.isPending) return <Skeleton className="h-80" />;
  if (markets.isError)
    return <ErrorState message="Could not load the markets." onRetry={() => markets.refetch()} />;
  return (
    <ul className="space-y-3">
      {markets.data.map((row) => (
        <li key={row.symbol}>
          <Link
            href={`/markets/${row.symbol}?tf=1h`}
            className="glass flex flex-wrap items-center gap-4 p-4 hover:border-cyan/40 sm:p-5"
          >
            <div className="w-32">
              <p className="font-display text-lg font-bold">{row.symbol}</p>
              <p className="text-sm text-muted">{row.name}</p>
            </div>
            <div className="w-36 font-mono">
              <p>{row.last_price ? formatPrice(row.last_price) : "n/a"}</p>
              <p className={`text-sm ${(row.change_24h_pct ?? 0) >= 0 ? "text-up" : "text-down-fg"}`}>
                {formatChange(row.change_24h_pct)} <span className="text-muted">24h</span>
              </p>
            </div>
            <div className="flex flex-1 flex-wrap justify-end gap-2">
              {TIMEFRAMES.map((tf) => {
                const chip = row.signals[tf];
                if (!chip)
                  return (
                    <span key={tf} className="tile px-3 py-2 text-xs text-muted">
                      {tf}: no signal
                    </span>
                  );
                const direction = asDirection(chip.label);
                return (
                  <span
                    key={tf}
                    className={`tile flex items-center gap-1.5 px-3 py-2 text-xs font-semibold ${DIRECTION_TEXT[direction]}`}
                    title={chip.model_status === "degraded" ? "Model below baseline: extra caution" : undefined}
                  >
                    <span className="font-mono text-muted">{tf}</span>
                    <DirectionIcon direction={direction} size={14} />
                    {direction === "neutral" ? "Neutral" : direction === "up" ? "Up" : "Down"}
                    <span className="font-mono">{formatProbability(shownProbability(direction, chip.p_up))}</span>
                    {chip.model_status === "degraded" && <span aria-label="model below baseline" className="text-neutral">*</span>}
                  </span>
                );
              })}
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

export function TrackStrip() {
  const perf = usePerformance({ days: 30 });
  const data = perf.data;
  const tiles = [
    { label: "Signals recorded (30 days)", value: data ? String(data.n_predictions) : "…" },
    {
      label: "Model accuracy on Up/Down calls",
      value: data?.accuracy != null ? formatProbability(data.accuracy) : "not enough data yet",
    },
    {
      label: 'Simple baseline ("repeat the last move")',
      value: data?.baseline.naive != null ? formatProbability(data.baseline.naive) : "not enough data yet",
    },
  ];
  return (
    <section aria-labelledby="track" className="space-y-4">
      <h2 id="track" className="font-display text-2xl font-bold">
        We show our results, even when they are poor
      </h2>
      <div className="grid gap-4 sm:grid-cols-3">
        {tiles.map((tile) => (
          <div key={tile.label} className="tile p-5">
            <p className="text-sm text-muted">{tile.label}</p>
            <p className="mt-2 font-mono text-2xl font-semibold">{tile.value}</p>
          </div>
        ))}
      </div>
      {data?.low_sample && (
        <p className="text-sm text-neutral">
          Few signals have finished so far ({data.n_resolved}), so these numbers can still change a lot.
        </p>
      )}
      <Link href="/track-record" className="inline-block text-sm text-cyan underline-offset-4 hover:underline">
        See the full track record
      </Link>
    </section>
  );
}
