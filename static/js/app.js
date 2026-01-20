/**
 * Application Entry Point
 * Главная точка входа приложения
 * 
 * Single Responsibility: координация и инициализация модулей
 * Dependency Inversion: связывает модули через их публичные интерфейсы
 */

import { CONFIG } from './config.js';
import { screenManager } from './navigation/screenManager.js';
import { userService } from './users/userService.js';
import { userUI } from './users/userUI.js';
import { modalManager } from './modals/modalManager.js';
import { onDOMReady } from './utils/domHelpers.js';

/**
 * Главный класс приложения
 * Координирует работу всех модулей
 */
class Application {
    /**
     * Конструктор приложения
     */
    constructor() {
        this.isInitialized = false;
        this.currentFilter = CONFIG.FILTERS.ALL;
    }

    /**
     * Инициализация приложения
     * Запускается после загрузки DOM
     */
    async init() {
        if (this.isInitialized) {
            console.warn('[App] Application already initialized');
            return;
        }

        try {
            // Инициализируем все модули
            this._initModules();

            // Устанавливаем обработчики событий
            this._setupEventHandlers();

            // Регистрируем глобальные функции для HTML onclick
            this._registerGlobalHandlers();

            // Инициализируем экраны
            screenManager.init();

            this.isInitialized = true;
            console.log('[App] Application initialized successfully');
        } catch (error) {
            console.error('[App] Initialization error:', error);
            alert('Ошибка инициализации приложения');
        }
    }

    /**
     * Инициализация модулей
     * @private
     */
    _initModules() {
        // UI модули
        userUI.init();
        modalManager.init();
        
        // Менеджер экранов уже имеет метод init
        // screenManager.init() - вызывается отдельно
    }

    /**
     * Установка обработчиков событий
     * @private
     */
    _setupEventHandlers() {
        // Обработчик смены экрана
        screenManager.onScreenChange((screenName) => {
            this._handleScreenChange(screenName);
        });

        // Обработчик отправки формы добавления пользователя
        modalManager.onSubmit('addUser', async (formData) => {
            await this._handleCreateUser(formData);
        });

        // Обработчик удаления пользователя (через UI callback)
        userUI.onDeleteUser(async (userId, userName) => {
            await this._handleDeleteUser(userId, userName);
        });
    }

    /**
     * Регистрация глобальных функций для HTML onclick
     * @private
     */
    _registerGlobalHandlers() {
        // Навигация между экранами
        window.showHomeScreen = () => screenManager.showHome();
        window.showUsersScreen = () => screenManager.showUsers();

        // Управление пользователями
        window.showAll = () => this.loadAllUsers();
        window.showActive = () => this.loadActiveUsers();
        
        // Модальные окна
        window.openModal = () => modalManager.open('addUser');
        window.closeModal = () => modalManager.close('addUser');

        // Удаление пользователя
        window.handleDeleteUser = async (userId, userName) => {
            await this._handleDeleteUser(userId, userName);
        };
    }

    /**
     * Обработчик смены экрана
     * @param {string} screenName - имя экрана
     * @private
     */
    _handleScreenChange(screenName) {
        console.log(`[App] Screen changed to: ${screenName}`);

        // При переходе на экран пользователей - загружаем их
        if (screenName === 'users') {
            this.loadAllUsers();
        }
    }

    /**
     * Загрузить всех пользователей
     */
    async loadAllUsers() {
        this.currentFilter = CONFIG.FILTERS.ALL;
        await this._loadUsers(() => userService.getAllUsers(), CONFIG.UI_TEXTS.TITLES.ALL_CONTACTS);
        this._updateFilterButtons(CONFIG.FILTERS.ALL);
    }

    /**
     * Загрузить активных пользователей
     */
    async loadActiveUsers() {
        this.currentFilter = CONFIG.FILTERS.ACTIVE;
        await this._loadUsers(() => userService.getActiveUsers(), CONFIG.UI_TEXTS.TITLES.ACTIVE_CONTACTS);
        this._updateFilterButtons(CONFIG.FILTERS.ACTIVE);
    }

