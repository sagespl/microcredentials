import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { StockQuote } from "../types/Stock";

export function Chart({ quotes }: { quotes: StockQuote[] }) {
  const data = quotes.map(({ date, close }) => ({ date, close }));
  return <div className="h-80 w-full"><ResponsiveContainer><LineChart data={data}><CartesianGrid stroke="#263241" strokeDasharray="3 3" /><XAxis dataKey="date" hide /><YAxis domain={["auto", "auto"]} stroke="#94a3b8" width={55} /><Tooltip contentStyle={{ background: "#101923", border: "1px solid #334155" }} /><Line type="monotone" dataKey="close" stroke="#22c55e" strokeWidth={2} dot={false} /></LineChart></ResponsiveContainer></div>;
}