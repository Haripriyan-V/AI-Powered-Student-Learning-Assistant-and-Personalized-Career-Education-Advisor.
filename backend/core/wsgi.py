import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

try:
    from django.core.management import call_command
    call_command('setup_admin')
except Exception as e:
    print(f"Startup setup_admin notice: {e}")
