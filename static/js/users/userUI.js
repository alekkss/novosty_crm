/**
 * User UI Module
 * Отображение пользователей в интерфейсе
 * 
 * Single Responsibility: отвечает только за рендеринг UI пользователей
 * Separation of Concerns: отделен от бизнес-логики (userService)
 */

import { CONFIG } from '../config.js';
import {
    getElement,
    setHTML,
    setText,
} from '../utils/domHelpers.js';

/**
 * Класс для управления UI пользователей
 */
class UserUI {
    /**
     * Конструктор UI менеджера
     */
    constructor() {
        this.tableBody = null;
        this.contentTitle = null;
        this.deleteCallback = null;
    }

    /**
     * Инициализация UI компонента
     * Получает ссылки на DOM элементы
     */
    init() {
        this.tableBody = getElement(CONFIG.DOM_IDS.TABLE_BODY);
        this.contentTitle = getElement(CONFIG.DOM_IDS.CONTENT_TITLE);
    }

    /**
     * Отобразить список пользователей в таблице
     * @param {Array} users - массив пользователей
     */
    displayUsers(users) {
        if (!this.tableBody) {
            console.error('[UserUI] Table body element not found');
            return;
        }

        // Если пользователей нет - показываем пустое состояние
        if (!users || users.length === 0) {
            this._displayEmptyState();
            return;
        }

        // Генерируем HTML для каждого пользователя
        const html = users.map(user => this._createUserRow(user)).join('');
        setHTML(this.tableBody, html);
    }

    /**
     * Обновить заголовок контента
     * @param {string} title - новый заголовок
     */
    updateTitle(title) {
        if (this.contentTitle) {
            setText(this.contentTitle, title);
        }
    }

    /**
     * Показать состояние загрузки
     */
    showLoading() {
        if (!this.tableBody) return;

        const loadingHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <div class="loading-spinner">⏳ Загрузка...</div>
                </td>
            </tr>
        `;
        setHTML(this.tableBody, loadingHTML);
    }

    /**
     * Показать сообщение об ошибке
     * @param {string} errorMessage - текст ошибки
     */
    showError(errorMessage) {
        if (!this.tableBody) return;

        const errorHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px; color: #e74c3c;">
                    <div class="error-message">
                        <div style="font-size: 48px; margin-bottom: 15px;">⚠️</div>
                        <div style="font-size: 16px; font-weight: 600;">${errorMessage}</div>
                    </div>
                </td>
            </tr>
        `;
        setHTML(this.tableBody, errorHTML);
    }

    /**
     * Зарегистрировать callback для удаления пользователя
     * @param {Function} callback - функция (userId, userName)
     */
    onDeleteUser(callback) {
        this.deleteCallback = callback;
    }

    /**
     * Очистить таблицу
     */
    clear() {
        if (this.tableBody) {
            setHTML(this.tableBody, '');
        }
    }

    /**
     * Создать HTML строку для пользователя
     * @param {Object} user - данные пользователя
     * @returns {string} HTML строка
     * @private
     */
    _createUserRow(user) {
        const statusClass = user.status === 'active' 
            ? CONFIG.CSS_CLASSES.STATUS_ACTIVE 
            : CONFIG.CSS_CLASSES.STATUS_INACTIVE;
        
        const statusText = user.status === 'active'
            ? CONFIG.UI_TEXTS.STATUS_LABELS.ACTIVE
            : CONFIG.UI_TEXTS.STATUS_LABELS.INACTIVE;

        // Экранируем данные для безопасности (XSS защита)
        const safeUser = {
            id: this._escapeHtml(String(user.id)),
            name: this._escapeHtml(user.name),
            email: this._escapeHtml(user.email),
            phone: this._escapeHtml(user.phone),
        };

        return `
            <tr data-user-id="${safeUser.id}">
                <td>${safeUser.id}</td>
                <td>${safeUser.name}</td>
                <td>${safeUser.email}</td>
                <td>${safeUser.phone}</td>
                <td>
                    <span class="${CONFIG.CSS_CLASSES.STATUS_BADGE} ${statusClass}">
                        ${statusText}
                    </span>
                </td>
                <td>
                    <button 
                        class="btn btn-danger" 
                        onclick="window.handleDeleteUser(${user.id}, '${this._escapeHtml(user.name)}')"
                    >
                        🗑️ Удалить
                    </button>
                </td>
            </tr>
        `;
    }

    /**
     * Отобразить пустое состояние (нет пользователей)
     * @private
     */
    _displayEmptyState() {
        const emptyHTML = `
            <tr>
                <td colspan="6" style="text-align: center; padding: 40px;">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div style="color: #7f8c8d; font-size: 16px;">
                            ${CONFIG.UI_TEXTS.MESSAGES.NO_CONTACTS}
                        </div>
                    </div>
                </td>
            </tr>
        `;
        setHTML(this.tableBody, emptyHTML);
    }

    /**
     * Экранирование HTML для защиты от XSS
     * @param {string} text - текст для экранирования
     * @returns {string} безопасный текст
     * @private
     */
    _escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, char => map[char]);
    }

    /**
     * Форматирование телефона для отображения
     * @param {string} phone - номер телефона
     * @returns {string} отформатированный номер
     */
    formatPhone(phone) {
        // Пример: 79001234567 -> +7 (900) 123-45-67
        if (!phone) return '';
        
        const cleaned = phone.replace(/\D/g, '');
        
        if (cleaned.length === 11 && cleaned.startsWith('7')) {
            return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9)}`;
        }
        
        return phone;
    }

    /**
     * Получить элемент строки пользователя по ID
     * @param {number} userId - ID пользователя
     * @returns {HTMLElement|null} элемент строки
     */
    getUserRow(userId) {
        if (!this.tableBody) return null;
        return this.tableBody.querySelector(`tr[data-user-id="${userId}"]`);
    }

    /**
     * Удалить строку пользователя из таблицы (визуально)
     * @param {number} userId - ID пользователя
     */
    removeUserRow(userId) {
        const row = this.getUserRow(userId);
        if (row) {
            // Плавное удаление с анимацией
            row.style.transition = 'opacity 0.3s ease';
            row.style.opacity = '0';
            
            setTimeout(() => {
                row.remove();
                
                // Если таблица пустая - показываем empty state
                const remainingRows = this.tableBody.querySelectorAll('tr');
                if (remainingRows.length === 0) {
                    this._displayEmptyState();
                }
            }, 300);
        }
    }

    /**
     * Подсветить строку пользователя (например, после создания)
     * @param {number} userId - ID пользователя
     */
    highlightUserRow(userId) {
        const row = this.getUserRow(userId);
        if (row) {
            row.style.backgroundColor = '#d4edda';
            
            setTimeout(() => {
                row.style.transition = 'background-color 1s ease';
                row.style.backgroundColor = '';
            }, 2000);
        }
    }
}

/**
 * Singleton instance UI менеджера пользователей
 */
export const userUI = new UserUI();

/**
 * Экспорт класса для тестирования
 */
export default UserUI;
