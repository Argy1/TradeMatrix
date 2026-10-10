import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

import '../../config.dart';
import '../../theme/tokens.dart';
import '../../widgets/brand.dart';
import '../../widgets/glass.dart';
import '../../widgets/keycap.dart';
import '../../widgets/page.dart';
import '../../widgets/states.dart';

/// Email + password sign-in and sign-up through Supabase Auth. The app only holds
/// Supabase's public URL and anon key; passwords go straight to Supabase and are never
/// stored or logged here.
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _email = TextEditingController();
  final _password = TextEditingController();
  bool _signUp = false, _busy = false, _checkInbox = false;
  String? _problem;

  @override
  void dispose() {
    _email.dispose();
    _password.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final email = _email.text.trim(), password = _password.text;
    if (!email.contains('@')) return setState(() => _problem = 'Enter your email address.');
    if (password.length < 8) return setState(() => _problem = 'Use a password of at least 8 characters.');
    setState(() {
      _problem = null;
      _busy = true;
    });
    final auth = Supabase.instance.client.auth;
    try {
      if (_signUp) {
        final result = await auth.signUp(email: email, password: password);
        if (!mounted) return;
        // With email confirmation on, there is no session until the link is opened.
        if (result.session == null) return setState(() => _checkInbox = true);
      } else {
        await auth.signInWithPassword(email: email, password: password);
        if (!mounted) return;
      }
      context.canPop() ? context.pop() : context.go('/signals');
    } on AuthException catch (e) {
      if (mounted) setState(() => _problem = e.message);
    } catch (_) {
      if (mounted) setState(() => _problem = 'Could not reach the sign-in service. Please try again.');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final Widget body;
    if (!AppConfig.authConfigured) {
      body = const EmptyState(
        title: 'Sign-in is not set up in this build',
        text: 'Every signal, the chart and the track record still work without an account.',
      );
    } else if (_checkInbox) {
      body = EmptyState(
        title: 'Check your inbox',
        text: 'We sent a confirmation link to ${_email.text.trim()}. Open it, then come back and sign in.',
        action: KeyButton(
          onTap: () => setState(() {
            _checkInbox = false;
            _signUp = false;
          }),
          child: const Text('Back to sign in'),
        ),
      );
    } else {
      body = GlassCard(
        padding: const EdgeInsets.all(20),
        child: AutofillGroup(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(_signUp ? 'Create a free account' : 'Sign in', style: TmText.display(22)),
              const SizedBox(height: 6),
              Text('For your watchlist and alerts. Signals stay public either way.',
                  style: TmText.body(14, color: Tm.fg3, height: 1.45)),
              const SizedBox(height: 18),
              TextField(
                controller: _email,
                keyboardType: TextInputType.emailAddress,
                autofillHints: const [AutofillHints.email],
                autocorrect: false,
                textInputAction: TextInputAction.next,
                decoration: const InputDecoration(labelText: 'Email'),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: _password,
                obscureText: true,
                autofillHints: [_signUp ? AutofillHints.newPassword : AutofillHints.password],
                textInputAction: TextInputAction.done,
                onSubmitted: (_) => _submit(),
                decoration: InputDecoration(
                  labelText: 'Password',
                  helperText: _signUp ? 'At least 8 characters.' : null,
                ),
              ),
              if (_problem != null) ...[
                const SizedBox(height: 12),
                Semantics(liveRegion: true, child: Text(_problem!, style: TmText.body(14, color: Tm.downText))),
              ],
              const SizedBox(height: 18),
              PrimaryButton(label: _signUp ? 'Create account' : 'Sign in', busy: _busy, onTap: _submit),
              const SizedBox(height: 14),
              KeyButton(
                onTap: () => setState(() {
                  _signUp = !_signUp;
                  _problem = null;
                }),
                child: Text(_signUp ? 'I already have an account' : 'New here? Create a free account'),
              ),
            ],
          ),
        ),
      );
    }

    return TmPage(
      grid: true,
      header: const BackBar(title: 'Account'),
      children: [
        const SizedBox(height: 18),
        const Center(child: BrandLockup(logoSize: 48, nameSize: 22)),
        const SizedBox(height: 26),
        body,
      ],
    );
  }
}
