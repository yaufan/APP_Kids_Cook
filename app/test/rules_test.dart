import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:animal_restaurant/core/dishes.dart';
import 'package:animal_restaurant/core/game.dart';
import 'package:animal_restaurant/core/store.dart';

/// The menu, the orders and the saved game.
void main() {
  test('five dishes, each with its own customer and steps that make sense', () {
    expect(dishes.map((d) => d.id), ['sandwich', 'fruit_skewer', 'danbing', 'milk_tea', 'dumplings']);
    expect(dishes.map((d) => d.customer).toSet().length, 5);
    for (final d in dishes) {
      for (final level in Level.values) {
        final (lo, hi) = level == Level.little ? d.little : d.big;
        expect(lo, lessThanOrEqualTo(hi));
        expect(hi, lessThanOrEqualTo(level == Level.little ? 5 : 10), reason: '${d.id}: little ones count to five');
        for (var n = lo; n <= hi; n++) {
          final steps = d.steps(n, level);
          expect(steps.length, inInclusiveRange(4, 10), reason: d.id);
          for (final s in steps) {
            expect(s.zh, isNotEmpty);
            if (s.kind == StepKind.cut || s.kind == StepKind.tapIn || s.kind == StepKind.wrap) expect(s.count, greaterThan(0), reason: '${d.id} ${s.zh}');
            if (s.kind == StepKind.build || s.kind == StepKind.finish) expect(s.sequence, isNotEmpty);
          }
        }
      }
    }
  });

  test('the counted thing in the order is what the steps count', () {
    final sandwich = dishById('sandwich')!.steps(4, Level.little);
    expect(sandwich.firstWhere((s) => s.kind == StepKind.cut).count, 4);
    expect(sandwich.firstWhere((s) => s.kind == StepKind.build).sequence.where((x) => x == 'food/tomato_slice').length, 4);
    final dumplings = dishById('dumplings')!.steps(5, Level.big);
    expect(dumplings.firstWhere((s) => s.kind == StepKind.wrap).count, 5);
    expect(dumplings.firstWhere((s) => s.kind == StepKind.boil).count, 5);
  });

  test('big children follow a longer pattern on the fruit skewer', () {
    final little = dishById('fruit_skewer')!.steps(2, Level.little).firstWhere((s) => s.kind == StepKind.build).sequence;
    final big = dishById('fruit_skewer')!.steps(2, Level.big).firstWhere((s) => s.kind == StepKind.build).sequence;
    expect(little, ['food/strawberry', 'food/banana_piece', 'food/strawberry', 'food/banana_piece']);
    expect(big.toSet().length, 3);
  });

  test('fire and boiling water always ask a grown-up first', () {
    for (final d in dishes) {
      final steps = d.steps(d.little.$1, Level.little);
      for (final (i, s) in steps.indexed) {
        final hot = s.kind == StepKind.cook || s.kind == StepKind.boil || (s.kind == StepKind.pour && s.target == 'tools/pan');
        if (hot) expect(steps.sublist(0, i).any((x) => x.kind == StepKind.adult), isTrue, reason: '${d.id} ${s.zh}');
      }
    }
  });

  test('orders change dish each time and count by the level', () {
    final r = math.Random(3);
    var g = const Game();
    String? last;
    for (var i = 0; i < 30; i++) {
      final o = g.nextOrder(r, last: last);
      expect(o.dish.id, isNot(last));
      expect(o.count, inInclusiveRange(o.dish.little.$1, o.dish.little.$2));
      last = o.dish.id;
    }
    g = g.copyWith(settings: const Settings(level: Level.big));
    final o = g.nextOrder(r);
    expect(o.count, inInclusiveRange(o.dish.big.$1, o.dish.big.$2));
  });

  test('serving gives coins and a star, and the book counts each dish', () async {
    var g = const Game().servedDish('sandwich', 6).servedDish('sandwich', 4).servedDish('milk_tea', 5);
    expect(g.coins, 15);
    expect(g.stars, 3);
    expect(g.served, 3);
    expect(g.starsOf('sandwich'), 2);
    for (var i = 0; i < 5; i++) {
      g = g.servedDish('sandwich', 1);
    }
    expect(g.starsOf('sandwich'), 3, reason: 'three at most');
    g = g.copyWith(settings: const Settings(level: Level.big, english: true, music: false));
    final store = MemoryStore()..write(g.toJson());
    final back = Game.fromJson(await store.read());
    expect(back.toJson(), g.toJson());
    expect(Game.fromJson({'coins': 'lots', 'cooked': 3}).coins, 0);
  });
}
