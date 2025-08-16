"""
Configuración de desarrollo con auto-reload automático
Importa este archivo en lugar de settings.py para desarrollo
"""

from .settings import *

# ✅ CONFIGURACIÓN ESPECÍFICA PARA DESARROLLO
DEBUG = True

# Habilitar auto-reload
DJANGO_EXTENSIONS_AUTO_RELOAD = True

# Configuración de debug toolbar
INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Configuración de debug toolbar
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
    '::1',
]

# Configuración de logging para desarrollo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Configuración de desarrollo
print("🚀 CONFIGURACIÓN DE DESARROLLO CARGADA")
print("   - DEBUG: True")
print("   - Auto-reload: Habilitado")
print("   - Debug toolbar: Habilitado")
print("   - Logging detallado: Habilitado")
print("   - Archivo de log: debug.log")
