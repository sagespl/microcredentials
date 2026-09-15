import { useParams } from "react-router-dom";

import { getReport } from "../api/report";
import { getScore } from "../api/score";
import { getStocks } from "../api/stocks";
import { Chart } from "../components/Chart";
import { Error } from "../components/Error";
import { Loading } from "../components/Loading";
import { ScoreBadge } from "../components/ScoreBadge";
import { useFetch } from "../hooks/useFetch";

const indicators = ["rsi_14", "macd", "sma_12", "sma_26", "ema_12", "ema_26"];

export function Stock() {
  const ticker = useParams().ticker?.toUpperCase() ?? "";
  const stocks = useFetch((signal) => getStocks(ticker, signal), [ticker]);
  const score = useFetch((signal) => getScore(ticker, signal), [ticker]);
  const report = useFetch((signal) => getReport(ticker, signal), [ticker]);
  const error = stocks.error ?? score.error ?? report.error;

  if (stocks.loading || score.loading || report.loading) return <Loading />;
  if (error) return <Error message={error.message} />;
  if (!stocks.data || !score.data || !report.data) return <Error message="Nie udało się pobrać danych spółki." />;
  const latest = stocks.data.at(-1);
  return <section><div className="mb-8 flex flex-wrap items-end justify-between gap-5"><div><p className="text-xs uppercase tracking-[0.16em] text-emerald-400">Spółka</p><h1 className="mt-2 text-3xl font-bold">{ticker}</h1><p className="mt-1 text-slate-400">{latest?.name ?? latest?.isin}</p></div><ScoreBadge score={score.data.score.score} /></div><div className="grid gap-6 lg:grid-cols-3"><div className="border border-slate-800 bg-slate-900/40 p-5 lg:col-span-2"><h2 className="text-lg font-bold">Cena zamknięcia</h2><Chart quotes={stocks.data} /></div><div className="border border-slate-800 bg-slate-900/40 p-5"><h2 className="text-lg font-bold">Wskaźniki techniczne</h2><dl className="mt-4 space-y-3">{indicators.map((key) => <div key={key} className="flex justify-between border-b border-slate-800 pb-2"><dt className="uppercase text-slate-400">{key}</dt><dd>{score.data.analysis[key]?.toString() ?? "-"}</dd></div>)}</dl></div><div className="border border-slate-800 bg-slate-900/40 p-5 lg:col-span-2"><h2 className="text-lg font-bold">Raport</h2><p className="mt-4 whitespace-pre-wrap leading-7 text-slate-300">{report.data.report}</p></div><div className="border border-slate-800 bg-slate-900/40 p-5"><h2 className="text-lg font-bold">Anomalie</h2><ul className="mt-4 space-y-3 text-sm text-slate-300">{score.data.anomalies.length ? score.data.anomalies.map((anomaly, index) => <li key={`${anomaly.type}-${index}`} className="border-l-2 border-amber-400 pl-3">{anomaly.message ?? anomaly.type}</li>) : <li className="text-slate-500">Brak wykrytych anomalii.</li>}</ul></div></div></section>;
}