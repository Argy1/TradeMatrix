import type { Timeframe } from "./api/client";

// Data is UTC everywhere; only the UI converts to the user's zone (default WIB). CLAUDE.md.
export const DISPLAY_TIME_ZONE = "Asia/Jakarta";
export const DISPLAY_ZONE_LABEL = "WIB";

const TF_WORDS: Record<Timeframe, string> = { "1h": "1 hour", "4h": "4 hour", "1d": "1 day" };

/** "1 hour" / "4 hour" / "1 day", as used in "the next 1 hour candle". */
export function timeframeWords(tf: Timeframe): string {
  return TF_WORDS[tf];
}

/** Prices arrive as exact strings; show thousands separators without float rounding. */
export function formatPrice(value: string, { dollar = true } = {}): string {
  const [whole, fraction] = value.split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  const decimals = fraction ? fraction.padEnd(2, "0") : "00";
  return `${dollar ? "$" : ""}${grouped}.${decimals}`;
}

/** 0.582 -> "58.2%" (one decimal, docs/01). */
export function formatProbability(p: number): string {
  return `${(p * 100).toFixed(1)}%`;
}

export function formatChange(pct: number | null | undefined): string {
  if (pct === null || pct === undefined) return "n/a";
  return `${pct > 0 ? "+" : ""}${pct.toFixed(2)}%`;
}

/** "22:00 WIB" */
export function formatClock(iso: string): string {
  const time = new Intl.DateTimeFormat("en-GB", {
    timeZone: DISPLAY_TIME_ZONE,
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).format(new Date(iso));
  return `${time} ${DISPLAY_ZONE_LABEL}`;
}

/** "3 Oct, 22:00 WIB" */
export function formatDateTime(iso: string): string {
  const date = new Intl.DateTimeFormat("en-GB", {
    timeZone: DISPLAY_TIME_ZONE,
    day: "numeric",
    month: "short",
  }).format(new Date(iso));
  return `${date}, ${formatClock(iso)}`;
}

/** "in 41 min" / "in 2 h 5 min" / "now" */
export function formatCountdown(targetIso: string, now: Date = new Date()): string {
  const minutes = Math.round((new Date(targetIso).getTime() - now.getTime()) / 60_000);
  if (minutes <= 0) return "now";
  if (minutes < 60) return `in ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  const rest = minutes % 60;
  return rest ? `in ${hours} h ${rest} min` : `in ${hours} h`;
}
