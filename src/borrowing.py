from src.database import get_connection
from src.books import update_book_status
import sqlite3

def borrow_book(book_id, member_id):
    """Issues a book to a member if it's currently available."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Check if the book exists and is available
        cursor.execute("SELECT status, title FROM books WHERE book_id = ?", (book_id,))
        book = cursor.fetchone()
        
        if not book:
            print(f"❌ Error: Book ID {book_id} does not exist.")
            return False
        
        if book['status'] != 'Available':
            print(f"❌ Error: '{book['title']}' is currently already borrowed.")
            return False
            
        # 2. Check if the member exists
        cursor.execute("SELECT name FROM members WHERE member_id = ?", (member_id,))
        member = cursor.fetchone()
        if not member:
            print(f"❌ Error: Member ID {member_id} does not exist.")
            return False
        
        # 3. Create the borrowing transaction record
        cursor.execute(
            "INSERT INTO borrowing_records (book_id, member_id) VALUES (?, ?)",
            (book_id, member_id)
        )
        conn.commit()
        
    # 4. Update the book's availability status using our existing book module function
    update_book_status(book_id, 'Borrowed')
    print(f"✅ Success: '{book['title']}' has been checked out to {member['name']}.")
    return True

def return_book(book_id):
    """Handles returning a book and making it available again."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Find the active borrowing transaction (where return_date is still null)
        cursor.execute(
            """SELECT record_id FROM borrowing_records 
               WHERE book_id = ? AND return_date IS NULL""", 
            (book_id,)
        )
        record = cursor.fetchone()
        
        if not record:
            print(f"❌ Error: No active borrowing record found for Book ID {book_id}.")
            return False
            
        # Update the record with the current date as the return date
        cursor.execute(
            "UPDATE borrowing_records SET return_date = CURRENT_DATE WHERE record_id = ?",
            (record['record_id'],)
        )
        conn.commit()
        
    # Update the book status back to Available
    update_book_status(book_id, 'Available')
    print(f"🔄 Success: Book ID {book_id} has been successfully returned.")
    return True