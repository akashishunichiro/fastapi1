from sqladmin import ModelView
from models import Book

class BookAdmin(ModelView, model=Book):
    column_list = [Book.id, Book.title, Book.author, Book.price]
    column_searchable_list = [Book.title, Book.author]
    column_sortable_list = [Book.id, Book.price]

    name = "Book"
    name_plural = "Books"
    icon = "fa-solid fa-book"
