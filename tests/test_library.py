import unittest
import sqlite3
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from src.books import add_book, get_all_books, search_book_by_title, update_book_status, delete_book
from src.members import add_member, get_all_members, search_member_by_name, delete_member
from src.borrowing import borrow_book, return_book, list_active_borrows
from src.database import initialize_db


def make_test_db():
    """Creates a fresh in-memory SQLite database with all required tables."""
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.executescript('''
        CREATE TABLE books (
            book_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT NOT NULL,
            author    TEXT NOT NULL,
            isbn      TEXT UNIQUE NOT NULL,
            status    TEXT DEFAULT 'Available'
        );
        CREATE TABLE members (
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            join_date TEXT DEFAULT CURRENT_DATE
        );
        CREATE TABLE borrowing_records (
            record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id     INTEGER,
            member_id   INTEGER,
            issue_date  TEXT DEFAULT CURRENT_DATE,
            return_date TEXT,
            FOREIGN KEY (book_id)   REFERENCES books   (book_id),
            FOREIGN KEY (member_id) REFERENCES members (member_id)
        );
    ''')
    return conn


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

class TestInitializeDb(unittest.TestCase):

    def test_initialize_db_creates_tables(self):
        """initialize_db should create all three tables without raising."""
        with patch('src.database.get_connection') as mock_get_conn:
            mock_get_conn.return_value = make_test_db()
            initialize_db()


# ---------------------------------------------------------------------------
# Books
# ---------------------------------------------------------------------------

class TestBooks(unittest.TestCase):

    def setUp(self):
        self.conn = make_test_db()
        self.patcher = patch('src.books.get_connection', return_value=self.conn)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.conn.close()

    # --- add_book ---

    def test_add_book_returns_true_on_success(self):
        self.assertTrue(add_book('Clean Code', 'Robert Martin', 'ISBN-001'))

    def test_add_book_persists_record(self):
        add_book('Clean Code', 'Robert Martin', 'ISBN-001')
        books = get_all_books()
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]['title'], 'Clean Code')
        self.assertEqual(books[0]['author'], 'Robert Martin')
        self.assertEqual(books[0]['status'], 'Available')

    def test_add_book_duplicate_isbn_returns_false(self):
        add_book('Book A', 'Author A', 'ISBN-DUP')
        self.assertFalse(add_book('Book B', 'Author B', 'ISBN-DUP'))

    def test_add_book_duplicate_isbn_does_not_insert(self):
        add_book('Book A', 'Author A', 'ISBN-DUP')
        add_book('Book B', 'Author B', 'ISBN-DUP')
        self.assertEqual(len(get_all_books()), 1)

    # --- get_all_books ---

    def test_get_all_books_empty_database(self):
        self.assertEqual(get_all_books(), [])

    def test_get_all_books_returns_all(self):
        add_book('Book 1', 'Author', 'ISBN-1')
        add_book('Book 2', 'Author', 'ISBN-2')
        self.assertEqual(len(get_all_books()), 2)

    # --- search_book_by_title ---

    def test_search_exact_title_match(self):
        add_book('Python Programming', 'Author', 'ISBN-PY')
        self.assertEqual(len(search_book_by_title('Python Programming')), 1)

    def test_search_partial_title_match(self):
        add_book('Python Programming', 'Author', 'ISBN-PY1')
        add_book('Python Basics', 'Author', 'ISBN-PY2')
        self.assertEqual(len(search_book_by_title('Python')), 2)

    def test_search_case_insensitive(self):
        add_book('Python Programming', 'Author', 'ISBN-PY')
        self.assertEqual(len(search_book_by_title('python')), 1)

    def test_search_no_match_returns_empty(self):
        add_book('Python Programming', 'Author', 'ISBN-PY')
        self.assertEqual(search_book_by_title('Java'), [])

    # --- update_book_status ---

    def test_update_book_status_to_borrowed(self):
        add_book('Test Book', 'Author', 'ISBN-T')
        book_id = get_all_books()[0]['book_id']
        update_book_status(book_id, 'Borrowed')
        self.assertEqual(get_all_books()[0]['status'], 'Borrowed')

    def test_update_book_status_back_to_available(self):
        add_book('Test Book', 'Author', 'ISBN-T')
        book_id = get_all_books()[0]['book_id']
        update_book_status(book_id, 'Borrowed')
        update_book_status(book_id, 'Available')
        self.assertEqual(get_all_books()[0]['status'], 'Available')

    # --- delete_book ---

    def test_delete_book_success(self):
        add_book('To Delete', 'Author', 'ISBN-DEL')
        book_id = get_all_books()[0]['book_id']
        self.assertTrue(delete_book(book_id))
        self.assertEqual(get_all_books(), [])

    def test_delete_nonexistent_book_returns_false(self):
        self.assertFalse(delete_book(9999))

    def test_delete_borrowed_book_returns_false(self):
        add_book('Borrowed Book', 'Author', 'ISBN-BOR')
        book_id = get_all_books()[0]['book_id']
        update_book_status(book_id, 'Borrowed')
        self.assertFalse(delete_book(book_id))

    def test_delete_borrowed_book_leaves_record_intact(self):
        add_book('Borrowed Book', 'Author', 'ISBN-BOR')
        book_id = get_all_books()[0]['book_id']
        update_book_status(book_id, 'Borrowed')
        delete_book(book_id)
        self.assertEqual(len(get_all_books()), 1)


