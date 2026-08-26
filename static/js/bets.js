// JavaScript для функционала ставок

document.addEventListener('DOMContentLoaded', function() {
    initQuickBets();
    initBetCalculator();
    initBetFilters();
    initAutoRefresh();
    initBetSlip();
});

// Быстрые ставки
function initQuickBets() {
    document.querySelectorAll('.quick-bet-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = this.dataset.amount;
            const amountInput = document.querySelector('input[name="amount"]');
            
            if (amountInput) {
                amountInput.value = amount;
                amountInput.dispatchEvent(new Event('input'));
            }
        });
    });
    
    // Удвоение/обнуление ставки
    const doubleBtn = document.getElementById('doubleBet');
    const clearBtn = document.getElementById('clearBet');
    
    if (doubleBtn) {
        doubleBtn.addEventListener('click', function() {
            const amountInput = document.querySelector('input[name="amount"]');
            if (amountInput) {
                amountInput.value = (parseFloat(amountInput.value) || 0) * 2;
                amountInput.dispatchEvent(new Event('input'));
            }
        });
    }
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            const amountInput = document.querySelector('input[name="amount"]');
            if (amountInput) {
                amountInput.value = '';
                amountInput.dispatchEvent(new Event('input'));
            }
        });
    }
}

// Калькулятор ставок
function initBetCalculator() {
    const calculator = document.getElementById('betCalculator');
    if (!calculator) return;
    
    const amountInput = calculator.querySelector('input[name="calc_amount"]');
    const coefficientInput = calculator.querySelector('input[name="calc_coefficient"]');
    const resultElement = calculator.querySelector('.calc-result');
    
    const calculate = () => {
        const amount = parseFloat(amountInput.value) || 0;
        const coefficient = parseFloat(coefficientInput.value) || 1;
        const potentialWin = (amount * coefficient).toFixed(2);
        const profit = (amount * coefficient - amount).toFixed(2);
        
        if (resultElement) {
            resultElement.innerHTML = `
                <div class="mb-2">
                    <strong>Потенциальный выигрыш:</strong> 
                    <span class="text-success fw-bold">${potentialWin} ₽</span>
                </div>
                <div>
                    <strong>Чистая прибыль:</strong> 
                    <span class="text-warning fw-bold">${profit} ₽</span>
                </div>
            `;
        }
    };
    
    amountInput.addEventListener('input', calculate);
    coefficientInput.addEventListener('input', calculate);
    calculate();
}

