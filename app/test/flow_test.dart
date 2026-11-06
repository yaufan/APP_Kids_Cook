import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:animal_restaurant/app/strings.dart';
import 'package:animal_restaurant/core/dishes.dart';
import 'package:animal_restaurant/core/providers.dart';
import 'package:animal_restaurant/features/kitchen/steps.dart';

import 'helpers.dart';

/// Every dish cooked once, from the order to the customer eating, on a
/// phone (and one on a tablet). Screenshots go to `build/screenshots/<device>/`.
void main() {
  /// Plays the step on screen the way a child would.
  Future<void> play(TestApp app, CookStep step) async {
    final tester = app.tester;
    // Let the step's pictures load first.
    await app.settle(400);
    Rect area(Type t) => tester.getRect(find.byType(t));
    Future<void> drag(List<Offset> points, {int ms = 16}) async {
      final g = await tester.startGesture(points.first);
      for (final p in points.skip(1)) {
        await g.moveTo(p);
        await tester.pump(Duration(milliseconds: ms));
      }
      await g.up();
      await tester.pump();
    }

    switch (step.kind) {
      case StepKind.rub:
        final r = area(RubStep);
        final c = Offset(r.center.dx, r.top + r.height * 0.48);
        await drag([for (var i = 0; i < 60; i++) c + Offset((i % 2 == 0 ? -1 : 1) * 60.0, (i % 3) * 8.0)]);
      case StepKind.cut:
        final r = area(CutStep);
        final board = Rect.fromCenter(center: Offset(r.width / 2, r.height * 0.42), width: r.width * 0.9, height: r.height * 0.52);
        final s = math.min(board.width * 0.62, board.height * 0.8);
        final item = Rect.fromCenter(center: board.center, width: s, height: s).shift(r.topLeft);
        if (step.count == 1) {
          await drag([for (var i = 0; i <= 10; i++) Offset.lerp(item.topRight, item.bottomLeft, i / 10)!]);
        } else {
          for (var i = 0; i < step.count; i++) {
            final x = item.left + item.width * (i + 1) / (step.count + 1);
            await drag([for (var k = 0; k <= 8; k++) Offset(x, item.top + 4 + (item.height - 8) * k / 8)]);
            await tester.pump(const Duration(milliseconds: 200));
          }
        }
      case StepKind.tapIn:
        for (var i = 0; i < step.count; i++) {
          await tester.tap(find.bySemanticsLabel(Strings.tapIn));
          for (var f = 0; f < 10; f++) {
            await tester.pump(const Duration(milliseconds: 60));
          }
        }
      case StepKind.stir:
        final r = area(StirStep);
        final c = Offset(r.center.dx, r.top + r.height * 0.45);
        await drag([for (var i = 0; i <= 64; i++) c + Offset(math.cos(i * math.pi / 8), math.sin(i * math.pi / 8)) * 80]);
      case StepKind.pour:
        final g = await tester.startGesture(area(PourStep).center);
        for (var i = 0; i < 22; i++) {
          await tester.pump(const Duration(milliseconds: 100));
        }
        await g.up();
        await tester.pump();
      case StepKind.cook:
        for (var i = 0; i < 44; i++) {
          await tester.pump(const Duration(milliseconds: 100));
        }
        final c = area(CookPanStep).center;
        await drag([for (var i = 0; i <= 6; i++) c + Offset(0, -i * 25.0)]);
      case StepKind.adult:
        await tester.tap(find.bySemanticsLabel(Strings.adultHere));
        await tester.pump();
      case StepKind.build:
        for (final art in step.sequence) {
          await tester.tap(find.bySemanticsLabel(Strings.foodName(art)));
          await tester.pump(const Duration(milliseconds: 150));
        }
      case StepKind.wrap:
        for (var i = 0; i < step.count; i++) {
          await tester.tap(find.bySemanticsLabel(Strings.wrapFill));
          await tester.pump(const Duration(milliseconds: 150));
          await tester.tap(find.bySemanticsLabel(Strings.wrapPinch));
          await tester.pump(const Duration(milliseconds: 150));
          await tester.tap(find.bySemanticsLabel(Strings.wrapPinch));
          await tester.pump(const Duration(milliseconds: 200));
        }
      case StepKind.boil:
        for (var i = 0; i < 33; i++) {
          await tester.pump(const Duration(milliseconds: 100));
        }
        await tester.tap(find.bySemanticsLabel(Strings.floated));
        await tester.pump();
      case StepKind.finish:
        for (final art in step.sequence) {
          await tester.tap(find.bySemanticsLabel(Strings.foodName(art)));
          await tester.pump(const Duration(milliseconds: 150));
        }
      case StepKind.roll:
        final c = area(RollStep).center;
        await drag([for (var i = 0; i <= 6; i++) c + Offset(i * 25.0 - 75, 0)]);
    }
    // The tick, then the next step (some steps wait a moment first).
    await app.settle(2400);
  }

  for (final (device, size, ratio, which) in [
    ('phone', const Size(1080, 2340), 2.75, dishes),
    ('tablet', const Size(1600, 2560), 2.0, [dishes[2]]),
  ]) {
    testWidgets('$device: cooking ${which.map((d) => d.id).join(', ')}', (tester) async {
      await tester.runAsync(loadFonts);
      final app = await TestApp.start(tester, size: size, ratio: ratio);
      Future<void> shot(String name) => shoot(tester, device, name);
      var n = 0;
      for (final dish in which) {
        final order = Order(dish, dish.little.$2);
        app.container.read(visitProvider.notifier).take(order);
        await app.settle(900);
        expect(find.bySemanticsLabel(Strings.order(order)), findsOneWidget);
        expect(app.sounds.played, contains('voice_${dish.customer.name}'));
        if (n == 0) await shot('01_order');
        await app.tapLabel(Strings.start, ms: 900);
        final steps = order.stepsFor(app.game.settings.level);
        for (final (i, step) in steps.indexed) {
          expect(find.text(step.zh), findsOneWidget, reason: '${dish.id} step $i');
          app.sounds.played.clear();
          if (device == 'phone') {
            await app.settle(400);
            await shot('${(n + 2).toString().padLeft(2, '0')}_${dish.id}_${i}_${step.kind.name}');
          }
          await play(app, step);
          expect(app.sounds.played, contains('ding'), reason: '${dish.id}: ${step.zh}');
        }
        expect(find.text(Strings.dishDone), findsWidgets);
        await shot('${(n + 2).toString().padLeft(2, '0')}_${dish.id}_done');
        await app.tapLabel(Strings.serve, ms: 1200);
        expect(app.visit.served, isTrue);
        expect(app.game.cooked[dish.id], 1);
        expect(app.sounds.played, contains('yum'));
        await shot('${(n + 2).toString().padLeft(2, '0')}_${dish.id}_served');
        await app.tapLabel(Strings.nextCustomer, ms: 900);
        n++;
      }
      expect(app.game.served, which.length);

      await app.tapLabel(Strings.book, ms: 900);
      await shot('90_book');
      await app.tapLabel(which.first.zh, ms: 600);
      await shot('91_recipe');
      await app.end();
    }, timeout: const Timeout(Duration(minutes: 8)));
  }
}
