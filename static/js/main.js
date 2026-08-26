// Основной JavaScript файл

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация всех компонентов
    initTheme();
    initBalanceUpdates();
    initMatchTimers();
    initCoefficientUpdates();
    initBetForms();
    initNotifications();
    initMobileMenu();
    initLiveUpdates();
    initButtonHandlers();
    initFormHandlers();
    initAnimations();
});

// Тема оформления
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
    }
    
    // Восстановление темы
    const savedTheme = localStorage.getItem('theme') || 'dark';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
    }
}

// Обновление баланса
function initBalanceUpdates() {
    // Обновление баланса каждые 30 секунд
    if (document.querySelector('.user-balance')) {
        setInterval(updateUserBalance, 30000);
    }
}

async function updateUserBalance() {
    try {
        const response = await fetch('/users/api/balance/');
        if (response.ok) {
            const data = await response.json();
            document.querySelectorAll('.user-balance').forEach(el => {
                el.textContent = `${parseFloat(data.balance).toFixed(2)} ₽`;
            });
        }
    } catch (error) {
        console.error('Ошибка обновления баланса:', error);
    }
}

// Таймеры матчей
function initMatchTimers() {
    const timers = document.querySelectorAll('.match-timer');
    timers.forEach(timer => {
        const endTime = new Date(timer.dataset.endTime).getTime();
        updateTimer(timer, endTime);
        setInterval(() => updateTimer(timer, endTime), 1000);
    });
}

function updateTimer(timerElement, endTime) {
    const now = new Date().getTime();
    const distance = endTime - now;
    
    if (distance < 0) {
        timerElement.textContent = 'Матч завершен';
        timerElement.classList.add('text-danger');
        return;
    }
    
    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((distance % (1000 * 60)) / 1000);
    
    timerElement.textContent = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Изменение цвета при приближении к концу
    if (hours === 0 && minutes < 5) {
        timerElement.classList.add('text-warning');
    }
    if (hours === 0 && minutes < 1) {
        timerElement.classList.add('text-danger', 'blink');
    }
}

// Обновление коэффициентов
function initCoefficientUpdates() {
    // Обновление коэффициентов каждые 10 секунд для live матчей
    const liveMatches = document.querySelectorAll('.match-card.live');
    if (liveMatches.length > 0) {
        setInterval(updateLiveOdds, 10000);
    }
}

async function updateLiveOdds() {
    try {
        const response = await fetch('/matches/api/live-odds/');
        if (response.ok) {
            const data = await response.json();
            data.odds.forEach(odd => {
                const element = document.getElementById(`odd-${odd.match_id}-${odd.type}`);
                if (element) {
                    const oldValue = parseFloat(element.textContent);
                    const newValue = parseFloat(odd.value);
                    
                    // Анимация изменения
                    if (newValue > oldValue) {
                        element.classList.add('text-success');
                        setTimeout(() => element.classList.remove('text-success'), 1000);
                    } else if (newValue < oldValue) {
                        element.classList.add('text-danger');
                        setTimeout(() => element.classList.remove('text-danger'), 1000);
                    }
                    
                    element.textContent = newValue.toFixed(2);
                }
            });
        }
    } catch (error) {
        console.error('Ошибка обновления коэффициентов:', error);
    }
}

// Формы ставок
function initBetForms() {
    const betForms = document.querySelectorAll('.bet-form');
    betForms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Обработка...';
            
            try {
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showNotification('Ставка размещена успешно!', 'success');
                    
                    // Обновление баланса
                    document.querySelectorAll('.user-balance').forEach(el => {
                        el.textContent = `${parseFloat(result.new_balance).toFixed(2)} ₽`;
                    });
                    
                    // Перенаправление на страницу успеха
                    setTimeout(() => {
                        window.location.href = `/bets/success/${result.bet_id}/`;
                    }, 1500);
                } else {
                    showNotification(result.error || 'Ошибка при размещении ставки', 'danger');
                    submitBtn.disabled = false;
                    submitBtn.textContent = originalText;
                }
            } catch (error) {
                showNotification('Ошибка сети. Попробуйте еще раз.', 'danger');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
        
        // Обновление потенциального выигрыша
        const amountInput = form.querySelector('input[name="amount"]');
        const coefficientElement = form.querySelector('.selected-coefficient');
        
        if (amountInput && coefficientElement) {
            const updatePotentialWin = () => {
                const amount = parseFloat(amountInput.value) || 0;
                const coefficient = parseFloat(coefficientElement.dataset.coefficient) || 1;
                const potentialWin = (amount * coefficient).toFixed(2);
                
                const winElement = form.querySelector('.potential-win');
                if (winElement) {
                    winElement.textContent = `${potentialWin} ₽`;
                }
            };
            
            amountInput.addEventListener('input', updatePotentialWin);
            updatePotentialWin();
        }
    });
    
    // Выбор коэффициента
    document.querySelectorAll('.coefficient-badge').forEach(badge => {
        badge.addEventListener('click', function() {
            // Снимаем выделение со всех коэффициентов
            document.querySelectorAll('.coefficient-badge').forEach(b => {
                b.classList.remove('selected');
            });
            
            // Выделяем выбранный коэффициент
            this.classList.add('selected');
            
            // Обновляем скрытое поле формы
            const betType = this.dataset.betType;
            const coefficient = this.dataset.coefficient;
            
            document.querySelectorAll('input[name="bet_type"]').forEach(input => {
                if (input.value === betType) {
                    input.checked = true;
                }
            });
            
            // Обновляем отображение потенциального выигрыша
            const coefficientElement = document.querySelector('.selected-coefficient');
            if (coefficientElement) {
                coefficientElement.textContent = coefficient;
                coefficientElement.dataset.coefficient = coefficient;
                
                const amountInput = document.querySelector('input[name="amount"]');
                if (amountInput && amountInput.value) {
                    const potentialWin = (parseFloat(amountInput.value) * parseFloat(coefficient)).toFixed(2);
                    const winElement = document.querySelector('.potential-win');
                    if (winElement) {
                        winElement.textContent = `${potentialWin} ₽`;
                    }
                }
            }
        });
    });
}

