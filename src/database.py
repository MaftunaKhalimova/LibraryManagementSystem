import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/library.db')

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  
    return conn

def initialize_db():
    """Creates the necessary tables if they do not exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Create Books Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'Available'
            )
        ''')
        
        # 2. Create Members Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                join_date TEXT DEFAULT CURRENT_DATE
            )
        ''')
        
        # 3. Create Borrowing Records Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowing_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                member_id INTEGER,
                issue_date TEXT DEFAULT CURRENT_DATE,
                return_date TEXT,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (member_id) REFERENCES members (member_id)
            )
        ''')
        
        conn.commit()