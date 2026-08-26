from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, verbose_name='Баланс')
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    def deposit(self, amount):
        """Пополнение баланса"""
        self.balance += amount
        self.save()
        return self.balance
    
    def withdraw(self, amount):
        """Снятие средств"""
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True, self.balance
        return False, "Недостаточно средств"
