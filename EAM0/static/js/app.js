/**
 * Alpha-Soft Task Tracker - Kanban Board
 * Full-featured frontend with JWT auth, filters, and role-based UI
 */

// ==================== CONFIGURATION ====================
const API = {
  BASE: '/api',
  AUTH: '/api/auth/token/',
  TASKS: '/api/tasks/',
  PROJECTS: '/api/projects/',
  USERS: '/api/users/',
};

const state = {
  accessToken: localStorage.getItem('access_token'),
  refreshToken: localStorage.getItem('refresh_token'),
  userId: parseInt(localStorage.getItem('user_id'), 10) || null,
  tasks: [],
  projects: [],
  users: [],
  filters: {},
  isLoading: false,
};

// ==================== API CLIENT ====================
async function apiFetch(url, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (state.accessToken) {
    headers['Authorization'] = `Bearer ${state.accessToken}`;
  }

  try {
    let response = await fetch(url, { ...options, headers });

    // Handle 401: try to refresh token
    if (response.status === 401 && !options._retried) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        headers['Authorization'] = `Bearer ${state.accessToken}`;
        return apiFetch(url, { ...options, headers, _retried: true });
      }
      logout();
      throw new Error('Сессия истекла. Пожалуйста, войдите снова.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw { status: response.status, data: errorData };
    }

    return response.status === 204 ? null : await response.json();
  } catch (err) {
    if (err.status) throw err;
    throw new Error(err.message || 'Сетевая ошибка');
  }
}

async function refreshAccessToken() {
  try {
    const res = await fetch(API.AUTH + 'refresh/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh: state.refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    state.accessToken = data.access;
    localStorage.setItem('access_token', data.access);
    return true;
  } catch {
    return false;
  }
}

// ==================== AUTHENTICATION ====================
async function login(username, password) {
  const loginBtn = document.querySelector('#loginForm button[type="submit"]');
  if (loginBtn) {
    loginBtn.disabled = true;
    loginBtn.textContent = 'Вход...';
  }

  try {
    const res = await fetch(API.AUTH, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    
    if (!res.ok) {
      if (res.status === 401) throw new Error('Неверный логин или пароль');
      if (res.status === 404) throw new Error('Эндпоинт авторизации не найден');
      throw new Error(`Ошибка сервера: ${res.status}`);
    }
    
    const data = await res.json();
    state.accessToken = data.access;
    state.refreshToken = data.refresh;
    state.userId = data.user_id || null;
    
    localStorage.setItem('access_token', data.access);
    localStorage.setItem('refresh_token', data.refresh);
    if (state.userId) localStorage.setItem('user_id', state.userId);

    showNotification('Успешный вход!', 'success');
    updateAuthUI(true);
    await Promise.all([loadTasks(), loadProjects(), loadUsers()]);
  } catch (err) {
    console.error('Login error:', err);
    showNotification(err.message, 'error');
  } finally {
    if (loginBtn) {
      loginBtn.disabled = false;
      loginBtn.textContent = 'Войти';
    }
  }
}

function logout() {
  state.accessToken = null;
  state.refreshToken = null;
  state.userId = null;
  localStorage.clear();
  updateAuthUI(false);
  showNotification('Вы вышли из системы', 'info');
}

function updateAuthUI(isLoggedIn) {
  const loginSection = document.getElementById('loginSection');
  const mainContent = document.getElementById('mainContent');
  const userInfo = document.getElementById('userInfo');
  const logoutBtn = document.getElementById('logoutBtn');

  if (loginSection) loginSection.style.display = isLoggedIn ? 'none' : 'flex';
  if (mainContent) mainContent.style.display = isLoggedIn ? 'flex' : 'none';
  
  if (userInfo) {
    userInfo.style.display = isLoggedIn ? 'block' : 'none';
    if (isLoggedIn && state.userId) {
      userInfo.textContent = `ID: ${state.userId}`;
    }
  }
  
  if (logoutBtn) logoutBtn.style.display = isLoggedIn ? 'block' : 'none';
}

// ==================== DATA LOADING ====================
async function loadProjects() {
  try {
    state.projects = await apiFetch(API.PROJECTS);
    populateProjectSelect();
  } catch (err) {
    console.error('Load projects error:', err);
  }
}

async function loadUsers() {
  try {
    state.users = await apiFetch(API.USERS);
    populateUserSelects();
  } catch (err) {
    console.error('Load users error:', err);
  }
}

async function loadTasks(filters = {}) {
  state.isLoading = true;
  state.filters = filters;
  
  const taskList = document.querySelector('.kanban-board');
  if (taskList) {
    taskList.style.opacity = '0.5';
  }
  
  try {
    const params = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, val]) => {
      if (key === 'performer' && val === 'null') {
        params.append('performer__isnull', 'true');
      } else if (val) {
        params.append(key, val);
      }
    });

    const query = params.toString() ? `?${params.toString()}` : '';
    state.tasks = await apiFetch(API.TASKS + query);
    renderKanbanBoard(state.tasks);
  } catch (err) {
    console.error('Load tasks error:', err);
    showNotification(`Ошибка загрузки: ${err.data?.detail || err.message}`, 'error');
  } finally {
    state.isLoading = false;
    if (taskList) {
      taskList.style.opacity = '1';
    }
  }
}

