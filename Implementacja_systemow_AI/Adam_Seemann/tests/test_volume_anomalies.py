"""Tests for volume anomaly detection."""
import pandas as pd
import pytest

from agent.agents import detect_volume_anomalies
from agent.models.volume_anomalies import (
    calculate_volume_metrics,
    detect_price_volume_divergence,
    detect_volume_collapse,
    detect_volume_spike,
)


class TestVolumeMetrics:
    """Test volume metrics calculation."""

    def test_calculate_volume_metrics_valid(self):
        """Test metrics calculation with valid data."""
        data = pd.DataFrame({
            "volume": [100, 110, 120, 150, 130, 140],
        })
        result = calculate_volume_metrics(data, lookback_window=3)

        assert "vol_mean" in result.columns
        assert "vol_std" in result.columns
        assert "vol_ratio" in result.columns
        assert len(result) == len(data)

    def test_calculate_volume_metrics_missing_column(self):
        """Test that missing 'volume' column raises error."""
        data = pd.DataFrame({"price": [100, 110, 120]})

        with pytest.raises(ValueError, match="Missing required column: volume"):
            calculate_volume_metrics(data)


class TestVolumeSpike:
    """Test volume spike detection."""

    def test_detect_volume_spike_basic(self):
        """Test detecting a clear volume spike."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 100, 300, 100, 100],
        })
        anomalies = detect_volume_spike(data, spike_threshold=2.0, lookback_window=4)

        assert len(anomalies) > 0
        assert anomalies[0].anomaly_type == "spike"
        assert anomalies[0].severity in ["low", "medium", "high"]

    def test_detect_volume_spike_none(self):
        """Test no spikes detected with stable volume."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 100, 100],
        })
        anomalies = detect_volume_spike(data, spike_threshold=2.0, lookback_window=3)

        assert len(anomalies) == 0

    def test_detect_volume_spike_high_severity(self):
        """Test that volume spike is detected with appropriate severity."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 100, 400, 100, 100],
        })
        anomalies = detect_volume_spike(data, spike_threshold=2.0, lookback_window=4)

        # Should detect at least one spike
        assert len(anomalies) > 0
        # Verify spike properties
        spike = anomalies[0]
        assert spike.anomaly_type == "spike"
        assert spike.volume > spike.average_volume * 2.0


class TestVolumeCollapse:
    """Test volume collapse detection."""

    def test_detect_volume_collapse_basic(self):
        """Test detecting a clear volume collapse."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 30, 100, 100],
        })
        anomalies = detect_volume_collapse(data, collapse_threshold=0.5, lookback_window=3)

        assert len(anomalies) > 0
        assert anomalies[0].anomaly_type == "collapse"

    def test_detect_volume_collapse_none(self):
        """Test no collapses detected with stable volume."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 100, 100],
        })
        anomalies = detect_volume_collapse(data, collapse_threshold=0.5, lookback_window=3)

        assert len(anomalies) == 0


class TestPriceVolumeDivergence:
    """Test price-volume divergence detection."""

    def test_detect_divergence_high_vol_low_price(self):
        """Test detecting high volume with low price change."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 200, 100, 100],
            "close": [100.0, 100.5, 100.1, 100.2, 100.1, 100.0],
        })
        anomalies = detect_price_volume_divergence(
            data,
            high_volume_threshold=1.5,
            low_price_change_threshold=0.5,
            lookback_window=3
        )

        assert len(anomalies) > 0
        assert anomalies[0].anomaly_type == "price_divergence"

    def test_detect_divergence_none(self):
        """Test no divergence with normal data."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 100, 100, 100],
            "close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
        })
        anomalies = detect_price_volume_divergence(data, lookback_window=3)

        assert len(anomalies) == 0


class TestDetectVolumeAnomalies:
    """Test integrated detect_volume_anomalies function."""

    def test_detect_all_anomalies(self):
        """Test detection with all anomaly types enabled."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 250, 100, 30, 100],
            "close": [100.0, 100.5, 100.1, 100.2, 100.1, 100.0, 100.0],
        })
        anomalies = detect_volume_anomalies(
            data,
            include_spikes=True,
            include_collapses=True,
            include_divergence=True,
        )

        # Should detect at least spike and collapse
        assert len(anomalies) >= 2
        assert all(isinstance(a, dict) for a in anomalies)
        assert all("type" in a and "severity" in a for a in anomalies)

    def test_detect_only_spikes(self):
        """Test detecting only spikes."""
        data = pd.DataFrame({
            "volume": [100, 100, 100, 250, 100, 30, 100],
            "close": [100.0, 100.5, 100.1, 100.2, 100.1, 100.0, 100.0],
        })
        anomalies = detect_volume_anomalies(
            data,
            include_spikes=True,
            include_collapses=False,
            include_divergence=False,
        )

        assert all(a["type"] == "spike" for a in anomalies)

    def test_detect_volume_anomalies_missing_column(self):
        """Test that missing 'volume' raises error."""
        data = pd.DataFrame({"close": [100, 110, 120]})

        with pytest.raises(ValueError, match="Missing required column: volume"):
            detect_volume_anomalies(data)
