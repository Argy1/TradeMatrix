import { describe, expect, it } from "vitest";

import { formatAgo, formatCountdown, formatScore, timeframeWords } from "./format";

describe("news formatting", () => {
  const now = new Date("2026-10-07T12:00:00Z");

  it("says how long ago a headline was published", () => {
    expect(formatAgo("2026-10-07T11:59:40Z", now)).toBe("just now");
    expect(formatAgo("2026-10-07T11:48:00Z", now)).toBe("12 min ago");
    expect(formatAgo("2026-10-07T09:00:00Z", now)).toBe("3 h ago");
    expect(formatAgo("2026-10-05T11:00:00Z", now)).toBe("2 d ago");
    // A publisher clock that runs a little ahead must not show a negative time.
    expect(formatAgo("2026-10-07T12:03:00Z", now)).toBe("just now");
  });

  it("always shows the sign of a sentiment score", () => {
    expect(formatScore(0.31)).toBe("+0.31");
    expect(formatScore(-0.2)).toBe("-0.20");
    expect(formatScore(0)).toBe("+0.00");
    expect(formatScore(-0.004)).toBe("+0.00"); // rounds to zero: never "-0.00"
  });
});

describe("candle sizes", () => {
  it("names every size", () => {
    expect(timeframeWords("1m")).toBe("1 minute");
    expect(timeframeWords("15m")).toBe("15 minute");
    expect(timeframeWords("4h")).toBe("4 hour");
    expect(timeframeWords("1d")).toBe("1 day");
  });

  it("counts down in minutes for the slow sizes, as before", () => {
    const now = new Date("2026-10-11T12:00:00Z");
    expect(formatCountdown("2026-10-11T12:41:00Z", now)).toBe("in 41 min");
    expect(formatCountdown("2026-10-11T14:05:00Z", now)).toBe("in 2 h 5 min");
    expect(formatCountdown("2026-10-11T12:00:20Z", now)).toBe("now");
    expect(formatCountdown("2026-10-11T11:59:00Z", now)).toBe("now");
  });

  it("counts down in seconds for the fast sizes", () => {
    const now = new Date("2026-10-11T12:00:00Z");
    const fast = { seconds: true };
    expect(formatCountdown("2026-10-11T12:00:42Z", now, fast)).toBe("in 42 s");
    expect(formatCountdown("2026-10-11T12:01:59Z", now, fast)).toBe("in 119 s");
    expect(formatCountdown("2026-10-11T12:03:20Z", now, fast)).toBe("in 3 min 20 s");
    expect(formatCountdown("2026-10-11T12:05:00Z", now, fast)).toBe("in 5 min");
    expect(formatCountdown("2026-10-11T12:25:00Z", now, fast)).toBe("in 25 min"); // far away: minutes
    expect(formatCountdown("2026-10-11T12:00:00Z", now, fast)).toBe("now");
    expect(formatCountdown("2026-10-11T11:59:30Z", now, fast)).toBe("now");
  });
});
