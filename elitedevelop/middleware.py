# middleware.py
import time
from .models import RequestLog

class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = (time.time() - start_time) * 1000

        # Avoid logging the status dashboard itself to prevent endless loops!
        if not request.path.startswith('/system-status/'):
            RequestLog.objects.create(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=round(duration, 2)
            )

        return response