import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/dishes.dart';

/// What every step needs from the kitchen: sounds, speech, counting, and
/// telling the kitchen it is done.
class StepEnv {
  const StepEnv({required this.play, required this.say, required this.english, required this.level, required this.done});

  final void Function(String sfx) play;
  final void Function(String zh, {String? en}) say;
  final bool english;
  final Level level;
  final VoidCallback done;

  /// Says the number out loud ("三", and "three" with English on).
  void count(int n) => say(Strings.countZh(n), en: english && n <= 10 ? Strings.countEn[n] : null);
}

/// The little game for [step].
Widget stepView(CookStep step, StepEnv env, {Key? key}) => switch (step.kind) {
      StepKind.rub => RubStep(step: step, env: env, key: key),
      StepKind.cut => CutStep(step: step, env: env, key: key),
      StepKind.tapIn => TapInStep(step: step, env: env, key: key),
      StepKind.stir => StirStep(step: step, env: env, key: key),
      StepKind.pour => PourStep(step: step, env: env, key: key),
      StepKind.cook => CookPanStep(step: step, env: env, key: key),
      StepKind.adult => AdultStep(step: step, env: env, key: key),
      StepKind.build => BuildStep(step: step, env: env, key: key),
      StepKind.wrap => WrapStep(step: step, env: env, key: key),
      StepKind.boil => BoilStep(step: step, env: env, key: key),
      StepKind.finish => FinishStep(step: step, env: env, key: key),
      StepKind.roll => RollStep(step: step, env: env, key: key),
    };

/// A thin bar of how far along a step is.
class StepBar extends StatelessWidget {
  const StepBar(this.value, {super.key, this.color = Clay.go});

  final double value;
  final Color color;

  @override
  Widget build(BuildContext context) => Container(
        width: 220,
        height: 18,
        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.8), borderRadius: BorderRadius.circular(9)),
        alignment: Alignment.centerLeft,
        child: FractionallySizedBox(
          widthFactor: value.clamp(0.04, 1),
          child: Container(decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(9))),
        ),
      );
}

/// Bubbles and drops that float and fall from where the finger rubs.
class _Bits extends CustomPainter {
  _Bits(this.bits, this.t);

  final List<(Offset, double, bool)> bits;
  final double t;

  @override
  void paint(Canvas canvas, Size size) {
    for (final (at, born, drop) in bits) {
      final age = t - born;
      if (age < 0 || age > 1.2) continue;
      final fade = 1 - age / 1.2;
      if (drop) {
        canvas.drawCircle(at + Offset(0, age * 160), 5, Paint()..color = Clay.sky.withValues(alpha: fade));
      } else {
        final r = 7 + age * 8;
        final p = at + Offset(math.sin(born * 9) * 10 * age, -age * 70);
        canvas.drawCircle(p, r, Paint()..color = Colors.white.withValues(alpha: 0.6 * fade));
        canvas.drawCircle(p + Offset(-r * 0.3, -r * 0.3), r * 0.25, Paint()..color = Colors.white.withValues(alpha: fade));
      }
    }
  }

  @override
  bool shouldRepaint(_Bits old) => true;
}

/// A small helper: a ticking clock in seconds for step animations.
mixin _Clock<T extends StatefulWidget> on State<T>, TickerProviderStateMixin<T> {
  late final AnimationController clock = AnimationController(vsync: this, duration: const Duration(days: 1))..forward();
  double get t => clock.lastElapsedDuration == null ? 0 : clock.lastElapsedDuration!.inMicroseconds / 1e6;

  @override
  void dispose() {
    clock.dispose();
    super.dispose();
  }
}

// --- Rub: wash hands, wash food, shake a cup -------------------------------

class RubStep extends StatefulWidget {
  const RubStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<RubStep> createState() => _RubStepState();
}

class _RubStepState extends State<RubStep> with TickerProviderStateMixin, _Clock {
  double _rubbed = 0, _sinceSound = 0;
  Offset? _last;
  final _bits = <(Offset, double, bool)>[];
  var _done = false;

  static const _needed = 1400.0;

  bool get _shake => widget.step.sfx == 'shake';

  void _move(Offset p) {
    if (_done) return;
    final last = _last;
    _last = p;
    if (last == null) return;
    final d = (p - last).distance;
    _rubbed += d;
    _sinceSound += d;
    if (!_shake && _bits.length < 120 && (_rubbed ~/ 30) != ((_rubbed - d) ~/ 30)) {
      _bits.add((p, t, widget.step.sfx == 'water'));
    }
    if (_sinceSound > 320) {
      _sinceSound = 0;
      widget.env.play(widget.step.sfx);
    }
    if (_rubbed >= _needed) {
      _done = true;
      widget.env.done();
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    return LayoutBuilder(builder: (context, box) {
      final size = math.min(box.maxWidth * 0.62, box.maxHeight * 0.55);
      return Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: (e) => _last = e.localPosition,
        onPointerMove: (e) => _move(e.localPosition),
        onPointerUp: (_) => _last = null,
        child: AnimatedBuilder(
          animation: clock,
          builder: (context, _) => Stack(children: [
            if (step.target.isNotEmpty)
              Positioned(left: box.maxWidth / 2 - size * 0.75, top: box.maxHeight * 0.5 - size * 0.55, width: size * 1.5, height: size * 1.1, child: Art(step.target)),
            Positioned(
              left: box.maxWidth / 2 - size / 2,
              top: box.maxHeight * 0.48 - size / 2,
              width: size,
              height: size,
              child: Transform.rotate(angle: _shake && _last != null ? math.sin(t * 30) * 0.18 : 0, child: Art(step.art)),
            ),
            Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _Bits(_bits, t)))),
            Positioned(left: 0, right: 0, bottom: 18, child: Center(child: StepBar(_rubbed / _needed))),
          ]),
        ),
      );
    });
  }
}

