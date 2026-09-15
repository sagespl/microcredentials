-- Initial AGPW schema: core tables for quotes, ticker/sector mapping,
-- recommendations, and financial reports/metrics.

CREATE TABLE IF NOT EXISTS stocks_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    name TEXT,
    isin TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    num_trades INTEGER,
    open_interest INTEGER,
    open_interest_value REAL,
    par_value REAL,
    change_pct REAL,
    turnover REAL,
    currency TEXT
);

CREATE TABLE IF NOT EXISTS indexes_daily (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name TEXT NOT NULL,
    date DATE NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    change_pct REAL,
    turnover REAL,
    currency TEXT
);

CREATE TABLE IF NOT EXISTS tickers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,
    name TEXT,
    sector TEXT,
    market TEXT
);

CREATE TABLE IF NOT EXISTS sectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS sector_companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector TEXT NOT NULL,
    ticker TEXT NOT NULL,
    company_name TEXT
);

CREATE TABLE IF NOT EXISTS sector_index_map (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector TEXT NOT NULL,
    index_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    company_name TEXT,
    recommendation TEXT,
    target_price REAL,
    current_price REAL,
    potential_pct REAL,
    price_at_issue REAL,
    published_at TEXT NOT NULL,
    author TEXT,
    source_url TEXT
);

CREATE TABLE IF NOT EXISTS financial_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_name TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    ticker TEXT,
    company_name TEXT,
    report_type TEXT,
    period_start TEXT,
    period_end TEXT,
    currency TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS financial_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    period_start TEXT,
    period_end TEXT,
    currency TEXT,
    unit TEXT,
    source_page INTEGER,
    source_quote TEXT,
    confidence REAL,
    FOREIGN KEY (report_id) REFERENCES financial_reports(id) ON DELETE CASCADE,
    UNIQUE(report_id, metric_name, period_start, period_end)
);
