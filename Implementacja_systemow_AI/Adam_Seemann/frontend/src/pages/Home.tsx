import { useDeferredValue, useState } from "react";
import { Link } from "react-router-dom";

import { getTickers } from "../api/tickers";
import { Error } from "../components/Error";
import { Loading } from "../components/Loading";
import { useFetch } from "../hooks/useFetch";

export function Home() {
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query.trim().toLowerCase());
  const { data: tickers, error, loading } = useFetch(getTickers, []);
  const matches = (tickers ?? []).filter((ticker) => `${ticker.ticker} ${ticker.name ?? ""}`.toLowerCase().includes(deferredQuery));

  return <section><p className="mb-2 text-xs uppercase tracking-[0.16em] text-emerald-400">Rynek akcji</p><h1 className="text-3xl font-bold">Monitor spółek GPW</h1><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Szukaj tickera lub nazwy" className="mt-8 w-full border border-slate-700 bg-slate-900 px-4 py-3 text-slate-100 outline-none ring-emerald-500 focus:ring-1" />{loading && <Loading />}{error && <Error message={error.message} />}{tickers && <div className="mt-5 divide-y divide-slate-800 border-y border-slate-800">{matches.map((ticker) => <Link key={ticker.ticker} to={`/stock/${ticker.ticker}`} className="flex items-center justify-between py-4 hover:bg-slate-900/60"><span><strong className="text-emerald-300">{ticker.ticker}</strong><span className="ml-3 text-slate-300">{ticker.name ?? "Brak nazwy"}</span></span><span className="text-sm text-slate-500">{ticker.sector ?? ""}</span></Link>)}{matches.length === 0 && <p className="py-8 text-center text-slate-500">Brak wyników.</p>}</div>}</section>;
}