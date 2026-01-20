"""
Logger Utility Module
Обертка над стандартным логгером с добавлением контекста

Single Responsibility: отвечает только за логирование с контекстом
Interface Segregation: предоставляет только необходимые методы
Dependency Inversion: использует стандартный интерфейс logging
"""
import logging
import traceback
import uuid
from typing import Any, Optional, Dict
from functools import wraps
from datetime import datetime


class ContextLogger:
    """
    Логгер с поддержкой контекста.
    Добавляет к каждому логу дополнительную информацию: request_id, user_id, action.
    """
    
    def __init__(self, name: str):
        """
        Инициализация логгера.
        
        Args:
            name: Имя логгера (обычно __name__ модуля)
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs: Any) -> None:
        """
        Установить контекст для всех последующих логов.
        
        Args:
            **kwargs: Произвольные параметры контекста
        
        Examples:
            logger.set_context(request_id='abc-123', user_id=1)
        """
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Очистить весь контекст."""
        self.context.clear()
    
    def _build_extra(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Объединить контекст с дополнительными параметрами.
        
        Args:
            extra: Дополнительные параметры для конкретного лога
        
        Returns:
            Объединенный словарь параметров
        """
        combined = {'context': self.context.copy()}
        if extra:
            combined['context'].update(extra)
        return combined
    
    def debug(self, message: str, **kwargs: Any) -> None:
        """
        Логировать сообщение уровня DEBUG.
        
        Args:
            message: Сообщение для лога
            **kwargs: Дополнительный контекст
        """
        self.logger.debug(message, extra=self._build_extra(kwargs))
    
    def info(self, message: str, **kwargs: Any) -> None:
        """
        Логировать сообщение уровня INFO.
        
        Args:
            message: Сообщение для лога
            **kwargs: Дополнительный контекст
        """
        self.logger.info(message, extra=self._build_extra(kwargs))
    
    def warning(self, message: str, **kwargs: Any) -> None:
        """
        Логировать сообщение уровня WARNING.
        
        Args:
            message: Сообщение для лога
            **kwargs: Дополнительный контекст
        """
        self.logger.warning(message, extra=self._build_extra(kwargs))
    
    def error(self, message: str, exception: Optional[Exception] = None, **kwargs: Any) -> None:
        """
        Логировать сообщение уровня ERROR.
        
        Args:
            message: Сообщение для лога
            exception: Исключение (если есть)
            **kwargs: Дополнительный контекст
        """
        extra = kwargs.copy()
        
        if exception:
            extra['exception_type'] = type(exception).__name__
            extra['exception_message'] = str(exception)
            extra['stack_trace'] = traceback.format_exc()
        
        self.logger.error(message, extra=self._build_extra(extra))
    
    def critical(self, message: str, exception: Optional[Exception] = None, **kwargs: Any) -> None:
        """
        Логировать сообщение уровня CRITICAL.
        
        Args:
            message: Сообщение для лога
            exception: Исключение (если есть)
            **kwargs: Дополнительный контекст
        """
        extra = kwargs.copy()
        
        if exception:
            extra['exception_type'] = type(exception).__name__
            extra['exception_message'] = str(exception)
            extra['stack_trace'] = traceback.format_exc()
        
        self.logger.critical(message, extra=self._build_extra(extra))
    
    def log_operation(
        self, 
        operation: str, 
        status: str = 'started',
        **kwargs: Any
    ) -> None:
        """
        Логировать операцию (создание, обновление, удаление).
        
        Args:
            operation: Название операции (create_user, update_contact, etc.)
            status: Статус операции (started, success, failed)
            **kwargs: Дополнительные данные операции
        """
        extra = {
            'operation': operation,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if status == 'failed':
            self.error(f"Operation failed: {operation}", **extra)
        elif status == 'success':
            self.info(f"Operation completed: {operation}", **extra)
        else:
            self.info(f"Operation {status}: {operation}", **extra)


def get_logger(name: str) -> ContextLogger:
    """
    Фабричная функция для создания логгера.
    
    Args:
        name: Имя логгера (обычно __name__ модуля)
    
    Returns:
        Экземпляр ContextLogger
    
    Examples:
        logger = get_logger(__name__)
        logger.info("User created", user_id=123)
    """
    return ContextLogger(name)


def log_execution(operation_name: Optional[str] = None):
    """
    Декоратор для автоматического логирования выполнения функции.
    
    Args:
        operation_name: Название операции (если None, используется имя функции)
    
    Examples:
        @log_execution('create_user')
        def create_user(data):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Получаем логгер для модуля функции
            logger = get_logger(func.__module__)
            op_name = operation_name or func.__name__
            
            # Генерируем operation_id для трейсинга
            operation_id = str(uuid.uuid4())[:8]
            
            # Логируем начало операции
            logger.log_operation(
                operation=op_name,
                status='started',
                operation_id=operation_id,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )
            
            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                
                # Логируем успех
                logger.log_operation(
                    operation=op_name,
                    status='success',
                    operation_id=operation_id
                )
                
                return result
                
            except Exception as e:
                # Логируем ошибку
                logger.log_operation(
                    operation=op_name,
                    status='failed',
                    operation_id=operation_id
                )
                logger.error(
                    f"Exception in {op_name}",
                    exception=e,
                    operation_id=operation_id
                )
                raise
        
        return wrapper
    return decorator


def generate_request_id() -> str:
    """
    Генерация уникального ID для запроса.
    
    Returns:
        Уникальный строковый идентификатор
    """
    return str(uuid.uuid4())


# Утилиты для быстрого логирования
def log_api_request(logger: ContextLogger, method: str, path: str, **kwargs: Any) -> None:
    """
    Логировать API запрос.
    
    Args:
        logger: Экземпляр логгера
        method: HTTP метод
        path: Путь запроса
        **kwargs: Дополнительная информация
    """
    logger.info(
        f"API Request: {method} {path}",
        method=method,
        path=path,
        **kwargs
    )


def log_api_response(
    logger: ContextLogger, 
    method: str, 
    path: str, 
    status_code: int,
    duration_ms: float,
    **kwargs: Any
) -> None:
    """
    Логировать API ответ.
    
    Args:
        logger: Экземпляр логгера
        method: HTTP метод
        path: Путь запроса
        status_code: Код ответа
        duration_ms: Длительность в миллисекундах
        **kwargs: Дополнительная информация
    """
    level = 'error' if status_code >= 500 else 'warning' if status_code >= 400 else 'info'
    
    log_method = getattr(logger, level)
    log_method(
        f"API Response: {method} {path} - {status_code} ({duration_ms:.2f}ms)",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )
