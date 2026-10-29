import os
import tempfile
import unittest

import mido

from jamtrack import (INSTRUMENTS, Meter, generate, parse_chord, parse_progression,
                      parse_time_signature)
from jamtrack.instruments import CLOSED_HAT, DRUM_CHANNEL, KICK, SNARE, voice_chord


class ChordTests(unittest.TestCase):
    def test_qualities(self):
        self.assertEqual(parse_chord("C").pitch_classes, [0, 4, 7])
        self.assertEqual(parse_chord("Am").pitch_classes, [9, 0, 4])
        self.assertEqual(parse_chord("G7").pitch_classes, [7, 11, 2, 5])
        self.assertEqual(parse_chord("Bbmaj7").pitch_classes, [10, 2, 5, 9])
        self.assertEqual(parse_chord("F#m7b5").pitch_classes, [6, 9, 0, 4])

    def test_slash_chord(self):
        chord = parse_chord("C/E")
        self.assertEqual(chord.root, 0)
        self.assertEqual(chord.bass, 4)

    def test_progression_with_bars(self):
        chords = parse_progression("Dm7 | G7 | Cmaj7")
        self.assertEqual([c.symbol for c in chords], ["Dm7", "G7", "Cmaj7"])

    def test_bad_symbols(self):
        for bad in ["H", "Cxyz", ""]:
            with self.assertRaises(ValueError):
                parse_progression(bad)


class VoicingTests(unittest.TestCase):
    def test_voicing_contains_chord_tones_near_center(self):
        chord = parse_chord("G7")
        notes = voice_chord(chord, center=64)
        self.assertEqual(sorted({n % 12 for n in notes}), sorted(chord.pitch_classes))
        self.assertLess(abs(sum(notes) / len(notes) - 64), 6)


class MeterTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parse_time_signature("6/8"), Meter(6, 8))
        for bad in ["4", "4/3", "0/4", "x/4", "4/4/4"]:
            with self.assertRaises(ValueError):
                parse_time_signature(bad)

    def test_groups(self):
        self.assertEqual(Meter(4, 4).groups, [(0, 2), (2, 2)])
        self.assertEqual(Meter(3, 4).groups, [(0, 3)])
        self.assertEqual(Meter(6, 8).groups, [(0, 3), (3, 3)])
        self.assertEqual(Meter(5, 4).groups, [(0, 2), (2, 3)])
        self.assertEqual(Meter(7, 8).groups, [(0, 2), (2, 2), (4, 3)])
        self.assertEqual(Meter(1, 4).groups, [(0, 1)])

    def test_compound(self):
        self.assertTrue(Meter(6, 8).compound)
        self.assertTrue(Meter(12, 8).compound)
        self.assertFalse(Meter(3, 8).compound)
        self.assertFalse(Meter(6, 4).compound)


def _drum_hits(path):
    """{pitch: [beat positions]} for the drum track's first bar, in quarter notes."""
    midi = mido.MidiFile(path)
    track = next(t for t in midi.tracks if t.name == "drums")
    tick, hits = 0, {}
    for msg in track:
        tick += msg.time
        if msg.type == "note_on":
            hits.setdefault(msg.note, []).append(tick / midi.ticks_per_beat)
    return hits


