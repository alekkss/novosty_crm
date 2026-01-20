# DEPLOYMENT.md

## Novosty CRM - Техническая документация по развертыванию

### Описание проекта
Novosty CRM - веб-приложение для управления контактами клиентов, построенное на Django с использованием архитектурного паттерна Repository-Service на backend и модульной компонентной архитектуры на frontend.

**Технологический стек:**
- Backend: Django 5.1.4
- Frontend: ES6 JavaScript Modules + Modular CSS + Django Templates
- WSGI Server: Gunicorn 21.2.0
- Web Server: Nginx 1.24.0
- Database: SQLite3
- Python: 3.10+

---

## Архитектура проекта

### Структура директорий
```
/var/www/novosty-top.ru/
├── config/                      # Основная конфигурация Django
│   ├── settings.py              # Настройки проекта
│   ├── urls.py                  # Главный роутинг
│   └── wsgi.py                  # WSGI точка входа
├── apps/
│   └── contacts/                # Приложение управления контактами
│       ├── admin.py             # Django Admin панель
│       ├── apps.py              # Конфигурация приложения
│       ├── models.py            # Модели данных (Contact)
│       ├── serializers.py       # DRF сериализаторы
│       ├── repositories.py      # Слой доступа к данным
│       ├── services.py          # Бизнес-логика
│       ├── views.py             # API эндпоинты
│       └── urls.py              # Роутинг приложения
├── templates/                   # Django шаблоны (модульные)
│   ├── base.html                # Базовый шаблон (наследование)
│   ├── index.html               # Главная страница (сборка компонентов)
│   ├── components/              # Переиспользуемые компоненты
│   │   ├── navigation.html      # Навигационное меню
│   │   └── sidebar_controls.html # Контролы sidebar
│   ├── screens/                 # Экраны приложения
│   │   ├── home_screen.html     # Главный экран
│   │   └── users_screen.html    # Экран пользователей
│   └── modals/                  # Модальные окна
│       └── add_user_modal.html  # Добавление пользователя
        ├── edit_user_modal.html # Редактирование пользователя
├── static/                      # Исходные статические файлы
│   ├── css/                     # Модульные стили
│   │   ├── main.css             # Точка входа CSS (импорты)
│   │   ├── base.css             # Базовые стили, переменные, reset
│   │   ├── layout.css           # Структура страницы, grid
│   │   ├── navigation.css       # Стили навигации
│   │   └── components/          # Стили компонентов
│   │       ├── buttons.css      # Все типы кнопок
│   │       ├── tables.css       # Таблицы и состояния
│   │       ├── cards.css        # Карточки dashboard
│   │       ├── modals.css       # Модальные окна
│   │       └── forms.css        # Формы и валидация
│   └── js/                      # ES6 модули JavaScript
│       ├── app.js               # Точка входа приложения
│       ├── config.js            # Конфигурация и константы
│       ├── api/                 # API слой
│       │   └── apiClient.js     # HTTP клиент (fetch wrapper)
│       ├── users/               # User management модуль
│       │   ├── userService.js   # Бизнес-логика пользователей
│       │   └── userUI.js        # UI рендеринг пользователей
│       ├── navigation/          # Navigation модуль
│       │   └── screenManager.js # Управление экранами
│       ├── modals/              # Modals модуль
│       │   └── modalManager.js  # Управление модальными окнами
│       └── utils/               # Утилиты
│           └── domHelpers.js    # DOM манипуляции
├── staticfiles/                 # Собранная статика (collectstatic)
├── logs/                        # Логи приложения
│   ├── gunicorn_error.log
│   └── gunicorn_access.log
├── venv/                        # Виртуальное окружение Python
├── db.sqlite3                   # База данных SQLite
├── manage.py                    # Django management утилита
└── gunicorn_config.py           # Конфигурация Gunicorn

/etc/nginx/sites-available/
└── novosty-top.ru               # Nginx конфигурация

/etc/systemd/system/
└── novosty_crm.service          # Systemd сервис
```

### Архитектурные слои

#### Backend (Django)

**1. Presentation Layer (views.py)**
- Обработка HTTP запросов
- Валидация входящих данных
- Формирование HTTP ответов