// ==================== POPULATE SELECTS ====================
function populateProjectSelect() {
  const createSelect = document.getElementById('taskProject');
  const filterSelect = document.getElementById('filterProject');
  
  if (!createSelect || !filterSelect) return;
  
  createSelect.innerHTML = '<option value="">Выберите проект *</option>';
  filterSelect.innerHTML = '<option value="">Все проекты</option>';
  
  state.projects.forEach(project => {
    const option1 = document.createElement('option');
    option1.value = project.id;
    option1.textContent = project.name;
    createSelect.appendChild(option1);
    
    const option2 = document.createElement('option');
    option2.value = project.id;
    option2.textContent = project.name;
    filterSelect.appendChild(option2);
  });
}

function populateUserSelects() {
  const performerSelect = document.getElementById('taskPerformer');
  const filterPerformer = document.getElementById('filterPerformer');
  
  if (!performerSelect || !filterPerformer) return;
  
  performerSelect.innerHTML = '<option value="">Не назначен</option>';
  filterPerformer.innerHTML = '<option value="">Все</option><option value="null">Не назначен</option>';
  
  state.users.forEach(user => {
    const displayName = user.display_name || user.email || `ID: ${user.id}`;
    
    const option1 = document.createElement('option');
    option1.value = user.id;
    option1.textContent = displayName;
    performerSelect.appendChild(option1);
    
    const option2 = document.createElement('option');
    option2.value = user.id;
    option2.textContent = displayName;
    filterPerformer.appendChild(option2);
  });
}

// ==================== KANBAN RENDERING ====================
function renderKanbanBoard(tasks) {
  const columns = {
    'new': document.getElementById('column-new'),
    'in_progress': document.getElementById('column-in_progress'),
    'in_review': document.getElementById('column-in_review'),
    'done': document.getElementById('column-done'),
    'cancelled': document.getElementById('column-cancelled'),
  };

  Object.values(columns).forEach(col => {
    if (col) col.innerHTML = '';
  });

  const counts = { 'new': 0, 'in_progress': 0, 'in_review': 0, 'done': 0, 'cancelled': 0 };

  if (!tasks || !tasks.length) {
    updateTaskCounts(counts);
    return;
  }

  tasks.forEach(task => {
    const card = createTaskCard(task);
    const column = columns[task.status];
    if (column) {
      column.appendChild(card);
      counts[task.status]++;
    }
  });

  updateTaskCounts(counts);
}