// --- Cut: swipe down across each dashed line ------------------------------

class CutStep extends StatefulWidget {
  const CutStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<CutStep> createState() => _CutStepState();
}

class _CutStepState extends State<CutStep> {
  final _cut = <int>{};
  Offset? _start;
  Rect _item = Rect.zero;
  var _done = false;

  int get _n => widget.step.count;
  bool get _diagonal => _n == 1;

  double _lineX(int i) => _item.left + _item.width * (i + 1) / (_n + 1);

  void _check(Offset end) {
    final s = _start;
    if (s == null || _done) return;
    final drag = end - s;
    int? which;
    if (_diagonal) {
      if (drag.distance > _item.shortestSide * 0.55) which = 0;
    } else if (drag.dy.abs() > _item.height * 0.45 && drag.dx.abs() < 60) {
      final x = (s.dx + end.dx) / 2;
      var best = 999.0;
      for (var i = 0; i < _n; i++) {
        if (_cut.contains(i)) continue;
        final d = (_lineX(i) - x).abs();
        if (d < best && d < 46) {
          best = d;
          which = i;
        }
      }
    }
    if (which == null) return;
    _start = null;
    widget.env.play(widget.step.sfx);
    setState(() => _cut.add(which!));
    widget.env.count(_cut.length);
    if (_cut.length == _n) {
      _done = true;
      Timer(const Duration(milliseconds: 500), widget.env.done);
    }
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    return LayoutBuilder(builder: (context, box) {
      final w = box.maxWidth, h = box.maxHeight;
      final board = Rect.fromCenter(center: Offset(w / 2, h * 0.42), width: w * 0.9, height: h * 0.52);
      final s = math.min(board.width * 0.62, board.height * 0.8);
      _item = Rect.fromCenter(center: board.center, width: s, height: s);
      return Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: (e) => _start = e.localPosition,
        onPointerMove: (e) => _check(e.localPosition),
        onPointerUp: (_) => _start = null,
        child: Stack(children: [
          if (step.target.isNotEmpty) Positioned.fromRect(rect: board, child: Art(step.target, fit: BoxFit.fill)),
          Positioned.fromRect(
            rect: _item,
            child: _done && step.result.isNotEmpty && _diagonal ? Art(step.result) : Art(step.art),
          ),
          Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _CutLines(_item, _n, _cut, _diagonal)))),
          if (!_diagonal && step.result.isNotEmpty)
            Positioned(
              left: 0,
              right: 0,
              bottom: 20,
              child: Column(children: [
                SizedBox(
                  height: 64,
                  child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                    for (var i = 0; i < _cut.length; i++) SizedBox(width: 58, height: 58, child: Art(step.result)),
                  ]),
                ),
                const SizedBox(height: 6),
                CountDots(count: _n, done: _cut.length),
              ]),
            ),
        ]),
      );
    });
  }
}

class _CutLines extends CustomPainter {
  _CutLines(this.item, this.n, this.cut, this.diagonal);

  final Rect item;
  final int n;
  final Set<int> cut;
  final bool diagonal;

  @override
  void paint(Canvas canvas, Size size) {
    final dash = Paint()
      ..color = Colors.white
      ..strokeWidth = 5
      ..strokeCap = StrokeCap.round;
    final gap = Paint()
      ..color = Clay.creamDeep
      ..strokeWidth = 7;
    void dashed(Offset a, Offset b) {
      final len = (b - a).distance;
      for (var d = 0.0; d < len; d += 22) {
        canvas.drawLine(Offset.lerp(a, b, d / len)!, Offset.lerp(a, b, math.min(1, (d + 12) / len))!, dash);
      }
    }

    if (diagonal) {
      if (!cut.contains(0)) dashed(item.topRight + const Offset(-10, 10), item.bottomLeft + const Offset(10, -10));
      return;
    }
    for (var i = 0; i < n; i++) {
      final x = item.left + item.width * (i + 1) / (n + 1);
      final a = Offset(x, item.top - 14), b = Offset(x, item.bottom + 14);
      cut.contains(i) ? canvas.drawLine(a, b, gap) : dashed(a, b);
    }
  }

  @override
  bool shouldRepaint(_CutLines old) => true;
}