// Уведомления
function initNotifications() {
    // Показ всплывающих уведомлений
    window.showNotification = function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = `
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        `;
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    };
    
    // Показ сообщений из Django
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(message);
            bsAlert.close();
        }, 5000);
    });
}

// Мобильное меню
function initMobileMenu() {
    const menuToggles = document.querySelectorAll('[data-bs-toggle="collapse"]');
    menuToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const target = document.querySelector(this.dataset.bsTarget);
            if (target) {
                target.classList.toggle('show');
            }
        });
    });
}

// Live обновления
function initLiveUpdates() {
    // WebSocket подключение для live обновлений
    if (window.location.pathname.includes('live')) {
        connectWebSocket();
    }
    
    // Автоматическое обновление live матчей каждые 5 секунд
    const liveSection = document.getElementById('live-matches-section');
    if (liveSection) {
        setInterval(updateLiveMatches, 5000);
    }
}

function connectWebSocket() {
    // В реальном проекте здесь будет WebSocket подключение
    console.log('WebSocket подключение для live обновлений');
}

async function updateLiveMatches() {
    try {
        const response = await fetch('/matches/api/live-matches/');
        if (response.ok) {
            const data = await response.json();
            // Обновление DOM с новыми данными live матчей
            // (реализация зависит от структуры вашего шаблона)
        }
    } catch (error) {
        console.error('Ошибка обновления live матчей:', error);
    }
}

// Вспомогательные функции
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Копирование в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(err => {
        showNotification('Ошибка копирования', 'danger');
    });
}

// Подтверждение действий
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Загрузка данных с индикатором
async function fetchWithLoading(url, options = {}) {
    const loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loading);
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } finally {
        loading.remove();
    }
}

// Инициализация tooltips Bootstrap
const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
});

// Инициализация popovers Bootstrap
const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
});

// ===== НОВАЯ ФУНКЦИОНАЛЬНОСТЬ КНОПОК =====

// Обработчик кнопок
function initButtonHandlers() {
    // Toggle кнопки
    document.querySelectorAll('.btn-toggle').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            this.classList.toggle('active');
            
            // Получаем group и toggle другие кнопки в группе если нужно
            const group = this.dataset.group;
            if (group) {
                document.querySelectorAll(`[data-group="${group}"]`).forEach(b => {
                    if (b !== this) b.classList.remove('active');
                });
            }
            
            // Вызываем callback если указан
            if (this.dataset.callback) {
                window[this.dataset.callback](this);
            }
        });
    });
    
    // Кнопки с подтверждением
    document.querySelectorAll('.btn-confirm').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const message = this.dataset.confirm || 'Вы уверены?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Кнопки копирования
    document.querySelectorAll('.btn-copy').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const text = this.dataset.copy || this.textContent;
            copyToClipboard(text);
        });
    });
    
    // Кнопки с быстрыми действиями
    document.querySelectorAll('.quick-amount').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const amount = this.dataset.amount;
            const input = document.getElementById('amountInput');
            if (input) {
                input.value = amount;
                input.dispatchEvent(new Event('input'));
                input.focus();
            }
        });
    });
    
    // Кнопки методов оплаты
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', function() {
            document.querySelectorAll('.payment-method').forEach(m => {
                m.classList.remove('active');
            });
            this.classList.add('active');
            
            const methodType = this.dataset.method;
            const input = document.querySelector('input[name="payment_method"]');
            if (input) {
                input.value = methodType;
            }
        });
    });
    
    // Кнопки выбора спорта
    document.querySelectorAll('.sport-filter').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Визуальное выделение
            document.querySelectorAll('.sport-filter').forEach(b => {
                b.classList.remove('active');
            });
            this.classList.add('active');
            
            // Фильтрация матчей
            const sport = this.dataset.sport;
            filterMatchesBySport(sport);
        });
    });
    
    // Кнопки сортировки
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const sortBy = this.dataset.sortBy;
            sortMatches(sortBy);
        });
    });
}

