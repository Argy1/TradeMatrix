// Shared Sentry settings for the browser and the server. Sentry stays off without a DSN.
// Privacy first (docs/06): no user info, cookies, headers or bodies, and never the one-time
// login codes that appear in auth callback URLs.
export const sentryOptions = {
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  enabled: Boolean(process.env.NEXT_PUBLIC_SENTRY_DSN),
  tracesSampleRate: 0.1, // 10% of page loads: enough to spot slow pages on the free plan
  dataCollection: {
    userInfo: false,
    cookies: false,
    httpHeaders: false,
    httpBodies: [],
    urlQueryParams: { deny: ["code", "token", "token_hash", "access_token", "refresh_token"] },
  },
};
