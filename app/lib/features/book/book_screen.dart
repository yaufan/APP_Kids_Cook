import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/widgets.dart';
import '../../core/dishes.dart';
import '../../core/providers.dart';
import '../../core/sounds.dart';

/// The recipe book: every dish, how often it was made (a star each time,
/// three at most), and its steps as pictures.
class BookScreen extends ConsumerStatefulWidget {
  const BookScreen({super.key});

  @override
  ConsumerState<BookScreen> createState() => _BookScreenState();
}

class _BookScreenState extends ConsumerState<BookScreen> {
  late final Sounds _sounds;
  Dish? _open;

  @override
  void initState() {
    super.initState();
    _sounds = ref.read(soundsProvider);
    _sounds.hold(this, Music.book);
    _sounds.play('open');
  }

  @override
  void dispose() {
    _sounds.release(this);
    super.dispose();
  }

  void _tap(Dish d) {
    _sounds.play('open');
    setState(() => _open = d);
    final s = ref.read(gameProvider).settings;
    if (s.voice) ref.read(voiceProvider).say(d.zh, en: s.english ? d.en : null);
  }

  @override
  Widget build(BuildContext context) {
    final g = ref.watch(gameProvider);
    final open = _open;
    return Scaffold(
      backgroundColor: Clay.cream,
      body: SafeArea(
        child: Column(children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 8, 12, 4),
            child: Row(children: [
              CornerButton(label: Strings.back, icon: Icons.arrow_back_rounded, onTap: () => context.pop()),
              const SizedBox(width: 12),
              const SizedBox(width: 40, height: 40, child: Art('ui/recipe_book')),
              const SizedBox(width: 8),
              const Text(Strings.book, style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: Clay.ink)),
            ]),
          ),
          Expanded(
            child: open == null
                ? GridView.count(
                    padding: const EdgeInsets.all(14),
                    crossAxisCount: 2,
                    mainAxisSpacing: 14,
                    crossAxisSpacing: 14,
                    childAspectRatio: 0.82,
                    children: [
                      for (final d in dishes)
                        Semantics(
                          container: true,
                          button: true,
                          label: d.zh,
                          excludeSemantics: true,
                          child: Pressable(
                            sound: null,
                            onTap: () => _tap(d),
                            child: ClayBox(
                              color: Colors.white,
                              radius: 24,
                              padding: const EdgeInsets.all(10),
                              child: Column(children: [
                                Expanded(child: Opacity(opacity: (g.cooked[d.id] ?? 0) > 0 ? 1 : 0.45, child: Art(d.icon))),
                                Text(d.zh, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                                Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                  for (var i = 0; i < 3; i++)
                                    Opacity(opacity: i < g.starsOf(d.id) ? 1 : 0.2, child: const SizedBox(width: 24, height: 24, child: Art('ui/star'))),
                                ]),
                                Text(Strings.timesCooked(g.cooked[d.id] ?? 0), style: const TextStyle(fontSize: 13, color: Clay.inkSoft)),
                              ]),
                            ),
                          ),
                        ),
                    ],
                  )
                : _Recipe(dish: open, onClose: () => setState(() => _open = null), level: g.settings.level),
          ),
        ]),
      ),
    );
  }
}

class _Recipe extends StatelessWidget {
  const _Recipe({required this.dish, required this.onClose, required this.level});

  final Dish dish;
  final VoidCallback onClose;
  final Level level;

  @override
  Widget build(BuildContext context) {
    final steps = dish.steps(dish.little.$1, level);
    return GestureDetector(
      onTap: onClose,
      child: ListView(padding: const EdgeInsets.all(16), children: [
        SizedBox(height: 180, child: Art(dish.icon)),
        Center(child: Text(dish.zh, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700))),
        const SizedBox(height: 4),
        Center(child: Text(Strings.steps(steps.length), style: const TextStyle(fontSize: 15, color: Clay.inkSoft))),
        const SizedBox(height: 12),
        for (final (i, s) in steps.indexed)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: ClayBox(
              color: Colors.white,
              radius: 18,
              padding: const EdgeInsets.all(8),
              child: Row(children: [
                Container(
                  width: 34,
                  height: 34,
                  alignment: Alignment.center,
                  decoration: const BoxDecoration(color: Clay.butter, shape: BoxShape.circle),
                  child: Text('${i + 1}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                ),
                const SizedBox(width: 8),
                SizedBox(width: 52, height: 52, child: Art(s.icon)),
                const SizedBox(width: 8),
                Expanded(child: Text(s.zh, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600))),
              ]),
            ),
          ),
      ]),
    );
  }
}
