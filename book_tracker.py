import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

DATA_FILE = "books.json"


class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker - Трекер прочитанных книг")
        self.root.geometry("850x600")
        self.root.resizable(True, True)

        self.books = []
        self.load_data()

        self.create_widgets()
        self.refresh_table()

    def create_widgets(self):
        # ===== Фрейм ввода данных =====
        input_frame = ttk.LabelFrame(self.root, text="Добавить книгу", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Название
        ttk.Label(input_frame, text="Название:").grid(row=0, column=0, sticky="w", pady=2)
        self.title_entry = ttk.Entry(input_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Автор
        ttk.Label(input_frame, text="Автор:").grid(row=1, column=0, sticky="w", pady=2)
        self.author_entry = ttk.Entry(input_frame, width=40)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        # Жанр
        ttk.Label(input_frame, text="Жанр:").grid(row=2, column=0, sticky="w", pady=2)
        self.genre_entry = ttk.Entry(input_frame, width=40)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        # Количество страниц
        ttk.Label(input_frame, text="Страниц:").grid(row=3, column=0, sticky="w", pady=2)
        self.pages_entry = ttk.Entry(input_frame, width=40)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # Кнопка "Добавить"
        self.add_button = ttk.Button(input_frame, text="Добавить книгу", command=self.add_book)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # ===== Фрейм фильтрации =====
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по жанру
        ttk.Label(filter_frame, text="По жанру:").grid(row=0, column=0, sticky="w", pady=2)
        self.filter_genre = ttk.Combobox(filter_frame, width=30)
        self.filter_genre.grid(row=0, column=1, padx=5, pady=2, sticky="w")
        self.filter_genre.bind("<<ComboboxSelected>>", self.apply_filters)

        # Фильтр по страницам
        ttk.Label(filter_frame, text="Страниц больше:").grid(row=0, column=2, sticky="w", pady=2)
        self.filter_pages = ttk.Entry(filter_frame, width=15)
        self.filter_pages.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        # Кнопки фильтрации
        self.apply_filter_button = ttk.Button(filter_frame, text="Применить", command=self.apply_filters)
        self.apply_filter_button.grid(row=0, column=4, padx=5, pady=2)

        self.reset_filter_button = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters)
        self.reset_filter_button.grid(row=0, column=5, padx=5, pady=2)

        # ===== Таблица книг =====
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")

        self.tree.column("title", width=250)
        self.tree.column("author", width=200)
        self.tree.column("genre", width=150)
        self.tree.column("pages", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== Контекстное меню =====
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Удалить книгу", command=self.delete_book)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Показать контекстное меню по правому клику"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def add_book(self):
        """Добавление новой книги в список"""
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages = self.pages_entry.get().strip()

        # Проверка на пустые поля
        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return

        # Проверка, что страницы — число
        try:
            pages = int(pages)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом!")
            return

        # Добавление книги
        book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(book)
        self.save_data()
        self.refresh_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", f"Книга «{title}» добавлена!")

    def delete_book(self):
        """Удаление выбранной книги"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return

        item = self.tree.item(selected[0])
        title = item['values'][0]

        if messagebox.askyesno("Подтверждение", f"Удалить книгу «{title}»?"):
            self.books = [b for b in self.books if b["title"] != title]
            self.save_data()
            self.refresh_table()

    def apply_filters(self, event=None):
        """Применение фильтров"""
        genre_filter = self.filter_genre.get().strip()
        pages_filter = self.filter_pages.get().strip()

        filtered_books = self.books.copy()

        # Фильтрация по жанру
        if genre_filter:
            filtered_books = [b for b in filtered_books if b["genre"].lower() == genre_filter.lower()]

        # Фильтрация по количеству страниц
        if pages_filter:
            try:
                pages_min = int(pages_filter)
                filtered_books = [b for b in filtered_books if b["pages"] > pages_min]
            except ValueError:
                messagebox.showerror("Ошибка", "Введите число для фильтра по страницам!")
                return

        self.refresh_table(filtered_books)

    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_genre.set("")
        self.filter_pages.delete(0, tk.END)
        self.refresh_table()

    def refresh_table(self, data=None):
        """Обновление таблицы"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        books_to_show = data if data is not None else self.books

        for book in books_to_show:
            self.tree.insert("", "end", values=(
                book["title"],
                book["author"],
                book["genre"],
                book["pages"]
            ))

        # Обновление списка жанров в фильтре
        genres = sorted(set(b["genre"] for b in self.books))
        self.filter_genre['values'] = genres

    def clear_inputs(self):
        """Очистка полей ввода"""
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def save_data(self):
        """Сохранение данных в JSON"""
        os.makedirs(os.path.dirname(DATA_FILE) if os.path.dirname(DATA_FILE) else ".", exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.books, f, ensure_ascii=False, indent=4)

    def load_data(self):
        """Загрузка данных из JSON"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.books = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.books = []


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()