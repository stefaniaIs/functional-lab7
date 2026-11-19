from pathlib import Path

from core import average_rating, books_by, clean_and_rank, to_books, total_pages
from loaders import load_books

HERE = Path(__file__).parent


def main() -> None:
    for src in (HERE / "sample_data.json", str(HERE / "sample_data.csv")):
        print(f"Top-3 з {Path(src).name} (рік ≥ 1900, рейтинг ≥ 4.5):")
        for r in clean_and_rank(src, top_n=3, min_year=1900, min_rating=4.5):
            print(f"  {r['rating']}  {r['year']}  {r['title']} — {r['author']}")

    everything = clean_and_rank(HERE / "sample_data.json", top_n=100)
    print("Усього сторінок:", total_pages(everything))
    print("Середній рейтинг:", average_rating(everything))
    books = to_books(everything)
    print("Найкраща книга (max за total_ordering):", max(books).title)
    print("sorted(books):", [b.title for b in sorted(books)])
    print("Книги Шевченка:", books_by("Taras Shevchenko")(books))
    print("load_books(list) працює:", len(load_books(everything)))


if __name__ == "__main__":
    main()
