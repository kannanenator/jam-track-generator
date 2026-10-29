import os
import tempfile
import unittest

import mido

from jamtrack import INSTRUMENTS, generate, parse_chord, parse_progression
from jamtrack.instruments import voice_chord


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

    def test_unknown_instrument(self):
        with self.assertRaises(ValueError):
            generate("C", self.path, instruments=["kazoo"])


if __name__ == "__main__":
    unittest.main()
