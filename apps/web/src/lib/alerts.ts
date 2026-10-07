import type { components } from "./api/schema";
import { formatPrice } from "./format";

export type Alert = components["schemas"]["AlertOut"];
export type AlertInput = components["schemas"]["AlertIn"];
export type AlertType = AlertInput["type"];
export type AppNotification = components["schemas"]["NotificationOut"];

// Display only. The API decides which combinations are valid and what fires when.
export const SIGNAL_TYPES: AlertType[] = ["signal_change", "prob_above", "prob_below"];

export function isSignalType(type: string): boolean {
  return (SIGNAL_TYPES as string[]).includes(type);
}

/** What the person picks in the "Tell me when" list, in plain words. */
export const TYPE_OPTIONS: { type: AlertType; label: string }[] = [
  { type: "signal_change", label: "The signal changes (Up, Down or Neutral)" },
  { type: "prob_above", label: "The chance of Up is at or above a level" },
  { type: "prob_below", label: "The chance of Up is at or below a level" },
  { type: "price_above", label: "The price crosses above a level" },
  { type: "price_below", label: "The price crosses below a level" },
];

/** 60 -> "1 hour", 240 -> "4 hours", 1440 -> "1 day", 15 -> "15 minutes" */
export function cooldownWords(minutes: number): string {
  const plural = (n: number, word: string) => `${n} ${word}${n === 1 ? "" : "s"}`;
  if (minutes % 1440 === 0) return plural(minutes / 1440, "day");
  if (minutes % 60 === 0) return plural(minutes / 60, "hour");
  return plural(minutes, "minute");
}

/** "0.6" -> "60%" (thresholds of probability rules travel as 0..1 strings) */
function percent(threshold: string | null | undefined): string {
  return `${Math.round(Number(threshold ?? 0) * 1000) / 10}%`;
}

/** One plain sentence for a rule, e.g. "When the BTC 1h signal changes". */
export function ruleSentence(alert: Pick<Alert, "symbol" | "type" | "timeframe" | "threshold">): string {
  const { symbol, timeframe: tf, threshold } = alert;
  switch (alert.type) {
    case "signal_change":
      return `When the ${symbol} ${tf} signal changes`;
    case "prob_above":
      return `When the ${symbol} ${tf} chance of Up is ${percent(threshold)} or more`;
    case "prob_below":
      return `When the ${symbol} ${tf} chance of Up is ${percent(threshold)} or less`;
    case "price_above":
      return `When the ${symbol} price crosses above ${formatPrice(threshold ?? "0")}`;
    case "price_below":
      return `When the ${symbol} price crosses below ${formatPrice(threshold ?? "0")}`;
    default:
      return `${symbol} alert`;
  }
}

/** Turn what was typed into the threshold the API expects, or explain what is wrong. */
export function parseThreshold(
  type: AlertType,
  typed: string,
): { threshold: string | null; error?: string } {
  if (type === "signal_change") return { threshold: null };
  const text = typed.trim().replace(/,/g, "");
  if (!/^\d+(\.\d+)?$/.test(text)) return { threshold: null, error: "Enter a number." };
  if (isSignalType(type)) {
    const value = Number(text);
    if (value <= 0 || value >= 100)
      return { threshold: null, error: "Enter a percentage between 1 and 99." };
    return { threshold: (value / 100).toFixed(4) }; // 60 (%) -> "0.6000"
  }
  if (Number(text) <= 0) return { threshold: null, error: "Enter a price above 0." };
  return { threshold: text }; // prices stay exact strings
}
