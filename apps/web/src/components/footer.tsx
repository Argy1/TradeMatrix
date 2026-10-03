import Link from "next/link";

import { DISCLAIMER } from "@/lib/copy";

import { Brand } from "./brand";

export function Footer() {
  return (
    <footer className="mt-auto border-t border-white/10">
      <div className="mx-auto flex max-w-[1376px] flex-col gap-6 px-4 py-10 sm:px-8 md:flex-row md:items-start md:justify-between">
        <Brand />
        <p className="max-w-2xl text-sm leading-relaxed text-muted">{DISCLAIMER}</p>
        <nav aria-label="Footer" className="flex gap-4 text-sm text-fg-2">
          <Link href="/about" className="hover:text-fg">
            About
          </Link>
          <Link href="/track-record" className="hover:text-fg">
            Track record
          </Link>
        </nav>
      </div>
    </footer>
  );
}
