-- Unique indexes required to support upserts (ON CONFLICT) on mapping tables.

CREATE UNIQUE INDEX IF NOT EXISTS ux_stocks_daily_isin_date ON stocks_daily(isin, date);
CREATE UNIQUE INDEX IF NOT EXISTS ux_sector_companies_sector_ticker ON sector_companies(sector, ticker);
CREATE UNIQUE INDEX IF NOT EXISTS ux_sector_index_map_sector_index ON sector_index_map(sector, index_name);
CREATE UNIQUE INDEX IF NOT EXISTS ux_recommendations_ticker_published_author
    ON recommendations(ticker, published_at, author);
