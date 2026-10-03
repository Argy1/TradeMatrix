"use client";

import { AlertTriangle, ChevronRight } from "lucide-react";
import Link from "next/link";

import { TIMEFRAMES } from "@/lib/api/client";
import { useMarkets, usePerformance } from "@/lib/api/hooks";
import { formatChange, formatPrice, formatProbability } from "@/lib/format";
import { type Direction, asDirection, shownProbability } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon } from "./direction";
import { ErrorState, Skeleton } from "./states";

const CHIP: Record<Direction, { word: string; bg: string; border: string }> = {
  up: { word: "Up", bg: "rgba(46,230,166,.10)", border: "rgba(46,230,166,.4)" },
  down: { word: "Down", bg: "rgba(255,92,122,.10)", border: "rgba(255,92,122,.4)" },
  neutral: { word: "Neutral", bg: "rgba(255,200,87,.10)", border: "rgba(255,200,87,.4)" },
};

export function MarketList() {
  const markets = useMarkets();
  if (markets.isPending) return <Skeleton className="h-96" />;
  if (markets.isError)
    return <ErrorState message="Could not load the markets." onRetry={() => markets.refetch()} />;
  return (
    <div className="glass overflow-hidden">
      <ul>
        {markets.data.map((row, index) => (
          <li key={row.symbol} className={index ? "border-t border-white/8" : ""}>
            <Link
              href={`/markets/${row.symbol}?tf=1h`}
              className="flex flex-wrap items-center gap-x-5 gap-y-3.5 px-6 py-4.5 hover:bg-white/5"
            >
              <span className="flex min-w-0 flex-[1_1_190px] items-center gap-3.5">
                <span className="tile grid h-[60px] w-14 shrink-0 place-items-center font-display text-[15px] font-extrabold">
                  {row.symbol}
                </span>
                <span className="flex flex-col leading-snug">
                  <span className="text-[17px] font-bold">{row.name}</span>
                  <span className="text-[13px] text-muted">{row.symbol} / USDT</span>
                </span>
              </span>
              <span className="flex flex-[1_1_140px] flex-col leading-snug">
                <span className="font-mono text-lg font-bold">
                  {row.last_price ? formatPrice(row.last_price) : "n/a"}
                </span>
                <span
                  className={`font-mono text-sm font-bold ${(row.change_24h_pct ?? 0) >= 0 ? "text-up" : "text-down-fg"}`}
                >
                  {formatChange(row.change_24h_pct)} <span className="font-sans font-normal text-muted">24h</span>
                </span>
              </span>
              <span className="flex flex-[3_1_420px] flex-wrap gap-2.5">
                {TIMEFRAMES.map((tf) => {
                  const chip = row.signals[tf];
                  if (!chip)
                    return (
                      <span key={tf} className="flex min-h-12 flex-[1_1_120px] items-center rounded-[14px] border border-white/10 px-3 text-xs text-muted">
                        {tf}: no signal
                      </span>
                    );
                  const direction = asDirection(chip.label);
                  const style = CHIP[direction];
                  const degraded = chip.model_status === "degraded";
                  return (
                    <span
                      key={tf}
                      className="flex min-h-12 flex-[1_1_120px] items-center gap-2 rounded-[14px] border px-3 py-1.5 shadow-[0_3px_0_rgba(0,0,0,.4)]"
                      style={{ background: style.bg, borderColor: style.border }}
                    >
                      <span className="w-6 text-xs font-bold text-muted">{tf}</span>
                      <span className={DIRECTION_TEXT[direction]}>
                        <DirectionIcon direction={direction} size={18} />
                      </span>
                      <span className="flex flex-col leading-tight">
                        <span className={`text-sm font-bold ${DIRECTION_TEXT[direction]}`}>{style.word}</span>
                        <span className="font-mono text-[13px] text-fg-2">
                          {formatProbability(shownProbability(direction, chip.p_up))}
                        </span>
                      </span>
                      {degraded && (
                        <AlertTriangle
                          size={14}
                          className="ml-auto text-neutral"
                          aria-label="Model below the baseline: extra caution"
                        />
                      )}
                    </span>
                  );
                })}
              </span>
              <span className="inline-flex items-center gap-1.5 text-[15px] font-bold text-[#7BE8FF]">
                Open <ChevronRight aria-hidden size={18} />
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export function TrackStrip() {
  const perf = usePerformance({ days: 30 });
  const data = perf.data;
  const tiles = [
    { label: "Signals recorded", value: data ? String(data.n_predictions) : "…", tone: "" },
    {
      label: "Accuracy, last 30 days",
      value: data?.accuracy != null ? formatProbability(data.accuracy) : "not enough data",
      tone: "text-[#7BE8FF]",
    },
    {
      label: "Simple baseline",
      value: data?.baseline.naive != null ? formatProbability(data.baseline.naive) : "not enough data",
      tone: "text-[#B4C0DC]",
    },
  ];
  return (
    <section aria-labelledby="track" className="glass flex flex-wrap items-center gap-6 p-7">
      <div className="flex-[1_1_320px]">
        <h2 id="track" className="font-display text-[26px] font-bold">
          We show our results, even when they are poor
        </h2>
        <p className="mt-2.5 text-[15px] leading-relaxed text-[#B4C0DC]">
          Every signal is saved and checked when its candle closes. Accuracy is always shown next to
          a simple baseline so you can judge the edge yourself.
        </p>
        {data?.low_sample && (
          <p className="mt-2 text-sm text-neutral">
            Only {data.n_resolved} signals have finished so far, so these numbers can still change a lot.
          </p>
        )}
        <Link href="/track-record" className="mt-3 inline-block text-sm text-cyan underline-offset-4 hover:underline">
          See the full track record
        </Link>
      </div>
      <div className="flex flex-[2_1_520px] flex-wrap gap-4">
        {tiles.map((tile) => (
          <div
            key={tile.label}
            className="flex-[1_1_150px] rounded-[18px] bg-white/5 p-4 shadow-[inset_0_1px_0_rgba(255,255,255,.1),0_4px_0_rgba(0,0,0,.35)]"
          >
            <p className="text-[13px] font-semibold text-muted">{tile.label}</p>
            <p className={`mt-1 font-mono text-[28px] font-bold ${tile.tone}`}>{tile.value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
