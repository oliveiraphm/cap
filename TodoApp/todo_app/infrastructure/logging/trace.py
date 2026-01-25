from uuid import uuid4
from contextvars import ContextVar
from typing import Optional

trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)

def get_trace_id() -> str:
    current = trace_id_var.get()
    if current is None:
        current = str(uuid4())
        trace_id_var.set(current)
    return current

def set_trace_id(trace_id: Optional[str] = None) -> str:
    new_id = trace_id or str(uuid4())
    trace_id_var.set(new_id)
    return new_id