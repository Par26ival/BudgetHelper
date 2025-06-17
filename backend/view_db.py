import sqlite3
from tabulate import tabulate
import os


def view_db():
    try:
        # Connect to the database
        db_path = os.path.join("instance", "transactions.db")
        print(f"Attempting to open database at: {os.path.abspath(db_path)}")

        if not os.path.exists(db_path):
            print(f"Error: Database file not found at {db_path}")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("No tables found in the database.")
            return

        print("\n=== Database Structure ===")
        for table in tables:
            table_name = table[0]
            print(f"\n=== Table: {table_name} ===")

            try:
                # Get column information
                cursor.execute(f'PRAGMA table_info("{table_name}");')
                columns = cursor.fetchall()
                print("\nColumns:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")

                # Get row count
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}";')
                count = cursor.fetchone()[0]
                print(f"\nTotal rows: {count}")

                # Get sample data (up to 5 rows)
                cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 5;')
                rows = cursor.fetchall()

                if rows:
                    print("\nSample data:")
                    # Get column names for headers
                    headers = [col[1] for col in columns]
                    print(tabulate(rows, headers=headers, tablefmt="grid"))
                else:
                    print("\nNo data in table")

            except sqlite3.Error as e:
                print(f"Error accessing table {table_name}: {str(e)}")

    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if "conn" in locals():
            conn.close()


if __name__ == "__main__":
    view_db()
