"""Chord symbol parsing."""

import re
from dataclasses import dataclass

NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Intervals above the root for each supported chord quality.
QUALITIES = {
    "": (0, 4, 7),
    "maj": (0, 4, 7),
    "m": (0, 3, 7),
    "min": (0, 3, 7),
    "-": (0, 3, 7),
    "dim": (0, 3, 6),
    "aug": (0, 4, 8),
    "+": (0, 4, 8),
    "sus2": (0, 2, 7),
    "sus4": (0, 5, 7),
    "sus": (0, 5, 7),
    "5": (0, 7),
    "6": (0, 4, 7, 9),
    "m6": (0, 3, 7, 9),
    "7": (0, 4, 7, 10),
    "maj7": (0, 4, 7, 11),
    "M7": (0, 4, 7, 11),
    "m7": (0, 3, 7, 10),
    "min7": (0, 3, 7, 10),
    "-7": (0, 3, 7, 10),
    "mmaj7": (0, 3, 7, 11),
    "m7b5": (0, 3, 6, 10),
    "dim7": (0, 3, 6, 9),
    "7sus4": (0, 5, 7, 10),
    "9": (0, 4, 7, 10, 14),
    "maj9": (0, 4, 7, 11, 14),
    "m9": (0, 3, 7, 10, 14),
    "add9": (0, 4, 7, 14),
}

_CHORD_RE = re.compile(r"^([A-G])([#b]?)(.*?)(?:/([A-G])([#b]?))?$")


def _pitch_class(letter, accidental):
    pc = NOTE_NAMES[letter]
    if accidental == "#":
        pc += 1
    elif accidental == "b":
        pc -= 1
    return pc % 12


@dataclass(frozen=True)
class Chord:
    symbol: str
    root: int  # pitch class 0-11
    intervals: tuple
    bass: int  # pitch class of the bass note (differs from root for slash chords)

    @property
    def pitch_classes(self):
        return [(self.root + i) % 12 for i in self.intervals]


def parse_chord(symbol):
    match = _CHORD_RE.match(symbol.strip())
    if not match:
        raise ValueError(f"Can't parse chord symbol: {symbol!r}")
    letter, acc, quality, bass_letter, bass_acc = match.groups()
    if quality not in QUALITIES:
        raise ValueError(f"Unknown chord quality {quality!r} in {symbol!r}")
    root = _pitch_class(letter, acc)
    bass = _pitch_class(bass_letter, bass_acc) if bass_letter else root
    return Chord(symbol, root, QUALITIES[quality], bass)


def parse_progression(text):
    """Parse a space/bar separated progression like "C G | Am F"."""
    tokens = text.replace("|", " ").split()
    if not tokens:
        raise ValueError("Progression is empty")
    return [parse_chord(t) for t in tokens]
