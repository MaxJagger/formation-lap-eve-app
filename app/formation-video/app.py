import os
from fastapi import FastAPI

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from prometheus_fastapi_instrumentator import Instrumentator


def _normalize_otlp_grpc_endpoint(endpoint: str) -> str:
    if endpoint.startswith("http://"):
        return endpoint[len("http://") :]
    if endpoint.startswith("https://"):
        return endpoint[len("https://") :]
    return endpoint


SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "formation-video")
OTLP_ENDPOINT = _normalize_otlp_grpc_endpoint(
    os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
)

resource = Resource.create({"service.name": SERVICE_NAME})
provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)
provider.add_span_processor(BatchSpanProcessor(exporter))

app = FastAPI()
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
FastAPIInstrumentor.instrument_app(app)


@app.get("/")
def root():
    return {"ok": True}


@app.get("/api/v1/videos/{video_id}")
def get_video(video_id: str):
    return [
        {
            "service": SERVICE_NAME,
            "endpoint": "/api/v1/videos/{video_id}",
            "video": {"id": video_id, "title": f"Video {video_id}"},
        }
    ]


@app.post("/api/v1/videos/{video_id}/play")
def play_video(video_id: str):
    return [
        {
            "service": SERVICE_NAME,
            "endpoint": "/api/v1/videos/{video_id}/play",
            "video_id": video_id,
            "status": "playing",
        }
    ]

