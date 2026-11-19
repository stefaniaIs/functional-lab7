# Лабораторна робота №7 — functools та operator

**Варіант 3. Бібліотечний каталог.** Іщенко Стефанія, ФеП-22.

Книги: `title, author, year, pages, rating`. Нормалізуємо назви, відбираємо книги за
роком/рейтингом, сортуємо, беремо Top-N.

## Структура
| Файл | Що всередині |
|---|---|
| `core.py` | `pipeline` (через `reduce`), `mapf`/`filt` (через `partial`), `normalize` (`itemgetter` + `methodcaller`), `book_filter` (налаштовується `partial`), `rank_key`, `clean_and_rank`, `total_pages` / `average_rating` (`reduce`), `books_by` (`attrgetter`) |
| `loaders.py` | `load_books` на `@singledispatch`: `str` (JSON-рядок / CSV-текст / шлях), `Path` (.json / .csv), відкритий файл `io.TextIOBase`, `list`, `tuple` |
| `models.py` | `Book` з `@total_ordering`: `__eq__` + `__lt__` за `(rating, year, title)`, `NotImplemented` для чужих типів |
| `main.py` | демо; `sample_data.json`, `sample_data.csv` — дані |

## Конвеєр `clean_and_rank(src, top_n=, min_year=, min_rating=)`
```
load_books → map(normalize) → filter(partial(book_filter, …)) → partial(sorted, key=rank_key) → top(n)
```
Сортування багатокритеріальне: rating ↓, year ↓, title ↑.

## Тести (`tests/test_lab07.py`, 14 шт.)
`pipeline`, `reduce` з початковим значенням, `partial`, `itemgetter`/`methodcaller`/`attrgetter`,
Top-N і тай-брейк, немутація вхідного списку, **однаковий результат для 11 видів джерел**
(str-шлях JSON/CSV, Path, відкриті файли, StringIO, CSV-текст, list, tuple), помилки
`load_books`, усі оператори порівняння `<, <=, >, >=, ==, !=`, `NotImplemented`.

## Запуск
```bash
pip install -r requirements.txt
pytest -q
mypy . && black --check . && ruff check .
python main.py
```
