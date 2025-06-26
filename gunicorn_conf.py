# gunicorn_conf.py
import logging

# Basic gunicorn config
bind = "0.0.0.0:10000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 1

# Custom filter for health checks
class HealthCheckFilter(logging.Filter):
    def filter(self, record):
        # Filter out health check and favicon requests
        message = record.getMessage()
        return not any(path in message for path in [
            '/api/v1/health',
            '/favicon.ico'
        ])

# Configure logging to filter health checks
def when_ready(server):
    """Configure logging when server starts"""
    gunicorn_logger = logging.getLogger("gunicorn.access")
    gunicorn_logger.addFilter(HealthCheckFilter())

# Custom access log format (optional - makes logs cleaner)
access_log_format = '%(h)s - "%(r)s" %(s)s - %(D)s microseconds'