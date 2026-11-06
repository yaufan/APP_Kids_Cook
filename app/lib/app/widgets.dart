import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_svg/flutter_svg.dart';

import '../core/providers.dart';
import 'theme.dart';

/// A picture from assets/art/.
class Art extends StatelessWidget {
  const Art(this.path, {super.key, this.width, this.height, this.fit = BoxFit.contain});

  final String path;
  final double? width;
  final double? height;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) =>
      SvgPicture.asset('assets/art/$path.svg', width: width, height: height, fit: fit, excludeFromSemantics: true);
}

/// Squashes a little while pressed, like clay, and clicks.
class Pressable extends ConsumerStatefulWidget {
  const Pressable({super.key, required this.child, this.onTap, this.sound = 'tap'});

  final Widget child;
  final VoidCallback? onTap;
  final String? sound;

  @override
  ConsumerState<Pressable> createState() => _PressableState();
}

class _PressableState extends ConsumerState<Pressable> {
  var _down = false;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.onTap != null;
    return GestureDetector(
      behavior: HitTestBehavior.opaque,
      excludeFromSemantics: true,
      onTapDown: enabled ? (_) => setState(() => _down = true) : null,
      onTapCancel: enabled ? () => setState(() => _down = false) : null,
      onTapUp: enabled ? (_) => setState(() => _down = false) : null,
      onTap: enabled
          ? () {
              final s = widget.sound;
              if (s != null) ref.read(soundsProvider).play(s);
              widget.onTap!();
            }
          : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 90),
        transform: Matrix4.diagonal3Values(_down ? 1.06 : 1, _down ? 0.9 : 1, 1),
        transformAlignment: Alignment.bottomCenter,
        child: widget.child,
      ),
    );
  }
}

/// A gentle squash and stretch, like breathing.
class Breathing extends StatefulWidget {
  const Breathing({super.key, required this.child, this.amount = 0.04, this.period = const Duration(milliseconds: 2200)});

  final Widget child;
  final double amount;
  final Duration period;

  @override
  State<Breathing> createState() => _BreathingState();
}

class _BreathingState extends State<Breathing> with SingleTickerProviderStateMixin {
  late final _c = AnimationController(vsync: this, duration: widget.period)..repeat();

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => AnimatedBuilder(
        animation: _c,
        builder: (_, child) {
          final s = math.sin(_c.value * 2 * math.pi) * widget.amount;
          return Transform(
            alignment: Alignment.bottomCenter,
            transform: Matrix4.diagonal3Values(1 - s * 0.5, 1 + s, 1),
            child: child,
          );
        },
        child: widget.child,
      );
}

/// A lump of coloured clay: a rounded shape lit from the top left, with a
/// soft shadow under it and no outline.
class ClayBox extends StatelessWidget {
  const ClayBox({super.key, required this.color, this.radius = 26, this.child, this.padding = EdgeInsets.zero, this.shadow = true});

  final Color color;
  final double radius;
  final Widget? child;
  final EdgeInsets padding;
  final bool shadow;

  @override
  Widget build(BuildContext context) => Container(
        padding: padding,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(radius),
          gradient: RadialGradient(
            center: const Alignment(-0.45, -0.6),
            radius: 1.25,
            colors: [Color.lerp(color, Colors.white, 0.35)!, color, Color.lerp(color, Colors.black, 0.14)!],
            stops: const [0, 0.55, 1],
          ),
          boxShadow: shadow
              ? [
                  BoxShadow(color: Color.lerp(color, Colors.black, 0.45)!.withValues(alpha: 0.35), blurRadius: 10, offset: const Offset(0, 6)),
                ]
              : null,
        ),
        child: child,
      );
}

/// A big button for small hands: a picture and/or a word on clay.
class ClayButton extends StatelessWidget {
  const ClayButton({super.key, required this.label, this.icon, this.onTap, this.color = Clay.peach, this.size = 72, this.wide = false, this.showLabel = true, this.textColor = Clay.ink});

  final String label;
  final Widget? icon;
  final VoidCallback? onTap;
  final Color color;
  final double size;
  final bool wide;
  final bool showLabel;
  final Color textColor;

  @override
  Widget build(BuildContext context) {
    final content = Row(mainAxisSize: MainAxisSize.min, children: [
      if (icon != null) SizedBox(width: size * 0.6, height: size * 0.6, child: icon),
      if (icon != null && wide && showLabel) const SizedBox(width: 10),
      if (showLabel && (wide || icon == null))
        Text(label, style: TextStyle(fontSize: size * 0.34, fontWeight: FontWeight.w700, color: textColor)),
    ]);
    return Semantics(
      container: true,
      button: true,
      label: label,
      excludeSemantics: true,
      onTap: onTap,
      child: Pressable(
        onTap: onTap,
        child: Opacity(
          opacity: onTap == null ? 0.5 : 1,
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SizedBox(
              height: size,
              width: wide ? null : size,
              child: ClayBox(
                color: color,
                radius: size * 0.4,
                padding: EdgeInsets.symmetric(horizontal: wide ? size * 0.32 : 0),
                child: Center(child: content),
              ),
            ),
            if (showLabel && !wide && icon != null) ...[
              const SizedBox(height: 4),
              Text(label, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w700, color: Clay.ink)),
            ],
          ]),
        ),
      ),
    );
  }
}

/// What a customer says: a white rounded bubble.
class Bubble extends StatelessWidget {
  const Bubble({super.key, this.text, this.child, this.size = 20});

  final String? text;
  final Widget? child;
  final double size;

  @override
  Widget build(BuildContext context) => ClayBox(
        color: Colors.white,
        radius: 24,
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        child: child ?? Text(text ?? '', style: TextStyle(fontSize: size, height: 1.35, color: Clay.ink, fontWeight: FontWeight.w700)),
      );
}

/// A round back/close button in the corner.
class CornerButton extends StatelessWidget {
  const CornerButton({super.key, required this.label, required this.icon, this.onTap});

  final String label;
  final IconData icon;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) => Semantics(
        container: true,
        button: true,
        label: label,
        excludeSemantics: true,
        onTap: onTap,
        child: Pressable(
          onTap: onTap,
          child: SizedBox(width: 54, height: 54, child: ClayBox(color: Colors.white, radius: 27, child: Icon(icon, color: Clay.inkSoft, size: 28))),
        ),
      );
}

/// Dots for counting: [done] of [count] filled.
class CountDots extends StatelessWidget {
  const CountDots({super.key, required this.count, required this.done, this.size = 18, this.color = Clay.tomato});

  final int count;
  final int done;
  final double size;
  final Color color;

  @override
  Widget build(BuildContext context) => Row(mainAxisSize: MainAxisSize.min, children: [
        for (var i = 0; i < count; i++)
          Container(
            width: size,
            height: size,
            margin: EdgeInsets.symmetric(horizontal: size * 0.15),
            decoration: BoxDecoration(shape: BoxShape.circle, color: i < done ? color : Clay.creamDeep),
          ),
      ]);
}
