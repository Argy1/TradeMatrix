/// Build-time settings, passed with `--dart-define-from-file=dart_defines.json`.
///
/// Only PUBLIC values belong in a mobile app (CLAUDE.md rule 4): the API address and
/// Supabase's URL and anon key. The Gemini key and the Supabase service key never leave
/// the server.
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'https://api-production-a829.up.railway.app',
  );
  static const wsUrl = String.fromEnvironment(
    'WS_URL',
    defaultValue: 'wss://api-production-a829.up.railway.app',
  );
  static const supabaseUrl = String.fromEnvironment('SUPABASE_URL');
  static const supabaseAnonKey = String.fromEnvironment('SUPABASE_ANON_KEY');

  /// Without the two Supabase values the app still shows every public signal;
  /// only sign-in, watchlist and alerts are switched off.
  static bool get authConfigured => supabaseUrl.isNotEmpty && supabaseAnonKey.isNotEmpty;
}
