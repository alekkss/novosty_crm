/**
 * Error Handler Module
 * Глобальная обработка ошибок JavaScript
 * 
 * Single Responsibility: отвечает только за отлов и обработку ошибок
 */

import logger from './logger.js';

/**
 * Класс для глобальной обработки ошибок
 */
class ErrorHandler {
    /**
     * Инициализация обработчика ошибок
     */
    constructor() {
        this.initialized = false;
        this.errorCount = 0;
        this.maxErrorsPerMinute = 10;
        this.errorTimestamps = [];
    }
    
    /**
     * Инициализировать глобальные обработчики
     */
    init() {
        if (this.initialized) {
            logger.warning('ErrorHandler already initialized');
            return;
        }
        
        this._setupWindowErrorHandler();
        this._setupUnhandledRejectionHandler();
        this._setupConsoleErrorProxy();
        
        this.initialized = true;
        logger.info('ErrorHandler initialized');
    }
    
    /**
     * Установить обработчик window.onerror
     * @private
     */
    _setupWindowErrorHandler() {
        window.addEventListener('error', (event) => {
            // Проверяем rate limiting
            if (!this._checkRateLimit()) {
                return;
            }
            
            const error = {
                message: event.message,
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                error: event.error
            };
            
            logger.error(
                `Uncaught error: ${error.message}`,
                error.error,
                {
                    filename: error.filename,
                    line: error.lineno,
                    column: error.colno,
                    type: 'window.error'
                }
            );
            
            // Не предотвращаем дефолтное поведение
            return false;
        });
    }
    
    /**
     * Установить обработчик unhandledrejection
     * @private
     */
    _setupUnhandledRejectionHandler() {
        window.addEventListener('unhandledrejection', (event) => {
            // Проверяем rate limiting
            if (!this._checkRateLimit()) {
                return;
            }
            
            const reason = event.reason;
            let errorMessage = 'Unhandled Promise rejection';
            let errorObj = null;
            
            if (reason instanceof Error) {
                errorMessage = reason.message;
                errorObj = reason;
            } else if (typeof reason === 'string') {
                errorMessage = reason;
            } else {
                errorMessage = JSON.stringify(reason);
            }
            
            logger.error(
                `Unhandled Promise rejection: ${errorMessage}`,
                errorObj,
                {
                    reason: reason,
                    type: 'unhandledrejection'
                }
            );
            
            // Предотвращаем дефолтное поведение (чтобы не показывать в консоли дважды)
            event.preventDefault();
        });
    }
    
    /**
     * Проксировать console.error для отлова всех ошибок
     * @private
     */
    _setupConsoleErrorProxy() {
        const originalConsoleError = console.error;
        
        console.error = (...args) => {
            // Вызываем оригинальный console.error
            originalConsoleError.apply(console, args);
            
            // Логируем через наш logger (если это не наш собственный лог)
            const message = args.map(arg => {
                if (arg instanceof Error) {
                    return arg.message;
                }
                return String(arg);
            }).join(' ');
            
            // Проверяем что это не наш собственный лог
            if (!message.includes('[ERROR]')) {
                logger.warning(
                    `Console error: ${message}`,
                    {
                        type: 'console.error',
                        args: args.map(arg => String(arg))
                    }
                );
            }
        };
    }
    
    /**
     * Проверить rate limiting (не более N ошибок в минуту)
     * @returns {boolean} Можно ли логировать
     * @private
     */
    _checkRateLimit() {
        const now = Date.now();
        const oneMinuteAgo = now - 60000;
        
        // Удаляем старые timestamps
        this.errorTimestamps = this.errorTimestamps.filter(
            timestamp => timestamp > oneMinuteAgo
        );
        
        // Проверяем лимит
        if (this.errorTimestamps.length >= this.maxErrorsPerMinute) {
            console.warn('Error rate limit exceeded, skipping error logging');
            return false;
        }
        
        // Добавляем текущий timestamp
        this.errorTimestamps.push(now);
        return true;
    }
    
    /**
     * Обработать ошибку вручную
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Дополнительный контекст
     */
    handleError(error, context = {}) {
        if (!this._checkRateLimit()) {
            return;
        }
        
        logger.error(
            error.message || 'Unknown error',
            error,
            {
                ...context,
                type: 'manual'
            }
        );
    }
    
    /**
     * Обработать критичную ошибку
     * @param {Error} error - Объект ошибки
     * @param {Object} context - Дополнительный контекст
     */
    handleCriticalError(error, context = {}) {
        logger.critical(
            error.message || 'Critical error',
            error,
            {
                ...context,
                type: 'critical'
            }
        );
        
        // Можно показать пользователю уведомление о критичной ошибке
        this._showCriticalErrorNotification(error);
    }
    
    /**
     * Показать уведомление о критичной ошибке
     * @param {Error} error - Объект ошибки
     * @private
     */
    _showCriticalErrorNotification(error) {
        // Используем alert как временное решение
        // В будущем можно заменить на красивое модальное окно
        alert(
            'Произошла критическая ошибка.\n' +
            'Пожалуйста, перезагрузите страницу.\n\n' +
            `Детали: ${error.message}`
        );
    }
    
    /**
     * Получить статистику ошибок
     * @returns {Object} Статистика
     */
    getStats() {
        return {
            totalErrors: this.errorCount,
            recentErrors: this.errorTimestamps.length,
            rateLimit: this.maxErrorsPerMinute
        };
    }
}

// Создаем singleton экземпляр
const errorHandler = new ErrorHandler();

// Экспортируем
export default errorHandler;
