"""Backing instruments: a General MIDI program plus a playing pattern.

Each pattern turns one chord into a list of ``Note``s. Times are measured in
beats (the time signature's beat unit) from the start of the chord, and
``bar_offset`` is the bar position the chord starts on.
"""

from dataclasses import dataclass
from typing import Callable

DRUM_CHANNEL = 9  # General MIDI percussion channel (channel 10, 1-based)
KICK, SNARE, CLOSED_HAT = 36, 38, 42


@dataclass(frozen=True)
class Note:
    start: float  # beats from the start of the chord
    duration: float  # beats
    pitch: int
    velocity: int


@dataclass(frozen=True)
class Instrument:
    name: str
    description: str
    program: int  # General MIDI program number (0-based)
    channel: int
    volume: int  # CC7, 0-127
    pattern: Callable  # (chord, beats, meter, bar_offset) -> [Note]


def _lowest_at_or_above(pitch_class, floor):
    return floor + (pitch_class - floor) % 12


def voice_chord(chord, center, size=None):
    """Close-voice the chord's tones, choosing the inversion nearest ``center``.

    ``size`` repeats chord tones upward until that many notes are voiced.
    """
    pcs = chord.pitch_classes
    size = size or len(pcs)
    best = None
    for inversion in range(len(pcs)):
        order = pcs[inversion:] + pcs[:inversion]
        notes = [_lowest_at_or_above(order[0], center - 12)]
        for i in range(1, size):
            notes.append(_lowest_at_or_above(order[i % len(order)], notes[-1] + 1))
        # Shift by octaves so the voicing straddles the center.
        mean = sum(notes) / len(notes)
        shift = round((center - mean) / 12) * 12
        notes = [n + shift for n in notes]
        score = abs(sum(notes) / len(notes) - center)
        if best is None or score < best[0]:
            best = (score, notes)
    return best[1]


def _group_starts(beats, meter, bar_offset):
    """Yield (beat, group_index, group_length) for each pulse group in the chord."""
    for beat in range(beats):
        index, start, length = meter.group_at((bar_offset + beat) % meter.numerator)
        if beat == 0 or (bar_offset + beat) % meter.numerator == start:
            # A chord can start mid-group; only play what's left of it.
            remaining = start + length - (bar_offset + beat) % meter.numerator
            yield beat, index, min(remaining, beats - beat)


def piano_pattern(chord, beats, meter, bar_offset):
    """Left hand holds the bass note; right hand comps on each pulse."""
    notes = [Note(0, beats, _lowest_at_or_above(chord.bass, 36), 70)]
    right_hand = voice_chord(chord, center=64)
    for beat, index, length in _group_starts(beats, meter, bar_offset):
        accent = 82 if index == 0 else 72
        notes += [Note(beat, length * 0.9, p, accent) for p in right_hand]
    return notes


def guitar_pattern(chord, beats, meter, bar_offset):
    """Strum down on every beat; in simple meters, also up on the off-beat "and"s."""
    root = _lowest_at_or_above(chord.bass, 40)
    shape = [root] + [p for p in voice_chord(chord, center=60, size=5) if p > root]
    spread = 0.03 * meter.denominator / 4  # strum speed, in beats
    notes = []
    for beat in range(beats):
        position = (bar_offset + beat) % meter.numerator
        _, group_start, _ = meter.group_at(position)
        strums = [(beat, "down")]
        if not meter.compound and position != group_start:
            strums.append((beat + 0.5, "up"))
        for start, direction in strums:
            strings = shape if direction == "down" else list(reversed(shape[1:]))
            if direction == "up":
                velocity, length = 60, 0.5
            else:
                velocity = 88 if position == 0 else 78 if position == group_start else 70
                length = 1 if meter.compound or position == group_start else 0.5
            for i, pitch in enumerate(strings):
                onset = start + i * spread
                notes.append(Note(onset, start + length - onset, pitch, velocity))
    return notes


def strings_pattern(chord, beats, meter, bar_offset):
    """Sustained pad held for the whole chord, voiced above the piano."""
    pad = voice_chord(chord, center=70)
    bass = _lowest_at_or_above(chord.bass, 48)
    return [Note(0, beats, p, 60) for p in [bass] + pad]


def bass_pattern(chord, beats, meter, bar_offset):
    """Root on the downbeat and alternating fifth/root on the other pulses."""
    root = _lowest_at_or_above(chord.bass, 28)
    fifth = root + 7 if 7 in chord.intervals else root + 12
    notes = []
    for count, (beat, _, length) in enumerate(_group_starts(beats, meter, bar_offset)):
        pitch = root if count % 2 == 0 else fifth
        notes.append(Note(beat, length * 0.9, pitch, 90))
    return notes


def drums_pattern(chord, beats, meter, bar_offset):
    """Kick on each pulse with a snare backbeat, plus a steady hi-hat.

    Simple meters (4/4, 3/4): kick on each group's first beat, snare on the
    rest, hi-hat in eighths. Compound meters (6/8, 12/8): kick and snare
    alternate on the dotted-quarter pulses, hi-hat on every beat.
    """
    notes = []
    for beat in range(beats):
        position = (bar_offset + beat) % meter.numerator
        index, group_start, _ = meter.group_at(position)
        if position == group_start:
            if meter.compound and index % 2:
                notes.append(Note(beat, 0.25, SNARE, 95))
            else:
                notes.append(Note(beat, 0.25, KICK, 105 if position == 0 else 95))
        elif not meter.compound:
            notes.append(Note(beat, 0.25, SNARE, 95))
        hats = [beat] if meter.compound else [beat, beat + 0.5]
        for hat in hats:
            on_beat = hat == beat
            notes.append(Note(hat, 0.25, CLOSED_HAT, 75 if on_beat else 55))
    return notes


INSTRUMENTS = {
    instrument.name: instrument
    for instrument in [
        Instrument("piano", "Acoustic Grand Piano comping", 0, 0, 100, piano_pattern),
        Instrument("guitar", "Steel-string acoustic guitar strumming", 25, 1, 90, guitar_pattern),
        Instrument("strings", "String ensemble pad", 48, 2, 80, strings_pattern),
        Instrument("bass", "Fingered electric bass", 33, 3, 105, bass_pattern),
        Instrument("drums", "Standard drum kit: kick, snare, hi-hat", 0, DRUM_CHANNEL, 100,
                   drums_pattern),
    ]
}
