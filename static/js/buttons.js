// ===== РАСШИРЕННАЯ ФУНКЦИОНАЛЬНОСТЬ КНОПОК =====

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    initButtonEffects();
    initSelectableElements();
    initQuickAmountButtons();
    initPaymentMethods();
    initFormValidation();
});

// ===== ЭФФЕКТЫ КНОПОК =====

function initButtonEffects() {
    // Ripple эффект
    document.querySelectorAll('.btn-ripple').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const ripple = document.createElement('span');
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.background = 'rgba(255, 255, 255, 0.6)';
            ripple.style.borderRadius = '50%';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'rippleEffect 0.6s ease-out';
            ripple.style.pointerEvents = 'none';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Pulse эффект
    document.querySelectorAll('.btn-pulse').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.animation = 'buttonPulse 0.6s ease-out';
        });
    });
    
    // Glow эффект
    document.querySelectorAll('.btn-glow').forEach(btn => {
        btn.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            this.style.boxShadow = `
                0 0 20px rgba(212, 175, 55, 0.5),
                ${(x - rect.width / 2) * 0.1}px ${(y - rect.height / 2) * 0.1}px 30px rgba(212, 175, 55, 0.3)
            `;
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 0 10px rgba(212, 175, 55, 0.5)';
        });
    });
}

// ===== СЕЛЕКТИРУЕМЫЕ ЭЛЕМЕНТЫ =====

function initSelectableElements() {
    // Bet options
    document.querySelectorAll('.bet-option').forEach(option => {
        option.addEventListener('click', function() {
            // Снимаем выделение со всех
            document.querySelectorAll('.bet-option').forEach(o => {
                o.classList.remove('selected');
            });
            
            // Выделяем текущий
            this.classList.add('selected');
            
            // Обновляем коэффициент
            updateCoefficient(this.dataset.coefficient, this.dataset.type);
            
            // Обновляем потенциальный выигрыш
            updatePotentialWin();
        });
    });
    
    // Payment methods
    document.querySelectorAll('.payment-method').forEach(method => {
        method.addEventListener('click', function() {
            document.querySelectorAll('.payment-method').forEach(m => {
                m.classList.remove('active');
            });
            this.classList.add('active');
            
            const methodType = this.dataset.method;
            updatePaymentFields(methodType);
            
            const input = document.querySelector('input[name="payment_method"]');
            if (input) {
                input.value = methodType;
            }
        });
    });
}

// ===== БЫСТРЫЕ СУММЫ =====

function initQuickAmountButtons() {
    document.querySelectorAll('.quick-amount').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const amount = this.dataset.amount;
            const input = document.getElementById('amountInput');
            
            if (input) {
                // Анимируем изменение
                input.style.transition = 'all 0.3s ease';
                input.style.transform = 'scale(0.95)';
                
                setTimeout(() => {
                    input.value = amount;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.style.transform = 'scale(1)';
                }, 100);
                
                // Визуальная обратная связь кнопки
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = 'scale(1)';
                }, 100);
            }
        });
    });
}

// ===== СПОСОБЫ ОПЛАТЫ =====

function updatePaymentFields(methodType) {
    document.querySelectorAll('.payment-fields').forEach(field => {
        field.style.display = 'none';
    });
    
    const activeFields = document.querySelector(`.${methodType}-fields`);
    if (activeFields) {
        activeFields.style.display = 'block';
        // Анимируем появление
        activeFields.style.animation = 'fadeIn 0.3s ease';
    }
}

function initPaymentMethods() {
    // Первый метод активен по умолчанию
    const firstMethod = document.querySelector('.payment-method');
    if (firstMethod) {
        firstMethod.click();
    }
}

// ===== КОЭФФИЦИЕНТЫ И РАСЧЁТЫ =====

