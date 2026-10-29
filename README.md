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
jamtrack "Dm7 | G7 | Cmaj7 | Cmaj7" --bpm 120 -i piano,bass,strings -r 8
```

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

Each instrument gets its own track and MIDI channel, so you can mute, swap
sounds or mix the parts in a DAW. Pick a subset with `-i`, e.g.
`-i piano,strings`.

From Python:

```python
from jamtrack import generate

generate("Am F C G", "jam.mid", instruments=["guitar", "bass"], bpm=90)
```

## Tests

```bash
python -m unittest discover -s tests
```
