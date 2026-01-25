from functools import wraps
from flask import request, g
from ..logging.trace import set_trace_id, get_trace_id
import logging


def trace_requests(flask_app):

    @flask_app.before_request
    def before_request():
        trace_id = request.headers.get("X-Trace-ID") or None
        g.trace_id = set_trace_id(trace_id)

    @flask_app.after_request
    def after_request(response):
        response.headers["X-Trace-ID"] = g.trace_id
        return response

    logging.getLogger("werkzeug").addFilter(
        lambda record: setattr(record, "trace_id", get_trace_id()) or True
    )