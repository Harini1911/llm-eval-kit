import contextlib, functools, time
from contextvars import ContextVar
from .config import get_settings

s = get_settings()
_tracer = None
if s.otel_endpoint:
    try:
        from opentelemetry import trace
        _tracer = trace.get_tracer(s.service_name)
    except Exception:
        _tracer = None
_lf = None
if s.langfuse_secret_key:
    try:
        from langfuse import Langfuse
        _lf = Langfuse(public_key=s.langfuse_public_key, secret_key=s.langfuse_secret_key,
                       host=s.langfuse_host)
    except Exception:
        _lf = None

cost_ctx: ContextVar[dict | None] = ContextVar("cost", default=None)

@contextlib.contextmanager
def span(name: str, **attrs):
    """Never let tracing fail the request."""
    cm = _tracer.start_as_current_span(name) if _tracer else contextlib.nullcontext()
    t0 = time.perf_counter()
    try:
        with cm as sp:
            try:
                if sp is not None:
                    for k, v in attrs.items():
                        sp.set_attribute(k, v)
            except Exception:
                pass
            yield
    finally:
        pass  # timing available via x-process-time-ms / per-span

def observe(name: str):
    def deco(fn):
        @functools.wraps(fn)
        async def wrap(*a, **k):
            with span(name):
                return await fn(*a, **k)
        return wrap
    return deco

def track_cost(prompt_tokens: int, completion_tokens: int):
    c = cost_ctx.get()
    if c is not None:
        c["prompt_tokens"] += prompt_tokens
        c["completion_tokens"] += completion_tokens