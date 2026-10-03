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

export const EFFECT_TAG: Record<string, string> = {
  up: "Pushes up",
  down: "Pushes down",
  none: "No clear push",
};
