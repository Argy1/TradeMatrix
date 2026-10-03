import type { Metadata } from "next";

import { Brand } from "@/components/brand";
import { DISCLAIMER } from "@/lib/copy";

export const metadata: Metadata = { title: "How it works" };

const SECTIONS = [
  {
    title: "What a signal is",
    text: "For each coin and candle size (1 hour, 4 hours, 1 day) we estimate the chance that the next candle closes higher than the last one. Above 55% we say Up, below 45% Down, and in between Neutral: too close to call.",
  },
  {
    title: "How it is made",
    text: "When a candle closes, we compute indicators such as RSI, moving averages, MACD, Bollinger Bands and volume from closed candles only. A machine-learning model (XGBoost) turns them into a probability, calibrated so that 60% means Up about 60% of the time. The three reasons you see come from fixed templates, never from free AI text.",
  },
  {
    title: "The baseline",
    text: 'A model is only useful if it beats simple rules. Our baseline is "repeat the last move": if the last candle went up, say up. We show the model’s live accuracy next to that baseline on every signal and on the track-record page.',
  },
  {
    title: "What we found when testing",
    text: "In walk-forward tests on data the models had never seen, most 1-hour models beat the baselines by a small margin, while the 4-hour and daily models did not. Any model that is below the baseline shows a warning on its signal. Even the small edge is smaller than trading fees if you traded every signal. Treat signals as one input to your own decision.",
  },
  {
    title: "What we never do",
    text: "TradeMatrix AI never places trades, never asks for exchange keys, and never promises profit.",
  },
];

export default function AboutPage() {
  return (
    <div className="max-w-3xl space-y-8 pt-4">
      <h1 className="font-display text-3xl font-bold sm:text-5xl">How it works</h1>
      {SECTIONS.map((section) => (
        <section key={section.title} className="glass p-6">
          <h2 className="font-display text-xl font-semibold">{section.title}</h2>
          <p className="mt-2 leading-relaxed text-fg-2">{section.text}</p>
        </section>
      ))}
      <p className="rounded-2xl border border-neutral/40 bg-neutral/10 p-5 leading-relaxed text-fg-2">{DISCLAIMER}</p>
      <Brand linked={false} />
    </div>
  );
}
