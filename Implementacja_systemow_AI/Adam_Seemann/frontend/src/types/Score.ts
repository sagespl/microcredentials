export interface TechnicalAnalysis {
  [key: string]: number | string | null | undefined;
  rsi_14?: number | null;
  macd?: number | null;
  sma_12?: number | null;
  sma_26?: number | null;
  ema_12?: number | null;
  ema_26?: number | null;
}

export interface Anomaly {
  type: string;
  message?: string;
  z_score?: number;
  [key: string]: string | number | null | undefined;
}

export interface CompanyScore {
  score: number;
  [key: string]: number | string | null | undefined;
}

export interface ScoreResponse {
  ticker: string;
  analysis: TechnicalAnalysis;
  anomalies: Anomaly[];
  score: CompanyScore;
}