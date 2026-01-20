"""
URL Configuration for logs application.
Defines routes for frontend log collection and statistics.

Single Responsibility: отвечает только за маршрутизацию
"""
from django.urls import path
from apps.logs.views import (
    FrontendLogAPIView,
    FrontendLogStatsAPIView,
    FrontendLogBatchAPIView
)


app_name = 'logs'


urlpatterns = [
    # Прием одиночного лога
    path(
        'frontend',
        FrontendLogAPIView.as_view(),
        name='frontend-log'
    ),
    
    # Пакетный прием логов
    path(
        'frontend/batch',
        FrontendLogBatchAPIView.as_view(),
        name='frontend-log-batch'
    ),
    
    # Статистика по логам
    path(
        'frontend/stats',
        FrontendLogStatsAPIView.as_view(),
        name='frontend-log-stats'
    ),
]