// --- Tap in: eggs, pearls, ice, dumplings into the bowl, cup or pot -------

class TapInStep extends StatefulWidget {
  const TapInStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<TapInStep> createState() => _TapInStepState();
}

class _TapInStepState extends State<TapInStep> with TickerProviderStateMixin {
  var _in = 0;
  late final _fly = AnimationController(vsync: this, duration: const Duration(milliseconds: 450));

  @override
  void dispose() {
    _fly.dispose();
    super.dispose();
  }

  Future<void> _tap() async {
    if (_fly.isAnimating || _in >= widget.step.count) return;
    await _fly.forward(from: 0);
    if (!mounted) return;
    widget.env.play(widget.step.sfx);
    setState(() => _in++);
    widget.env.count(_in);
    if (_in == widget.step.count) Timer(const Duration(milliseconds: 600), widget.env.done);
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    return LayoutBuilder(builder: (context, box) {
      final w = box.maxWidth, h = box.maxHeight;
      final target = Rect.fromCenter(center: Offset(w * 0.4, h * 0.55), width: w * 0.55, height: w * 0.55);
      final source = Rect.fromCenter(center: Offset(w * 0.82, h * 0.25), width: w * 0.28, height: w * 0.28);
      final egg = step.sfx == 'crack';
      return Stack(children: [
        Positioned.fromRect(rect: target, child: Art(egg && _in > 0 ? step.result : step.target)),
        // What went in so far (not for eggs: the bowl shows them).
        if (!egg)
          for (var i = 0; i < _in; i++)
            Positioned(
              left: target.left + target.width * (0.28 + 0.44 * ((i * 0.37) % 1)),
              top: target.top + target.height * (0.45 + 0.08 * (i % 3)),
              width: target.width * 0.22,
              height: target.width * 0.22,
              child: Art(step.result),
            ),
        Positioned.fromRect(
          rect: source,
          child: Semantics(
            container: true,
            button: true,
            label: Strings.tapIn,
            excludeSemantics: true,
            child: GestureDetector(onTap: _tap, child: Breathing(amount: 0.05, child: Art(step.art))),
          ),
        ),
        AnimatedBuilder(
          animation: _fly,
          builder: (_, _) {
            if (!_fly.isAnimating) return const SizedBox.shrink();
            final v = Curves.easeIn.transform(_fly.value);
            final at = Offset.lerp(source.center, target.center, v)! + Offset(0, -math.sin(v * math.pi) * 80);
            final s = source.width * (1 - 0.4 * v);
            return Positioned(left: at.dx - s / 2, top: at.dy - s / 2, width: s, height: s, child: Art(step.art));
          },
        ),
        Positioned(left: 0, right: 0, bottom: 16, child: Center(child: CountDots(count: step.count, done: _in, size: 22))),
      ]);
    });
  }
}

// --- Stir: circles in the bowl --------------------------------------------

class StirStep extends StatefulWidget {
  const StirStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<StirStep> createState() => _StirStepState();
}

class _StirStepState extends State<StirStep> {
  double _turned = 0, _sinceSound = 0;
  double? _angle;
  Offset _center = Offset.zero;
  var _done = false;

  static const _needed = math.pi * 6;

  void _move(Offset p) {
    final v = p - _center;
    if (v.distance < 18 || _done) return;
    final a = math.atan2(v.dy, v.dx);
    final last = _angle;
    _angle = a;
    if (last == null) return;
    var d = a - last;
    if (d > math.pi) d -= 2 * math.pi;
    if (d < -math.pi) d += 2 * math.pi;
    _turned += d.abs();
    _sinceSound += d.abs();
    if (_sinceSound > math.pi) {
      _sinceSound = 0;
      widget.env.play(widget.step.sfx);
    }
    if (_turned >= _needed) {
      _done = true;
      widget.env.done();
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final s = math.min(box.maxWidth * 0.8, box.maxHeight * 0.7);
        _center = Offset(box.maxWidth / 2, box.maxHeight * 0.45);
        return Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (e) => _angle = null,
          onPointerMove: (e) => _move(e.localPosition),
          child: Stack(children: [
            Positioned(
              left: _center.dx - s / 2,
              top: _center.dy - s / 2,
              width: s,
              height: s,
              child: Transform.rotate(angle: _turned, child: Art(widget.step.art)),
            ),
            Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _Swirl(_center, s * 0.3, _turned)))),
            Positioned(left: 0, right: 0, bottom: 18, child: Center(child: StepBar(_turned / _needed))),
          ]),
        );
      });
}

class _Swirl extends CustomPainter {
  _Swirl(this.c, this.r, this.turned);

  final Offset c;
  final double r;
  final double turned;

