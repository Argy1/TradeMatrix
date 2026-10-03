import Link from "next/link";

/** Logo lockup: mark + "TradeMatrix AI" + "Created by Argy" (docs/01, docs/08). */
export function Brand({ linked = true }: { linked?: boolean }) {
  const lockup = (
    <span className="flex items-center gap-3">
      <span
        aria-hidden
        className="relative grid h-[42px] w-[42px] place-items-center overflow-hidden rounded-[12px]"
        style={{
          background: "linear-gradient(135deg, #4DD8FF, #7C5CFF)",
          boxShadow: "0 4px 0 #3B2FA8",
        }}
      >
        <span
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.6) 1px, transparent 1px)",
            backgroundSize: "10px 10px",
          }}
        />
        <span className="relative font-display text-lg font-extrabold text-white">T</span>
      </span>
      <span className="flex flex-col leading-tight">
        <span className="font-display text-lg font-bold text-fg">
          TradeMatrix <span className="text-cyan">AI</span>
        </span>
        <span className="text-xs text-muted">Created by Argy</span>
      </span>
    </span>
  );
  return linked ? (
    <Link href="/" aria-label="TradeMatrix AI, created by Argy. Home" className="rounded-xl">
      {lockup}
    </Link>
  ) : (
    lockup
  );
}