function createTaskCard(task) {
  const card = document.createElement('div');
  card.className = 'task-card';
  card.onclick = () => openEditModal(task);

  const priorityLabels = {
    '1': '🟢 Низкий',
    '2': '🟡 Средний',
    '3': '🟠 Высокий',
    '4': '🔴 Критический'
  };

  const isOverdue = task.deadline && new Date(task.deadline) < new Date();
  
  const authorName = task.author?.display_name || task.author?.email || `ID: ${task.author?.id}`;
  const performerName = task.performer?.display_name || task.performer?.email || 'Не назначен';
  
  card.innerHTML = `
    <div class="task-card-header">
      <span class="task-priority priority-${task.priority}">${priorityLabels[task.priority] || '🟡 Средний'}</span>
    </div>
    <div class="task-title">${escapeHtml(task.title)}</div>
    <div class="task-description">${escapeHtml(task.description || 'Нет описания')}</div>
    <div class="task-meta">
      <div class="task-meta-item">👤 Исполнитель: ${performerName}</div>
      <div class="task-meta-item">👤 Автор: ${authorName}</div>
      ${task.deadline ? `<div class="task-meta-item task-deadline ${isOverdue ? 'overdue' : ''}">📅 ${formatDate(task.deadline)}${isOverdue ? ' (Просрочено)' : ''}</div>` : ''}
    </div>
  `;

  return card;
}

function updateTaskCounts(counts) {
  Object.entries(counts).forEach(([status, count]) => {
    const column = document.querySelector(`.kanban-column[data-status="${status}"] .task-count`);
    if (column) column.textContent = count;
  });
}

// ==================== CRUD OPERATIONS ====================
async function createTask(data) {
  try {
    const payload = {
      title: data.title,
      description: data.description || '',
      project_id: parseInt(data.project),
      priority: parseInt(data.priority),
      deadline: data.deadline || null,
    };
    
    if (data.performer && data.performer !== '') {
      payload.performer_id = parseInt(data.performer);
    }
    
    await apiFetch(API.TASKS, { method: 'POST', body: JSON.stringify(payload) });
    showNotification('Задача создана', 'success');
    closeCreateModal();
    await loadTasks(state.filters);
  } catch (err) {
    console.error('Create task error:', err);
    showNotification(`Ошибка создания: ${formatErrors(err.data)}`, 'error');
  }
}

async function updateTask(id, data) {
  try {
    await apiFetch(API.TASKS + id + '/', { method: 'PATCH', body: JSON.stringify(data) });
    showNotification('Задача обновлена', 'success');
    closeEditModal();
    await loadTasks(state.filters);
  } catch (err) {
    console.error('Update task error:', err);
    showNotification(`Ошибка обновления: ${formatErrors(err.data)}`, 'error');
  }
}

async function deleteTask(id) {
  if (!confirm('Удалить задачу? Это действие нельзя отменить.')) return;
  try {
    await apiFetch(API.TASKS + id + '/', { method: 'DELETE' });
    showNotification('Задача удалена', 'success');
    closeEditModal();
    await loadTasks(state.filters);
  } catch (err) {
    console.error('Delete task error:', err);
    showNotification('Не удалось удалить задачу', 'error');
  }
}

// ==================== MODALS ====================
function openCreateModal() {
  document.getElementById('createTaskModal').style.display = 'flex';
}

function closeCreateModal() {
  document.getElementById('createTaskModal').style.display = 'none';
  const form = document.getElementById('createTaskForm');
  if (form) form.reset();
}

function openEditModal(task) {
  document.getElementById('editTaskId').value = task.id;
  document.getElementById('editTitle').value = task.title;
  document.getElementById('editDescription').value = task.description || '';
  document.getElementById('editStatus').value = task.status;
  document.getElementById('editPriority').value = task.priority;
  
  const isAuthor = task.author?.id === state.userId;
  const isPerformer = task.performer?.id === state.userId;
  
  const descGroup = document.getElementById('editDescriptionGroup');
  const statusGroup = document.getElementById('editStatusPriorityGroup');
  
  if (descGroup) descGroup.style.display = isAuthor ? 'block' : 'none';
  if (statusGroup) statusGroup.style.display = isPerformer ? 'block' : 'none';
  
  document.getElementById('editTaskModal').style.display = 'flex';
}

function closeEditModal() {
  document.getElementById('editTaskModal').style.display = 'none';
}

