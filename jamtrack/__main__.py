"""Command line entry point: ``python -m jamtrack "C G Am F" -o jam.mid``."""

import argparse
import sys

from .generator import generate
from .instruments import INSTRUMENTS


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="jamtrack",
        description="Generate a MIDI backing track from a chord progression.",
        epilog="Instruments: " + "; ".join(
            f"{i.name} ({i.description})" for i in INSTRUMENTS.values()),
    )
    parser.add_argument("progression", help='chords, e.g. "C G Am F" or "Dm7 | G7 | Cmaj7"')
    parser.add_argument("-o", "--output", default="jam.mid", help="output .mid file")
    parser.add_argument("-i", "--instruments", default="piano,guitar,strings,bass",
                        help="comma-separated instruments (default: %(default)s)")
    parser.add_argument("--bpm", type=float, default=100)
    parser.add_argument("--beats-per-bar", type=int, default=4)
    parser.add_argument("--beats-per-chord", type=int,
                        help="beats each chord lasts (default: one bar)")
    parser.add_argument("-r", "--repeats", type=int, default=4,
                        help="times to loop the progression")
    parser.add_argument("--no-humanize", action="store_true",
                        help="disable velocity variation")
    parser.add_argument("--seed", type=int, help="random seed for humanizing")
    args = parser.parse_args(argv)

    instruments = [name.strip() for name in args.instruments.split(",") if name.strip()]
    try:
        generate(args.progression, args.output, instruments=instruments, bpm=args.bpm,
                 beats_per_bar=args.beats_per_bar, beats_per_chord=args.beats_per_chord,
                 repeats=args.repeats, humanize=not args.no_humanize, seed=args.seed)
    except ValueError as err:
        parser.error(str(err))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    sys.exit(main())
