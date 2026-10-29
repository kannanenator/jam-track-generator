"""Time signatures and how their beats group into pulses."""

from dataclasses import dataclass

VALID_DENOMINATORS = (2, 4, 8, 16)


@dataclass(frozen=True)
class Meter:
    numerator: int  # beats per bar
    denominator: int  # note value of one beat (4 = quarter, 8 = eighth)

    def __post_init__(self):
        if not 1 <= self.numerator <= 32:
            raise ValueError(f"Beats per bar must be between 1 and 32, got {self.numerator}")
        if self.denominator not in VALID_DENOMINATORS:
            raise ValueError(f"Time signature denominator must be one of "
                             f"{', '.join(map(str, VALID_DENOMINATORS))}, got {self.denominator}")

    def __str__(self):
        return f"{self.numerator}/{self.denominator}"

    @property
    def compound(self):
        """6/8, 9/8, 12/8...: beats felt in groups of three."""
        return self.denominator >= 8 and self.numerator % 3 == 0 and self.numerator > 3

    @property
    def quarters_per_beat(self):
        return 4 / self.denominator

    @property
    def groups(self):
        """(start, length) of each pulse group in a bar.

        4/4 -> two groups of 2, 3/4 -> one group of 3, 6/8 -> two groups of 3,
        5/4 -> 2 + 3, 7/8 -> 2 + 2 + 3.
        """
        n = self.numerator
        if self.compound or n == 3:
            sizes = [3] * (n // 3)
        elif n % 2 == 0:
            sizes = [2] * (n // 2)
        elif n == 1:
            sizes = [1]
        else:
            sizes = [2] * ((n - 3) // 2) + [3]
        groups, start = [], 0
        for size in sizes:
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
    """Parse "4/4", "3/4", "6/8" etc. into a ``Meter``."""
    if isinstance(text, Meter):
        return text
    try:
        numerator, denominator = (int(part) for part in str(text).split("/"))
    except ValueError:
        raise ValueError(f"Time signature should look like 4/4 or 6/8, got {text!r}") from None
    return Meter(numerator, denominator)
