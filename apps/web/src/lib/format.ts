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
  const [whole, fraction = ""] = value.split(".");
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  // Exchanges send "84536.00000000": drop trailing zeros but keep at least 2 decimals.
  const decimals = fraction.replace(/0+$/, "").padEnd(2, "0");
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

/** "just now" / "12 min ago" / "3 h ago" / "2 d ago" */
export function formatAgo(iso: string, now: Date = new Date()): string {
  const minutes = Math.floor((now.getTime() - new Date(iso).getTime()) / 60_000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  return `${Math.floor(hours / 24)} d ago`;
}

/** A sentiment score always shows its sign: 0.31 -> "+0.31", -0.2 -> "-0.20". */
export function formatScore(score: number): string {
  const rounded = Number(score.toFixed(2)); // -0.004 becomes 0, so it never prints "-0.00"
  return `${rounded >= 0 ? "+" : "-"}${Math.abs(rounded).toFixed(2)}`;
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
