"use client";

import { useState } from "react";

import { TIMEFRAMES, type Timeframe } from "@/lib/api/client";
import { useMarkets, usePerformance } from "@/lib/api/hooks";
import { formatProbability } from "@/lib/format";

import { Skeleton } from "./states";

const pct = (value: number | null | undefined) => (value == null ? "n/a" : formatProbability(value));

function Row({ symbol, tf, days }: { symbol: string; tf: Timeframe; days: number }) {
  const { data, isPending } = usePerformance({ symbol, tf, days });
  if (isPending || !data)
    return (
      <tr>
        <td colSpan={8} className="py-2"><Skeleton className="h-6" /></td>
      </tr>
    );
  const beats = data.accuracy != null && data.baseline.naive != null && data.accuracy > data.baseline.naive;
  return (
    <tr className="border-t border-white/5">
      <th scope="row" className="py-3 pr-4 text-left font-semibold">{symbol} <span className="font-mono text-muted">{tf}</span></th>
      <td className="font-mono">{data.n_resolved}</td>
      <td className="font-mono">{pct(data.coverage)}</td>
      <td className={`font-mono ${beats ? "text-up" : ""}`}>{pct(data.accuracy)}</td>
      <td className="font-mono">{pct(data.baseline.naive)}</td>
      <td className="font-mono">{pct(data.baseline.always_up)}</td>
      <td className="font-mono">{data.brier?.toFixed(4) ?? "n/a"} <span className="text-muted">/ {data.brier_baseline?.toFixed(4) ?? "n/a"}</span></td>
      <td>{data.low_sample ? <span className="text-neutral">low sample</span> : <span className="text-muted">ok</span>}</td>
    </tr>
  );
}

export function TrackRecord() {
  const [days, setDays] = useState(30);
  const markets = useMarkets();
  const overall = usePerformance({ days });
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Period">
        {[30, 90].map((option) => (
          <button key={option} type="button" aria-pressed={days === option} onClick={() => setDays(option)} className="key px-4 py-2 font-mono text-sm font-semibold">
            Last {option} days
          </button>
        ))}
      </div>
      {overall.data && (
        <div className="grid gap-4 sm:grid-cols-4">
          {[
            ["Signals recorded", String(overall.data.n_predictions)],
            ["Finished signals", String(overall.data.n_resolved)],
            ["Model accuracy (Up/Down calls)", pct(overall.data.accuracy)],
            ['Baseline "repeat the last move"', pct(overall.data.baseline.naive)],
          ].map(([label, value]) => (
            <div key={label} className="tile p-5">
              <p className="text-sm text-muted">{label}</p>
              <p className="mt-2 font-mono text-2xl font-semibold">{value}</p>
            </div>
          ))}
        </div>
      )}
      {overall.data?.low_sample && (
        <p className="text-sm text-neutral">
          Only {overall.data.n_resolved} signals have finished in this period. Numbers from small samples can swing a lot; give it time.
        </p>
      )}
      <div className="glass overflow-x-auto p-4 sm:p-6">
        <table className="w-full min-w-[760px] text-sm">
          <caption className="mb-3 text-left text-muted">
            Live results per coin and candle size. Accuracy counts only Up/Down calls; coverage is the share of candles where the model made a call.
          </caption>
          <thead className="text-left text-xs uppercase tracking-wider text-muted">
            <tr>
              <th scope="col" className="pb-2">Signal</th>
              <th scope="col">Finished</th>
              <th scope="col">Coverage</th>
              <th scope="col">Accuracy</th>
              <th scope="col">Naive</th>
              <th scope="col">Always up</th>
              <th scope="col">Brier / base</th>
              <th scope="col">Sample</th>
            </tr>
          </thead>
          <tbody>
            {(markets.data ?? []).flatMap((row) =>
              TIMEFRAMES.map((tf) => <Row key={row.symbol + tf} symbol={row.symbol} tf={tf} days={days} />),
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
