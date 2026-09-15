import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "agpw.db")

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def list_tables(cur):
    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    return [row["name"] for row in cur.fetchall()]

def clear_table(cur, table):
    cur.execute(f"DELETE FROM {table};")

def count_rows(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    return cur.fetchone()[0]

def main():
    print(f"Używam bazy: {DB_PATH}")

    conn = connect_db()
    cur = conn.cursor()

    tables = list_tables(cur)

    print("\n=== Tabele w bazie ===")
    for t in tables:
        print("-", t)

    print("\n=== Czyszczenie danych ===")
    for t in tables:
        clear_table(cur, t)
        print(f"Wyczyszczono: {t}")

    conn.commit()

    print("\n=== Liczba rekordów po czyszczeniu ===")
    for t in tables:
        print(f"{t}: {count_rows(cur, t)} rekordów")

    conn.close()

if __name__ == "__main__":
    main()
