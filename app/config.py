import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
REDIS_URL = os.getenv('REDIS_URL')

CSRF_PROTECTION = True

RATE_LIMIT_ENABLED = True
RATE_LIMIT_COOLDOWN = 900
RATE_LIMIT_MAX_REQUESTS = 100

THREAD_ID_LABEL = 'PINBAN'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s in %(funcName)s, %(filename)s: %(message)s'
        },
        'verbose': {
            'format': '%(asctime)s - %(levelname)s in %(funcName)s, %(pathname)s on line %(lineno)d by %(name)s: %(message)s'
        }
    },

    'handlers': {
        'stdout': {
            'level': 'INFO',
            'formatter': 'default',
            'class': 'logging.StreamHandler'
        },
        'error_log': {
            'level': 'ERROR',
            'formatter': 'verbose',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'error.log'
        }
    },

    'loggers': {
        'app.backend.admin.schemas': {
            'handlers': {'stdout', 'error_log'},
            'level': 'INFO',
            'propagate': False
        },
    },
    'loggers': {
        'app.backend.admin.routes': {
            'handlers': {'stdout', 'error_log'},
            'level': 'INFO',
            'propagate': False
        },
    },
    'loggers': {
        'app.backend.messages.routes': {
            'handlers': {'stdout', 'error_log'},
            'level': 'INFO',
            'propagate': False
        },
    },
    'root': {
        'handlers': ['error_log'],
        'level': 'ERROR'
    }
}
