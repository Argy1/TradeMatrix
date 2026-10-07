"use client";

import { AlertTriangle, Clock } from "lucide-react";
import { useEffect, useState } from "react";

import type { Prediction, Timeframe } from "@/lib/api/client";
import { DISCLAIMER, EFFECT_TAG, REASON_EXPLAINERS } from "@/lib/copy";
import { formatClock, formatCountdown, formatProbability, timeframeWords } from "@/lib/format";
import {
  DEGRADED_WARNING,
  type Direction,
  HEADLINE,
  NEUTRAL_HIGH,
  NEUTRAL_LOW,
  STALE_WARNING,
  WORD,
  asDirection,
  plainSentence,
  reliabilitySentence,
  screenReaderSummary,
  shownProbability,
} from "@/lib/signal";

import { SignalAlertButton } from "./alerts-view";
import { DIRECTION_TEXT, DirectionIcon } from "./direction";

const ORB: Record<Direction, { c1: string; c2: string; glow: string; ring: string }> = {
  up: { c1: "#34F0B0", c2: "#0A6E53", glow: "rgba(46,230,166,.55)", ring: "#2EE6A6" },
  down: { c1: "#FF7E96", c2: "#8C1B38", glow: "rgba(255,92,122,.5)", ring: "#FF5C7A" },
  neutral: { c1: "#FFD98A", c2: "#8A5F0E", glow: "rgba(255,200,87,.45)", ring: "#FFC857" },
};

/** The hero orb with the probability ring around it (pure CSS, docs/08 block 2). */
function Orb({ direction, probability }: { direction: Direction; probability: number }) {
  const { c1, c2, glow, ring } = ORB[direction];
  return (
    <div className="relative mx-auto h-[184px] w-[184px]" aria-hidden>
      <div
        className="absolute inset-0 rounded-full"
        style={{
          background: `conic-gradient(${ring} ${probability * 360}deg, rgba(255,255,255,.09) 0)`,
          mask: "radial-gradient(farthest-side, transparent calc(100% - 12px), #000 calc(100% - 11px))",
        }}
      />
      <div
        className="orb-bob absolute inset-[14px] grid place-items-center rounded-full"
        style={{
          background: `radial-gradient(circle at 32% 26%, rgba(255,255,255,.75), transparent 26%), radial-gradient(circle at 50% 55%, ${c1}, ${c2} 72%, #04060c)`,
          boxShadow: `0 0 54px ${glow}, inset -16px -20px 34px rgba(0,0,0,.55), inset 10px 12px 22px rgba(255,255,255,.22)`,
        }}
      >
        <div className="text-center text-white [text-shadow:0_2px_8px_rgba(0,0,0,.55)]">
          <div className="font-display text-[30px] font-extrabold leading-none tracking-wide">
            {WORD[direction]}
          </div>
          <div className="mt-1 font-mono text-lg font-semibold">
            {formatProbability(probability)}
          </div>
        </div>
      </div>
      <div
        className="absolute -bottom-3 left-1/2 h-4 w-28 -translate-x-1/2 rounded-full blur-md"
        style={{ background: glow }}
      />
    </div>
  );
}

/** Red-to-green bar with the amber neutral zone and a knob at p_up (docs/08 block 5). */
function Meter({ pUp }: { pUp: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs font-medium">
        <span className="text-down-fg">Down more likely</span>
        <span className="text-up">Up more likely</span>
      </div>
      <div
        className="relative mt-2 h-3 rounded-full"
        style={{ background: "linear-gradient(90deg, #FF5C7A, #FFC857 50%, #2EE6A6)" }}
      >
        <div
          className="absolute -inset-y-1 rounded-md border-2 border-neutral/90"
          style={{ left: `${NEUTRAL_LOW * 100}%`, width: `${(NEUTRAL_HIGH - NEUTRAL_LOW) * 100}%` }}
        />
        <div
          className="absolute top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white"
          style={{
            left: `${pUp * 100}%`,
            background: "radial-gradient(circle at 35% 30%, #fff, #b4c0dc 60%, #5b6785)",
            boxShadow: "0 3px 0 rgba(0,0,0,.5), 0 6px 14px rgba(0,0,0,.4)",
          }}
        />
      </div>
      <div className="relative mt-2 h-4 font-mono text-xs text-muted">
        <span className="absolute left-0">0%</span>
        <span className="absolute -translate-x-full" style={{ left: `${NEUTRAL_LOW * 100}%` }}>
          45%
        </span>
        <span className="absolute" style={{ left: `${NEUTRAL_HIGH * 100}%` }}>
          55%
        </span>
        <span className="absolute right-0">100%</span>
      </div>
      <p className="mt-1 text-center text-xs text-muted">Neutral zone: too close to call</p>
      <p className="mt-2 text-center text-sm text-fg-2">
        Chance of going up: <strong className="font-mono text-fg">{formatProbability(pUp)}</strong>
      </p>
    </div>
  );
}

