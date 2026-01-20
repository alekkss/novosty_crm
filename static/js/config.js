/**
 * Application Configuration
 * Централизованное хранение всех конфигурационных параметров приложения
 * 
 * Single Responsibility: отвечает только за хранение конфигурации
 * Open/Closed: легко добавлять новые параметры без изменения существующих
 */

export const CONFIG = Object.freeze({
    /**
     * Базовый URL для API запросов
     */
    API_BASE_URL: '/api',

    /**
     * Endpoints для работы с пользователями
     */
    ENDPOINTS: {
        USERS: '/users',
        USER_BY_ID: (id) => `/users/${id}`,
        ACTIVE_USERS: '/users?status=active',
    },

    /**
     * Идентификаторы DOM элементов
     * Централизованное управление селекторами для избежания опечаток
     */
    DOM_IDS: {
        // Экраны
        HOME_SCREEN: 'homeScreen',
        USERS_SCREEN: 'usersScreen',
        
        // Контролы
        USERS_CONTROLS: 'usersControls',
        
        // Таблица пользователей
        TABLE_BODY: 'tableBody',
        USERS_TABLE: 'usersTable',
        CONTENT_TITLE: 'contentTitle',
        CONTENT_SUBTITLE: 'contentSubtitle',
        
        // Модальное окно
        MODAL: 'modal',
        ADD_USER_FORM: 'addUserForm',
        USER_NAME: 'userName',
        USER_EMAIL: 'userEmail',
        USER_PHONE: 'userPhone',
        USER_STATUS: 'userStatus',

        // Редактирование
        EDIT_MODAL: 'editModal',
        EDIT_USER_FORM: 'editUserForm',
        EDIT_USER_ID: 'editUserId',
        EDIT_USER_NAME: 'editUserName',
        EDIT_USER_EMAIL: 'editUserEmail',
        EDIT_USER_PHONE: 'editUserPhone',
        EDIT_USER_STATUS: 'editUserStatus',
    },

    /**
     * CSS классы для управления состояниями
     */
    CSS_CLASSES: {
        ACTIVE: 'active',
        SCREEN: 'screen',
        NAV_BUTTON: 'nav-button',
        FILTER_BUTTON: 'filter-button',
        STATUS_BADGE: 'status-badge',
        STATUS_ACTIVE: 'status-active',
        STATUS_INACTIVE: 'status-inactive',
    },

    /**
     * Тексты интерфейса
     */
    UI_TEXTS: {
        TITLES: {
            ALL_CONTACTS: 'Все контакты',
            ACTIVE_CONTACTS: 'Активные контакты',
        },
        MESSAGES: {
            CONTACT_CREATED: 'Контакт успешно создан!',
            CONTACT_DELETED: 'Контакт успешно удален',
            ERROR_LOADING: 'Ошибка при загрузке контактов',
            ERROR_CREATING: 'Ошибка при создании контакта',
            ERROR_DELETING: 'Ошибка при удалении контакта',
            NO_CONTACTS: 'Контакты не найдены',
            CONTACT_UPDATED: 'Контакт успешно обновлен!',
            ERROR_UPDATING: 'Ошибка при обновлении контакта',
        },
        CONFIRMATIONS: {
            DELETE_USER: (name) => `Вы уверены, что хотите удалить контакт "${name}"?`,
            UPDATE_USER: (name) => `Сохранить изменения для "${name}"?`,
        },
        STATUS_LABELS: {
            ACTIVE: 'Активный',
            INACTIVE: 'Неактивный',
        },
    },

    /**
     * Настройки навигации
     */
    NAVIGATION: {
        SCREENS: {
            HOME: 'home',
            USERS: 'users',
        },
        DEFAULT_SCREEN: 'home',
    },

    /**
     * Настройки фильтров пользователей
     */
    FILTERS: {
        ALL: 0,
        ACTIVE: 1,
    },
});

/**
 * Вспомогательная функция для получения полного URL endpoint'а
 * @param {string} endpoint - относительный путь endpoint'а
 * @returns {string} полный URL
 */
export function getApiUrl(endpoint) {
    return `${CONFIG.API_BASE_URL}${endpoint}`;
}

/**
 * Проверка окружения (dev/prod)
 */
export const IS_DEVELOPMENT = window.location.hostname === 'localhost' || 
                              window.location.hostname === '127.0.0.1';

/**
 * Настройки для разработки
 */
export const DEV_CONFIG = Object.freeze({
    ENABLE_LOGGING: true,
    DEBUG_MODE: true,
});
