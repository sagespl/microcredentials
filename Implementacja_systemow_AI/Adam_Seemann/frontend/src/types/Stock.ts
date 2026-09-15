export interface StockQuote {
  ticker: string | null;
  name: string | null;
  isin: string;
  date: string;
  open: number | null;
  high: number | null;
  low: number | null;
  close: number | null;
  volume: number | null;
  change_pct: number | null;
  currency: string | null;
}

export interface Ticker {
  ticker: string;
  name: string | null;
  sector: string | null;
  market: string | null;
}