  @override
  void paint(Canvas canvas, Size size) {
    // The circle to follow, with an arrow going round.
    final p = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 5
      ..strokeCap = StrokeCap.round
      ..color = Colors.white.withValues(alpha: 0.85);
    canvas.drawArc(Rect.fromCircle(center: c, radius: r), turned, math.pi * 1.6, false, p);
    final end = turned + math.pi * 1.6;
    final tip = c + Offset(math.cos(end), math.sin(end)) * r;
    final dir = Offset(-math.sin(end), math.cos(end));
    final side = Offset(math.cos(end), math.sin(end));
    canvas.drawPath(
        Path()
          ..moveTo(tip.dx - dir.dx * 14 + side.dx * 10, tip.dy - dir.dy * 14 + side.dy * 10)
          ..lineTo(tip.dx, tip.dy)
          ..lineTo(tip.dx - dir.dx * 14 - side.dx * 10, tip.dy - dir.dy * 14 - side.dy * 10),
        p);
  }

  @override
  bool shouldRepaint(_Swirl old) => old.turned != turned;
}

// --- Pour: hold, let go at the line ---------------------------------------

class PourStep extends StatefulWidget {
  const PourStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<PourStep> createState() => _PourStepState();
}

class _PourStepState extends State<PourStep> with TickerProviderStateMixin, _Clock {
  double _level = 0;
  double? _pouringSince;
  double _from = 0;
  var _done = false;
  Timer? _sound;

  static const line = 0.8;

  @override
  void dispose() {
    _sound?.cancel();
    super.dispose();
  }

  void _down() {
    if (_done) return;
    _from = _level;
    _pouringSince = t;
    widget.env.play(widget.step.sfx);
    _sound = Timer.periodic(const Duration(milliseconds: 1100), (_) => widget.env.play(widget.step.sfx));
  }

  void _up() {
    if (_pouringSince == null) return;
    _pouringSince = null;
    _sound?.cancel();
    if (_level >= line - 0.12) {
      _done = true;
      widget.env.say(_level > line + 0.12 ? Strings.tooMuch : Strings.justRight);
      Timer(const Duration(milliseconds: 700), widget.env.done);
    }
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    final pan = step.target == 'tools/pan';
    return LayoutBuilder(builder: (context, box) {
      final w = box.maxWidth, h = box.maxHeight;
      final target = Rect.fromCenter(center: Offset(w * 0.42, h * 0.62), width: w * (pan ? 0.75 : 0.42), height: pan ? w * 0.6 : w * 0.62);
      final source = Rect.fromCenter(center: Offset(w * 0.72, h * 0.22), width: w * 0.36, height: w * 0.36);
      return Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: (_) => _down(),
        onPointerUp: (_) => _up(),
        onPointerCancel: (_) => _up(),
        child: AnimatedBuilder(
          animation: clock,
          builder: (context, _) {
            final since = _pouringSince;
            if (since != null) _level = math.min(1.15, _from + (t - since) / 2.6);
            return Stack(children: [
              Positioned.fromRect(rect: target, child: Art(step.target)),
              // What is in it so far.
              if (pan)
                Positioned.fromRect(
                  rect: Rect.fromCenter(center: target.center + Offset(-target.width * 0.08, 0), width: target.width * 0.62, height: target.width * 0.62),
                  child: Opacity(opacity: _level.clamp(0, 1), child: Art(step.result)),
                )
              else ...[
                Positioned(
                  left: target.left + target.width * 0.16,
                  width: target.width * 0.68,
                  bottom: h - target.bottom + target.height * 0.08,
                  height: target.height * 0.8 * _level.clamp(0, 1.05),
                  child: ClipRRect(
                    borderRadius: const BorderRadius.vertical(bottom: Radius.circular(18)),
                    child: ColoredBox(color: const Color(0xFFC8955C).withValues(alpha: 0.85)),
                  ),
                ),
                // The line to stop at.
                Positioned(
                  left: target.left + target.width * 0.08,
                  width: target.width * 0.84,
                  top: target.bottom - target.height * 0.08 - target.height * 0.8 * line,
                  height: 4,
                  child: const ColoredBox(color: Clay.tomato),
                ),
              ],
              if (since != null)
                Positioned(
                  left: source.left + source.width * 0.12,
                  top: source.center.dy,
                  width: 12,
                  height: target.center.dy - source.center.dy,
                  child: DecoratedBox(decoration: BoxDecoration(color: (pan ? Clay.butter : const Color(0xFFC8955C)).withValues(alpha: 0.85), borderRadius: BorderRadius.circular(6))),
                ),
              Positioned.fromRect(
                rect: source,
                child: Transform.rotate(angle: since != null ? -0.7 : 0, alignment: Alignment.bottomLeft, child: Art(step.art)),
              ),
              Positioned(left: 0, right: 0, bottom: 14, child: Center(child: StepBar(_level / line, color: _level > line + 0.12 ? Clay.butter : Clay.go))),
            ]);
          },
        ),
      );
    });
  }
}

// --- Cook: wait for gold, swipe up to flip --------------------------------

class CookPanStep extends StatefulWidget {
  const CookPanStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<CookPanStep> createState() => _CookPanStepState();
}

class _CookPanStepState extends State<CookPanStep> with TickerProviderStateMixin, _Clock {
  Offset? _start;
  double? _flippedAt;
  Timer? _sizzle;
  var _told = false;

  static const _cookTime = 4.0;

