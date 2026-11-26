import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/game.dart';
import '../core/providers.dart';
import '../features/book/book_screen.dart';
import '../features/kitchen/kitchen_screen.dart';
import '../features/parent/parent_gate.dart';
import '../features/parent/parent_screen.dart';
import '../features/rest/rest_screen.dart';
import '../features/restaurant/restaurant_screen.dart';
import 'strings.dart';
import 'theme.dart';

final routerProvider = Provider<GoRouter>((ref) {
  final resting = ref.read(gameProvider).resting(ref.read(clockProvider)());
  final router = GoRouter(
    initialLocation: resting ? '/rest' : '/',
    // Always start here, whatever page another app asks the phone to open.
    overridePlatformDefaultLocation: true,
    redirect: (_, state) => state.matchedLocation == '/parent' && !ParentPass.take() ? '/' : null,
    routes: [
      GoRoute(path: '/', builder: (_, _) => const RestaurantScreen()),
      GoRoute(path: '/kitchen', builder: (_, _) => const KitchenScreen()),
      GoRoute(path: '/book', builder: (_, _) => const BookScreen()),
      GoRoute(path: '/parent', builder: (_, _) => const ParentScreen()),
      GoRoute(path: '/rest', builder: (_, _) => const RestScreen()),
    ],
  );
  ref.onDispose(router.dispose);
  return router;
});

class RestaurantApp extends ConsumerWidget {
  const RestaurantApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(gameProvider.select((g) => g.settings));
    ref.read(soundsProvider)
      ..music = settings.music
      ..effects = settings.sounds;
    return MaterialApp.router(
      title: Strings.appName,
      debugShowCheckedModeBanner: false,
      theme: ClayTheme.light(),
      locale: const Locale('zh', 'TW'),
      supportedLocales: const [Locale('zh', 'TW')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: ref.watch(routerProvider),
      builder: (_, child) => RestGuard(child: child ?? const SizedBox()),
    );
  }
}

/// Keeps the parent's play time (docs/design.md 「每天可以玩多久」): when
/// the sitting has had the minutes they set, the restaurant closes and the
/// child is sent to help set the table; an hour later (or when a parent
/// says so) play can go on. A dish being made is finished and served first
/// (at most [finishDish] more).
///
/// Only play counts: not parent mode or the parent gate, not the rest, not
/// the app in the background, and a phone clock moved back gives nothing
/// back. The sitting is saved, so closing the app and opening it again
/// within ten minutes goes on with it (the closed time is not play); ten
/// minutes or more away is a rest, and a new sitting starts.
///
/// It also shuts parent mode when the app goes to the background or after
/// [parentIdle] without a touch, so a child picking up the phone later
/// finds the restaurant, not the settings.
class RestGuard extends ConsumerStatefulWidget {
  const RestGuard({super.key, required this.child});

  final Widget child;

  static const check = Duration(seconds: 2);

  /// The sitting is saved this often (and when the app is hidden).
  static const saveEvery = Duration(seconds: 30);

  /// How long a dish being made may go on after the time is up (served
  /// and thanked for).
  static const finishDish = Duration(minutes: 3);

  static const parentIdle = Duration(minutes: 5);

  @override
  ConsumerState<RestGuard> createState() => _RestGuardState();
}

class _RestGuardState extends ConsumerState<RestGuard> {
  Timer? _timer;
  AppLifecycleListener? _life;
  late final GoRouter _router;

  /// Play time in this sitting.
  var _played = Duration.zero;

  /// When the time counted next began, and whether it is play.
  late DateTime _from;
  var _playing = false;

  /// Time in sight since the sitting was last saved.
  var _unsaved = Duration.zero;
  DateTime? _hiddenAt;
  late DateTime _touched;

  /// The clock (read once: the gate going away as the app is torn down
  /// still tells this, and the providers cannot be read then).
  late final DateTime Function() _clock;

  DateTime get _now => _clock();

  String get _path => _router.routerDelegate.currentConfiguration.isEmpty ? '' : _router.state.matchedLocation;

  bool get _inParent => _path.startsWith('/parent') || parentShowing.value > 0;

