import io
from copy import deepcopy
from functools import partial, reduce
from operator import attrgetter, itemgetter, methodcaller, mul
from pathlib import Path

import pytest

from core import (
    average_rating,
    book_filter,
    books_by,
    clean_and_rank,
    normalize,
    pipeline,
    rank_key,
    to_books,
    total_pages,
)
from loaders import load_books
from models import Book

DATA = Path(__file__).parent.parent
JSON_TEXT = (DATA / "sample_data.json").read_text(encoding="utf-8")
CSV_TEXT = (DATA / "sample_data.csv").read_text(encoding="utf-8")


# --- pipeline / reduce / partial ----------------------------------------------
def test_pipeline_order() -> None:
    assert pipeline(3, lambda x: x + 1, lambda x: x * 2, lambda x: x + 1) == 9
    assert pipeline(5) == 5


def test_reduce_initial_value() -> None:
    assert reduce(mul, [], 1) == 1
    assert total_pages([]) == 0 and average_rating([]) == 0.0


def test_partial_filter() -> None:
    newer = partial(book_filter, min_year=2000, min_rating=4.6)
    recs = [normalize(r) for r in load_books(JSON_TEXT)]
    assert [r["title"] for r in filter(newer, recs)] == [
        "Voroshilovgrad",
        "Felix Austria",
    ]


# --- operator ---------------------------------------------------------------
def test_normalize_with_methodcaller() -> None:
    r = normalize(
        {
            "title": "  the  forest song ",
            "author": "lesya ukrainka",
            "year": "1911",
            "pages": "120",
            "rating": "4.7",
        }
    )
    assert r == {
        "title": "The Forest Song",
        "author": "Lesya Ukrainka",
        "year": 1911,
        "pages": 120,
        "rating": 4.7,
    }


def test_itemgetter_multi_key_sort() -> None:
    rows = [{"a": 1, "b": 2}, {"a": 1, "b": 1}, {"a": 0, "b": 9}]
    assert sorted(rows, key=itemgetter("a", "b")) == [rows[2], rows[1], rows[0]]
    assert methodcaller("upper")("x") == "X"


def test_attrgetter_on_books() -> None:
    books = to_books(clean_and_rank(JSON_TEXT, top_n=10))
    assert [b.year for b in sorted(books, key=attrgetter("year"))][0] == 1840
    assert [b.title for b in books_by("Taras Shevchenko")(books)] == ["Kobzar"]


# --- конвеєр clean_and_rank -------------------------------------------------
def test_clean_and_rank_top_n() -> None:
    res = clean_and_rank(JSON_TEXT, top_n=3, min_year=1900)
    assert [r["title"] for r in res] == [
        "Tygrolovy",
        "The Forest Song",
        "Felix Austria",
    ]


def test_rank_tiebreak_newer_first() -> None:
    res = clean_and_rank(JSON_TEXT, top_n=10)
    tied = [r["title"] for r in res if r["rating"] == 4.6]
    assert tied == ["Felix Austria", "Voroshilovgrad"]  # 2014 перед 2010
    assert sorted(res, key=rank_key) == res


def test_no_mutation_of_list_source() -> None:
    src = load_books(JSON_TEXT)
    snapshot = deepcopy(src)
    clean_and_rank(src, top_n=2)
    assert src == snapshot


def test_top_zero() -> None:
    assert clean_and_rank(JSON_TEXT, top_n=0) == []


# --- singledispatch ---------------------------------------------------------
def test_load_books_all_sources_agree(tmp_path: Path) -> None:
    jp, cp = tmp_path / "b.json", tmp_path / "b.csv"
    jp.write_text(JSON_TEXT, encoding="utf-8")
    cp.write_text(CSV_TEXT, encoding="utf-8")
    expected = clean_and_rank(JSON_TEXT, top_n=10)
    with open(jp, encoding="utf-8") as fj, open(cp, encoding="utf-8") as fc:
        sources: list[object] = [
            str(jp),
            jp,
            fj,
            str(cp),
            cp,
            fc,
            CSV_TEXT,
            io.StringIO(JSON_TEXT),
            io.StringIO(CSV_TEXT),
            load_books(JSON_TEXT),
            tuple(load_books(JSON_TEXT)),
        ]
        for src in sources:
            assert clean_and_rank(src, top_n=10) == expected, src


def test_load_books_errors() -> None:
    with pytest.raises(TypeError):
        load_books(42)
    with pytest.raises(ValueError):
        load_books([1, 2])
    with pytest.raises(ValueError):
        load_books('{"title": "x"}')


# --- total_ordering ---------------------------------------------------------
def test_book_comparisons() -> None:
    a = Book("A", "x", 2000, 100, 4.5)
    b = Book("B", "y", 2000, 100, 4.8)
    c = Book("C", "z", 2010, 100, 4.5)
    a2 = Book("A", "other author", 2000, 999, 4.5)
    assert a < b and a <= b and b > a and b >= a and a != b
    assert a < c  # той самий рейтинг -> новіша більша
    assert a == a2 and a <= a2 and a >= a2 and hash(a) == hash(a2)
    assert sorted([b, c, a]) == [a, c, b]
    assert max([a, b, c]) is b


def test_book_not_implemented_for_other_types() -> None:
    a = Book("A", "x", 2000, 100, 4.5)
    assert a.__eq__(5) is NotImplemented
    assert a.__lt__("x") is NotImplemented
    assert (a == 5) is False
    with pytest.raises(TypeError):
        _ = a < 5
