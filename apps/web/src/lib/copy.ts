// Fixed copy. The disclaimer text comes from docs/06 and may only change with Argy's approval.
export const DISCLAIMER =
  "Signals are probabilistic estimates for information and education only, not financial advice. Crypto is volatile and you can lose all the money you invest. Past performance does not guarantee future results. TradeMatrix AI does not execute trades.";

export const DISCLAIMER_SHORT = "Not financial advice. Estimates only.";

/** One plain sentence per reason code, so jargon is explained the first time (docs/08). */
export const REASON_EXPLAINERS: Record<string, string> = {
  rsi: "RSI measures recent momentum on a 0 to 100 scale; above 70 or below 30 is stretched.",
  ema_trend: "EMA 50 is the average price of the last 50 candles, a simple view of the trend.",
  ema_cross: "When the fast average (EMA 9) crosses the slower one (EMA 21), momentum is turning.",
  macd: "MACD compares a fast and a slow trend; a positive histogram means momentum is rising.",
  volume: "Unusual volume means more traders than normal are active right now.",
  bollinger: "Bollinger Bands mark the usual price range; outside them, moves are stretched.",
  momentum: "How far the price moved over the last 24 candles.",
  sentiment: "The average tone of recent news headlines about this coin.",
};

// News section. Which of the two sentences is shown comes from the API (`sentiment_used`),
// so the page never claims news is part of the signal while it is only being recorded.
export const NEWS_SCALE =
  "Each badge is an automated reading of the headline, from -1 (bearish) to +1 (bullish).";
export const NEWS_CONTEXT_ONLY =
  "For now news is context only: it does not change the signal's probability.";
export const NEWS_BLENDED = "News tone is one of the inputs of the signal, with a small weight.";
export const NEWS_FOOTNOTE =
  "Headlines link to the original publishers. The tone rating is made by an AI model and can be wrong.";

export const EFFECT_TAG: Record<string, string> = {
  up: "Pushes up",
  down: "Pushes down",
  none: "No clear push",
};
