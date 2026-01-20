/**
 * User Service Module
 * Бизнес-логика работы с пользователями
 * 
 * Single Responsibility: отвечает только за операции с данными пользователей
 * Dependency Inversion: зависит от apiClient (абстракция), а не от fetch
 * Interface Segregation: четкий API для работы с пользователями
 */

import { apiClient } from '../utils/api.js';
import { CONFIG } from '../config.js';

/**
 * Класс сервиса для работы с пользователями
 */
class UserService {
    /**
     * Конструктор сервиса
     * @param {ApiClient} client - HTTP клиент для запросов
     */
    constructor(client) {
        this.client = client;
    }

    /**
     * Получить всех пользователей
     * @returns {Promise<Array>} массив пользователей
     * @throws {Error} при ошибке загрузки
     */
    async getAllUsers() {
        try {
            const response = await this.client.get(CONFIG.ENDPOINTS.USERS);
            return response.users || [];
        } catch (error) {
            console.error('[UserService] Error loading all users:', error);
            throw new Error(CONFIG.UI_TEXTS.MESSAGES.ERROR_LOADING);
        }
    }

    /**
     * Получить только активных пользователей
     * @returns {Promise<Array>} массив активных пользователей
     * @throws {Error} при ошибке загрузки
     */
    async getActiveUsers() {
        try {
            const response = await this.client.get(CONFIG.ENDPOINTS.ACTIVE_USERS);
            return response.users || [];
        } catch (error) {
            console.error('[UserService] Error loading active users:', error);
            throw new Error(CONFIG.UI_TEXTS.MESSAGES.ERROR_LOADING);
        }
    }

    /**
     * Получить пользователя по ID
     * @param {number} userId - ID пользователя
     * @returns {Promise<Object>} данные пользователя
     * @throws {Error} при ошибке загрузки
     */
    async getUserById(userId) {
        try {
            console.log(`[UserService] Fetching user ${userId}...`);
            
            // Получаем всех пользователей
            const users = await this.getAllUsers();
            
            // Ищем нужного пользователя
            const user = users.find(u => u.id === parseInt(userId));
            
            if (!user) {
                throw new Error(`Пользователь с ID ${userId} не найден`);
            }
            
            console.log('[UserService] User found:', user);
            return user;
        } catch (error) {
            console.error(`[UserService] Error loading user ${userId}:`, error);
            throw error;
        }
    }

    /**
     * Создать нового пользователя
     * @param {Object} userData - данные пользователя
     * @param {string} userData.name - имя пользователя
     * @param {string} userData.email - email пользователя
     * @param {string} userData.phone - телефон пользователя
     * @param {string} userData.status - статус ('active' или 'inactive')
     * @returns {Promise<Object>} созданный пользователь
     * @throws {Error} при ошибке создания или валидации
     */
    async createUser(userData) {
        // Валидация данных перед отправкой
        this._validateUserData(userData);

        try {
            const response = await this.client.post(CONFIG.ENDPOINTS.USERS, userData);
            return response;
        } catch (error) {
            console.error('[UserService] Error creating user:', error);
            
            // Если ошибка содержит детали от сервера, пробрасываем их
            if (error.data && error.data.error) {
                throw error;
            }
            
            throw new Error(CONFIG.UI_TEXTS.MESSAGES.ERROR_CREATING);
        }
    }

    /**
     * Обновить данные пользователя
     * @param {number} userId - ID пользователя
     * @param {Object} userData - данные для обновления
     * @returns {Promise<Object>} обновленный пользователь
     * @throws {Error} при ошибке обновления
     */
    async updateUser(userId, userData) {
        try {
            const endpoint = CONFIG.ENDPOINTS.USER_BY_ID(userId);
            const response = await this.client.put(endpoint, userData);
            return response;
        } catch (error) {
            console.error(`[UserService] Error updating user ${userId}:`, error);
            throw new Error('Ошибка при обновлении контакта');
        }
    }

    /**
     * Удалить пользователя
     * @param {number} userId - ID пользователя
     * @returns {Promise<Object>} результат удаления
     * @throws {Error} при ошибке удаления
     */
    async deleteUser(userId) {
        try {
            const endpoint = CONFIG.ENDPOINTS.USER_BY_ID(userId);
            const response = await this.client.delete(endpoint);
            return response;
        } catch (error) {
            console.error(`[UserService] Error deleting user ${userId}:`, error);
            throw new Error(CONFIG.UI_TEXTS.MESSAGES.ERROR_DELETING);
        }
    }

    /**
     * Фильтровать пользователей по статусу
     * @param {Array} users - массив пользователей
     * @param {string} status - статус для фильтрации ('active' или 'inactive')
     * @returns {Array} отфильтрованный массив
     */
    filterByStatus(users, status) {
        if (!Array.isArray(users)) {
            return [];
        }
        
        return users.filter(user => user.status === status);
    }

    /**
     * Поиск пользователей по имени или email
     * @param {Array} users - массив пользователей
     * @param {string} query - поисковый запрос
     * @returns {Array} найденные пользователи
     */
    searchUsers(users, query) {
        if (!Array.isArray(users) || !query) {
            return users;
        }

        const lowerQuery = query.toLowerCase();
        
        return users.filter(user => 
            user.name.toLowerCase().includes(lowerQuery) ||
            user.email.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Валидация данных пользователя
     * @param {Object} userData - данные для валидации
     * @throws {Error} если данные невалидны
     * @private
     */
    _validateUserData(userData) {
        const errors = [];

        // Проверка имени
        if (!userData.name || userData.name.trim().length === 0) {
            errors.push('Имя обязательно для заполнения');
        }

        // Проверка email
        if (!userData.email || !this._isValidEmail(userData.email)) {
            errors.push('Введите корректный email');
        }

        // Проверка телефона
        if (!userData.phone || userData.phone.trim().length === 0) {
            errors.push('Телефон обязателен для заполнения');
        }

        // Проверка статуса
        if (!userData.status || !['active', 'inactive'].includes(userData.status)) {
            errors.push('Некорректный статус пользователя');
        }

        if (errors.length > 0) {
            throw new Error(errors.join('\n'));
        }
    }

    /**
     * Проверка валидности email
     * @param {string} email - email для проверки
     * @returns {boolean} true если email валиден
     * @private
     */
    _isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    /**
     * Получить статистику пользователей
     * @param {Array} users - массив пользователей
     * @returns {Object} объект со статистикой
     */
    getStatistics(users) {
        if (!Array.isArray(users)) {
            return {
                total: 0,
                active: 0,
                inactive: 0,
            };
        }

        return {
            total: users.length,
            active: users.filter(u => u.status === 'active').length,
            inactive: users.filter(u => u.status === 'inactive').length,
        };
    }
}

/**
 * Singleton instance сервиса пользователей
 * Инжектим apiClient как зависимость (Dependency Injection)
 */
export const userService = new UserService(apiClient);

/**
 * Экспорт класса для тестирования и создания кастомных экземпляров
 */
export default UserService;