// ==================== UTILITIES ====================
function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleString('ru-RU', { 
    day: '2-digit', 
    month: '2-digit', 
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function showNotification(msg, type = 'info') {
  let box = document.getElementById('notification');
  if (!box) {
    box = document.createElement('div');
    box.id = 'notification';
    box.className = 'notification';
    document.body.insertBefore(box, document.body.firstChild);
  }
  
  box.textContent = msg;
  box.className = `notification ${type}`;
  box.style.display = 'block';
  setTimeout(() => box.style.display = 'none', 4000);
}

function formatErrors(data) {
  if (!data) return 'Неизвестная ошибка';
  return Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join('; ');
}

function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ==================== EVENT LISTENERS ====================
document.addEventListener('DOMContentLoaded', () => {
  // Login form
  const loginForm = document.getElementById('loginForm');
  if (loginForm) {
    loginForm.addEventListener('submit', e => {
      e.preventDefault();
      const username = document.getElementById('username')?.value;
      const password = document.getElementById('password')?.value;
      if (username && password) login(username, password);
    });
  }

  // Logout button
  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) logoutBtn.addEventListener('click', logout);

  // Create task button
  const createTaskBtn = document.getElementById('createTaskBtn');
  if (createTaskBtn) createTaskBtn.addEventListener('click', openCreateModal);

  // Create task form
  const createTaskForm = document.getElementById('createTaskForm');
  if (createTaskForm) {
    createTaskForm.addEventListener('submit', e => {
      e.preventDefault();
      const data = {
        title: document.getElementById('taskTitle')?.value,
        description: document.getElementById('taskDesc')?.value,
        project: document.getElementById('taskProject')?.value,
        priority: document.getElementById('taskPriority')?.value,
        deadline: document.getElementById('taskDeadline')?.value,
        performer: document.getElementById('taskPerformer')?.value,
      };
      
      if (data.title && data.project) {
        createTask(data);
      } else {
        showNotification('Заполните название и выберите проект', 'error');
      }
    });
  }

  // Edit task form
  const editTaskForm = document.getElementById('editTaskForm');
  if (editTaskForm) {
    editTaskForm.addEventListener('submit', e => {
      e.preventDefault();
      const id = document.getElementById('editTaskId')?.value;
      const data = {};
      
      const descGroup = document.getElementById('editDescriptionGroup');
      const statusGroup = document.getElementById('editStatusPriorityGroup');
      
      if (descGroup && descGroup.style.display !== 'none') {
        data.description = document.getElementById('editDescription')?.value;
      }
      
      if (statusGroup && statusGroup.style.display !== 'none') {
        data.status = document.getElementById('editStatus')?.value;
        data.priority = parseInt(document.getElementById('editPriority')?.value);
      }
      
      if (Object.keys(data).length > 0) {
        updateTask(id, data);
      }
    });
  }

  // Delete task button
  const deleteTaskBtn = document.getElementById('deleteTaskBtn');
  if (deleteTaskBtn) {
    deleteTaskBtn.addEventListener('click', () => {
      const id = document.getElementById('editTaskId')?.value;
      if (id) deleteTask(id);
    });
  }

  // Refresh button
  const refreshBtn = document.getElementById('refreshBtn');
  if (refreshBtn) refreshBtn.addEventListener('click', () => loadTasks(state.filters));

  // Apply filters
  const applyFiltersBtn = document.getElementById('applyFilters');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', () => {
      const performerValue = document.getElementById('filterPerformer')?.value;
      
      const filters = {
        project: document.getElementById('filterProject')?.value,
        performer: performerValue === 'null' ? 'null' : performerValue,
        priority: document.getElementById('filterPriority')?.value,
        deadline__gte: document.getElementById('filterDeadline')?.value,
      };
      
      Object.keys(filters).forEach(key => {
        if (!filters[key]) delete filters[key];
      });
      
      loadTasks(filters);
    });
  }

  // Reset filters
  const resetFiltersBtn = document.getElementById('resetFilters');
  if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', () => {
      ['filterProject', 'filterPerformer', 'filterPriority', 'filterDeadline'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      loadTasks({});
    });
  }

  // Close modals on outside click
  window.addEventListener('click', e => {
    if (e.target.id === 'createTaskModal') closeCreateModal();
    if (e.target.id === 'editTaskModal') closeEditModal();
  });

  // Auto-login if token exists
  if (state.accessToken) {
    updateAuthUI(true);
    Promise.all([loadTasks(), loadProjects(), loadUsers()]);
  } else {
    updateAuthUI(false);
  }
  
  console.log('✅ Alpha-Soft Kanban Board initialized');
});