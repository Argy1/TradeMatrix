import Link from "next/link";

import { AuthButtons } from "./auth-buttons";
import { Brand } from "./brand";

const NAV = [
  { href: "/", label: "Markets" },
  { href: "/track-record", label: "Track record" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/about", label: "How it works" },
] as const;

export function Header() {
  return (
    <header className="mx-auto flex w-full max-w-[1376px] flex-wrap items-center justify-between gap-4 px-4 py-5 sm:px-8">
      <Brand />
      <nav aria-label="Main" className="order-3 w-full sm:order-none sm:w-auto">
        <ul className="flex flex-wrap gap-1 text-sm font-medium text-fg-2">
          {NAV.map((item) => (
            <li key={item.href}>
              <Link href={item.href} className="block rounded-lg px-3 py-2 hover:text-fg">
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
      <AuthButtons />
    </header>
  );
}
