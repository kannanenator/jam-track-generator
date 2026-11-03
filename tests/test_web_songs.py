"""Songs in sections, MIDI tempo changes, and the test-mode checkout in web/index.html.

These run the page's own JavaScript in Node. Skipped when Node isn't installed.
"""

import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

import mido

WEB_APP = pathlib.Path(__file__).resolve().parent.parent / "web" / "index.html"

EXPORTS = ("parseChord, tokenize, parseTimeSignature, parseForm, renameInForm, removeFromForm, "
           "sectionNameError, generateSong, loopRepeats, buildMidi, transposeText, spellingFor, "
           "PLAN, validateTestCard, createTestBilling")


def run_node(script):
    """Run `script` with the page's engine and billing code in scope; return its JSON output."""
    html = WEB_APP.read_text()
    code = "\n".join(re.search(rf'<script id="{name}">(.*?)</script>', html, re.S).group(1)
                     for name in ("engine", "billing"))
    with tempfile.TemporaryDirectory() as tmp:
        module = pathlib.Path(tmp, "page.cjs")
        module.write_text(code + f"\nmodule.exports = {{ {EXPORTS} }};\n")
        runner = pathlib.Path(tmp, "run.cjs")
        runner.write_text(f"const P = require({json.dumps(str(module))});\n"
                          "(async () => { console.log(JSON.stringify(await (async () => {\n"
                          f"{script}\n"
                          "})())); })().catch((e) => { console.error(e); process.exit(1); });\n")
        out = subprocess.run(["node", str(runner)], check=True, capture_output=True, text=True).stdout
    return json.loads(out)


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class PlayOrderTests(unittest.TestCase):
    def test_parse_form(self):
        result = run_node("""
          const names = ["A", "B", "Chorus"];
          const ok = (t) => P.parseForm(t, names);
          const err = (t) => { try { P.parseForm(t, names); return null; } catch (e) { return e.message; } };
          return {
            empty: ok(""), spaced: ok("A A B B"), commas: ok("a,b, chorus"), repeat: ok("A x2 B ×3"),
            unknown: err("A C"), leading: err("x2 A"), tooMany: err("A x17"),
          };
        """)
        self.assertEqual(result["empty"], [0, 1, 2])
        self.assertEqual(result["spaced"], [0, 0, 1, 1])
        self.assertEqual(result["commas"], [0, 1, 2])
        self.assertEqual(result["repeat"], [0, 0, 1, 1, 1])
        self.assertIn("no section called “C”", result["unknown"])
        self.assertIn("before “x2”", result["leading"])
        self.assertIn("x1 to x16", result["tooMany"])

    def test_rename_and_remove(self):
        result = run_node("""
          return {
            renamed: P.renameInForm("A a B A", "A", "Verse"),
            removed: P.removeFromForm("A x2 B A C x3", "A"),
            badNames: ["", "Two words", "x2", "Chorus"].map(P.sectionNameError),
          };
        """)
        self.assertEqual(result["renamed"], "Verse Verse B Verse")
        self.assertEqual(result["removed"], "B C x3")
        self.assertTrue(all(result["badNames"][:3]))
        self.assertEqual(result["badNames"][3], "")

    def test_transposing_sections_uses_one_spelling(self):
        result = run_node("""
          const names = P.spellingFor("C G Am F", 1);
          return ["C G Am F", "Dm7 E7"].map((t) => P.transposeText(t, 1, names));
        """)
        # Db major is written with flats, so the second section is too.
        self.assertEqual(result, ["Db Ab Bbm Gb", "Ebm7 F7"])


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class SongTests(unittest.TestCase):
    def test_segments_and_cells(self):
        result = run_node("""
          const m = P.parseTimeSignature("4/4");
          const chords = (t) => P.tokenize(t).map(P.parseChord);
          const parts = [
            { name: "Intro", chords: chords("Am F"), bpm: 72 },
            { name: "A", chords: chords("C G Am"), bpm: null },
          ];
          const song = P.generateSong(parts, m, 4, 2, ["bass"]);
          return { beats: song.beats, cells: song.cells.length,
                   segments: song.segments.map(({ start, end, name, bpm }) => ({ start, end, name, bpm })) };
        """)
        self.assertEqual(result["beats"], 40)
        self.assertEqual(result["cells"], 10)
        self.assertEqual(result["segments"], [
            {"start": 0, "end": 8, "name": "Intro", "bpm": 72},
            {"start": 8, "end": 20, "name": "A", "bpm": None},
            {"start": 20, "end": 28, "name": "Intro", "bpm": 72},
            {"start": 28, "end": 40, "name": "A", "bpm": None},
        ])

    def test_sections_in_different_time_signatures(self):
        result = run_node("""
          const chords = (t) => P.tokenize(t).map(P.parseChord);
          const meter = (sig) => P.parseTimeSignature(sig);
          const bpc = (m) => m.numerator;
          const waltz = meter("3/4"), common = meter("4/4"), compound = meter("6/8");
          const parts = [
            { name: "A", chords: chords("G D"), bpm: 150, meter: waltz, beatsPerChord: 3 },
            { name: "B", chords: chords("Em"), bpm: 100, meter: common, beatsPerChord: 2 },
            { name: "C", chords: chords("C"), bpm: 60, meter: compound, beatsPerChord: 6 },
          ];
          const song = P.generateSong(parts, waltz, 3, 1, ["drums"]);
          const kicks = song.notes.filter((n) => n.pitch === 36).map((n) => n.q);
          return {
            segments: song.segments.map(({ start, end, qStart, qEnd, barPos }) => [start, end, qStart, qEnd, barPos]),
            kicks,
            sameMeterRepeats: P.loopRepeats([{ chords: chords("C G Am"), meter: common, beatsPerChord: 2 }], common, 2),
            mixedRepeats: P.loopRepeats(parts, waltz, 3),
          };
        """)
        # Beats are each section's own (quarters, quarters, eighths); q lines them up.
        self.assertEqual(result["segments"], [
            [0, 6, 0, 6, 0],
            [6, 8, 6, 8, 0],     # 4/4 starts a fresh bar
            [8, 14, 8, 11, 0],   # six eighths = three quarters
        ])
        # Kick on each waltz downbeat, beats 1 and 3 of the 4/4 bar, then the 6/8 downbeat.
        self.assertEqual(result["kicks"], [0, 3, 6, 8])
        # 3 chords of half a bar end mid-bar, so the loop takes two passes to land on a bar line.
        self.assertEqual(result["sameMeterRepeats"], 2)
        self.assertEqual(result["mixedRepeats"], 1)

    def test_midi_has_tempo_changes_and_markers(self):
        midi_bytes = run_node("""
          const m = P.parseTimeSignature("4/4");
          const chords = (t) => P.tokenize(t).map(P.parseChord);
          const parts = [
            { name: "Intro", chords: chords("Am F"), bpm: 60 },
            { name: "A", chords: chords("C G"), bpm: null },
            { name: "A", chords: chords("C G"), bpm: null },
            { name: "B", chords: chords("F"), bpm: 180 },
          ];
          return [...P.buildMidi({ parts, meter: m, beatsPerChord: 4, repeats: 1, bpm: 120,
                                   names: ["piano", "drums"], humanize: false })];
        """)
        with tempfile.NamedTemporaryFile(suffix=".mid") as f:
            f.write(bytes(midi_bytes))
            f.flush()
            midi = mido.MidiFile(f.name)
        tick, tempos, markers = 0, [], []
        for msg in midi.tracks[0]:
            tick += msg.time
            if msg.type == "set_tempo":
                tempos.append((tick // 480, round(mido.tempo2bpm(msg.tempo))))
            elif msg.type == "marker":
                markers.append((tick // 480, msg.text))
        # 60 bpm intro, 120 for both A's (one change, not two), then 180 for B.
        self.assertEqual(tempos, [(0, 60), (8, 120), (24, 180)])
        self.assertEqual(markers, [(0, "Intro"), (8, "A"), (16, "A"), (24, "B")])
        # 8 beats at 60 + 16 at 120 + 4 at 180 = 8 + 8 + 1.333 seconds.
        self.assertAlmostEqual(midi.length, 17.333, places=2)
        self.assertEqual([t.name for t in midi.tracks[1:]], ["piano", "drums"])

    def test_midi_changes_time_signature_between_sections(self):
        midi_bytes = run_node("""
          const chords = (t) => P.tokenize(t).map(P.parseChord);
          const waltz = P.parseTimeSignature("3/4"), compound = P.parseTimeSignature("6/8");
          const parts = [
            { name: "A", chords: chords("G D"), bpm: 150, meter: waltz, beatsPerChord: 3 },
            { name: "B", chords: chords("Em C"), bpm: 90, meter: compound, beatsPerChord: 6 },
          ];
          return [...P.buildMidi({ parts, meter: waltz, beatsPerChord: 3, repeats: 1, bpm: 150,
                                   names: ["bass"], humanize: false })];
        """)
        with tempfile.NamedTemporaryFile(suffix=".mid") as f:
            f.write(bytes(midi_bytes))
            f.flush()
            midi = mido.MidiFile(f.name)
        tick, sigs, tempos, notes = 0, [], [], []
        for msg in midi.tracks[0]:
            tick += msg.time
            if msg.type == "time_signature":
                sigs.append((tick / 480, f"{msg.numerator}/{msg.denominator}"))
            elif msg.type == "set_tempo":
                tempos.append((tick / 480, round(mido.tempo2bpm(msg.tempo))))
        tick = 0
        for msg in midi.tracks[1]:
            tick += msg.time
            if msg.type == "note_on":
                notes.append(tick / 480)
        self.assertEqual(sigs, [(0, "3/4"), (6, "6/8")])
        # Bass once per waltz bar, then on both dotted-quarter pulses of each 6/8 bar.
        self.assertEqual(notes, [0, 3, 6, 7.5, 9, 10.5])
        self.assertEqual(tempos, [(0, 150), (6, 90)])


@unittest.skipUnless(shutil.which("node"), "Node.js is not installed")
class TestCheckoutTests(unittest.TestCase):
    def test_card_rules(self):
        result = run_node("""
          const now = new Date(2026, 10, 2);
          const good = { name: "Pat", number: "4242 4242 4242 4242", exp: "12/30", cvc: "123" };
          const check = (overrides) => {
            try { return P.validateTestCard({ ...good, ...overrides }, now); }
            catch (e) { return { field: e.field, message: e.message }; }
          };
          return {
            ok: check({}),
            amex: check({ number: "3782 822463 10005", cvc: "1234" }),
            noName: check({ name: " " }),
            realCard: check({ number: "4111 1111 1111 1111" }),
            junk: check({ number: "1234 5678 9012 3456" }),
            badExp: check({ exp: "13/30" }),
            lastMonth: check({ exp: "10/26" }),
            thisMonth: check({ exp: "11/26" }),
            shortCvc: check({ cvc: "12" }),
          };
        """)
        self.assertEqual(result["ok"], {"last4": "4242", "brand": "Visa"})
        self.assertEqual(result["amex"], {"last4": "0005", "brand": "Amex"})
        self.assertEqual(result["noName"]["field"], "card-name")
        # A real-looking card is refused, so test mode never takes one.
        self.assertEqual(result["realCard"]["field"], "card-number")
        self.assertIn("real cards don't work", result["realCard"]["message"])
        self.assertIn("isn't valid", result["junk"]["message"])
        self.assertEqual(result["badExp"]["field"], "card-exp")
        self.assertIn("passed", result["lastMonth"]["message"])
        self.assertEqual(result["thisMonth"], {"last4": "4242", "brand": "Visa"})
        self.assertEqual(result["shortCvc"]["field"], "card-cvc")

    def test_billing_keeps_only_the_last_four_digits(self):
        result = run_node("""
          let saved = null;
          const store = { async getAccount() { return saved; }, async setAccount(a) { saved = a; } };
          const billing = P.createTestBilling(store, async () => {});
          const before = await billing.status();
          let refused = null;
          try { await billing.subscribe({ name: "Pat", number: "4111111111111111", exp: "12/40", cvc: "123" }); }
          catch (e) { refused = e.field; }
          await billing.subscribe({ name: "Pat", number: "4242424242424242", exp: "12/40", cvc: "123" });
          const after = await billing.status();
          const stored = JSON.stringify(saved);
          await billing.cancel();
          return { before, refused, after, stored, cancelled: await billing.status() };
        """)
        self.assertIsNone(result["before"])
        self.assertEqual(result["refused"], "card-number")
        self.assertEqual(result["after"]["status"], "active")
        self.assertEqual(result["after"]["last4"], "4242")
        self.assertNotIn("42424242", result["stored"])
        self.assertNotIn("Pat", result["stored"])
        self.assertIsNone(result["cancelled"])


if __name__ == "__main__":
    unittest.main()
