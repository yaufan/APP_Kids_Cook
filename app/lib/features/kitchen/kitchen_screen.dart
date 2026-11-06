import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/dishes.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import 'steps.dart';

/// The kitchen: the recipe card's steps along the top, and the little game
/// for the step being done; "叮" and the next. At the end the dish is
/// ready to take out to the customer.
class KitchenScreen extends ConsumerStatefulWidget {
  const KitchenScreen({super.key});

  @override
  ConsumerState<KitchenScreen> createState() => _KitchenScreenState();
}

class _KitchenScreenState extends ConsumerState<KitchenScreen> {
  late final Sounds _sounds;
  late final Order _order;
  late final List<CookStep> _steps;
  var _at = 0;
  var _ticked = false;
  var _finished = false;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.cooking);
    _order = ref.read(visitProvider).order;
    _steps = _order.stepsFor(ref.read(gameProvider).settings.level);
    WidgetsBinding.instance.addPostFrameCallback((_) => _announce());
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _say(String zh, {String? en}) {
    final s = ref.read(gameProvider).settings;
    if (mounted && s.voice) ref.read(voiceProvider).say(zh, en: s.english ? en : null);
  }

  void _announce() {
    final step = _steps[_at];
    _say(step.zh, en: step.en.isEmpty ? null : step.en);
  }

  void _stepDone() {
    if (!mounted || _ticked) return;
    _sounds.play('ding');
    setState(() => _ticked = true);
    Timer(const Duration(milliseconds: 700), () {
      if (!mounted) return;
      if (_at + 1 < _steps.length) {
        setState(() {
          _at++;
          _ticked = false;
        });
        _announce();
      } else {
        _sounds.play('done');
        setState(() => _finished = true);
        _say(Strings.dishDone);
      }
    });
  }

  void _serve() {
    ref.read(visitProvider.notifier).served(3 + _order.count);
    context.pop();
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(gameProvider).settings;
    final env = StepEnv(
      play: _sounds.play,
      say: (zh, {en}) => _say(zh, en: en),
      english: s.english,
      level: s.level,
      done: _stepDone,
    );
    final step = _steps[_at];
    return Scaffold(
      body: Stack(children: [
        const Positioned.fill(child: Art('scenes/kitchen', fit: BoxFit.cover)),
        SafeArea(
          child: Column(children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(10, 8, 10, 0),
              child: Row(children: [
                CornerButton(label: Strings.back, icon: Icons.arrow_back_rounded, onTap: () => context.pop()),
                const SizedBox(width: 8),
                Expanded(child: _RecipeStrip(steps: _steps, at: _at, ticked: _ticked || _finished)),
              ]),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: GestureDetector(
                onTap: _announce,
                child: Bubble(text: _finished ? Strings.dishDone : step.zh, size: 19),
              ),
            ),
            Expanded(
              child: _finished
                  ? _Done(dish: _order.dish, onServe: _serve)
                  : AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      child: KeyedSubtree(key: ValueKey('step-$_at'), child: Padding(padding: const EdgeInsets.all(8), child: stepView(step, env))),
                    ),
            ),
          ]),
        ),
        if (_ticked && !_finished)
          const IgnorePointer(child: Center(child: SizedBox(width: 150, height: 150, child: Art('ui/check')))),
      ]),
    );
  }
}

/// The recipe card: a little picture for each step, the current one big.
class _RecipeStrip extends StatelessWidget {
  const _RecipeStrip({required this.steps, required this.at, required this.ticked});

  final List<CookStep> steps;
  final int at;
  final bool ticked;

  @override
  Widget build(BuildContext context) => SizedBox(
        height: 56,
        child: ListView.separated(
          scrollDirection: Axis.horizontal,
          itemCount: steps.length,
          separatorBuilder: (_, _) => const SizedBox(width: 4),
          itemBuilder: (context, i) {
            final done = i < at || (i == at && ticked);
            return Container(
              key: ValueKey('strip-$i'),
              width: i == at ? 56 : 44,
              padding: const EdgeInsets.all(5),
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: done ? Clay.mint : (i == at ? Clay.butter : Colors.white.withValues(alpha: 0.8)),
              ),
              child: done ? const Icon(Icons.check_rounded, color: Colors.white) : Art(steps[i].icon),
            );
          },
        ),
      );
}

class _Done extends StatelessWidget {
  const _Done({required this.dish, required this.onServe});

  final Dish dish;
  final VoidCallback onServe;

  @override
  Widget build(BuildContext context) => Column(children: [
        const Spacer(),
        Breathing(amount: 0.05, child: SizedBox(width: 240, height: 240, child: Art(dish.icon))),
        const SizedBox(height: 8),
        Text(dish.zh, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700, color: Clay.ink)),
        const Spacer(),
        ClayButton(label: Strings.serve, icon: const Art('tools/tray'), color: Clay.tomato, textColor: Colors.white, wide: true, size: 80, onTap: onServe),
        const SizedBox(height: 24),
      ]);
}
