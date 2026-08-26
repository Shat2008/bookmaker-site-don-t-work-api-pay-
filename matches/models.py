from django.db import models

class Sport(models.Model):
    SPORT_CHOICES = [
        ('football', '⚽ Футбол'),
        ('basketball', '🏀 Баскетбол'),
        ('tennis', '🎾 Теннис'),
        ('hockey', '🏒 Хоккей'),
        ('boxing', '🥊 Бокс'),
        ('esports', '🎮 Киберспорт'),
        ('volleyball', '🏐 Волейбол'),
        ('baseball', '⚾ Бейсбол'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    icon = models.CharField(max_length=50, default='fas fa-trophy', verbose_name='Иконка')
    order = models.IntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    
    class Meta:
        verbose_name = 'Вид спорта'
        verbose_name_plural = 'Виды спорта'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_active_matches(self):
        """Возвращает активные матчи для этого вида спорта"""
        return self.match_set.filter(is_active=True).order_by('start_time')

class Match(models.Model):
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, verbose_name='Вид спорта')
    external_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='Внешний ID')
    
    team1 = models.CharField(max_length=200, verbose_name='Команда 1')
    team2 = models.CharField(max_length=200, verbose_name='Команда 2')
    team1_logo = models.CharField(max_length=500, blank=True, verbose_name='Логотип команды 1')
    team2_logo = models.CharField(max_length=500, blank=True, verbose_name='Логотип команды 2')
    
    start_time = models.DateTimeField(verbose_name='Время начала')
    league = models.CharField(max_length=200, verbose_name='Лига/Турнир')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')
    
    # Основные коэффициенты
    coefficient_team1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Коэффициент 1')
    coefficient_team2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Коэффициент 2')
    coefficient_draw = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Коэффициент ничьи')
    
    # Дополнительные коэффициенты
    total_over = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Тотал больше')
    total_under = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Тотал меньше')
    
    # Статус матча
    STATUS_CHOICES = [
        ('upcoming', 'Предстоящий'),
        ('live', 'В прямом эфире'),
        ('finished', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', verbose_name='Статус')
    
    is_active = models.BooleanField(default=True, verbose_name='Активен для ставок')
    result = models.CharField(max_length=50, blank=True, verbose_name='Результат')
    score = models.CharField(max_length=20, blank=True, verbose_name='Счет')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Матч'
        verbose_name_plural = 'Матчи'
        ordering = ['start_time']
        indexes = [
            models.Index(fields=['sport', 'start_time']),
            models.Index(fields=['status', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.team1} vs {self.team2} ({self.start_time.strftime('%d.%m %H:%M')})"
    
    @property
    def is_live(self):
        """Проверка, идет ли матч в прямом эфире"""
        return self.status == 'live'
    
    @property
    def time_until_start(self):
        """Время до начала матча"""
        from django.utils import timezone
        delta = self.start_time - timezone.now()
        if delta.days > 0:
            return f"Через {delta.days} дней"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"Через {hours} часов"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"Через {minutes} минут"
        else:
            return "Скоро"