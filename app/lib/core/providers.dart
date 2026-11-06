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

/// The customer at the counter: their order, and whether it was served.
class Visit {
  const Visit(this.order, {this.served = false});

  final Order order;
  final bool served;
}

final visitProvider = NotifierProvider<VisitNotifier, Visit>(VisitNotifier.new);

class VisitNotifier extends Notifier<Visit> {
  @override
  Visit build() => Visit(ref.read(gameProvider).nextOrder(ref.read(randomProvider)));

  /// The dish went out: coins and a star.
  void served(int coins) {
    if (state.served) return;
    ref.read(gameProvider.notifier).change((g) => g.servedDish(state.order.dish.id, coins));
    state = Visit(state.order, served: true);
  }

  void next() => state = Visit(ref.read(gameProvider).nextOrder(ref.read(randomProvider), last: state.order.dish.id));
}
