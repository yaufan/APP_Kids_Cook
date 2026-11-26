import 'dart:async';

import 'package:animal_restaurant/app/app.dart';
import 'package:animal_restaurant/app/strings.dart';
import 'package:animal_restaurant/core/dishes.dart';
import 'package:animal_restaurant/core/game.dart';
import 'package:animal_restaurant/core/providers.dart';
import 'package:animal_restaurant/core/sounds.dart';
import 'package:animal_restaurant/core/speech.dart';
import 'package:animal_restaurant/core/voice.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'helpers.dart';

/// A voice that takes as long as the test says: each line is "being said"
/// until [finish].
class HoldingVoice extends RecordingVoice {
  Completer<void>? _line;

  @override
  Future<void> say(String zh, {String? en}) {
    super.say(zh, en: en);
    _line?.complete();
    final c = _line = Completer<void>();
    return c.future;
  }

  void finish() {
    _line?.complete();
    _line = null;
  }
}

/// 0.1.2: what the review of the sibling apps found, checked here: the play
/// time (the restaurant closes), the back key, the kitchen remembering the
/// dish, the voice, the pouring sound, the narrow phone, the parent gate.
void main() {
  final morning = DateTime(2026, 11, 9, 10);
  Dish dish(String id) => dishById(id)!;

  /// Opens the kitchen on [order], [at] steps already done.
  Future<void> kitchen(TestApp app, Order order, {int at = 0}) async {
    app.container.read(visitProvider.notifier)
      ..take(order)
      ..progress(at);
    await app.settle(300);
    await app.tapLabel(Strings.start, ms: 900);
    expect(app.location, '/kitchen');
  }

  group('play time', () {
    testWidgets('after the minutes a parent set, the restaurant closes', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      app.now = app.now.add(const Duration(minutes: 14));
      await app.settle(2600);
      expect(app.location, '/');
      app.now = app.now.add(const Duration(minutes: 1, seconds: 10));
      await app.settle(2600);
      expect(app.location, '/rest');
      expect(find.byKey(const ValueKey('rest-line')), findsOneWidget);
      expect(app.voice.said.last, spoken('${Strings.restTitle}${Strings.restLine}'));
      expect(app.sounds.played, contains('closing'));
      expect(app.sounds.music, isNull, reason: 'a closed restaurant is quiet');
      expect(await tester.binding.handlePopRoute(), isTrue);
      await app.settle();
      expect(app.location, '/rest');
      app.now = app.now.add(const Duration(minutes: 61));
      await app.settle(2600);
      expect(app.location, '/');
      expect(app.game.restSince, isNull);
      await app.end();
    });

    testWidgets('a dish being made is finished first, at most three minutes', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      await kitchen(app, Order(dish('danbing'), 1));
      app.now = app.now.add(const Duration(minutes: 15, seconds: 10));
      await app.settle(2600);
      expect(app.location, '/kitchen');
      app.now = app.now.add(const Duration(minutes: 3));
      await app.settle(2600);
      expect(app.location, '/rest');
      expect(app.visit.at, 0, reason: 'the dish waits for next time');
      await app.end();
    });

    testWidgets('parent mode and the gate are not play time; the parent sets the minutes', (tester) async {
      final app = await TestApp.start(tester, game: const Game(settings: Settings(minutes: 20)), now: morning);
      app.now = app.now.add(const Duration(minutes: 15));
      await app.settle(2600);
      await app.tapLabel(Strings.parent, ms: 600);
      app.now = app.now.add(const Duration(minutes: 3));
      await app.settle(2600);
      await app.answerGate();
      expect(app.location, '/parent');
      app.now = app.now.add(const Duration(minutes: 4));
      await app.settle(2600);
      expect(app.location, '/parent');
      await tester.tap(find.byTooltip(Strings.back));
      await app.settle(2600);
      expect(app.location, '/', reason: '15 of the 20 minutes played');
      app.now = app.now.add(const Duration(minutes: 6));
      await app.settle(2600);
      expect(app.location, '/rest');
      expect(Settings.fromJson({'minutes': 45}).minutes, 15);
      await app.end();
    });

    testWidgets('the background is not play time, and a clock moved back gives none', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      app.now = app.now.add(const Duration(minutes: 10));
      await app.settle(2600);
      app.hide();
      app.now = app.now.add(const Duration(minutes: 8));
      await app.settle(600);
      app.show();
      await app.settle(2600);
      app.now = app.now.subtract(const Duration(hours: 2));
      await app.settle(2600);
      expect(app.location, '/');
      app.now = app.now.add(const Duration(minutes: 6));
      await app.settle(2600);
      expect(app.location, '/rest', reason: '10 + 6 minutes played');
      await app.end();
    });

    testWidgets('closing the app and opening it soon goes on; ten minutes away is a new sitting', (tester) async {
      final soon = Game(sitting: Sitting(const Duration(minutes: 13), morning.subtract(const Duration(minutes: 4))));
      final app = await TestApp.start(tester, game: soon, now: morning);
      app.now = app.now.add(const Duration(minutes: 2, seconds: 10));
      await app.settle(2600);
      expect(app.location, '/rest');
      await app.end();

      final later = Game(sitting: Sitting(const Duration(minutes: 13), morning.subtract(const Duration(minutes: 10))));
      final again = await TestApp.start(tester, game: later, now: morning);
      again.now = again.now.add(const Duration(minutes: 3));
      await again.settle(2600);
      expect(again.location, '/');
      await again.end();
    });

    testWidgets('the restaurant stays closed after a restart and a clock moved back; a parent can open it', (tester) async {
      final app = await TestApp.start(tester, game: Game(restSince: morning.subtract(const Duration(minutes: 20))), now: morning);
      expect(app.location, '/rest');
      app.now = app.now.subtract(const Duration(days: 2));
      await app.settle(2600);
      expect(app.location, '/rest');
      await app.tapLabel(Strings.restParent, ms: 600);
      await app.answerGate();
      expect(app.location, '/');
      expect(app.game.restSince, isNull);
      await app.end();
    });
  });

  group('the back key', () {
    testWidgets('never closes the app', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      expect(await tester.binding.handlePopRoute(), isTrue, reason: 'the restaurant: nothing');
      await app.settle();
      expect(app.location, '/');
      await app.tapLabel(Strings.start, ms: 900);
      expect(app.location, '/kitchen');
      expect(await tester.binding.handlePopRoute(), isTrue);
      await app.settle(600);
      expect(app.location, '/');
      await app.tapLabel(Strings.book, ms: 900);
      expect(await tester.binding.handlePopRoute(), isTrue);
      await app.settle(600);
      expect(app.location, '/');
      await app.tapLabel(Strings.parent, ms: 600);
      await app.answerGate();
      expect(app.location, '/parent');
      expect(await tester.binding.handlePopRoute(), isTrue);
      await app.settle(600);
      expect(app.location, '/');
      await app.end();
    });
  });

  group('the kitchen', () {
    testWidgets('going back mid-recipe keeps the dish: the next time goes on from that step', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      await kitchen(app, Order(dish('danbing'), 1), at: 1);
      final steps = Order(dish('danbing'), 1).stepsFor(Level.little);
      expect(find.text(steps[1].zh), findsOneWidget);
      // One egg into the bowl.
      await app.tapLabel(Strings.tapIn, ms: 1600);
      await app.settle(1600);
      expect(find.text(steps[2].zh), findsOneWidget);
      await app.tapLabel(Strings.back, ms: 900);
      expect(app.location, '/');
      expect(app.visit.at, 2);
      await app.tapLabel(Strings.start, ms: 900);
      expect(find.text(steps[2].zh), findsOneWidget, reason: 'straight back to stirring');
      await app.end();
    });

    testWidgets('pouring with two fingers: the sound stops when they let go', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      await kitchen(app, Order(dish('milk_tea'), 1), at: 2);
      expect(find.text('倒茶，倒到線就放開'), findsOneWidget);
      final area = tester.getRect(find.byType(Scaffold).last);
      final one = await tester.startGesture(area.center);
      await tester.pump(const Duration(milliseconds: 300));
      final two = await tester.startGesture(area.center + const Offset(60, 40));
      await tester.pump(const Duration(milliseconds: 300));
      await two.up();
      await one.up();
      await tester.pump(const Duration(milliseconds: 100));
      app.sounds.played.clear();
      await app.settle(6000);
      expect(app.sounds.played.where((s) => s == 'pour'), isEmpty);
      await app.end();
    });

    testWidgets('the next step waits for what was just said (a count)', (tester) async {
      final voice = HoldingVoice();
      final app = await TestApp.start(tester, now: morning, voice: voice);
      await kitchen(app, Order(dish('danbing'), 1), at: 1);
      final steps = Order(dish('danbing'), 1).stepsFor(Level.little);
      await app.tapLabel(Strings.tapIn, ms: 1600);
      expect(voice.said.last, '一');
      await app.settle(3000);
      expect(find.text(steps[2].zh), findsNothing, reason: '「一」 is still being said');
      voice.finish();
      await app.settle(1200);
      expect(find.text(steps[2].zh), findsOneWidget);
      await app.end();
    });
  });

  group('the order', () {
    test('numbers are said the way people say them: 兩片, not 二片', () {
      expect(spoken(Strings.order(Order(dish('sandwich'), 2))), '我想要番茄起司三明治，要兩片番茄');
      expect(spoken('切成 4 塊'), '切成四塊');
      expect(spoken('打 1 顆蛋'), '打一顆蛋');
      expect(spoken('包 6 顆水餃：放餡，再捏起來'), '包六顆水餃：放餡，再捏起來');
      expect(amount(10), '十');
      expect(amount(12), '十二');
      expect(amount(22), '二十二');
    });

    testWidgets('the customer says it with 兩', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      app.container.read(visitProvider.notifier).take(Order(dish('sandwich'), 2));
      await app.settle(600);
      expect(app.voice.said.last, '我想要番茄起司三明治，要兩片番茄');
      await app.end();
    });

    testWidgets('a new level changes the order at the counter now, not only the next one', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      app.container.read(visitProvider.notifier).take(Order(dish('dumplings'), 2));
      await app.settle(600);
      await app.tapLabel(Strings.parent, ms: 600);
      await app.answerGate();
      final said = app.voice.said.length;
      await tester.tap(find.byKey(const ValueKey('level-big')));
      await app.settle(600);
      expect(app.visit.order.dish.id, 'dumplings', reason: 'the same customer');
      expect(app.visit.order.count, inInclusiveRange(4, 6));
      expect(app.voice.said.length, said, reason: 'not over parent mode');
      await tester.tap(find.byTooltip(Strings.back));
      await app.settle(900);
      expect(app.voice.said.last, spoken(Strings.order(app.visit.order)), reason: 'said on coming back');
      await app.end();
    });
  });

  testWidgets('a narrow phone with lots of coins: the parent lock stays on screen', (tester) async {
    final app = await TestApp.start(tester, game: const Game(coins: 12345, stars: 1234), size: const Size(1080, 1920), ratio: 3, now: morning);
    expect(tester.takeException(), isNull, reason: 'no overflow');
    final lock = tester.getRect(find.bySemanticsLabel(Strings.parent).first);
    expect(lock.right, lessThanOrEqualTo(360));
    expect(lock.left, greaterThan(250));
    await app.end();
  });

  group('the parent gate', () {
    testWidgets('locks 1, then 5 minutes, remembered after a restart', (tester) async {
      Future<void> wrong(TestApp app) async {
        final before = app.game.gate;
        for (var i = 0; i < 2 && identical(app.game.gate, before); i++) {
          await tester.tap(find.byKey(const ValueKey('gate-key-0')));
          await tester.pump();
        }
      }

      final app = await TestApp.start(tester, now: morning);
      await app.tapLabel(Strings.parent, ms: 600);
      for (var i = 0; i < 3; i++) {
        await wrong(app);
      }
      expect(app.game.gate.until, app.now.add(const Duration(minutes: 1)));
      final saved = Game.fromJson(app.store.saved);
      await app.end();

      final again = await TestApp.start(tester, game: saved, now: morning);
      await again.tapLabel(Strings.parent, ms: 600);
      expect(find.text(Strings.gateWait(60)), findsOneWidget);
      again.now = again.now.add(const Duration(minutes: 1, seconds: 1));
      await again.settle(1200);
      for (var i = 0; i < 3; i++) {
        await wrong(again);
      }
      expect(again.game.gate.until, again.now.add(const Duration(minutes: 5)));
      await again.end();
    });

    testWidgets('the gate and parent mode shut when the app goes to the background or is left alone', (tester) async {
      final app = await TestApp.start(tester, now: morning);
      await app.tapLabel(Strings.parent, ms: 600);
      app.hide();
      await app.settle(600);
      app.show();
      await app.settle(600);
      expect(find.text(Strings.parentGateTitle), findsNothing);
      await app.tapLabel(Strings.parent, ms: 600);
      await app.answerGate();
      expect(app.location, '/parent');
      app.now = app.now.add(const Duration(minutes: 5, seconds: 2));
      await app.settle(2600);
      expect(app.location, '/');
      app.go('/parent');
      await app.settle();
      expect(app.location, '/', reason: 'the gate has to be passed again');
      await app.end();
    });
  });

  test('sounds play on the media stream and never take the focus', () {
    final effects = soundContext(music: false), music = soundContext(music: true);
    for (final c in [effects, music]) {
      expect(c.android.usageType.name, isNot('notificationRingtone'));
      expect(c.android.audioFocus.name, 'none');
      expect(c.iOS.category.name, 'ambient');
    }
    expect(effects.android.usageType.name, 'game');
    expect(music.android.usageType.name, 'media');
    expect(RestGuard.finishDish, const Duration(minutes: 3));
  });

  test('the closed restaurant and the gate lock are saved', () {
    final g = const Game().rest(morning).withGate(const GateLock(level: 2, until: null));
    final back = Game.fromJson(g.toJson());
    expect(back.restSince, morning);
    expect(back.resting(morning.add(const Duration(minutes: 59))), isTrue);
    expect(back.resting(morning.add(const Duration(minutes: 61))), isFalse);
    expect(back.gate.level, 2);
    var lock = const GateLock();
    for (var i = 0; i < 9; i++) {
      lock = lock.wrong(morning);
    }
    expect(lock.until, morning.add(const Duration(minutes: 15)));
    expect(lock.settled(morning.subtract(const Duration(days: 1))).until, morning.subtract(const Duration(days: 1)).add(const Duration(minutes: 15)));
  });
}
