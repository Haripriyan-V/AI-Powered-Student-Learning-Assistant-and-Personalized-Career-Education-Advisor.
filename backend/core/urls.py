from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve
from rest_framework_simplejwt.views import TokenRefreshView


def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'disha-ai-backend',
        'version': '1.0.0',
    })


def root_view(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'disha-ai-backend',
        'version': '1.0.0',
        'message': 'DishaAI Backend API is running successfully.',
        'endpoints': {
            'admin': '/admin/',
            'health': '/health/',
            'api_health': '/api/health/',
            'auth': '/api/accounts/',
            'career': '/api/career/',
            'learning': '/api/learning/',
            'students': '/api/students/',
            'chatbot': '/api/chatbot/',
        },
        'frontend_url': 'https://ai-powered-student-learning-assista-red.vercel.app'
    })


urlpatterns = [
    # Root & Health check endpoints
    path('', root_view, name='root'),
    path('health/', health_check, name='health_check'),
    path('api/health/', health_check, name='api_health_check'),

    path('admin/', admin.site.urls),

    # JWT token endpoints
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App-level APIs
    path('api/accounts/', include('accounts.urls')),
    path('api/students/', include('students.urls')),
    path('api/learning/', include('learning.urls')),
    path('api/career/', include('career.urls')),
    path('api/chatbot/', include('chatbot.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # Ensure media files (e.g. uploaded resumes) remain accessible in production environments
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

