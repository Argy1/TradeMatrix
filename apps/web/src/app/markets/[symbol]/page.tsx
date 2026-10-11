import type { Metadata } from "next";

import { CoinView } from "@/components/coin-view";
import { DEFAULT_TIMEFRAME, isTimeframe, type Timeframe } from "@/lib/api/client";

function pickTimeframe(value: string | string[] | undefined): Timeframe {
  return isTimeframe(value) ? value : DEFAULT_TIMEFRAME;
}

export async function generateMetadata({
  params,
}: PageProps<"/markets/[symbol]">): Promise<Metadata> {
  const { symbol } = await params;
  return { title: `${symbol.toUpperCase()} signal` };
}

export default async function CoinPage({ params, searchParams }: PageProps<"/markets/[symbol]">) {
  const { symbol } = await params;
  const { tf } = await searchParams;
  return <CoinView symbol={symbol.toUpperCase()} tf={pickTimeframe(tf)} />;
}