# ---------------------------------------------------------------------------
# Members
# ---------------------------------------------------------------------------

class TestMembers(unittest.TestCase):

    def setUp(self):
        self.conn = make_test_db()
        self.patcher = patch('src.members.get_connection', return_value=self.conn)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.conn.close()

    # --- add_member ---

    def test_add_member_returns_true_on_success(self):
        self.assertTrue(add_member('Alice', 'alice@example.com'))

    def test_add_member_persists_record(self):
        add_member('Alice', 'alice@example.com')
        members = get_all_members()
        self.assertEqual(len(members), 1)
        self.assertEqual(members[0]['name'], 'Alice')
        self.assertEqual(members[0]['email'], 'alice@example.com')

    def test_add_member_duplicate_email_returns_false(self):
        add_member('Alice', 'alice@example.com')
        self.assertFalse(add_member('Alice 2', 'alice@example.com'))

    def test_add_member_duplicate_email_does_not_insert(self):
        add_member('Alice', 'alice@example.com')
        add_member('Alice 2', 'alice@example.com')
        self.assertEqual(len(get_all_members()), 1)

    # --- get_all_members ---

    def test_get_all_members_empty_database(self):
        self.assertEqual(get_all_members(), [])

    def test_get_all_members_returns_all(self):
        add_member('Alice', 'alice@example.com')
        add_member('Bob', 'bob@example.com')
        self.assertEqual(len(get_all_members()), 2)

    # --- search_member_by_name ---

    def test_search_member_exact_match(self):
        add_member('Alice Smith', 'alice@example.com')
        add_member('Bob Jones', 'bob@example.com')
        results = search_member_by_name('Alice Smith')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'Alice Smith')

    def test_search_member_partial_match(self):
        add_member('Alice Smith', 'alice@example.com')
        add_member('Alice Walker', 'awalker@example.com')
        self.assertEqual(len(search_member_by_name('Alice')), 2)

    def test_search_member_no_match(self):
        add_member('Alice', 'alice@example.com')
        self.assertEqual(search_member_by_name('Charlie'), [])

    # --- delete_member ---

    def test_delete_member_removes_record(self):
        add_member('Alice', 'alice@example.com')
        member_id = get_all_members()[0]['member_id']
        self.assertTrue(delete_member(member_id))
        self.assertEqual(get_all_members(), [])

    def test_delete_nonexistent_member_returns_false(self):
        self.assertFalse(delete_member(9999))

    def test_delete_member_with_active_borrow_returns_false(self):
        add_member('Alice', 'alice@example.com')
        member_id = get_all_members()[0]['member_id']
        self.conn.execute(
            "INSERT INTO borrowing_records (book_id, member_id) VALUES (1, ?)", (member_id,)
        )
        self.conn.commit()
        self.assertFalse(delete_member(member_id))

    def test_delete_member_with_active_borrow_keeps_record(self):
        add_member('Alice', 'alice@example.com')
        member_id = get_all_members()[0]['member_id']
        self.conn.execute(
            "INSERT INTO borrowing_records (book_id, member_id) VALUES (1, ?)", (member_id,)
        )
        self.conn.commit()
        delete_member(member_id)
        self.assertEqual(len(get_all_members()), 1)

    def test_delete_member_allowed_after_all_books_returned(self):
        add_member('Alice', 'alice@example.com')
        member_id = get_all_members()[0]['member_id']
        self.conn.execute(
            "INSERT INTO borrowing_records (book_id, member_id, return_date) VALUES (1, ?, CURRENT_DATE)",
            (member_id,)
        )
        self.conn.commit()
        self.assertTrue(delete_member(member_id))


# ---------------------------------------------------------------------------
# Borrowing
# ---------------------------------------------------------------------------

