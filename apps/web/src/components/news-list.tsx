"use client";

import { ExternalLink } from "lucide-react";

import type { NewsItem } from "@/lib/api/client";
import { useNews } from "@/lib/api/hooks";
import { NEWS_BLENDED, NEWS_CONTEXT_ONLY, NEWS_FOOTNOTE, NEWS_SCALE } from "@/lib/copy";
import { formatAgo, formatDateTime, formatScore } from "@/lib/format";
import type { Direction } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon } from "./direction";
import { ErrorState, Skeleton } from "./states";

// The API decides bullish / bearish / neutral; here it only becomes a word, an icon and a color.
const TONE: Record<string, { direction: Direction; word: string }> = {
  bullish: { direction: "up", word: "Bullish" },
  bearish: { direction: "down", word: "Bearish" },
  neutral: { direction: "neutral", word: "Neutral" },
};

/** Word + icon + number, so the tone never depends on color alone (docs/08). */
function ToneBadge({ sentiment }: { sentiment: NewsItem["sentiment"] }) {
  if (!sentiment) return <span className="shrink-0 text-xs text-muted">Not rated yet</span>;
  const tone = TONE[sentiment.label] ?? TONE.neutral;
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1.5 rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-semibold ${DIRECTION_TEXT[tone.direction]}`}
    >
      <DirectionIcon direction={tone.direction} size={14} />
      {tone.word} <span className="font-mono">{formatScore(sentiment.score)}</span>
    </span>
  );
}

function NewsRow({ item }: { item: NewsItem }) {
  // The API only stores http(s) links; checking again here costs nothing.
  const safeUrl = /^https?:\/\//.test(item.url) ? item.url : undefined;
  return (
    <li className="flex flex-wrap items-start justify-between gap-x-4 gap-y-2 border-t border-white/10 py-3 first:border-t-0 first:pt-0">
      <div className="min-w-0 flex-1 basis-64">
        {safeUrl ? (
          <a
            href={safeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-fg underline-offset-4 hover:underline"
          >
            {item.title}{" "}
            <ExternalLink aria-hidden size={13} className="inline -translate-y-px text-muted" />
            <span className="sr-only"> (opens the publisher&apos;s site in a new tab)</span>
          </a>
        ) : (
          <span className="font-medium text-fg">{item.title}</span>
        )}
        <p className="mt-1 text-xs text-muted">
          {item.source_name} ·{" "}
          <time dateTime={item.published_at} title={formatDateTime(item.published_at)}>
            {formatAgo(item.published_at)}
          </time>
        </p>
      </div>
      <ToneBadge sentiment={item.sentiment} />
    </li>
  );
}

export function NewsList({
  symbol,
  name,
  sentimentUsed,
}: {
  symbol: string;
  name: string;
  sentimentUsed: boolean;
}) {
  const news = useNews(symbol);
  return (
    <section aria-labelledby="news" className="glass space-y-4 p-6">
      <div>
        <h2 id="news" className="font-display text-lg font-semibold">
          News tone for {name}
        </h2>
        <p className="text-sm text-muted">
          {NEWS_SCALE} {sentimentUsed ? NEWS_BLENDED : NEWS_CONTEXT_ONLY}
        </p>
      </div>
      {news.isPending ? (
        <Skeleton className="h-40" />
      ) : news.isError ? (
        <ErrorState message="Could not load the news." onRetry={() => news.refetch()} />
      ) : news.data.items.length === 0 ? (
        <p className="text-sm text-fg-2">No recent headlines mention {name}.</p>
      ) : (
        <ul>
          {news.data.items.map((item) => (
            <NewsRow key={item.id} item={item} />
          ))}
        </ul>
      )}
      <p className="text-xs text-muted">{NEWS_FOOTNOTE}</p>
    </section>
  );
}
