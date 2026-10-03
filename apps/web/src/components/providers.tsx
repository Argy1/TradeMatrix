"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";

export function Providers({ children }: { children: React.ReactNode }) {
  // One cache per browser tab; created in state so it survives re-renders.
  const [client] = useState(
    () => new QueryClient({ defaultOptions: { queries: { staleTime: 15_000 } } }),
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