class TestBorrowing(unittest.TestCase):

    def setUp(self):
        self.conn = make_test_db()
        self.p_books     = patch('src.books.get_connection',     return_value=self.conn)
        self.p_members   = patch('src.members.get_connection',   return_value=self.conn)
        self.p_borrowing = patch('src.borrowing.get_connection', return_value=self.conn)
        self.p_books.start()
        self.p_members.start()
        self.p_borrowing.start()

        add_book('Test Book', 'Test Author', 'ISBN-T1')
        add_member('Test Member', 'member@example.com')
        self.book_id   = get_all_books()[0]['book_id']
        self.member_id = get_all_members()[0]['member_id']

    def tearDown(self):
        self.p_books.stop()
        self.p_members.stop()
        self.p_borrowing.stop()
        self.conn.close()

    # --- borrow_book ---

    def test_borrow_book_returns_true(self):
        self.assertTrue(borrow_book(self.book_id, self.member_id))

    def test_borrow_book_sets_status_to_borrowed(self):
        borrow_book(self.book_id, self.member_id)
        self.assertEqual(get_all_books()[0]['status'], 'Borrowed')

    def test_borrow_book_creates_record(self):
        borrow_book(self.book_id, self.member_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM borrowing_records WHERE book_id = ? AND return_date IS NULL",
            (self.book_id,)
        )
        self.assertEqual(cursor.fetchone()['cnt'], 1)

    def test_borrow_nonexistent_book_returns_false(self):
        self.assertFalse(borrow_book(9999, self.member_id))

    def test_borrow_nonexistent_member_returns_false(self):
        self.assertFalse(borrow_book(self.book_id, 9999))

    def test_borrow_already_borrowed_book_returns_false(self):
        borrow_book(self.book_id, self.member_id)
        self.assertFalse(borrow_book(self.book_id, self.member_id))

    def test_borrow_already_borrowed_does_not_create_extra_record(self):
        borrow_book(self.book_id, self.member_id)
        borrow_book(self.book_id, self.member_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS cnt FROM borrowing_records WHERE book_id = ?",
            (self.book_id,)
        )
        self.assertEqual(cursor.fetchone()['cnt'], 1)

    # --- return_book ---

    def test_return_book_returns_true(self):
        borrow_book(self.book_id, self.member_id)
        self.assertTrue(return_book(self.book_id))

    def test_return_book_sets_status_to_available(self):
        borrow_book(self.book_id, self.member_id)
        return_book(self.book_id)
        self.assertEqual(get_all_books()[0]['status'], 'Available')

    def test_return_book_sets_return_date_on_record(self):
        borrow_book(self.book_id, self.member_id)
        return_book(self.book_id)
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT return_date FROM borrowing_records WHERE book_id = ?",
            (self.book_id,)
        )
        self.assertIsNotNone(cursor.fetchone()['return_date'])

    def test_return_book_not_borrowed_returns_false(self):
        self.assertFalse(return_book(self.book_id))

    def test_return_book_twice_returns_false_second_time(self):
        borrow_book(self.book_id, self.member_id)
        return_book(self.book_id)
        self.assertFalse(return_book(self.book_id))

    def test_full_borrow_return_cycle(self):
        """A book can be borrowed again after it has been returned."""
        borrow_book(self.book_id, self.member_id)
        return_book(self.book_id)
        self.assertTrue(borrow_book(self.book_id, self.member_id))
        self.assertEqual(get_all_books()[0]['status'], 'Borrowed')

    # --- list_active_borrows ---

    def test_list_active_borrows_empty_when_none_borrowed(self):
        self.assertEqual(list_active_borrows(), [])

    def test_list_active_borrows_shows_current_borrow(self):
        borrow_book(self.book_id, self.member_id)
        borrows = list_active_borrows()
        self.assertEqual(len(borrows), 1)
        self.assertEqual(borrows[0]['book_id'], self.book_id)
        self.assertEqual(borrows[0]['member_id'], self.member_id)

    def test_list_active_borrows_excludes_returned_books(self):
        borrow_book(self.book_id, self.member_id)
        return_book(self.book_id)
        self.assertEqual(list_active_borrows(), [])

    def test_list_active_borrows_includes_correct_fields(self):
        borrow_book(self.book_id, self.member_id)
        br = list_active_borrows()[0]
        self.assertEqual(br['title'], 'Test Book')
        self.assertEqual(br['author'], 'Test Author')
        self.assertEqual(br['member_name'], 'Test Member')
        self.assertIsNotNone(br['issue_date'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
