"use client";

// Isometric 3D candle scene for the home hero (docs/08 block 4, design canvas "Markets").
// Pure CSS and decorative, except the floating badge, which shows the LIVE BTC 1h signal
// (the canvas used sample data there; docs/08 forbids sample numbers in production).

import { useMarkets } from "@/lib/api/hooks";
import { formatProbability } from "@/lib/format";
import { WORD, asDirection, shownProbability } from "@/lib/signal";

import { DIRECTION_TEXT, DirectionIcon } from "./direction";

const SIZE = 56;
const GREEN = { top: "#6DF5C6", front: "#22C896", side: "#127A5C" };
const RED = { top: "#FF93A7", front: "#E24465", side: "#8E2339" };
const CANDLES = [
  { h: 64, c: GREEN },
  { h: 44, c: RED },
  { h: 92, c: GREEN },
  { h: 70, c: RED },
  { h: 128, c: GREEN },
];

function Prism({ index, h, faces, ghost = false }: { index: number; h: number; faces: typeof GREEN; ghost?: boolean }) {
  const border = ghost ? "2px dashed #2EE6A6" : "none";
  const face = (color: string): React.CSSProperties => ({ background: color, border });
  return (
    <div className="absolute" style={{ left: -200 + index * 70, top: -28, width: SIZE, height: SIZE, transformStyle: "preserve-3d" }}>
      <i className="absolute" style={{ ...face(faces.top), left: 0, top: 0, width: SIZE, height: SIZE, transform: `translateZ(${h}px)` }} />
      <i className="absolute" style={{ ...face(faces.front), left: 0, top: SIZE, width: SIZE, height: h, transformOrigin: "top", transform: "rotateX(90deg)" }} />
      <i className="absolute" style={{ ...face(faces.side), left: 0, top: 0, width: h, height: SIZE, transformOrigin: "left", transform: "rotateY(-90deg)" }} />
    </div>
  );
}

function LiveBadge() {
  const { data } = useMarkets();
  const chip = data?.find((row) => row.symbol === "BTC")?.signals["1h"];
  if (!chip) return null;
  const direction = asDirection(chip.label);
  return (
    <div className="glass absolute right-[4%] top-[6%] flex items-center gap-3 rounded-[18px] px-4 py-3">
      <span className={`tile grid h-12 w-11 place-items-center ${DIRECTION_TEXT[direction]}`}>
        <DirectionIcon direction={direction} size={22} />
      </span>
      <span className="flex flex-col leading-tight">
        <span className="text-xs font-semibold text-muted">BTC · next 1h · live</span>
        <span className={`font-mono text-xl font-bold ${DIRECTION_TEXT[direction]}`}>
          {formatProbability(shownProbability(direction, chip.p_up))} {WORD[direction]}
        </span>
      </span>
    </div>
  );
}

export function CandleScene() {
  return (
    <div className="relative h-[420px] w-full" style={{ perspective: "1400px" }}>
      <div
        role="img"
        aria-label="Illustration: five 3D candlesticks and a dashed ghost candle for the predicted next move"
        className="absolute left-1/2 top-[62%] h-0 w-0"
        style={{ transformStyle: "preserve-3d", transform: "rotateX(58deg) rotateZ(-40deg)" }}
      >
        <div
          className="absolute"
          style={{
            width: 440,
            height: 440,
            left: -220,
            top: -220,
            borderRadius: 28,
            background:
              "linear-gradient(rgba(77,216,255,.2) 1px, transparent 1px) 0 0/44px 44px, linear-gradient(90deg, rgba(77,216,255,.2) 1px, transparent 1px) 0 0/44px 44px, rgba(77,216,255,.06)",
            border: "1px solid rgba(77,216,255,.4)",
            boxShadow: "0 0 70px rgba(77,216,255,.18)",
          }}
        />
        {CANDLES.map((candle, index) => (
          <Prism key={index} index={index} h={candle.h} faces={candle.c} />
        ))}
        <Prism
          index={5}
          h={176}
          ghost
          faces={{ top: "rgba(46,230,166,.22)", front: "rgba(46,230,166,.14)", side: "rgba(46,230,166,.10)" }}
        />
      </div>
      <LiveBadge />
    </div>
  );
}
