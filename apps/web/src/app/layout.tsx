import type { Metadata } from "next";
import { DM_Sans, JetBrains_Mono, Sora } from "next/font/google";

import { Footer } from "@/components/footer";
import { Header } from "@/components/header";
import { Providers } from "@/components/providers";

import "./globals.css";

// Display: Sora. Body: DM Sans. Numbers: JetBrains Mono (tabular digits). docs/08.
const sora = Sora({ variable: "--font-sora", subsets: ["latin"], weight: ["600", "700", "800"] });
const dmSans = DM_Sans({ variable: "--font-dm-sans", subsets: ["latin"] });
const mono = JetBrains_Mono({ variable: "--font-jetbrains-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: { default: "TradeMatrix AI", template: "%s · TradeMatrix AI" },
  description:
    "Crypto signals as honest probabilities: Up, Down or Neutral for the next candle, with the reasons and the track record.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${sora.variable} ${dmSans.variable} ${mono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <Providers>
          <Header />
          <main className="mx-auto w-full max-w-[1376px] flex-1 px-4 pb-16 sm:px-8">
            {children}
          </main>
          <Footer />
        </Providers>
      </body>
    </html>
  );
}
