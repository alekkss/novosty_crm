"""
API views for logs application.
Handles frontend log collection.

Single Responsibility: отвечает только за прием и сохранение логов
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from typing import Any, Dict

from apps.logs.models import FrontendLog
from apps.core.logger import get_logger


# Инициализируем логгер
logger = get_logger('frontend')


@method_decorator(csrf_exempt, name='dispatch')
class FrontendLogAPIView(APIView):
    """
    API View для приема логов с frontend.
    
    Endpoint: POST /api/logs/frontend
    
    Принимает логи от JavaScript приложения и сохраняет их в БД.
    """
    
    def post(self, request) -> Response:
        """
        POST /api/logs/frontend
        
        Принять лог с frontend.
        
        Request body:
        {
            "level": "error",
            "message": "User action failed",
            "error_type": "TypeError",
            "error_message": "Cannot read property...",
            "stack_trace": "Error: ...",
            "url": "https://example.com/users",
            "context": {
                "action": "create_user",
                "user_id": 123
            }
        }
        
        Returns:
            Response с подтверждением или ошибкой
        """
        try:
            data = request.data
            
            # Валидация обязательных полей
            if not data.get('level'):
                return Response(
                    {'error': 'Поле level обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not data.get('message'):
                return Response(
                    {'error': 'Поле message обязательно'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Валидация уровня логирования
            valid_levels = [choice[0] for choice in FrontendLog.LEVEL_CHOICES]
            if data['level'] not in valid_levels:
                return Response(
                    {'error': f'Недопустимый уровень. Используйте: {", ".join(valid_levels)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Подготовка данных для сохранения
            log_data = self._prepare_log_data(data, request)
            
            # Сохранение в БД
            frontend_log = FrontendLog.objects.create(**log_data)
            
            # Логируем в backend логи для серьезных ошибок
            if data['level'] in ['error', 'critical']:
                logger.error(
                    f"Frontend {data['level']}: {data['message']}",
                    frontend_log_id=frontend_log.id,
                    url=data.get('url'),
                    error_type=data.get('error_type'),
                    user_id=log_data.get('user_id')
                )
            else:
                logger.info(
                    f"Frontend {data['level']}: {data['message']}",
                    frontend_log_id=frontend_log.id,
                    url=data.get('url')
                )
            
            return Response(
                {
                    'status': 'success',
                    'message': 'Лог успешно сохранен',
                    'log_id': frontend_log.id
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # Логируем ошибку при сохранении лога
            logger.error(
                "Error saving frontend log",
                exception=e,
                request_data=request.data
            )
            
            return Response(
                {'error': 'Ошибка при сохранении лога'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _prepare_log_data(self, data: Dict[str, Any], request) -> Dict[str, Any]:
        """
        Подготовить данные для сохранения в БД.
        
        Args:
            data: Данные из request.data
            request: HTTP request объект
        
        Returns:
            Словарь с данными для создания FrontendLog
        """
        log_data = {
            'level': data['level'],
            'message': data['message'],
        }
        
        # Информация об ошибке
        if 'error_type' in data:
            log_data['error_type'] = data['error_type'][:255]
        
        if 'error_message' in data:
            log_data['error_message'] = data['error_message']
        
        if 'stack_trace' in data:
            log_data['stack_trace'] = data['stack_trace']
        
        # URL и контекст
        if 'url' in data:
            log_data['url'] = data['url'][:500]
        
        if 'context' in data and isinstance(data['context'], dict):
            log_data['context'] = data['context']
        
        # Информация о браузере
        if 'user_agent' in data:
            log_data['user_agent'] = data['user_agent'][:500]
        
        if 'browser' in data:
            log_data['browser'] = data['browser'][:100]
        
        if 'browser_version' in data:
            log_data['browser_version'] = data['browser_version'][:50]
        
        if 'os' in data:
            log_data['os'] = data['os'][:100]
        
        if 'screen_resolution' in data:
            log_data['screen_resolution'] = data['screen_resolution'][:50]
        
        # ID пользователя и сессии
        if 'user_id' in data:
            log_data['user_id'] = data['user_id']
        
        if 'session_id' in data:
            log_data['session_id'] = data['session_id'][:255]
        
        # Timestamp (если передан с фронтенда)
        if 'timestamp' in data:
            from django.utils.dateparse import parse_datetime
            timestamp = parse_datetime(data['timestamp'])
            if timestamp:
                log_data['timestamp'] = timestamp
        
        # Добавляем server-side данные
        log_data['ip_address'] = self._get_client_ip(request)
        
        # Request ID из middleware (если есть)
        if hasattr(request, 'request_id'):
            log_data['request_id'] = request.request_id
        
        # User Agent из заголовков (если не передан с фронта)
        if 'user_agent' not in log_data:
            log_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return log_data
    
    def _get_client_ip(self, request) -> str:
        """
        Получить IP адрес клиента.
        
        Args:
            request: HTTP request объект
        
        Returns:
            IP адрес клиента
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        
        return ip


