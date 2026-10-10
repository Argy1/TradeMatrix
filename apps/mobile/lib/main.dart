import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import 'app.dart';
import 'config.dart';

/// TradeMatrix AI, created by Argy.
///
/// The app is a thin client (CLAUDE.md rule 5): it draws what the API returns and never
/// computes an indicator or a probability itself.
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  if (AppConfig.authConfigured) {
    // Sign-in only. The anon key is public by design; row-level security and the API's own
    // token check protect each person's data.
    await Supabase.initialize(url: AppConfig.supabaseUrl, publishableKey: AppConfig.supabaseAnonKey);
  }
  // Light status-bar icons over the dark page.
  SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
  runApp(const ProviderScope(child: TradeMatrixApp()));
}
