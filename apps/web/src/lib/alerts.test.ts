import { describe, expect, it } from "vitest";

import { cooldownWords, parseThreshold, ruleSentence } from "./alerts";

describe("alert wording", () => {
  it("describes each kind of rule in one plain sentence", () => {
    const base = { symbol: "BTC", timeframe: "1h", threshold: null };
    expect(ruleSentence({ ...base, type: "signal_change" })).toBe("When the BTC 1h signal changes");
    expect(ruleSentence({ ...base, type: "prob_above", threshold: "0.6" })).toBe(
      "When the BTC 1h chance of Up is 60% or more",
    );
    expect(ruleSentence({ ...base, type: "prob_below", threshold: "0.425" })).toBe(
      "When the BTC 1h chance of Up is 42.5% or less",
    );
    expect(
      ruleSentence({ symbol: "BTC", timeframe: null, type: "price_above", threshold: "85000.5" }),
    ).toBe("When the BTC price crosses above $85,000.50");
    expect(
      ruleSentence({ symbol: "XLM", timeframe: null, type: "price_below", threshold: "0.2" }),
    ).toBe("When the XLM price crosses below $0.20");
  });

  it("writes the cooldown in everyday units", () => {
    expect(cooldownWords(15)).toBe("15 minutes");
    expect(cooldownWords(60)).toBe("1 hour");
    expect(cooldownWords(240)).toBe("4 hours");
    expect(cooldownWords(1440)).toBe("1 day");
    expect(cooldownWords(90)).toBe("90 minutes");
  });
});

describe("threshold input", () => {
  it("turns a typed percentage into a probability", () => {
    expect(parseThreshold("prob_above", "60")).toEqual({ threshold: "0.6000" });
    expect(parseThreshold("prob_below", " 42.5 ")).toEqual({ threshold: "0.4250" });
  });

  it("keeps a price as the exact text that was typed", () => {
    expect(parseThreshold("price_above", "85,000.50")).toEqual({ threshold: "85000.50" });
    expect(parseThreshold("price_below", "0.00001234")).toEqual({ threshold: "0.00001234" });
  });

  it("needs no threshold for a signal change", () => {
    expect(parseThreshold("signal_change", "anything")).toEqual({ threshold: null });
  });

  it("explains what is wrong instead of sending a bad value", () => {
    expect(parseThreshold("prob_above", "100").error).toBe("Enter a percentage between 1 and 99.");
    expect(parseThreshold("prob_above", "0").error).toBe("Enter a percentage between 1 and 99.");
    expect(parseThreshold("price_above", "abc").error).toBe("Enter a number.");
    expect(parseThreshold("price_above", "-5").error).toBe("Enter a number.");
    expect(parseThreshold("price_above", "0").error).toBe("Enter a price above 0.");
  });
});
