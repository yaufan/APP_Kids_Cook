import 'dart:math' as math;

import 'dishes.dart';

/// What a parent set.
class Settings {
  const Settings({this.level = Level.little, this.english = false, this.music = true, this.sounds = true, this.voice = true, this.full = true});

  final Level level;

  /// Say the English word after the Mandarin (番茄, tomato).
  final bool english;
  final bool music;
  final bool sounds;
  final bool voice;

  /// The full version (bought once in parent mode later; open in tests).
  final bool full;

  Settings copyWith({Level? level, bool? english, bool? music, bool? sounds, bool? voice, bool? full}) => Settings(
        level: level ?? this.level,
        english: english ?? this.english,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
      );

  Map<String, dynamic> toJson() => {'level': level.name, 'english': english, 'music': music, 'sounds': sounds, 'voice': voice, 'full': full};

  factory Settings.fromJson(Map<String, dynamic> j) => Settings(
        level: Level.values.where((l) => l.name == j['level']).firstOrNull ?? Level.little,
        english: j['english'] as bool? ?? false,
        music: j['music'] as bool? ?? true,
        sounds: j['sounds'] as bool? ?? true,
        voice: j['voice'] as bool? ?? true,
        full: j['full'] as bool? ?? true,
      );
}

/// Everything the app keeps: coins and stars, how often each dish was made,
/// the parent's settings. One small file (store.dart).
class Game {
  const Game({this.coins = 0, this.stars = 0, this.cooked = const {}, this.served = 0, this.settings = const Settings()});

  final int coins;
  final int stars;

  /// Times each dish was made and served.
  final Map<String, int> cooked;
  final int served;
  final Settings settings;

  /// Stars on a dish in the recipe book: one each time, up to three.
  int starsOf(String dish) => math.min(3, cooked[dish] ?? 0);

  Game copyWith({int? coins, int? stars, Map<String, int>? cooked, int? served, Settings? settings}) => Game(
        coins: coins ?? this.coins,
        stars: stars ?? this.stars,
        cooked: cooked ?? this.cooked,
        served: served ?? this.served,
        settings: settings ?? this.settings,
      );

  /// A dish served: coins for the customer, a star, and it goes in the book.
  Game servedDish(String dish, int coins) => copyWith(
        coins: this.coins + coins,
        stars: stars + 1,
        served: served + 1,
        cooked: {...cooked, dish: (cooked[dish] ?? 0) + 1},
      );

  /// The next customer's order: the dishes take turns, a different one from
  /// the last, the number by the parent's level.
  Order nextOrder(math.Random r, {String? last}) {
    final choices = [for (final d in dishes) if (d.id != last) d];
    final dish = choices[r.nextInt(choices.length)];
    return Order(dish, dish.countFor(settings.level, r));
  }

  Map<String, dynamic> toJson() => {'version': 1, 'coins': coins, 'stars': stars, 'cooked': cooked, 'served': served, 'settings': settings.toJson()};

  factory Game.fromJson(Map<String, dynamic>? j) {
    if (j == null) return const Game();
    final cooked = j['cooked'];
    int n(Object? o) => o is int && o >= 0 ? o : 0;
    return Game(
      coins: n(j['coins']),
      stars: n(j['stars']),
      cooked: {if (cooked is Map) for (final e in cooked.entries) if (e.key is String && e.value is int) e.key as String: e.value as int},
      served: n(j['served']),
      settings: Settings.fromJson(j['settings'] is Map ? (j['settings'] as Map).cast<String, dynamic>() : const {}),
    );
  }
}
