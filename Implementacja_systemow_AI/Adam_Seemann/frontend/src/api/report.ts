import { getJson } from "./client";
import type { ReportResponse } from "../types/Report";

export const getReport = (ticker: string, signal?: AbortSignal) =>
  getJson<ReportResponse>(`/api/report/${encodeURIComponent(ticker)}`, signal);