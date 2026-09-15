from agent.ingest.scrape_recommendations import (
    _parse_number,
    _parse_profile,
    parse_recommendations,
    save_recommendations,
)
from data import db

SAMPLE_HTML = """
<table class="table">
<tr><th>Profil</th><th>Rodzaj</th><th>Cena docelowa*</th><th>Kurs aktualny</th>
<th>CD/K**</th><th>Kurs z dnia wydania*</th><th>Data upublicznienia</th><th>Autor</th><th>Plik</th></tr>
<tr>
<td>MBR (MOBRUK)</td><td>akumuluj</td><td>462,00</td><td>388,50</td>
<td>+18,92%</td><td>390,00</td><td>2026-08-31 14:49</td>
<td>Dariusz Dadej, Michał Sztabler (Noble Securities)</td><td></td>
</tr>
<tr>
<td>XTB</td><td>akumuluj</td><td>151,70</td><td>179,70</td>
<td>-15,58%</td><td>135,94</td><td>2026-07-29 16:42</td>
<td>Mateusz Chrzanowski (Noble Securities)</td><td></td>
</tr>
<tr>
<td>SHO (SHOPER)</td><td>zawieszona</td><td>-</td><td>42,10</td>
<td>-</td><td>41,55</td><td>2026-07-21 00:00</td>
<td>Seweryn Żołyniak (DM Millennium)</td><td></td>
</tr>
</table>
"""


def test_parse_number():
    assert _parse_number("462,00") == 462.0
    assert _parse_number("1 117,00") == 1117.0
    assert _parse_number("+18,92%") == 18.92
    assert _parse_number("-15,58%") == -15.58
    assert _parse_number("-") is None
    assert _parse_number("") is None


def test_parse_profile():
    assert _parse_profile("MBR (MOBRUK)") == ("MBR", "MOBRUK")
    assert _parse_profile("XTB") == ("XTB", None)


def test_parse_recommendations():
    rows = parse_recommendations(SAMPLE_HTML, source_url="https://example.test/rekomendacje/")
    assert len(rows) == 3

    row = rows[0]
    assert row["ticker"] == "MBR"
    assert row["company_name"] == "MOBRUK"
    assert row["recommendation"] == "akumuluj"
    assert row["target_price"] == 462.0
    assert row["current_price"] == 388.5
    assert row["potential_pct"] == 18.92
    assert row["price_at_issue"] == 390.0
    assert row["published_at"] == "2026-08-31 14:49"
    assert row["author"] == "Dariusz Dadej, Michał Sztabler (Noble Securities)"

    row_no_company = rows[1]
    assert row_no_company["ticker"] == "XTB"
    assert row_no_company["company_name"] is None

    row_suspended = rows[2]
    assert row_suspended["target_price"] is None
    assert row_suspended["potential_pct"] is None


def test_save_recommendations_upsert(tmp_path, monkeypatch):
    db_path = tmp_path / "agpw.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    db.initialize_database(db_path)

    rows = parse_recommendations(SAMPLE_HTML, source_url="https://example.test/rekomendacje/")
    count = save_recommendations(rows)
    assert count == 3

    # Re-saving the same rows should upsert, not duplicate.
    save_recommendations(rows)

    conn = db.connect_db(db_path)
    total = conn.execute("SELECT COUNT(*) AS c FROM recommendations").fetchone()["c"]
    assert total == 3

    mbr = conn.execute(
        "SELECT recommendation, target_price FROM recommendations WHERE ticker = ?",
        ("MBR",),
    ).fetchone()
    assert mbr["recommendation"] == "akumuluj"
    assert abs(mbr["target_price"] - 462.0) < 1e-6
    conn.close()
