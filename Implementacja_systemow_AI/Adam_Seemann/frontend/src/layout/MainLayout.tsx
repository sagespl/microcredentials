import type { ReactNode } from "react";
import { Link } from "react-router-dom";

export function MainLayout({ children }: { children: ReactNode }) {
  return <div className="min-h-screen bg-[#080d14] text-slate-100"><header className="border-b border-slate-800"><div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5"><Link to="/" className="text-xl font-bold tracking-[0.18em] text-emerald-400">AGPW</Link><span className="text-xs uppercase tracking-[0.14em] text-slate-500">Analiza GPW</span></div></header><main className="mx-auto max-w-6xl px-5 py-8">{children}</main></div>;
}