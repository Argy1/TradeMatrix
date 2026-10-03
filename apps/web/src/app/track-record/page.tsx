import type { Metadata } from "next";

import { TrackRecord } from "@/components/track-record";

export const metadata: Metadata = { title: "Track record" };

export default function TrackRecordPage() {
  return (
    <div className="space-y-6 pt-4">
      <div>
        <h1 className="font-display text-3xl font-bold sm:text-5xl">Track record</h1>
        <p className="mt-2 max-w-3xl text-fg-2">
          Every signal is stored and scored when its candle closes. We always show the model next to
          two simple baselines, even when the model loses. Brier score measures probability quality:
          lower is better, 0.25 is a coin flip.
        </p>
      </div>
      <TrackRecord />
    </div>
  );
}
