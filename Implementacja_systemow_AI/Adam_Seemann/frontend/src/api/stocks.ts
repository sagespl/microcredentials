import { getJson } from "./client";
import type { StockQuote } from "../types/Stock";

export const getStocks = (ticker: string, signal?: AbortSignal) =>
  getJson<StockQuote[]>(`/api/stocks/${encodeURIComponent(ticker)}`, signal);