"""動物小餐廳 (Animal Restaurant): every sound in the app, made here from sine
waves and noise, so every one is ours: nothing recorded, nothing downloaded,
and every tune written for this app.

- Music (WAV, 16,000 Hz): three tunes for a little cafe kitchen, played on a
  marimba, a ukulele, a glockenspiel, a kalimba and a soft ocarina, with
  light percussion. Each tune is as long as its bars, and what still rings at
  the end is carried round to the start, so it loops without a seam.
- Short sounds, kitchen sounds and the customers' voices (WAV, 22,050 Hz).
  `sizzle` is a seamless loop too, so the app can keep a pan frying.
- Voices are a buzz through formant filters, as in 畫畫小鎮 and 字母寵物.
- Every random choice uses a fixed seed, so each run writes the same files.

The helpers (env, sweep, decay, lowpass, bandpass, partial, bell, marimba,
place, tune_loop, resonator, voice, ease, glide, bubble, above, spans, tidy,
write, report) come from 字母寵物's design/sounds/make_sounds.py; the
instruments uke, kalimba, ocarina, pluck_bass and metal, and every tune and
sound, are new.

    python3 design/sounds/make_sounds.py                  # writes app/assets/sounds/*.wav
    python3 design/sounds/make_sounds.py preview OUT.m4a  # and a listening preview
"""
import pathlib
import subprocess
import sys
import wave

import numpy as np
from scipy.signal import lfilter, resample_poly

OUT = pathlib.Path(__file__).resolve().parents[2] / "app" / "assets" / "sounds"
SR = 22050       # short sounds and voices
LOOP_SR = 16000  # music

# Notes (Hz), with flats as well as sharps.
NOTE = {f"{n}{o}": 440 * 2 ** ((k - 9) / 12 + o - 4)
        for o in range(1, 9) for k, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
for _o in range(1, 9):
    for _flat, _sharp in (("Db", "C#"), ("Eb", "D#"), ("Gb", "F#"), ("Ab", "G#"), ("Bb", "A#")):
        NOTE[f"{_flat}{_o}"] = NOTE[f"{_sharp}{_o}"]

# The ukulele's chord shapes, strummed in this order: the top string first,
# and it is a high one, as on a real (re-entrant) ukulele.
UKE = {k: v.split() for k, v in {
    "C": "G4 C4 E4 C5", "C6": "G4 C4 E4 A4", "Cmaj7": "G4 C4 E4 B4", "Am": "A4 C4 E4 A4",
    "Dm": "A4 D4 F4 A4", "Dm7": "A4 D4 F4 C5", "G": "G4 D4 G4 B4", "G7": "G4 D4 F4 B4",
    "A7": "G4 C#4 E4 A4", "F": "A4 C4 F4 A4", "Bb": "F4 D4 F4 Bb4", "Gm": "G4 D4 G4 Bb4",
    "D": "A4 D4 F#4 A4", "E": "G#4 E4 G#4 B4", "A": "A4 C#4 E4 A4",
}.items()}


# ---------------------------------------------------------------- helpers (from 字母寵物)


def t_of(dur, sr=SR):
    return np.arange(int(dur * sr)) / sr


def env(n, attack=0.005, release=0.05, sr=SR):
    """Up quickly, down smoothly: no clicks at either end."""
    e = np.ones(n)
    a, r = max(1, min(n, int(attack * sr))), max(1, min(n, int(release * sr)))
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def sweep(f, sr=SR):
    """A sine whose frequency follows the array [f] (Hz per sample)."""
    return np.sin(2 * np.pi * np.cumsum(f) / sr)


def decay(n, tau, sr=SR):
    return np.exp(-np.arange(n) / (tau * sr))


def lowpass(x, cutoff, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (freqs / cutoff) ** 4)
    return np.fft.irfft(spec, len(x))


def bandpass(x, lo, hi, sr=SR):
    spec = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / sr)
    spec *= 1 / (1 + (lo / np.maximum(freqs, 1)) ** 4) / (1 + (freqs / hi) ** 4)
    return np.fft.irfft(spec, len(x))


def norm(x):
    return x / max(1e-9, np.abs(x).max())


def partial(freq, t, sr):
    """A sine at [freq], or silence if it is too high for [sr] (it would fold
    back down as a wrong note)."""
    return np.sin(2 * np.pi * freq * t) if freq < 0.45 * sr else np.zeros_like(t)


