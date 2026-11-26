import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';
import '../parent/parent_gate.dart';

/// The play time is up (docs/design.md 「每天可以玩多久」): evening falls on
/// the restaurant, the sign turns to its night side, the door bell rings
/// and the little chef sends the child off: 「打烊囉！換你去做了！去幫爸爸
/// 媽媽擺碗筷吧」. Only a parent (through the gate) or an hour's wait opens
/// it again (RestGuard).
class RestScreen extends ConsumerStatefulWidget {
  const RestScreen({super.key});

  @override
  ConsumerState<RestScreen> createState() => _RestScreenState();
}

class _RestScreenState extends ConsumerState<RestScreen> with HushOnLeave {
  late final Sounds _sounds;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    // A closed restaurant is quiet: no music.
    _sounds.hold(this, null);
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      _sounds.play('closing');
      speak(ref, '${Strings.restTitle}${Strings.restLine}');
    });
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  Future<void> _parent() async {
    if (!await showParentGate(context) || !mounted) return;
    ParentPass.take();
    ref.read(gameProvider.notifier).change((g) => g.playOn(ref.read(clockProvider)()));
    context.go('/');
  }

  @override
  Widget build(BuildContext context) => BackKey(
        child: Scaffold(
          backgroundColor: const Color(0xFF3E4C7E),
          body: LayoutBuilder(builder: (context, box) {
            final w = box.maxWidth, h = box.maxHeight;
            final pad = MediaQuery.paddingOf(context);
            final sign = math.min(w * 0.62, h * 0.3);
            return Stack(children: [
              const Positioned.fill(child: Art('scenes/restaurant', fit: BoxFit.cover)),
              Positioned.fill(child: ColoredBox(color: const Color(0xFF2B3566).withValues(alpha: 0.66))),
              // The sign, turned to the night side.
              Positioned(
                left: w / 2 - sign / 2,
                top: pad.top + h * 0.06,
                width: sign,
                height: sign * 239 / 260,
                child: const Breathing(amount: 0.02, child: Art('ui/closed_sign')),
              ),
              // What to do now.
              Positioned(
                left: 20,
                right: 20,
                top: pad.top + h * 0.08 + sign * 239 / 260,
                child: Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 480),
                    child: ClayBox(
                      color: Clay.cream,
                      radius: 28,
                      padding: const EdgeInsets.fromLTRB(18, 14, 18, 18),
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        Text(Strings.restTitle, textAlign: TextAlign.center, style: TextStyle(fontSize: math.min(32, w * 0.08), fontWeight: FontWeight.w700, color: Clay.tomato)),
                        const SizedBox(height: 10),
                        Row(children: [
                          const SizedBox(width: 72, height: 72, child: Art('chef/chef')),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(Strings.restLine,
                                key: const ValueKey('rest-line'), style: TextStyle(fontSize: math.min(21, w * 0.055), height: 1.45, fontWeight: FontWeight.w700, color: Clay.ink)),
                          ),
                        ]),
                      ]),
                    ),
                  ),
                ),
              ),
              // Only a parent opens it again now.
              Positioned(
                left: 0,
                right: 0,
                bottom: pad.bottom + 18,
                child: Center(
                  child: Semantics(
                    container: true,
                    button: true,
                    label: Strings.restParent,
                    excludeSemantics: true,
                    onTap: _parent,
                    child: Pressable(
                      onTap: _parent,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        decoration: BoxDecoration(color: Colors.white.withValues(alpha: 0.88), borderRadius: BorderRadius.circular(24)),
                        child: const Row(mainAxisSize: MainAxisSize.min, children: [
                          Icon(Icons.lock_outline_rounded, color: Clay.inkSoft, size: 20),
                          SizedBox(width: 6),
                          Text(Strings.restParent, style: TextStyle(fontSize: 16, color: Clay.inkSoft)),
                        ]),
                      ),
                    ),
                  ),
                ),
              ),
            ]);
          }),
        ),
      );
}
