import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'dishes.dart';
import 'game.dart';
import 'sounds.dart';
import 'store.dart';
import 'voice.dart';

/// What time it is (tests and screenshots set it).
final clockProvider = Provider<DateTime Function()>((ref) => DateTime.now);

/// Dice for orders (tests give a seeded one).
final randomProvider = Provider<math.Random>((ref) => math.Random());

final storeProvider = Provider<GameStore>((ref) => MemoryStore());
final savedGameProvider = Provider<Game>((ref) => const Game());
final soundsProvider = Provider<Sounds>((ref) => const SilentSounds());
final voiceProvider = Provider<Voice>((ref) => const SilentVoice());

/// The game; every change is saved straight away.
final gameProvider = NotifierProvider<GameNotifier, Game>(GameNotifier.new);

class GameNotifier extends Notifier<Game> {
  @override
  Game build() => ref.read(savedGameProvider);

  void change(Game Function(Game g) f) {
    final next = f(state);
    if (identical(next, state)) return;
    state = next;
    ref.read(storeProvider).write(next.toJson());
  }

  void settings(Settings Function(Settings s) f) => change((g) => g.copyWith(settings: f(g.settings)));
}

/// The customer at the counter: their order, how many of its steps are
/// done (so a child who leaves the kitchen mid-recipe goes on from there),
/// and whether it was served.
class Visit {
  const Visit(this.order, {this.served = false, this.at = 0});

  final Order order;
  final bool served;

  /// Steps of the recipe done so far.
  final int at;
}

final visitProvider = NotifierProvider<VisitNotifier, Visit>(VisitNotifier.new);

class VisitNotifier extends Notifier<Visit> {
  @override
  Visit build() {
    // A parent who changes the level changes the order waiting at the
    // counter too (the same customer, the new level's number), not only
    // the next customer's.
    ref.listen(gameProvider.select((g) => g.settings.level), (_, level) {
      if (state.served) return;
      final dish = state.order.dish;
      state = Visit(Order(dish, dish.countFor(level, ref.read(randomProvider))));
    });
    return Visit(ref.read(gameProvider).nextOrder(ref.read(randomProvider)));
  }

  /// [at] steps of the recipe are done.
  void progress(int at) {
    if (state.served || at == state.at) return;
    state = Visit(state.order, at: at);
  }

  /// The dish went out: coins and a star.
  void served(int coins) {
    if (state.served) return;
    ref.read(gameProvider.notifier).change((g) => g.servedDish(state.order.dish.id, coins));
    state = Visit(state.order, served: true);
  }

  void next() => state = Visit(ref.read(gameProvider).nextOrder(ref.read(randomProvider), last: state.order.dish.id));

  /// A particular order (the walk-through and the demo use it).
  void take(Order order) => state = Visit(order);
}

/// A simple on/off flag shared by the screens and the play-time keeper.
class Flag extends Notifier<bool> {
  @override
  bool build() => false;

  void set(bool on) => state = on;
}

/// The app is in the background: nothing is said (RestGuard sets it).
final hiddenProvider = NotifierProvider<Flag, bool>(Flag.new);

/// Whether a dish is being made: when the play time is up, it is finished
/// and served first (at most [RestGuard.finishDish]). The screen making it
/// holds it, so a screen going away cannot let go of another one's dish.
final busyProvider = Provider<Busy>((ref) => Busy());

class Busy {
  Object? _owner;

  bool get busy => _owner != null;

  /// [owner] is making a dish.
  void start(Object owner) => _owner = owner;

  /// [owner]'s dish is done (or it went away); another screen's goes on.
  void end(Object owner) {
    if (identical(_owner, owner)) _owner = null;
  }
}