@method_decorator(csrf_exempt, name='dispatch')
class FrontendLogStatsAPIView(APIView):
    """
    API View для получения статистики по frontend логам.
    
    Endpoint: GET /api/logs/frontend/stats
    """
    
    def get(self, request) -> Response:
        """
        GET /api/logs/frontend/stats
        
        Получить статистику по логам.
        
        Query Parameters:
            hours (optional): За сколько часов (по умолчанию 24)
        
        Returns:
            Статистика по уровням логирования
        """
        try:
            hours = int(request.GET.get('hours', 24))
            
            from datetime import timedelta
            from django.utils import timezone
            from django.db.models import Count
            
            since = timezone.now() - timedelta(hours=hours)
            
            # Подсчитываем логи по уровням
            stats = FrontendLog.objects.filter(
                timestamp__gte=since
            ).values('level').annotate(
                count=Count('id')
            ).order_by('level')
            
            # Подсчитываем нерешенные ошибки
            unresolved_errors = FrontendLog.objects.filter(
                level__in=['error', 'critical'],
                is_resolved=False,
                is_ignored=False,
                timestamp__gte=since
            ).count()
            
            # Форматируем результат
            stats_dict = {item['level']: item['count'] for item in stats}
            
            return Response({
                'period_hours': hours,
                'stats': stats_dict,
                'unresolved_errors': unresolved_errors,
                'total': sum(stats_dict.values())
            })
            
        except ValueError:
            return Response(
                {'error': 'Параметр hours должен быть числом'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        except Exception as e:
            logger.error(
                "Error getting frontend log stats",
                exception=e
            )
            
            return Response(
                {'error': 'Ошибка при получении статистики'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FrontendLogBatchAPIView(APIView):
    """
    API View для приема пакетных логов с frontend.
    
    Endpoint: POST /api/logs/frontend/batch
    
    Позволяет отправить несколько логов за один запрос (эффективнее).
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request) -> Response:
        """
        POST /api/logs/frontend/batch
        
        Принять несколько логов одновременно.
        
        Request body:
        {
            "logs": [
                {
                    "level": "info",
                    "message": "User logged in"
                },
                {
                    "level": "error",
                    "message": "Failed to load data"
                }
            ]
        }
        
        Returns:
            Response с количеством сохраненных логов
        """
        try:
            data = request.data
            
            if 'logs' not in data or not isinstance(data['logs'], list):
                return Response(
                    {'error': 'Требуется массив logs'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(data['logs']) > 100:
                return Response(
                    {'error': 'Максимум 100 логов за запрос'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаем экземпляр FrontendLogAPIView для переиспользования логики
            single_log_view = FrontendLogAPIView()
            
            saved_count = 0
            errors = []
            
            for idx, log_item in enumerate(data['logs']):
                try:
                    # Валидация и подготовка данных
                    if 'level' not in log_item or 'message' not in log_item:
                        errors.append(f"Log {idx}: отсутствуют обязательные поля")
                        continue
                    
                    log_data = single_log_view._prepare_log_data(log_item, request)
                    FrontendLog.objects.create(**log_data)
                    saved_count += 1
                    
                except Exception as e:
                    errors.append(f"Log {idx}: {str(e)}")
            
            logger.info(
                f"Batch frontend logs saved",
                saved_count=saved_count,
                total_count=len(data['logs']),
                errors_count=len(errors)
            )
            
            response_data = {
                'status': 'success',
                'saved': saved_count,
                'total': len(data['logs'])
            }
            
            if errors:
                response_data['errors'] = errors
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(
                "Error saving batch frontend logs",
                exception=e
            )
            
            return Response(
                {'error': 'Ошибка при сохранении логов'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
