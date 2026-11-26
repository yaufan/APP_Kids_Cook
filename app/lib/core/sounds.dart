import 'dart:async';

import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/widgets.dart';

import 'dishes.dart';

/// The music (design/sounds/make_sounds.py), which changes with the screen.
enum Music {
  restaurant('music_restaurant'),
  cooking('music_cooking'),
  book('music_book');

  const Music(this.file);

  final String file;
}

/// A customer's happy voice.
String voiceOf(Customer c) => 'voice_${c.name}';

/// Short sounds are named by their file in assets/sounds/ (tap, chop, ding…).
abstract interface class Sounds {
  set music(bool on);
  set effects(bool on);

  void play(String sfx);

  /// [owner] (a screen) wants [music]; the one asked for last plays.
  void hold(Object owner, Music? music);

  void release(Object owner);
}

class MusicHolders {
  final _holders = <Object, Music?>{};

  void hold(Object owner, Music? music) {
    _holders.remove(owner);
    _holders[owner] = music;
  }

  void release(Object owner) => _holders.remove(owner);

  Music? get current => _holders.isEmpty ? null : _holders.values.last;
}

class SilentSounds implements Sounds {
  const SilentSounds();

  @override
  set music(bool on) {}

  @override
  set effects(bool on) {}

  @override
  void play(String sfx) {}

  @override
  void hold(Object owner, Music? music) {}

  @override
  void release(Object owner) {}
}

/// Where the sounds play: on Android the media stream, not the ringer (so a
/// phone on vibrate or silent still plays them, with the media volume), and
/// never taking the audio focus, so a sound never stops another one, the
/// music or the voice; on iOS mixed with other sounds (ambient).
AudioContext soundContext({required bool music}) => AudioContext(
      android: AudioContextAndroid(
        usageType: music ? AndroidUsageType.media : AndroidUsageType.game,
        contentType: music ? AndroidContentType.music : AndroidContentType.sonification,
        audioFocus: AndroidAudioFocus.none,
      ),
      iOS: AudioContextIOS(category: AVAudioSessionCategory.ambient),
    );

/// The one looping music player (audioplayers on the phone; tests give a
/// pretend one).
abstract interface class MusicLoop {
  Future<void> stop();
  Future<void> play(String file, double volume);
}

class _PlayerLoop implements MusicLoop {
  _PlayerLoop(this._ready);

  final Future<void> Function() _ready;
  AudioPlayer? _player;

  Future<AudioPlayer> _get() async {
    await _ready();
    var p = _player;
    if (p == null) {
      p = _player = AudioPlayer();
      await p.setAudioContext(soundContext(music: true));
      await p.setReleaseMode(ReleaseMode.loop);
    }
    return p;
  }

  @override
  Future<void> stop() async => (await _get()).stop();

  @override
  Future<void> play(String file, double volume) async {
    final p = await _get();
    await p.setVolume(volume);
    await p.play(AssetSource('sounds/$file.wav'));
  }

  void dispose() => unawaited(_player?.dispose());
}

/// Plays through audioplayers: a pool per sound, one looping player for
/// the music; quiet while the app is in the background.
class SystemSounds implements Sounds {
  SystemSounds({MusicLoop? loop}) {
    _loop = loop ?? _PlayerLoop(_ready);
    _lifecycle = AppLifecycleListener(onHide: () => _setAway(true), onShow: () => _setAway(false));
  }

  static const _sfxVolume = 0.85, _musicVolume = 0.35;

  late final AppLifecycleListener _lifecycle;
  late final MusicLoop _loop;
  final _pools = <String, Future<AudioPool>>{};
  final _holders = MusicHolders();
  Future<void>? _setUp;

  /// The music wanted now, and the music the loop was last started with.
  Music? _playing, _sounding;

  /// Switches of the music, one after the other: a stop asked for while a
  /// start is still loading waits for it, so the music never starts after
  /// it was stopped (the app hidden, the restaurant closed).
  Future<void> _switching = Future.value();
  var _music = true, _effects = true, _away = false;

  @override
  set music(bool on) {
    _music = on;
    _update();
  }

  @override
  set effects(bool on) => _effects = on;

  void _setAway(bool away) {
    _away = away;
    _update();
  }

  Future<void> _ready() => _setUp ??= AudioPlayer.global.setAudioContext(soundContext(music: false));

  @override
  void play(String sfx) {
    if (!_effects || _away || sfx.isEmpty) return;
    unawaited(_play(sfx));
  }

  Future<void> _play(String sfx) async {
    try {
      await _ready();
      final pool = await (_pools[sfx] ??= AudioPool.create(source: AssetSource('sounds/$sfx.wav'), maxPlayers: 3, audioContext: soundContext(music: false)));
      await pool.start(volume: _sfxVolume);
    } catch (_) {
      _pools.remove(sfx);
    }
  }

  @override
  void hold(Object owner, Music? music) {
    _holders.hold(owner, music);
    _update();
  }

  @override
  void release(Object owner) {
    _holders.release(owner);
    _update();
  }

  void _update() {
    final wanted = !_music || _away ? null : _holders.current;
    if (wanted == _playing) return;
    _playing = wanted;
    _switching = _switching.then((_) => _apply());
  }

  /// Makes the loop play what is wanted now (a later wish queues another).
  Future<void> _apply() async {
    final music = _playing;
    if (music == _sounding) return;
    try {
      await _loop.stop();
      _sounding = null;
      if (music == null) return;
      await _loop.play(music.file, _musicVolume);
      _sounding = music;
    } catch (_) {
      _sounding = null;
    }
  }

  void dispose() {
    _lifecycle.dispose();
    final loop = _loop;
    if (loop is _PlayerLoop) loop.dispose();
  }
}
