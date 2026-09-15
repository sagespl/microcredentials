from agent.ingest.ingest_financial_report import split_document
from data import db


def test_split_document_respects_limit_and_preserves_text():
    document = "first section\nsecond section\n" + "x" * 30

    chunks = split_document(document, max_chars=20)

    assert "".join(chunks) == document
    assert all(len(chunk) <= 20 for chunk in chunks)


def test_financial_report_upsert_replaces_metrics(tmp_path):
    db_path = tmp_path / "agpw.db"
    db.initialize_database(db_path)

    report = {
        "file_name": "wyniki_q1.pdf",
        "file_hash": "report-hash",
        "ticker": "AGPW",
        "company_name": "AGPW S.A.",
        "report_type": "quarterly",
        "period_start": "2026-01-01",
        "period_end": "2026-03-31",
        "currency": "PLN",
    }
    first_id = db.upsert_financial_report(
        **report,
        metrics=[
            {
                "metric_name": "revenue",
                "value": 100.0,
                "period_start": "2026-01-01",
                "period_end": "2026-03-31",
                "unit": "million_PLN",
                "source_page": 5,
                "source_quote": "Przychody: 100 mln PLN",
                "confidence": 0.95,
            }
        ],
        path=db_path,
    )
    second_id = db.upsert_financial_report(
        **report,
        metrics=[
            {
                "metric_name": "revenue",
                "value": 101.0,
                "period_start": "2026-01-01",
                "period_end": "2026-03-31",
            }
        ],
        path=db_path,
    )

    assert first_id == second_id
    with db.connect_db(db_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM financial_reports").fetchone()[0] == 1
        row = connection.execute("SELECT value FROM financial_metrics").fetchone()
    assert row["value"] == 101.0