  @override
  void initState() {
    super.initState();
    widget.env.play(widget.step.sfx);
    _sizzle = Timer.periodic(const Duration(milliseconds: 1500), (_) => widget.env.play(widget.step.sfx));
  }

  @override
  void dispose() {
    _sizzle?.cancel();
    super.dispose();
  }

  double get _cooked => (t / _cookTime).clamp(0, 1);

  void _swipe(Offset end) {
    final s = _start;
    if (s == null || _flippedAt != null) return;
    if (s.dy - end.dy < 60) return;
    _start = null;
    if (_cooked < 1) {
      widget.env.say(Strings.notYet);
      return;
    }
    _sizzle?.cancel();
    widget.env.play('flip');
    setState(() => _flippedAt = t);
    Timer(const Duration(milliseconds: 900), widget.env.done);
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    return LayoutBuilder(builder: (context, box) {
      final w = box.maxWidth, h = box.maxHeight;
      final pan = Rect.fromCenter(center: Offset(w * 0.5, h * 0.48), width: w * 0.92, height: w * 0.72);
      final food = Rect.fromCenter(center: pan.center + Offset(-pan.width * 0.08, 0), width: pan.width * 0.6, height: pan.width * 0.6);
      return Listener(
        behavior: HitTestBehavior.opaque,
        onPointerDown: (e) => _start = e.localPosition,
        onPointerMove: (e) => _swipe(e.localPosition),
        child: AnimatedBuilder(
          animation: clock,
          builder: (context, _) {
            if (_cooked >= 1 && !_told) {
              _told = true;
              scheduleMicrotask(() => widget.env.say(Strings.flipNow));
            }
            final flip = _flippedAt == null ? 0.0 : ((t - _flippedAt!) / 0.6).clamp(0.0, 1.0);
            return Stack(children: [
              Positioned.fromRect(rect: pan, child: Art(step.target)),
              Positioned.fromRect(
                rect: food.translate(0, -math.sin(flip * math.pi) * 90),
                child: Transform(
                  alignment: Alignment.center,
                  transform: Matrix4.diagonal3Values(1, math.cos(flip * math.pi).abs().clamp(0.05, 1), 1),
                  child: Stack(fit: StackFit.expand, children: [
                    Art(step.art),
                    Opacity(opacity: _cooked, child: Art(step.result)),
                  ]),
                ),
              ),
              Positioned.fill(child: IgnorePointer(child: CustomPaint(painter: _Ring(food.center, food.width * 0.62, _cooked)))),
              if (_cooked >= 1 && _flippedAt == null)
                Positioned(
                  left: food.center.dx - 40,
                  top: food.top - 70,
                  width: 80,
                  height: 80,
                  child: Transform.translate(offset: Offset(0, -math.sin(t * 6).abs() * 12), child: const Art('ui/arrow_flip')),
                ),
            ]);
          },
        ),
      );
    });
  }
}

class _Ring extends CustomPainter {
  _Ring(this.c, this.r, this.v);

  final Offset c;
  final double r;
  final double v;

  @override
  void paint(Canvas canvas, Size size) {
    canvas.drawCircle(
        c,
        r,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 9
          ..color = Colors.white.withValues(alpha: 0.4));
    canvas.drawArc(
        Rect.fromCircle(center: c, radius: r),
        -math.pi / 2,
        math.pi * 2 * v,
        false,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 9
          ..strokeCap = StrokeCap.round
          ..color = Color.lerp(Clay.butter, const Color(0xFFE0A030), v)!);
  }

  @override
  bool shouldRepaint(_Ring old) => old.v != v;
}

// --- A grown-up's help: the fire, the hot water ---------------------------

class AdultStep extends StatefulWidget {
  const AdultStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<AdultStep> createState() => _AdultStepState();
}

class _AdultStepState extends State<AdultStep> {
  var _on = false;

  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 1800), () {
      if (mounted) widget.env.say(Strings.adultSafety);
    });
  }

  void _help() {
    if (_on) return;
    widget.env.play('pop');
    setState(() => _on = true);
    Timer(const Duration(milliseconds: 900), widget.env.done);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final s = math.min(box.maxWidth * 0.7, box.maxHeight * 0.48);
        return Column(children: [
          const SizedBox(height: 8),
          SizedBox(
            width: s,
            height: s,
            child: Stack(children: [
              Positioned.fill(child: Art(widget.step.art)),
              if (_on) Positioned(left: s * 0.3, top: s * 0.3, width: s * 0.4, height: s * 0.4, child: const Breathing(amount: 0.08, period: Duration(milliseconds: 700), child: Art('ui/fire'))),
            ]),
          ),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            const SizedBox(width: 54, height: 54, child: Art('ui/adult_help')),
            const SizedBox(width: 8),
            Flexible(child: Text(Strings.adultSafety, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: Clay.ink))),
          ]),
          const Spacer(),
          ClayButton(label: Strings.adultHere, icon: const Art('ui/adult_help'), color: Clay.butter, wide: true, size: 76, onTap: _on ? null : _help),
          const SizedBox(height: 18),
        ]);
      });
}

