"""Turn a chord progression into a multi-instrument MIDI file."""

import random

import mido

from .chords import parse_progression
from .instruments import INSTRUMENTS
from .meter import parse_time_signature

TICKS_PER_BEAT = 480


def _instrument_track(instrument, progression, beats_per_chord, meter,
                      repeats, humanize, rng):
    ticks_per_beat = TICKS_PER_BEAT * meter.quarters_per_beat
    events = []  # (tick, order, message); note-offs sort before note-ons
    beat = 0
    for _ in range(repeats):
        for chord in progression:
            notes = instrument.pattern(
                chord, beats_per_chord, meter, beat % meter.numerator)
            for note in notes:
                start = round((beat + note.start) * ticks_per_beat)
                end = start + max(1, round(note.duration * ticks_per_beat))
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


DEFAULT_INSTRUMENTS = ("piano", "guitar", "strings", "bass", "drums")


def generate(progression, path, instruments=DEFAULT_INSTRUMENTS, bpm=100,
             time_signature="4/4", beats_per_chord=None, repeats=4,
             humanize=True, seed=None):
    """Write a backing track for ``progression`` to ``path``.

    ``progression`` is a chord string like ``"C G Am F"`` (each chord lasts one
    bar unless ``beats_per_chord`` says otherwise) or a list of ``Chord``s.
    ``bpm`` is in quarter notes per minute, as in a DAW, whatever the time
    signature. ``time_signature`` is a string like ``"3/4"`` or ``"6/8"``.
    """
    if isinstance(progression, str):
        progression = parse_progression(progression)
    unknown = [name for name in instruments if name not in INSTRUMENTS]
    if unknown:
        raise ValueError(f"Unknown instrument(s): {', '.join(unknown)}. "
                         f"Choose from: {', '.join(INSTRUMENTS)}")
    if not instruments:
        raise ValueError("Pick at least one instrument")
    if not 20 <= bpm <= 400:
        raise ValueError(f"Tempo must be between 20 and 400 bpm, got {bpm}")
    meter = parse_time_signature(time_signature)
    if beats_per_chord is None:
        beats_per_chord = meter.numerator
    if beats_per_chord < 1:
        raise ValueError("Each chord must last at least one beat")
    if repeats < 1:
        raise ValueError("Repeats must be at least 1")
    rng = random.Random(seed)

    midi = mido.MidiFile(type=1, ticks_per_beat=TICKS_PER_BEAT)
    conductor = mido.MidiTrack()
    conductor.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm), time=0))
    conductor.append(mido.MetaMessage(
        "time_signature", numerator=meter.numerator, denominator=meter.denominator,
        time=0))
    midi.tracks.append(conductor)
    for name in instruments:
        midi.tracks.append(_instrument_track(
            INSTRUMENTS[name], progression, beats_per_chord, meter,
            repeats, humanize, rng))
    midi.save(path)
    return midi
