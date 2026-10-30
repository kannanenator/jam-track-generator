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
grouping like `3+2+2/8`), mix the band and play along. It
synthesizes the instruments in the browser and can save the MIDI file. Open
the file directly or serve the `web/` folder from any static host, such as
GitHub Pages.

The page carries a JavaScript copy of the chord parser, meters and instrument
patterns. `tests/test_web_parity.py` runs it in Node and checks that it plays
exactly the same notes as the Python package, so change both together.

## Tests

```bash
python -m unittest discover -s tests
```