// --- Build: put things on in the order the card shows ---------------------

class BuildStep extends StatefulWidget {
  const BuildStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<BuildStep> createState() => _BuildStepState();
}

class _BuildStepState extends State<BuildStep> with TickerProviderStateMixin {
  var _placed = 0;
  String? _wobble;
  late final _wobbleCtl = AnimationController(vsync: this, duration: const Duration(milliseconds: 450));

  List<String> get _seq => widget.step.sequence;
  bool get _skewer => widget.step.target == 'food/skewer';

  /// The choices on the tray: each kind once, in a fixed order.
  late final List<String> _choices = <String>{..._seq}.toList();

  @override
  void dispose() {
    _wobbleCtl.dispose();
    super.dispose();
  }

  /// Big children follow a pattern: after the first round the card hides
  /// what comes next.
  bool _hidden(int i) {
    if (!_skewer || widget.env.level == Level.little) return false;
    final round = _choices.length;
    return i >= round && i >= _placed;
  }

  void _pick(String art) {
    if (_placed >= _seq.length) return;
    final want = _seq[_placed];
    if (art != want) {
      widget.env.play('oops');
      setState(() => _wobble = art);
      _wobbleCtl.forward(from: 0);
      widget.env.say(_hidden(_placed) ? Strings.nextOne : Strings.putThis(Strings.foodName(want)));
      return;
    }
    widget.env.play(widget.step.sfx);
    setState(() => _placed++);
    if (art == 'food/tomato_slice') widget.env.count(_seq.sublist(0, _placed).where((s) => s == art).length);
    if (_placed == _seq.length) Timer(const Duration(milliseconds: 600), widget.env.done);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final chip = math.min(52.0, (w - 24) / _seq.length - 4);
        return Stack(children: [
          // The recipe card: what goes on, in order.
          Positioned(
            left: 10,
            right: 10,
            top: 0,
            child: ClayBox(
              color: Colors.white,
              radius: 20,
              padding: const EdgeInsets.all(6),
              child: Wrap(alignment: WrapAlignment.center, spacing: 4, runSpacing: 4, children: [
                for (var i = 0; i < _seq.length; i++)
                  Container(
                    width: chip,
                    height: chip,
                    padding: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      color: i < _placed ? Clay.mint.withValues(alpha: 0.5) : (i == _placed ? Clay.butter : Clay.cream),
                    ),
                    child: _hidden(i)
                        ? const Center(child: Text('?', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w700, color: Clay.inkSoft)))
                        : Art(_seq[i]),
                  ),
              ]),
            ),
          ),
          // The plate or the stick, with what is on it.
          if (_skewer)
            ..._skewerItems(w, h)
          else
            ..._plateItems(w, h),
          // The tray.
          Positioned(
            left: 0,
            right: 0,
            bottom: 12,
            child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              for (final c in _choices)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8),
                  child: AnimatedBuilder(
                    animation: _wobbleCtl,
                    builder: (_, child) => Transform.rotate(angle: _wobble == c ? math.sin(_wobbleCtl.value * math.pi * 5) * 0.2 * (1 - _wobbleCtl.value) : 0, child: child),
                    child: Semantics(
                      container: true,
                      button: true,
                      label: Strings.foodName(c),
                      excludeSemantics: true,
                      child: Pressable(
                        sound: null,
                        onTap: () => _pick(c),
                        child: SizedBox(width: 84, height: 84, child: ClayBox(color: Clay.cream, radius: 24, padding: const EdgeInsets.all(10), child: Art(c))),
                      ),
                    ),
                  ),
                ),
            ]),
          ),
        ]);
      });

  List<Widget> _plateItems(double w, double h) {
    final plate = Rect.fromCenter(center: Offset(w / 2, h * 0.52), width: w * 0.78, height: w * 0.78);
    final layer = plate.width * 0.62;
    return [
      Positioned.fromRect(rect: plate, child: Art(widget.step.target)),
      for (var i = 0; i < _placed; i++)
        Positioned(
          left: plate.center.dx - layer / 2 + (_seq[i] == 'food/tomato_slice' ? (i % 3 - 1) * layer * 0.22 : 0),
          top: plate.center.dy - layer / 2 - i * 5 + (_seq[i] == 'food/tomato_slice' ? (i % 2) * layer * 0.15 : 0),
          width: _seq[i] == 'food/tomato_slice' ? layer * 0.42 : layer,
          height: _seq[i] == 'food/tomato_slice' ? layer * 0.42 : layer,
          child: Art(_seq[i]),
        ),
    ];
  }

  List<Widget> _skewerItems(double w, double h) {
    final stick = Rect.fromCenter(center: Offset(w / 2, h * 0.5), width: 40, height: h * 0.55);
    final n = _seq.length;
    final step = stick.height * 0.88 / n;
    final s = math.min(step * 1.25, 70.0);
    return [
      Positioned.fromRect(rect: stick.inflate(6), child: Art(widget.step.target, fit: BoxFit.fill)),
      for (var i = 0; i < _placed; i++)
        Positioned(left: stick.center.dx - s / 2, top: stick.bottom - (i + 1) * step - s * 0.1, width: s, height: s, child: Art(_seq[i])),
    ];
  }
}

