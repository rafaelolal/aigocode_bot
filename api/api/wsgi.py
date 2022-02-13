"""
WSGI config for api project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os, sys

site_packages = '/home/thinkland/projects/envs/aigocode_bot_env/lib/python3.10/site-packages'
if site_packages not in sys.path:
    sys.path.append(site_packages)

project_path = '/home/thinkland/projects/bots/aigocode_bot/api'
project_path2 = '/home/thinkland/projects/bots/aigocode_bot/api/api'

if project_path not in sys.path:
    sys.path.append(project_path)
if project_path2 not in sys.path:
    sys.path.append(project_path2)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
