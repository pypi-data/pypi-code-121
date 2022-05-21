# Class for using OTel tracing

from typing import Optional, Sequence
from grpc import ChannelCredentials, Compression
from opentelemetry import trace
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  

# Auto Instrumentation libraries
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# SDK libraries 
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider

class Tracer:
    """Tracer

    Args:
        isTraceDisabled: set this to 'True' for disabling trace 
        serviceName: name of your service
    """

    def __init__(self, isTraceEnabled: bool, serviceName: str, currentFileName: str):
        self.isTraceEnabled = isTraceEnabled
        self.serviceName = serviceName
        self.currentFileName = currentFileName
    
    def configTracer(
        self,
        endpoint: Optional[str] = None, 
        isInsecure: Optional[bool] = None, 
        credentials: Optional[ChannelCredentials] = None, 
        headers: Optional[Sequence] = None, 
        timeout: Optional[int] = None, 
        compression: Optional[Compression] = None
    ):
        if (self.isTraceEnabled == False): return

        OTLPSpan_exporter = OTLPSpanExporter(  
            endpoint = endpoint,   
            insecure = isInsecure,
            credentials = credentials,
            headers = headers,
            timeout = timeout,
            compression = compression
        )   

        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: f"{self.serviceName}"}),
            )
        )

        trace.get_tracer_provider().add_span_processor(
            # Set up a simple processor to write spans out to the console so we can see what's happening.
            # SimpleSpanProcessor(ConsoleSpanExporter()),
            # Set up a BatchSpan processor to write spans out to the otlp collector.
            BatchSpanProcessor(OTLPSpan_exporter)
        )

        self.trace = trace
        # use in your code if u want get e.g. current trace id, look example:
        # ctx = self.trace.get_current_span().get_span_context()
        # ctx.trace_id

        self.tracer = trace.get_tracer(self.currentFileName)
        self.OTLPSpanExporter = OTLPSpan_exporter
    
    def startAutoInstrumentation(self, flaskApp):
        FlaskInstrumentor().instrument_app(flaskApp) 
        RequestsInstrumentor().instrument()