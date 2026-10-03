"use client";

import { X } from "lucide-react";
import Link from "next/link";
import { useSyncExternalStore } from "react";

import { ApiError, type HistoryItem, TIMEFRAMES, type Timeframe } from "@/lib/api/client";
import { useCandles, useHistory, useLatestPrediction, useMarkets } from "@/lib/api/hooks";
import { DISCLAIMER_SHORT } from "@/lib/copy";
import { formatDateTime, timeframeWords } from "@/lib/format";
import { asDirection } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon, DirectionLabel } from "./direction";
import { PriceChart } from "./price-chart";
import { SignalCard } from "./signal-card";
import { ErrorState, Skeleton } from "./states";

const GUIDE_KEY = "tm-guide-hidden";
const GUIDE_EVENT = "tm-guide-change";
// Fallback when browser storage is blocked (private mode): remember for this page visit only.
let guideMemory: boolean | null = null;

function readGuideHidden(): boolean {
  if (guideMemory !== null) return guideMemory;
  try {
    return localStorage.getItem(GUIDE_KEY) === "1";
  } catch {
    return false;
  }
}

function subscribeGuide(onChange: () => void) {
  window.addEventListener(GUIDE_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(GUIDE_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

function GuideStrip() {
  // The server cannot see this browser's choice, so it renders the guide hidden; the browser
  // then shows it if the person has not dismissed it before (no hydration mismatch).
  const hidden = useSyncExternalStore(subscribeGuide, readGuideHidden, () => true);
  const remember = (value: boolean) => {
    guideMemory = value;
    try {
      localStorage.setItem(GUIDE_KEY, value ? "1" : "0");
    } catch {}
    window.dispatchEvent(new Event(GUIDE_EVENT));
  };
  if (hidden)
    return (
      <button type="button" onClick={() => remember(false)} className="text-sm text-cyan underline-offset-4 hover:underline">
        Show the 3-step guide
      </button>
    );
  const steps = [
    ["Direction", "Up, Down or Neutral for the next candle. Neutral means too close to call."],
    ["Chance", "How likely that direction is. 58% is a lean, not a promise."],
    ["Reliability", "How the model did on recent candles, next to a simple baseline."],
  ];
  return (
    <section aria-label="How to read a signal" className="glass relative grid gap-4 p-5 md:grid-cols-3">
      <button
        type="button"
        onClick={() => remember(true)}
        aria-label="Hide the guide"
        className="absolute right-3 top-3 rounded-lg p-1 text-muted hover:text-fg"
      >
        <X size={18} aria-hidden />
      </button>
      {steps.map(([title, text], index) => (
        <div key={title} className="flex gap-3 pr-6">
          <span className="key grid h-8 w-8 shrink-0 place-items-center font-display font-bold">
            {index + 1}
          </span>
          <div>
            <p className="font-semibold">{title}</p>
            <p className="text-sm text-muted">{text}</p>
          </div>
        </div>
      ))}
    </section>
  );
}

function RecentSignals({ items }: { items: HistoryItem[] }) {
  const resolved = items.filter((item) => item.outcome);
  if (resolved.length === 0)
    return <p className="text-sm text-muted">No finished signals yet. They appear after each candle closes.</p>;
  const calls = resolved.filter((item) => item.outcome?.correct !== null);
  const hits = calls.filter((item) => item.outcome?.correct).length;
  const skipped = resolved.length - calls.length;
  return (
    <div>
      <ul className="flex flex-wrap gap-2">
        {resolved.map((item) => {
          const direction = asDirection(item.label);
          const result = item.outcome?.correct === null ? "Skip" : item.outcome?.correct ? "Hit" : "Miss";
          return (
            <li
              key={item.target_open_time}
              title={`${formatDateTime(item.target_open_time)}: called ${direction}, went ${item.outcome?.actual_direction}`}
              className={`key flex h-[76px] w-[68px] flex-col items-center justify-center gap-1 text-xs font-semibold ${DIRECTION_TEXT[direction]}`}
            >
              <DirectionIcon direction={direction} size={18} />
              <span className="text-fg">{result}</span>
            </li>
          );
        })}
      </ul>
      <p className="mt-3 text-sm text-fg-2">
        {hits} of {calls.length} calls correct{skipped ? `, ${skipped} skipped as Neutral` : ""}.
      </p>
    </div>
  );
}

export function CoinView({ symbol, tf }: { symbol: string; tf: Timeframe }) {
  const markets = useMarkets();
  const prediction = useLatestPrediction(symbol, tf);
  const candles = useCandles(symbol, tf, 200);
  const history = useHistory(symbol, tf, 12);
  const coin = markets.data?.find((row) => row.symbol === symbol);
  const name = coin?.name ?? symbol;

  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="font-display text-3xl font-bold sm:text-5xl">
          Will {name} rise or fall in the next {tf}?
        </h1>
        <p className="mt-2 text-fg-2">
          A probability for the next {timeframeWords(tf)} candle, the reasons behind it, and how
          reliable it has been. {DISCLAIMER_SHORT}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-3">
        <nav aria-label="Coin" className="flex flex-wrap gap-2">
          {(markets.data ?? []).map((row) => {
            const chip = row.signals[tf];
            const direction = asDirection(chip?.label ?? "neutral");
            return (
              <Link
                key={row.symbol}
                href={`/markets/${row.symbol}?tf=${tf}`}
                aria-current={row.symbol === symbol ? "page" : undefined}
                className="key flex flex-col px-4 py-2 text-left"
              >
                <span className="font-display font-bold">{row.symbol}</span>
                {chip ? <DirectionLabel direction={direction} size={12} /> : <span className="text-xs text-muted">no signal</span>}
              </Link>
            );
          })}
        </nav>
        <nav aria-label="Candle size" className="ml-auto flex gap-2">
          {TIMEFRAMES.map((option) => (
            <Link
              key={option}
              href={`/markets/${symbol}?tf=${option}`}
              aria-current={option === tf ? "page" : undefined}
              className="key px-4 py-3 font-mono text-sm font-semibold"
            >
              {option}
            </Link>
          ))}
        </nav>
      </div>

      <GuideStrip />

      <div className="grid gap-6 min-[1050px]:grid-cols-[minmax(0,1fr)_420px]">
        {/* On phones the signal card comes first (docs/08). */}
        <div className="order-1 min-[1050px]:order-2">
          {prediction.isPending ? (
            <Skeleton className="h-[720px]" />
          ) : prediction.isError ? (
            <ErrorState
              message={
                prediction.error instanceof ApiError && prediction.error.status === 404
                  ? "No signal yet for this coin and candle size. The first one appears after the next candle closes."
                  : "Could not load the signal. Last known data is kept when available."
              }
              onRetry={() => prediction.refetch()}
            />
          ) : (
            <SignalCard prediction={prediction.data} coinName={name} />
          )}
        </div>

        <div className="order-2 space-y-6 min-[1050px]:order-1">
          <section aria-label="Chart" className="glass p-4 sm:p-6">
            {candles.isPending ? (
              <Skeleton className="h-[380px]" />
            ) : candles.isError ? (
              <ErrorState message="Could not load the chart." onRetry={() => candles.refetch()} />
            ) : (
              <>
                {candles.data.stale && <p className="mb-3 text-sm text-neutral">Data is delayed. Signals may be out of date.</p>}
                <PriceChart candles={candles.data.candles} />
              </>
            )}
          </section>

          <section aria-labelledby="recent" className="glass space-y-4 p-6">
            <h2 id="recent" className="font-display text-lg font-semibold">Recent signals</h2>
            {history.data ? <RecentSignals items={history.data.items} /> : <Skeleton className="h-24" />}
          </section>

          <section aria-labelledby="news" className="glass space-y-2 p-6">
            <h2 id="news" className="font-display text-lg font-semibold">News</h2>
            <p className="text-sm text-muted">Headlines with a sentiment badge arrive in the next update.</p>
          </section>
        </div>
      </div>
    </div>
  );
}