// Фильтры ставок
function initBetFilters() {
    const filters = document.querySelectorAll('.bet-filter');
    filters.forEach(filter => {
        filter.addEventListener('change', function() {
            const status = this.value;
            const betCards = document.querySelectorAll('.bet-card');
            
            betCards.forEach(card => {
                if (status === 'all' || card.dataset.status === status) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    });
    
    // Поиск ставок
    const searchInput = document.getElementById('betSearch');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const betCards = document.querySelectorAll('.bet-card');
            
            betCards.forEach(card => {
                const text = card.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// Автообновление
function initAutoRefresh() {
    const refreshToggle = document.getElementById('autoRefreshToggle');
    let refreshInterval;
    
    if (refreshToggle) {
        refreshToggle.addEventListener('change', function() {
            if (this.checked) {
                refreshInterval = setInterval(() => {
                    location.reload();
                }, 30000); // Каждые 30 секунд
            } else {
                clearInterval(refreshInterval);
            }
        });
    }
}

// Купон ставок
function initBetSlip() {
    const betSlip = {
        bets: [],
        totalCoefficient: 1,
        totalAmount: 0,
        potentialWin: 0
    };
    
    // Добавление ставки в купон
    document.querySelectorAll('.add-to-slip').forEach(btn => {
        btn.addEventListener('click', function() {
            const matchId = this.dataset.matchId;
            const betType = this.dataset.betType;
            const coefficient = parseFloat(this.dataset.coefficient);
            const matchInfo = this.dataset.matchInfo;
            
            // Проверка, не добавлена ли уже эта ставка
            const existingBet = betSlip.bets.find(bet => 
                bet.matchId === matchId && bet.betType === betType
            );
            
            if (existingBet) {
                showNotification('Эта ставка уже в купоне', 'warning');
                return;
            }
            
            // Добавление ставки
            betSlip.bets.push({
                matchId,
                betType,
                coefficient,
                matchInfo
            });
            
            updateBetSlip();
            showNotification('Ставка добавлена в купон', 'success');
        });
    });
    
    // Обновление отображения купона
    function updateBetSlip() {
        const slipElement = document.getElementById('betSlip');
        if (!slipElement) return;
        
        // Пересчет
        betSlip.totalCoefficient = betSlip.bets.reduce((total, bet) => total * bet.coefficient, 1);
        
        // Обновление UI
        slipElement.innerHTML = `
            <div class="card luxury-card">
                <div class="card-header gold-text">
                    <h5 class="mb-0">Купон ставок (${betSlip.bets.length})</h5>
                </div>
                <div class="card-body">
                    ${betSlip.bets.length > 0 ? `
                        <ul class="list-unstyled">
                            ${betSlip.bets.map((bet, index) => `
                                <li class="mb-2">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small>${bet.matchInfo}</small>
                                        <button class="btn btn-sm btn-outline-danger remove-bet" data-index="${index}">
                                            <i class="fas fa-times"></i>
                                        </button>
                                    </div>
                                    <div class="d-flex justify-content-between">
                                        <span>${bet.betType === 'team1' ? 'П1' : bet.betType === 'team2' ? 'П2' : 'Н'}</span>
                                        <span class="fw-bold">${bet.coefficient.toFixed(2)}</span>
                                    </div>
                                </li>
                            `).join('')}
                        </ul>
                        <hr>
                        <div class="mb-3">
                            <label class="form-label">Общий коэффициент:</label>
                            <div class="fs-4 gold-text fw-bold">${betSlip.totalCoefficient.toFixed(2)}</div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Сумма ставки:</label>
                            <input type="number" class="form-control" id="slipAmount" 
                                   min="10" step="10" placeholder="Введите сумму">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Потенциальный выигрыш:</label>
                            <div id="slipPotentialWin" class="fs-5 text-success fw-bold">0 ₽</div>
                        </div>
                        <button id="placeSlipBet" class="btn btn-gold w-100" disabled>
                            Сделать ставку
                        </button>
                    ` : `
                        <p class="text-center text-muted">Добавьте ставки в купон</p>
                    `}
                </div>
            </div>
        `;
        
        // Инициализация событий после обновления UI
        initSlipEvents();
    }
    
    // Инициализация событий купона
    function initSlipEvents() {
        // Удаление ставки
        document.querySelectorAll('.remove-bet').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.dataset.index);
                betSlip.bets.splice(index, 1);
                updateBetSlip();
                showNotification('Ставка удалена из купона', 'info');
            });
        });
        
        // Расчет потенциального выигрыша
        const amountInput = document.getElementById('slipAmount');
        const potentialWinElement = document.getElementById('slipPotentialWin');
        const placeBtn = document.getElementById('placeSlipBet');
        
        if (amountInput && potentialWinElement) {
            amountInput.addEventListener('input', function() {
                const amount = parseFloat(this.value) || 0;
                const potentialWin = (amount * betSlip.totalCoefficient).toFixed(2);
                potentialWinElement.textContent = `${potentialWin} ₽`;
                
                // Активация/деактивация кнопки
                if (amount >= 10 && amount <= parseFloat(document.querySelector('.user-balance').textContent)) {
                    placeBtn.disabled = false;
                } else {
                    placeBtn.disabled = true;
                }
            });
        }
        
        // Размещение комбинированной ставки
        if (placeBtn) {
            placeBtn.addEventListener('click', async function() {
                const amount = parseFloat(document.getElementById('slipAmount').value);
                
                if (!amount || amount < 10) {
                    showNotification('Минимальная сумма ставки - 10 ₽', 'warning');
                    return;
                }
                
                if (amount > parseFloat(document.querySelector('.user-balance').textContent)) {
                    showNotification('Недостаточно средств на балансе', 'danger');
                    return;
                }
                
                // Отправка ставок
                try {
                    const betsData = betSlip.bets.map(bet => ({
                        match_id: bet.matchId,
                        bet_type: bet.betType,
                        coefficient: bet.coefficient
                    }));
                    
                    const response = await fetch('/bets/api/place-slip/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify({
                            bets: betsData,
                            amount: amount
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        showNotification('Комбинированная ставка размещена успешно!', 'success');
                        
                        // Обновление баланса
                        document.querySelectorAll('.user-balance').forEach(el => {
                            el.textContent = `${parseFloat(result.new_balance).toFixed(2)} ₽`;
                        });
                        
                        // Очистка купона
                        betSlip.bets = [];
                        updateBetSlip();
                        
                        // Перенаправление
                        setTimeout(() => {
                            window.location.href = '/bets/history/';
                        }, 2000);
                    } else {
                        showNotification(result.error || 'Ошибка при размещении ставки', 'danger');
                    }
                } catch (error) {
                    showNotification('Ошибка сети. Попробуйте еще раз.', 'danger');
                }
            });
        }
    }
    
    // Вспомогательная функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Статистика ставок
function initBetStatistics() {
    const ctx = document.getElementById('betStatsChart');
    if (!ctx) return;
    
    // В реальном проекте здесь будет загрузка данных с сервера
    const data = {
        labels: ['Выиграно', 'Проиграно', 'В ожидании'],
        datasets: [{
            data: [30, 50, 20],
            backgroundColor: [
                '#28a745',
                '#dc3545',
                '#ffc107'
            ],
            borderWidth: 2,
            borderColor: '#fff'
        }]
    };
    
    new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#f0e6d2',
                        padding: 20
                    }
                }
            }
        }
    });
}

