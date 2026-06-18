from src.database import get_connection
import sqlite3

def add_book(title, author, isbn):
    """Adds a new book to the database."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)",
                (title, author, isbn)
            )
            conn.commit()
            print(f"📚 Book '{title}' added successfully!")
            return True
    except sqlite3.IntegrityError:
        print(f"❌ Error: A book with ISBN {isbn} already exists.")
        return False

def get_all_books():
    """Retrieves and returns all books from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books")
        return cursor.fetchall()

def search_book_by_title(title):
    """Searches for books with a title matching or containing the query."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", (f"%{title}%",))
        return cursor.fetchall()

def update_book_status(book_id, status):
    """Updates the status of a book (e.g., 'Available', 'Borrowed')."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE books SET status = ? WHERE book_id = ?",
            (status, book_id)
        )
        conn.commit()

def delete_book(book_id):
    """Deletes a book from the database by its ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, status FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print(f"❌ Error: Book ID {book_id} does not exist.")
            return False
        if book['status'] == 'Borrowed':
            print(f"❌ Error: '{book['title']}' is currently borrowed and cannot be removed.")
            return False
        cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        conn.commit()
        print(f"🗑️ Book ID {book_id} removed from system.")
        return True