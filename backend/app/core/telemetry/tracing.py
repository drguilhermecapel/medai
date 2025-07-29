"""
OpenTelemetry Tracing and Metrics for MedAI
Provides distributed tracing and metrics collection
"""
import logging
import os
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource

logger = logging.getLogger(__name__)


def setup_telemetry(
    service_name: str = "medai",
    service_version: str = "1.0.0",
    jaeger_endpoint: Optional[str] = None,
    prometheus_endpoint: Optional[str] = None
):
    """
    Setup OpenTelemetry tracing and metrics
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        jaeger_endpoint: Jaeger collector endpoint
        prometheus_endpoint: Prometheus metrics endpoint
    """
    try:
        # Create resource with service information
        resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "service.environment": os.getenv("ENVIRONMENT", "development"),
            "service.instance.id": os.getenv("HOSTNAME", "unknown")
        })
        
        # Setup tracing
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)
        
        # Setup trace exporters
        _setup_trace_exporters(tracer_provider, jaeger_endpoint)
        
        # Setup metrics
        _setup_metrics(resource, prometheus_endpoint)
        
        logger.info("OpenTelemetry telemetry initialized", extra={
            "service_name": service_name,
            "service_version": service_version
        })
        
        # Return tracer and meter instances
        tracer = trace.get_tracer(__name__)
        meter = metrics.get_meter(__name__)
        
        return tracer, meter
        
    except Exception as e:
        logger.error(f"Failed to initialize telemetry: {e}")
        # Return no-op instances
        return trace.NoOpTracer(), metrics.NoOpMeter()


def _setup_trace_exporters(tracer_provider: TracerProvider, jaeger_endpoint: Optional[str]):
    """Setup trace exporters based on available endpoints"""
    
    # Try to setup OTLP exporter (for Jaeger)
    if jaeger_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
            
            otlp_exporter = OTLPSpanExporter(endpoint=jaeger_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            logger.info(f"OTLP trace exporter configured: {jaeger_endpoint}")
            
        except ImportError:
            logger.warning("OTLP exporter not available, install opentelemetry-exporter-otlp")
        except Exception as e:
            logger.error(f"Failed to setup OTLP exporter: {e}")
    
    # Fallback to console exporter for development
    else:
        try:
            from opentelemetry.sdk.trace.export import ConsoleSpanExporter
            
            console_exporter = ConsoleSpanExporter()
            span_processor = BatchSpanProcessor(console_exporter)
            tracer_provider.add_span_processor(span_processor)
            
            logger.info("Console trace exporter configured")
            
        except Exception as e:
            logger.error(f"Failed to setup console exporter: {e}")


def _setup_metrics(resource: Resource, prometheus_endpoint: Optional[str]):
    """Setup metrics collection and export"""
    
    try:
        # Setup metric readers
        metric_readers = []
        
        # Try Prometheus exporter
        if prometheus_endpoint:
            try:
                from opentelemetry.exporter.prometheus import PrometheusMetricReader
                
                prometheus_reader = PrometheusMetricReader()
                metric_readers.append(prometheus_reader)
                
                logger.info(f"Prometheus metrics exporter configured: {prometheus_endpoint}")
                
            except ImportError:
                logger.warning("Prometheus exporter not available, install opentelemetry-exporter-prometheus")
            except Exception as e:
                logger.error(f"Failed to setup Prometheus exporter: {e}")
        
        # Try OTLP metrics exporter
        else:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
                
                otlp_metric_exporter = OTLPMetricExporter()
                metric_reader = PeriodicExportingMetricReader(
                    otlp_metric_exporter,
                    export_interval_millis=5000
                )
                metric_readers.append(metric_reader)
                
                logger.info("OTLP metrics exporter configured")
                
            except ImportError:
                logger.warning("OTLP metrics exporter not available")
            except Exception as e:
                logger.error(f"Failed to setup OTLP metrics exporter: {e}")
        
        # Create meter provider
        meter_provider = MeterProvider(
            resource=resource,
            metric_readers=metric_readers
        )
        metrics.set_meter_provider(meter_provider)
        
    except Exception as e:
        logger.error(f"Failed to setup metrics: {e}")


class MedAITelemetry:
    """MedAI-specific telemetry helper class"""
    
    def __init__(self):
        """Initialize MedAI telemetry"""
        self.tracer, self.meter = setup_telemetry()
        
        # Create custom metrics
        self._create_custom_metrics()
    
    def _create_custom_metrics(self):
        """Create MedAI-specific metrics"""
        try:
            # API metrics
            self.request_counter = self.meter.create_counter(
                name="medai_requests_total",
                description="Total number of API requests",
                unit="1"
            )
            
            self.request_duration = self.meter.create_histogram(
                name="medai_request_duration_seconds",
                description="Request duration in seconds",
                unit="s"
            )
            
            # PHI encryption metrics
            self.phi_encryption_counter = self.meter.create_counter(
                name="medai_phi_encryptions_total",
                description="Total number of PHI encryption operations",
                unit="1"
            )
            
            self.phi_encryption_duration = self.meter.create_histogram(
                name="medai_phi_encryption_duration_seconds",
                description="PHI encryption duration in seconds",
                unit="s"
            )
            
            # Session metrics
            self.session_counter = self.meter.create_counter(
                name="medai_sessions_total",
                description="Total number of session operations",
                unit="1"
            )
            
            self.active_sessions = self.meter.create_up_down_counter(
                name="medai_active_sessions",
                description="Number of active sessions",
                unit="1"
            )
            
            # FHIR metrics
            self.fhir_operations_counter = self.meter.create_counter(
                name="medai_fhir_operations_total",
                description="Total number of FHIR operations",
                unit="1"
            )
            
            logger.info("Custom metrics created")
            
        except Exception as e:
            logger.error(f"Failed to create custom metrics: {e}")
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record API request metrics"""
        try:
            self.request_counter.add(1, {
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code)
            })
            
            self.request_duration.record(duration, {
                "method": method,
                "endpoint": endpoint
            })
            
        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")
    
    def record_phi_encryption(self, operation: str, duration: float, success: bool):
        """Record PHI encryption metrics"""
        try:
            self.phi_encryption_counter.add(1, {
                "operation": operation,
                "success": str(success)
            })
            
            if success:
                self.phi_encryption_duration.record(duration, {
                    "operation": operation
                })
                
        except Exception as e:
            logger.error(f"Failed to record PHI encryption metrics: {e}")
    
    def record_session_operation(self, operation: str, success: bool):
        """Record session operation metrics"""
        try:
            self.session_counter.add(1, {
                "operation": operation,
                "success": str(success)
            })
            
        except Exception as e:
            logger.error(f"Failed to record session metrics: {e}")
    
    def update_active_sessions(self, delta: int):
        """Update active sessions count"""
        try:
            self.active_sessions.add(delta)
        except Exception as e:
            logger.error(f"Failed to update active sessions: {e}")
    
    def record_fhir_operation(self, resource_type: str, operation: str, success: bool):
        """Record FHIR operation metrics"""
        try:
            self.fhir_operations_counter.add(1, {
                "resource_type": resource_type,
                "operation": operation,
                "success": str(success)
            })
            
        except Exception as e:
            logger.error(f"Failed to record FHIR metrics: {e}")
    
    def create_span(self, name: str, attributes: dict = None):
        """Create a new trace span"""
        return self.tracer.start_span(name, attributes=attributes or {})


# Global telemetry instance
telemetry = MedAITelemetry()