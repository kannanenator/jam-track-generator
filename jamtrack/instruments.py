"""Backing instruments: a General MIDI program plus a playing pattern.

Each pattern turns one chord into a list of ``Note``s, with times measured in
beats from the start of the chord.
"""

from dataclasses import dataclass
from typing import Callable


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
    pattern: Callable  # (chord, beats, beats_per_bar, bar_offset) -> [Note]


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


def piano_pattern(chord, beats, beats_per_bar, bar_offset):
    """Left hand holds the bass note; right hand comps on the strong beats."""
    notes = [Note(0, beats, _lowest_at_or_above(chord.bass, 36), 70)]
    right_hand = voice_chord(chord, center=64)
    half_bar = max(1, beats_per_bar // 2)
    for beat in range(beats):
        if (bar_offset + beat) % half_bar == 0:
            length = min(half_bar, beats - beat) * 0.9
            accent = 82 if (bar_offset + beat) % beats_per_bar == 0 else 72
            notes += [Note(beat, length, p, accent) for p in right_hand]
    return notes


def guitar_pattern(chord, beats, beats_per_bar, bar_offset):
    """Strummed eighths: down on every beat, up on the "and" after beat one."""
    root = _lowest_at_or_above(chord.bass, 40)
    shape = [root] + [p for p in voice_chord(chord, center=60, size=5) if p > root]
    spread = 0.03  # beats between strings in a strum
    notes = []
    for beat in range(beats):
        position = (bar_offset + beat) % beats_per_bar
        strums = [(beat, "down")]
        if position != 0:
            strums.append((beat + 0.5, "up"))
        for start, direction in strums:
            strings = shape if direction == "down" else list(reversed(shape[1:]))
            velocity = 78 if direction == "down" else 60
            if position == 0 and direction == "down":
                velocity = 88
            for i, pitch in enumerate(strings):
                onset = start + i * spread
                notes.append(Note(onset, start + 0.5 - onset, pitch, velocity))
    return notes


def strings_pattern(chord, beats, beats_per_bar, bar_offset):
    """Sustained pad held for the whole chord, voiced above the piano."""
    pad = voice_chord(chord, center=70)
    bass = _lowest_at_or_above(chord.bass, 48)
    return [Note(0, beats, p, 60) for p in [bass] + pad]


def bass_pattern(chord, beats, beats_per_bar, bar_offset):
    """Root on the downbeat, fifth (or root) halfway through the bar."""
    root = _lowest_at_or_above(chord.bass, 28)
    fifth = root + 7 if 7 in chord.intervals else root + 12
    half_bar = max(1, beats_per_bar // 2)
    notes = []
    for beat in range(beats):
        position = (bar_offset + beat) % beats_per_bar
        if beat == 0 or position == 0:
            pitch = root
        elif position == half_bar:
            pitch = fifth
        else:
            continue
        notes.append(Note(beat, min(half_bar, beats - beat) * 0.9, pitch, 90))
    return notes


INSTRUMENTS = {
    instrument.name: instrument
    for instrument in [
        Instrument("piano", "Acoustic Grand Piano comping", 0, 0, 100, piano_pattern),
        Instrument("guitar", "Steel-string acoustic guitar strumming", 25, 1, 90, guitar_pattern),
        Instrument("strings", "String ensemble pad", 48, 2, 80, strings_pattern),
        Instrument("bass", "Fingered electric bass", 33, 3, 105, bass_pattern),
    ]
}
