/**
 * Screen Manager Module
 * Управление навигацией между экранами приложения
 * 
 * Single Responsibility: отвечает только за переключение экранов
 * Open/Closed: легко добавить новые экраны без изменения существующей логики
 */

import { CONFIG } from '../config.js';
import {
    getElement,
    getElements,
    addClass,
    removeClass,
    show,
    hide,
    forEach
} from '../utils/domHelpers.js';

/**
 * Класс для управления экранами приложения
 */
class ScreenManager {
    /**
     * Конструктор менеджера экранов
     */
    constructor() {
        this.currentScreen = null;
        this.screens = {
            home: CONFIG.DOM_IDS.HOME_SCREEN,
            users: CONFIG.DOM_IDS.USERS_SCREEN,
        };
        this.callbacks = {
            onScreenChange: [],
        };
    }

    /**
     * Инициализация менеджера
     * Устанавливает начальный экран
     */
    init() {
        const defaultScreen = CONFIG.NAVIGATION.DEFAULT_SCREEN;
        this.showScreen(defaultScreen);
    }

    /**
     * Показать конкретный экран
     * @param {string} screenName - имя экрана ('home' или 'users')
     * @param {Object} options - дополнительные опции
     */
    showScreen(screenName, options = {}) {
        // Валидация имени экрана
        if (!this.screens[screenName]) {
            console.error(`Screen "${screenName}" not found`);
            return;
        }

        // Скрыть все экраны
        this._hideAllScreens();

        // Показать нужный экран
        const screenId = this.screens[screenName];
        const screenElement = getElement(screenId);
        
        if (screenElement) {
            addClass(screenElement, CONFIG.CSS_CLASSES.ACTIVE);
        }

        // Обновить навигацию
        this._updateNavigation(screenName);

        // Управление sidebar контролами
        this._toggleSidebarControls(screenName);

        // Сохранить текущий экран
        this.currentScreen = screenName;

        // Вызвать callback'и
        this._triggerCallbacks('onScreenChange', screenName, options);
    }

    /**
     * Показать главный экран
     */
    showHome() {
        this.showScreen(CONFIG.NAVIGATION.SCREENS.HOME);
    }

    /**
     * Показать экран пользователей
     */
    showUsers() {
        this.showScreen(CONFIG.NAVIGATION.SCREENS.USERS);
    }

    /**
     * Получить текущий экран
     * @returns {string} имя текущего экрана
     */
    getCurrentScreen() {
        return this.currentScreen;
    }

    /**
     * Проверка активности экрана
     * @param {string} screenName - имя экрана
     * @returns {boolean} true если экран активен
     */
    isScreenActive(screenName) {
        return this.currentScreen === screenName;
    }

    /**
     * Зарегистрировать callback на изменение экрана
     * @param {Function} callback - функция callback
     */
    onScreenChange(callback) {
        if (typeof callback === 'function') {
            this.callbacks.onScreenChange.push(callback);
        }
    }

    /**
     * Скрыть все экраны
     * @private
     */
    _hideAllScreens() {
        const screens = getElements(`.${CONFIG.CSS_CLASSES.SCREEN}`);
        forEach(screens, (screen) => {
            removeClass(screen, CONFIG.CSS_CLASSES.ACTIVE);
        });
    }

    /**
     * Обновить состояние навигационных кнопок
     * @param {string} activeScreen - активный экран
     * @private
     */
    _updateNavigation(activeScreen) {
        const navButtons = getElements(`.${CONFIG.CSS_CLASSES.NAV_BUTTON}`);
        
        forEach(navButtons, (button, index) => {
            removeClass(button, CONFIG.CSS_CLASSES.ACTIVE);
            
            // Первая кнопка - home, вторая - users
            const isActive = (activeScreen === 'home' && index === 0) ||
                           (activeScreen === 'users' && index === 1);
            
            if (isActive) {
                addClass(button, CONFIG.CSS_CLASSES.ACTIVE);
            }
        });
    }

    /**
     * Управление видимостью sidebar контролов
     * @param {string} screenName - имя экрана
     * @private
     */
    _toggleSidebarControls(screenName) {
        const usersControls = getElement(CONFIG.DOM_IDS.USERS_CONTROLS);
        
        if (!usersControls) return;

        if (screenName === 'users') {
            show(usersControls, 'block');
        } else {
            hide(usersControls);
        }
    }

    /**
     * Вызвать зарегистрированные callback'и
     * @param {string} event - имя события
     * @param {...any} args - аргументы для callback
     * @private
     */
    _triggerCallbacks(event, ...args) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(...args);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }

    /**
     * Очистить все callback'и
     */
    clearCallbacks() {
        Object.keys(this.callbacks).forEach(key => {
            this.callbacks[key] = [];
        });
    }
}

/**
 * Singleton instance менеджера экранов
 * Используем один экземпляр во всем приложении
 */
export const screenManager = new ScreenManager();

/**
 * Экспорт класса для возможности создания кастомных экземпляров
 */
export default ScreenManager;
