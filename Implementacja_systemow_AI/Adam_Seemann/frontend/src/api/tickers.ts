import { getJson } from "./client";
import type { Ticker } from "../types/Stock";

export const getTickers = (signal?: AbortSignal) => getJson<Ticker[]>("/api/ticker-map", signal);