function updateCoefficient(coefficient, type) {
    const coeffDisplay = document.getElementById('coefficientDisplay');
    if (coeffDisplay) {
        coeffDisplay.textContent = parseFloat(coefficient).toFixed(2);
        coeffDisplay.style.animation = 'none';
        
        // Триггер анимацию
        setTimeout(() => {
            coeffDisplay.style.animation = 'scaleAnimation 0.3s ease';
        }, 10);
    }
    
    // Обновляем скрытое поле
    const betTypeInput = document.getElementById('id_bet_type');
    if (betTypeInput) {
        betTypeInput.value = type;
    }
}

function updatePotentialWin() {
    const amountInput = document.getElementById('id_amount');
    const coeffDisplay = document.getElementById('coefficientDisplay');
    const winDisplay = document.getElementById('potentialWin');
    const deductDisplay = document.getElementById('amountToDeduct');
    
    if (amountInput && coeffDisplay && winDisplay) {
        const amount = parseFloat(amountInput.value) || 0;
        const coefficient = parseFloat(coeffDisplay.textContent) || 1;
        const win = (amount * coefficient).toFixed(2);
        const deduct = amount.toFixed(2);
        
        winDisplay.textContent = `${win} ₽`;
        if (deductDisplay) {
            deductDisplay.textContent = `${deduct} ₽`;
        }
    }
}

// ===== ВАЛИДАЦИЯ ФОРМ =====

function initFormValidation() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required], select[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    input.classList.remove('is-valid');
                    isValid = false;
                } else {
                    input.classList.remove('is-invalid');
                    input.classList.add('is-valid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showNotification('Пожалуйста, заполните все обязательные поля', 'warning');
            }
        });
        
        // Валидация при изменении
        form.querySelectorAll('input[required], select[required], textarea[required]').forEach(input => {
            input.addEventListener('change', function() {
                if (this.value.trim()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// ===== УТИЛИТ-ФУНКЦИИ =====

// Форматирование сумм
function formatAmount(amount) {
    return parseFloat(amount).toLocaleString('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    });
}

// Анимированное изменение числа
function animateNumber(element, endValue, duration = 500) {
    const startValue = parseFloat(element.textContent.replace(/[^\d.]/g, '')) || 0;
    const startTime = Date.now();
    
    const updateValue = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const currentValue = startValue + (endValue - startValue) * progress;
        element.textContent = formatAmount(currentValue);
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    };
    
    updateValue();
}

// Обновление баланса с анимацией
function updateBalanceAnimated(newBalance) {
    const balanceElements = document.querySelectorAll('.user-balance');
    balanceElements.forEach(el => {
        animateNumber(el, parseFloat(newBalance));
    });
}

// ===== ТОСТЕРЫ И УВЕДОМЛЕНИЯ =====

function showButtonNotification(btn, message, duration = 2000) {
    const originalContent = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-check me-2"></i>${message}`;
    
    setTimeout(() => {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }, duration);
}

// ===== ДОБАВЛЯЕМ СТИЛИ АНИМАЦИЙ =====

const style = document.createElement('style');
style.textContent = `
    @keyframes rippleEffect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    @keyframes scaleAnimation {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    .is-invalid {
        border-color: #dc3545 !important;
        background-color: rgba(220, 53, 69, 0.1) !important;
    }
    
    .is-valid {
        border-color: #28a745 !important;
        background-color: rgba(40, 167, 69, 0.1) !important;
    }
    
    input:focus.is-valid,
    input:focus.is-invalid {
        box-shadow: 0 0 0 0.25rem rgba(212, 175, 55, 0.25);
    }
`;
document.head.appendChild(style);

// ===== УТИЛИТЫ ДЛЯ ОТЛАДКИ =====

// Экспортируем функции в глобальную область для использования в HTML
window.updatePotentialWin = updatePotentialWin;
window.updatePaymentFields = updatePaymentFields;
window.showButtonNotification = showButtonNotification;
window.updateBalanceAnimated = updateBalanceAnimated;
window.formatAmount = formatAmount;
