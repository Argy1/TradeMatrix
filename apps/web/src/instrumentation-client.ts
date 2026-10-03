// Runs in the browser before the app starts.
import * as Sentry from "@sentry/nextjs";

import { sentryOptions } from "@/lib/sentry-options";

Sentry.init({ ...sentryOptions, environment: process.env.NEXT_PUBLIC_VERCEL_ENV ?? "development" });

export const onRouterTransitionStart = Sentry.captureRouterTransitionStart;
