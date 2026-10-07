"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { UnreadBadge } from "./alerts-view";
import { AuthButtons } from "./auth-buttons";
import { Brand } from "./brand";

const NAV = [
  { href: "/", label: "Markets", match: (path: string) => path === "/" || path.startsWith("/markets") },
  { href: "/track-record", label: "Track record", match: (path: string) => path.startsWith("/track-record") },
  { href: "/watchlist", label: "Watchlist", match: (path: string) => path.startsWith("/watchlist") },
  { href: "/alerts", label: "Alerts", match: (path: string) => path.startsWith("/alerts") },
  { href: "/about", label: "How it works", match: (path: string) => path.startsWith("/about") },
] as const;

export function Header() {
  const pathname = usePathname();
  return (
    <header className="mx-auto flex w-full max-w-[1376px] flex-wrap items-center justify-between gap-4 px-4 py-5 sm:px-8">
      <Brand />
      <nav aria-label="Main" className="order-3 w-full sm:order-none sm:w-auto">
        <ul className="flex flex-wrap gap-1.5">
          {NAV.map((item) => {
            const active = item.match(pathname);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={`flex min-h-11 items-center rounded-xl px-4 font-semibold ${
                    active ? "bg-white/8 font-bold text-white" : "text-fg-2 hover:text-fg"
                  }`}
                >
                  {item.label}
                  {item.href === "/alerts" && <UnreadBadge />}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <AuthButtons />
    </header>
  );
}