**2. Business Logic Layer (services.py)**
- Бизнес-правила и логика
- Обработка исключений
- Координация между слоями

**3. Data Access Layer (repositories.py)**
- Абстракция работы с БД
- CRUD операции
- Оптимизация запросов

**4. Data Layer (models.py)**
- ORM модели Django
- Связи между сущностями
- Валидация на уровне БД

#### Frontend (ES6 Modules + Modular CSS)

**1. Application Layer (app.js)**
- Точка входа приложения
- Инициализация модулей
- Координация компонентов

**2. Presentation Layer (UI модули)**
- userUI.js - рендеринг пользователей
- modalManager.js - управление модальными окнами
- screenManager.js - переключение экранов

**3. Business Logic Layer (Service модули)**
- userService.js - логика работы с пользователями
- Валидация данных
- Обработка ошибок

**4. Data Layer (API модуль)**
- apiClient.js - HTTP клиент
- Взаимодействие с backend API
- Обработка responses/errors

**5. Utility Layer**
- config.js - константы и конфигурация
- domHelpers.js - DOM утилиты

**Применение SOLID принципов во frontend:**
- **Single Responsibility:** Каждый модуль отвечает за одну задачу
- **Open/Closed:** Легко расширяем без изменения существующего кода
- **Liskov Substitution:** Компоненты взаимозаменяемы
- **Interface Segregation:** Минимальные зависимости между модулями
- **Dependency Inversion:** Зависимости через интерфейсы, не реализации

---

## Требования к системе

### Минимальные требования
- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** 512 MB (рекомендуется 1 GB)
- **Disk:** 5 GB свободного места
- **CPU:** 1 ядро (рекомендуется 2+)

### Необходимое ПО
```bash
sudo apt update && sudo apt install -y \
    python3.10 \
    python3.10-venv \
    python3-pip \
    nginx \
    git \
    certbot \
    python3-certbot-nginx
```

---

## Пошаговое развертывание

### Шаг 1: Подготовка сервера

```bash
# Создать директорию проекта
sudo mkdir -p /var/www/novosty-top.ru
sudo chown -R $USER:$USER /var/www/novosty-top.ru
cd /var/www/novosty-top.ru

# Создать директории для логов
mkdir -p logs
```

### Шаг 2: Развертывание кода

```bash
# Скопировать файлы проекта в /var/www/novosty-top.ru/
# Или клонировать из репозитория:
# git clone <repository-url> .

# Создать виртуальное окружение
python3.10 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install django==5.1.4 djangorestframework gunicorn
```

### Шаг 3: Конфигурация Django

**config/settings.py - ключевые настройки:**

```python
DEBUG = False
ALLOWED_HOSTS = ['novosty-top.ru', 'www.novosty-top.ru', '77.222.47.245']

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Статика
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Безопасность
CSRF_TRUSTED_ORIGINS = ['https://novosty-top.ru', 'https://www.novosty-top.ru']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Шаг 4: Инициализация базы данных

```bash
cd /var/www/novosty-top.ru
source venv/bin/activate

# Применить миграции
python manage.py makemigrations
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Собрать статику
python manage.py collectstatic --noinput
```

### Шаг 5: Конфигурация Gunicorn

**Создать файл gunicorn_config.py:**

```python
bind = '127.0.0.1:8001'
workers = 5
worker_class = 'sync'
timeout = 120
keepalive = 5

accesslog = '/var/www/novosty-top.ru/logs/gunicorn_access.log'
errorlog = '/var/www/novosty-top.ru/logs/gunicorn_error.log'
loglevel = 'info'

daemon = False
pidfile = None
```

**Тест запуска:**
```bash
cd /var/www/novosty-top.ru
source venv/bin/activate
gunicorn --config gunicorn_config.py config.wsgi:application
```

### Шаг 6: Настройка Systemd сервиса

**Создать /etc/systemd/system/novosty_crm.service:**

```ini
[Unit]
Description=Novosty CRM Django Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/novosty-top.ru
Environment="PATH=/var/www/novosty-top.ru/venv/bin"
ExecStart=/var/www/novosty-top.ru/venv/bin/gunicorn \
    --config /var/www/novosty-top.ru/gunicorn_config.py \
    config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

