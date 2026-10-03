import { describe, expect, it } from "vitest";

import type { Candle } from "./client";
import { mergeCandle } from "./live";

const bar = (t: string, c: string): Candle => ({
  t, o: "100", h: "110", l: "90", c, v: "1",
  ema9: 1, ema21: 2, ema50: 3, bb_upper: 4, bb_mid: 5, bb_lower: 6,
  rsi14: 50, macd: 0.1, macd_signal: 0.2, macd_hist: -0.1,
}); // prettier-ignore

const live = (t: string, c: string) => ({ t, o: "100", h: "120", l: "95", c, v: "2", closed: false });

describe("mergeCandle", () => {
  const history = [bar("2026-10-03T00:00:00Z", "101"), bar("2026-10-03T01:00:00Z", "102")];

  it("updates the forming candle in place", () => {
    const merged = mergeCandle(history, live("2026-10-03T01:00:00Z", "105"));
    expect(merged).toHaveLength(2);
    expect(merged[1].c).toBe("105");
    expect(merged[1].ema9).toBe(1); // keeps the last known indicator values
  });

  it("appends a new candle without indicators", () => {
    const merged = mergeCandle(history, live("2026-10-03T02:00:00Z", "103"));
    expect(merged).toHaveLength(3);
    expect(merged[2]).toMatchObject({ c: "103", ema9: null, rsi14: null });
  });

  it("ignores a late message for an older candle", () => {
    expect(mergeCandle(history, live("2026-10-02T23:00:00Z", "99"))).toBe(history);
  });
});
