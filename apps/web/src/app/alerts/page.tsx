import type { Metadata } from "next";

import { AlertsView } from "@/components/alerts-view";

export const metadata: Metadata = { title: "Alerts" };

export default function AlertsPage() {
  return (
    <div className="max-w-4xl space-y-6 pt-4">
      <div>
        <h1 className="font-display text-3xl font-bold sm:text-5xl">Alerts</h1>
        <p className="mt-2 text-fg-2">
          Get told when a signal changes or a price crosses a level, instead of checking the page.
        </p>
      </div>
      <AlertsView />
    </div>
  );
}