// --- Wrap dumplings: filling in, pinch shut -------------------------------

class WrapStep extends StatefulWidget {
  const WrapStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<WrapStep> createState() => _WrapStepState();
}

class _WrapStepState extends State<WrapStep> {
  var _made = 0;
  var _filled = false;
  var _pinches = 0;

  void _fill() {
    if (_filled) return;
    widget.env.play('pop');
    setState(() => _filled = true);
    widget.env.say(Strings.wrapPinch);
  }

  void _pinch() {
    if (!_filled) {
      widget.env.say(Strings.wrapFill);
      return;
    }
    widget.env.play(widget.step.sfx);
    setState(() => _pinches++);
    if (_pinches < 2) return;
    setState(() {
      _made++;
      _filled = false;
      _pinches = 0;
    });
    widget.env.count(_made);
    if (_made == widget.step.count) Timer(const Duration(milliseconds: 600), widget.env.done);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final s = w * 0.56;
        return Stack(children: [
          Positioned(
            left: w * 0.08,
            top: h * 0.2,
            width: s,
            height: s,
            child: Semantics(
              container: true,
              button: true,
              label: Strings.wrapPinch,
              excludeSemantics: true,
              child: GestureDetector(
                onTap: _pinch,
                child: AnimatedScale(
                  scale: 1 - _pinches * 0.08,
                  duration: const Duration(milliseconds: 150),
                  child: Art(_made == widget.step.count ? 'food/dumpling' : (_filled ? 'food/wrapper_filled' : 'food/wrapper')),
                ),
              ),
            ),
          ),
          Positioned(
            right: w * 0.04,
            top: h * 0.1,
            width: w * 0.32,
            height: w * 0.32,
            child: Semantics(
              container: true,
              button: true,
              label: Strings.wrapFill,
              excludeSemantics: true,
              child: GestureDetector(
                onTap: _fill,
                child: Breathing(
                  amount: _filled ? 0 : 0.05,
                  child: Stack(children: [const Positioned.fill(child: Art('tools/bowl')), Positioned.fill(child: Padding(padding: EdgeInsets.all(w * 0.06), child: const Art('food/filling')))]),
                ),
              ),
            ),
          ),
          Positioned(
            left: 0,
            right: 0,
            bottom: 14,
            child: Column(children: [
              SizedBox(
                height: 60,
                child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                  for (var i = 0; i < _made; i++) const SizedBox(width: 56, height: 56, child: Art('food/dumpling')),
                ]),
              ),
              CountDots(count: widget.step.count, done: _made, size: 20),
            ]),
          ),
        ]);
      });
}

// --- Boil: wait for them to float, scoop them out -------------------------

class BoilStep extends StatefulWidget {
  const BoilStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<BoilStep> createState() => _BoilStepState();
}

class _BoilStepState extends State<BoilStep> with TickerProviderStateMixin, _Clock {
  var _scooped = false;
  var _told = false;
  Timer? _bubbles;

  static const _floatAt = 3.0;

  @override
  void initState() {
    super.initState();
    widget.env.play(widget.step.sfx);
    _bubbles = Timer.periodic(const Duration(milliseconds: 1500), (_) => widget.env.play(widget.step.sfx));
  }

  @override
  void dispose() {
    _bubbles?.cancel();
    super.dispose();
  }

  void _scoop() {
    if (t < _floatAt) {
      widget.env.say(Strings.waitFloat);
      return;
    }
    if (_scooped) return;
    _bubbles?.cancel();
    widget.env.play('pop');
    setState(() => _scooped = true);
    Timer(const Duration(milliseconds: 900), widget.env.done);
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final w = box.maxWidth, h = box.maxHeight;
        final pot = Rect.fromCenter(center: Offset(w * 0.44, h * 0.5), width: w * 0.78, height: w * 0.78);
        return AnimatedBuilder(
          animation: clock,
          builder: (context, _) {
            final up = ((t - 0.5) / (_floatAt - 0.5)).clamp(0.0, 1.0);
            if (up >= 1 && !_told) {
              _told = true;
              scheduleMicrotask(() => widget.env.say(Strings.floated));
            }
            return Stack(children: [
              Positioned.fromRect(rect: pot, child: Art(_scooped ? 'tools/pot' : widget.step.target)),
              if (!_scooped)
                for (var i = 0; i < widget.step.count; i++)
                  Positioned(
                    left: pot.left + pot.width * (0.22 + 0.5 * ((i * 0.41) % 1)),
                    top: pot.top + pot.height * (0.62 - 0.3 * up) + math.sin(t * 3 + i) * 4,
                    width: pot.width * 0.2,
                    height: pot.width * 0.2,
                    child: Opacity(opacity: 0.55 + 0.45 * up, child: const Art('food/dumpling')),
                  ),
              if (_scooped)
                Positioned(left: w * 0.2, top: h * 0.62, width: w * 0.6, height: w * 0.42, child: Art(widget.step.result)),
              Positioned(
                right: 8,
                top: h * 0.08,
                width: w * 0.26,
                height: w * 0.26,
                child: Semantics(
                  container: true,
                  button: true,
                  label: Strings.floated,
                  excludeSemantics: true,
                  child: GestureDetector(onTap: _scoop, child: Breathing(amount: up >= 1 ? 0.07 : 0, child: const Art('tools/ladle'))),
                ),
              ),
            ]);
          },
        );
      });
}