def bell(freq, dur=0.5, sr=SR, bright=1.0):
    """A soft glockenspiel note: a few partials, the high ones dying first."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.35 * bright * partial(freq * 2.76, t, sr) * np.exp(-t / (dur * 0.12))
         + 0.15 * bright * partial(freq * 5.4, t, sr) * np.exp(-t / (dur * 0.06)))
    return x * env(len(t), 0.002, 0.03, sr)


def marimba(freq, dur=0.5, sr=SR):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / (dur * 0.3)) + 0.2 * partial(freq * 4, t, sr) * np.exp(-t / (dur * 0.05))
    return x * env(len(t), 0.003, 0.03, sr)


def place(total, parts, sr=SR):
    """[parts]: (start seconds, signal) mixed into [total] seconds."""
    out = np.zeros(int(total * sr))
    for start, sig in parts:
        i = int(start * sr)
        j = min(len(out), i + len(sig))
        out[i:j] += sig[: j - i]
    return out


def tune_loop(seconds, notes, sr=LOOP_SR):
    """[notes]: (start seconds, signal); what rings past [seconds] wraps to the start."""
    n = int(round(seconds * sr))
    tail = max(len(sig) + int(start * sr) for start, sig in notes) - n
    out = np.zeros(n + max(0, tail))
    for start, sig in notes:
        i = int(start * sr)
        out[i:i + len(sig)] += sig
    loop = out[:n].copy()
    if tail > 0:
        loop[:tail] += out[n:]
    return loop


def resonator(x, freq, bw, sr=SR, block=64):
    """A two-pole resonance at [freq] Hz (a number, or one per sample, for a
    sound that changes) of bandwidth [bw] Hz."""
    freq = np.broadcast_to(np.asarray(freq, dtype=float), x.shape)
    y, zi = np.zeros_like(x), np.zeros(2)
    r = np.exp(-np.pi * bw / sr)
    for i in range(0, len(x), block):
        th = 2 * np.pi * freq[i] / sr
        y[i:i + block], zi = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x[i:i + block], zi=zi)
    return y


def voice(f0, formants, rng, breath=0.03, rough=0.0, sr=SR):
    """A voice at pitch [f0] (Hz per sample) through [formants]: (Hz or Hz
    per sample, bandwidth, gain). [rough] jitters the pitch, for a growl."""
    n = len(f0)
    if rough:
        f0 = f0 * (1 + rough * lowpass(rng.standard_normal(n), 60, sr) * 3)
    buzz = 2 * (np.cumsum(f0) / sr % 1) - 1 + breath * rng.standard_normal(n)
    out = np.zeros(n)
    for f, bw, gain in formants:
        y = resonator(buzz, f, bw, sr)
        out += gain * y / max(1e-9, np.abs(y).max())
    return lowpass(out, 3800, sr)  # soft, not a kazoo


def ease(u):
    """0 to 1, smoothly, over u in 0..1."""
    u = np.clip(u, 0, 1)
    return u * u * (3 - 2 * u)


def glide(t, *points):
    """A value that moves smoothly between (time, value) [points]."""
    ts, vs = zip(*points)
    out = np.interp(t, ts, vs)
    return lowpass(out - out.mean(), 25) + out.mean() if len(t) > 64 else out


def bubble(rng, sr=SR, low=(300, 550), rise=(2.2, 3.2), dur=(0.04, 0.08)):
    """One little bubble: a quick rising blip that starts and ends at zero."""
    d = rng.uniform(*dur)
    t = t_of(d, sr)
    f0 = rng.uniform(*low)
    f = np.geomspace(f0, f0 * rng.uniform(*rise), len(t))
    return sweep(f, sr) * np.sin(np.pi * t / d)


def above(name, low):
    """The note called [name] (no octave) at or just above the note [low]."""
    for o in range(1, 9):
        if NOTE[f"{name}{o}"] >= NOTE[low] * 0.999:
            return f"{name}{o}"
    raise ValueError(name)


def spans(bars, beats_per_bar):
    """Bars like "F" or "Gm-C" (two chords, half a bar each) -> (beat, length in beats, chord)."""
    out = []
    for i, bar in enumerate(bars):
        parts = bar.split("-")
        each = beats_per_bar / len(parts)
        out += [(i * beats_per_bar + k * each, each, c) for k, c in enumerate(parts)]
    return out


# ---------------------------------------------------------------- new helpers and instruments


def melody(tune, beat, start=0.0, swing=0.0, bars=None, beats_per_bar=4):
    """[tune]: (note or None for a rest, beats) one after another ->
    (seconds, note, seconds long). [swing] (in beats) delays each note that
    falls halfway through a beat, for a lilt. [bars]: check the tune fills them."""
    if bars is not None:
        assert abs(sum(b for _, b in tune) - bars * beats_per_bar) < 1e-9, tune
    out, b = [], 0.0
    for name, beats in tune:
        if name:
            late = swing if abs(b % 1 - 0.5) < 1e-6 else 0.0
            out.append((start + (b + late) * beat, name, (beats - late) * beat))
        b += beats
    return out


def root_of(chord):
    return chord[:2] if len(chord) > 1 and chord[1] in "#b" else chord[0]


def third_of(chord):
    """Semitones from the root to the third: 3 for a minor chord, else 4."""
    rest = chord[len(root_of(chord)):]
    return 3 if rest.startswith("m") and not rest.startswith("maj") else 4


def uke(freq, dur=1.0, sr=LOOP_SR, bright=1.0, pos=0.18):
    """A ukulele's nylon string: whole-number harmonics shaped by where it is
    plucked ([pos] along the string), the high ones fading first."""
    t = t_of(dur, sr)
    x = np.zeros_like(t)
    for k in range(1, 10):
        a = abs(np.sin(np.pi * k * pos)) / np.sin(np.pi * pos) / k ** 1.5
        x += (a if k == 1 else a * bright) * partial(freq * k, t, sr) * np.exp(-t / (dur * 0.3 / (1 + 0.5 * (k - 1))))
    return x * env(len(t), 0.002, 0.05, sr)


def strum(chord, at, amp, dur, down=True, sr=LOOP_SR, gap=0.012, bright=0.8):
    """The ukulele strummed: its strings one after another, [gap] apart."""
    names = UKE[chord] if down else UKE[chord][::-1]
    return [(at + k * gap, amp * (1 - 0.06 * k) * uke(NOTE[n], dur, sr, bright)) for k, n in enumerate(names)]


def kalimba(freq, dur=1.8, sr=LOOP_SR):
    """A thumb piano's tine: a round note and a quick metal tick high above it
    (a tine's second mode is about 6.3 times the first)."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.3))
         + 0.28 * partial(freq * 6.27, t, sr) * np.exp(-t / 0.025)
         + 0.08 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.001, 0.08, sr)


def ocarina(freq, dur, sr=LOOP_SR):
    """A soft little ocarina: almost a pure tone, a slow vibrato on long
    notes, gentle in and out."""
    t = t_of(dur, sr)
    vib = 1 + 0.008 * np.sin(2 * np.pi * 5.0 * t) * ease((t - 0.18) / 0.25)
    ph = 2 * np.pi * np.cumsum(freq * vib) / sr
    x = np.sin(ph) + 0.1 * np.sin(2 * ph) + 0.04 * np.sin(3 * ph)
    return x * env(len(t), 0.025, min(0.12, dur * 0.4), sr)


def pluck_bass(freq, dur=1.0, sr=LOOP_SR):
    """A plucked double bass: round, short, warm."""
    t = t_of(dur, sr)
    x = (partial(freq, t, sr) * np.exp(-t / (dur * 0.35))
         + 0.45 * partial(freq * 2, t, sr) * np.exp(-t / (dur * 0.15))
         + 0.15 * partial(freq * 3, t, sr) * np.exp(-t / (dur * 0.08)))
    return x * env(len(t), 0.006, 0.08, sr)


def metal(freq, dur, sr=SR, ratios=(1, 1.59, 2.14, 2.65, 3.15), amps=(1, .6, .45, .3, .2), taus=(.5, .3, .2, .15, .1)):
    """A small metal ting (a coin, a spoon on a pot, an ice cube): partials
    that are not whole-number multiples; [taus] are fractions of [dur]."""
    t = t_of(dur, sr)
    x = sum(a * partial(freq * r, t, sr) * np.exp(-t / (dur * k)) for r, a, k in zip(ratios, amps, taus))
    return x * env(len(t), 0.0008, 0.03, sr)


def woodblock(freq, sr=LOOP_SR, dur=0.09):
    t = t_of(dur, sr)
    x = partial(freq, t, sr) * np.exp(-t / 0.018) + 0.45 * partial(freq * 2.3, t, sr) * np.exp(-t / 0.007)
    return x * env(len(t), 0.0008, 0.02, sr)


def shaker(rng, sr=LOOP_SR, dur=0.06):
    n = int(dur * sr)
    return norm(bandpass(rng.standard_normal(n), 3000, 7000, sr)) * env(n, 0.006, dur * 0.8, sr)


def kick(sr=LOOP_SR, dur=0.16):
    n = int(dur * sr)
    return sweep(np.geomspace(130, 55, n), sr) * decay(n, 0.05, sr) * env(n, 0.002, 0.04, sr)


def jingle(rng, dur=0.2, sr=SR):
    """A tambourine's little cymbals."""
    t = t_of(dur, sr)
    x = sum(rng.uniform(0.4, 1.0) * partial(f, t, sr) * np.exp(-t / rng.uniform(0.03, 0.07))
            for f in rng.uniform(4500, 9000, 8))
    x += 0.5 * norm(bandpass(rng.standard_normal(len(t)), 5000, 10000, sr)) * np.exp(-t / 0.02)
    return x * env(len(t), 0.001, 0.04, sr)


def noise_through(rng, centre, bw, n):
    """Noise through a resonance that can move: the voice of air and water."""
    return norm(resonator(rng.standard_normal(n), centre, bw))


def wrap_place(n, parts):
    """Like place, but what runs past the end comes round to the start (for a loop)."""
    out = np.zeros(n)
    for i, sig in parts:
        out[(i + np.arange(len(sig))) % n] += sig
    return out


