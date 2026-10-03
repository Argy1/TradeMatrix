import { ArrowDown, ArrowUp, Minus } from "lucide-react";

import type { Direction } from "@/lib/signal";
import { WORD } from "@/lib/signal";

export const DIRECTION_TEXT: Record<Direction, string> = {
  up: "text-up",
  down: "text-down-fg",
  neutral: "text-neutral",
};

/** Arrow / dash icon. Always paired with a word: color is never the only cue (docs/08). */
export function DirectionIcon({ direction, size = 16 }: { direction: Direction; size?: number }) {
  const Icon = direction === "up" ? ArrowUp : direction === "down" ? ArrowDown : Minus;
  return <Icon aria-hidden size={size} strokeWidth={2.5} />;
}

export function DirectionLabel({
  direction,
  size = 14,
  word,
}: {
  direction: Direction;
  size?: number;
  word?: string;
}) {
  return (
    <span className={`inline-flex items-center gap-1 font-semibold ${DIRECTION_TEXT[direction]}`}>
      <DirectionIcon direction={direction} size={size} />
      {word ?? WORD[direction].charAt(0) + WORD[direction].slice(1).toLowerCase()}
    </span>
  );
}
