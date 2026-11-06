import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/dishes.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// The restaurant (the home screen): a customer at the counter with their
/// order in pictures, "開始做", and once served, the customer eating happily
/// and the coins and star it earned.
class RestaurantScreen extends ConsumerStatefulWidget {
  const RestaurantScreen({super.key});

  @override
  ConsumerState<RestaurantScreen> createState() => _RestaurantScreenState();
}

class _RestaurantScreenState extends ConsumerState<RestaurantScreen> with SingleTickerProviderStateMixin {
  late final Sounds _sounds;
  late final _enter = AnimationController(vsync: this, duration: const Duration(milliseconds: 700))..forward();
  Order? _greeted;
  bool _thanked = false;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.restaurant);
  }

  @override
  void dispose() {
    _enter.dispose();
    _sounds.release(this);
    super.dispose();
  }

  void _say(String zh, {String? en}) {
    final s = ref.read(gameProvider).settings;
    if (mounted && s.voice) ref.read(voiceProvider).say(zh, en: s.english ? en : null);
  }

  /// A new customer says hello and what they would like; a served one says
  /// thank you.
  void _react(Visit v) {
    if (v.served) {
      if (_thanked) return;
      _thanked = true;
      _sounds.play('yum');
      Future.delayed(const Duration(milliseconds: 600), () {
        if (!mounted) return;
        _sounds.play(voiceOf(v.order.dish.customer));
        _sounds.play('coin');
      });
      _say(Strings.yum);
      return;
    }
    if (identical(_greeted, v.order)) return;
    _greeted = v.order;
    _thanked = false;
    _enter.forward(from: 0);
    _sounds.play(voiceOf(v.order.dish.customer));
    _say(Strings.order(v.order), en: v.order.dish.en);
  }

  Future<void> _openParent() async {
    if (await showParentGate(context) && mounted) await context.push('/parent');
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final visit = ref.watch(visitProvider);
    WidgetsBinding.instance.addPostFrameCallback((_) => _react(visit));
    final order = visit.order;
    final customer = order.dish.customer;
    return Scaffold(
      body: Stack(children: [
        const Positioned.fill(child: Art('scenes/restaurant', fit: BoxFit.cover)),
        SafeArea(
          child: LayoutBuilder(builder: (context, box) {
            final w = box.maxWidth, h = box.maxHeight;
            final cw = math.min(w * 0.62, h * 0.36);
            final counterTop = h * 0.66;
            return Stack(children: [
              // The top bar.
              Positioned(
                left: 10,
                right: 10,
                top: 6,
                child: Row(children: [
                  SizedBox(width: 50, height: 50, child: ClayBox(color: Colors.white, radius: 25, padding: const EdgeInsets.all(4), child: const Art('chef/chef'))),
                  const SizedBox(width: 8),
                  _Chip(art: 'ui/coin', value: g.coins, label: Strings.coins),
                  const SizedBox(width: 6),
                  _Chip(art: 'ui/star', value: g.stars, label: Strings.stars),
                  const Spacer(),
                  Semantics(
                    container: true,
                    button: true,
                    label: Strings.book,
                    excludeSemantics: true,
                    onTap: () => context.push('/book'),
                    child: Pressable(
                      onTap: () => context.push('/book'),
                      child: SizedBox(width: 56, height: 56, child: ClayBox(color: Colors.white, radius: 28, padding: const EdgeInsets.all(8), child: const Art('ui/recipe_book'))),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Semantics(
                    container: true,
                    button: true,
                    label: Strings.parent,
                    excludeSemantics: true,
                    onTap: _openParent,
                    child: GestureDetector(
                      behavior: HitTestBehavior.opaque,
                      onTap: _openParent,
                      child: Container(
                        width: 44,
                        height: 44,
                        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.75), shape: BoxShape.circle),
                        child: const Icon(Icons.lock_outline_rounded, color: Clay.inkSoft, size: 22),
                      ),
                    ),
                  ),
                ]),
              ),
              // The customer, behind the counter.
              AnimatedBuilder(
                animation: _enter,
                builder: (context, child) {
                  final v = Curves.easeOutBack.transform(_enter.value);
                  return Positioned(
                    left: w / 2 - cw / 2 + (1 - v) * w * 0.7,
                    top: counterTop - cw * 0.92,
                    width: cw,
                    height: cw,
                    child: child!,
                  );
                },
                child: Semantics(
                  container: true,
                  label: customer.zh,
                  excludeSemantics: true,
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => _sounds.play(voiceOf(customer)),
                    child: Breathing(child: Art(visit.served ? 'customers/${customer.name}_happy' : 'customers/${customer.name}', fit: BoxFit.contain)),
                  ),
                ),
              ),
              // The dish on the counter once served.
              if (visit.served)
                Positioned(left: w / 2 - 70, top: counterTop - 40, width: 140, height: 140, child: Art(order.dish.icon)),
              // The order (or the thank-you).
              Positioned(
                left: 18,
                right: 18,
                top: math.max(70, counterTop - cw * 0.92 - 150),
                child: Center(
                  child: GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => _say(Strings.order(order), en: order.dish.en),
                    child: Semantics(
                      container: true,
                      label: visit.served ? Strings.yum : Strings.order(order),
                      excludeSemantics: true,
                      child: Bubble(
                        child: visit.served
                            ? Column(mainAxisSize: MainAxisSize.min, children: [
                                const Text(Strings.yum, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700, color: Clay.ink)),
                                const SizedBox(height: 4),
                                Row(mainAxisSize: MainAxisSize.min, children: [
                                  const SizedBox(width: 28, height: 28, child: Art('ui/coin')),
                                  Text(' +${3 + order.count}   ', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                                  const SizedBox(width: 28, height: 28, child: Art('ui/star')),
                                  const Text(' +1', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w700)),
                                ]),
                              ])
                            : _OrderPicture(order: order),
                      ),
                    ),
                  ),
                ),
              ),
              // Start cooking, or the next customer.
              Positioned(
                left: 0,
                right: 0,
                bottom: 22,
                child: Center(
                  child: visit.served
                      ? ClayButton(
                          label: Strings.nextCustomer,
                          icon: const Icon(Icons.waving_hand_rounded, color: Clay.ink, size: 40),
                          color: Clay.butter,
                          wide: true,
                          size: 80,
                          onTap: () => ref.read(visitProvider.notifier).next(),
                        )
                      : Breathing(
                          amount: 0.04,
                          period: const Duration(milliseconds: 1300),
                          child: ClayButton(
                            label: Strings.start,
                            icon: const Icon(Icons.play_arrow_rounded, color: Colors.white, size: 48),
                            color: Clay.tomato,
                            textColor: Colors.white,
                            wide: true,
                            size: 86,
                            onTap: () => context.push('/kitchen'),
                          ),
                        ),
                ),
              ),
            ]);
          }),
        ),
      ]),
    );
  }
}

