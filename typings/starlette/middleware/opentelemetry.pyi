from collections.abc import Sequence

from opentelemetry import metrics, trace

from starlette.types import ASGIApp, Receive, Scope, Send

class OpenTelemetryMiddleware:
    """Create OpenTelemetry server spans for incoming HTTP requests.

    This middleware is experimental. Its API and emitted telemetry may change in minor
    releases without a deprecation period.

    Args:
        app: The ASGI application to wrap.
        excluded_urls: Regular expressions matched against the full request URL.
            Pass a comma-separated string or a sequence. By default, exclude no URLs.
        tracer_provider: Optional tracer provider. If omitted, use the global tracer provider.
        meter_provider: Optional meter provider. If omitted, use the global meter provider.
    """
    def __init__(self, app: ASGIApp, *, excluded_urls: str | Sequence[str] = ..., tracer_provider: trace.TracerProvider | None = ..., meter_provider: metrics.MeterProvider | None = ...) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...



