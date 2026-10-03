import type { Metadata } from "next";

import { WatchlistView } from "@/components/watchlist-view";

export const metadata: Metadata = { title: "Watchlist" };

export default function WatchlistPage() {
  return (
    <div className="max-w-4xl space-y-6 pt-4">
      <h1 className="font-display text-3xl font-bold sm:text-5xl">Watchlist</h1>
      <WatchlistView />
    </div>
  );
}
