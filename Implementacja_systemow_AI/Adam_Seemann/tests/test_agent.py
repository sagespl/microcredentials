"""Tests for deterministic analysis agents."""

import pandas as pd
import pytest

from agent.agents import (
    analyze_data,
    analyze_financials,
    detect_anomalies,
    detect_fin_anomalies,
    generate_report,
    score_company,
    score_financials,
)
from agent.models.fundamental import BalanceSheet, CashFlow, FinancialMetrics, IncomeStatement


@pytest.fixture
def market_data():
    close = [100 + index for index in range(40)]
    return pd.DataFrame({"close": close, "high": [value + 2 for value in close], "low": [value - 2 for value in close]})


@pytest.fixture
def fundamentals():
    return (
        IncomeStatement("ABC", "2024-12-31", 1000, 400, 200, 200),
        BalanceSheet("ABC", "2024-12-31", 2000, 600, 1400, 800, 400),
        CashFlow("ABC", "2024-12-31", 300, -100, -50),
        FinancialMetrics("ABC", "2024-12-31", 2, 12, 1.5, 2, 18, 8),
    )


def test_analyze_data_returns_latest_indicators(market_data):
    result = analyze_data(market_data)
    assert result["rows"] == 40
    assert result["latest_close"] == 139.0
    assert result["sma_12"] == pytest.approx(133.5)
    assert result["sma_26"] == pytest.approx(126.5)
    assert result["sma_50"] is None
    assert result["sma_200"] is None
    assert result["ema_12"] is not None
    assert result["ema_26"] is not None
    assert result["ema_50"] is None
    assert result["ema_200"] is None
    assert result["ad"] is None


def test_analyze_data_rejects_missing_columns():
    with pytest.raises(ValueError, match="high"):
        analyze_data(pd.DataFrame({"close": [1, 2]}))


def test_detect_anomalies_finds_large_move():
    data = pd.DataFrame({"close": [100] * 20 + [200] + [100] * 20})
    assert any(item["index"] == 20 for item in detect_anomalies(data, z_threshold=2))


def test_financial_agents_and_report(fundamentals):
    income, balance, cash_flow, metrics = fundamentals
    analysis = analyze_financials(income, balance, cash_flow, metrics)
    assert analysis["cash_flow"]["free_cash_flow"] == 200
    assert detect_fin_anomalies(income, balance, cash_flow, metrics) == []
    technical_score = score_company({"latest_close": 110, "sma_26": 100, "rsi_14": 55})
    financial_score = score_financials(analysis)
    report = generate_report("ABC", technical_score, financial_score)
    assert technical_score["score"] > 50
    assert financial_score["score"] > 50
    assert "ABC" in report


def test_financial_anomalies_are_reported(fundamentals):
    income, _, cash_flow, metrics = fundamentals
    risky_balance = BalanceSheet("ABC", "2024-12-31", 2000, 1800, 200, 100, 200)
    warnings = detect_fin_anomalies(
        IncomeStatement("ABC", "2024-12-31", 1000, 400, 200, -10),
        risky_balance,
        CashFlow("ABC", "2024-12-31", 50, -200, 0),
        FinancialMetrics("ABC", "2024-12-31", 2, 8, 1.5, 2, 5, 2),
    )
    assert {"negative_net_income", "high_debt_to_equity", "low_current_ratio", "negative_free_cash_flow", "possible_value_trap"} <= set(warnings)
