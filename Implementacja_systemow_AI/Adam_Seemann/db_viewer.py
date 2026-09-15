import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "agpw.db")

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_tables(cur):
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    return [row["name"] for row in cur.fetchall()]

def count_rows(cur, table):
    cur.execute(f"SELECT COUNT(*) FROM {table};")
    return cur.fetchone()[0]

def preview_table(cur, table, limit=10):
    cur.execute(f"SELECT * FROM {table} LIMIT {limit};")
    return [dict(row) for row in cur.fetchall()]

def date_range(cur, table):
    try:
        cur.execute(f"SELECT MIN(date), MAX(date) FROM {table};")
        return cur.fetchone()
    except sqlite3.Error:
        return None, None

def unique_isin(cur, table):
    try:
        cur.execute(f"SELECT DISTINCT isin FROM {table};")
        return [row[0] for row in cur.fetchall()]
    except sqlite3.Error:
        return []

def main():
    print(f"Używam bazy: {DB_PATH}")

    conn = connect()
    cur = conn.cursor()

    tables = get_tables(cur)

    print("\n=== Tabele w bazie ===")
    for t in tables:
        print("-", t)

    print("\n=== Podstawowe zestawienie ===")
    for t in tables:
        print(f"\n--- {t} ---")

        # liczba rekordów
        rows = count_rows(cur, t)
        print(f"Rekordów: {rows}")

        # zakres dat
        min_date, max_date = date_range(cur, t)
        if min_date is not None:
            print(f"Zakres dat: od {min_date} do {max_date}")

        # unikalne ISIN
        isins = unique_isin(cur, t)
        if isins:
            print(f"Unikalne ISIN ({len(isins)}):")
            for i in isins[:10]:  # tylko pierwsze 10
                print(" -", i)

        # podgląd pierwszych rekordów
        preview = preview_table(cur, t, limit=10)
        print("\nPierwsze rekordy:")
        for row in preview:
            print(row)

    conn.close()

if __name__ == "__main__":
    main()
