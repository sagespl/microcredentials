"""Volume anomaly detection models and calculations."""
from dataclasses import dataclass

import pandas as pd


@dataclass
class VolumeAnomaly:
    """Represents a detected volume anomaly."""

    date: str
    anomaly_type: str  # "spike", "collapse", "price_divergence"
    volume: float
    average_volume: float
    price_change_pct: float | None = None
    severity: str = "medium"  # "low", "medium", "high"

    def __repr__(self) -> str:
        return (
            f"VolumeAnomaly(date={self.date}, type={self.anomaly_type}, "
            f"volume={self.volume:.0f}, avg={self.average_volume:.0f}, "
            f"severity={self.severity})"
        )


def calculate_volume_metrics(
    data: pd.DataFrame,
    lookback_window: int = 20
) -> pd.DataFrame:
    """
    Calculate volume metrics: mean, std, ratio to mean.

    Args:
        data: DataFrame with 'volume' column and date index
        lookback_window: Number of days to look back for mean calculation

    Returns:
        DataFrame with volume, vol_mean, vol_ratio columns
    """
    if "volume" not in data.columns:
        raise ValueError("Missing required column: volume")

    result = data.copy()
    result["vol_mean"] = result["volume"].rolling(window=lookback_window, min_periods=1).mean()
    result["vol_std"] = result["volume"].rolling(window=lookback_window, min_periods=1).std()
    result["vol_ratio"] = result["volume"] / result["vol_mean"]

    return result


def detect_volume_spike(
    data: pd.DataFrame,
    spike_threshold: float = 2.0,
    lookback_window: int = 20
) -> list[VolumeAnomaly]:
    """
    Detect unusual volume spikes (volume > spike_threshold * average).

    Args:
        data: DataFrame with 'volume' and 'close' columns
        spike_threshold: Multiplier of average volume (default 2.0 = 2x average)
        lookback_window: Days to look back for average calculation

    Returns:
        List of VolumeAnomaly objects with type 'spike'
    """
    if "volume" not in data.columns:
        raise ValueError("Missing required column: volume")

    metrics = calculate_volume_metrics(data, lookback_window)
    anomalies = []

    for idx, row in metrics.iterrows():
        if pd.isna(row["vol_mean"]) or pd.isna(row["vol_ratio"]):
            continue

        if row["vol_ratio"] >= spike_threshold:
            # Determine severity
            ratio = row["vol_ratio"]
            if ratio >= 3.0:
                severity = "high"
            elif ratio >= 2.5:
                severity = "medium"
            else:
                severity = "low"

            anomalies.append(
                VolumeAnomaly(
                    date=str(idx),
                    anomaly_type="spike",
                    volume=row["volume"],
                    average_volume=row["vol_mean"],
                    price_change_pct=None,
                    severity=severity
                )
            )

    return anomalies


def detect_volume_collapse(
    data: pd.DataFrame,
    collapse_threshold: float = 0.5,
    lookback_window: int = 20
) -> list[VolumeAnomaly]:
    """
    Detect unusual volume collapses (volume < collapse_threshold * average).

    Args:
        data: DataFrame with 'volume' column
        collapse_threshold: Multiplier of average volume (default 0.5 = half average)
        lookback_window: Days to look back for average calculation

    Returns:
        List of VolumeAnomaly objects with type 'collapse'
    """
    if "volume" not in data.columns:
        raise ValueError("Missing required column: volume")

    metrics = calculate_volume_metrics(data, lookback_window)
    anomalies = []

    for idx, row in metrics.iterrows():
        if pd.isna(row["vol_mean"]) or pd.isna(row["vol_ratio"]):
            continue

        if row["vol_ratio"] <= collapse_threshold:
            # Determine severity
            ratio = row["vol_ratio"]
            if ratio <= 0.3:
                severity = "high"
            elif ratio <= 0.4:
                severity = "medium"
            else:
                severity = "low"

            anomalies.append(
                VolumeAnomaly(
                    date=str(idx),
                    anomaly_type="collapse",
                    volume=row["volume"],
                    average_volume=row["vol_mean"],
                    price_change_pct=None,
                    severity=severity
                )
            )

    return anomalies


def detect_price_volume_divergence(
    data: pd.DataFrame,
    high_volume_threshold: float = 1.8,
    low_price_change_threshold: float = 0.5,
    lookback_window: int = 20
) -> list[VolumeAnomaly]:
    """
    Detect price-volume divergence: high volume but low price change.

    Possible signals:
    - Accumulation/distribution without clear direction
    - Potential reversal

    Args:
        data: DataFrame with 'volume', 'close' columns
        high_volume_threshold: Consider volume "high" if > this * average (default 1.8)
        low_price_change_threshold: Consider price change "low" if < this % (default 0.5%)
        lookback_window: Days for average calculation

    Returns:
        List of VolumeAnomaly objects with type 'price_divergence'
    """
    if "volume" not in data.columns or "close" not in data.columns:
        raise ValueError("Missing required columns: volume, close")

    metrics = calculate_volume_metrics(data, lookback_window)
    metrics["price_change_pct"] = metrics["close"].pct_change().abs() * 100

    anomalies = []

    for idx, row in metrics.iterrows():
        if pd.isna(row["vol_mean"]) or pd.isna(row["price_change_pct"]):
            continue

        # High volume + low price change = divergence
        if (row["vol_ratio"] >= high_volume_threshold and
            row["price_change_pct"] < low_price_change_threshold):

            anomalies.append(
                VolumeAnomaly(
                    date=str(idx),
                    anomaly_type="price_divergence",
                    volume=row["volume"],
                    average_volume=row["vol_mean"],
                    price_change_pct=row["price_change_pct"],
                    severity="medium"
                )
            )

    return anomalies