# ---------------------------------------------------------------- music


def music_restaurant():
    """The restaurant: cosy and welcoming, a little cafe tune in C with a
    lilt (swung eighths). The ukulele strums, a plucked bass walks under it,
    a shaker and a soft wood click keep time. The marimba sings the tune,
    a glockenspiel sparkling an octave above; then a soft ocarina takes it.
    At the end the shop door's little bell: ting-ting."""
    beat, swing = 0.6, 1 / 6
    bars = ["Cmaj7", "Am", "Dm7", "G7", "Cmaj7", "A7", "Dm7-G7", "C6"]
    tune_a = [("G4", .5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5), ("E5", 1),
              ("A5", 1.5), ("G5", .5), ("E5", 2),
              ("F5", .5), ("E5", .5), ("D5", 1), ("A4", .5), ("C5", .5), ("D5", 1),
              ("B4", 1), ("D5", 1), ("F5", 2)]
    tune_b = [("G4", .5), ("C5", .5), ("E5", 1), ("D5", .5), ("C5", .5), ("G5", 1),
              ("A5", 1.5), ("G5", .5), ("E5", 1), ("C#5", 1),
              ("D5", .5), ("F5", .5), ("A5", 1), ("G5", .5), ("F5", .5), ("D5", 1),
              ("E5", 1.5), ("D5", .5), ("C5", 1), (None, 1)]
    notes = []
    for at, name, d in melody(tune_a, beat, 0, swing, bars=4):
        f = NOTE[name]
        notes += [(at, 0.7 * marimba(f, max(0.5, d + 0.3), LOOP_SR)), (at, 0.1 * bell(2 * f, 0.6, LOOP_SR, bright=0.4))]
    for at, name, d in melody(tune_b, beat, 16 * beat, swing, bars=4):
        f = NOTE[name]
        notes += [(at, 0.5 * ocarina(f, d * 0.92)), (at, 0.25 * marimba(f, 0.6, LOOP_SR))]
    whole = [(0, True, 0.30, 0.9), (1, True, 0.22, 0.6), (1.5, False, 0.15, 0.5),
             (2.5, False, 0.15, 0.5), (3, True, 0.22, 0.6), (3.5, False, 0.14, 0.5)]
    half = [(0, True, 0.28, 0.8), (1, True, 0.2, 0.5), (1.5, False, 0.14, 0.45)]
    for b, length, chord in spans(bars, 4):
        for off, down, a, d in (whole if length == 4 else half):
            notes += strum(chord, (b + off + (swing if off % 1 else 0)) * beat, a, d, down)
        root = NOTE[above(root_of(chord), "E2")]
        notes.append((b * beat, 0.55 * pluck_bass(root, 1.2)))
        if length == 4:
            fifth = root * 2 ** (7 / 12)
            notes.append(((b + 2) * beat, 0.45 * pluck_bass(fifth / 2 if fifth > NOTE["D3"] else fifth, 1.0)))
    rng = np.random.default_rng(101)
    beats = len(bars) * 4
    for b in range(beats):
        notes += [(b * beat, 0.06 * shaker(rng)), ((b + 0.5 + swing) * beat, 0.09 * shaker(rng))]
        if b % 2:
            notes.append((b * beat, 0.1 * woodblock(1500)))
        if b % 4 == 0:
            notes.append((b * beat, 0.3 * kick()))
    notes += [(31 * beat, 0.22 * bell(NOTE["G6"], 0.9, LOOP_SR, bright=0.5)),
              ((31.5 + swing) * beat, 0.2 * bell(NOTE["C7"], 0.9, LOOP_SR, bright=0.5))]
    x = tune_loop(beats * beat, notes)
    return lowpass(x, 4500, LOOP_SR)


def music_cooking():
    """Cooking: busy, light and steady, for little hands at work. A marimba
    bubbles away in eighths, a wood block goes tick-tock like a kitchen
    timer, a shaker and a soft drum keep it moving, the ukulele chops on
    two and four. The glockenspiel has a short tune with gaps in it (a spoon
    taps the pot in the gaps); then the ukulele takes a turn."""
    beat = 0.44
    bars = ["F", "Bb", "C", "F", "F", "Bb", "Gm-C", "F", "Dm", "Bb", "Gm", "C"]
    glock_tune = [  # bars 1-8
        ("A5", .5), ("C6", .5), ("A5", .5), ("F5", .5), ("G5", 1), (None, 1),
        ("Bb5", .5), ("A5", .5), ("G5", .5), ("F5", .5), ("D5", 1), (None, 1),
        ("E5", .5), ("G5", .5), ("C6", .5), ("Bb5", .5), ("A5", .5), ("G5", .5), ("E5", 1),
        ("F5", 1), ("C5", 1), ("F5", 1), (None, 1),
        ("A5", .5), ("C6", .5), ("A5", .5), ("F5", .5), ("G5", 1), (None, 1),
        ("D6", .5), ("C6", .5), ("Bb5", .5), ("A5", .5), ("G5", 1), (None, 1),
        ("Bb5", .5), ("A5", .5), ("G5", 1), ("E5", .5), ("F5", .5), ("G5", 1),
        ("F5", 1), ("C5", .5), ("F5", .5), (None, 2)]
    uke_tune = [  # bars 9-12
        ("D5", 1), ("F5", .5), ("A5", .5), (None, .5), ("A5", .5), ("G5", .5), ("F5", .5),
        ("D5", 1), ("F5", .5), ("Bb5", .5), (None, .5), ("Bb5", .5), ("A5", .5), ("G5", .5),
        ("G5", .5), ("Bb5", .5), ("D6", 1), ("C6", .5), ("Bb5", .5), ("A5", .5), ("G5", .5),
        ("E5", .5), ("G5", .5), ("C6", 1), (None, 2)]
    notes = [(at, 0.5 * bell(NOTE[n], 0.7, LOOP_SR, bright=0.7)) for at, n, _ in melody(glock_tune, beat, bars=8)]
    for at, name, _ in melody(uke_tune, beat, 32 * beat, bars=4):
        notes += [(at, 0.6 * uke(NOTE[name], 0.9)), (at, 0.12 * bell(NOTE[name], 0.5, LOOP_SR, bright=0.3))]
    for b, length, chord in spans(bars, 4):
        r = NOTE[above(root_of(chord), "C3")]
        steps = [0, 7, 12, 7, 12 + third_of(chord), 7, 12, 7][:int(length * 2)]
        for k, s in enumerate(steps):
            notes.append(((b + k / 2) * beat, (0.3 if k % 2 == 0 else 0.2) * marimba(r * 2 ** (s / 12), 0.32, LOOP_SR)))
        bass = NOTE[above(root_of(chord), "E2")]
        notes.append((b * beat, 0.5 * pluck_bass(bass, 0.6)))
        if length == 4:
            notes.append(((b + 2) * beat, 0.4 * pluck_bass(bass * 2 ** (7 / 12) / (2 if bass > NOTE["G2"] else 1), 0.6)))
        for off in ((1, 3) if length == 4 else (1,)):
            notes += strum(chord, (b + off) * beat, 0.1, 0.16, bright=0.6)
    rng = np.random.default_rng(102)
    beats = len(bars) * 4
    for b in range(beats):
        notes += [(b * beat, 0.12 * woodblock(1250 if b % 2 == 0 else 900)), ((b + 0.5) * beat, 0.08 * shaker(rng))]
        if b % 2 == 0:
            notes.append((b * beat, 0.3 * kick()))
    for b in (15, 15.5, 30, 30.5, 46, 46.5):  # a spoon on the pot, in the gaps of the tune
        notes.append((b * beat, 0.13 * metal(1480, 0.45, LOOP_SR)))
    x = tune_loop(beats * beat, notes)
    return lowpass(x, 5000, LOOP_SR)


