"""Варіант 3. Бібліотечний каталог: конвеєр на partial + reduce + operator."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import partial, reduce
from itertools import islice
from operator import add, attrgetter, itemgetter, methodcaller
from typing import Any, TypeVar

from loaders import RawBook, load_books
from models import Book

T = TypeVar("T")
U = TypeVar("U")


def pipeline(value: Any, *funcs: Callable[[Any], Any]) -> Any:
    """Пропускає value крізь funcs зліва направо (functools.reduce)."""
    return reduce(lambda acc, f: f(acc), funcs, value)


def mapf(fn: Callable[[T], U]) -> Callable[[Iterable[T]], Iterable[U]]:
    return partial(map, fn)


def filt(pred: Callable[[T], bool]) -> Callable[[Iterable[T]], Iterable[T]]:
    return partial(filter, pred)


# --- operator-гетери ---------------------------------------------------------
get_title, get_author = itemgetter("title"), itemgetter("author")
get_year, get_pages, get_rating = (
    itemgetter("year"),
    itemgetter("pages"),
    itemgetter("rating"),
)
strip, title_case = methodcaller("strip"), methodcaller("title")
squash_spaces = partial(lambda s: " ".join(s.split()))


def normalize(r: RawBook) -> RawBook:
    """Новий запис: обрізані/нормалізовані рядки, правильні типи."""
    return {
        "title": title_case(squash_spaces(strip(str(get_title(r))))),
        "author": title_case(squash_spaces(strip(str(get_author(r))))),
        "year": int(get_year(r)),
        "pages": int(get_pages(r)),
        "rating": float(get_rating(r)),
    }


def book_filter(
    r: RawBook, *, min_year: int = 0, max_year: int = 9999, min_rating: float = 0.0
) -> bool:
    year: int = r["year"]
    rating: float = r["rating"]
    return min_year <= year <= max_year and rating >= min_rating


def rank_key(r: RawBook) -> tuple[float, int, str]:
    """rating ↓, year ↓ (новіші вище), title ↑."""
    return (-get_rating(r), -get_year(r), get_title(r))


def top(n: int) -> Callable[[Iterable[T]], list[T]]:
    return lambda it: list(islice(it, max(n, 0)))


def clean_and_rank(
    src: object, *, top_n: int = 3, min_year: int = 0, min_rating: float = 0.0
) -> list[RawBook]:
    """Завантажити → нормалізувати → відфільтрувати → відсортувати → Top-N."""
    return pipeline(  # type: ignore[no-any-return]
        src,
        load_books,
        mapf(normalize),
        filt(partial(book_filter, min_year=min_year, min_rating=min_rating)),
        partial(sorted, key=rank_key),
        top(top_n),
    )


def to_books(records: Iterable[RawBook]) -> list[Book]:
    return list(map(Book.from_record, records))


def total_pages(records: Iterable[RawBook]) -> int:
    return reduce(add, map(get_pages, records), 0)


def average_rating(records: list[RawBook]) -> float:
    count, s = reduce(lambda a, r: (a[0] + 1, a[1] + r["rating"]), records, (0, 0.0))
    return round(s / count, 2) if count else 0.0


def books_by(author: str) -> Callable[[Iterable[Book]], list[Book]]:
    """attrgetter для об'єктів Book."""
    get = attrgetter("author")
    return lambda books: sorted(
        (b for b in books if get(b) == author), key=attrgetter("year")
    )
