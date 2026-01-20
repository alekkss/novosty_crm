"""
Logging Middleware Module
Middleware для автоматического логирования HTTP запросов

Single Responsibility: отвечает только за логирование HTTP запросов/ответов
Open/Closed: легко расширить через наследование
"""
import time
import json
from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from apps.core.logger import get_logger, generate_request_id, log_api_request, log_api_response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для логирования HTTP запросов и ответов.
    
    Функции:
    - Генерирует уникальный request_id для каждого запроса
    - Логирует входящие запросы с параметрами
    - Логирует ответы с кодом статуса и временем выполнения
    - Добавляет request_id в заголовки ответа
    - Обрабатывает исключения
    """
    
    def __init__(self, get_response: Callable):
        """
        Инициализация middleware.
        
        Args:
            get_response: Следующий middleware или view
        """
        super().__init__(get_response)
        self.get_response = get_response
        self.logger = get_logger('django.request')
    
    def process_request(self, request: HttpRequest) -> None:
        """
        Обработка входящего запроса.
        
        Args:
            request: HTTP запрос
        """
        # Генерируем уникальный ID для запроса
        request.request_id = generate_request_id()
        
        # Сохраняем время начала запроса
        request.start_time = time.time()
        
        # Устанавливаем контекст для логгера
        self.logger.set_context(
            request_id=request.request_id,
            method=request.method,
            path=request.path,
            remote_addr=self._get_client_ip(request)
        )
        
        # Логируем входящий запрос
        log_data = {
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
            'content_type': request.content_type,
        }
        
        # Добавляем query params если есть
        if request.GET:
            log_data['query_params'] = dict(request.GET)
        
        # Для POST/PUT/PATCH логируем размер тела
        if request.method in ['POST', 'PUT', 'PATCH']:
            log_data['content_length'] = request.META.get('CONTENT_LENGTH', 0)
        
        log_api_request(
            self.logger,
            method=request.method,
            path=request.path,
            **log_data
        )
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Обработка исходящего ответа.
        
        Args:
            request: HTTP запрос
            response: HTTP ответ
        
        Returns:
            Обработанный HTTP ответ
        """
        # Вычисляем длительность запроса
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
        else:
            duration_ms = 0
        
        # Добавляем request_id в заголовки ответа
        if hasattr(request, 'request_id'):
            response['X-Request-ID'] = request.request_id
        
        # Логируем ответ
        log_data = {
            'content_type': response.get('Content-Type', 'unknown'),
        }
        
        # Для ошибок добавляем тело ответа (если оно небольшое)
        if response.status_code >= 400:
            try:
                if hasattr(response, 'content') and len(response.content) < 1024:
                    content = response.content.decode('utf-8', errors='ignore')
                    try:
                        log_data['response_body'] = json.loads(content)
                    except json.JSONDecodeError:
                        log_data['response_body'] = content
            except Exception:
                pass
        
        log_api_response(
            self.logger,
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            **log_data
        )
        
        # Очищаем контекст логгера
        self.logger.clear_context()
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        """
        Обработка исключений во время выполнения запроса.
        
        Args:
            request: HTTP запрос
            exception: Возникшее исключение
        """
        # Вычисляем длительность до ошибки
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
        else:
            duration_ms = 0
        
        # Логируем исключение
        self.logger.error(
            f"Unhandled exception during request: {request.method} {request.path}",
            exception=exception,
            duration_ms=duration_ms,
            remote_addr=self._get_client_ip(request)
        )
        
        # Очищаем контекст
        self.logger.clear_context()
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Получить IP адрес клиента с учетом прокси.
        
        Args:
            request: HTTP запрос
        
        Returns:
            IP адрес клиента
        """
        # Проверяем заголовки прокси
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Берем первый IP из списка (реальный клиент)
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return ip


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """
    Middleware для логирования медленных запросов.
    
    Логирует запросы, которые выполняются дольше заданного порога.
    """
    
    # Порог в миллисекундах (можно вынести в settings)
    SLOW_REQUEST_THRESHOLD_MS = 1000  # 1 секунда
    
    def __init__(self, get_response: Callable):
        """
        Инициализация middleware.
        
        Args:
            get_response: Следующий middleware или view
        """
        super().__init__(get_response)
        self.get_response = get_response
        self.logger = get_logger('performance')
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Проверка времени выполнения запроса.
        
        Args:
            request: HTTP запрос
            response: HTTP ответ
        
        Returns:
            HTTP ответ
        """
        if hasattr(request, 'start_time'):
            duration_ms = (time.time() - request.start_time) * 1000
            
            # Если запрос медленный - логируем предупреждение
            if duration_ms > self.SLOW_REQUEST_THRESHOLD_MS:
                self.logger.warning(
                    f"Slow request detected: {request.method} {request.path}",
                    duration_ms=duration_ms,
                    threshold_ms=self.SLOW_REQUEST_THRESHOLD_MS,
                    request_id=getattr(request, 'request_id', 'unknown'),
                    status_code=response.status_code
                )
        
        return response


class UserContextMiddleware(MiddlewareMixin):
    """
    Middleware для добавления информации о пользователе в контекст логгера.
    
    Добавляет user_id и username в контекст всех логов в рамках запроса.
    """
    
    def __init__(self, get_response: Callable):
        """
        Инициализация middleware.
        
        Args:
            get_response: Следующий middleware или view
        """
        super().__init__(get_response)
        self.get_response = get_response
        self.logger = get_logger('django.request')
    
    def process_request(self, request: HttpRequest) -> None:
        """
        Добавление информации о пользователе в контекст.
        
        Args:
            request: HTTP запрос
        """
        # Если пользователь аутентифицирован
        if hasattr(request, 'user') and request.user.is_authenticated:
            self.logger.set_context(
                user_id=request.user.id,
                username=request.user.username,
                is_staff=request.user.is_staff,
                is_superuser=request.user.is_superuser
            )