    /**
     * Общая функция загрузки пользователей
     * @param {Function} loadFunction - функция загрузки
     * @param {string} title - заголовок для отображения
     * @private
     */
    async _loadUsers(loadFunction, title) {
        try {
            // Показываем индикатор загрузки
            userUI.showLoading();
            userUI.updateTitle(title);

            // Загружаем данные
            const users = await loadFunction();

            // Отображаем пользователей
            userUI.displayUsers(users);
        } catch (error) {
            console.error('[App] Error loading users:', error);
            userUI.showError(error.message || CONFIG.UI_TEXTS.MESSAGES.ERROR_LOADING);
        }
    }

    /**
     * Обработчик создания пользователя
     * @param {Object} formData - данные формы
     * @private
     */
    async _handleCreateUser(formData) {
        try {
            // Создаем пользователя через сервис
            await userService.createUser(formData);

            // Закрываем модальное окно
            modalManager.close('addUser');

            // Показываем сообщение об успехе
            alert(CONFIG.UI_TEXTS.MESSAGES.CONTACT_CREATED);

            // Перезагружаем список пользователей с учетом текущего фильтра
            if (this.currentFilter === CONFIG.FILTERS.ACTIVE) {
                await this.loadActiveUsers();
            } else {
                await this.loadAllUsers();
            }
        } catch (error) {
            console.error('[App] Error creating user:', error);
            
            // Форматируем ошибку для отображения
            const errorMessage = this._formatErrorMessage(error);
            alert(errorMessage);
        }
    }

    /**
     * Обработчик удаления пользователя
     * @param {number} userId - ID пользователя
     * @param {string} userName - имя пользователя
     * @private
     */
    async _handleDeleteUser(userId, userName) {
        // Запрашиваем подтверждение
        const confirmed = confirm(CONFIG.UI_TEXTS.CONFIRMATIONS.DELETE_USER(userName));
        
        if (!confirmed) {
            return;
        }

        try {
            // Удаляем через сервис
            const response = await userService.deleteUser(userId);

            // Показываем сообщение об успехе
            alert(response.message || CONFIG.UI_TEXTS.MESSAGES.CONTACT_DELETED);

            // Удаляем строку из таблицы с анимацией
            userUI.removeUserRow(userId);
        } catch (error) {
            console.error('[App] Error deleting user:', error);
            alert(error.message || CONFIG.UI_TEXTS.MESSAGES.ERROR_DELETING);
        }
    }

    /**
     * Обновить состояние кнопок фильтра
     * @param {number} activeFilter - индекс активного фильтра
     * @private
     */
    _updateFilterButtons(activeFilter) {
        const filterButtons = document.querySelectorAll('.filter-button');
        
        filterButtons.forEach((btn, index) => {
            btn.classList.remove(CONFIG.CSS_CLASSES.ACTIVE);
            
            if (index === activeFilter) {
                btn.classList.add(CONFIG.CSS_CLASSES.ACTIVE);
            }
        });
    }

    /**
     * Форматировать сообщение об ошибке
     * @param {Error} error - объект ошибки
     * @returns {string} отформатированное сообщение
     * @private
     */
    _formatErrorMessage(error) {
        // Если ошибка содержит данные от сервера
        if (error.data && error.data.error) {
            const serverError = error.data.error;
            
            // Если это объект с полями
            if (typeof serverError === 'object') {
                return Object.entries(serverError)
                    .map(([field, messages]) => `${field}: ${messages}`)
                    .join('\n');
            }
            
            return serverError;
        }

        return error.message || CONFIG.UI_TEXTS.MESSAGES.ERROR_CREATING;
    }

    /**
     * Перезагрузить текущий список пользователей
     */
    async reloadUsers() {
        if (this.currentFilter === CONFIG.FILTERS.ACTIVE) {
            await this.loadActiveUsers();
        } else {
            await this.loadAllUsers();
        }
    }

    /**
     * Получить статус приложения
     * @returns {Object} объект со статусом
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            currentScreen: screenManager.getCurrentScreen(),
            currentFilter: this.currentFilter,
        };
    }
}

/**
 * Создаем единственный экземпляр приложения
 */
const app = new Application();

/**
 * Инициализация при загрузке DOM
 */
onDOMReady(() => {
    app.init();
});

/**
 * Экспортируем экземпляр приложения для доступа из консоли
 */
window.app = app;

/**
 * Экспорт для модульной системы
 */
export default app;
