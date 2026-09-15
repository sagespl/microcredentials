export function ScoreBadge({ score }: { score: number }) {
  const color = score >= 70 ? "border-emerald-500 text-emerald-300" : score >= 40 ? "border-amber-400 text-amber-200" : "border-red-500 text-red-300";
  return <span className={`inline-flex h-20 w-20 items-center justify-center rounded-full border-2 text-2xl font-bold ${color}`}>{Math.round(score)}</span>;
}