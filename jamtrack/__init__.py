"""Generate simple MIDI backing tracks to jam over."""

from .chords import Chord, parse_chord, parse_progression
from .instruments import INSTRUMENTS, Instrument
from .generator import generate
from .meter import Meter, parse_time_signature

__all__ = [
    "Chord",
    "parse_chord",
    "parse_progression",
    "INSTRUMENTS",
    "Instrument",
    "generate",
    "Meter",
    "parse_time_signature",
]
