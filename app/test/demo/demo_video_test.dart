// Records a demo video of 動物小餐廳 being played: a scripted child (a white
// dot where the finger is) with a caption under the phone screen; the music
// and sounds the app asked for are written down and mixed in afterwards by
// tools/demo_audio.py.
//
//   flutter test test/demo/demo_video_test.dart --dart-define=DEMO=true
//   python3 ../tools/demo_audio.py
//
// Needs ffmpeg; writes build/demo/demo.mp4, chapters.txt and sounds.txt.
// Skipped in normal test runs.
import 'dart:io';
import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:animal_restaurant/app/app.dart';
import 'package:animal_restaurant/app/strings.dart';
import 'package:animal_restaurant/core/dishes.dart';
import 'package:animal_restaurant/core/providers.dart';
import 'package:animal_restaurant/core/sounds.dart';
import 'package:animal_restaurant/core/store.dart';
import 'package:animal_restaurant/core/voice.dart';
import 'package:animal_restaurant/features/kitchen/steps.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers.dart' show loadFonts;

const _phone = Size(390, 844);
const _captionHeight = 84.0;
const _fps = 10;
const _demo = bool.fromEnvironment('DEMO');

/// The music and sounds asked for, with the frame they were asked at.
class _Track implements Sounds {
  _Track(this.frame);

  final int Function() frame;
  final lines = <String>[];
  final _holders = MusicHolders();
  Music? _playing;

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) => lines.add('${frame()} sfx $sfx');

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _changed();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _changed();
  }

  void _changed() {
    final now = _holders.current;
    if (now == _playing) return;
    _playing = now;
    lines.add('${frame()} music ${now?.file ?? '-'}');
  }
}

/// What the caption says about each kind of step: what is learned.
String _about(CookStep s) => switch (s.kind) {
      StepKind.rub => s.art == 'ui/hands_wash' ? '先洗手：搓出泡泡（衛生習慣）' : (s.sfx == 'shake' ? '搖一搖：手指左右搓' : '洗乾淨：手指在上面搓一搓'),
      StepKind.cut => s.count == 1 ? '切成三角形：形狀' : '沿著虛線切，邊切邊數：數數',
      StepKind.tapIn => '點一下放進去，一個一個數：數量',
      StepKind.stir => '手指畫圈圈攪拌（也是寫字前的手部練習）',
      StepKind.pour => '按住倒，到紅線就放開：多和少',
      StepKind.cook => '等顏色變金黃，再往上滑翻面：耐心',
      StepKind.adult => '爐火、熱水要請大人幫忙：安全',
      StepKind.build => '照卡片的順序疊起來：順序和規律',
      StepKind.wrap => '放餡、捏一捏，包水餃：數數',
      StepKind.boil => '等水餃浮起來，再撈起來',
      StepKind.finish => '最後完成：淋醬、蓋蓋子、插吸管',
      StepKind.roll => '往旁邊滑，捲起來',
    };