def music_book():
    """The recipe book and other calm screens: gentle, in A. A kalimba sings a
    slow tune; a ukulele is picked softly, rocking up and down; a plucked
    bass and a warm hum hold the chords; a little glockenspiel twinkle at
    the end of each half."""
    beat = 0.68
    bars = ["A", "C#m", "D", "A", "F#m", "D", "Bm", "E"]
    tune = [("C#5", 1.5), ("E5", .5), ("A5", 2),
            ("G#5", 1.5), ("E5", .5), ("C#5", 2),
            ("F#5", 1), ("A5", 1), ("F#5", 1), ("D5", 1),
            ("E5", 3), (None, 1),
            ("C#5", 1), ("F#5", 1), ("A5", 1.5), ("G#5", .5),
            ("F#5", 1.5), ("E5", .5), ("D5", 2),
            ("D5", 1), ("F#5", 1), ("E5", 1), ("D5", 1),
            ("E5", 1.5), ("D5", .5), ("B4", 2)]
    notes = [(at, 0.7 * kalimba(NOTE[n], max(1.6, d + 0.8))) for at, n, d in melody(tune, beat, bars=8)]
    for i, chord in enumerate(bars):
        root = root_of(chord)
        base = NOTE[above(root, "G3")]
        t3 = 12 + third_of(chord)
        for k, s in enumerate([7, 12, t3, 12, 7, 12, t3, 12]):
            notes.append(((i * 4 + k / 2) * beat, (0.17 if k % 2 == 0 else 0.13) * uke(base * 2 ** (s / 12), 1.3, bright=0.6)))
        bass = NOTE[above(root, "E2")]
        notes += [(i * 4 * beat, 0.45 * pluck_bass(bass, 2.4)),
                  ((i * 4 + 2) * beat, 0.3 * pluck_bass(bass * 2 ** (7 / 12) / (2 if bass > NOTE["G2"] else 1), 1.6))]
        # the hum: the chord held, swelling in and out, two tones a hair apart
        d = 4 * beat + 1.0
        t = t_of(d, LOOP_SR)
        swell = np.sin(np.pi * t / d) ** 2
        tones = [base, base * 2 ** (t3 / 12 - 1), base * 2 ** (7 / 12)]
        hum = sum(np.sin(2 * np.pi * f * t) + np.sin(2 * np.pi * f * 1.002 * t) for f in tones)
        notes.append((i * 4 * beat, 0.03 * hum * swell))
    for k, n in enumerate(["E6", "C#6", "A5"]):  # end of the first half
        notes.append(((15 + k * 0.33) * beat, (0.22 - 0.03 * k) * bell(NOTE[n], 0.9, LOOP_SR, bright=0.4)))
    for k, n in enumerate(["G#5", "B5", "E6"]):  # end of the loop, leading home
        notes.append(((30.5 + k * 0.5) * beat, (0.16 + 0.02 * k) * bell(NOTE[n], 0.9, LOOP_SR, bright=0.4)))
    x = tune_loop(len(bars) * 4 * beat, notes)
    return lowpass(x, 3200, LOOP_SR)


MUSIC = {
    "music_restaurant": (music_restaurant, 0.28),
    "music_cooking": (music_cooking, 0.26),
    "music_book": (music_book, 0.24),
}


# ---------------------------------------------------------------- short sounds


def tap():
    """A button: a soft wooden-spoon tok."""
    t = t_of(0.07)
    x = (partial(980, t, SR) * np.exp(-t / 0.014) + 0.35 * partial(2350, t, SR) * np.exp(-t / 0.005)
         + 0.15 * partial(3900, t, SR) * np.exp(-t / 0.002))
    return x * env(len(t), 0.0008, 0.02)


def pop():
    """Something pops up: a round bloop, like a cork from a tiny jar."""
    rng = np.random.default_rng(111)
    t = t_of(0.12)
    f = np.interp(t, [0, 0.035, 0.12], [260, 900, 860])
    x = (sweep(f) + 0.2 * sweep(2 * f)) * env(len(t), 0.002, 0.05) * decay(len(t), 0.04)
    click = norm(bandpass(rng.standard_normal(len(t)), 1000, 6000)) * np.exp(-t / 0.002) * 0.3
    return x + click * env(len(t), 0.0005, 0.02)


def ding():
    """A step done: the counter bell of the restaurant, ding! Bright and
    clear, with a little shimmer as it rings."""
    rng = np.random.default_rng(112)
    t = t_of(1.0)
    f = NOTE["E6"]
    x = ((np.sin(2 * np.pi * f * t) + 0.6 * np.sin(2 * np.pi * f * 1.004 * t)) * np.exp(-t / 0.4)
         + 0.45 * np.sin(2 * np.pi * f * 2.41 * t) * np.exp(-t / 0.16)
         + 0.2 * np.sin(2 * np.pi * f * 4.13 * t) * np.exp(-t / 0.06)
         + 0.1 * np.sin(2 * np.pi * f * 6.2 * t) * np.exp(-t / 0.025))
    strike = norm(bandpass(rng.standard_normal(len(t)), 3000, 9000)) * np.exp(-t / 0.0015) * 0.3
    return (x + strike) * env(len(t), 0.0008, 0.1)


def done():
    """A whole dish done: ta-da-da-DAA! Marimba and glockenspiel run up, the
    ukulele strums, a little bass, then sparkles. About 1.5 s."""
    run = [("C5", 0.0), ("E5", 0.1), ("G5", 0.2), ("C6", 0.32)]
    parts = []
    for i, (n, at) in enumerate(run):
        last = i == len(run) - 1
        parts += [(at, 0.6 * marimba(NOTE[n], 1.1 if last else 0.35)),
                  (at, 0.25 * bell(NOTE[n] * 2, 0.9 if last else 0.3, bright=0.6))]
    parts += strum("C", 0.32, 0.4, 1.1, sr=SR) + [(0.32, 0.5 * pluck_bass(NOTE["C3"], 1.0, SR))]
    parts += [(0.5 + 0.07 * k, (0.2 - 0.025 * k) * bell(NOTE[n], 0.5, bright=0.5)) for k, n in enumerate(["G6", "C7", "E7", "G7"])]
    return place(1.5, parts)


