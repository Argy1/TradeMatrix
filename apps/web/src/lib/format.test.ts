import { describe, expect, it } from "vitest";

import { formatAgo, formatScore } from "./format";

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
