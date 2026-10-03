"use client";

import {
  CandlestickSeries,
  ColorType,
  HistogramSeries,
  type IChartApi,
  type ISeriesApi,
  LineSeries,
  LineStyle,
  type SeriesType,
  type Time,
  type UTCTimestamp,
  createChart,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

import type { Candle } from "@/lib/api/client";
import { DISPLAY_TIME_ZONE } from "@/lib/format";

type Overlay = "ema" | "bollinger" | "rsi" | "macd";
type LineKey = "ema9" | "ema21" | "ema50" | "bb_upper" | "bb_mid" | "bb_lower" | "rsi14" | "macd" | "macd_signal";

const LABELS: Record<Overlay, string> = {
  ema: "EMA 9/21/50",
  bollinger: "Bollinger Bands",
  rsi: "RSI",
  macd: "MACD",
};

const toTime = (iso: string) => Math.floor(Date.parse(iso) / 1000) as UTCTimestamp;

// The chart library draws in UTC; we label the axis in WIB (data stays UTC, CLAUDE.md).
const wib = (time: Time, options: Intl.DateTimeFormatOptions) =>
  new Intl.DateTimeFormat("en-GB", { timeZone: DISPLAY_TIME_ZONE, hourCycle: "h23", ...options }).format(
    new Date((time as number) * 1000),
  );

type Built = {
  chart: IChartApi;
  price: ISeriesApi<"Candlestick">;
  volume: ISeriesApi<"Histogram">;
  lines: { key: LineKey; series: ISeriesApi<SeriesType> }[];
  macdHist: ISeriesApi<"Histogram"> | null;
  fitted: boolean;
};

function fill(built: Built, candles: Candle[]) {
  built.price.setData(
    candles.map((c) => ({ time: toTime(c.t), open: Number(c.o), high: Number(c.h), low: Number(c.l), close: Number(c.c) })),
  );
  built.volume.setData(
    candles.map((c) => ({
      time: toTime(c.t),
      value: Number(c.v),
      color: Number(c.c) >= Number(c.o) ? "rgba(46,230,166,0.35)" : "rgba(255,92,122,0.35)",
    })),
  );
  for (const { key, series } of built.lines) {
    series.setData(
      candles.filter((c) => c[key] !== null).map((c) => ({ time: toTime(c.t), value: c[key] as number })),
    );
  }
  built.macdHist?.setData(
    candles
      .filter((c) => c.macd_hist !== null)
      .map((c) => ({
        time: toTime(c.t),
        value: c.macd_hist as number,
        color: (c.macd_hist as number) >= 0 ? "rgba(46,230,166,.6)" : "rgba(255,92,122,.6)",
      })),
  );
  if (!built.fitted && candles.length) {
    built.chart.timeScale().fitContent(); // only once, so the person's zoom is kept on updates
    built.fitted = true;
  }
}

/** Candles + volume + indicator overlays. Every number comes from the API (clients are thin). */
export function PriceChart({ candles }: { candles: Candle[] }) {
  const container = useRef<HTMLDivElement>(null);
  const built = useRef<Built | null>(null);
  const latest = useRef(candles);
  const [overlays, setOverlays] = useState<Record<Overlay, boolean>>({
    ema: true,
    bollinger: false,
    rsi: false,
    macd: false,
  });

  useEffect(() => {
    latest.current = candles;
  }, [candles]);

  // Build the chart when it mounts or when the overlays change.
  useEffect(() => {
    if (!container.current) return;
    const chart = createChart(container.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9AA8C7",
        fontFamily: "var(--font-jetbrains-mono), monospace",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.04)" },
        horzLines: { color: "rgba(255,255,255,0.05)" },
      },
      rightPriceScale: { borderVisible: false },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
        tickMarkFormatter: (time: Time) => wib(time, { hour: "2-digit", minute: "2-digit" }),
      },
      localization: {
        timeFormatter: (time: Time) =>
          `${wib(time, { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" })} WIB`,
      },
    });
    const price = chart.addSeries(CandlestickSeries, {
      upColor: "#2EE6A6",
      downColor: "#FF5C7A",
      borderVisible: false,
      wickUpColor: "#2EE6A6",
      wickDownColor: "#FF5C7A",
      priceLineStyle: LineStyle.Dashed,
      priceLineColor: "#ffffff",
    });
    const volume = chart.addSeries(HistogramSeries, {
      priceScaleId: "",
      priceFormat: { type: "volume" },
      lastValueVisible: false,
      priceLineVisible: false,
    });
    volume.priceScale().applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

    const lines: Built["lines"] = [];
    const line = (key: LineKey, color: string, pane = 0, style: LineStyle = LineStyle.Solid) => {
      const series = chart.addSeries(
        LineSeries,
        { color, lineWidth: 2, lineStyle: style, priceLineVisible: false, lastValueVisible: false },
        pane,
      );
      lines.push({ key, series });
      return series;
    };
    if (overlays.ema) {
      line("ema9", "#4DD8FF");
      line("ema21", "#B49BFF");
      line("ema50", "#FFC857");
    }
    if (overlays.bollinger) {
      line("bb_upper", "rgba(234,240,255,0.55)", 0, LineStyle.Dotted);
      line("bb_mid", "rgba(234,240,255,0.35)", 0, LineStyle.Dashed);
      line("bb_lower", "rgba(234,240,255,0.55)", 0, LineStyle.Dotted);
    }
    let pane = 1;
    if (overlays.rsi) {
      const rsi = line("rsi14", "#B49BFF", pane);
      for (const [level, color] of [[70, "rgba(255,92,122,.6)"], [30, "rgba(46,230,166,.6)"]] as const) {
        rsi.createPriceLine({ price: level, color, lineStyle: LineStyle.Dashed, lineWidth: 1, axisLabelVisible: false, title: "" });
      }
      pane += 1;
    }
    let macdHist: Built["macdHist"] = null;
    if (overlays.macd) {
      macdHist = chart.addSeries(HistogramSeries, { priceLineVisible: false, lastValueVisible: false }, pane);
      line("macd", "#4DD8FF", pane);
      line("macd_signal", "#FFC857", pane);
    }
    chart.panes().forEach((p, index) => p.setStretchFactor(index === 0 ? 3 : 1));

    built.current = { chart, price, volume, lines, macdHist, fitted: false };
    fill(built.current, latest.current);
    return () => {
      chart.remove();
      built.current = null;
    };
  }, [overlays]);

  // New data (refetch or live candle): update the series, never rebuild the chart.
  useEffect(() => {
    if (built.current) fill(built.current, candles);
  }, [candles]);

  const height = 380 + (overlays.rsi ? 110 : 0) + (overlays.macd ? 110 : 0);

  return (
    <div>
      <div className="mb-3 flex flex-wrap gap-2" role="group" aria-label="Chart overlays">
        {(Object.keys(LABELS) as Overlay[]).map((key) => (
          <button
            key={key}
            type="button"
            aria-pressed={overlays[key]}
            onClick={() => setOverlays((current) => ({ ...current, [key]: !current[key] }))}
            className="key px-3 py-1.5 text-xs font-semibold text-fg-2"
          >
            {LABELS[key]}
          </button>
        ))}
      </div>
      <div
        ref={container}
        style={{ height }}
        role="img"
        aria-label="Price chart with candles, volume and the selected indicators"
      />
      <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted" aria-label="Legend">
        <li><span className="text-up">▲ green candle</span>: closed higher</li>
        <li><span className="text-down-fg">▼ red candle</span>: closed lower</li>
        {overlays.ema && (
          <>
            <li><span className="text-ema9">━ EMA 9</span></li>
            <li><span className="text-ema21">━ EMA 21</span></li>
            <li><span className="text-ema50">━ EMA 50</span></li>
          </>
        )}
        {overlays.bollinger && <li>┄ Bollinger Bands (20, 2)</li>}
        {overlays.rsi && <li><span className="text-ema21">RSI 14</span> (lines at 30 and 70)</li>}
        {overlays.macd && <li>MACD (12, 26, 9)</li>}
        <li>White dashed line: last price</li>
      </ul>
    </div>
  );
}
