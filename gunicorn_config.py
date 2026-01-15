"""Gunicorn configuration for Django CRM."""
import multiprocessing

bind = "127.0.0.1:8001"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "/var/www/novosty-top.ru/logs/gunicorn_error.log"
accesslog = "/var/www/novosty-top.ru/logs/gunicorn_access.log"
loglevel = "info"
