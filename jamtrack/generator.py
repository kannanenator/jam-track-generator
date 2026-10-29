"""Turn a chord progression into a multi-instrument MIDI file."""

import random

import mido

from .chords import parse_progression
from .instruments import INSTRUMENTS

TICKS_PER_BEAT = 480


def _instrument_track(instrument, progression, beats_per_chord, beats_per_bar,
                      repeats, humanize, rng):
    events = []  # (tick, order, message); note-offs sort before note-ons
    beat = 0
    for _ in range(repeats):
        for chord in progression:
            notes = instrument.pattern(
                chord, beats_per_chord, beats_per_bar, beat % beats_per_bar)
            for note in notes:
                start = round((beat + note.start) * TICKS_PER_BEAT)
                end = start + max(1, round(note.duration * TICKS_PER_BEAT))
                velocity = note.velocity
                if humanize:
                    velocity += rng.randint(-6, 6)
                velocity = max(1, min(127, velocity))
                events.append((start, 1, mido.Message(
                    "note_on", channel=instrument.channel,
                    note=note.pitch, velocity=velocity)))
                events.append((end, 0, mido.Message(
                    "note_off", channel=instrument.channel,
                    note=note.pitch, velocity=0)))
            beat += beats_per_chord

    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name=instrument.name, time=0))
    track.append(mido.Message("program_change", channel=instrument.channel,
                              program=instrument.program, time=0))
    track.append(mido.Message("control_change", channel=instrument.channel,
                              control=7, value=instrument.volume, time=0))
    last = 0
    for tick, _, message in sorted(events, key=lambda e: (e[0], e[1])):
        track.append(message.copy(time=tick - last))
        last = tick
    return track


def generate(progression, path, instruments=("piano", "guitar", "strings", "bass"),
             bpm=100, beats_per_bar=4, beats_per_chord=None, repeats=4,
             humanize=True, seed=None):
    """Write a backing track for ``progression`` to ``path``.

    ``progression`` is a chord string like ``"C G Am F"`` (each chord lasts one
    bar unless ``beats_per_chord`` says otherwise) or a list of ``Chord``s.
    """
    if isinstance(progression, str):
        progression = parse_progression(progression)
    unknown = [name for name in instruments if name not in INSTRUMENTS]
    if unknown:
        raise ValueError(f"Unknown instrument(s): {', '.join(unknown)}. "
                         f"Choose from: {', '.join(INSTRUMENTS)}")
    if not instruments:
        raise ValueError("Pick at least one instrument")
    beats_per_chord = beats_per_chord or beats_per_bar
    rng = random.Random(seed)

    midi = mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    conductor = mido.MidiTrack()
    conductor.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    conductor.append(mido.MetaMessage(
        "time_signature", numerator=beats_per_bar, denominator=4, time=0))
    midi.tracks.append(conductor)
    for name in instruments:
        midi.tracks.append(_instrument_track(
            INSTRUMENTS[name], progression, beats_per_chord, beats_per_bar,
            repeats, humanize, rng))
    midi.save(path)
    return midi