// --- Finish: sauce, a lid, a straw -----------------------------------------

class FinishStep extends StatefulWidget {
  const FinishStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<FinishStep> createState() => _FinishStepState();
}

class _FinishStepState extends State<FinishStep> {
  var _done = 0;

  void _tap(int i) {
    if (i != _done) return;
    widget.env.play(widget.step.sfx);
    setState(() => _done++);
    if (_done == widget.step.sequence.length) Timer(const Duration(milliseconds: 700), widget.env.done);
  }

  @override
  Widget build(BuildContext context) {
    final step = widget.step;
    final all = _done == step.sequence.length;
    return LayoutBuilder(builder: (context, box) {
      final w = box.maxWidth, h = box.maxHeight;
      final s = math.min(w * 0.6, h * 0.55);
      final sauce = step.sfx == 'squeeze';
      return Stack(children: [
        Positioned(
          left: w / 2 - s / 2,
          top: h * 0.32,
          width: s,
          height: s,
          child: Stack(fit: StackFit.expand, children: [
            Art(all && step.result.isNotEmpty ? step.result : step.target),
            if (sauce && _done > 0) CustomPaint(painter: _Drizzle()),
            if (!sauce)
              for (var i = 0; i < _done && !all; i++) Art(step.sequence[i]),
          ]),
        ),
        Positioned(
          left: 0,
          right: 0,
          top: 0,
          child: Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            for (final (i, art) in step.sequence.indexed)
              if (i >= _done)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 10),
                  child: Semantics(
                    container: true,
                    button: true,
                    label: Strings.foodName(art),
                    excludeSemantics: true,
                    child: Pressable(
                      sound: null,
                      onTap: () => _tap(i),
                      child: Opacity(
                        opacity: i == _done ? 1 : 0.45,
                        child: SizedBox(
                          width: 104,
                          height: 104,
                          child: i == _done ? Breathing(amount: 0.06, child: Art(art)) : Art(art),
                        ),
                      ),
                    ),
                  ),
                ),
          ]),
        ),
      ]);
    });
  }
}

class _Drizzle extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final p = Path()..moveTo(size.width * 0.2, size.height * 0.35);
    for (var i = 1; i <= 6; i++) {
      p.lineTo(size.width * (0.2 + i * 0.1), size.height * (i.isEven ? 0.35 : 0.6));
    }
    canvas.drawPath(
        p,
        Paint()
          ..style = PaintingStyle.stroke
          ..strokeWidth = 7
          ..strokeCap = StrokeCap.round
          ..strokeJoin = StrokeJoin.round
          ..color = const Color(0xFF5A3420));
  }

  @override
  bool shouldRepaint(_Drizzle old) => false;
}

// --- Roll: swipe sideways --------------------------------------------------

class RollStep extends StatefulWidget {
  const RollStep({super.key, required this.step, required this.env});

  final CookStep step;
  final StepEnv env;

  @override
  State<RollStep> createState() => _RollStepState();
}

class _RollStepState extends State<RollStep> with TickerProviderStateMixin {
  late final _roll = AnimationController(vsync: this, duration: const Duration(milliseconds: 600));
  Offset? _start;

  @override
  void dispose() {
    _roll.dispose();
    super.dispose();
  }

  void _move(Offset p) {
    final s = _start;
    if (s == null || _roll.value > 0) return;
    if ((p - s).dx.abs() < 70) return;
    widget.env.play(widget.step.sfx);
    _roll.forward().then((_) => Timer(const Duration(milliseconds: 500), widget.env.done));
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(builder: (context, box) {
        final s = math.min(box.maxWidth * 0.75, box.maxHeight * 0.6);
        return Listener(
          behavior: HitTestBehavior.opaque,
          onPointerDown: (e) => _start = e.localPosition,
          onPointerMove: (e) => _move(e.localPosition),
          child: Center(
            child: AnimatedBuilder(
              animation: _roll,
              builder: (_, _) => SizedBox(
                width: s,
                height: s,
                child: _roll.value < 0.6
                    ? Transform(
                        alignment: Alignment.centerRight,
                        transform: Matrix4.diagonal3Values(1 - _roll.value * 1.3, 1, 1),
                        child: Stack(fit: StackFit.expand, children: [Art(widget.step.art), const Opacity(opacity: 0.85, child: Art('food/batter_cooked'))]),
                      )
                    : Opacity(opacity: ((_roll.value - 0.6) / 0.4).clamp(0, 1), child: Art(widget.step.result)),
              ),
            ),
          ),
        );
      });
}
