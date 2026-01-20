/**
 * CRM System Application
 * Логика взаимодействия с API и управление UI
 */

const API_BASE_URL = '/api';

// ========================================
// НАВИГАЦИЯ МЕЖДУ ЭКРАНАМИ
// ========================================

/**
 * Показать главный экран
 * Single Responsibility: отвечает только за переключение на главную страницу
 */
function showHomeScreen() {
    // Скрыть все экраны
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Показать главный экран
    const homeScreen = document.getElementById('homeScreen');
    if (homeScreen) {
        homeScreen.classList.add('active');
    }
    
    // Обновить активную навигационную кнопку
    updateNavigationButtons('home');
    
    // Скрыть контролы пользователей в sidebar
    const usersControls = document.getElementById('usersControls');
    if (usersControls) {
        usersControls.style.display = 'none';
    }
}

/**
 * Показать экран пользователей
 * Single Responsibility: отвечает только за переключение на экран пользователей
 */
function showUsersScreen() {
    // Скрыть все экраны
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    
    // Показать экран пользователей
    const usersScreen = document.getElementById('usersScreen');
    if (usersScreen) {
        usersScreen.classList.add('active');
    }
    
    // Обновить активную навигационную кнопку
    updateNavigationButtons('users');
    
    // Показать контролы пользователей в sidebar
    const usersControls = document.getElementById('usersControls');
    if (usersControls) {
        usersControls.style.display = 'block';
    }
    
    // Загрузить пользователей при открытии экрана
    loadUsers();
}

/**
 * Обновить состояние навигационных кнопок
 * @param {string} activeScreen - 'home' или 'users'
 */
function updateNavigationButtons(activeScreen) {
    const navButtons = document.querySelectorAll('.nav-button');
    navButtons.forEach((btn, index) => {
        btn.classList.remove('active');
        if ((activeScreen === 'home' && index === 0) || 
            (activeScreen === 'users' && index === 1)) {
            btn.classList.add('active');
        }
    });
}

// ========================================
// РАБОТА С ПОЛЬЗОВАТЕЛЯМИ (API)
// ========================================

/**
 * Загрузить всех пользователей
 */
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users`);
        const data = await response.json();

        if (data.users) {
            displayUsers(data.users);
            updateContentTitle('Все контакты');
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Ошибка при загрузке контактов');
    }
}

/**
 * Загрузить только активных пользователей
 */
async function loadActiveUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users?status=active`);
        const data = await response.json();

        if (data.users) {
            displayUsers(data.users);
            updateContentTitle('Активные контакты');
        }
    } catch (error) {
        console.error('Error loading active users:', error);
        alert('Ошибка при загрузке активных контактов');
    }
}

/**
 * Отобразить пользователей в таблице
 * @param {Array} users - массив объектов пользователей
 */
function displayUsers(users) {
    const tbody = document.getElementById('tableBody');

    if (!tbody) {
        console.error('Element tableBody not found');
        return;
    }

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px;">Контакты не найдены</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user.id}</td>
            <td>${user.name}</td>
            <td>${user.email}</td>
            <td>${user.phone}</td>
            <td>
                <span class="status-badge status-${user.status}">
                    ${user.status === 'active' ? 'Активный' : 'Неактивный'}
                </span>
            </td>
            <td>
                <button class="btn btn-danger" onclick="deleteUser(${user.id}, '${user.name}')">
                    🗑️ Удалить
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Удалить пользователя
 * @param {number} userId - ID пользователя
 * @param {string} userName - Имя пользователя для подтверждения
 */
async function deleteUser(userId, userName) {
    if (!confirm(`Вы уверены, что хотите удалить контакт "${userName}"?`)) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            alert(data.message || 'Контакт успешно удален');
            loadUsers();
        } else {
            alert(data.error || 'Ошибка при удалении контакта');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Ошибка при удалении контакта');
    }
}

// ========================================
// ФИЛЬТРАЦИЯ И УПРАВЛЕНИЕ
// ========================================

/**
 * Показать всех пользователей и обновить активную кнопку фильтра
 */
function showAll() {
    // Переключить активную кнопку фильтра
    updateFilterButtons(0);
    loadUsers();
}

/**
 * Показать только активных пользователей и обновить активную кнопку фильтра
 */
function showActive() {
    // Переключить активную кнопку фильтра
    updateFilterButtons(1);
    loadActiveUsers();
}

/**
 * Обновить состояние кнопок фильтра
 * @param {number} activeIndex - индекс активной кнопки (0 или 1)
 */
function updateFilterButtons(activeIndex) {
    const filterButtons = document.querySelectorAll('.filter-button');
    filterButtons.forEach((btn, index) => {
        btn.classList.remove('active');
        if (index === activeIndex) {
            btn.classList.add('active');
        }
    });
}

/**
 * Обновить заголовок контента
 * @param {string} title - новый заголовок
 */
function updateContentTitle(title) {
    const titleElement = document.getElementById('contentTitle');
    if (titleElement) {
        titleElement.textContent = title;
    }
}

// ========================================
// МОДАЛЬНОЕ ОКНО
// ========================================

/**
 * Открыть модальное окно добавления контакта
 */
function openModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.add('active');
        const form = document.getElementById('addUserForm');
        if (form) {
            form.reset();
        }
    }
}

/**
 * Закрыть модальное окно
 */
function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// ========================================
// ИНИЦИАЛИЗАЦИЯ
// ========================================

/**
 * Инициализация приложения при загрузке страницы
 */
document.addEventListener('DOMContentLoaded', () => {
    // По умолчанию показываем главный экран
    showHomeScreen();

    // Обработчик формы добавления пользователя
    const form = document.getElementById('addUserForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = {
                name: document.getElementById('userName').value,
                email: document.getElementById('userEmail').value,
                phone: document.getElementById('userPhone').value,
                status: document.getElementById('userStatus').value
            };

            try {
                const response = await fetch(`${API_BASE_URL}/users`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    closeModal();
                    loadUsers();
                    alert('Контакт успешно создан!');
                } else {
                    alert(formatErrorMessage(data.error));
                }
            } catch (error) {
                console.error('Error creating user:', error);
                alert('Ошибка при создании контакта');
            }
        });
    }

    // Закрытие модального окна по клику на overlay
    const modal = document.getElementById('modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'modal') {
                closeModal();
            }
        });
    }
});

// ========================================
// УТИЛИТЫ
// ========================================

/**
 * Форматировать сообщение об ошибке
 * @param {Object|string} error - объект ошибки или строка
 * @returns {string} отформатированное сообщение
 */
function formatErrorMessage(error) {
    if (typeof error === 'object') {
        return Object.entries(error)
            .map(([field, messages]) => `${field}: ${messages}`)
            .join('\n');
    }
    return error;
}
