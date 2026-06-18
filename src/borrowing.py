from src.database import get_connection


def borrow_book(book_id, member_id):
    """Issues a book to a member if it is currently available."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT title, status FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        if not book:
            print(f"❌ Error: Book ID {book_id} does not exist.")
            return False
        if book['status'] != 'Available':
            print(f"❌ Error: '{book['title']}' is currently already borrowed.")
            return False

        cursor.execute("SELECT name FROM members WHERE member_id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            print(f"❌ Error: Member ID {member_id} does not exist.")
            return False

        cursor.execute(
            "INSERT INTO borrowing_records (book_id, member_id) VALUES (?, ?)",
            (book_id, member_id)
        )
        cursor.execute(
            "UPDATE books SET status = 'Borrowed' WHERE book_id = ?",
            (book_id,)
        )
        conn.commit()

    print(f"✅ Success: '{book['title']}' has been checked out to {member['name']}.")
    return True


def return_book(book_id):
    """Handles returning a book and making it available again."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT record_id FROM borrowing_records WHERE book_id = ? AND return_date IS NULL",
            (book_id,)
        )
        record = cursor.fetchone()
        if not record:
            print(f"❌ Error: No active borrowing record found for Book ID {book_id}.")
            return False

        cursor.execute(
            "UPDATE borrowing_records SET return_date = CURRENT_DATE WHERE record_id = ?",
            (record['record_id'],)
        )
        cursor.execute(
            "UPDATE books SET status = 'Available' WHERE book_id = ?",
            (book_id,)
        )
        conn.commit()

    print(f"🔄 Success: Book ID {book_id} has been successfully returned.")
    return True


def list_active_borrows():
    """Returns all books that are currently borrowed, with borrower details."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.book_id, b.title, b.author,
                   m.member_id, m.name AS member_name,
                   br.issue_date
            FROM borrowing_records br
            JOIN books   b ON br.book_id   = b.book_id
            JOIN members m ON br.member_id = m.member_id
            WHERE br.return_date IS NULL
            ORDER BY br.issue_date
        """)
        return cursor.fetchall()