function Reliability({ prediction, symbol }: { prediction: Prediction; symbol: string }) {
  const { model, naive_baseline: naive, n, low_sample: lowSample } = prediction.recent_accuracy;
  const scale = (value: number) => `${Math.min(Math.max((value - 0.4) / 0.2, 0), 1) * 100}%`;
  return (
    <section aria-labelledby="reliability" className="space-y-3">
      <div>
        <h3 id="reliability" className="font-display text-base font-semibold">
          How reliable is it?
        </h3>
        <p className="text-xs text-muted">
          Real results from the last {n} finished {prediction.timeframe} signals for {symbol}.
        </p>
      </div>
      {model != null && naive != null && (
        <div className="space-y-2 text-sm">
          {[
            { label: "TradeMatrix model", value: model, color: "#4DD8FF" },
            { label: "Simple baseline: repeat the last move", value: naive, color: "#9AA8C7" },
          ].map((bar) => (
            <div key={bar.label}>
              <div className="flex justify-between text-fg-2">
                <span>{bar.label}</span>
                <span className="font-mono">{formatProbability(bar.value)}</span>
              </div>
              <div className="mt-1 h-2 rounded-full bg-white/10">
                <div
                  className="h-2 rounded-full"
                  style={{ width: scale(bar.value), background: bar.color }}
                />
              </div>
            </div>
          ))}
          <p className="text-xs text-muted">Scale 40% to 60%. {n} finished signals.</p>
        </div>
      )}
      <p className="text-sm text-fg-2">{reliabilitySentence(model, naive, n, lowSample)}</p>
    </section>
  );
}

function Countdown({ targetIso }: { targetIso: string }) {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 30_000);
    return () => clearInterval(timer);
  }, []);
  return <>{formatCountdown(targetIso, now)}</>;
}

export function SignalCard({
  prediction,
  coinName,
}: {
  prediction: Prediction;
  coinName: string;
}) {
  const tf = prediction.timeframe as Timeframe;
  const direction = asDirection(prediction.label);
  const probability = shownProbability(direction, prediction.p_up);
  const degraded = prediction.model.status === "degraded";

  return (
    <div className="space-y-3">
      {prediction.stale && (
        <p role="status" className="glass flex gap-2 p-4 text-sm text-neutral">
          <AlertTriangle aria-hidden size={18} className="shrink-0" /> {STALE_WARNING}
        </p>
      )}
      {degraded && (
        <p role="status" className="glass flex gap-2 border-neutral/40 p-4 text-sm text-neutral">
          <AlertTriangle aria-hidden size={18} className="shrink-0" /> {DEGRADED_WARNING}
        </p>
      )}
      <article className="glass space-y-6 p-6" aria-label={`${coinName} signal`}>
        <p className="sr-only">
          {screenReaderSummary(coinName, tf, prediction.label, prediction.p_up)}
        </p>
        <header className="flex items-baseline justify-between text-xs font-semibold tracking-[0.14em] text-muted">
          <span>TRADEMATRIX SIGNAL</span>
          <span className="tracking-normal">for the next {timeframeWords(tf)} candle</span>
        </header>

        <Orb direction={direction} probability={probability} />

        <div className="space-y-2 text-center">
          <h2
            className={`inline-flex items-center gap-2 font-display text-2xl font-bold ${DIRECTION_TEXT[direction]}`}
          >
            <DirectionIcon direction={direction} size={22} />
            {HEADLINE[direction]}
          </h2>
          <p className="text-[15px] leading-relaxed text-fg-2">
            {plainSentence(direction, prediction.p_up, tf, prediction.base_close)}
          </p>
        </div>

        <Meter pUp={prediction.p_up} />

        <p className="flex gap-2 text-sm text-fg-2">
          <Clock aria-hidden size={18} className="mt-0.5 shrink-0 text-cyan" />
          <span>
            Valid for the {timeframeWords(tf)} candle that closes at{" "}
            <strong className="font-mono text-fg">
              {formatClock(prediction.target_close_time)}
            </strong>
            , <Countdown targetIso={prediction.target_close_time} />. A new signal appears right
            after it closes.
          </span>
        </p>

        <section aria-labelledby="why" className="space-y-3">
          <div>
            <h3 id="why" className="font-display text-base font-semibold">
              Why this signal
            </h3>
            <p className="text-xs text-muted">The three things that mattered most, in plain words.</p>
          </div>
          <ul className="space-y-3">
            {prediction.reasons.map((reason) => {
              const effect = asDirection(reason.effect === "none" ? "neutral" : reason.effect);
              return (
                <li key={reason.code + reason.text} className="tile flex flex-wrap gap-3 p-3">
                  <span
                    className={`grid h-9 w-9 shrink-0 place-items-center rounded-full bg-white/10 ${DIRECTION_TEXT[effect]}`}
                  >
                    <DirectionIcon direction={effect} />
                  </span>
                  {/* On narrow screens the tag wraps under the text instead of squeezing it. */}
                  <div className="min-w-0 grow basis-[11rem]">
                    <p className="font-semibold text-fg">{reason.text}</p>
                    <p className="text-sm text-muted">{REASON_EXPLAINERS[reason.code] ?? ""}</p>
                  </div>
                  <span
                    className={`h-fit shrink-0 rounded-full bg-white/5 px-2 py-1 text-xs font-medium ${DIRECTION_TEXT[effect]}`}
                  >
                    {EFFECT_TAG[reason.effect] ?? EFFECT_TAG.none}
                  </span>
                </li>
              );
            })}
          </ul>
        </section>

        <Reliability prediction={prediction} symbol={prediction.symbol} />

        <p className="rounded-2xl border border-neutral/40 bg-neutral/10 p-4 text-sm leading-relaxed text-fg-2">
          {DISCLAIMER}
        </p>

        <SignalAlertButton symbol={prediction.symbol} tf={tf} />
      </article>
    </div>
  );
}
