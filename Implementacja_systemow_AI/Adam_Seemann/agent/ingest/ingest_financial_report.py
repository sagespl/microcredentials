"""Extract structured financial metrics from local PDF and Excel reports."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TypedDict

import pandas as pd

from data.db import upsert_financial_report

MAX_CHUNK_CHARS = 24_000


class FinancialMetric(TypedDict):
    metric_name: str
    value: float
    period_start: str | None
    period_end: str | None
    currency: str | None
    unit: str | None
    source_page: int | None
    source_quote: str | None
    confidence: float | None


class FinancialReport(TypedDict):
    ticker: str | None
    company_name: str | None
    report_type: str | None
    period_start: str | None
    period_end: str | None
    currency: str | None
    metrics: list[FinancialMetric]


class ReportState(TypedDict):
    path: Path
    document_text: str
    report: FinancialReport


def _read_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as error:
        raise RuntimeError("PDF ingest requires pypdf. Install requirements.txt.") from error

    text = "\n".join(
        f"--- PAGE {page_number} ---\n{page.extract_text() or ''}"
        for page_number, page in enumerate(PdfReader(path).pages, start=1)
    )
    if not text.strip():
        raise ValueError("PDF contains no extractable text; OCR is required")
    return text


def _read_excel(path: Path) -> str:
    sheets = pd.read_excel(path, sheet_name=None)
    if not sheets:
        raise ValueError("Excel report contains no worksheets")
    return "\n\n".join(
        f"SHEET: {name}\n{frame.dropna(how='all').to_csv(index=False)}" for name, frame in sheets.items()
    )


def read_report_document(path: Path) -> str:
    """Return a text representation suitable for structured LLM extraction."""
    if path.suffix.lower() == ".pdf":
        return _read_pdf(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return _read_excel(path)
    raise ValueError(f"Unsupported financial report type: {path.suffix}")


def split_document(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split a report on paragraph boundaries to stay within the model context."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")

    chunks: list[str] = []
    current = ""
    for paragraph in text.splitlines(keepends=True):
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(paragraph[index:index + max_chars] for index in range(0, len(paragraph), max_chars))
        elif current and len(current) + len(paragraph) > max_chars:
            chunks.append(current)
            current = paragraph
        else:
            current += paragraph

    if current:
        chunks.append(current)
    return chunks


def _as_dict(report) -> FinancialReport:
    """Support both dictionary and Pydantic structured-output return values."""
    if hasattr(report, "model_dump"):
        return report.model_dump()
    return report


def _extract(state: ReportState) -> dict:
    try:
        from langchain_ollama import ChatOllama
    except ImportError as error:
        raise RuntimeError("Financial report ingest requires langchain-ollama.") from error

    model = ChatOllama(model="qwen2.5:7b", temperature=0).with_structured_output(FinancialReport)
    prompt_prefix = """Extract data from this Polish financial report. Return only reported facts.
Use ISO dates where possible. Metric names must be stable snake_case English names, such as
revenue, ebit, ebitda, net_income, total_assets, total_liabilities, equity,
operating_cash_flow, investing_cash_flow, financing_cash_flow, and net_debt.
Keep the report's scale in unit (PLN, thousand_PLN, million_PLN). For every metric include
the originating PDF page when known and a short exact source_quote. Never invent a value.

REPORT FRAGMENT:\n"""
    reports = [_as_dict(model.invoke(prompt_prefix + chunk)) for chunk in split_document(state["document_text"])]
    metadata = {
        field: next((report.get(field) for report in reports if report.get(field)), None)
        for field in ("ticker", "company_name", "report_type", "period_start", "period_end", "currency")
    }
    metrics = [metric for report in reports for metric in report.get("metrics", [])]
    return {"report": {**metadata, "metrics": metrics}}


def _validate(state: ReportState) -> dict:
    report = state["report"]
    valid_metrics = [
        metric for metric in report.get("metrics", [])
        if metric.get("metric_name") and isinstance(metric.get("value"), (int, float))
    ]
    if not valid_metrics:
        raise ValueError("No valid financial metrics were extracted")
    metrics_by_key: dict[tuple, FinancialMetric] = {}
    for metric in valid_metrics:
        key = (metric["metric_name"], metric.get("period_start"), metric.get("period_end"))
        current = metrics_by_key.get(key)
        if current is None or (metric.get("confidence") or 0) > (current.get("confidence") or 0):
            metrics_by_key[key] = metric
    report["metrics"] = list(metrics_by_key.values())
    return {"report": report}


def build_report_graph():
    """Build the extraction and validation graph; imports stay optional until used."""
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as error:
        raise RuntimeError("Financial report ingest requires langgraph.") from error

    graph = StateGraph(ReportState)
    graph.add_node("extract", _extract)
    graph.add_node("validate", _validate)
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "validate")
    graph.add_edge("validate", END)
    return graph.compile()


def ingest_financial_report(path: Path) -> int:
    """Extract, validate and persist a PDF/XLSX financial report with a local LLM."""
    path = Path(path)
    result = build_report_graph().invoke({"path": path, "document_text": read_report_document(path)})
    report = result["report"]
    return upsert_financial_report(
        file_name=path.name,
        file_hash=hashlib.sha256(path.read_bytes()).hexdigest(),
        ticker=report.get("ticker"),
        company_name=report.get("company_name"),
        report_type=report.get("report_type"),
        period_start=report.get("period_start"),
        period_end=report.get("period_end"),
        currency=report.get("currency"),
        metrics=report["metrics"],
    )
