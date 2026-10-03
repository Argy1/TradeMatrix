// Isometric 3D candle scene for the home hero (docs/08 block 4). Pure CSS, decorative only.

const CANDLES = [
  { x: 20, y: 150, h: 46, up: true },
  { x: 62, y: 120, h: 70, up: true },
  { x: 104, y: 90, h: 38, up: false },
  { x: 146, y: 60, h: 84, up: true },
  { x: 188, y: 30, h: 58, up: false },
];
const SIZE = 26;

function Box({ x, y, h, up, ghost = false }: { x: number; y: number; h: number; up: boolean; ghost?: boolean }) {
  const [light, mid, dark] = up ? ["#7af5cc", "#2EE6A6", "#13946b"] : ["#ffa3b5", "#FF5C7A", "#a8283f"];
  const face = (background: string): React.CSSProperties =>
    ghost
      ? { background: "rgba(77,216,255,0.12)", border: "1.5px dashed rgba(77,216,255,0.8)" }
      : { background };
  return (
    <div className="absolute" style={{ left: x, top: y, width: SIZE, height: SIZE, transformStyle: "preserve-3d" }}>
      {/* top */}
      <div className="absolute inset-0" style={{ ...face(light), transform: `translateZ(${h}px)` }} />
      {/* front: stands up from the near edge */}
      <div
        className="absolute left-0"
        style={{ ...face(mid), top: SIZE, width: SIZE, height: h, transformOrigin: "top", transform: "rotateX(90deg)" }}
      />
      {/* side: stands up from the right edge */}
      <div
        className="absolute top-0"
        style={{ ...face(dark), left: SIZE, width: h, height: SIZE, transformOrigin: "left", transform: "rotateY(-90deg)" }}
      />
    </div>
  );
}

export function CandleScene() {
  return (
    <div
      role="img"
      aria-label="Illustration: five 3D candles and one dashed ghost candle for the predicted next move"
      className="relative grid h-[340px] place-items-center"
      style={{ perspective: "1400px" }}
    >
      <div
        className="relative h-[260px] w-[260px]"
        style={{ transformStyle: "preserve-3d", transform: "rotateX(58deg) rotateZ(-40deg)" }}
      >
        <div
          className="absolute -inset-6 rounded-3xl"
          style={{
            background: "radial-gradient(circle, rgba(77,216,255,0.28), rgba(124,92,255,0.12) 55%, transparent 75%)",
            border: "1px solid rgba(77,216,255,0.25)",
          }}
        />
        {CANDLES.map((candle) => (
          <Box key={candle.x} {...candle} />
        ))}
        <Box x={230} y={0} h={64} up ghost />
      </div>
    </div>
  );
}
