"""Fundamental analysis models for financial data."""
from dataclasses import dataclass


@dataclass
class IncomeStatement:
    """Income Statement model."""

    ticker: str
    date: str
    revenue: float
    cost_of_goods_sold: float
    operating_expenses: float
    net_income: float
    tax_expense: float | None = None
    interest_expense: float | None = None

    @property
    def gross_profit(self) -> float:
        """Calculate gross profit."""
        return self.revenue - self.cost_of_goods_sold

    @property
    def operating_income(self) -> float:
        """Calculate operating income (EBIT)."""
        return self.gross_profit - self.operating_expenses

    @property
    def gross_profit_margin(self) -> float:
        """Calculate gross profit margin (%)."""
        if self.revenue == 0:
            return 0
        return (self.gross_profit / self.revenue) * 100

    @property
    def operating_profit_margin(self) -> float:
        """Calculate operating profit margin (%)."""
        if self.revenue == 0:
            return 0
        return (self.operating_income / self.revenue) * 100

    @property
    def net_profit_margin(self) -> float:
        """Calculate net profit margin (%)."""
        if self.revenue == 0:
            return 0
        return (self.net_income / self.revenue) * 100


@dataclass
class BalanceSheet:
    """Balance Sheet model."""

    ticker: str
    date: str
    total_assets: float
    total_liabilities: float
    total_equity: float
    current_assets: float | None = None
    current_liabilities: float | None = None
    long_term_liabilities: float | None = None

    @property
    def debt_to_equity(self) -> float:
        """Calculate debt-to-equity ratio."""
        if self.total_equity == 0:
            return float('inf')
        return self.total_liabilities / self.total_equity

    @property
    def debt_to_assets(self) -> float:
        """Calculate debt-to-assets ratio."""
        if self.total_assets == 0:
            return 0
        return self.total_liabilities / self.total_assets

    @property
    def current_ratio(self) -> float | None:
        """Calculate current ratio."""
        if self.current_assets is None or self.current_liabilities is None:
            return None
        if self.current_liabilities == 0:
            return float('inf')
        return self.current_assets / self.current_liabilities

    @property
    def equity_ratio(self) -> float:
        """Calculate equity ratio (equity/assets)."""
        if self.total_assets == 0:
            return 0
        return self.total_equity / self.total_assets


@dataclass
class CashFlow:
    """Cash Flow Statement model."""

    ticker: str
    date: str
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float
    depreciation: float | None = None
    capital_expenditure: float | None = None

    @property
    def net_cash_flow(self) -> float:
        """Calculate total net cash flow."""
        return (
            self.operating_cash_flow
            + self.investing_cash_flow
            + self.financing_cash_flow
        )

    @property
    def free_cash_flow(self) -> float:
        """Calculate free cash flow (OCF - investing activities)."""
        return self.operating_cash_flow + self.investing_cash_flow

    @property
    def operating_cash_flow_ratio(self) -> float | None:
        """Calculate operating cash flow efficiency."""
        if self.capital_expenditure is None or self.capital_expenditure == 0:
            return None
        return self.operating_cash_flow / self.capital_expenditure


@dataclass
class FinancialMetrics:
    """Aggregated financial metrics for analysis."""

    ticker: str
    date: str
    earnings_per_share: float
    price_to_earnings: float
    price_to_book: float
    dividend_yield: float
    roe: float  # Return on Equity (%)
    roa: float  # Return on Assets (%)
    current_price: float | None = None
    book_value_per_share: float | None = None

    @property
    def peg_ratio(self) -> float | None:
        """
        Calculate PEG ratio (P/E to Growth ratio).
        Requires growth rate data, so returns None for now.
        """
        return None

    @property
    def is_undervalued(self) -> bool:
        """
        Simple heuristic: stock might be undervalued if P/E is low
        relative to growth expectations (simplified).
        """
        return self.price_to_earnings < 15 and self.roe > 15

    @property
    def is_value_trap(self) -> bool:
        """
        Simple heuristic: might be value trap if P/E is low
        but ROE is also low.
        """
        return self.price_to_earnings < 10 and self.roe < 10
