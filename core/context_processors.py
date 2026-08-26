from matches.models import Sport

def sports_menu(request):
    """Добавляет меню видов спорта в контекст всех шаблонов"""
    sports = Sport.objects.filter(is_active=True)
    return {'sports_menu': sports}

def user_balance(request):
    """Добавляет баланс пользователя в контекст"""
    if request.user.is_authenticated:
        return {'user_balance': request.user.balance}
    return {'user_balance': 0}