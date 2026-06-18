from src.database import get_connection
import sqlite3

def add_member(name, email):
    """Registers a new library member."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO members (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            print(f"👤 Member '{name}' registered successfully!")
            return True
    except sqlite3.IntegrityError:
        print(f"❌ Error: A member with email '{email}' is already registered.")
        return False

def get_all_members():
    """Retrieves all registered members."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members")
        return cursor.fetchall()

def search_member_by_name(name):
    """Searches for members by name."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE name LIKE ?", (f"%{name}%",))
        return cursor.fetchall()

def delete_member(member_id):
    """Removes a member from the database."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE member_id = ?", (member_id,))
        conn.commit()
        print(f"🗑️ Member ID {member_id} removed from system.")