**Активация сервиса:**

```bash
# Установить права на файлы
sudo chown -R www-data:www-data /var/www/novosty-top.ru
sudo chmod -R 755 /var/www/novosty-top.ru

# Запустить сервис
sudo systemctl daemon-reload
sudo systemctl enable novosty_crm
sudo systemctl start novosty_crm

# Проверить статус
sudo systemctl status novosty_crm
```

### Шаг 7: Конфигурация Nginx

**Создать /etc/nginx/sites-available/novosty-top.ru:**

```nginx
# HTTP -> HTTPS редирект
server {
    listen 80;
    listen [::]:80;
    server_name novosty-top.ru www.novosty-top.ru;
    return 301 https://$host$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name novosty-top.ru www.novosty-top.ru;

    # SSL сертификаты (после certbot)
    ssl_certificate /etc/letsencrypt/live/novosty-top.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/novosty-top.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Общие настройки
    client_max_body_size 10M;
    charset utf-8;

    # Статические файлы
    location /static/ {
        alias /var/www/novosty-top.ru/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API эндпоинты
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Оптимизация для POST запросов
        proxy_buffering off;
        proxy_request_buffering off;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Фронтенд
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Логи
    access_log /var/log/nginx/novosty_access.log;
    error_log /var/log/nginx/novosty_error.log;
}
```

**Активация конфигурации:**

```bash
# Создать симлинк
sudo ln -s /etc/nginx/sites-available/novosty-top.ru /etc/nginx/sites-enabled/

# Проверить конфигурацию
sudo nginx -t

# Перезапустить Nginx
sudo systemctl restart nginx
```

### Шаг 8: Получение SSL сертификата

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d novosty-top.ru -d www.novosty-top.ru

# Проверить автообновление
sudo certbot renew --dry-run
```

### Шаг 9: Настройка Firewall

```bash
# Разрешить порты
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Активировать firewall
sudo ufw enable

# Проверить статус
sudo ufw status
```

---

## API Эндпоинты

### Contact Management API

**1. Получить все контакты**
```http
GET /api/users
```
**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "name": "Иван Иванов",
      "email": "ivan@example.com",
      "phone": "79001234567",
      "status": "active"
    }
  ]
}
```

**2. Получить активные контакты**
```http
GET /api/users?status=active
```

**3. Создать контакт**
```http
POST /api/users
Content-Type: application/json

{
  "name": "Петр Петров",
  "email": "petr@example.com",
  "phone": "79009876543",
  "status": "active"
}
```

**4. Обновить контакт**
```http
PUT /api/users/<id>
Content-Type: application/json

{
  "name": "Петр Петров Updated",
  "email": "petr@example.com",
  "phone": "79009876543",
  "status": "inactive"
}
Особенности:

Email можно оставить прежним - валидация исключит текущий контакт

Все поля обязательны для заполнения

Статус может быть только 'active' или 'inactive'

Response (success):

json
{
  "message": "Контакт успешно обновлен",
  "contact": {
    "id": 1,
    "name": "Петр Петров Updated",
    "email": "petr@example.com",
    "phone": "79009876543",
    "status": "inactive"
  }
}
Response (email занят другим контактом):

json
{
  "error": {
    "email": ["Контакт с таким email уже существует"]
  }
}
***

## В секцию "Модульная архитектура Frontend" → "JavaScript (ES6 Modules)"

**Добавить ПОСЛЕ "Структура зависимостей":**

```markdown
**Реализованная функциональность:**
- ✅ Просмотр списка контактов (все/активные)
- ✅ Создание нового контакта
- ✅ **Редактирование контакта** (модальное окно, валидация email)
- ✅ Удаление контакта с подтверждением
- ✅ Фильтрация по статусу
- ✅ Обработка ошибок валидации


**5. Удалить контакт**
```http
DELETE /api/users/<id>
```

---

## Управление сервисом

### Основные команды

