"""Tests for technical and fundamental analysis models."""
import pandas as pd
import pytest

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
    calculate_obv,
    calculate_rsi,
    calculate_sma,
    calculate_stochastic_oscillator,  # ← DODANE
    ema12,
    ema26,
    ema50,
    ema200,
    sma12,
    sma26,
    sma50,
    sma200,
)

# ============================================================
# TECHNICAL INDICATORS
# ============================================================

class TestTechnicalIndicators:
    """Test technical analysis indicators."""

    @pytest.fixture
    def sample_ohlc(self):
        """Create sample OHLC data."""
        return pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=100),
            "open": [100 + i * 0.5 for i in range(100)],
            "high": [102 + i * 0.5 for i in range(100)],
            "low": [99 + i * 0.5 for i in range(100)],
            "close": [101 + i * 0.5 for i in range(100)],
            "volume": [1000000 + i * 1000 for i in range(100)],
        })

    # ---------------- SMA ----------------

    def test_sma_calculation(self, sample_ohlc):
        sma = calculate_sma(sample_ohlc["close"], window=20)
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 19
        assert sma.iloc[19] > 0

    # SMA SHORTCUTS

    def test_sma12(self, sample_ohlc):
        sma = sma12(sample_ohlc["close"])
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 11  # first 11 NaN

    def test_sma26(self, sample_ohlc):
        sma = sma26(sample_ohlc["close"])
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 25

    def test_sma50(self, sample_ohlc):
        sma = sma50(sample_ohlc["close"])
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 49

    def test_sma200(self, sample_ohlc):
        sma = sma200(sample_ohlc["close"])
        assert len(sma) == len(sample_ohlc)
        assert sma.isna().sum() == 100  # dataset has only 100 rows → all NaN

    # ---------------- EMA ----------------

    def test_ema_calculation(self, sample_ohlc):
        ema = calculate_ema(sample_ohlc["close"], window=20)
        assert len(ema) == len(sample_ohlc)
        assert ema.isna().sum() == 0
        assert ema.iloc[19] > 0

    # EMA SHORTCUTS

    def test_ema12(self, sample_ohlc):
        result = ema12(sample_ohlc["close"])
        assert len(result) == len(sample_ohlc)
        assert result.iloc[0] == sample_ohlc["close"].iloc[0]

    def test_ema26(self, sample_ohlc):
        result = ema26(sample_ohlc["close"])
        assert len(result) == len(sample_ohlc)
        assert result.iloc[0] == sample_ohlc["close"].iloc[0]

    def test_ema50(self, sample_ohlc):
        result = ema50(sample_ohlc["close"])
        assert len(result) == len(sample_ohlc)
        assert result.iloc[0] == sample_ohlc["close"].iloc[0]

    def test_ema200(self, sample_ohlc):
        result = ema200(sample_ohlc["close"])
        assert len(result) == len(sample_ohlc)
        assert result.iloc[0] == sample_ohlc["close"].iloc[0]

    # ---------------- MACD ----------------

    def test_macd_calculation(self, sample_ohlc):
        macd, signal, histogram = calculate_macd(sample_ohlc["close"])
        assert len(macd) == len(sample_ohlc)
        assert len(signal) == len(sample_ohlc)
        assert len(histogram) == len(sample_ohlc)

        pd.testing.assert_series_equal(
            histogram.dropna(),
            (macd - signal).dropna(),
            check_names=False,
        )

    # ---------------- RSI ----------------

    def test_rsi_calculation(self, sample_ohlc):
        rsi = calculate_rsi(sample_ohlc["close"], window=14)
        assert len(rsi) == len(sample_ohlc)
        valid = rsi.dropna()
        assert valid.min() >= 0
        assert valid.max() <= 100

    # ---------------- ATR ----------------

    def test_atr_calculation(self, sample_ohlc):
        atr = calculate_atr(sample_ohlc, window=14)
        assert len(atr) == len(sample_ohlc)
        assert atr.dropna().min() > 0

    # ---------------- BOLLINGER ----------------

    def test_bollinger_bands_calculation(self, sample_ohlc):
        upper, middle, lower = calculate_bollinger_bands(
            sample_ohlc["close"], window=20, num_std=2
        )
        assert len(upper) == len(sample_ohlc)
        assert len(middle) == len(sample_ohlc)
        assert len(lower) == len(sample_ohlc)

        assert (upper.dropna() >= middle.dropna()).all()
        assert (middle.dropna() >= lower.dropna()).all()

    # ---------------- OBV ----------------

    def test_obv_calculation(self, sample_ohlc):
        obv = calculate_obv(sample_ohlc["close"], sample_ohlc["volume"])
        assert len(obv) == len(sample_ohlc)
        assert obv.iloc[0] >= 0

    # ---------------- AD ----------------

    def test_ad_calculation(self, sample_ohlc):
        ad = calculate_ad(sample_ohlc)
        assert len(ad) == len(sample_ohlc)
        assert ad.isna().sum() == 0
        assert ad.dtype in ["float64", "float32"]


