/**
 * Modal Manager Module
 * Управление модальными окнами приложения
 * 
 * Single Responsibility: отвечает только за управление модальными окнами
 * Open/Closed: легко добавить новые модальные окна
 */

import { CONFIG } from '../config.js';
import {
    getElement,
    addClass,
    removeClass,
    hasClass,
    on,
    resetForm,
    getValue,
} from '../utils/domHelpers.js';

/**
 * Класс для управления модальными окнами
 */
class ModalManager {
    /**
     * Конструктор менеджера модальных окон
     */
    constructor() {
        this.modals = new Map();
        this.currentModal = null;
        this.callbacks = {
            onSubmit: new Map(),
            onClose: new Map(),
        };
    }

    /**
     * Инициализация менеджера
     * Регистрирует модальные окна и обработчики событий
     */
    init() {
        // Регистрируем модальное окно добавления пользователя
        this.registerModal('addUser', CONFIG.DOM_IDS.MODAL, CONFIG.DOM_IDS.ADD_USER_FORM);
        
        // Устанавливаем обработчики
        this._setupEventListeners();
    }

    /**
     * Зарегистрировать модальное окно
     * @param {string} name - имя модального окна
     * @param {string} modalId - ID DOM элемента модального окна
     * @param {string} formId - ID формы внутри модального окна (опционально)
     */
    registerModal(name, modalId, formId = null) {
        const modal = {
            name,
            element: getElement(modalId),
            form: formId ? getElement(formId) : null,
        };

        if (!modal.element) {
            console.error(`[ModalManager] Modal element "${modalId}" not found`);
            return;
        }

        this.modals.set(name, modal);
    }

    /**
     * Открыть модальное окно
     * @param {string} name - имя модального окна
     */
    open(name) {
        const modal = this.modals.get(name);
        
        if (!modal) {
            console.error(`[ModalManager] Modal "${name}" not registered`);
            return;
        }

        // Добавляем класс active для отображения
        addClass(modal.element, CONFIG.CSS_CLASSES.ACTIVE);
        
        // Сбрасываем форму если есть
        if (modal.form) {
            resetForm(modal.form);
        }

        // Сохраняем текущее модальное окно
        this.currentModal = name;

        // Блокируем прокрутку body
        this._lockBodyScroll();

        // Фокус на первое поле ввода
        this._focusFirstInput(modal);
    }

    /**
     * Закрыть модальное окно
     * @param {string} name - имя модального окна (опционально, если не указано - закрывает текущее)
     */
    close(name = null) {
        const modalName = name || this.currentModal;
        
        if (!modalName) {
            return;
        }

        const modal = this.modals.get(modalName);
        
        if (!modal) {
            return;
        }

        // Убираем класс active
        removeClass(modal.element, CONFIG.CSS_CLASSES.ACTIVE);
        
        // Сбрасываем форму
        if (modal.form) {
            resetForm(modal.form);
        }

        // Разблокируем прокрутку body
        this._unlockBodyScroll();

        // Вызываем callback закрытия
        this._triggerCallback('onClose', modalName);

        // Сбрасываем текущее модальное окно
        if (this.currentModal === modalName) {
            this.currentModal = null;
        }
    }

    /**
     * Проверить открыто ли модальное окно
     * @param {string} name - имя модального окна
     * @returns {boolean} true если открыто
     */
    isOpen(name) {
        const modal = this.modals.get(name);
        return modal ? hasClass(modal.element, CONFIG.CSS_CLASSES.ACTIVE) : false;
    }

    /**
     * Получить данные из формы модального окна
     * @param {string} name - имя модального окна
     * @returns {Object|null} данные формы
     */
    getFormData(name) {
        const modal = this.modals.get(name);
        
        if (!modal || !modal.form) {
            return null;
        }

        // Специфичная логика для формы добавления пользователя
        if (name === 'addUser') {
            return {
                name: getValue(CONFIG.DOM_IDS.USER_NAME),
                email: getValue(CONFIG.DOM_IDS.USER_EMAIL),
                phone: getValue(CONFIG.DOM_IDS.USER_PHONE),
                status: getValue(CONFIG.DOM_IDS.USER_STATUS),
            };
        }

        // Общая логика для других форм
        return this._getGenericFormData(modal.form);
    }