```bash
# Запуск/остановка
sudo systemctl start novosty_crm
sudo systemctl stop novosty_crm
sudo systemctl restart novosty_crm

# Перезагрузка конфигурации (без downtime)
sudo systemctl reload novosty_crm

# Статус
sudo systemctl status novosty_crm

# Включить автозапуск
sudo systemctl enable novosty_crm

# Отключить автозапуск
sudo systemctl disable novosty_crm

# Логи
sudo journalctl -u novosty_crm -f
tail -f /var/www/novosty-top.ru/logs/gunicorn_error.log
```

### Обновление кода (модульная архитектура)

```bash
# 1. Перейти в директорию проекта
cd /var/www/novosty-top.ru

# 2. Активировать venv
source venv/bin/activate

# 3. Обновить код
# Для git:
git pull origin main

# Или вручную обновить файлы:
# - Backend: apps/contacts/*.py, config/*.py
# - Frontend JS: static/js/**/*.js
# - Frontend CSS: static/css/**/*.css
# - Templates: templates/**/*.html

# 4. Установить новые зависимости (если есть)
pip install -r requirements.txt

# 5. Применить миграции (если есть изменения в models.py)
python manage.py makemigrations
python manage.py migrate

# 6. Собрать статику (обязательно после изменений CSS/JS)
python manage.py collectstatic --noinput

# 7. Перезапустить сервис
sudo systemctl restart novosty_crm

# 8. Проверить статус
sudo systemctl status novosty_crm

# 9. Проверить логи на ошибки
sudo journalctl -u novosty_crm -n 50
```

**Примечание:** При обновлении frontend файлов (JS/CSS/Templates) важно выполнить `collectstatic`, чтобы изменения попали в `staticfiles/` директорию, которую использует Nginx.

### Быстрое обновление только frontend

```bash
cd /var/www/novosty-top.ru
source venv/bin/activate

# Обновить статику
python manage.py collectstatic --noinput

# Перезапустить (для обновления шаблонов)
sudo systemctl restart novosty_crm
```

---

## Модульная архитектура Frontend

### JavaScript (ES6 Modules)

**Преимущества:**
- ✅ Модульность - каждый файл имеет одну ответственность
- ✅ Переиспользование - нет дублирования кода
- ✅ Тестируемость - легко покрыть unit-тестами
- ✅ Масштабируемость - легко добавить новые модули
- ✅ Читаемость - понятная структура, легко найти код

**Подключение в HTML:**
```html
<script type="module" src="{% static 'js/app.js' %}"></script>
```

**Структура зависимостей:**
```
app.js (точка входа)
├── config.js (константы)
├── screenManager.js (навигация)
├── modalManager.js (модальные окна)
├── userService.js (бизнес-логика)
│   └── apiClient.js (HTTP запросы)
├── userUI.js (рендеринг UI)
│   └── domHelpers.js (DOM утилиты)
└── domHelpers.js (утилиты)
```

### CSS (Modular CSS)

**Преимущества:**
- ✅ CSS Variables - централизованные цвета/размеры
- ✅ Компонентный подход - стили изолированы
- ✅ Переиспользование - utility классы
- ✅ Responsive - адаптивность под все устройства
- ✅ Accessibility - WCAG 2.1 AA compliance

**Подключение в HTML:**
```html
<link rel="stylesheet" href="{% static 'css/main.css' %}">
```

**Порядок импорта в main.css:**
```css
@import url('base.css');           /* 1. Базовые стили */
@import url('layout.css');         /* 2. Структура */
@import url('navigation.css');     /* 3. Навигация */
@import url('components/buttons.css');  /* 4. Компоненты */
@import url('components/forms.css');
@import url('components/tables.css');
@import url('components/cards.css');
@import url('components/modals.css');
```

### HTML Templates (Component-Based)

**Преимущества:**
- ✅ DRY - компоненты через {% include %}
- ✅ Maintainability - изменения в одном месте
- ✅ Semantic HTML - SEO и accessibility
- ✅ Django Integration - template inheritance
- ✅ Extensibility - легко добавить компоненты

**Структура:**
```
templates/
├── base.html                      # Базовый шаблон
├── index.html                     # Главная (сборка)
├── components/                    # Переиспользуемые
│   ├── navigation.html
│   └── sidebar_controls.html
├── screens/                       # Экраны
│   ├── home_screen.html
│   └── users_screen.html
└── modals/                        # Модальные окна
    └── add_user_modal.html
```