void main() {
  testWidgets('demo video', skip: !_demo, (tester) async {
    await tester.runAsync(loadFonts);
    tester.view.physicalSize = Size(_phone.width * 3, (_phone.height + _captionHeight) * 3);
    tester.view.devicePixelRatio = 3;
    addTearDown(tester.view.reset);

    var frameCount = 0;
    final track = _Track(() => frameCount);
    final finger = ValueNotifier<Offset?>(null);
    final caption = ValueNotifier<String>('');
    final key = GlobalKey();
    await tester.pumpWidget(RepaintBoundary(
      key: key,
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: Column(children: [
          SizedBox.fromSize(
            size: _phone,
            child: MediaQuery(
              data: const MediaQueryData(size: _phone, devicePixelRatio: 3, padding: EdgeInsets.only(top: 24)),
              child: Stack(children: [
                ProviderScope(
                  overrides: [
                    storeProvider.overrideWithValue(MemoryStore()),
                    soundsProvider.overrideWithValue(track),
                    voiceProvider.overrideWithValue(const SilentVoice()),
                    randomProvider.overrideWithValue(math.Random(5)),
                  ],
                  child: const RestaurantApp(),
                ),
                IgnorePointer(child: ValueListenableBuilder(valueListenable: finger, builder: (_, at, _) => _Finger(at))),
              ]),
            ),
          ),
          SizedBox(
            width: _phone.width,
            height: _captionHeight,
            child: ColoredBox(
              color: const Color(0xFF6B4A3A),
              child: Center(
                child: ValueListenableBuilder(
                  valueListenable: caption,
                  builder: (_, text, _) => Text(text,
                      textAlign: TextAlign.center, style: const TextStyle(fontFamily: 'Huninn', color: Colors.white, fontSize: 17, height: 1.35)),
                ),
              ),
            ),
          ),
        ]),
      ),
    ));

    final rec = (await tester.runAsync(() => _Recorder.start(key)))!;
    final marks = <String>[];
    void mark(String name) => marks.add('$name $frameCount');
    Future<void> frames(int n) async {
      for (var i = 0; i < n; i++) {
        frameCount++;
        await tester.runAsync(() async {
          await rec.capture();
          await Future<void>.delayed(const Duration(milliseconds: 15));
        });
        await tester.pump(const Duration(milliseconds: 1000 ~/ _fps));
      }
    }

    Future<void> seconds(double s) => frames((s * _fps).round());
    Future<void> touch(Offset at) async {
      finger.value = at;
      await frames(2);
      await tester.tapAt(at);
      await frames(2);
      finger.value = null;
    }

    Future<void> label(String l) => touch(tester.getCenter(find.bySemanticsLabel(l).first));
    Future<void> drag(List<Offset> points, {int every = 1}) async {
      finger.value = points.first;
      final g = await tester.startGesture(points.first);
      await frames(1);
      for (var i = 1; i < points.length; i++) {
        await g.moveTo(points[i]);
        finger.value = points[i];
        if (i % every == 0) await frames(1);
      }
      await g.up();
      finger.value = null;
      await frames(1);
    }

    Rect area(Type t) => tester.getRect(find.byType(t));
    ProviderContainer container() => ProviderScope.containerOf(tester.element(find.byType(RestaurantApp)));

    Future<void> play(CookStep step) async {
      switch (step.kind) {
        case StepKind.rub:
          final r = area(RubStep);
          final c = Offset(r.center.dx, r.top + r.height * 0.48);
          await drag([for (var i = 0; i < 48; i++) c + Offset((i % 2 == 0 ? -1 : 1) * 70.0, (i % 3) * 10.0)]);
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
              await drag([for (var k = 0; k <= 6; k++) Offset(x, item.top + 4 + (item.height - 8) * k / 6)]);
              await frames(3);
            }
          }
        case StepKind.tapIn:
          for (var i = 0; i < step.count; i++) {
            await label(Strings.tapIn);
            await frames(5);
          }
        case StepKind.stir:
          final r = area(StirStep);
          final c = Offset(r.center.dx, r.top + r.height * 0.45);
          await drag([for (var i = 0; i <= 56; i++) c + Offset(math.cos(i * math.pi / 7), math.sin(i * math.pi / 7)) * 80]);
        case StepKind.pour:
          final at = area(PourStep).center;
          finger.value = at;
          final g = await tester.startGesture(at);
          await seconds(2.2);
          await g.up();
          finger.value = null;
        case StepKind.cook:
          await seconds(4.4);
          final c = area(CookPanStep).center;
          await drag([for (var i = 0; i <= 6; i++) c + Offset(0, -i * 25.0)]);
        case StepKind.adult:
          await seconds(1.5);
          await label(Strings.adultHere);
        case StepKind.build:
          for (final art in step.sequence) {
            await label(Strings.foodName(art));
            await frames(3);
          }
        case StepKind.wrap:
          for (var i = 0; i < step.count; i++) {
            await label(Strings.wrapFill);
            await frames(3);
            await label(Strings.wrapPinch);
            await label(Strings.wrapPinch);
            await frames(3);
          }
        case StepKind.boil:
          await seconds(3.2);
          await label(Strings.floated);
        case StepKind.finish:
          for (final art in step.sequence) {
            await label(Strings.foodName(art));
            await frames(4);
          }
        case StepKind.roll:
          final c = area(RollStep).center;
          await drag([for (var i = 0; i <= 6; i++) c + Offset(i * 25.0 - 75, 0)]);
      }
      await seconds(2.2);
    }

    // The restaurant opens.
    mark('restaurant');
    caption.value = '動物小餐廳：動物客人來點餐\n點餐單只有圖，不用認字';
    final first = Order(dishById('sandwich')!, 3);
    container().read(visitProvider.notifier).take(first);
    await seconds(3.5);
    caption.value = '小熊要番茄起司三明治，要 3 片番茄';
    await seconds(2.5);

    for (final (i, dish) in dishes.indexed) {
      final order = i == 0 ? first : Order(dish, dish.little.$2);
      if (i > 0) {
        container().read(visitProvider.notifier).take(order);
        caption.value = '${dish.customer.zh}來了：${Strings.orderShort(order)}';
        await seconds(3);
      }
      mark(dish.id);
      await label(Strings.start);
      await seconds(1.2);
      for (final step in order.stepsFor(Level.little)) {
        caption.value = _about(step);
        await seconds(1.2);
        await play(step);
      }
      caption.value = '完成了！端給客人';
      await seconds(1.5);
      await label(Strings.serve);
      caption.value = '客人吃得好開心：得到金幣和星星';
      await seconds(3);
      await label(Strings.nextCustomer);
      await seconds(1);
    }

    mark('book');
    caption.value = '食譜書：做過的菜和步驟，每道做 3 次得到 3 顆星';
    await label(Strings.book);
    await seconds(2.5);
    await label(dishes[2].zh);
    await seconds(3);
    await label(Strings.back);
    await seconds(1);
    caption.value = '';
    mark('end');
    await seconds(0.5);

    await tester.runAsync(() async {
      await rec.finish();
      File('build/demo/chapters.txt').writeAsStringSync('${marks.join('\n')}\n');
      File('build/demo/sounds.txt').writeAsStringSync('fps $_fps\nframes $frameCount\n${track.lines.join('\n')}\n');
    });
    await tester.pumpWidget(const SizedBox());
    await tester.pump(const Duration(milliseconds: 100));
  }, timeout: const Timeout(Duration(minutes: 40)));
}

