"""Предметний клас Book з повним порядком через @total_ordering."""

from __future__ import annotations

from dataclasses import dataclass
from functools import total_ordering
from typing import Any


@total_ordering
@dataclass(frozen=True, eq=False)
class Book:
    title: str
    author: str
    year: int
    pages: int
    rating: float

    def _key(self) -> tuple[float, int, str]:
        """Порядок: rating, потім year, потім title."""
        return (self.rating, self.year, self.title)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Book):
            return NotImplemented
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    @classmethod
    def from_record(cls, r: dict[str, Any]) -> Book:
        return cls(r["title"], r["author"], r["year"], r["pages"], r["rating"])