---

## Мониторинг и логи

### Пути к логам

```bash
# Gunicorn логи
/var/www/novosty-top.ru/logs/gunicorn_error.log
/var/www/novosty-top.ru/logs/gunicorn_access.log

# Nginx логи
/var/log/nginx/novosty_access.log
/var/log/nginx/novosty_error.log

# Systemd логи
journalctl -u novosty_crm
```

### Просмотр логов в реальном времени

```bash
# Gunicorn errors
tail -f /var/www/novosty-top.ru/logs/gunicorn_error.log

# Nginx access
tail -f /var/log/nginx/novosty_access.log

# Все логи сервиса
sudo journalctl -u novosty_crm -f
```

### Ротация логов

**Создать /etc/logrotate.d/novosty_crm:**

```
/var/www/novosty-top.ru/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    missingok
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload novosty_crm > /dev/null 2>&1 || true
    endscript
}
```

---

## Troubleshooting

### Проблема: 502 Bad Gateway

**Причины и решения:**

1. **Gunicorn не запущен**
```bash
sudo systemctl status novosty_crm
sudo systemctl start novosty_crm
```

2. **Неверный порт в nginx**
```bash
# Проверить что Gunicorn слушает 127.0.0.1:8001
sudo lsof -i:8001
# Должно показать gunicorn процессы
```

3. **Неверный ALLOWED_HOSTS в Django**
```python
# config/settings.py
ALLOWED_HOSTS = ['novosty-top.ru', 'www.novosty-top.ru']
```

### Проблема: Статика не загружается

```bash
# Пересобрать статику
cd /var/www/novosty-top.ru
source venv/bin/activate
python manage.py collectstatic --noinput

# Проверить права
sudo chown -R www-data:www-data /var/www/novosty-top.ru/staticfiles/
sudo chmod -R 755 /var/www/novosty-top.ru/staticfiles/
```

### Проблема: JavaScript модули не работают

**Возможные причины:**

1. **Не указан type="module"**
```html
<!-- Неправильно -->
<script src="{% static 'js/app.js' %}"></script>

<!-- Правильно -->
<script type="module" src="{% static 'js/app.js' %}"></script>
```

2. **Не собрана статика**
```bash
python manage.py collectstatic --noinput
```

3. **CORS ошибки (проверить в консоли браузера)**
```bash
# Проверить что staticfiles отдаются правильно
curl -I https://novosty-top.ru/static/js/app.js
```

### Проблема: CSS не применяется

```bash
# 1. Проверить что main.css импортирует все модули
cat /var/www/novosty-top.ru/static/css/main.css

# 2. Пересобрать статику
python manage.py collectstatic --noinput

# 3. Проверить права
ls -la /var/www/novosty-top.ru/staticfiles/css/

# 4. Очистить кэш браузера (Ctrl+Shift+R)
```

### Проблема: Database is locked

```bash
# Проверить права на db.sqlite3
sudo chown www-data:www-data /var/www/novosty-top.ru/db.sqlite3
sudo chmod 664 /var/www/novosty-top.ru/db.sqlite3

# Проверить права на директорию
sudo chown www-data:www-data /var/www/novosty-top.ru/
```

### Проблема: Permission denied

```bash
# Установить правильные права на весь проект
sudo chown -R www-data:www-data /var/www/novosty-top.ru/
sudo chmod -R 755 /var/www/novosty-top.ru/

# Дать права на запись для логов
sudo chmod -R 775 /var/www/novosty-top.ru/logs/
```

### Проблема: DNS не обновился

```bash
# Проверить DNS
nslookup novosty-top.ru 8.8.8.8

# Очистить DNS кэш (на клиенте)
# Windows: ipconfig /flushdns
# Linux: sudo systemd-resolve --flush-caches
```

---

## Бэкап и восстановление

### Создание бэкапа

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/var/backups/novosty_crm"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/var/www/novosty-top.ru"

mkdir -p $BACKUP_DIR

