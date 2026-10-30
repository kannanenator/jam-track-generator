"""Check the web app's JavaScript engine plays the same notes as the Python one.

web/index.html carries its own copy of the chord parser, meters and instrument
patterns so it can run in a phone browser. This test runs that copy in Node
and compares its notes with jamtrack's. Skipped when Node isn't installed.
"""

import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

from jamtrack.chords import parse_progression
from jamtrack.instruments import INSTRUMENTS
from jamtrack.meter import parse_time_signature

WEB_APP = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"

CASES = [
    ("C G Am F", "4/4", None, 2),
    ("Dm7 G7/B Cmaj7 F#m7b5", "3/4", None, 2),
    ("Em C G D", "6/8", None, 2),
    ("Ebm7 Bbm7 Csus4 Gadd9", "5/4", 3, 3),
    ("A7 D9 E7", "7/8", None, 2),
    ("Dm Gm/D A7", "3+2+2/8", None, 2),
    ("Cmaj7 F#m7b5 B7", "11/8", None, 2),
    ("C Dm", "13/16", 5, 3),
    ("Am F", "5/32", None, 2),
    ("C G", "4/1", 2, 2),
    ("Bb/D Fm6 C", "12/8", None, 1),
]

RUNNER = """
const E = require(process.argv[2]);
const cases = JSON.parse(process.argv[3]);
const names = ["piano", "guitar", "strings", "bass", "drums"];
console.log(JSON.stringify(cases.map(([prog, sig, bpc, reps]) => {
  const m = E.parseTimeSignature(sig);
  const chords = E.tokenize(prog).map(E.parseChord);
  return E.generateNotes(chords, m, bpc || m.numerator, reps, names).notes
    .map((n) => [n.inst, +n.start.toFixed(4), +n.duration.toFixed(4), n.pitch, n.velocity]);
})));
"""


def python_notes(progression, signature, beats_per_chord, repeats):
    meter = parse_time_signature(signature)
    beats_per_chord = beats_per_chord or meter.numerator
    notes, beat = [], 0
    for _ in range(repeats):
        for chord in parse_progression(progression):
            for name, instrument in INSTRUMENTS.items():
                for n in instrument.pattern(chord, beats_per_chord, meter, beat % meter.numerator):
                    notes.append((name, round(beat + n.start, 4), round(n.duration, 4),
                                  n.pitch, n.velocity))
            beat += beats_per_chord
    return sorted(notes)


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class WebParityTests(unittest.TestCase):
    def test_web_engine_matches_python(self):
        html = WEB_APP.read_text()
        engine = re.search(r'<script id="engine">(.*?)</script>', html, re.S).group(1)
        with tempfile.TemporaryDirectory() as tmp:
            engine_path = pathlib.Path(tmp, "engine.cjs")
            engine_path.write_text(engine + "\nmodule.exports = { parseChord, tokenize, "
                                   "parseTimeSignature, generateNotes };\n")
            runner_path = pathlib.Path(tmp, "runner.cjs")
            runner_path.write_text(RUNNER)
            output = subprocess.run(
                ["node", str(runner_path), str(engine_path), json.dumps(CASES)],
                check=True, capture_output=True, text=True).stdout
        for case, js_notes in zip(CASES, json.loads(output)):
            with self.subTest(signature=case[1], progression=case[0]):
                self.assertEqual(python_notes(*case), sorted(map(tuple, js_notes)))


if __name__ == "__main__":
    unittest.main()