def celebrate():
    """A customer served: a happy little tune on marimba and glockenspiel,
    the ukulele strumming D then G, a tambourine and a soft drum, a marimba
    roll on the last chord and sparkles. About 2.5 s."""
    rng = np.random.default_rng(113)
    q = 0.13
    tune = [("D5", 0, 1), ("E5", 1, 1), ("F#5", 2, 1), ("A5", 3, 3), ("B5", 6, 1), ("A5", 7, 1), ("B5", 8, 1), ("D6", 9, 8)]
    parts = []
    for n, k, length in tune:
        parts += [(k * q, 0.6 * marimba(NOTE[n], max(0.35, length * q * 1.5))),
                  (k * q, 0.22 * bell(NOTE[n] * 2, 0.4 if length < 8 else 1.0, bright=0.6))]
    parts += strum("D", 0, 0.3, 0.5, sr=SR) + strum("D", 3 * q, 0.3, 0.7, sr=SR) + strum("G", 6 * q, 0.25, 0.5, sr=SR)
    parts += strum("G", 9 * q, 0.4, 1.3, sr=SR)
    parts += [(0, 0.45 * pluck_bass(NOTE["D3"], 0.7, SR)), (9 * q, 0.55 * pluck_bass(NOTE["G2"], 1.2, SR))]
    k_ = kick(SR, 0.2)
    parts += [(0, 0.5 * k_), (3 * q, 0.4 * k_), (9 * q, 0.6 * k_)]
    parts += [(k * q, 0.2 * jingle(rng)) for k in (3, 6, 9)] + [(k * q, 0.12 * jingle(rng)) for k in (4.5, 7.5)]
    for j in range(10):  # the marimba roll on G
        parts.append((9 * q + 0.07 + j * 0.07, (0.22 - 0.018 * j) * marimba(NOTE[["G4", "B4", "D5"][j % 3]], 0.3)))
    sparkle = ["G6", "A6", "B6", "D7", "E7", "G7"]
    parts += [(9 * q + 0.04 * k, (0.25 - 0.02 * k) * bell(NOTE[n], 0.45, bright=0.6)) for k, n in enumerate(sparkle)]
    for k in range(8):
        at = 1.6 + k * 0.1 + rng.uniform(-0.02, 0.02)
        parts.append((at, (0.18 - 0.018 * k) * bell(NOTE[sparkle[rng.integers(2, 6)]], 0.4, bright=0.5)))
    return place(2.5, parts)


def coin():
    """A coin: clink-clink into the till, and a little chime."""
    return place(0.62, [(0, 0.7 * metal(2700, 0.3)), (0.075, 0.85 * metal(3150, 0.45)),
                        (0.075, 0.35 * bell(NOTE["B6"], 0.5, bright=0.3))])


def star():
    """A star: a twinkle running up the glockenspiel, then a shimmer."""
    run = ["E6", "G#6", "B6", "E7"]
    parts = [(i * 0.055, (0.5 + 0.1 * i) * bell(NOTE[n], 0.5, bright=0.6)) for i, n in enumerate(run)]
    parts += [(0.26 + k * 0.06, 0.32 * 0.8 ** k * bell(NOTE["B6" if k % 2 else "E7"], 0.3, bright=0.3)) for k in range(8)]
    return place(0.95, parts)


def oops():
    """Not quite: a soft, round "uh-oh" on an ocarina, the second note
    sliding gently down. Friendly, not a buzzer."""
    def note(f0, f1, dur):
        t = t_of(dur)
        f = np.interp(t, [0, dur * 0.5, dur], [f0, f0, f1])
        ph = 2 * np.pi * np.cumsum(f) / SR
        return (np.sin(ph) + 0.15 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)) * env(len(t), 0.02, dur * 0.45)
    return lowpass(place(0.6, [(0, note(NOTE["A4"], NOTE["A4"], 0.17)), (0.2, note(NOTE["F4"], NOTE["D4"], 0.38))]), 1800)


def wash():
    """Washing: scrub-scrub-scrub, with soapy little bubbles. About 1 s."""
    rng = np.random.default_rng(114)
    dur = 1.0
    t = t_of(dur)
    n = len(t)
    scrub = noise_through(rng, 1800 + 700 * np.sin(2 * np.pi * 3.5 * t), 900, n)
    strokes = np.abs(np.sin(2 * np.pi * 3.5 * t)) ** 0.7
    wet = 0.25 * norm(lowpass(rng.standard_normal(n), 900))
    shape = ease(t / 0.05) * (1 - ease((t - 0.75) / 0.25))
    x = (0.55 * scrub + wet) * strokes * shape
    bubbles = [(rng.uniform(0.02, 0.9), rng.uniform(0.2, 0.45) * bubble(rng, SR, (500, 1100), (1.6, 2.4), (0.02, 0.05)))
               for _ in range(14)]
    return x + place(dur, bubbles)


def water():
    """The tap running: a bright hiss full of tiny bubbles. About 1.2 s."""
    rng = np.random.default_rng(115)
    dur = 1.2
    t = t_of(dur)
    n = len(t)
    hiss = 0.35 * norm(bandpass(rng.standard_normal(n), 600, 4500))
    gurgle = 0.25 * norm(lowpass(rng.standard_normal(n), 350)) * (1 + 0.3 * norm(lowpass(rng.standard_normal(n), 6)))
    drops = np.zeros(n)
    for _ in range(320):
        f0, tau = rng.uniform(500, 2600), rng.uniform(0.003, 0.010)
        m = int(5 * tau * SR)
        tt = np.arange(m) / SR
        b = sweep(f0 * (1 + 0.4 * tt / (5 * tau))) * np.exp(-tt / tau) * rng.uniform(0.1, 0.5)
        i = rng.integers(0, n - m)
        drops[i:i + m] += b
    shape = ease(t / 0.06) * (1 - ease((t - 0.9) / 0.3))
    return (hiss + gurgle + drops) * shape


def chop():
    """One chop: the knife through something crisp, then a wooden tok on the board."""
    rng = np.random.default_rng(116)
    m = int(0.03 * SR)
    crunch = norm(bandpass(rng.standard_normal(m), 2000, 8000)) * np.hanning(m) * 0.35
    t = t_of(0.2)
    board = (sweep(np.geomspace(260, 170, len(t))) * np.exp(-t / 0.028)
             + 0.5 * partial(740, t, SR) * np.exp(-t / 0.012) + 0.25 * partial(1630, t, SR) * np.exp(-t / 0.006))
    knock = norm(bandpass(rng.standard_normal(len(t)), 600, 3500)) * np.exp(-t / 0.006) * 0.5
    return place(0.25, [(0, crunch), (0.025, (board + knock) * env(len(t), 0.0008, 0.03))])


def crack():
    """An egg: a tok on the bowl's rim, then the shell cracks, krrk."""
    rng = np.random.default_rng(117)
    t = t_of(0.12)
    tok = (partial(1450, t, SR) * np.exp(-t / 0.02) + 0.5 * partial(3350, t, SR) * np.exp(-t / 0.008)
           + 0.6 * sweep(np.geomspace(320, 260, len(t))) * np.exp(-t / 0.015)) * env(len(t), 0.0008, 0.03)
    n = int(0.11 * SR)
    krk = np.zeros(n)
    for i in sorted((rng.beta(1.2, 2.5, 14) * (n - 120)).astype(int)):
        c = norm(bandpass(rng.standard_normal(120), 1500, 8000)) * np.exp(-np.arange(120) / 12)
        krk[i:i + 120] += c * rng.uniform(0.4, 1.0)
    krk += norm(bandpass(rng.standard_normal(n), 500, 2500)) * np.exp(-np.arange(n) / (0.015 * SR)) * 0.3
    return place(0.32, [(0, 0.8 * tok), (0.1, krk * env(n, 0.0005, 0.02))])


