import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

from src.database import initialize_db
from src.books import add_book, get_all_books, search_book_by_title, delete_book
from src.members import add_member, get_all_members
from src.borrowing import borrow_book, return_book, list_active_borrows


def print_menu():
    print("\n" + "="*40)
    print("      📚 LIBRARY MANAGEMENT SYSTEM      ")
    print("="*40)
    print("1. Add a New Book")
    print("2. View All Books")
    print("3. Search Book by Title")
    print("4. Register a New Member")
    print("5. View All Members")
    print("6. Borrow a Book")
    print("7. Return a Book")
    print("8. Remove a Book")
    print("9. View Active Borrows")
    print("0. Exit Application")
    print("="*40)


def main():
    initialize_db()

    while True:
        print_menu()
        choice = input("Select an option (0-9): ").strip()

        if choice == '1':
            print("\n--- Add a New Book ---")
            title  = input("Enter book title: ").strip()
            author = input("Enter author: ").strip()
            isbn   = input("Enter ISBN: ").strip()
            if title and author and isbn:
                add_book(title, author, isbn)
            else:
                print("❌ Error: All fields are required.")

        elif choice == '2':
            print("\n--- Library Inventory ---")
            books = get_all_books()
            if not books:
                print("No books found in inventory.")
            else:
                for b in books:
                    print(f"ID: {b['book_id']} | '{b['title']}' by {b['author']} | ISBN: {b['isbn']} | Status: {b['status']}")

        elif choice == '3':
            print("\n--- Search Inventory ---")
            query = input("Enter title keyword to search: ").strip()
            if not query:
                print("❌ Error: Search keyword cannot be empty.")
            else:
                books = search_book_by_title(query)
                if not books:
                    print("No matching books found.")
                else:
                    for b in books:
                        print(f"ID: {b['book_id']} | '{b['title']}' by {b['author']} | Status: {b['status']}")

        elif choice == '4':
            print("\n--- Register a New Member ---")
            name  = input("Enter member name: ").strip()
            email = input("Enter member email: ").strip()
            if name and email:
                add_member(name, email)
            else:
                print("❌ Error: All fields are required.")

        elif choice == '5':
            print("\n--- Registered Members ---")
            members = get_all_members()
            if not members:
                print("No registered members found.")
            else:
                for m in members:
                    print(f"ID: {m['member_id']} | Name: {m['name']} | Email: {m['email']} | Joined: {m['join_date']}")

        elif choice == '6':
            print("\n--- Book Checkout ---")
            try:
                b_id = int(input("Enter Book ID to borrow: "))
                m_id = int(input("Enter Member ID: "))
                borrow_book(b_id, m_id)
            except ValueError:
                print("❌ Error: IDs must be numeric values.")

        elif choice == '7':
            print("\n--- Book Return ---")
            try:
                b_id = int(input("Enter Book ID being returned: "))
                return_book(b_id)
            except ValueError:
                print("❌ Error: ID must be a numeric value.")

        elif choice == '8':
            print("\n--- Remove Book From Inventory ---")
            try:
                b_id = int(input("Enter Book ID to delete: "))
                delete_book(b_id)
            except ValueError:
                print("❌ Error: ID must be a numeric value.")

        elif choice == '9':
            print("\n--- Active Borrows ---")
            borrows = list_active_borrows()
            if not borrows:
                print("No books are currently borrowed.")
            else:
                for br in borrows:
                    print(f"Book ID: {br['book_id']} | '{br['title']}' by {br['author']}"
                          f" → Member ID: {br['member_id']} | {br['member_name']} | Since: {br['issue_date']}")

        elif choice == '0':
            print("\nThank you for using the Library Management System. Goodbye!")
            sys.exit()

        else:
            print("❌ Invalid selection. Please choose an option between 0 and 9.")


if __name__ == "__main__":
    main()
