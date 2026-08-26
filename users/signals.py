from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def add_user_to_group(sender, instance, created, **kwargs):
    """Добавляем нового пользователя в группу 'Игроки'"""
    if created:
        # Используем update_or_create чтобы избежать рекурсии
        group, _ = Group.objects.get_or_create(name='Игроки')
        instance.groups.add(group)
        # НЕ вызываем instance.save() здесь - это вызовет рекурсию

# УДАЛИТЕ этот сигнал, он вызывает рекурсию:
# @receiver(post_save, sender=CustomUser)
# def save_user_profile(sender, instance, **kwargs):
#     """Сохранение профиля пользователя"""
#     instance.save()  # ← ЭТО ВЫЗЫВАЕТ РЕКУРСИЮ