def stir():
    """Stirring: a spoon swishing round a bowl, with a tiny tink on its side."""
    rng = np.random.default_rng(118)
    dur = 0.75
    t = t_of(dur)
    n = len(t)
    swish = noise_through(rng, 1000 + 450 * np.sin(2 * np.pi * 1.5 * t - np.pi / 2), 300, n)
    slosh = 0.4 * norm(lowpass(rng.standard_normal(n), 500)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))
    scrape = np.clip(1 + 0.6 * norm(lowpass(rng.standard_normal(n), 70)), 0.2, None)
    x = (swish * scrape + slosh) * np.sin(np.pi * t / dur) ** 1.5
    tink = metal(2600, 0.15, ratios=(1, 2.7, 5.1), amps=(1, 0.4, 0.15), taus=(0.4, 0.2, 0.1))
    return place(dur, [(0, x), (0.33, 0.25 * tink)])


def pour():
    """Pouring: a stream into a cup, its note rising as the cup fills. About 1.2 s."""
    rng = np.random.default_rng(119)
    dur = 1.2
    t = t_of(dur)
    n = len(t)
    centre = 380 * (1 + 2.2 * (t / dur) ** 1.3)
    stream = noise_through(rng, centre, 220, n) + 0.35 * noise_through(rng, centre * 2.1, 400, n)
    hiss = 0.12 * norm(bandpass(rng.standard_normal(n), 1500, 6000))
    flutter = 1 + 0.25 * norm(lowpass(rng.standard_normal(n), 18))
    shape = ease(t / 0.05) * (1 - ease((t - 0.95) / 0.25))
    glugs = [(rng.uniform(0.05, 0.9), rng.uniform(0.15, 0.3) * bubble(rng, SR, (250, 500), (1.8, 2.4), (0.04, 0.07)))
             for _ in range(6)]
    return (stream * flutter + hiss) * shape + place(dur, glugs)


def sizzle():
    """Frying: a pan sizzling and crackling. 1.5 s, and it loops: everything
    in it wraps round, and it starts and ends where the sound crosses zero."""
    rng = np.random.default_rng(120)
    n = int(1.5 * SR)
    hiss = norm(bandpass(rng.standard_normal(n), 2500, 8000))  # the FFT filter goes round: it joins up
    swell = 1 + 0.3 * norm(lowpass(rng.standard_normal(n), 6))
    crackles = []
    for i in rng.integers(0, n, 280):
        m = int(rng.uniform(0.0008, 0.003) * SR)
        crackles.append((i, rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 4)) * min(1.0, 0.15 + 0.25 * rng.pareto(2.5))))
    crackle = norm(bandpass(wrap_place(n, crackles), 1500, 9000))
    pops = []
    for i in rng.integers(0, n, 8):
        m = int(0.006 * SR)
        pops.append((i, rng.standard_normal(m) * np.exp(-np.arange(m) / (m / 5)) * rng.uniform(0.5, 1.0)))
    pop_ = norm(bandpass(wrap_place(n, pops), 800, 4000))
    x = lowpass(0.4 * hiss * swell + 0.7 * crackle + 0.5 * pop_, 8000)
    # start the loop where it crosses zero most gently, so it starts and ends near 0
    nxt = np.roll(x, -1)
    cross = np.nonzero(np.sign(x) != np.sign(nxt))[0]
    k = cross[np.argmin(np.abs(x[cross]) + np.abs(nxt[cross]))]
    return np.roll(x, -(k + 1))


def flip():
    """Flipping: a whoosh up into the air, then a soft plop back in the pan."""
    rng = np.random.default_rng(121)
    dur = 0.3
    t = t_of(dur)
    whoosh = noise_through(rng, np.interp(t, [0, 0.15, dur], [500, 1900, 800]), 500, len(t)) * np.sin(np.pi * t / dur) ** 2
    t2 = t_of(0.16)
    thump = sweep(np.geomspace(150, 85, len(t2))) * np.exp(-t2 / 0.035)
    fwap = 0.7 * norm(bandpass(rng.standard_normal(len(t2)), 300, 2000)) * np.exp(-t2 / 0.018)
    t3 = t_of(0.3)
    tail = 0.08 * norm(bandpass(rng.standard_normal(len(t3)), 3000, 8000)) * np.exp(-t3 / 0.1) * env(len(t3), 0.01, 0.05)
    return place(0.7, [(0, 1.5 * whoosh), (0.33, (thump + fwap) * env(len(t2), 0.001, 0.04)), (0.35, tail)])


def plop():
    """Into the water: plop! and a couple of little drops."""
    rng = np.random.default_rng(122)
    t = t_of(0.14)
    blip = sweep(320 * (1 + 2.6 * (1 - np.exp(-t / 0.03)))) * np.exp(-t / 0.04) * env(len(t), 0.001, 0.03)
    splash = 0.25 * norm(bandpass(rng.standard_normal(len(t)), 1200, 7000)) * np.exp(-t / 0.012) * env(len(t), 0.0005, 0.02)

    def drop(f):
        td = t_of(0.05)
        return sweep(np.geomspace(f, 2 * f, len(td))) * np.sin(np.pi * td / 0.05)
    return place(0.42, [(0, splash), (0.005, blip), (0.2, 0.3 * drop(900)), (0.31, 0.2 * drop(1050))])


def boil():
    """A pot on the boil: big round blubs, small bubbles, a low simmer. About 1.5 s."""
    rng = np.random.default_rng(123)
    dur = 1.5
    t = t_of(dur)
    n = len(t)
    simmer = 0.18 * norm(lowpass(rng.standard_normal(n), 700)) * (1 + 0.3 * norm(lowpass(rng.standard_normal(n), 8)))
    blubs = [(rng.uniform(0.02, 1.35), rng.uniform(0.5, 1.0) * bubble(rng, SR, (200, 340), (1.8, 2.6), (0.05, 0.1)))
             for _ in range(16)]
    small = [(rng.uniform(0.02, 1.4), rng.uniform(0.15, 0.4) * bubble(rng, SR, (500, 1000), (1.8, 2.6), (0.02, 0.04)))
             for _ in range(30)]
    shape = ease(t / 0.08) * (1 - ease((t - 1.2) / 0.3))
    return (simmer + place(dur, blubs + small)) * shape


def shake():
    """Shaking a drink: ice rattling in a cup shaker, shk-shk-shk-shk-shk. About 1 s."""
    rng = np.random.default_rng(124)
    parts = []
    for k in range(5):
        at, amp = k * 0.19, (1.0 if k < 4 else 0.8)
        m = int(0.13 * SR)
        tt = np.arange(m) / SR
        parts.append((at, 0.35 * amp * norm(bandpass(rng.standard_normal(m), 1800, 7000)) * np.sin(np.pi * tt / 0.13) ** 2))
        for _ in range(10):  # the ice hits the end of the cup
            clink = metal(rng.uniform(2200, 5200), rng.uniform(0.03, 0.07), ratios=(1, 2.3, 3.7), amps=(1, .4, .2), taus=(.4, .25, .15))
            parts.append((at + 0.07 + rng.uniform(0, 0.06), rng.uniform(0.15, 0.4) * amp * clink))
        tb = t_of(0.05)
        parts.append((at + 0.09, 0.25 * amp * np.sin(2 * np.pi * 200 * tb) * np.exp(-tb / 0.012) * env(len(tb), 0.001, 0.01)))
    return place(1.05, parts)


