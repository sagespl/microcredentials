import { getJson } from "./client";
import type { ScoreResponse } from "../types/Score";

export const getScore = (ticker: string, signal?: AbortSignal) =>
  getJson<ScoreResponse>(`/api/score/${encodeURIComponent(ticker)}`, signal);