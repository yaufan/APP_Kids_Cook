import 'dart:math' as math;

import 'dishes.dart';

/// What a parent set.
class Settings {
  const Settings({this.level = Level.little, this.english = false, this.music = true, this.sounds = true, this.voice = true, this.full = true, this.minutes = 15});

  final Level level;

  /// Say the English word after the Mandarin (番茄, tomato).
  final bool english;
  final bool music;
  final bool sounds;
  final bool voice;

  /// The full version (bought once in parent mode later; open in tests).
  final bool full;

  /// How long one sitting may be before the restaurant closes (one of
  /// [minuteChoices]).
  final int minutes;

  static const minuteChoices = [10, 15, 20, 30];

  Settings copyWith({Level? level, bool? english, bool? music, bool? sounds, bool? voice, bool? full, int? minutes}) => Settings(
        level: level ?? this.level,
        english: english ?? this.english,
        music: music ?? this.music,
        sounds: sounds ?? this.sounds,
        voice: voice ?? this.voice,
        full: full ?? this.full,
        minutes: minutes ?? this.minutes,
      );

  Map<String, dynamic> toJson() => {'level': level.name, 'english': english, 'music': music, 'sounds': sounds, 'voice': voice, 'full': full, 'minutes': minutes};

  factory Settings.fromJson(Map<String, dynamic> j) => Settings(
        level: Level.values.where((l) => l.name == j['level']).firstOrNull ?? Level.little,
        english: j['english'] as bool? ?? false,
        music: j['music'] as bool? ?? true,
        sounds: j['sounds'] as bool? ?? true,
        voice: j['voice'] as bool? ?? true,
        full: j['full'] as bool? ?? true,
        minutes: minuteChoices.contains(j['minutes']) ? j['minutes'] as int : 15,
      );
}

/// The sitting going on: the play time in it so far and when the app was
/// last seen open. Closing the app (or leaving it in the background) for
/// less than [awayIsRest] goes on with the same sitting, and that time is
/// not play; [awayIsRest] or more is a rest, and a new sitting starts.
class Sitting {
  const Sitting(this.played, this.seen);

  final Duration played;
  final DateTime seen;

  static const awayIsRest = Duration(minutes: 10);

  /// The play time to go on from when the app is open again at [now]: the
  /// same sitting within ten minutes, and also when the phone's clock was
  /// moved back (that gives no extra time); a new sitting after.
  Duration goOn(DateTime now) => now.difference(seen) >= awayIsRest ? Duration.zero : played;

  Map<String, dynamic> toJson() => {'played': played.inSeconds, 'seen': seen.toIso8601String()};

  static Sitting? fromJson(Object? j) {
    if (j is! Map) return null;
    final played = j['played'], seen = DateTime.tryParse(j['seen'] as String? ?? '');
    if (played is! int || seen == null) return null;
    return Sitting(Duration(seconds: played.clamp(0, 24 * 3600)), seen);
  }
}

/// The parent gate's lock: three wrong answers in a row lock it for a
/// minute, the next three for five, then fifteen. Saved, so closing the app
/// does not open it; a right answer starts again from nothing.
class GateLock {
  const GateLock({this.misses = 0, this.level = 0, this.until});

  /// Wrong answers in a row since the last lock.
  final int misses;

  /// Locks since the last right answer.
  final int level;
  final DateTime? until;

  static const maxMisses = 3;
  static const steps = [Duration(minutes: 1), Duration(minutes: 5), Duration(minutes: 15)];

  /// How long the lock at [level] lasts.
  Duration get length => steps[(level - 1).clamp(0, steps.length - 1)];

  /// Whether the gate is locked at [now].
  bool locked(DateTime now) => until != null && now.isBefore(until!);

  /// The lock made right for [now]: a phone clock moved back cannot make it
  /// last longer than its own length (or it might never end).
  GateLock settled(DateTime now) {
    final u = until;
    if (u == null || u.difference(now) <= length) return this;
    return GateLock(misses: misses, level: level, until: now.add(length));
  }

  /// A wrong answer at [now].
  GateLock wrong(DateTime now) {
    if (misses + 1 < maxMisses) return GateLock(misses: misses + 1, level: level, until: until);
    final next = math.min(level + 1, steps.length);
    return GateLock(level: next, until: now.add(steps[next - 1]));
  }

  Map<String, dynamic> toJson() => {'misses': misses, 'level': level, if (until != null) 'until': until!.toIso8601String()};

  factory GateLock.fromJson(Object? j) {
    if (j is! Map) return const GateLock();
    return GateLock(
      misses: (j['misses'] as int? ?? 0).clamp(0, maxMisses - 1),
      level: (j['level'] as int? ?? 0).clamp(0, steps.length),
      until: DateTime.tryParse(j['until'] as String? ?? ''),
    );
  }
}

/// Everything the app keeps: coins and stars, how often each dish was made,
/// the parent's settings. One small file (store.dart).
class Game {
  const Game({this.coins = 0, this.stars = 0, this.cooked = const {}, this.served = 0, this.settings = const Settings(), this.restSince, this.sitting, this.gate = const GateLock()});

  final int coins;
  final int stars;

  /// Times each dish was made and served.
  final Map<String, int> cooked;
  final int served;
  final Settings settings;

  /// When the restaurant closed (the play time was up); null when open.
  final DateTime? restSince;

  /// The sitting going on (saved, so closing and opening the app again
  /// soon goes on with it).
  final Sitting? sitting;
  final GateLock gate;

  static const restLength = Duration(hours: 1);

  /// Closed for an hour after the play time ran out. A phone clock moved
  /// back (now before the rest began) does not open it early (RestGuard
  /// then counts the hour again from now, so never more than one).
  bool resting(DateTime now) => restSince != null && now.difference(restSince!) < restLength;

  /// Stars on a dish in the recipe book: one each time, up to three.
  int starsOf(String dish) => math.min(3, cooked[dish] ?? 0);

  Game copyWith({int? coins, int? stars, Map<String, int>? cooked, int? served, Settings? settings, DateTime? restSince, bool clearRest = false, Sitting? sitting, GateLock? gate}) => Game(
        coins: coins ?? this.coins,
        stars: stars ?? this.stars,
        cooked: cooked ?? this.cooked,
        served: served ?? this.served,
        settings: settings ?? this.settings,
        restSince: clearRest ? null : (restSince ?? this.restSince),
        sitting: sitting ?? this.sitting,
        gate: gate ?? this.gate,
      );

  /// The play time is up at [now]: the restaurant closes for an hour.
  Game rest(DateTime now) => copyWith(restSince: now, sitting: Sitting(Duration.zero, now));

  /// The hour is over, or a parent let play go on: a new sitting.
  Game playOn(DateTime now) => copyWith(clearRest: true, sitting: Sitting(Duration.zero, now));

  Game sat(Sitting s) => copyWith(sitting: s);

  Game withGate(GateLock lock) => copyWith(gate: lock);

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

  Map<String, dynamic> toJson() => {
        'version': 1,
        'coins': coins,
        'stars': stars,
        'cooked': cooked,
        'served': served,
        'settings': settings.toJson(),
        if (restSince != null) 'restSince': restSince!.toIso8601String(),
        if (sitting != null) 'sitting': sitting!.toJson(),
        'gate': gate.toJson(),
      };

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
      restSince: DateTime.tryParse(j['restSince'] as String? ?? ''),
      sitting: Sitting.fromJson(j['sitting']),
      gate: GateLock.fromJson(j['gate']),
    );
  }
}
