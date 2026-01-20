/**
 * Frontend Logger Module
 * Централизованное логирование на клиенте с отправкой на backend
 * 
 * Single Responsibility: отвечает только за логирование
 * Dependency Inversion: не зависит от конкретной реализации отправки
 */

import { CONFIG } from '../config.js';

/**
 * Уровни логирования
 */
const LogLevel = {
    DEBUG: 'debug',
    INFO: 'info',
    WARNING: 'warning',
    ERROR: 'error',
    CRITICAL: 'critical'
};

/**
 * Класс логгера для frontend
 */
class FrontendLogger {
    /**
     * Инициализация логгера
     */
    constructor() {
        this.enabled = true;
        this.sendToBackend = true;
        this.logBuffer = [];
        this.flushInterval = 10000; // 10 секунд
        this.maxBufferSize = 50;
        this.sessionId = this._generateSessionId();
        
        // Запускаем периодическую отправку логов
        this._startFlushTimer();
    }
    
    /**
     * Логировать debug сообщение
     * @param {string} message - Сообщение
     * @param {Object} context - Дополнительный контекст
     */
    debug(message, context = {}) {
        this._log(LogLevel.DEBUG, message, context);
    }
    
    /**
     * Логировать info сообщение
     * @param {string} message - Сообщение
     * @param {Object} context - Дополнительный контекст
     */
    info(message, context = {}) {
        this._log(LogLevel.INFO, message, context);
    }
    
    /**
     * Логировать warning
     * @param {string} message - Сообщение
     * @param {Object} context - Дополнительный контекст
     */
    warning(message, context = {}) {
        this._log(LogLevel.WARNING, message, context);
    }
    
    /**
     * Логировать error
     * @param {string} message - Сообщение
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Дополнительный контекст
     */
    error(message, error = null, context = {}) {
        const logData = {
            ...context
        };
        
        if (error) {
            logData.error_type = error.name;
            logData.error_message = error.message;
            logData.stack_trace = error.stack;
        }
        
        this._log(LogLevel.ERROR, message, logData, true);
    }
    
    /**
     * Логировать critical error
     * @param {string} message - Сообщение
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Дополнительный контекст
     */
    critical(message, error = null, context = {}) {
        const logData = {
            ...context
        };
        
        if (error) {
            logData.error_type = error.name;
            logData.error_message = error.message;
            logData.stack_trace = error.stack;
        }
        
        this._log(LogLevel.CRITICAL, message, logData, true);
    }
    
    /**
     * Внутренний метод логирования
     * @param {string} level - Уровень
     * @param {string} message - Сообщение
     * @param {Object} context - Контекст
     * @param {boolean} sendImmediately - Отправить немедленно
     * @private
     */
    _log(level, message, context = {}, sendImmediately = false) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        
        // Логируем в консоль браузера
        this._logToConsole(level, message, context);
        
        // Подготавливаем данные для отправки на backend
        const logEntry = {
            level,
            message,
            timestamp,
            url: window.location.href,
            context: {
                ...context,
                session_id: this.sessionId
            },
            ...this._getBrowserInfo()
        };
        
        // Добавляем в буфер
        this.logBuffer.push(logEntry);
        
        // Отправляем немедленно для ошибок или если буфер заполнен
        if (sendImmediately || this.logBuffer.length >= this.maxBufferSize) {
            this._flushLogs();
        }
    }
    
    /**
     * Логировать в консоль браузера
     * @param {string} level - Уровень
     * @param {string} message - Сообщение
     * @param {Object} context - Контекст
     * @private
     */
    _logToConsole(level, message, context) {
        const timestamp = new Date().toLocaleTimeString();
        const prefix = `[${timestamp}] [${level.toUpperCase()}]`;
        
        switch (level) {
            case LogLevel.DEBUG:
                console.debug(prefix, message, context);
                break;
            case LogLevel.INFO:
                console.info(prefix, message, context);
                break;
            case LogLevel.WARNING:
                console.warn(prefix, message, context);
                break;
            case LogLevel.ERROR:
            case LogLevel.CRITICAL:
                console.error(prefix, message, context);
                break;
            default:
                console.log(prefix, message, context);
        }
    }
    
    /**
     * Получить информацию о браузере
     * @returns {Object} Информация о браузере
     * @private
     */
    _getBrowserInfo() {
        const ua = navigator.userAgent;
        
        return {
            user_agent: ua,
            browser: this._detectBrowser(ua),
            browser_version: this._detectBrowserVersion(ua),
            os: this._detectOS(ua),
            screen_resolution: `${window.screen.width}x${window.screen.height}`
        };
    }
    
    /**
     * Определить браузер
     * @param {string} ua - User agent
     * @returns {string} Название браузера
     * @private
     */
    _detectBrowser(ua) {
        if (ua.indexOf('Firefox') > -1) return 'Firefox';
        if (ua.indexOf('Chrome') > -1) return 'Chrome';
        if (ua.indexOf('Safari') > -1) return 'Safari';
        if (ua.indexOf('Edge') > -1) return 'Edge';
        if (ua.indexOf('Opera') > -1 || ua.indexOf('OPR') > -1) return 'Opera';
        return 'Unknown';
    }
    
    /**
     * Определить версию браузера
     * @param {string} ua - User agent
     * @returns {string} Версия браузера
     * @private
     */
    _detectBrowserVersion(ua) {
        const match = ua.match(/(Firefox|Chrome|Safari|Edge|Opera|OPR)\/(\d+)/);
        return match ? match[2] : 'Unknown';
    }
    
    /**
     * Определить ОС
     * @param {string} ua - User agent
     * @returns {string} Название ОС
     * @private
     */
    _detectOS(ua) {
        if (ua.indexOf('Windows') > -1) return 'Windows';
        if (ua.indexOf('Mac') > -1) return 'MacOS';
        if (ua.indexOf('Linux') > -1) return 'Linux';
        if (ua.indexOf('Android') > -1) return 'Android';
        if (ua.indexOf('iOS') > -1) return 'iOS';
        return 'Unknown';
    }
    
    /**
     * Генерировать ID сессии
     * @returns {string} Session ID
     * @private
     */
    _generateSessionId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    /**
     * Отправить логи на backend
     * @private
     */
    async _flushLogs() {
        if (!this.sendToBackend || this.logBuffer.length === 0) return;
        
        const logsToSend = [...this.logBuffer];
        this.logBuffer = [];
        
        try {
            const response = await fetch('/api/logs/frontend/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    logs: logsToSend
                })
            });
            
            if (!response.ok) {
                console.warn('Failed to send logs to backend:', response.status);
            }
        } catch (error) {
            console.warn('Error sending logs to backend:', error);
            // Возвращаем логи в буфер при ошибке
            this.logBuffer = [...logsToSend, ...this.logBuffer];
        }
    }
    
    /**
     * Запустить таймер периодической отправки
     * @private
     */
    _startFlushTimer() {
        setInterval(() => {
            this._flushLogs();
        }, this.flushInterval);
    }
    
    /**
     * Включить/выключить логирование
     * @param {boolean} enabled
     */
    setEnabled(enabled) {
        this.enabled = enabled;
    }
    
    /**
     * Включить/выключить отправку на backend
     * @param {boolean} enabled
     */
    setSendToBackend(enabled) {
        this.sendToBackend = enabled;
    }
}

// Создаем singleton экземпляр
const logger = new FrontendLogger();

// Экспортируем
export { logger, LogLevel };
export default logger;
