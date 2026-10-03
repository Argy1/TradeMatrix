import { CandlestickChart, Scale, ShieldCheck } from "lucide-react";
import Link from "next/link";

import { CandleScene } from "@/components/candle-scene";
import { MarketList, TrackStrip } from "@/components/market-list";

const TRUST = [
  { icon: Scale, text: "Probabilities, not promises" },
  { icon: ShieldCheck, text: "Results shown next to a simple baseline" },
  { icon: CandlestickChart, text: "Never places trades for you" },
];

const STEPS = [
  {
    title: "1. Read the chart",
    text: "Indicators like RSI, moving averages and volume are computed from closed candles only.",
  },
  {
    title: "2. Weigh the odds",
    text: "A machine-learning model turns them into a calibrated chance that the next candle closes higher.",
  },
  {
    title: "3. Check the record",
    text: "Every signal is stored and scored, and compared with a simple baseline, even when that looks bad.",
  },
];

export default function MarketsPage() {
  return (
    <div className="space-y-16 pt-6">
      <section className="grid items-center gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <h1 className="font-display text-4xl font-extrabold leading-tight sm:text-[54px]">
            Crypto signals that show their odds
          </h1>
          <p className="max-w-xl text-lg text-fg-2">
            For Bitcoin, Ethereum, Solana, BNB and XRP: will the next candle close higher or lower?
            You get a chance, the reasons, and an honest track record.
          </p>
          <div className="flex flex-wrap gap-3">
            <a href="#signals" className="btn-primary px-5 py-3">
              See today&apos;s signals
            </a>
            <Link href="/about" className="key px-5 py-3 font-semibold">
              How a signal is made
            </Link>
          </div>
          <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-fg-2">
            {TRUST.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-2">
                <Icon aria-hidden size={16} className="text-cyan" /> {text}
              </li>
            ))}
          </ul>
        </div>
        <CandleScene />
      </section>

      <section id="signals" aria-labelledby="today" className="scroll-mt-6 space-y-4">
        <h2 id="today" className="font-display text-2xl font-bold">
          Today&apos;s signals
        </h2>
        <p className="text-sm text-muted">
          Each chip is the signal for the next 1h, 4h or 1d candle. * means that model is currently
          below the baseline, so treat it with extra caution.
        </p>
        <MarketList />
      </section>

      <section aria-labelledby="how" className="space-y-4">
        <h2 id="how" className="font-display text-2xl font-bold">
          How a signal is made
        </h2>
        <div className="grid gap-4 md:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.title} className="glass p-6">
              <h3 className="font-display text-lg font-semibold">{step.title}</h3>
              <p className="mt-2 text-fg-2">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <TrackStrip />
    </div>
  );
}
