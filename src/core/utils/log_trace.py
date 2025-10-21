from src.models.tracing import TraceEvent
from azure.monitor.opentelemetry import configure_azure_monitor
from logging import INFO, getLogger
import os

is_tracing_enabled = True

# get the env var APPLICATIONINSIGHTS_CONNECTION_STRING
if "APPLICATIONINSIGHTS_CONNECTION_STRING" not in os.environ:
    is_tracing_enabled = False
    print("Tracing is disabled because APPLICATIONINSIGHTS_CONNECTION_STRING is not set.")
else:
    print("Tracing is enabled because APPLICATIONINSIGHTS_CONNECTION_STRING is set.")


if is_tracing_enabled:
    configure_azure_monitor(
        logger_name="TRACE_EVENT"
    )
    logger = getLogger("TRACE_EVENT")
    logger.setLevel(INFO)

def log_trace_event(trace_id: str, step: str):
    
    if is_tracing_enabled is False:
        return
    
    trace = TraceEvent(
        trace_id=trace_id,
        step=step,
    )
    logger.info(f"[TRACE_EVENT] {trace.model_dump_json()}")


