/**
 * API Client Module
 * Базовый HTTP клиент для работы с REST API
 * 
 * Single Responsibility: отвечает только за выполнение HTTP запросов
 * Dependency Inversion: другие модули зависят от этой абстракции, а не от fetch напрямую
 * Open/Closed: легко расширить новыми методами (PATCH, etc.)
 */

import { getApiUrl, IS_DEVELOPMENT } from '../config.js';

/**
 * Базовый класс для работы с API
 * Инкапсулирует логику HTTP запросов
 */
class ApiClient {
    /**
     * Конструктор API клиента
     */
    constructor() {
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Логирование запросов (только в dev режиме)
     * @param {string} method - HTTP метод
     * @param {string} url - URL запроса
     * @param {Object} data - данные запроса
     * @private
     */
    _log(method, url, data = null) {
        if (IS_DEVELOPMENT) {
            console.log(`[API] ${method} ${url}`, data || '');
        }
    }

    /**
     * Обработка ответа от сервера
     * @param {Response} response - объект Response от fetch
     * @returns {Promise<Object>} распарсенные данные
     * @throws {Error} если статус не 2xx
     * @private
     */
    async _handleResponse(response) {
        const data = await response.json();

        if (!response.ok) {
            // Бросаем ошибку с данными от сервера
            const error = new Error(data.error || 'Ошибка сервера');
            error.status = response.status;
            error.data = data;
            throw error;
        }

        return data;
    }

    /**
     * Обработка ошибок запроса
     * @param {Error} error - объект ошибки
     * @param {string} defaultMessage - сообщение по умолчанию
     * @throws {Error} отформатированная ошибка
     * @private
     */
    _handleError(error, defaultMessage) {
        if (IS_DEVELOPMENT) {
            console.error('[API Error]', error);
        }

        // Если ошибка сети
        if (!error.status) {
            throw new Error('Ошибка сети. Проверьте подключение к интернету.');
        }

        // Иначе пробрасываем ошибку дальше
        throw error;
    }

    /**
     * GET запрос
     * @param {string} endpoint - относительный путь API
     * @returns {Promise<Object>} данные ответа
     */
    async get(endpoint) {
        const url = getApiUrl(endpoint);
        this._log('GET', url);

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: this.defaultHeaders,
            });

            return await this._handleResponse(response);
        } catch (error) {
            this._handleError(error, 'Ошибка при получении данных');
        }
    }

    /**
     * POST запрос
     * @param {string} endpoint - относительный путь API
     * @param {Object} data - данные для отправки
     * @returns {Promise<Object>} данные ответа
     */
    async post(endpoint, data) {
        const url = getApiUrl(endpoint);
        this._log('POST', url, data);

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: this.defaultHeaders,
                body: JSON.stringify(data),
            });

            return await this._handleResponse(response);
        } catch (error) {
            this._handleError(error, 'Ошибка при создании данных');
        }
    }

    /**
     * PUT запрос
     * @param {string} endpoint - относительный путь API
     * @param {Object} data - данные для обновления
     * @returns {Promise<Object>} данные ответа
     */
    async put(endpoint, data) {
        const url = getApiUrl(endpoint);
        this._log('PUT', url, data);

        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: this.defaultHeaders,
                body: JSON.stringify(data),
            });

            return await this._handleResponse(response);
        } catch (error) {
            this._handleError(error, 'Ошибка при обновлении данных');
        }
    }

    /**
     * DELETE запрос
     * @param {string} endpoint - относительный путь API
     * @returns {Promise<Object>} данные ответа
     */
    async delete(endpoint) {
        const url = getApiUrl(endpoint);
        this._log('DELETE', url);

        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: this.defaultHeaders,
            });

            return await this._handleResponse(response);
        } catch (error) {
            this._handleError(error, 'Ошибка при удалении данных');
        }
    }

    /**
     * PATCH запрос (для частичного обновления)
     * @param {string} endpoint - относительный путь API
     * @param {Object} data - данные для обновления
     * @returns {Promise<Object>} данные ответа
     */
    async patch(endpoint, data) {
        const url = getApiUrl(endpoint);
        this._log('PATCH', url, data);

        try {
            const response = await fetch(url, {
                method: 'PATCH',
                headers: this.defaultHeaders,
                body: JSON.stringify(data),
            });

            return await this._handleResponse(response);
        } catch (error) {
            this._handleError(error, 'Ошибка при обновлении данных');
        }
    }
}

/**
 * Singleton instance API клиента
 * Используем один экземпляр во всем приложении
 */
export const apiClient = new ApiClient();

/**
 * Экспорт класса для возможности создания кастомных экземпляров
 * (например, с другими заголовками для разных API)
 */
export default ApiClient;
