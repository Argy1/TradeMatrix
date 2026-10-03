import { BarChart3, Check, ShieldCheck, SlidersHorizontal } from "lucide-react";
import Link from "next/link";

import { CandleScene } from "@/components/candle-scene";
import { MarketList, TrackStrip } from "@/components/market-list";

const TRUST = ["Shows odds, not promises", "Every past call is on record", "Free to explore"];

const STEPS = [
  {
    icon: BarChart3,
    color: "text-[#7BE8FF]",
    title: "1. We read the chart",
    text: "Price history and simple indicators like RSI and moving averages are computed from closed candles only.",
  },
  {
    icon: SlidersHorizontal,
    color: "text-[#B49BFF]",
    title: "2. A model weighs the odds",
    text: "A machine-learning model turns those readings into a calibrated chance that the next candle closes higher.",
  },
  {
    icon: ShieldCheck,
    color: "text-up",
    title: "3. You get odds and proof",
    text: "A probability, the reasons behind it, and a public record of how often we were right.",
  },
];

export default function MarketsPage() {
  return (
    <div className="pt-2">
      <section className="flex flex-wrap items-center gap-6">
        <div className="min-w-0 flex-[1_1_520px]">
          <span className="inline-flex items-center gap-2 rounded-full border border-cyan/30 bg-cyan/10 px-3.5 py-2 text-sm font-semibold text-[#9FEBFF]">
            Crypto signals in plain language
          </span>
          <h1 className="mt-4.5 font-display text-4xl font-extrabold leading-[1.05] tracking-[-0.03em] sm:text-[54px]">
            See which way the market leans before you decide.
          </h1>
          <p className="mt-4.5 max-w-[560px] text-[19px] leading-relaxed text-[#B4C0DC]">
            For Bitcoin and four other coins, TradeMatrix AI shows the chance the next candle goes up
            or down, explains why, and proves how past signals performed.
          </p>
          <div className="mt-7 flex flex-wrap gap-3.5">
            <a href="#signals" className="btn-primary inline-flex min-h-12 items-center px-6 text-base">
              See today&apos;s signals
            </a>
            <Link href="/about" className="key inline-flex min-h-12 items-center px-5 text-base font-semibold">
              How does it work?
            </Link>
          </div>
          <ul className="mt-7 flex flex-wrap gap-x-6 gap-y-3 text-[15px] text-fg-2">
            {TRUST.map((text) => (
              <li key={text} className="inline-flex items-center gap-2">
                <Check aria-hidden size={20} strokeWidth={2.6} className="text-up" /> {text}
              </li>
            ))}
          </ul>
        </div>
        <div className="min-w-0 flex-[1_1_440px]">
          <CandleScene />
        </div>
      </section>

      <section id="signals" aria-labelledby="today" className="mt-10 scroll-mt-6">
        <div className="mb-3.5 flex flex-wrap items-baseline justify-between gap-3">
          <h2 id="today" className="font-display text-[30px] font-bold tracking-[-0.01em]">
            Today&apos;s signals
          </h2>
          <span className="text-sm text-muted">Tap a coin to see the chart and the reasons.</span>
        </div>
        <MarketList />
        <p className="mx-1 mt-3 text-[13px] leading-relaxed text-[#8FA0C4]">
          Each chip is the chance for the next candle of that size (1h, 4h or 1d). Neutral means the
          odds are too close, so we make no call. A warning sign means that model is currently below
          the simple baseline, so treat it with extra caution.
        </p>
      </section>

      <section aria-labelledby="how" className="mt-12">
        <h2 id="how" className="mb-4 font-display text-[30px] font-bold tracking-[-0.01em]">
          How a signal is made
        </h2>
        <div className="flex flex-wrap gap-5">
          {STEPS.map(({ icon: Icon, color, title, text }) => (
            <div key={title} className="glass flex flex-[1_1_280px] flex-col gap-3.5 p-6">
              <span className={`tile grid h-[60px] w-14 place-items-center ${color}`}>
                <Icon aria-hidden size={26} strokeWidth={2.4} />
              </span>
              <h3 className="font-display text-xl font-bold">{title}</h3>
              <p className="text-[15px] leading-relaxed text-[#B4C0DC]">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <div className="mt-12">
        <TrackStrip />
      </div>
    </div>
  );
}
