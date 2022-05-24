import os, sys
{% if python_path %}
sys.path.insert(0, '{{python_path}}')
{% endif %}
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{django_settings_module}}")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
