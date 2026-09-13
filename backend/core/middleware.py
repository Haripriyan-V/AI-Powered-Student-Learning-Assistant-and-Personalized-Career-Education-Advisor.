import traceback
import sys
from django.http import HttpResponse


class ProductionExceptionLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        traceback.print_exc(file=sys.stderr)
        # If logged in as superuser, return the traceback to safely diagnose production admin issues
        if getattr(request, 'user', None) and request.user.is_authenticated and request.user.is_superuser:
            tb = traceback.format_exc()
            return HttpResponse(
                f"<pre style='color:#b91c1c; background:#fef2f2; padding:20px; font-size:13px; font-family:monospace;'>[Django Admin Production Error Diagnostic]\n\n{tb}</pre>",
                status=500,
                content_type="text/html"
            )
        return None