# ============================================================
# FUNDAMENTAL MODELS
# ============================================================

class TestFundamentalModels:
    """Test fundamental analysis models."""

    def test_income_statement_creation(self):
        stmt = IncomeStatement(
            ticker="MKCM",
            date="2024-12-31",
            revenue=1_000_000,
            cost_of_goods_sold=500_000,
            operating_expenses=200_000,
            net_income=250_000,
        )
        assert stmt.ticker == "MKCM"
        assert stmt.revenue == 1_000_000
        assert stmt.net_profit_margin == 25.0

    def test_balance_sheet_creation(self):
        sheet = BalanceSheet(
            ticker="MKCM",
            date="2024-12-31",
            total_assets=1_000_000,
            total_liabilities=400_000,
            total_equity=600_000,
            current_assets=300_000,
            current_liabilities=150_000,
        )
        assert sheet.ticker == "MKCM"
        assert sheet.total_assets == 1_000_000
        assert sheet.debt_to_equity == 400_000 / 600_000

    def test_cash_flow_creation(self):
        flow = CashFlow(
            ticker="MKCM",
            date="2024-12-31",
            operating_cash_flow=200_000,
            investing_cash_flow=-50_000,
            financing_cash_flow=-30_000,
        )
        assert flow.ticker == "MKCM"
        assert flow.net_cash_flow == 120_000
        assert flow.free_cash_flow == 150_000

    def test_financial_metrics_calculation(self):
        metrics = FinancialMetrics(
            ticker="MKCM",
            date="2024-12-31",
            earnings_per_share=10.0,
            price_to_earnings=15.0,
            price_to_book=2.5,
            dividend_yield=2.0,
            roe=15.0,
            roa=8.0,
        )
        assert metrics.ticker == "MKCM"
        assert metrics.earnings_per_share == 10.0
        assert metrics.roe == 15.0


# ============================================================
# EDGE CASES
# ============================================================

class TestTechnicalIndicatorEdgeCases:
    """Test edge cases for technical indicators."""

    def test_sma_with_small_window(self):
        data = pd.Series([1, 2, 3, 4, 5])
        sma = calculate_sma(data, window=2)
        assert sma.iloc[1] == 1.5

    def test_rsi_with_constant_prices(self):
        data = pd.Series([100] * 30)
        rsi = calculate_rsi(data, window=14)
        assert rsi.isna().all() or len(rsi.dropna()) == 0

    def test_macd_with_short_data(self):
        data = pd.Series(range(1, 50))
        macd, signal, histogram = calculate_macd(data)
        assert len(macd) == len(data)

    # ---------------- STS EDGE CASE ----------------

    def test_stochastic_oscillator_edge_case(self):
        """STS should handle flat OHLC data without crashing."""
        ohlc = pd.DataFrame({
            "high":  [10, 10, 10, 10, 10],
            "low":   [10, 10, 10, 10, 10],
            "close": [10, 10, 10, 10, 10],
        })

        percent_k, percent_d = calculate_stochastic_oscillator(
            ohlc,
            k_window=3,
            d_window=3
        )

        assert isinstance(percent_k, pd.Series)
        assert isinstance(percent_d, pd.Series)
        assert len(percent_k) == len(ohlc)
        assert len(percent_d) == len(ohlc)

        # Flat OHLC → range = 0 → zamienione na NaN
        assert percent_k.isna().all()
        assert percent_d.isna().all()
