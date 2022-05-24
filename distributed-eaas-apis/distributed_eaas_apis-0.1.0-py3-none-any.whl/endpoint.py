"""Endpoint definitions of Distributed EaaS."""

from __future__ import annotations

_STABLE_DOMAIN: str = "metrics.api.eaas-dev.inspiredco.ai"
_BETA_DOMAIN: str = "metrics.api-beta.eaas-dev.inspiredco.ai"

_STABLE_METRICS: set[str] = set()

_BETA_METRICS: set[str] = {
    "bleu",
    "rouge",
}


def get_endpoint_address(metric_name: str, use_beta: bool = False) -> str:
    """Obtains endpoint address of specified metric.

    Args:
        metric_name: Name of the metric.
        use_beta: Whether to use beta APIs or not.

    Returns:
        Endpoint address of the metric service.

    Raises:
        ValueError: Specified metric is not supported for now.
    """
    domain = _BETA_DOMAIN if use_beta else _STABLE_DOMAIN
    metrics = _BETA_METRICS if use_beta else _STABLE_METRICS
    if metric_name not in metrics:
        raise ValueError(f"Unsupported metric: {metric_name}")
    return f"{metric_name}.{domain}"
