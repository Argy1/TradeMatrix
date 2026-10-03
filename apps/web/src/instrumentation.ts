// Runs once when the Next.js server starts (Node or Edge).
import * as Sentry from "@sentry/nextjs";

import { sentryOptions } from "@/lib/sentry-options";

export async function register() {
  Sentry.init({ ...sentryOptions, environment: process.env.VERCEL_ENV ?? "development" });
}

// Reports errors thrown while rendering server components and route handlers.
export const onRequestError = Sentry.captureRequestError;
