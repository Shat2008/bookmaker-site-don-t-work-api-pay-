import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'applications.settings')
django.setup()

from django.contrib.auth.models import Group

# Создаем группы
group1, created1 = Group.objects.get_or_create(name='Игроки')
if created1:
    print('✅ Создана группа: Игроки')
else:
    print('ℹ️ Группа "Игроки" уже существует')

group2, created2 = Group.objects.get_or_create(name='VIP Игроки')
if created2:
    print('✅ Создана группа: VIP Игроки')
else:
    print('ℹ️ Группа "VIP Игроки" уже существует')

print('\n📊 Все группы в системе:')
for group in Group.objects.all():
    print(f'  - {group.name}')