    /**
     * Зарегистрировать callback на отправку формы
     * @param {string} modalName - имя модального окна
     * @param {Function} callback - функция обработчик
     */
    onSubmit(modalName, callback) {
        if (typeof callback === 'function') {
            this.callbacks.onSubmit.set(modalName, callback);
        }
    }

    /**
     * Зарегистрировать callback на закрытие
     * @param {string} modalName - имя модального окна
     * @param {Function} callback - функция обработчик
     */
    onClose(modalName, callback) {
        if (typeof callback === 'function') {
            this.callbacks.onClose.set(modalName, callback);
        }
    }

    /**
     * Установить обработчики событий
     * @private
     */
    _setupEventListeners() {
        this.modals.forEach((modal, name) => {
            // Закрытие по клику на overlay
            if (modal.element) {
                on(modal.element, 'click', (e) => {
                    if (e.target === modal.element) {
                        this.close(name);
                    }
                });
            }

            // Обработка отправки формы
            if (modal.form) {
                on(modal.form, 'submit', (e) => {
                    e.preventDefault();
                    this._handleFormSubmit(name);
                });
            }
        });

        // Закрытие по Escape
        on(document, 'keydown', (e) => {
            if (e.key === 'Escape' && this.currentModal) {
                this.close();
            }
        });
    }

    /**
     * Обработка отправки формы
     * @param {string} modalName - имя модального окна
     * @private
     */
    async _handleFormSubmit(modalName) {
        const callback = this.callbacks.onSubmit.get(modalName);
        
        if (!callback) {
            console.warn(`[ModalManager] No submit callback for modal "${modalName}"`);
            return;
        }

        // Получаем данные формы
        const formData = this.getFormData(modalName);
        
        if (!formData) {
            console.error(`[ModalManager] Could not get form data for modal "${modalName}"`);
            return;
        }

        try {
            // Вызываем callback с данными формы
            await callback(formData);
        } catch (error) {
            console.error(`[ModalManager] Error in submit callback:`, error);
            throw error;
        }
    }

    /**
     * Вызвать callback
     * @param {string} event - тип события
     * @param {string} modalName - имя модального окна
     * @param {...any} args - аргументы для callback
     * @private
     */
    _triggerCallback(event, modalName, ...args) {
        const callback = this.callbacks[event].get(modalName);
        
        if (callback && typeof callback === 'function') {
            try {
                callback(...args);
            } catch (error) {
                console.error(`[ModalManager] Error in ${event} callback:`, error);
            }
        }
    }

    /**
     * Блокировать прокрутку body
     * @private
     */
    _lockBodyScroll() {
        document.body.style.overflow = 'hidden';
    }

    /**
     * Разблокировать прокрутку body
     * @private
     */
    _unlockBodyScroll() {
        document.body.style.overflow = '';
    }

    /**
     * Установить фокус на первое поле ввода
     * @param {Object} modal - объект модального окна
     * @private
     */
    _focusFirstInput(modal) {
        if (!modal.form) return;

        setTimeout(() => {
            const firstInput = modal.form.querySelector('input, textarea, select');
            if (firstInput) {
                firstInput.focus();
            }
        }, 100);
    }

    /**
     * Получить данные из формы (generic)
     * @param {HTMLFormElement} form - форма
     * @returns {Object} данные формы
     * @private
     */
    _getGenericFormData(form) {
        const formData = new FormData(form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    /**
     * Очистить все callback'и
     */
    clearCallbacks() {
        this.callbacks.onSubmit.clear();
        this.callbacks.onClose.clear();
    }

    /**
     * Удалить модальное окно из реестра
     * @param {string} name - имя модального окна
     */
    unregisterModal(name) {
        this.modals.delete(name);
        this.callbacks.onSubmit.delete(name);
        this.callbacks.onClose.delete(name);
    }
}

/**
 * Singleton instance менеджера модальных окон
 */
export const modalManager = new ModalManager();

/**
 * Экспорт класса для тестирования
 */
export default ModalManager;
