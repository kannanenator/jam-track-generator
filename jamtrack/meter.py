"""Time signatures and how their beats group into pulses."""

from dataclasses import dataclass
from typing import Optional, Tuple

# MIDI stores the denominator as a power of two, so these are the note values
# a time signature can count in (whole note down to 32nd note).
VALID_DENOMINATORS = (1, 2, 4, 8, 16, 32)
MAX_BEATS = 64


def default_grouping(numerator, denominator):
    """How a meter's beats are felt when no grouping is given.

    4/4 -> 2+2, 3/4 -> 3, 6/8 -> 3+3, 5/4 -> 2+3, 7/8 -> 2+2+3, 11/8 -> 2+2+2+2+3.
    """
    n = numerator
    if n == 3 or (denominator >= 8 and n % 3 == 0):
        return (3,) * (n // 3)
    if n % 2 == 0:
        return (2,) * (n // 2)
    if n == 1:
        return (1,)
    return (2,) * ((n - 3) // 2) + (3,)


@dataclass(frozen=True)
class Meter:
    numerator: int  # beats per bar
    denominator: int  # note value of one beat (4 = quarter, 8 = eighth)
    grouping: Optional[Tuple[int, ...]] = None  # e.g. (3, 2, 2) for 3+2+2/8

    def __post_init__(self):
        if not 1 <= self.numerator <= MAX_BEATS:
            raise ValueError(
                f"Beats per bar must be between 1 and {MAX_BEATS}, got {self.numerator}")
        if self.denominator not in VALID_DENOMINATORS:
            raise ValueError(f"Time signature denominator must be one of "
                             f"{', '.join(map(str, VALID_DENOMINATORS))}, got {self.denominator}")
        if self.grouping is None:
            object.__setattr__(
                self, "grouping", default_grouping(self.numerator, self.denominator))
        else:
            grouping = tuple(self.grouping)
            if not grouping or any(size < 1 for size in grouping):
                raise ValueError("Beat groups must each be at least 1 beat")
            if sum(grouping) != self.numerator:
                raise ValueError(f"Beat groups {'+'.join(map(str, grouping))} add up to "
                                 f"{sum(grouping)}, not {self.numerator}")
            object.__setattr__(self, "grouping", grouping)

    def __str__(self):
        if self.grouping == default_grouping(self.numerator, self.denominator):
            return f"{self.numerator}/{self.denominator}"
        return f"{'+'.join(map(str, self.grouping))}/{self.denominator}"

    @property
    def compound(self):
        """6/8, 9/8, 12/8...: short beats felt in several groups of three."""
        return (self.denominator >= 8 and len(self.grouping) > 1
                and all(size == 3 for size in self.grouping))

    @property
    def offbeats(self):
        """Whether parts add an "and" between beats: not in compound meters,
        and not when the beat is already a 16th or shorter."""
        return not self.compound and self.denominator <= 8

    @property
    def quarters_per_beat(self):
        return 4 / self.denominator

    @property
    def groups(self):
        """(start, length) of each pulse group in a bar."""
        groups, start = [], 0
        for size in self.grouping:
            groups.append((start, size))
            start += size
        return groups

    def group_at(self, position):
        """Index, start and length of the group containing bar position ``position``."""
        for index, (start, length) in enumerate(self.groups):
            if start <= position < start + length:
                return index, start, length
        raise ValueError(f"Position {position} is outside a bar of {self}")


def parse_time_signature(text):
    """Parse a time signature into a ``Meter``.

    Accepts plain signatures ("4/4", "11/8", "13/16") and additive ones that
    spell out the beat grouping ("3+2+2/8", "2+2+2+3/8").
    """
    if isinstance(text, Meter):
        return text
    try:
        top, bottom = str(text).replace(" ", "").split("/")
        denominator = int(bottom)
        parts = [int(part) for part in top.split("+")]
    except ValueError:
        raise ValueError(f"Time signature should look like 4/4, 11/8 or 3+2+2/8, "
                         f"got {text!r}") from None
    if len(parts) == 1:
        return Meter(parts[0], denominator)
    return Meter(sum(parts), denominator, tuple(parts))
