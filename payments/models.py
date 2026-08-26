from django.db import models
from django.conf import settings

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('deposit', 'Пополнение'),
        ('withdrawal', 'Вывод'),
        ('bet', 'Ставка'),
        ('win', 'Выигрыш'),
        ('refund', 'Возврат'),
        ('bonus', 'Бонус'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'В обработке'),
        ('completed', 'Завершена'),
        ('failed', 'Неудачная'),
        ('cancelled', 'Отменена'),
    ]
    
    PAYMENT_METHODS = [
        ('card', 'Банковская карта'),
        ('stripe', 'Stripe'),
        ('qiwi', 'QIWI'),
        ('yoomoney', 'ЮMoney'),
        ('webmoney', 'WebMoney'),
        ('crypto', 'Криптовалюта'),
        ('bank_transfer', 'Банковский перевод'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name='Тип операции')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Сумма')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    
    # Для пополнений/выводов
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, blank=True, verbose_name='Способ оплаты')
    payment_details = models.JSONField(default=dict, blank=True, verbose_name='Детали платежа')
    
    # Stripe ID платежа
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Stripe Payment Intent ID')
    stripe_charge_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Stripe Charge ID')
    
    # Связь со ставкой (если это операция со ставкой)
    bet = models.ForeignKey('bets.Bet', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ставка')
    
    description = models.TextField(blank=True, verbose_name='Описание')
    external_id = models.CharField(max_length=100, blank=True, verbose_name='Внешний ID транзакции')
    bank_response = models.JSONField(default=dict, blank=True, verbose_name='Ответ банка')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата завершения')
    
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['external_id']),
            models.Index(fields=['stripe_payment_intent_id']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} ₽"
    
    def complete(self, response_data=None):
        """Завершение транзакции"""
        from django.utils import timezone
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        if response_data:
            self.bank_response = response_data
        
        # Обновление баланса пользователя
        if self.transaction_type == 'deposit' and self.status == 'completed':
            self.user.balance += self.amount
            self.user.save()
        elif self.transaction_type == 'withdrawal' and self.status == 'completed':
            self.user.balance -= self.amount
            self.user.save()
        elif self.transaction_type == 'win' and self.status == 'completed':
            self.user.balance += self.amount
            self.user.save()
        
        self.save()
        return True
    
    def fail(self, reason=""):
        """Отметка транзакции как неудачной"""
        self.status = 'failed'
        self.description = f"{self.description}\nОшибка: {reason}"
        self.save()
        return True
    
    def is_successful(self):
        """Проверка успешности транзакции"""
        return self.status == 'completed'