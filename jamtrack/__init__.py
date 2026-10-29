"""Generate simple MIDI backing tracks to jam over."""

from .chords import Chord, parse_chord, parse_progression
from .instruments import INSTRUMENTS, Instrument
from .generator import generate

__all__ = [
    "Chord",
    "parse_chord",
    "parse_progression",
    "INSTRUMENTS",
    "Instrument",
    "generate",
]
