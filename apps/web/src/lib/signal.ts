import type { Timeframe } from "./api/client";
import { formatPrice, formatProbability, timeframeWords } from "./format";

// Display only: the backend decides the label. These match NEUTRAL_LOW/HIGH in
// backend/app/ml/config.py and are used to draw the neutral zone on the meter.
export const NEUTRAL_LOW = 0.45;
export const NEUTRAL_HIGH = 0.55;

export type Direction = "up" | "down" | "neutral";

export function asDirection(label: string): Direction {
  return label === "up" || label === "down" ? label : "neutral";
}

/** The number shown on the orb: P(up) for Up and Neutral, P(down) for Down (docs/08). */
export function shownProbability(direction: Direction, pUp: number): number {
  return direction === "down" ? 1 - pUp : pUp;
}

export const WORD: Record<Direction, string> = { up: "UP", down: "DOWN", neutral: "NEUTRAL" };

export const HEADLINE: Record<Direction, string> = {
  up: "Buyers have the edge",
  down: "Sellers have the edge",
  neutral: "Too close to call",
};

/** The one plain-language sentence under the headline (docs/08 item 4). */
export function plainSentence(
  direction: Direction,
  pUp: number,
  tf: Timeframe,
  baseClose: string,
): string {
  const up = formatProbability(pUp);
  const down = formatProbability(1 - pUp);
  const price = formatPrice(baseClose);
  const candle = `the next ${timeframeWords(tf)} candle`;
  if (direction === "up")
    return `${up} chance ${candle} closes higher than ${price}. That leaves ${down} that it does not.`;
  if (direction === "down")
    return `${down} chance ${candle} closes lower than ${price}. That leaves ${up} that it does not.`;
  return `Up ${up} versus down ${down}. When the odds are this close we make no call and show Neutral.`;
}

/** One sentence a screen reader can read for the whole signal (docs/08 accessibility). */
export function screenReaderSummary(coin: string, tf: Timeframe, label: string, pUp: number) {
  const direction = asDirection(label);
  const percent = (shownProbability(direction, pUp) * 100).toFixed(1);
  return `${coin}, next ${timeframeWords(tf)} candle: ${WORD[direction].toLowerCase()}, ${percent} percent chance. Neutral zone is 45 to 55 percent.`;
}

/** The "How reliable is it?" sentence. Honest whatever the result (docs/06). */
export function reliabilitySentence(
  model: number | null | undefined,
  naive: number | null | undefined,
  n: number,
  lowSample: boolean,
): string {
  if (n === 0 || naive == null)
    return "Not enough finished signals yet to measure reliability. Check back after more candles close.";
  if (model == null)
    // Signals finished, but none of them was an Up or Down call.
    return `All ${n} recent signals were Neutral (too close to call), so there are no Up or Down calls to score yet. Staying Neutral is the honest answer when the odds are close.`;
  const points = (model - naive) * 100;
  const sample = lowSample ? ` Only ${n} finished signals so far, so this can still change a lot.` : "";
  if (points > 0)
    return `The model beat the baseline by ${points.toFixed(1)} points. That is a small edge, which is normal for crypto.${sample}`;
  return `The model did not beat the simple baseline (${Math.abs(points).toFixed(1)} points behind). Treat its signals with caution.${sample}`;
}

export const DEGRADED_WARNING =
  "This model is performing below the baseline right now. Treat the signal with extra caution.";
export const STALE_WARNING = "Data is delayed. Signals may be out of date.";
