# 📚 Library Management System

A command-line application for managing a library's books, members, and borrowing records. Built with Python and SQLite.

---

## Features

| # | Feature |
|---|---------|
| 1 | Add a new book |
| 2 | View all books in inventory |
| 3 | Search books by title keyword |
| 4 | Register a new member |
| 5 | View all registered members |
| 6 | Borrow a book |
| 7 | Return a book |
| 8 | Remove a book from inventory |
| 9 | View all active (unreturned) borrows |

---

## Project Structure

```
LibraryManagementSystem/
│
├── main.py                  # Entry point — runs the interactive menu
│
├── src/
│   ├── __init__.py
│   ├── database.py          # DB connection and table initialisation
│   ├── books.py             # Book CRUD operations
│   ├── members.py           # Member CRUD operations
│   └── borrowing.py         # Borrow / return / list active borrows
│
├── tests/
│   ├── __init__.py
│   └── test_library.py      # Full unit test suite (48 tests)
│
├── data/
│   └── library.db           # SQLite database (auto-created on first run)
│
└── README.md
```

---

## Requirements

- Python 3.7 or higher
- No third-party packages required — uses the Python standard library only

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/LibraryManagementSystem.git
cd LibraryManagementSystem
```

### 2. Run the application

```bash
python main.py
```

The database file (`data/library.db`) is created automatically on the first run.

---

## Usage

When you start the application you will see an interactive menu:

```
========================================
       LIBRARY MANAGEMENT SYSTEM
========================================
1. Add a New Book
2. View All Books
3. Search Book by Title
4. Register a New Member
5. View All Members
6. Borrow a Book
7. Return a Book
8. Remove a Book
9. View Active Borrows
0. Exit Application
========================================
Select an option (0-9):
```

Type the number of the action you want and press **Enter**.

### Example workflow

```
# Add a book
Select an option (0-9): 1
Enter book title: The Pragmatic Programmer
Enter author: Andrew Hunt
Enter ISBN: 978-0201616224
 Book 'The Pragmatic Programmer' added successfully!

# Register a member
Select an option (0-9): 4
Enter member name: Alice
Enter member email: alice@example.com
 Member 'Alice' registered successfully!

# Borrow the book
Select an option (0-9): 6
Enter Book ID to borrow: 1
Enter Member ID: 1
 Success: 'The Pragmatic Programmer' has been checked out to Alice.

# View active borrows
Select an option (0-9): 9
--- Active Borrows ---
Book ID: 1 | 'The Pragmatic Programmer' by Andrew Hunt → Member ID: 1 | Alice | Since: 2026-06-18

# Return the book
Select an option (0-9): 7
Enter Book ID being returned: 1
 Success: Book ID 1 has been successfully returned.
```

---

## Database Schema

### `books`
| Column | Type | Description |
|--------|------|-------------|
| `book_id` | INTEGER PK | Auto-incremented ID |
| `title` | TEXT | Book title |
| `author` | TEXT | Author name |
| `isbn` | TEXT UNIQUE | ISBN (must be unique) |
| `status` | TEXT | `Available` or `Borrowed` |

### `members`
| Column | Type | Description |
|--------|------|-------------|
| `member_id` | INTEGER PK | Auto-incremented ID |
| `name` | TEXT | Member's full name |
| `email` | TEXT UNIQUE | Email address (must be unique) |
| `join_date` | TEXT | Date of registration |

### `borrowing_records`
| Column | Type | Description |
|--------|------|-------------|
| `record_id` | INTEGER PK | Auto-incremented ID |
| `book_id` | INTEGER FK | References `books.book_id` |
| `member_id` | INTEGER FK | References `members.member_id` |
| `issue_date` | TEXT | Date the book was borrowed |
| `return_date` | TEXT | Date returned (`NULL` if still out) |

---

## Running the Tests

The test suite uses Python's built-in `unittest` module — no extra packages needed.

```bash
python -m unittest tests/test_library.py -v
```

**48 tests** cover all modules across four test classes:

| Test class | Coverage |
|---|---|
| `TestInitializeDb` | Database setup |
| `TestBooks` | Add, view, search, update status, delete |
| `TestMembers` | Add, view, search, delete (including borrow guards) |
| `TestBorrowing` | Borrow, return, active borrows list, full cycle |

Each test runs against an isolated **in-memory SQLite database** — the production database is never touched during testing.

---

## Business Rules

- A book cannot be borrowed if its status is already `Borrowed`.
- A book cannot be deleted while it is borrowed.
- A member cannot be deleted while they have books checked out.
- Duplicate ISBNs and duplicate member email addresses are rejected.
- Borrowing and returning a book are **atomic** — both the borrowing record and the book status update happen in a single database transaction.