/// The order in pictures: the dish, and how many of its counted thing.
class _OrderPicture extends StatelessWidget {
  const _OrderPicture({required this.order});

  final Order order;

  @override
  Widget build(BuildContext context) => Column(mainAxisSize: MainAxisSize.min, children: [
        Row(mainAxisSize: MainAxisSize.min, children: [
          SizedBox(width: 92, height: 92, child: Art(order.dish.icon)),
          const SizedBox(width: 8),
          Column(mainAxisSize: MainAxisSize.min, children: [
            Wrap(spacing: 2, runSpacing: 2, children: [
              for (var i = 0; i < order.count; i++) SizedBox(width: 34, height: 34, child: Art(order.dish.counted)),
            ]),
            const SizedBox(height: 4),
            Text('${order.count}', style: const TextStyle(fontSize: 30, fontWeight: FontWeight.w700, color: Clay.tomato)),
          ]),
        ]),
      ]);
}

class _Chip extends StatelessWidget {
  const _Chip({required this.art, required this.value, required this.label});

  final String art;
  final int value;
  final String label;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        label: '$label $value',
        excludeSemantics: true,
        child: ClayBox(
          color: Colors.white,
          radius: 18,
          padding: const EdgeInsets.fromLTRB(6, 4, 12, 4),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            SizedBox(width: 26, height: 26, child: Art(art)),
            const SizedBox(width: 4),
            Text('$value', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Clay.ink)),
          ]),
        ),
      );
}
