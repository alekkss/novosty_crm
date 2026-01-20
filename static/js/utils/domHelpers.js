/**
 * DOM Helpers Module
 * Вспомогательные функции для работы с DOM
 * 
 * Single Responsibility: отвечает только за взаимодействие с DOM
 * DRY: избавляет от дублирования кода работы с элементами
 */

import { IS_DEVELOPMENT } from '../config.js';

/**
 * Безопасное получение элемента по ID
 * @param {string} id - ID элемента
 * @param {boolean} required - выбросить ошибку если элемент не найден
 * @returns {HTMLElement|null} найденный элемент или null
 * @throws {Error} если required=true и элемент не найден
 */
export function getElement(id, required = false) {
    const element = document.getElementById(id);
    
    if (!element && required) {
        const error = `Element with ID "${id}" not found`;
        if (IS_DEVELOPMENT) {
            console.error(`[DOM Error] ${error}`);
        }
        throw new Error(error);
    }
    
    return element;
}

/**
 * Безопасное получение всех элементов по селектору
 * @param {string} selector - CSS селектор
 * @returns {NodeList} список найденных элементов
 */
export function getElements(selector) {
    return document.querySelectorAll(selector);
}

/**
 * Безопасное получение первого элемента по селектору
 * @param {string} selector - CSS селектор
 * @param {boolean} required - выбросить ошибку если элемент не найден
 * @returns {HTMLElement|null} найденный элемент или null
 * @throws {Error} если required=true и элемент не найден
 */
export function querySelector(selector, required = false) {
    const element = document.querySelector(selector);
    
    if (!element && required) {
        const error = `Element with selector "${selector}" not found`;
        if (IS_DEVELOPMENT) {
            console.error(`[DOM Error] ${error}`);
        }
        throw new Error(error);
    }
    
    return element;
}

/**
 * Добавить CSS класс к элементу
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} className - имя класса
 */
export function addClass(element, className) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.classList.add(className);
    }
}

/**
 * Удалить CSS класс у элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} className - имя класса
 */
export function removeClass(element, className) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.classList.remove(className);
    }
}

/**
 * Переключить CSS класс у элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} className - имя класса
 */
export function toggleClass(element, className) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.classList.toggle(className);
    }
}

/**
 * Проверить наличие CSS класса у элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} className - имя класса
 * @returns {boolean} true если класс присутствует
 */
export function hasClass(element, className) {
    const el = typeof element === 'string' ? getElement(element) : element;
    return el ? el.classList.contains(className) : false;
}

/**
 * Показать элемент (display: block)
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} displayType - тип display (по умолчанию 'block')
 */
export function show(element, displayType = 'block') {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.style.display = displayType;
    }
}

/**
 * Скрыть элемент (display: none)
 * @param {HTMLElement|string} element - элемент или его ID
 */
export function hide(element) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.style.display = 'none';
    }
}

/**
 * Установить HTML содержимое элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} html - HTML строка
 */
export function setHTML(element, html) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.innerHTML = html;
    }
}

/**
 * Установить текстовое содержимое элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} text - текст
 */
export function setText(element, text) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.textContent = text;
    }
}

/**
 * Получить значение input элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @returns {string} значение элемента
 */
export function getValue(element) {
    const el = typeof element === 'string' ? getElement(element) : element;
    return el ? el.value : '';
}

/**
 * Установить значение input элемента
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} value - новое значение
 */
export function setValue(element, value) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.value = value;
    }
}

/**
 * Добавить обработчик события
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} eventName - имя события (click, submit, etc.)
 * @param {Function} handler - функция-обработчик
 */
export function on(element, eventName, handler) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.addEventListener(eventName, handler);
    }
}

/**
 * Удалить обработчик события
 * @param {HTMLElement|string} element - элемент или его ID
 * @param {string} eventName - имя события
 * @param {Function} handler - функция-обработчик
 */
export function off(element, eventName, handler) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        el.removeEventListener(eventName, handler);
    }
}

/**
 * Сбросить форму
 * @param {HTMLFormElement|string} form - форма или её ID
 */
export function resetForm(form) {
    const el = typeof form === 'string' ? getElement(form) : form;
    if (el && el.tagName === 'FORM') {
        el.reset();
    }
}

/**
 * Итерация по NodeList с callback
 * @param {NodeList|Array} elements - список элементов
 * @param {Function} callback - функция для каждого элемента
 */
export function forEach(elements, callback) {
    Array.from(elements).forEach(callback);
}

/**
 * Удалить все дочерние элементы
 * @param {HTMLElement|string} element - элемент или его ID
 */
export function clearChildren(element) {
    const el = typeof element === 'string' ? getElement(element) : element;
    if (el) {
        while (el.firstChild) {
            el.removeChild(el.firstChild);
        }
    }
}

/**
 * Проверка существования элемента
 * @param {string} id - ID элемента
 * @returns {boolean} true если элемент существует
 */
export function exists(id) {
    return document.getElementById(id) !== null;
}

/**
 * Дождаться загрузки DOM
 * @param {Function} callback - функция для выполнения после загрузки
 */
export function onDOMReady(callback) {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', callback);
    } else {
        callback();
    }
}