def squeeze():
    """A sauce bottle: a little puff of air, the sauce drizzling out in soft
    gloops, then plip, plip."""
    rng = np.random.default_rng(125)
    dur = 0.55
    t = t_of(dur)
    n = len(t)
    goo = noise_through(rng, np.interp(t, [0, dur], [650, 480]), 160, n)
    gate = np.clip(0.5 + norm(lowpass(rng.standard_normal(n), 28)), 0, None) ** 1.5
    flow = goo * gate * np.sin(np.pi * t / dur) ** 0.8
    ta = t_of(0.06)
    puff = 0.3 * norm(bandpass(rng.standard_normal(len(ta)), 1000, 4000)) * np.exp(-ta / 0.02) * env(len(ta), 0.002, 0.02)
    plips = [(0.6 + 0.12 * k, (0.5 - 0.15 * k) * bubble(rng, SR, (260, 380), (1.6, 2.0), (0.05, 0.06))) for k in range(2)]
    return place(0.8, [(0, puff), (0.02, 0.8 * flow)] + plips)


def pinch():
    """Pinching dough: a tiny soft squish, and the dough's tiny squeak."""
    rng = np.random.default_rng(126)
    dur = 0.16
    t = t_of(dur)
    squish = noise_through(rng, np.interp(t, [0, dur], [1300, 550]), 350, len(t)) * np.sin(np.pi * t / dur) ** 2
    t2 = t_of(0.07)
    squeak = sweep(np.interp(t2, [0, 0.03, 0.07], [1250, 1500, 1350])) * np.sin(np.pi * t2 / 0.07) ** 2
    return place(0.2, [(0, 0.8 * squish), (0.04, 0.2 * squeak)])


def slurp():
    """Drinking through a straw: slrrrp, a little bubbly, rising at the end."""
    rng = np.random.default_rng(127)
    dur = 0.7
    t = t_of(dur)
    n = len(t)
    suck = noise_through(rng, np.interp(t, [0, 0.5, dur], [700, 950, 1500]), 250, n)
    rate = 22 + 4 * norm(lowpass(rng.standard_normal(n), 3))
    gate = 0.3 + 0.7 * (0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate) / SR)) ** 2  # little bubbles in the straw
    air = 0.15 * norm(bandpass(rng.standard_normal(n), 2000, 6000))
    shape = ease(t / 0.05) * (1 - ease((t - 0.55) / 0.15))
    return (suck * gate + air) * shape


def yum():
    """Yum! Two chewy bloops, nom-nom, then a happy jingle up to a sparkle."""
    def nom(f):
        t = t_of(0.12)
        fr = f * (1 + 0.25 * np.sin(np.pi * t / 0.12))
        return (sweep(fr) + 0.3 * sweep(2 * fr)) * np.sin(np.pi * t / 0.12) ** 1.5
    parts = [(0, 0.5 * nom(330)), (0.15, 0.5 * nom(392))]
    for k, n in enumerate(["E5", "G5", "C6"]):
        parts += [(0.32 + 0.08 * k, 0.6 * marimba(NOTE[n], 0.9 if k == 2 else 0.35)),
                  (0.32 + 0.08 * k, 0.2 * bell(NOTE[n] * 2, 0.6 if k == 2 else 0.3, bright=0.5))]
    parts += [(0.56, 0.2 * bell(NOTE["E7"], 0.5, bright=0.4)), (0.64, 0.15 * bell(NOTE["G7"], 0.45, bright=0.4))]
    return place(1.15, parts)


def open_page():
    """Opening the recipe book or a card: a soft papery swish, a little flap,
    and a gentle pling."""
    rng = np.random.default_rng(128)
    dur = 0.32
    t = t_of(dur)
    n = len(t)
    paper = norm(bandpass(rng.standard_normal(n), 1200, 7000)) * (1 + 0.5 * norm(lowpass(rng.standard_normal(n), 45)))
    paper *= np.interp(t, [0, 0.12, dur], [0, 1, 0]) ** 1.5
    t2 = t_of(0.08)
    flap = 0.35 * norm(lowpass(rng.standard_normal(len(t2)), 600)) * np.exp(-t2 / 0.02) * env(len(t2), 0.001, 0.02)
    return place(0.85, [(0, 0.6 * paper), (0.27, flap), (0.25, 0.3 * uke(NOTE["G5"], 0.6, SR)),
                        (0.31, 0.22 * uke(NOTE["D6"], 0.55, SR))])


# ---------------------------------------------------------------- the customers' voices


def voice_bear():
    """The bear: a deep, warm chuckle, ho-ho, and a happy mm-HM!"""
    rng = np.random.default_rng(131)

    def ho(f, dur):
        t = t_of(dur)
        x = voice(np.linspace(f, f * 0.88, len(t)), [(480, 110, 1.0), (850, 140, 0.55), (2400, 250, 0.08)], rng, breath=0.15)
        return x * np.sin(np.pi * t / dur) ** 0.7

    def mm(dur):
        t = t_of(dur)
        f0 = glide(t, (0, 150), (0.12, 165), (0.25, 215), (dur, 200))
        return voice(f0, [(260, 60, 1.0), (1100, 150, 0.3), (2300, 250, 0.1)], rng) * env(len(t), 0.03, 0.12)
    return place(0.8, [(0, ho(190, 0.11)), (0.15, ho(180, 0.12)), (0.33, mm(0.42))])


def voice_rabbit():
    """The rabbit: a quick, high giggle, hee-hee-hee-hee-hii!"""
    rng = np.random.default_rng(132)
    parts = []
    for k, f in enumerate([700, 740, 690, 720, 760]):
        last = k == 4
        dur = 0.14 if last else 0.06
        t = t_of(dur)
        f0 = np.interp(t, [0, dur], [f * 0.95, f * 1.12] if last else [f * 1.05, f * 0.92])
        x = voice(f0, [(400, 120, 1.0), (2500, 250, 0.6), (3300, 300, 0.2)], rng, breath=0.1)
        x *= np.sin(np.pi * t / dur) ** 0.8
        m = int(0.015 * SR)
        h = 0.15 * norm(bandpass(rng.standard_normal(m), 1500, 5000)) * np.hanning(m)
        at = 0.01 + k * 0.095
        parts += [(at, h), (at + 0.012, x)]
    return place(0.62, parts)


def voice_cat():
    """The cat: a rolled, purring "mrrrm" and then a bright little "mi!"."""
    rng = np.random.default_rng(133)
    t = t_of(0.28)
    f0 = glide(t, (0, 400), (0.28, 470))
    hum = voice(f0, [(300, 80, 1.0), (1500, 200, 0.15), (2600, 300, 0.05)], rng, breath=0.04)
    hum *= (1 - 0.45 * (0.5 + 0.5 * np.sin(2 * np.pi * 24 * t))) * env(len(t), 0.03, 0.05)
    d = 0.2
    t2 = t_of(d)
    f1 = glide(t2, (0, 560), (0.1, 700), (d, 650))
    mi = voice(f1, [(np.interp(t2, [0, 0.04, d], [280, 380, 380]), 110, 1.0), (2400, 220, 0.6), (3200, 300, 0.15)], rng, breath=0.04)
    return place(0.56, [(0, hum), (0.3, mi * env(len(t2), 0.015, 0.08))])