class _Finger extends StatelessWidget {
  const _Finger(this.at);

  final Offset? at;

  @override
  Widget build(BuildContext context) {
    final p = at;
    if (p == null) return const SizedBox.expand();
    return Stack(children: [
      Positioned(
        left: p.dx - 22,
        top: p.dy - 22,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white.withValues(alpha: 0.55),
            border: Border.all(color: const Color(0xFF6B4A3A).withValues(alpha: 0.5), width: 3),
          ),
        ),
      ),
    ]);
  }
}

/// Streams frames of [key]'s boundary into ffmpeg.
class _Recorder {
  _Recorder(this._key, this._ffmpeg);

  final GlobalKey _key;
  final Process _ffmpeg;

  static Future<_Recorder> start(GlobalKey key) async {
    Directory('build/demo').createSync(recursive: true);
    final size = Size(_phone.width * 2, (_phone.height + _captionHeight) * 2);
    final ffmpeg = await Process.start('ffmpeg', [
      '-y', '-loglevel', 'error',
      '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', '${size.width.toInt()}x${size.height.toInt()}', '-r', '$_fps', '-i', '-',
      '-vf', 'fps=30', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-movflags', '+faststart', 'build/demo/demo_silent.mp4',
    ]);
    ffmpeg.stderr.listen(stderr.add);
    return _Recorder(key, ffmpeg);
  }

  Future<void> capture() async {
    final boundary = _key.currentContext!.findRenderObject()! as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    image.dispose();
    _ffmpeg.stdin.add(bytes!.buffer.asUint8List());
    await _ffmpeg.stdin.flush();
  }

  Future<void> finish() async {
    await _ffmpeg.stdin.flush();
    await _ffmpeg.stdin.close();
    final code = await _ffmpeg.exitCode;
    if (code != 0) throw StateError('ffmpeg failed ($code)');
  }
}
