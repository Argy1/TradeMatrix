import { describe, expect, it } from "vitest";

import { formatClock, formatCountdown, formatPrice, formatProbability } from "./format";
import {
  asDirection,
  plainSentence,
  reliabilitySentence,
  screenReaderSummary,
  shownProbability,
} from "./signal";

describe("signal wording (docs/08)", () => {
  it("shows the down probability for a Down signal", () => {
    expect(shownProbability("down", 0.3)).toBeCloseTo(0.7);
    expect(shownProbability("up", 0.582)).toBeCloseTo(0.582);
    expect(shownProbability("neutral", 0.508)).toBeCloseTo(0.508);
  });

  it("writes the plain sentence from the example", () => {
    expect(plainSentence("up", 0.582, "1h", "67123.45")).toBe(
      "58.2% chance the next 1 hour candle closes higher than $67,123.45. That leaves 41.8% that it does not.",
    );
    expect(plainSentence("neutral", 0.508, "1h", "1")).toBe(
      "Up 50.8% versus down 49.2%. When the odds are this close we make no call and show Neutral.",
    );
  });

  it("is honest when the model loses to the baseline", () => {
    expect(reliabilitySentence(0.541, 0.512, 200, false)).toBe(
      "The model beat the baseline by 2.9 points. That is a small edge, which is normal for crypto.",
    );
    expect(reliabilitySentence(0.48, 0.5, 300, false)).toContain("did not beat");
    expect(reliabilitySentence(null, null, 0, true)).toContain("Not enough finished signals");
    expect(reliabilitySentence(0.6, 0.5, 12, true)).toContain("Only 12 finished signals");
  });

  it("gives screen readers one sentence", () => {
    expect(screenReaderSummary("Bitcoin", "1h", "up", 0.582)).toBe(
      "Bitcoin, next 1 hour candle: up, 58.2 percent chance. Neutral zone is 45 to 55 percent.",
    );
  });

  it("treats unknown labels as neutral", () => {
    expect(asDirection("sideways")).toBe("neutral");
  });
});

describe("formatting", () => {
  it("keeps price strings exact", () => {
    expect(formatPrice("84518.01")).toBe("$84,518.01");
    expect(formatPrice("1.4847")).toBe("$1.4847");
    expect(formatPrice("84460")).toBe("$84,460.00");
  });

  it("shows one decimal for probabilities", () => {
    expect(formatProbability(0.5198)).toBe("52.0%");
  });

  it("converts UTC to WIB only for display", () => {
    expect(formatClock("2026-10-03T15:00:00Z")).toBe("22:00 WIB");
  });

  it("counts down to the candle close", () => {
    const now = new Date("2026-10-03T14:19:00Z");
    expect(formatCountdown("2026-10-03T15:00:00Z", now)).toBe("in 41 min");
    expect(formatCountdown("2026-10-03T16:05:00Z", now)).toBe("in 1 h 46 min");
    expect(formatCountdown("2026-10-03T14:00:00Z", now)).toBe("now");
  });
});