// Экспорт истории ставок
function exportBetsHistory(format = 'csv') {
    const bets = document.querySelectorAll('.bet-card');
    let data = 'Дата,Матч,Тип,Сумма,Коэффициент,Статус,Выигрыш\n';
    
    bets.forEach(bet => {
        const date = bet.querySelector('.bet-date').textContent;
        const match = bet.querySelector('.bet-match').textContent;
        const type = bet.querySelector('.bet-type').textContent;
        const amount = bet.querySelector('.bet-amount').textContent;
        const coefficient = bet.querySelector('.bet-coefficient').textContent;
        const status = bet.querySelector('.bet-status').textContent;
        const win = bet.querySelector('.bet-win')?.textContent || '0 ₽';
        
        data += `"${date}","${match}","${type}","${amount}","${coefficient}","${status}","${win}"\n`;
    });
    
    if (format === 'csv') {
        const blob = new Blob([data], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `bets_history_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    }
}

// Уведомления о начале матчей
function initMatchNotifications() {
    if ('Notification' in window && Notification.permission === 'granted') {
        // Проверка приближающихся матчей
        setInterval(() => {
            const upcomingMatches = document.querySelectorAll('.match-card[data-start-time]');
            const now = new Date().getTime();
            
            upcomingMatches.forEach(match => {
                const startTime = new Date(match.dataset.startTime).getTime();
                const timeLeft = startTime - now;
                
                // Уведомление за 15 минут до начала
                if (timeLeft > 0 && timeLeft <= 15 * 60 * 1000) {
                    const matchTitle = match.querySelector('.match-title').textContent;
                    
                    if (!match.dataset.notified) {
                        new Notification('Скоро начнется матч!', {
                            body: `${matchTitle} начинается через 15 минут`,
                            icon: '/static/images/logo.png'
                        });
                        
                        match.dataset.notified = 'true';
                    }
                }
            });
        }, 60000); // Проверка каждую минуту
    }
}

// Запрос разрешения на уведомления
if ('Notification' in window && Notification.permission === 'default') {
    const notificationBtn = document.getElementById('enableNotifications');
    if (notificationBtn) {
        notificationBtn.addEventListener('click', () => {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    showNotification('Уведомления включены', 'success');
                    initMatchNotifications();
                }
            });
        });
    }
}