"""
Development settings for aberturas project.
"""

from .base import *

# Development specific settings
DEBUG = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Development logging
LOGGING['root']['level'] = 'DEBUG'

# CSRF settings for development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'https://z5906h8z-3001.brs.devtunnels.ms',
    'https://z5906h8z-8002.brs.devtunnels.ms',
]

# Disable secure cookies for development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allow all origins for CORS in development
CORS_ALLOW_ALL_ORIGINS = True

# Django Debug Toolbar (optional)
if DEBUG:
    try:
        import debug_toolbar
        INSTALLED_APPS += ['debug_toolbar']
        MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
        INTERNAL_IPS = ['127.0.0.1', 'localhost']
    except ImportError:
        pass