# Бэкап базы данных
cp $PROJECT_DIR/db.sqlite3 $BACKUP_DIR/db_$DATE.sqlite3

# Бэкап кода (опционально)
tar -czf $BACKUP_DIR/code_$DATE.tar.gz \
    $PROJECT_DIR \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs' \
    --exclude='staticfiles'

# Удалить бэкапы старше 30 дней
find $BACKUP_DIR -name "*.sqlite3" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Настроить автоматический бэкап через cron:**

```bash
# Добавить в crontab
sudo crontab -e

# Бэкап каждый день в 03:00
0 3 * * * /usr/local/bin/backup_novosty_crm.sh
```

### Восстановление из бэкапа

```bash
# Остановить сервис
sudo systemctl stop novosty_crm

# Восстановить базу
cp /var/backups/novosty_crm/db_20260120_030000.sqlite3 \
   /var/www/novosty-top.ru/db.sqlite3

# Установить права
sudo chown www-data:www-data /var/www/novosty-top.ru/db.sqlite3

# Запустить сервис
sudo systemctl start novosty_crm
```

---

## Производительность и масштабирование

### Оптимизация Gunicorn

```python
# gunicorn_config.py

# Формула для workers: (2 * CPU_CORES) + 1
workers = 5

# Для большой нагрузки использовать async workers
worker_class = 'gevent'  # требует: pip install gevent
worker_connections = 1000

# Тайм-ауты
timeout = 120
graceful_timeout = 30
keepalive = 5

# Предзагрузка кода (быстрее рестарт)
preload_app = True
```

### Кэширование в Django

```python
# config/settings.py

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Или file-based cache для простоты
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}
```

### Мониторинг производительности

```bash
# Установить htop для мониторинга
sudo apt install htop

# Мониторинг процессов
htop

# Мониторинг сети
sudo apt install nethogs
sudo nethogs

# Мониторинг дисков
df -h
iostat -x 1
```

---

## Безопасность

### Чек-лист безопасности

- [ ] DEBUG = False в production
- [ ] SECRET_KEY в переменных окружения (не в коде)
- [ ] ALLOWED_HOSTS настроен правильно
- [ ] SSL сертификат установлен и валиден
- [ ] CSRF_TRUSTED_ORIGINS настроен
- [ ] Firewall активен (ufw)
- [ ] Регулярные бэкапы настроены
- [ ] Логи ротируются
- [ ] PostgreSQL вместо SQLite для production (рекомендуется)
- [ ] Обновления безопасности установлены

### Использование переменных окружения

```bash
# Создать .env файл
nano /var/www/novosty-top.ru/.env
```

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=novosty-top.ru,www.novosty-top.ru
DATABASE_URL=sqlite:///db.sqlite3
```

**Установить python-dotenv:**
```bash
pip install python-dotenv
```

**В settings.py:**
```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
```

---

## Контакты и поддержка

**Разработчик:** Александр  
**Email:** support@novosty-top.ru  
**Домен:** https://novosty-top.ru

**Версия документации:** 2.0  
**Дата обновления:** 20 января 2026

---

## Changelog

### v2.0 (20.01.2026)
- ✨ **Модульная архитектура frontend:**
  - JavaScript: 8 ES6 модулей (app.js, config.js, apiClient.js, userService.js, userUI.js, screenManager.js, modalManager.js, domHelpers.js)
  - CSS: 9 модульных файлов (main.css, base.css, layout.css, navigation.css, buttons.css, tables.css, cards.css, modals.css, forms.css)
  - HTML Templates: 7 компонентных шаблонов (base.html, index.html, components/, screens/, modals/)
- ✅ **SOLID принципы во frontend**
- ✅ **Улучшенная maintainability и scalability**
- ✅ **Component-based architecture**
- 📝 Обновлена документация по развертыванию
- 📝 Добавлена секция troubleshooting для модульной архитектуры

### v1.0 (15.01.2026)
- Первоначальное развертывание на VPS 77.222.47.245
- Django 5.1.4 + Gunicorn + Nginx
- SSL сертификат от Let's Encrypt
- Repository-Service архитектура
- SQLite база данных
- Contact Management API