  @override
  void initState() {
    super.initState();
    _router = ref.read(routerProvider);
    _clock = ref.read(clockProvider);
    final now = _now;
    _played = ref.read(gameProvider).sitting?.goOn(now) ?? Duration.zero;
    _from = _touched = now;
    _router.routerDelegate.addListener(_changed);
    parentShowing.addListener(_changed);
    _startTimer();
    _life = AppLifecycleListener(onHide: _hide, onShow: _show);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _look();
      _save();
      _check();
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _life?.dispose();
    _router.routerDelegate.removeListener(_changed);
    parentShowing.removeListener(_changed);
    super.dispose();
  }

  void _startTimer() {
    _timer?.cancel();
    _timer = Timer.periodic(RestGuard.check, (_) => _tick());
  }

  /// Whether the time from now on is play.
  void _look() {
    final path = _path;
    _playing = _hiddenAt == null && path.isNotEmpty && !_inParent && path != '/rest';
  }

  /// The time since the last count goes to what was being done until now
  /// (a phone clock moved back counts nothing).
  void _count() {
    final now = _now, d = now.difference(_from);
    _from = now;
    if (d <= Duration.zero || _hiddenAt != null) return;
    _unsaved += d;
    if (_playing) _played += d;
  }

  /// The screen changed (or the gate opened or shut): counted the moment it
  /// happens, not at the next check.
  void _changed() {
    if (!mounted) return;
    _count();
    _look();
  }

  void _tick() {
    if (!mounted) return;
    _count();
    _look();
    if (_unsaved >= RestGuard.saveEvery) _save();
    _check();
  }

  void _save() {
    _unsaved = Duration.zero;
    final s = Sitting(_played, _now);
    ref.read(gameProvider.notifier).change((g) => g.sat(s));
  }

  void _hide() {
    if (!mounted || _hiddenAt != null) return;
    _count();
    _hiddenAt = _now;
    _look();
    _timer?.cancel();
    ref.read(hiddenProvider.notifier).set(true);
    ref.read(voiceProvider).stop();
    if (_path.startsWith('/parent')) _closeParent();
    _save();
  }

  void _show() {
    final at = _hiddenAt;
    if (!mounted || at == null) return;
    final now = _now;
    _hiddenAt = null;
    ref.read(hiddenProvider.notifier).set(false);
    // Ten minutes or more away is a rest: a new sitting.
    if (now.difference(at) >= Sitting.awayIsRest) _played = Duration.zero;
    _from = _touched = now;
    _look();
    _save();
    _startTimer();
    _check();
  }

  /// Parent mode left open (the app hidden, or no touch for a while): back
  /// to the pet, and the gate has to be passed again.
  void _closeParent() {
    ParentPass.take();
    _router.go('/');
  }

  void _check() {
    if (!mounted || _hiddenAt != null) return;
    final path = _path;
    if (path.isEmpty) return;
    final now = _now;
    if (now.isBefore(_touched)) _touched = now;
    if (path.startsWith('/parent')) {
      if (now.difference(_touched) >= RestGuard.parentIdle) _closeParent();
      return;
    }
    if (_inParent) return; // the gate is open
    final game = ref.read(gameProvider.notifier);
    final since = ref.read(gameProvider).restSince;
    if (since != null) {
      // The phone's clock moved back during the rest: the hour starts
      // again from now (so it neither ends early nor lasts for ever).
      if (now.isBefore(since)) game.change((g) => g.rest(now));
      if (ref.read(gameProvider).resting(now)) {
        if (path != '/rest') _router.go('/rest');
        return;
      }
      _played = Duration.zero;
      game.change((g) => g.playOn(now));
      if (path == '/rest') _router.go('/');
      return;
    }
    if (path == '/rest') {
      _router.go('/');
      return;
    }
    final over = _played - Duration(minutes: ref.read(gameProvider).settings.minutes);
    if (over.isNegative) return;
    // A dish being made is finished and served first (at most three minutes more).
    if (ref.read(busyProvider).busy && over < RestGuard.finishDish) return;
    _played = Duration.zero;
    _unsaved = Duration.zero;
    game.change((g) => g.rest(now));
    _router.go('/rest');
  }

  @override
  Widget build(BuildContext context) => Listener(
        behavior: HitTestBehavior.translucent,
        onPointerDown: (_) => _touched = _now,
        child: widget.child,
      );
}