// Обработчики форм
function initFormHandlers() {
    // Auto-save формы
    document.querySelectorAll('[data-autosave]').forEach(form => {
        form.addEventListener('change', function() {
            autoSaveForm(this);
        });
    });
    
    // Validation на ходу
    document.querySelectorAll('[data-validate]').forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    // Масковка телефонов
    document.querySelectorAll('input[type="tel"]').forEach(input => {
        input.addEventListener('input', function() {
            maskPhoneInput(this);
        });
    });
    
    // Форматирование сумм
    document.querySelectorAll('input[type="number"][data-format="currency"]').forEach(input => {
        input.addEventListener('input', function() {
            this.value = formatCurrency(this.value);
        });
    });
}

// Анимации
function initAnimations() {
    // Наблюдатель за видимостью элементов
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                if (entry.target.dataset.animation) {
                    entry.target.style.animation = entry.target.dataset.animation;
                }
            }
        });
    }, {
        threshold: 0.1
    });
    
    document.querySelectorAll('[data-animate]').forEach(el => {
        observer.observe(el);
    });
    
    // Ripple эффект для кнопок с классом btn-ripple
    document.querySelectorAll('.btn-ripple').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// Фильтрация матчей по спорту
async function filterMatchesBySport(sport) {
    const url = sport === 'all' ? '/matches/api/matches/' : `/matches/api/matches/?sport=${sport}`;
    try {
        const response = await fetch(url);
        const data = await response.json();
        updateMatchesDisplay(data.matches);
        showNotification(`Выбран вид спорта: ${sport}`, 'info');
    } catch (error) {
        console.error('Ошибка фильтрации:', error);
        showNotification('Ошибка при фильтрации матчей', 'danger');
    }
}

// Сортировка матчей
async function sortMatches(sortBy) {
    try {
        const response = await fetch(`/matches/api/matches/?sort=${sortBy}`);
        const data = await response.json();
        updateMatchesDisplay(data.matches);
    } catch (error) {
        console.error('Ошибка сортировки:', error);
    }
}

// Обновление отображения матчей
function updateMatchesDisplay(matches) {
    const container = document.getElementById('matches-container');
    if (!container) return;
    
    container.innerHTML = '';
    matches.forEach(match => {
        const card = createMatchCard(match);
        container.appendChild(card);
    });
}

// Создание карточки матча
function createMatchCard(match) {
    const div = document.createElement('div');
    div.className = 'match-card luxury-card p-3';
    div.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div class="match-teams">
                <strong>${match.team1}</strong> vs <strong>${match.team2}</strong>
            </div>
            <div class="match-time">
                <span class="badge bg-info">${match.status}</span>
            </div>
        </div>
    `;
    return div;
}

// Auto-save форма
async function autoSaveForm(form) {
    const formData = new FormData(form);
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            showNotification('Данные сохранены', 'success');
        }
    } catch (error) {
        console.error('Ошибка при сохранении:', error);
    }
}

// Валидация поля
function validateField(field) {
    const type = field.dataset.validate;
    let isValid = false;
    
    switch(type) {
        case 'email':
            isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(field.value);
            break;
        case 'phone':
            isValid = field.value.length >= 10;
            break;
        case 'required':
            isValid = field.value.trim().length > 0;
            break;
        default:
            isValid = true;
    }
    
    if (isValid) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
    } else {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
    }
    
    return isValid;
}

// Маска для телефона
function maskPhoneInput(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.length > 11) value = value.slice(0, 11);
    
    if (value.length > 0) {
        if (value[0] !== '7' && value[0] !== '8') {
            value = '7' + value;
        }
    }
    
    let formatted = '';
    if (value.length >= 1) formatted = '+' + value[0];
    if (value.length >= 3) formatted += ' (' + value.slice(1, 4);
    if (value.length >= 6) formatted += ') ' + value.slice(4, 7);
    if (value.length >= 9) formatted += '-' + value.slice(7, 9);
    if (value.length >= 11) formatted += '-' + value.slice(9, 11);
    
    input.value = formatted;
}

// Форматирование валюты
function formatCurrency(value) {
    const num = parseFloat(value) || 0;
    return num.toLocaleString('ru-RU', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });
}

// Debounce функция для оптимизации
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle функция
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Вспомогательные функции
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Копирование в буфер обмена
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Скопировано в буфер обмена', 'success');
    }).catch(err => {
        showNotification('Ошибка копирования', 'danger');
    });
}

// Подтверждение действий
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Загрузка данных с индикатором
async function fetchWithLoading(url, options = {}) {
    const loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.innerHTML = '<div class="loading-spinner"></div>';
    document.body.appendChild(loading);
    
    try {
        const response = await fetch(url, options);
        return await response.json();
    } finally {
        loading.remove();
    }
}