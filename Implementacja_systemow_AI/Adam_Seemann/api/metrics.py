"""Prometheus metrics for the AGPW API."""

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

__all__ = ["CONTENT_TYPE_LATEST", "REQUEST_COUNT", "REQUEST_LATENCY", "render_latest"]

REQUEST_COUNT = Counter(
    "agpw_http_requests_total",
    "Total number of HTTP requests processed",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "agpw_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


def render_latest() -> bytes:
    """Render current metrics in the Prometheus text exposition format."""
    return generate_latest()