class GenerateTests(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".mid")
        os.close(fd)

    def tearDown(self):
        os.remove(self.path)

    def test_each_instrument_gets_a_track_with_its_program(self):
        generate("C G Am F", self.path, repeats=2, seed=1)
        midi = mido.MidiFile(self.path)
        self.assertEqual(len(midi.tracks), 1 + len(INSTRUMENTS))
        for track, instrument in zip(midi.tracks[1:], INSTRUMENTS.values()):
            programs = [m.program for m in track if m.type == "program_change"]
            self.assertEqual(programs, [instrument.program])
            notes = [m for m in track if m.type == "note_on"]
            self.assertTrue(notes)
            self.assertTrue(all(m.channel == instrument.channel for m in notes))

    def test_length_matches_progression(self):
        generate("C G", self.path, instruments=["strings"], bpm=120, repeats=3)
        midi = mido.MidiFile(self.path)
        # 2 chords x 4 beats x 3 repeats = 24 beats at 120 bpm = 12 seconds
        self.assertAlmostEqual(midi.length, 12, places=2)

    def test_notes_are_balanced(self):
        generate("Dm7 G7 Cmaj7 A7", self.path, seed=3)
        for track in mido.MidiFile(self.path).tracks[1:]:
            ons = sum(1 for m in track if m.type == "note_on")
            offs = sum(1 for m in track if m.type == "note_off")
            self.assertEqual(ons, offs)

    def test_time_signature_meta_and_length(self):
        generate("C G", self.path, instruments=["piano"], bpm=120,
                 time_signature="6/8", repeats=1)
        midi = mido.MidiFile(self.path)
        sig = next(m for m in midi.tracks[0] if m.type == "time_signature")
        self.assertEqual((sig.numerator, sig.denominator), (6, 8))
        # 2 bars of 6/8 = 6 quarter notes at 120 bpm = 3 seconds
        self.assertAlmostEqual(midi.length, 3, places=2)

    def test_tempo(self):
        generate("C", self.path, instruments=["bass"], bpm=90, repeats=1)
        tempo = next(m for m in mido.MidiFile(self.path).tracks[0] if m.type == "set_tempo")
        self.assertAlmostEqual(mido.tempo2bpm(tempo.tempo), 90, places=3)

    def test_drums_rock_beat_in_four_four(self):
        generate("C", self.path, instruments=["drums"], repeats=1, humanize=False)
        hits = _drum_hits(self.path)
        self.assertEqual(hits[KICK], [0, 2])
        self.assertEqual(hits[SNARE], [1, 3])
        self.assertEqual(hits[CLOSED_HAT], [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5])

    def test_drums_waltz_and_six_eight(self):
        generate("C", self.path, instruments=["drums"], time_signature="3/4",
                 repeats=1, humanize=False)
        hits = _drum_hits(self.path)
        self.assertEqual(hits[KICK], [0])
        self.assertEqual(hits[SNARE], [1, 2])

        generate("C", self.path, instruments=["drums"], time_signature="6/8",
                 repeats=1, humanize=False)
        hits = _drum_hits(self.path)
        self.assertEqual(hits[KICK], [0])
        self.assertEqual(hits[SNARE], [1.5])
        self.assertEqual(hits[CLOSED_HAT], [0, 0.5, 1, 1.5, 2, 2.5])

    def test_drums_use_percussion_channel(self):
        generate("C G", self.path, instruments=["drums"], repeats=1)
        track = mido.MidiFile(self.path).tracks[1]
        self.assertTrue(all(m.channel == DRUM_CHANNEL for m in track if m.type == "note_on"))

    def test_every_instrument_in_odd_meters(self):
        for sig in ["3/4", "5/4", "6/8", "7/8", "12/8", "2/2"]:
            generate("Am7 D7/F# G", self.path, time_signature=sig,
                     beats_per_chord=5, repeats=2, seed=0)
            for track in mido.MidiFile(self.path).tracks[1:]:
                ons = sum(1 for m in track if m.type == "note_on")
                offs = sum(1 for m in track if m.type == "note_off")
                self.assertGreater(ons, 0, (sig, track.name))
                self.assertEqual(ons, offs, (sig, track.name))

    def test_invalid_settings(self):
        for kwargs in [{"bpm": 0}, {"time_signature": "4/5"}, {"repeats": 0},
                       {"beats_per_chord": 0}]:
            with self.assertRaises(ValueError, msg=kwargs):
                generate("C", self.path, **kwargs)

    def test_unknown_instrument(self):
        with self.assertRaises(ValueError):
            generate("C", self.path, instruments=["kazoo"])


if __name__ == "__main__":
    unittest.main()
