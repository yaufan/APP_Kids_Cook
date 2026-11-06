import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/strings.dart';
import '../../app/theme.dart';
import '../../app/version.dart';
import '../../core/dishes.dart';
import '../../core/providers.dart';

/// Parent mode (after the gate): how it is going, the settings, and real
/// recipes to make together.
class ParentScreen extends ConsumerWidget {
  const ParentScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final g = ref.watch(gameProvider);
    final s = g.settings;
    final game = ref.read(gameProvider.notifier);

    Widget section(String title, List<Widget> children) => Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Material(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(18, 14, 18, 10),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(title, style: const TextStyle(fontSize: 15, color: Clay.inkSoft, fontWeight: FontWeight.w700)),
                const SizedBox(height: 6),
                ...children,
              ]),
            ),
          ),
        );

    Widget toggle(String label, bool value, void Function(bool) set, {Key? key}) =>
        SwitchListTile(key: key, contentPadding: EdgeInsets.zero, title: Text(label, style: const TextStyle(fontSize: 17)), value: value, onChanged: set);

    return Scaffold(
      backgroundColor: Clay.parentBg,
      appBar: AppBar(
        backgroundColor: Clay.parentBg,
        title: const Text(Strings.parentTitle),
        leading: IconButton(icon: const Icon(Icons.close_rounded), tooltip: Strings.back, onPressed: () => context.pop()),
      ),
      body: ListView(padding: const EdgeInsets.fromLTRB(16, 8, 16, 32), children: [
        section(Strings.progress, [
          Text(Strings.servedLine(g.served, g.coins), style: const TextStyle(fontSize: 17)),
          const SizedBox(height: 6),
          for (final d in dishes) Text('${d.zh}：${Strings.timesCooked(g.cooked[d.id] ?? 0)}', style: const TextStyle(fontSize: 16)),
          const SizedBox(height: 6),
        ]),
        section(Strings.level, [
          RadioGroup<Level>(
            groupValue: s.level,
            onChanged: (v) => game.settings((x) => x.copyWith(level: v)),
            child: Column(children: [
              for (final l in Level.values)
                RadioListTile<Level>(
                  key: ValueKey('level-${l.name}'),
                  contentPadding: EdgeInsets.zero,
                  value: l,
                  title: Text(Strings.levelName(l), style: const TextStyle(fontSize: 16)),
                ),
            ]),
          ),
          toggle(Strings.english, s.english, (v) => game.settings((x) => x.copyWith(english: v)), key: const ValueKey('english')),
        ]),
        section(Strings.sound, [
          toggle(Strings.music, s.music, (v) => game.settings((x) => x.copyWith(music: v)), key: const ValueKey('music')),
          toggle(Strings.effects, s.sounds, (v) => game.settings((x) => x.copyWith(sounds: v)), key: const ValueKey('effects')),
          toggle(Strings.voice, s.voice, (v) => game.settings((x) => x.copyWith(voice: v)), key: const ValueKey('voice')),
        ]),
        section(Strings.together, [
          const Text(Strings.togetherNote, style: TextStyle(fontSize: 14, height: 1.5, color: Clay.inkSoft)),
          const SizedBox(height: 8),
          for (final (name, how) in Strings.realRecipes)
            Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                Text(how, style: const TextStyle(fontSize: 15, height: 1.5)),
              ]),
            ),
        ]),
        section(Strings.edition, [
          const Text(Strings.fullNote, style: TextStyle(fontSize: 14, height: 1.5, color: Clay.inkSoft)),
          toggle(Strings.fullTest, s.full, (v) => game.settings((x) => x.copyWith(full: v)), key: const ValueKey('full')),
        ]),
        section(Strings.about, [
          Text(Strings.version(appVersion), style: const TextStyle(fontSize: 17)),
          const SizedBox(height: 4),
          const Text(Strings.privacy, style: TextStyle(fontSize: 14, height: 1.5, color: Clay.inkSoft)),
          const SizedBox(height: 8),
        ]),
      ]),
    );
  }
}