def voice_pig():
    """The pig: a snorty little giggle, hn-hn-hn, and a happy "mm!"."""
    rng = np.random.default_rng(134)
    parts = []
    for k, f in enumerate([280, 265, 250]):
        dur = 0.085
        t = t_of(dur)
        x = voice(np.linspace(f, f * 0.9, len(t)), [(330, 120, 1.0), (1050, 180, 0.5), (2300, 250, 0.1)], rng, breath=0.2, rough=0.05)
        x *= np.sin(np.pi * t / dur) ** 0.7
        m = int(0.05 * SR)
        tt = np.arange(m) / SR
        snort = norm(bandpass(rng.standard_normal(m), 300, 1500)) * (0.5 + 0.5 * np.sin(2 * np.pi * 40 * tt)) * np.hanning(m)
        parts += [(k * 0.12, 0.4 * snort), (k * 0.12 + 0.02, x)]
    d = 0.26
    t = t_of(d)
    mm = voice(glide(t, (0, 240), (d, 320)), [(270, 70, 1.0), (1000, 150, 0.15)], rng) * env(len(t), 0.03, 0.1)
    return place(0.72, parts + [(0.42, mm)])


def voice_duck():
    """The duck: a buzzy, happy little laugh, wak-wak-wak-wak, a bit higher each time."""
    rng = np.random.default_rng(135)
    parts = []
    for k, f in enumerate([420, 440, 460, 500]):
        dur = 0.085 if k < 3 else 0.12
        t = t_of(dur)
        f0 = np.interp(t, [0, dur], [f, f * 0.93])
        f1 = np.interp(t, [0, 0.025, dur], [300, 700, 650])
        f2 = np.interp(t, [0, 0.025, dur], [900, 1400, 1350])
        x = voice(f0, [(f1, 120, 1.0), (f2, 150, 0.8), (2600, 220, 0.3)], rng, breath=0.05, rough=0.02)
        parts.append((k * 0.13, x * env(len(t), 0.008, 0.015)))
    return place(0.6, parts)


SHORT = {
    "tap": (tap, 0.50), "pop": (pop, 0.50), "ding": (ding, 0.55), "done": (done, 0.65),
    "celebrate": (celebrate, 0.70), "coin": (coin, 0.55), "star": (star, 0.50), "oops": (oops, 0.28),
    "wash": (wash, 0.50), "water": (water, 0.45), "chop": (chop, 0.72), "crack": (crack, 0.62),
    "stir": (stir, 0.50), "pour": (pour, 0.48), "sizzle": (sizzle, 0.48), "flip": (flip, 0.60),
    "plop": (plop, 0.55), "boil": (boil, 0.60), "shake": (shake, 0.55), "squeeze": (squeeze, 0.65),
    "pinch": (pinch, 0.50), "slurp": (slurp, 0.55), "yum": (yum, 0.55), "open": (open_page, 0.50),
    "voice_bear": (voice_bear, 0.72), "voice_rabbit": (voice_rabbit, 0.52), "voice_cat": (voice_cat, 0.54),
    "voice_pig": (voice_pig, 0.70), "voice_duck": (voice_duck, 0.52),
}
LOOPED = {"sizzle"}  # short sounds the app may loop: no fades, the ends join up


# ---------------------------------------------------------------- writing and checking


def tidy(x, sr=SR):
    """A short sound: drop the silent end, then fade both ends so neither clicks."""
    x = np.asarray(x, dtype=np.float64)
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 1e-3)[0]
    x = x[: min(len(x), loud[-1] + int(0.01 * sr))]
    return x * env(len(x), 0.002, 0.012, sr)


def write(path, x, peak, sr):
    x = np.asarray(x, dtype=np.float64)
    x = x / max(1e-9, np.abs(x).max()) * peak
    data = np.round(x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(data.tobytes())
    return data


def report(name, data, sr, loop):
    x = data.astype(np.float64) / 32767
    peak = np.abs(x).max()
    rms = 20 * np.log10(max(1e-9, np.sqrt(np.mean(x ** 2))))
    clipped = int(np.sum(np.abs(data) >= 32767))
    steps = np.abs(np.diff(data.astype(np.int32)))
    if loop:  # the jump from the last sample back to the first, beside the usual step
        jump = abs(int(data[0]) - int(data[-1]))
        edge = f"seam jump {jump:4d} (usual step {np.median(steps):.0f}, 99% {np.percentile(steps, 99):.0f})"
    else:
        edge = f"ends {int(data[0]):+d} / {int(data[-1]):+d}"
    print(f"  {name:18s} {len(x) / sr:5.2f} s  {(len(data) * 2 + 44) / 1024:6.1f} KB  peak {peak:.2f}  "
          f"rms {rms:6.1f} dB  clipped {clipped}  {edge}")


def read(path):
    with wave.open(str(path), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32767, w.getframerate()


def preview(path, loop_seconds=8.0, gap=0.5):
    """A listening preview: [loop_seconds] of each tune, then every short
    sound in order, [gap] apart. Prints where each one starts."""
    path = pathlib.Path(path)
    sr, pieces, at = 22050, [], 0.0
    print(f"preview {path}:")
    for name in list(MUSIC) + list(SHORT):
        x, rate = read(OUT / f"{name}.wav")
        if rate != sr:
            x = resample_poly(x, sr, rate)
        if name in MUSIC:
            x = x[: int(loop_seconds * sr)] * env(int(loop_seconds * sr), 0.01, 0.5, sr)
        print(f"  {int(at // 60)}:{at % 60:04.1f}  {name}")
        pieces += [x, np.zeros(int((1.0 if name in MUSIC else gap) * sr))]
        at += (len(x) + len(pieces[-1])) / sr
    wav = path.with_suffix(".wav")
    write(wav, np.concatenate(pieces), np.abs(np.concatenate(pieces)).max(), sr)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "aac", "-b:a", "96k", str(path)], check=True)
    wav.unlink()
    print(f"  total {at:.1f} s")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("music (16,000 Hz, loops):")
    for name, (make, peak) in MUSIC.items():
        report(name, write(OUT / f"{name}.wav", make(), peak, LOOP_SR), LOOP_SR, True)
    print("short sounds and voices (22,050 Hz):")
    for name, (make, peak) in SHORT.items():
        x = make() if name in LOOPED else tidy(make())
        report(name + (" (loop)" if name in LOOPED else ""), write(OUT / f"{name}.wav", x, peak, SR), SR, name in LOOPED)
    total = sum(p.stat().st_size for p in OUT.glob("*.wav"))
    print(f"{len(MUSIC) + len(SHORT)} sounds, {total:,} bytes ({total / 1024 / 1024:.2f} MiB) in {OUT}")
    assert total < 4_000_000, "the sounds must stay under 4,000,000 bytes"
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])


if __name__ == "__main__":
    main()
