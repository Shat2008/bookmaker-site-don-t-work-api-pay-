from django.db import models
from django.conf import settings
from matches.models import Match

class Bet(models.Model):
    BET_TYPES = [
        ('team1', 'Победа первой команды'),
        ('team2', 'Победа второй команды'),
        ('draw', 'Ничья'),
        ('total_over', 'Тотал больше'),
        ('total_under', 'Тотал меньше'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('won', 'Выиграна'),
        ('lost', 'Проиграна'),
        ('cancelled', 'Отменена'),
        ('returned', 'Возвращена'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Матч')
    
    bet_type = models.CharField(max_length=20, choices=BET_TYPES, verbose_name='Тип ставки')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма ставки')
    coefficient = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Коэффициент')
    potential_win = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Потенциальный выигрыш')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    result_amount = models.DecimalField(
        max_digits=10, decimal_places=2, 
        null=True, blank=True, 
        verbose_name='Фактический выигрыш'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    settled_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата расчета')
    
    class Meta:
        verbose_name = 'Ставка'
        verbose_name_plural = 'Ставки'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['match', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.amount} ₽"
    
    def save(self, *args, **kwargs):
        # Автоматически рассчитываем потенциальный выигрыш
        if not self.potential_win:
            self.potential_win = self.amount * self.coefficient
        
        # Если ставка выиграла, рассчитываем фактический выигрыш
        if self.status == 'won' and not self.result_amount:
            self.result_amount = self.amount * self.coefficient
        
        super().save(*args, **kwargs)
    
    def can_cancel(self):
        """Можно ли отменить ставку"""
        return self.status == 'pending' and self.match.status == 'upcoming'
    
    def get_bet_type_display_name(self):
        """Отображаемое имя типа ставки"""
        display_names = {
            'team1': f'Победа {self.match.team1}',
            'team2': f'Победа {self.match.team2}',
            'draw': 'Ничья',
            'total_over': 'Тотал больше',
            'total_under': 'Тотал меньше',
        }
        return display_names.get(self.bet_type, self.bet_type)