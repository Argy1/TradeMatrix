"use client";

import Link from "next/link";

import { FAST_TIMEFRAMES, SLOW_TIMEFRAMES, type Timeframe } from "@/lib/api/client";
import { timeframeWords } from "@/lib/format";

/**
 * The candle-size keys (docs/08): the fast sizes, a thin divider, the slow sizes. One row that
 * scrolls sideways on a phone. With `hrefFor` each key is a link (the coin page, where the
 * size is part of the address); with `onPick` it is a button (lists that only change what
 * they show).
 */
export function SizeSwitch({
  value,
  hrefFor,
  onPick,
}: {
  value: Timeframe;
  hrefFor?: (tf: Timeframe) => string;
  onPick?: (tf: Timeframe) => void;
}) {
  const key = (tf: Timeframe) => {
    const className = "key shrink-0 px-4 py-3 font-mono text-sm font-semibold";
    const label = `${timeframeWords(tf)} candles`;
    return hrefFor ? (
      <Link
        key={tf}
        href={hrefFor(tf)}
        aria-current={tf === value ? "page" : undefined}
        aria-label={label}
        className={className}
      >
        {tf}
      </Link>
    ) : (
      <button
        key={tf}
        type="button"
        aria-pressed={tf === value}
        aria-label={label}
        onClick={() => onPick?.(tf)}
        className={className}
      >
        {tf}
      </button>
    );
  };
  return (
    <nav
      aria-label="Candle size"
      className="-mx-1 flex max-w-full items-center gap-2 overflow-x-auto px-1 pb-2"
    >
      {FAST_TIMEFRAMES.map(key)}
      <span aria-hidden className="mx-1 h-7 w-px shrink-0 bg-white/20" />
      {SLOW_TIMEFRAMES.map(key)}
    </nav>
  );
}
