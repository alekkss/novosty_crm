"""
Logging Configuration Module
Централизованная конфигурация логирования приложения

Single Responsibility: отвечает только за настройку логирования
Open/Closed: легко добавить новые handlers без изменения существующих
"""
import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / 'logs'

# Создаем директорию для логов если её нет
LOGS_DIR.mkdir(exist_ok=True)


def get_logging_config():
    """
    Возвращает конфигурацию логирования для Django.
    
    Returns:
        dict: Конфигурация логирования в формате Django LOGGING
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        
        # Форматтеры - определяют формат логов
        'formatters': {
            # JSON формат для структурированных логов
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            
            # Человекочитаемый формат для консоли
            'verbose': {
                'format': '[{asctime}] {levelname:8s} | {name:30s} | {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            
            # Простой формат
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        
        # Фильтры (пока не используем, но можно добавить)
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        
        # Обработчики - куда отправляются логи
        'handlers': {
            # Консоль - для разработки
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
            
            # Файл для всех логов приложения (JSON)
            'app_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOGS_DIR / 'app.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 30,  # Хранить 30 файлов
                'formatter': 'json',
                'encoding': 'utf-8',
            },
            
            # Файл только для ошибок (JSON)
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOGS_DIR / 'errors.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 30,
                'formatter': 'json',
                'encoding': 'utf-8',
            },
            
            # Файл для логов фронтенда
            'frontend_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOGS_DIR / 'frontend.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 30,
                'formatter': 'json',
                'encoding': 'utf-8',
            },
            
            # Файл для SQL запросов (для отладки)
            'sql_file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(LOGS_DIR / 'sql.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 10,
                'formatter': 'verbose',
                'encoding': 'utf-8',
            },
        },
        
        # Логгеры - определяют какие компоненты логируются
        'loggers': {
            # Логгер для приложения contacts
            'apps.contacts': {
                'handlers': ['console', 'app_file', 'error_file'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Логгер для логов фронтенда
            'frontend': {
                'handlers': ['console', 'frontend_file'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Логгер для Django
            'django': {
                'handlers': ['console', 'app_file'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Логгер для Django запросов
            'django.request': {
                'handlers': ['console', 'error_file'],
                'level': 'WARNING',
                'propagate': False,
            },
            
            # Логгер для SQL запросов (только для разработки)
            'django.db.backends': {
                'handlers': ['sql_file'],
                'level': 'WARNING',  # Изменить на DEBUG для просмотра SQL
                'propagate': False,
            },
        },
        
        # Корневой логгер - ловит все что не попало в другие
        'root': {
            'handlers': ['console', 'app_file', 'error_file'],
            'level': 'INFO',
        },
    }


# Экспортируем готовую конфигурацию
LOGGING_CONFIG = get_logging_config()
