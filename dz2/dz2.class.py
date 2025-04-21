from pydantic import BaseModel, Field
from typing import List, Iterator, Generator, Type
from functools import wraps
import json
import logging
from abc import ABC, abstractmethod

# Налаштування логування
logging.basicConfig(filename='library_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BookModel(BaseModel):
    title: str = Field(..., description="Назва книги")
    author: str = Field(..., description="Автор книги")
    year: int = Field(..., description="Рік видання книги")

class Book:
    def __init__(self, book_data: BookModel):
        self._book = book_data

    def __str__(self) -> str:
        return f"Назва: {self._book.title}, Автор: {self._book.author}, Рік: {self._book.year}"

    @property
    def title(self) -> str:
        return self._book.title

    @property
    def author(self) -> str:
        return self._book.author

class JournalModel(BaseModel):
    title: str = Field(..., description="Назва журналу")
    publisher: str = Field(..., description="Видавництво журналу")
    issue: str = Field(..., description="Номер випуску журналу")

class Journal(Book):  # Спадкування від Book для поліморфізму в бібліотеці
    def __init__(self, journal_data: JournalModel):
        super().__init__(BookModel(title=journal_data.title, author="", year=0)) # Заповнюємо обов'язкові поля BookModel
        self._journal = journal_data

    def __str__(self) -> str:
        return f"Назва журналу: {self._journal.title}, Видавництво: {self._journal.publisher}, Випуск: {self._journal.issue}"

    @property
    def publisher(self) -> str:
        return self._journal.publisher

    @property
    def issue(self) -> str:
        return self._journal.issue

class LibraryItem(ABC):
    pass # Більше не вимагаємо абстрактний метод __str__, оскільки він реалізований в дочірніх класах Book та Journal

class BookWrapper(LibraryItem, Book):
    def __init__(self, book_data: BookModel):
        super().__init__(book_data)

class JournalWrapper(LibraryItem, Journal):
    def __init__(self, journal_data: JournalModel):
        super().__init__(journal_data)

def log_addition(func):
    @wraps(func)
    def wrapper(self, item: LibraryItem, *args, **kwargs):
        result = func(self, item, *args, **kwargs)
        logging.info(f"Додано до бібліотеки: {item}")
        return result
    return wrapper

def check_book_exists(func):
    @wraps(func)
    def wrapper(self, title: str, *args, **kwargs):
        for item in self._books:
            if isinstance(item, BookWrapper) and item.title == title:
                return func(self, title, *args, **kwargs)
            elif isinstance(item, JournalWrapper) and item._journal.title == title:
                return func(self, title, *args, **kwargs)
        print(f"Книгу/журнал з назвою '{title}' не знайдено в бібліотеці.")
        return None
    return wrapper

class Library:
    def __init__(self):
        self._books: List[LibraryItem] = []

    @log_addition
    def add_item(self, item: LibraryItem):
        self._books.append(item)

    def __iter__(self) -> Iterator[LibraryItem]:
        return iter(self._books)

    def get_books_by_author(self, author_name: str) -> Generator[LibraryItem, None, None]:
        for item in self._books:
            if isinstance(item, BookWrapper) and item.author == author_name:
                yield item
            elif isinstance(item, JournalWrapper) and item._journal.publisher == author_name: # Припустимо, що видавництво журналу можна вважати "автором" для пошуку
                yield item

    @check_book_exists
    def remove_book(self, title: str):
        self._books = [item for item in self._books if not (isinstance(item, BookWrapper) and item.title == title) and not (isinstance(item, JournalWrapper) and item._journal.title == title)]
        print(f"Книгу/журнал '{title}' видалено з бібліотеки.")

class LibraryFileManager:
    def __init__(self, filename: str):
        self.filename = filename

    def __enter__(self):
        self.file = open(self.filename, 'w+')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

    def save_books(self, library: Library):
        data = []
        for item in library:
            if isinstance(item, BookWrapper):
                data.append({"type": "book", "data": item._book.model_dump()})
            elif isinstance(item, JournalWrapper):
                data.append({"type": "journal", "data": item._journal.model_dump()})
        json.dump(data, self.file, indent=4, ensure_ascii=False)
        print(f"Список книг збережено до файлу '{self.filename}'")

    def load_books(self, library: Library):
        try:
            self.file.seek(0)
            data = json.load(self.file)
            for item_data in data:
                if item_data["type"] == "book":
                    book_model = BookModel(**item_data["data"])
                    library.add_item(BookWrapper(book_model))
                elif item_data["type"] == "journal":
                    journal_model = JournalModel(**item_data["data"])
                    library.add_item(JournalWrapper(journal_model))
            print(f"Список книг завантажено з файлу '{self.filename}'")
        except FileNotFoundError:
            print(f"Файл '{self.filename}' не знайдено. Створено новий.")
        except json.JSONDecodeError:
            print(f"Помилка декодування JSON у файлі '{self.filename}'.")

if __name__ == "__main__":
    # Створення бібліотеки
    my_library = Library()

    # Створення інстансів книги та журналу
    book1_data = BookModel(title="Маленький принц", author="Антуан де Сент-Екзюпері", year=1943)
    book1 = BookWrapper(book1_data)

    journal1_data = JournalModel(title="National Geographic", publisher="National Geographic Society", issue="Квітень 2025")
    journal1 = JournalWrapper(journal1_data)

    # Додавання їх у бібліотеку
    my_library.add_item(book1)
    my_library.add_item(journal1)

    # Виведення списку книг у бібліотеці
    print("\nСписок книг у бібліотеці:")
    for item in my_library:
        print(item)

    # Виведення списку книг бібліотеки по імені автора
    print("\nКниги автора Антуан де Сент-Екзюпері:")
    for book in my_library.get_books_by_author("Антуан де Сент-Екзюпері"):
        print(book)

    print("\nЖурнали видавництва National Geographic Society:")
    for journal in my_library.get_books_by_author("National Geographic Society"):
        print(journal)

    # Збереження списку книг у файл
    file_manager = LibraryFileManager("library_data.json")
    with file_manager:
        file_manager.save_books(my_library)

    # Видалення книги з бібліотеки
    my_library.remove_book("Маленький принц")

    # Виведення списку книг після видалення
    print("\nСписок книг у бібліотеці після видалення:")
    for item in my_library:
        print(item)

    # Додавання книг з файлу в бібліотеку
    new_library = Library()
    with file_manager:
        file_manager.load_books(new_library)

    # Виведення списку книг бібліотеки після додавання з файлу
    print("\nСписок книг у новій бібліотеці після завантаження з файлу:")
    for item in new_library:
        print(item)