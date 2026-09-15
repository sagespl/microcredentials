"""Deterministic analysis agents used by the AGPW pipeline."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd

from agent.models.fundamental import (
    BalanceSheet,
    CashFlow,
    FinancialMetrics,
    IncomeStatement,
)
from agent.models.technical import (
    calculate_ad,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_ema,
    calculate_macd,
    calculate_rsi,
    calculate_sma,
)
from agent.models.volume_anomalies import (
    VolumeAnomaly,
    detect_price_volume_divergence,
    detect_volume_collapse,
    detect_volume_spike,
)


def analyze_data(data: pd.DataFrame) -> dict[str, Any]:
    """Calculate the latest technical indicators for OHLCV data."""
    required = {"close", "high", "low"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if data.empty:
        raise ValueError("Cannot analyze an empty data frame")

    close = data["close"]
    macd, signal, histogram = calculate_macd(close)
    upper, middle, lower = calculate_bollinger_bands(close)
    return {
        "rows": len(data),
        "latest_close": _latest_number(close),
        "sma_12": _latest_number(calculate_sma(close, window=12)),
        "sma_26": _latest_number(calculate_sma(close, window=26)),
        "sma_50": _latest_number(calculate_sma(close, window=50)),
        "sma_200": _latest_number(calculate_sma(close, window=200)),
        "ema_12": _latest_number(calculate_ema(close, window=12)) if len(data) >= 12 else None,
        "ema_26": _latest_number(calculate_ema(close, window=26)) if len(data) >= 26 else None,
        "ema_50": _latest_number(calculate_ema(close, window=50)) if len(data) >= 50 else None,
        "ema_200": _latest_number(calculate_ema(close, window=200)) if len(data) >= 200 else None,
        "rsi_14": _latest_number(calculate_rsi(close)),
        "atr_14": _latest_number(calculate_atr(data)),
        "ad": _latest_number(calculate_ad(data)) if "volume" in data.columns else None,
        "macd": _latest_number(macd),
        "macd_signal": _latest_number(signal),
        "macd_histogram": _latest_number(histogram),
        "bollinger_upper": _latest_number(upper),
        "bollinger_middle": _latest_number(middle),
        "bollinger_lower": _latest_number(lower),
    }


def detect_anomalies(data: pd.DataFrame, z_threshold: float = 3.0) -> list[dict[str, Any]]:
    """Find unusually large daily price changes using a z-score."""
    if "close" not in data.columns:
        raise ValueError("Missing required column: close")
    if z_threshold <= 0:
        raise ValueError("z_threshold must be positive")
    changes = data["close"].pct_change()
    mean = changes.mean()
    std = changes.std(ddof=0)
    if pd.isna(std) or std == 0:
        return []
    anomalies = []
    for index, change in changes.items():
        if pd.isna(change):
            continue
        z_score = (change - mean) / std
        if abs(z_score) >= z_threshold:
            anomalies.append({"index": index, "change_pct": change * 100, "z_score": z_score})
    return anomalies


def analyze_financials(
    income: IncomeStatement,
    balance: BalanceSheet,
    cash_flow: CashFlow,
    metrics: FinancialMetrics,
) -> dict[str, Any]:
    """Aggregate the fundamental model properties into an analysis result."""
    return {
        "ticker": metrics.ticker,
        "date": metrics.date,
        "margins": {
            "gross_profit": income.gross_profit_margin,
            "operating_profit": income.operating_profit_margin,
            "net_profit": income.net_profit_margin,
        },
        "leverage": {
            "debt_to_equity": balance.debt_to_equity,
            "debt_to_assets": balance.debt_to_assets,
            "current_ratio": balance.current_ratio,
        },
        "cash_flow": {
            "net_cash_flow": cash_flow.net_cash_flow,
            "free_cash_flow": cash_flow.free_cash_flow,
        },
        "valuation": {
            "pe": metrics.price_to_earnings,
            "pb": metrics.price_to_book,
            "dividend_yield": metrics.dividend_yield,
            "roe": metrics.roe,
            "roa": metrics.roa,
        },
    }


def detect_fin_anomalies(
    income: IncomeStatement,
    balance: BalanceSheet,
    cash_flow: CashFlow,
    metrics: FinancialMetrics,
) -> list[str]:
    """Return explainable warnings for potentially risky fundamentals."""
    warnings: list[str] = []
    if income.revenue <= 0:
        warnings.append("non_positive_revenue")
    if income.net_income < 0:
        warnings.append("negative_net_income")
    if balance.debt_to_equity > 2:
        warnings.append("high_debt_to_equity")
    if balance.current_ratio is not None and balance.current_ratio < 1:
        warnings.append("low_current_ratio")
    if cash_flow.free_cash_flow < 0:
        warnings.append("negative_free_cash_flow")
    if metrics.is_value_trap:
        warnings.append("possible_value_trap")
    return warnings


def detect_volume_anomalies(
    data: pd.DataFrame,
    include_spikes: bool = True,
    include_collapses: bool = True,
    include_divergence: bool = True,
    spike_threshold: float = 2.0,
    collapse_threshold: float = 0.5,
    lookback_window: int = 20,
) -> list[dict[str, Any]]:
    """
    Detect volume anomalies: spikes, collapses, and price-volume divergences.

    Args:
        data: DataFrame with OHLCV data (columns: volume, close, etc.)
        include_spikes: Detect volume spikes (default True)
        include_collapses: Detect volume collapses (default True)
        include_divergence: Detect price-volume divergence (default True)
        spike_threshold: Volume spike multiplier (default 2.0 = 2x average)
        collapse_threshold: Volume collapse multiplier (default 0.5 = half average)
        lookback_window: Days for average calculation (default 20)

    Returns:
        List of dicts with volume anomaly information
    """
    if "volume" not in data.columns:
        raise ValueError("Missing required column: volume")

    all_anomalies: list[VolumeAnomaly] = []

    if include_spikes:
        all_anomalies.extend(
            detect_volume_spike(data, spike_threshold, lookback_window)
        )

    if include_collapses:
        all_anomalies.extend(
            detect_volume_collapse(data, collapse_threshold, lookback_window)
        )

    if include_divergence and "close" in data.columns:
        all_anomalies.extend(
            detect_price_volume_divergence(data, lookback_window=lookback_window)
        )

    # Convert to dict format for consistency with other anomaly functions
    return [
        {
            "date": a.date,
            "type": a.anomaly_type,
            "volume": a.volume,
            "average_volume": a.average_volume,
            "volume_ratio": a.volume / a.average_volume,
            "price_change_pct": a.price_change_pct,
            "severity": a.severity,
        }
        for a in all_anomalies
    ]


def score_company(analysis: Mapping[str, Any], anomalies: Sequence[Any] = ()) -> dict[str, Any]:
    """Score technical condition on a 0-100 scale."""
    score = 50.0
    close = analysis.get("latest_close")
    sma = analysis.get("sma_26")
    rsi = analysis.get("rsi_14")
    if close is not None and sma is not None:
        score += 15 if close > sma else -15
    if rsi is not None:
        score += 10 if 40 <= rsi <= 70 else -10
    score -= min(len(anomalies) * 10, 30)
    return {"score": max(0.0, min(100.0, score)), "rating": _rating(score)}


def score_financials(analysis: Mapping[str, Any], anomalies: Sequence[str] = ()) -> dict[str, Any]:
    """Score fundamental condition on a 0-100 scale."""
    margins = analysis.get("margins", {})
    valuation = analysis.get("valuation", {})
    leverage = analysis.get("leverage", {})
    score = 50.0
    score += 10 if margins.get("net_profit", 0) > 0 else -15
    score += 10 if valuation.get("roe", 0) > 10 else -5
    score += 10 if leverage.get("debt_to_equity", float("inf")) < 1.5 else -10
    score -= min(len(anomalies) * 8, 32)
    return {"score": max(0.0, min(100.0, score)), "rating": _rating(score)}


def generate_report(
    ticker: str,
    technical_score: Mapping[str, Any],
    financial_score: Mapping[str, Any] | None = None,
    anomalies: Sequence[Any] = (),
) -> str:
    """Create a short human-readable report from agent results."""
    report = (
        f"{ticker}: technical score {technical_score['score']:.1f}/100 "
        f"({technical_score['rating']}). "
    )
    if financial_score is None:
        report += "Financial score unavailable. "
    else:
        report += (
            f"Financial score {financial_score['score']:.1f}/100 "
            f"({financial_score['rating']}). "
        )
    return f"{report}Anomalies: {len(anomalies)}."


def _latest_number(series: pd.Series) -> float | None:
    valid = series.dropna()
    return None if valid.empty else float(valid.iloc[-1])


def _rating(score: float) -> str:
    if score >= 70:
        return "good"
    if score >= 45:
        return "neutral"
    return "weak"
