"use client";

import { RefreshCw } from "lucide-react";

/** Loading skeleton: a glass card with a shimmer (static when motion is reduced). */
export function Skeleton({ className = "h-40" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`glass animate-pulse motion-reduce:animate-none ${className}`}
    />
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="glass flex flex-col items-start gap-3 p-6">
      <p className="text-fg-2">{message}</p>
      {onRetry && (
        <button type="button" onClick={onRetry} className="key flex items-center gap-2 px-4 py-2 text-sm font-semibold">
          <RefreshCw aria-hidden size={16} /> Try again
        </button>
      )}
    </div>
  );
}
