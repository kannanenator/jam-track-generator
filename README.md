# jam-track-generator

Generate MIDI backing tracks to jam over from a chord progression.

## Install

```bash
pip install -e .
```

The only dependency is [mido](https://github.com/mido/mido) (MIT licensed).

## Usage

```bash
jamtrack "C G Am F" -o jam.mid
jamtrack "Dm7 | G7 | Cmaj7 | Cmaj7" --bpm 120 -i piano,bass,drums -r 8
jamtrack "D G A7 D" --time-signature 3/4 --bpm 150 -o waltz.mid
jamtrack "Em C G D" -t 6/8 --bpm 70 -o ballad.mid
jamtrack "Dm7 G7" -t 3+2+2/8 --bpm 200 -o balkan.mid
```

- `-b/--bpm/--tempo`: tempo in quarter notes per minute, the same way a DAW
  shows it, whatever the time signature (default 100).
- `-t/--time-signature`: any `N/D` with up to 64 beats and D of 1, 2, 4, 8,
  16 or 32 (default `4/4`). Beats are grouped into pulses the parts follow:
  4/4 as 2+2, 3/4 as 3, 6/8 and 12/8 as dotted quarters, odd meters as 2s
  with a 3 at the end (5/4 = 2+3, 7/8 = 2+2+3, 11/8 = 2+2+2+2+3). Spell out
  a different grouping with `+`, e.g. `-t 3+2+2/8` or `-t 3+3+2/8`.
- `-r/--repeats`: how many times to loop the progression (default 4).

Each chord lasts one bar by default (`--beats-per-chord` changes that). Chords
can be separated by spaces or `|`. Supported symbols include triads (`C`, `Am`,
`Bdim`, `Faug`, `Dsus4`), sevenths (`G7`, `Fmaj7`, `Em7`, `Bm7b5`, `Cdim7`),
extensions (`D9`, `Am9`, `Cadd9`) and slash chords (`C/E`).

## Instruments

| Name      | General MIDI sound      | Part                                           |
|-----------|-------------------------|------------------------------------------------|
| `piano`   | Acoustic Grand Piano    | Bass note held; chords on beats 1 and 3        |
| `guitar`  | Steel-string acoustic   | Strummed eighths (down on beats, up on the "and"s) |
| `strings` | String Ensemble 1       | Sustained pad                                  |
| `bass`    | Fingered electric bass  | Root on 1, fifth on 3                          |
| `drums`   | Standard GM drum kit    | Kick/snare backbeat with a steady hi-hat       |

In 4/4 the drums play kick on 1 and 3 and snare on 2 and 4; in 3/4, kick on 1
and snare on 2 and 3; in 6/8, kick on 1 and snare on 4. Drums use MIDI channel
10, the General MIDI percussion channel.

Each instrument gets its own track and MIDI channel, so you can mute, swap
sounds or mix the parts in a DAW. Pick a subset with `-i`, e.g.
`-i piano,strings`.

From Python:

```python
from jamtrack import generate

generate("Am F C G", "jam.mid", instruments=["guitar", "bass", "drums"],
         bpm=90, time_signature="6/8")
```

## Web app

`web/index.html` is the same generator as a single page that runs in a
browser, phones included: type chords or pick an example, transpose them a
half step at a time, set the tempo and time signature (any `N/D`, or a
grouping like `3+2+2/8`), mix the band and play along. Tempo and time
signature belong to each section of the song, so the music can change speed
and meter as it goes. It synthesizes the
instruments in the browser and can save the MIDI file. Open the file directly
or serve the `web/` folder from any static host, such as GitHub Pages.

### Sections and play order (Pro)

A song can have up to 12 named sections (A, B, Verse, Chorus, Intro...), each
with its own chords, tempo and time signature; a new section starts with the
previous one's tempo and time signature. Each section collapses to a one-line
summary, and transposes on its own (the buttons by the Chords label move the
whole song). The play order lists section names, like `A A B B` or
`Verse Chorus x2 Bridge Chorus`; left empty, each section plays once in
order.

Playback follows the order, each section's tempo and its meter: a section in
a new time signature starts on a fresh bar, while sections in the same meter
carry the bar on. Edits made while the band plays take effect from where it
is, without starting over, and a chord typo keeps the last version that
worked playing. Each section's play button, or tapping a chord in its chart,
jumps playback there. The chart highlights the section and chord that's playing,
and the saved MIDI file carries a marker plus any tempo or time signature
change at each section.

### Pro and the test-mode paywall

Free: one section (with its own tempo and time signature), everything else
above. Pro: more than one section, and
saving jams (title, sections with their tempos and time signatures, play
order and band mix) to open again later. Jams saved before sections had their
own tempo and time signature open with the song's old settings on every
section.

Billing is scaffolding for now. The page talks to billing only through
`createTestBilling`'s three methods (`status`, `subscribe`, `cancel`) in the
`<script id="billing">` block. In test mode, checkout accepts only the
standard test cards (`4242 4242 4242 4242`, any future date, any CVC), so a
real card can't be entered; card details are never stored or sent anywhere,
and only the last four digits are kept on the account.

To go live, replace `createTestBilling` with an implementation backed by a
payment provider (Stripe Checkout, for example). That needs a small server:
it creates the checkout session and, from the provider's webhooks, records who
is Pro. The page can only ask the server; anything kept in the browser can be
edited, so the client-side check is not the real paywall.

Saved jams and the account go through one storage interface (`openStore`).
Published as a Claude artifact, they live in each signed-in viewer's private
artifact storage. Opened anywhere else, the browser's localStorage stands in,
so jams stay on that one device until there's a server to keep them.

### Keeping the page and the package in step

The page carries a JavaScript copy of the chord parser, meters and instrument
patterns. `tests/test_web_parity.py` runs it in Node and checks that it plays
exactly the same notes as the Python package, so change both together.
`tests/test_web_songs.py` covers sections, play order, MIDI tempo changes and
the test-mode checkout.

## Tests

```bash
python -m unittest discover -s tests
```
