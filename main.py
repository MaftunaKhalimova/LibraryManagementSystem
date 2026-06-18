from src.database import initialize_db
from src.books import add_book, get_all_books

def main():
    print("--- Initializing Library System ---")
    # Step 1: Ensure tables exist
    initialize_db()
    
    print("\n--- Testing Book Actions ---")
    # Step 2: Try adding a test book
    add_book("The Pragmatic Programmer", "Andrew Hunt", "978-0201616224")
    add_book("Clean Code", "Robert C. Martin", "978-0132350884")
    
    # Step 3: Fetch and print all books to verify
    print("\n--- Current Library Inventory ---")
    books = get_all_books()
    for book in books:
        print(f"[{book['book_id']}] {book['title']} by {book['author']} | Status: {book['status']}")

if __name__ == "__main__":
    main()