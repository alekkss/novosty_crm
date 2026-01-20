/**
 * CRM System Application
 * Логика взаимодействия с API и управление UI
 */

const API_BASE_URL = '/api';

// Load all users
async function loadUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users`);
        const data = await response.json();

        if (data.users) {
            displayUsers(data.users);
        }
    } catch (error) {
        console.error('Error loading users:', error);
        alert('Ошибка при загрузке контактов');
    }
}

// Load active users only
async function loadActiveUsers() {
    try {
        const response = await fetch(`${API_BASE_URL}/users?status=active`);
        const data = await response.json();

        if (data.users) {
            displayUsers(data.users);
        }
    } catch (error) {
        console.error('Error loading active users:', error);
        alert('Ошибка при загрузке активных контактов');
    }
}

// Display users in table
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

// Delete user
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

// Wrapper functions for HTML buttons
function showAll() {
    // Переключить активную кнопку
    document.querySelectorAll('.menu-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.menu-button')[0].classList.add('active');
    
    loadUsers();
}

function showActive() {
    // Переключить активную кнопку
    document.querySelectorAll('.menu-button').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.menu-button')[1].classList.add('active');
    
    loadActiveUsers();
}

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

function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUsers();

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

    const modal = document.getElementById('modal');
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target.id === 'modal') {
                closeModal();
            }
        });
    }
});

// Format error message
function formatErrorMessage(error) {
    if (typeof error === 'object') {
        return Object.entries(error)
            .map(([field, messages]) => `${field}: ${messages}`)
            .join('\n');
    }
    return error;
}
