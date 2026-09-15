import pathlib
import sys

# Ensure workspace root is on sys.path for imports
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from data.db import connect_db

if __name__ == "__main__":
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT isin, date, COUNT(*) as c FROM stocks_daily GROUP BY isin, date HAVING c>1")
    dups = cur.fetchall()
    print(f"Found duplicate groups: {len(dups)}")
    for r in dups[:50]:
        print(r[0], r[1], r[2])

    if dups:
        print("Removing duplicates, keeping the row with the highest id for each (isin,date)")
        cur.execute(
            "DELETE FROM stocks_daily WHERE id NOT IN (SELECT MAX(id) FROM stocks_daily GROUP BY isin, date)"
        )
        conn.commit()
        cur.execute("SELECT isin, date, COUNT(*) as c FROM stocks_daily GROUP BY isin, date HAVING c>1")
        remaining = cur.fetchall()
        print(f"Remaining duplicate groups after cleanup: {len(remaining)}")

    try:
        cur.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS ux_stocks_daily_isin_date ON stocks_daily(isin, date);"
        )
        conn.commit()
        print("Unique index created or already exists.")
    except Exception as e:
        print("Failed to create unique index:", e)
    finally:
        conn.close()
