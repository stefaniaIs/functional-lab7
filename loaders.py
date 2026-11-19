"""Поліморфне завантаження книг (@singledispatch): JSON/CSV/Path/file/list."""

from __future__ import annotations

import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import Any

RawBook = dict[str, Any]


def _parse_text(text: str, fmt: str) -> list[RawBook]:
    if fmt == "csv":
        return [dict(row) for row in csv.DictReader(io.StringIO(text))]
    data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("JSON must contain a list of books")
    return data


def _guess_format(text: str) -> str:
    return "json" if text.lstrip().startswith(("[", "{")) else "csv"


@singledispatch
def load_books(src: object) -> list[RawBook]:
    """Єдина точка входу; конкретна реалізація обирається за типом src."""
    raise TypeError(f"Unsupported source type: {type(src)!r}")


@load_books.register
def _(src: str) -> list[RawBook]:
    s = src.strip()
    if s.startswith(("[", "{")):  # JSON-рядок
        return _parse_text(s, "json")
    if "\n" in s and "," in s:  # CSV-текст
        return _parse_text(s, "csv")
    return load_books(Path(s))  # інакше - шлях


@load_books.register
def _(src: Path) -> list[RawBook]:
    fmt = "csv" if src.suffix.lower() == ".csv" else "json"
    return _parse_text(src.read_text(encoding="utf-8"), fmt)


@load_books.register
def _(src: io.TextIOBase) -> list[RawBook]:
    text = src.read()
    name = str(getattr(src, "name", ""))
    fmt = "csv" if name.lower().endswith(".csv") else _guess_format(text)
    return _parse_text(text, fmt)


@load_books.register
def _(src: list) -> list[RawBook]:  # type: ignore[type-arg]
    if not all(isinstance(x, dict) for x in src):
        raise ValueError("Expected list of dicts")
    return [dict(x) for x in src]  # копія - вхід не мутуємо


@load_books.register
def _(src: tuple) -> list[RawBook]:  # type: ignore[type-arg]
    return load_books(list(src))
